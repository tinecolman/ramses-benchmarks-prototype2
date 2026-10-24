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

Run from the visu directory:
    python mpi_module_share.py -c marenostrum
    python mpi_module_share.py -c marenostrum -s lines
'''

from matplotlib import pyplot as plt
import matplotlib.lines as mlines
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import (MODULE_COLORS, STYLE, index_runs, module_times,
                                    module_labels_colors)
from io_timings import set_node_ticks
from openmp_best_speedup import get_openmp_dirs

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


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Share of the total time spent in every module for the MPI-only runs')

    parser.add_argument('-c', '--cluster', default='marenostrum', help='Cluster name')
    parser.add_argument('-s', '--style', default='stacked', choices=['stacked', 'lines'],
                        help='Stacked areas or one line per module')

    args = parser.parse_args()

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
    for bench, reso in BENCHMARKS:
        entries = load_timer_breakdown(get_openmp_dirs(args.cluster, bench), bench, reso,
                                       exclude_compilers=EXCLUDED_COMPILERS)
        plot_mpi_module_share(entries, order_modules(DESCRIPTION_MODULES[bench]),
                              legend_names=legend_names[bench], legend_rows=legend_rows,
                              lines=args.style=='lines', title=f'{bench} {reso}',
                              outname=f'mpi_module_share{suffix}_{bench}_{reso}_{args.cluster}.png')
