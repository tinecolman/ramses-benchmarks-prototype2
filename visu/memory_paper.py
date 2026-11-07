'''
Memory gain of the hybrid MPI-OpenMP configurations, illustrated with one
benchmark on one cluster (default: cosmo 1024 on LUMI). Two panels:
  * left:  memory per node as a function of the number of nodes, one line per
           configuration, with ideal scaling of the MPI-only run on one node
  * right: memory per node relative to MPI-only on the same number of nodes,
           or with --factor the reduction factor M_MPI/M_hybrid (×2, ×10, ...)

The memory is the one printed by RAMSES (resident memory, maximum over the MPI
processes) times the number of processes per node, see io_timings.py. For the
unigrid setups (sedov, cosmo) the per-process allocation of grids and particles
is adapted to the number of processes by launch_benchmark_suite.sh, leaving
room for the ghost zones, so that the memory per process only depends on the
total number of MPI processes.

With --fill, the second figure is made instead: the number of grids (top or
left) and particles (bottom or right) in use, from the fill level of the
preallocated arrays printed by RAMSES on the 'Fine step' lines ('mem= 75.0%
77.0%'). The percentages are those of the fullest MPI process (max over the
processes of used grid slots, own and ghost grids, and min of the free particle
slots), so ngridmax x % x number of processes is an upper bound of the total.
It is the peak over the run, averaged over the repeats. ngridmax (npartmax) is
read from the namelist of the run, or is ngridtot (nparttot) divided by the
number of processes if the namelist only sets the total. The number of grids
of the mesh (last 'Mesh structure' in the log) and, for cosmo, the number of
particles are shown as a reference.

Run from the visu directory:
    python memory_paper.py
    python memory_paper.py -c lumi -b sedov -r 1024
    python memory_paper.py --factor
    python memory_paper.py --fill --column
'''

import os
import re
import glob

import numpy as np
from matplotlib import pyplot as plt
from openmp_module_analysis import STYLE
from openmp_best_speedup import load_openmp_data, cluster_label
from omp_module_gain_heatmap import EXCLUDED_THREADS
from io_timings import set_node_ticks
from memory import gather_memory_results
from io_timings import get_info_from_subdir_name, parse_metadata, skip_compiler
from openmp_best_speedup import get_openmp_dirs, FIG_HEIGHT, DPI

CORES_PER_NODE = {'marenostrum': 112, 'lumi': 128, 'meluxina': 128}


''' Memory per node of MPI-only and of the hybrid configurations, the latter
    with at least two threads, as {omp: (nodes, memory per node [GB])} '''
def memory_per_config(cluster, bench, reso):
    results = gather_memory_results(load_openmp_data(cluster, bench), reso)
    excluded = [1]+EXCLUDED_THREADS.get(cluster, [])
    return {omp: results[omp] for omp in sorted(results) if omp not in excluded}


''' Line color and label of every configuration (number of threads), dark to
    light with the number of threads, MPI-only in black '''
def config_styles(configs, cores):
    hybrid = [omp for omp in configs if omp>0]
    # dark to light with the number of threads, without the lightest yellow
    cmap = plt.get_cmap('inferno')
    colors = {omp: cmap(0.15+0.7*i/max(len(hybrid)-1, 1)) for i, omp in enumerate(hybrid)}
    colors[0] = 'black'
    labels = {omp: f'{cores//max(omp, 1)}×{omp}' for omp in hybrid}
    labels[0] = 'MPI-only'
    return colors, labels


''' Value of a parameter in a namelist, None if it is not set '''
def namelist_value(text, name):
    match = re.search(rf'^\s*{name}\s*=\s*([0-9.eEdD+]+)', text, re.M | re.I)
    return float(match.group(1).lower().replace('d', 'e')) if match else None


''' Number of grids of the mesh, from the last 'Mesh structure' in the log '''
def mesh_grids(text):
    blocks = text.split('Mesh structure')
    if len(blocks)<2:
        return None
    return sum(int(n) for n in re.findall(r'^\s*Level\s+\d+\s+has\s+(\d+)\s+grids', blocks[-1], re.M))


''' Number of grid and particle slots in use, summed over the MPI processes, as
    {omp: (nodes, grids, particles)}, and the number of grids of the mesh. Only the
    full-node runs, without the configurations excluded from the memory figure. '''
def allocation_fill(cluster, bench, reso):
    from tagged_data import EXCLUDED_COMPILERS

    cores = CORES_PER_NODE[cluster]
    excluded = [1]+EXCLUDED_THREADS.get(cluster, [])
    fill = {}
    reference = None
    for benchmark_dir in get_openmp_dirs(cluster, bench):
        data_dir = os.path.join(benchmark_dir, bench)
        for item in os.listdir(data_dir):
            if not item.startswith('reso'):
                continue
            run_reso, nodes, mpi, omp = (get_info_from_subdir_name(item)[0],)+tuple(
                int(value) for value in get_info_from_subdir_name(item)[1:])
            if run_reso!=reso or max(mpi, 1)*max(omp, 1)!=cores or omp in excluded:
                continue
            run_dir = os.path.join(data_dir, item)
            nprocs = nodes*mpi
            namelist = open(glob.glob(os.path.join(run_dir, '*.nml'))[0]).read()
            ngridmax = int(namelist_value(namelist, 'ngridmax') or namelist_value(namelist, 'ngridtot')/nprocs)
            npartmax = int(namelist_value(namelist, 'npartmax') or namelist_value(namelist, 'nparttot')/nprocs)
            grids, particles = [], []
            for logfile in glob.glob(os.path.join(run_dir, '*.log')):
                if skip_compiler(parse_metadata(logfile), EXCLUDED_COMPILERS):
                    continue
                text = open(logfile).read()
                # only completed runs, which print the timers
                if 'TOTAL' not in text:
                    continue
                percentages = re.findall(r'mem=\s*([\d.]+)%\s*([\d.]+)%', text)
                if len(percentages)==0:
                    continue
                # RAMSES divides by ngridmax+1 (npartmax+1)
                grids.append(max(float(g) for g, p in percentages)/100.*(ngridmax+1)*nprocs)
                particles.append(max(float(p) for g, p in percentages)/100.*(npartmax+1)*nprocs)
                reference = reference or mesh_grids(text)
            if len(grids)>0:
                fill.setdefault(omp, {})[nodes] = (np.mean(grids), np.mean(particles))
    results = {}
    for omp in sorted(fill):
        nodes = sorted(fill[omp])
        results[omp] = (nodes, [fill[omp][n][0] for n in nodes], [fill[omp][n][1] for n in nodes])
    return results, reference


''' Number of grids (top or left) and particles (bottom or right) in use, summed
    over the MPI processes, with the number of grids of the mesh and (cosmo) of
    particles as a reference. With column=True the panels are stacked. '''
def plot_allocation_paper(cluster, bench, reso, column=False, outname='memory_fill_paper.png'):

    results, mesh = allocation_fill(cluster, bench, reso)
    colors, labels = config_styles(results, CORES_PER_NODE[cluster])
    references = [mesh, int(reso)**3 if bench=='cosmo' else None]

    with plt.rc_context(STYLE):
        if column:
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(3.4, 4.8), sharex=True)
            fig.subplots_adjust(hspace=0.08)
        else:
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(7.2, 3.))
            fig.subplots_adjust(wspace=0.3)

        for omp, (nodes, grids, particles) in results.items():
            style = dict(color=colors[omp], marker='o', ms=3.5, lw=1.5,
                         mfc='white' if omp==0 else colors[omp], label=labels[omp])
            axes[0].plot(nodes, np.array(grids)/1e6, **style)
            axes[1].plot(nodes, np.array(particles)/1e6, **style)
        # reference written on the line, at the right end
        for ax, reference, name in zip(axes, references, ['grids of the mesh', f'{reso}$^3$ particles']):
            if reference:
                ax.axhline(reference/1e6, color='grey', ls=':', lw=1.2, zorder=1)
                ax.annotate(name, (1., reference/1e6), xycoords=('axes fraction', 'data'),
                            xytext=(-2, -3), textcoords='offset points', ha='right', va='top',
                            fontsize=7, color='grey')

        all_nodes = sorted({n for nodes, grids, particles in results.values() for n in nodes})
        for ax in axes:
            ax.set_xscale('log')
            set_node_ticks(ax, all_nodes)
        axes[1].set_xlabel('number of nodes')
        if not column:
            axes[0].set_xlabel('number of nodes')
        axes[0].set_ylabel('grids in use [millions]')
        axes[1].set_ylabel('particles in use [millions]')
        # room for the reference under the lines and for the legend above them
        for ax, reference, top in zip(axes, references, [0.6, 0.05]):
            low, high = ax.get_ylim()
            if reference:
                low = min(low, 0.94*reference/1e6)
            ax.set_ylim(low, high+top*(high-low))
        axes[0].legend(frameon=False, fontsize=7.5, title='MPI×OMP per node', title_fontsize=7.5,
                       loc='upper left', ncol=2, handlelength=1.8, columnspacing=1.)
        if not column:
            fig.suptitle(f'{bench} {reso} on {cluster_label(cluster)}', fontsize=10)
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


''' One row of three panels: the grids in use, the particles in use (both the
    fullest process times the number of processes, see allocation_fill) and the
    memory per node, with ideal scaling of the MPI-only run on one node. '''
def plot_memory_row(cluster, bench, reso, outname='memory_row_paper.png'):

    fill, mesh = allocation_fill(cluster, bench, reso)
    memory = memory_per_config(cluster, bench, reso)
    colors, labels = config_styles(memory, CORES_PER_NODE[cluster])
    # (values per configuration, unit, reference, its label, y-axis label)
    panels = [
        ({omp: (nodes, grids) for omp, (nodes, grids, particles) in fill.items()}, 1e8,
         mesh, 'grids of the mesh', r'max grids in use [$10^8$]'),
        ({omp: (nodes, particles) for omp, (nodes, grids, particles) in fill.items()}, 1e9,
         int(reso)**3 if bench=='cosmo' else None, f'{reso}$^3$ particles', r'max particles in use [$10^9$]'),
        (memory, 1., None, None, 'memory per node [GB]'),
    ]

    # same size, font size and resolution as the speedup figure of Section 4
    # (openmp_best_speedup.py), so that both have the same shape in the paper
    with plt.rc_context({**STYLE, 'font.size': 10}):
        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(3.6*3, FIG_HEIGHT))
        fig.subplots_adjust(wspace=0.32)
        all_nodes = sorted({n for nodes, values in memory.values() for n in nodes})

        for ax, (values, unit, reference, ref_label, ylabel) in zip(axes, panels):
            for omp, (nodes, data) in values.items():
                ax.plot(nodes, np.array(data)/unit, color=colors[omp], marker='o', ms=3.5, lw=1.5,
                        mfc='white' if omp==0 else colors[omp], label=labels[omp])
            # reference written on the line, at the right end
            if reference:
                ax.axhline(reference/unit, color='grey', ls=':', lw=1.2, zorder=1)
                ax.annotate(ref_label, (1., reference/unit), xycoords=('axes fraction', 'data'),
                            xytext=(-2, -3), textcoords='offset points', ha='right', va='top',
                            fontsize=8.5, color='grey')
                low, high = ax.get_ylim()
                ax.set_ylim(min(low, reference/unit-0.12*(high-low)), high)
            ax.set_xscale('log')
            set_node_ticks(ax, all_nodes)
            ax.set_xlabel('number of nodes')
            ax.set_ylabel(ylabel)

        mpi_nodes, mpi_memory = memory[0]
        axes[2].plot([1, max(mpi_nodes)], [mpi_memory[0], mpi_memory[0]/max(mpi_nodes)], color='black',
                     ls=':', lw=1.2, label='ideal', zorder=1)
        axes[2].set_yscale('log')
        # room for the legend above the lines of the first panel
        low, high = axes[0].get_ylim()
        axes[0].set_ylim(low, high+0.6*(high-low))
        # two legends: the configurations, and the ideal scaling
        handles, leg_labels = axes[2].get_legend_handles_labels()
        entries = dict(zip(leg_labels, handles))
        configs = [label for label in leg_labels if label!='ideal']
        axes[0].legend([entries[label] for label in configs], configs, frameon=False,
                                       fontsize=8.5, title='MPI×OMP per node', title_fontsize=8.5,
                                       loc='upper left', ncol=2, handlelength=1.8, columnspacing=1.)
        # in the empty lower left corner of the memory panel, next to the ideal scaling
        axes[2].legend([entries['ideal']], ['ideal (MPI-only)'],
                       frameon=False, fontsize=8.5, loc='lower left', handlelength=1.8)
        plt.savefig(outname, dpi=DPI, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


''' Memory per node (top or left) and memory relative to MPI-only (bottom or right).
    With column=True the panels are stacked, to fit in one column of the paper. '''
def plot_memory_paper(cluster, bench, reso, factor=False, column=False, outname='memory_paper.png'):

    results = memory_per_config(cluster, bench, reso)
    cores = CORES_PER_NODE[cluster]
    mpi_nodes, mpi_memory = results[0]
    reference = dict(zip(mpi_nodes, mpi_memory))
    colors, labels = config_styles(results, cores)

    with plt.rc_context(STYLE):
        if column:
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(3.4, 4.8), sharex=True)
            fig.subplots_adjust(hspace=0.08)
        else:
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(7.2, 3.))
            fig.subplots_adjust(wspace=0.3)

        for omp, (nodes, memory) in results.items():
            style = dict(color=colors[omp], marker='o', ms=3.5, lw=1.5,
                         mfc='white' if omp==0 else colors[omp], label=labels[omp])
            axes[0].plot(nodes, memory, **style)
            common = [n for n in nodes if n in reference]
            relative = np.array([memory[nodes.index(n)]/reference[n] for n in common])
            axes[1].plot(common, 1./relative if factor else relative, **style)
        axes[0].plot([1, max(mpi_nodes)], [reference[1], reference[1]/max(mpi_nodes)], color='black',
                     ls=':', lw=1.2, label='ideal', zorder=1)

        all_nodes = sorted({n for nodes, memory in results.values() for n in nodes})
        for ax in axes:
            ax.set_xscale('log')
            ax.set_yscale('log')
            set_node_ticks(ax, all_nodes)
        axes[1].set_xlabel('number of nodes')
        if not column:
            axes[0].set_xlabel('number of nodes')
        axes[0].set_ylabel('memory per node [GB]')
        prefix = '×' if factor else ''
        axes[1].set_ylabel(('reduction w.r.t. MPI-only' if column else 'memory reduction w.r.t. MPI-only') if factor else 'memory relative to MPI-only')
        axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda value, pos: f'{prefix}{value:g}'))
        axes[1].yaxis.set_minor_formatter(plt.FuncFormatter(
            lambda value, pos: f'{prefix}{value:g}' if round(value/10**np.floor(np.log10(value))) in (2, 5) else ''))
        # legend in the empty upper (factor) or lower (relative) left corner of the right panel
        handles, leg_labels = axes[0].get_legend_handles_labels()
        axes[1].legend(handles, leg_labels, frameon=False, fontsize=7.5, title='MPI×OMP per node',
                       title_fontsize=7.5, loc='upper left' if factor else 'lower left', handlelength=1.8)
        # the caption names the benchmark in the paper version
        if not column:
            fig.suptitle(f'{bench} {reso} on {cluster_label(cluster)}', fontsize=10)
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Memory gain of the hybrid configurations (paper figure)')
    parser.add_argument('-c', '--cluster', default='lumi', help='Cluster name')
    parser.add_argument('-b', '--benchmark', default='cosmo', help='Benchmark setup name')
    parser.add_argument('-r', '--reso', default='1024', help='Resolution')
    parser.add_argument('--factor', action='store_true',
                        help='Show the reduction factor M_MPI/M_hybrid instead of the relative memory')
    parser.add_argument('--column', action='store_true',
                        help='Panels stacked vertically, to fit in one column of the paper')
    parser.add_argument('--fill', action='store_true',
                        help='Number of grids and particles in use instead of the memory')
    parser.add_argument('--row', action='store_true',
                        help='One row: grids in use, particles in use and memory per node')
    args = parser.parse_args()

    if args.row:
        plot_memory_row(args.cluster, args.benchmark, args.reso,
                        outname=f'memory_row_paper_{args.benchmark}_{args.reso}_{args.cluster}.png')
        exit(0)
    if args.fill:
        suffix = '_column' if args.column else ''
        plot_allocation_paper(args.cluster, args.benchmark, args.reso, column=args.column,
                              outname=f'memory_fill_paper{suffix}_{args.benchmark}_{args.reso}_{args.cluster}.png')
        exit(0)

    suffix = ('_factor' if args.factor else '')+('_column' if args.column else '')
    plot_memory_paper(args.cluster, args.benchmark, args.reso, factor=args.factor, column=args.column,
                      outname=f'memory_paper{suffix}_{args.benchmark}_{args.reso}_{args.cluster}.png')
