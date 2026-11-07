'''
Fraction of the total time spent in every module as a function of the number
of nodes, for the MPI-only runs, with one figure per benchmark. Meant for the
description of the benchmarks, the comparison with the hybrid MPI-OpenMP
version is made by openmp_module_analysis.py.

The colors of the modules are those of MODULE_COLORS in openmp_module_analysis.py,
so that a module has the same color in the figures of all benchmarks. The
modules are stacked in the order of MODULE_COLORS (hydro, gravity, particles,
AMR), with 'other' on top.

The figures are meant to be shown together, in the order of BENCHMARKS: a
module only appears in the legend of the first figure that contains it.

The figure is made as stacked areas and as lines (one per module).

The default is one figure with a row per benchmark and a column per cluster.

Run from the visu directory:
    python mpi_module_share.py -c marenostrum lumi meluxina
    python mpi_module_share.py -c marenostrum -l single
    python mpi_module_share.py -c marenostrum -l single -s lines
'''

from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import (MODULE_COLORS, STYLE, index_runs, module_times,
                                    module_labels_colors)
from io_timings import set_node_ticks
from openmp_best_speedup import get_openmp_dirs, benchmark_label, cluster_label

# benchmarks for which a figure is made, in the order in which they are shown
BENCHMARKS = [('sedov', '1024'), ('cosmo', '1024'), ('galaxy', 'highres')]

# Modules shown separately, as {timer (group) name: label}, see MODULES_PER_BENCHMARK
# in openmp_module_analysis.py. Courant (only noticeable in sedov) and the AMR flagging
# (small everywhere) are part of 'other' here. Coarse levels is shown in all benchmarks,
# since it grows strongly with the number of MPI processes in galaxy.
DESCRIPTION_MODULES = {
    'sedov': {
        'hydro - godunov': 'hydro - godunov',
        'hydro - communication': 'hydro - communication',
        'hydro - state copy': 'hydro - state copy',
        'coarse levels': 'amr - coarse levels',
    },
    'cosmo': {
        'poisson - phi multigrid': 'gravity - multigrid',
        'poisson - rho': 'gravity - rho (CIC)',
        'particles - update': 'particles - update',
        'particles - book keeping': 'particles - book keeping',
        'coarse levels': 'amr - coarse levels',
    },
    'galaxy': {
        'hydro - godunov': 'hydro - godunov',
        'hydro - communication': 'hydro - communication',
        'poisson - phi multigrid': 'gravity - multigrid',
        'poisson - rho': 'gravity - rho (CIC)',
        'particles - book keeping': 'particles - book keeping',
        'refine': 'amr - refine',
        'coarse levels': 'amr - coarse levels',
        'load balance': 'load balance',
    },
}

# number of columns of the legends
LEGEND_NCOL = 2


''' Modules ordered as in MODULE_COLORS, i.e. grouped by part of the code '''
def order_modules(modules):
    order = list(MODULE_COLORS)
    return {name: modules[name] for name in sorted(modules, key=lambda name:
                                                   order.index(name) if name in order else len(order))}


''' Share of the total time (in %) of every module and of 'other' for the MPI-only
    runs. Returns the numbers of nodes and {name: list of shares} '''
def mpi_module_shares(entries, modules):
    runs = index_runs(entries)
    arr_nodes = sorted(n for (n, o) in runs if o==0)
    shares = {name: [100.*module_times(runs[(n, 0)], modules)[name]/runs[(n, 0)]['total']
                     for n in arr_nodes]
              for name in list(modules)+['other']}
    return arr_nodes, shares


''' Same as mpi_module_shares, for the fastest hybrid configuration of every number
    of nodes, out of those of the total speedup grid (omp_total_ratio_grid.py: no
    single thread, no excluded_threads). Also returns the configurations (mpi, omp). '''
def best_hybrid_module_shares(entries, modules, excluded_threads=()):
    runs = index_runs(entries)
    best = {}
    for (n, o), entry in runs.items():
        if o<2 or o in excluded_threads:
            continue
        if n not in best or entry['total']<runs[(n, best[n])]['total']:
            best[n] = o
    arr_nodes = sorted(best)
    shares = {name: [100.*module_times(runs[(n, best[n])], modules)[name]/runs[(n, best[n])]['total']
                     for n in arr_nodes]
              for name in list(modules)+['other']}
    configs = [(runs[(n, best[n])]['mpi_procs_per_node'], best[n]) for n in arr_nodes]
    return arr_nodes, shares, configs


''' Legend under the axes with the given (handle, label) entries. It is filled
    up to nrows rows, so that the axes of figures shown together have the same size '''
def add_legend(ax, entries, nrows):
    blank = mlines.Line2D([], [], ls='', label=' ')
    handles = [handle for handle, label in entries]
    labels = [label for handle, label in entries]
    npad = LEGEND_NCOL*nrows-len(entries)
    ax.legend(handles+[blank]*npad, labels+[' ']*npad, frameon=False, fontsize=8,
              ncol=LEGEND_NCOL, loc='upper center', bbox_to_anchor=(0.5, -0.2),
              columnspacing=1., handlelength=1.5)


''' Share of the total time spent in every module as a function of the number of
    nodes, for the MPI-only runs, with the modules stacked on top of each other.
    Only the modules in legend_names are put in the legend, filled up to
    legend_rows rows. With lines=True, one line per module is drawn instead. '''
def plot_mpi_module_share(entries, modules, legend_names=None, legend_rows=None, lines=False,
                          title='', outname='mpi_module_share.png'):

    arr_nodes, shares = mpi_module_shares(entries, modules)
    if len(arr_nodes)==0:
        print('[MPI module share] No MPI-only runs found')
        return 1

    labels, colors = module_labels_colors(modules)
    names = list(modules)+['other']
    if legend_names is None:
        legend_names = names
    if legend_rows is None:
        legend_rows = -(-len(legend_names)//LEGEND_NCOL)

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4.2, 3.))
        if lines:
            handles = {name: ax.plot(arr_nodes, shares[name], '-o', color=colors[name],
                                     lw=1.8, ms=4)[0] for name in names}
        else:
            areas = ax.stackplot(arr_nodes, [shares[name] for name in names],
                                 colors=[colors[name] for name in names],
                                 edgecolor='white', linewidth=0.5)
            handles = dict(zip(names, areas))
            ax.set_xlim(min(arr_nodes), max(arr_nodes))
            ax.grid(False)
        ax.set_xscale('log')
        set_node_ticks(ax, arr_nodes)
        ax.set_ylim(0, 100)
        ax.set_xlabel('number of nodes')
        ax.set_ylabel('% of total time')
        ax.set_title(title)

        # for the stacked areas, the module on top of the stack comes first
        legend_order = names if lines else names[::-1]
        add_legend(ax, [(handles[name], labels[name]) for name in legend_order
                        if name in legend_names], legend_rows)
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


# Groups of modules in the legend of the grid figure, separated by a gap
LEGEND_GROUPS = [
    ['hydro - godunov', 'hydro - communication', 'hydro - state copy'],
    ['poisson - phi multigrid', 'poisson - rho', 'particles - update', 'particles - book keeping'],
    ['refine', 'coarse levels', 'load balance', 'other'],
]


''' Shares of the modules of the MPI-only runs for all benchmarks and clusters, or
    of the fastest hybrid configuration with best=True.
    Returns the labels and colors of the modules, {(bench, cluster): (names,
    numbers of nodes, shares, configurations or None)} and the numbers of nodes of
    all panels. '''
def gather_module_shares(clusters, benchmarks, best=False):
    from tagged_data import EXCLUDED_COMPILERS
    # same configurations as the stars of the total speedup grid
    from omp_total_ratio_grid import GRID_EXCLUDED_THREADS

    labels = {}
    colors = {}
    results = {}
    for bench, reso in benchmarks:
        modules = order_modules(DESCRIPTION_MODULES[bench])
        bench_labels, bench_colors = module_labels_colors(modules)
        labels.update(bench_labels)
        colors.update(bench_colors)
        for cluster in clusters:
            entries = load_timer_breakdown(get_openmp_dirs(cluster, bench), bench, reso,
                                           exclude_compilers=EXCLUDED_COMPILERS)
            if best:
                arr_nodes, shares, configs = best_hybrid_module_shares(
                    entries, modules, GRID_EXCLUDED_THREADS.get(cluster, []))
            else:
                arr_nodes, shares = mpi_module_shares(entries, modules)
                configs = None
            if len(arr_nodes)==0:
                print('[MPI module share] No runs found for', cluster, bench, reso)
                continue
            results[(bench, cluster)] = (list(modules)+['other'], arr_nodes, shares, configs)
    all_nodes = sorted({n for names, arr_nodes, shares, configs in results.values() for n in arr_nodes})
    return labels, colors, results, all_nodes


''' Stacked shares of one panel. With a common x-axis, the runs that do not go up
    to the highest number of nodes end before the right edge of the panel. For the
    fastest hybrid configurations, the configuration is written above the panel
    at every number of nodes. '''
def plot_share_panel(ax, results, key, colors, all_nodes, common_xaxis=True, config_size=6):
    if key in results:
        names, arr_nodes, shares, configs = results[key]
        ax.stackplot(arr_nodes, [shares[name] for name in names],
                     colors=[colors[name] for name in names],
                     edgecolor='white', linewidth=0.5)
        for nodes, (mpi, omp) in zip(arr_nodes if configs else [], configs or []):
            ax.text(nodes, 101, f'{mpi}×{omp}', rotation=90, ha='center', va='bottom',
                    fontsize=config_size, clip_on=False)
    else:
        ax.text(0.5, 0.5, 'no data', transform=ax.transAxes, ha='center', va='center',
                color='grey')
        arr_nodes = all_nodes
    panel_nodes = all_nodes if common_xaxis else arr_nodes
    ax.set_xscale('log')
    set_node_ticks(ax, panel_nodes)
    ax.set_xlim(min(panel_nodes), max(panel_nodes))
    ax.grid(False)
    ax.set_ylim(0, 100)
    ax.tick_params(axis='x', labelsize=8)


''' Share of the total time spent in every module as stacked areas, as a function of
    the number of nodes, for the MPI-only runs: one row per benchmark and one column
    per cluster. The legend is shared, right of the figure, with the modules grouped
    by part of the code (LEGEND_GROUPS). With common_xaxis, all panels span the same
    range of numbers of nodes, so that it shows which runs stop at fewer nodes. '''
def plot_mpi_module_share_grid(clusters, benchmarks=BENCHMARKS, common_xaxis=True, best=False,
                               outname='mpi_module_share_grid.png'):

    labels, colors, results, all_nodes = gather_module_shares(clusters, benchmarks, best)

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(nrows=len(benchmarks), ncols=len(clusters),
                                 figsize=(2.3*len(clusters), 2.*len(benchmarks)),
                                 sharex=common_xaxis, sharey=True, squeeze=False)
        fig.subplots_adjust(wspace=0.15, hspace=0.3 if not common_xaxis or best else 0.12)

        for irow, (bench, reso) in enumerate(benchmarks):
            for icol, cluster in enumerate(clusters):
                ax = axes[irow, icol]
                plot_share_panel(ax, results, (bench, cluster), colors, all_nodes, common_xaxis)
                # only label the outer panels
                if irow==0:
                    ax.set_title(cluster_label(cluster), fontweight='bold', pad=22 if best else None)
                if irow==len(benchmarks)-1:
                    ax.set_xlabel('number of nodes')
                if icol==0:
                    ax.set_ylabel(benchmark_label(bench, reso), fontweight='bold')

        # common label left of the benchmark names
        ylabel = fig.text(axes[0,0].get_position().x0-0.72/fig.get_figwidth(), 0.5,
                          '% of total time', rotation='vertical', ha='right', va='center',
                          fontsize='large')

        # shared legend right of the figure, with a gap between the groups of modules.
        # The groups follow LEGEND_GROUPS, so that hydro is next to the sedov panels,
        # and within a group the modules are in the order of the stack (top first)
        handles = []
        for group in LEGEND_GROUPS:
            group = [name for name in group if name in colors]
            if len(handles)>0 and len(group)>0:
                handles.append(mpatches.Patch(color='none', label=' '))
            handles += [mpatches.Patch(color=colors[name], label=labels[name]) for name in group[::-1]]
        legends = [fig.legend(handles=handles, ncol=1, frameon=False, fontsize=9,
                              handlelength=1.2, handletextpad=0.6, loc='center left',
                              bbox_to_anchor=(axes[0,-1].get_position().x1+0.15/fig.get_figwidth(),
                                              0.5*(axes[0,-1].get_position().y1+axes[-1,-1].get_position().y0)))]

        plt.savefig(outname, dpi=200, bbox_inches='tight', bbox_extra_artists=legends+[ylabel])
        plt.close()

    print(outname)
    return 0


''' Same as plot_mpi_module_share_grid, transposed: one row per cluster and one
    column per benchmark, with the legend under the panels (one column per group
    of LEGEND_GROUPS, top of the stack first). Meant for a single cluster. '''
def plot_mpi_module_share_row(clusters, benchmarks=BENCHMARKS, common_xaxis=True, best=False,
                              outname='mpi_module_share_row.png'):

    # same width, benchmark names and font sizes as the module figure, which imports
    # from this file
    from omp_module_gain_paper import FIG_WIDTH, TITLE_SIZE, LABEL_SIZE, TICK_SIZE

    labels, colors, results, all_nodes = gather_module_shares(clusters, benchmarks, best)

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(nrows=len(clusters), ncols=len(benchmarks),
                                 figsize=(FIG_WIDTH, 0.3*FIG_WIDTH*len(clusters)),
                                 sharex=common_xaxis, sharey=True, squeeze=False)
        # room for the configurations above the panels
        fig.subplots_adjust(left=0.08, right=1., wspace=0.22, hspace=0.35 if best else 0.12)

        for irow, cluster in enumerate(clusters):
            for icol, (bench, reso) in enumerate(benchmarks):
                ax = axes[irow, icol]
                plot_share_panel(ax, results, (bench, cluster), colors, all_nodes, common_xaxis)
                ax.tick_params(labelsize=TICK_SIZE)
                if irow==0:
                    ax.set_title(benchmark_label(bench, reso), fontsize=TITLE_SIZE,
                                 pad=22 if best else None)
                if irow==len(clusters)-1:
                    ax.set_xlabel('number of nodes', fontsize=LABEL_SIZE)
                if icol==0:
                    ax.set_ylabel('% of total time' if len(clusters)==1
                                  else f'{cluster}\n% of total time', fontsize=LABEL_SIZE)

        # shared legend under the panels, one column per group of modules. The legend
        # is filled column by column, so the groups are padded to the same length.
        blank = mpatches.Patch(color='none', label=' ')
        columns = []
        for group in LEGEND_GROUPS:
            group = [name for name in group if name in colors]
            columns.append([mpatches.Patch(color=colors[name], label=labels[name]) for name in group[::-1]])
        nrows = max(len(column) for column in columns)
        handles = [handle for column in columns for handle in column+[blank]*(nrows-len(column))]
        legends = [fig.legend(handles=handles, ncol=len(columns), frameon=False, fontsize=LABEL_SIZE,
                              handlelength=1.2, handletextpad=0.6, columnspacing=1.5,
                              loc='upper center',
                              bbox_to_anchor=(0.5*(axes[-1,0].get_position().x0+axes[-1,-1].get_position().x1),
                                              axes[-1,0].get_position().y0-0.5/fig.get_figheight()))]

        plt.savefig(outname, dpi=200, bbox_inches='tight', bbox_extra_artists=legends)
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Share of the total time spent in every module for the MPI-only runs')

    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'],
                        help='Cluster names')
    parser.add_argument('-l', '--layout', default='grid', choices=['grid', 'row', 'single'],
                        help='One figure with a row per benchmark and a column per cluster (grid), '
                             'with a row per cluster and a column per benchmark (row), '
                             'or one figure per benchmark and cluster (single)')
    parser.add_argument('-b', '--best', action='store_true',
                        help='Shares of the fastest hybrid configuration instead of MPI-only '
                             '(grid and row layouts)')
    parser.add_argument('-s', '--style', default='stacked', choices=['stacked', 'lines'],
                        help='Stacked areas or one line per module, for the single layout')

    args = parser.parse_args()

    if args.layout=='grid':
        prefix = 'best_hybrid' if args.best else 'mpi'
        plot_mpi_module_share_grid(args.clusters, best=args.best,
                                   outname=f'{prefix}_module_share_{"_".join(args.clusters)}.png')
        exit(0)
    if args.layout=='row':
        prefix = 'best_hybrid' if args.best else 'mpi'
        plot_mpi_module_share_row(args.clusters, best=args.best,
                                  outname=f'{prefix}_module_share_row_{"_".join(args.clusters)}.png')
        exit(0)

    # a module only appears in the legend of the first figure that contains it
    legend_names = {}
    shown = set()
    for bench, reso in BENCHMARKS:
        names = list(DESCRIPTION_MODULES[bench])+['other']
        legend_names[bench] = [name for name in names if name not in shown]
        shown.update(names)
    # same number of legend rows in all figures, so that their axes have the same size
    legend_rows = max(-(-len(names)//LEGEND_NCOL) for names in legend_names.values())

    from tagged_data import EXCLUDED_COMPILERS
    suffix = '_lines' if args.style=='lines' else ''
    for cluster in args.clusters:
        for bench, reso in BENCHMARKS:
            entries = load_timer_breakdown(get_openmp_dirs(cluster, bench), bench, reso,
                                           exclude_compilers=EXCLUDED_COMPILERS)
            plot_mpi_module_share(entries, order_modules(DESCRIPTION_MODULES[bench]),
                                  legend_names=legend_names[bench], legend_rows=legend_rows,
                                  lines=args.style=='lines', title=benchmark_label(bench, reso),
                                  outname=f'mpi_module_share{suffix}_{bench}_{reso}_{cluster}.png')
