'''
Contribution of every module to the speedup S = t_MPI/t_hybrid of the fastest
hybrid MPI-OpenMP configuration with respect to MPI-only, as a function of the
number of nodes. One row per benchmark and one column per cluster, as in
mpi_module_share.py, with the same colors and legend.

The contribution of a module is the time it saves, t_MPI,m - t_hybrid,m, in
percent of the MPI-only total time, so that the contributions add up to the net
gain 1 - t_hybrid/t_MPI (black marker). The gains are stacked upwards and the
losses downwards from zero. The axis on the right of every row gives the
speedup S = t_MPI/t_hybrid corresponding to a net gain. The marker gives the
configuration (MPI x OMP per node), with the shapes of openmp_best_speedup.py.

Run from the visu directory:
    python omp_gain_decomposition.py -c marenostrum lumi meluxina
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import STYLE, index_runs, module_times, module_labels_colors
from openmp_best_speedup import (get_openmp_dirs, assign_config_markers, add_config_legend,
                                 MARKER_SIZE, MARKER_SCALE, benchmark_label, cluster_label)
from mpi_module_share import BENCHMARKS, DESCRIPTION_MODULES, LEGEND_GROUPS, order_modules
from omp_module_gain_heatmap import EXCLUDED_THREADS

# horizontal extent of the panels, as fractions of the figure width
LEFT = 0.12
RIGHT = 0.945
# speedups marked on the axis on the right, a loss written as ÷ and a gain as ×
SPEEDUP_TICKS = [1/2., 1/1.5, 1/1.2, 1., 1.2, 1.5, 2., 3., 5.]


''' Fastest hybrid configuration on every number of nodes and the contribution of
    every module to its gain, in percent of the MPI-only total time. Returns the
    numbers of nodes, the configurations (mpi, omp), the net gains and {name: list
    of contributions}. '''
def gain_decomposition(entries, modules, excluded_threads=()):
    runs = {key: entry for key, entry in index_runs(entries).items() if key[1] not in excluded_threads}
    names = list(modules)+['other']

    arr_nodes, configs, net = [], [], []
    gains = {name: [] for name in names}
    for nodes in sorted(n for (n, o) in runs if o==0):
        hybrid = [o for (n, o) in runs if n==nodes and o>0]
        if len(hybrid)==0:
            continue
        omp = min(hybrid, key=lambda o: runs[(nodes, o)]['total'])
        ref, best = runs[(nodes, 0)], runs[(nodes, omp)]
        ref_times, best_times = module_times(ref, modules), module_times(best, modules)
        arr_nodes.append(nodes)
        configs.append((best['mpi_procs_per_node'], omp))
        net.append(100.*(ref['total']-best['total'])/ref['total'])
        for name in names:
            gains[name].append(100.*(ref_times[name]-best_times[name])/ref['total'])

    return arr_nodes, configs, net, gains


''' Loss as ÷1.5 and gain as ×1.5 '''
def ratio_label(value, pos=None):
    if np.isclose(value, 1.):
        return '1'
    return f'×{value:g}' if value>1. else f'÷{1./value:.3g}'


''' Contributions of the modules to the gain of the fastest hybrid configuration,
    as stacked bars: one row per benchmark and one column per cluster, with the
    legend of mpi_module_share.py under the figure. '''
def plot_gain_decomposition_grid(clusters, benchmarks=BENCHMARKS, outname='omp_gain_decomposition.png'):
    from tagged_data import EXCLUDED_COMPILERS

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
            result = gain_decomposition(entries, modules, EXCLUDED_THREADS.get(cluster, []))
            if len(result[0])==0:
                print('[Gain decomposition] No runs to compare for', cluster, bench, reso)
                continue
            results[(bench, cluster)] = (list(modules)+['other'],)+result
    all_nodes = sorted({n for names, arr_nodes, *rest in results.values() for n in arr_nodes})
    # same marker per configuration as in the speedup figure, which has the same best configurations
    markers, core_configs = assign_config_markers([configs for names, arr_nodes, configs, *rest
                                                   in results.values()])

    # same width, benchmark names and font sizes as the module figure
    from omp_module_gain_paper import FIG_WIDTH, TITLE_SIZE, LABEL_SIZE, TICK_SIZE

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(nrows=len(benchmarks), ncols=len(clusters),
                                 figsize=(FIG_WIDTH, 0.85*FIG_WIDTH),
                                 sharex=True, sharey='row', squeeze=False)
        fig.subplots_adjust(left=LEFT, right=RIGHT, wspace=0.1, hspace=0.15)

        for irow, (bench, reso) in enumerate(benchmarks):
            low, high = 0., 0.
            for icol, cluster in enumerate(clusters):
                ax = axes[irow, icol]
                ax.axhline(0., color='#333333', lw=0.8, zorder=1)
                if (bench, cluster) not in results:
                    ax.text(0.5, 0.5, 'no data', transform=ax.transAxes, ha='center', va='center',
                            color='grey')
                else:
                    names, arr_nodes, configs, net, gains = results[(bench, cluster)]
                    # bars at log2 of the number of nodes, so that all panels share the x-axis
                    xpos = np.log2(arr_nodes)
                    up = np.zeros(len(arr_nodes))
                    down = np.zeros(len(arr_nodes))
                    for name in names:
                        gain = np.array(gains[name])
                        pos = np.where(gain>0., gain, 0.)
                        neg = np.where(gain<0., gain, 0.)
                        ax.bar(xpos, pos, bottom=up, color=colors[name], width=0.7,
                               edgecolor='white', lw=0.5, zorder=2)
                        ax.bar(xpos, neg, bottom=down, color=colors[name], width=0.7,
                               edgecolor='white', lw=0.5, zorder=2)
                        up += pos
                        down += neg
                    # white edge, to be visible on the dark bars
                    for x, value, config in zip(xpos, net, configs):
                        ax.plot(x, value, marker=markers[config], color='black', mec='white', mew=0.6,
                                ms=0.9*MARKER_SIZE*MARKER_SCALE.get(markers[config], 1.), zorder=4)
                    low, high = min(low, down.min()), max(high, up.max())
                ax.grid(False)
                ax.grid(axis='y', which='major', color='#e6e6e6', lw=0.6, zorder=0)
                ax.set_xticks(np.log2(all_nodes), labels=[str(n) for n in all_nodes], fontsize=TICK_SIZE)
                ax.tick_params(axis='y', labelsize=TICK_SIZE)
                ax.set_xlim(np.log2(all_nodes[0])-0.6, np.log2(all_nodes[-1])+0.6)
                if irow==0:
                    ax.set_title(cluster_label(cluster), fontsize=TITLE_SIZE)
                if irow==len(benchmarks)-1:
                    ax.set_xlabel('number of nodes', fontsize=LABEL_SIZE)
                if icol==0:
                    ax.set_ylabel(benchmark_label(bench, reso), fontsize=TITLE_SIZE)
            span = high-low
            axes[irow, 0].set_ylim(low-0.05*span, high+0.08*span)
            axes[irow, 0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, pos: f'{value:g}%'))
            # speedup corresponding to a net gain, on the right of the row
            gain_low, gain_high = axes[irow, 0].get_ylim()
            right = axes[irow, -1].twinx()
            right.set_ylim(gain_low, gain_high)
            ticks = [speedup for speedup in SPEEDUP_TICKS if gain_low<=100.*(1.-1./speedup)<=gain_high]
            right.set_yticks([100.*(1.-1./speedup) for speedup in ticks],
                             labels=[ratio_label(speedup) for speedup in ticks], fontsize=TICK_SIZE)
            right.tick_params(axis='y', colors='#555555')
            right.grid(False)
            right.spines['right'].set_visible(True)
            right.spines['top'].set_visible(False)
            if irow==len(benchmarks)//2:
                right.set_ylabel('total speedup', color='#555555', fontsize=LABEL_SIZE)

        # common label left of the benchmark names
        ylabel = fig.text(axes[0,0].get_position().x0-0.7/fig.get_figwidth(), 0.5,
                          'gain w.r.t. MPI-only [% of MPI-only time]', rotation='vertical',
                          ha='right', va='center', fontsize=LABEL_SIZE)

        # shared legend under the figure, one column per group of mpi_module_share.py.
        # The legend is filled column by column.
        blank = mpatches.Patch(color='none', label=' ')
        columns = []
        for group in LEGEND_GROUPS:
            columns.append([mpatches.Patch(color=colors[name], label=labels[name])
                            for name in group if name in colors])
        nrows = max(len(column) for column in columns)
        handles = [handle for column in columns for handle in column+[blank]*(nrows-len(column))]
        center = 0.5*(axes[-1,0].get_position().x0+axes[-1,-1].get_position().x1)
        legends = [fig.legend(handles=handles, ncol=len(columns), frameon=False, fontsize=LABEL_SIZE,
                              handlelength=1.2, handletextpad=0.6, columnspacing=1.5,
                              loc='upper center',
                              bbox_to_anchor=(center, axes[-1,0].get_position().y0-0.5/fig.get_figheight()))]
        # legend of the configurations (markers of the net gain) under it
        fig.canvas.draw()
        bottom = legends[0].get_window_extent().transformed(fig.transFigure.inverted()).y0
        legends.append(add_config_legend(fig, core_configs, markers, loc='upper center', frameon=False,
                                         bbox_to_anchor=(center, bottom-0.1/fig.get_figheight())))
        legends[-1].set_title('net gain of the best configuration (MPI×OMP)', prop={'size': LABEL_SIZE})

        plt.savefig(outname, dpi=200, bbox_inches='tight', bbox_extra_artists=legends+[ylabel])
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Contribution of every module to the speedup of the fastest hybrid configuration')
    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'],
                        help='Cluster names')
    args = parser.parse_args()

    plot_gain_decomposition_grid(args.clusters,
                                 outname=f'omp_gain_decomposition_{"_".join(args.clusters)}.png')
