from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import matplotlib.ticker as mticker
from openmp_best_speedup import (BENCHMARKS, load_openmp_data, best_openmp_times,
                                 get_cluster_colors, get_linestyle, set_nodes_axis, add_cluster_legend, older_version_handles,
                                 benchmark_label, cluster_label)


# resolution of the saved figures, high enough to stay sharp in the paper
DPI = 400


''' Strong scaling of a curve given as {nodes: time}, with respect to its own
    smallest number of nodes n0. The speedup is multiplied by n0 so that ideal
    scaling corresponds to speedup = number of nodes for all curves.
    Returns the numbers of nodes and speedups. '''
def strong_scaling(times):
    nodes = sorted(times)
    ref = nodes[0]*times[nodes[0]]
    return nodes, [ref/times[nnodes] for nnodes in nodes]


''' Strong scaling of the MPI-only runs and of the fastest MPI-OpenMP
    configuration, each with respect to its own smallest number of nodes.
    The gain of OpenMP with respect to MPI-only on the same number of nodes
    is shown in the figure of openmp_best_speedup.py.
    Returns the numbers of nodes and speedups of MPI-only and of the best
    MPI-OpenMP runs. '''
def best_openmp_strong_scaling(data, reso):

    mpi_times, omp_times = best_openmp_times(data, reso)
    if len(mpi_times)==0 or len(omp_times)==0:
        return [], [], [], []

    mpi_nodes, mpi_speedups = strong_scaling(mpi_times)
    omp_nodes, omp_speedups = strong_scaling({nnodes: time for nnodes, (time, config) in omp_times.items()})

    return mpi_nodes, mpi_speedups, omp_nodes, omp_speedups


''' Write the efficiency (in percent) next to the point (x, y),
    above it if offset>0 and below it otherwise '''
def annotate_efficiency(ax, x, y, efficiency, color, offset):
    ax.annotate(f'{efficiency:.0f}%', (x, y),
                textcoords='offset points', xytext=(0, offset), ha='center',
                va='bottom' if offset>0 else 'top', fontsize=11, color=color)


''' Plot the strong scaling of MPI-only (thin lines) and of the best MPI-OpenMP
    configuration (thick lines) as a function of the number of nodes. There is
    one column per benchmark and one row per cluster. Which configuration is
    the fastest is shown in the figure of openmp_best_speedup.py. '''
def plot_best_openmp_strong_scaling(clusters, benchmarks=BENCHMARKS, timer='total',
                                    cmap_name='tab10', fig_name='omp_best_strong_scaling.png'):

    results = {}
    for bench, reso in benchmarks:
        for cluster in clusters:
            data = load_openmp_data(cluster, bench, timer)
            result = best_openmp_strong_scaling(data, reso)
            if len(result[0])==0:
                print('[OMP best strong scaling] No data to compare for', cluster, bench, reso)
                continue
            results[(bench, reso, cluster)] = result

    if len(results)==0:
        print('[OMP best strong scaling] No data available')
        return 1

    colors = get_cluster_colors(clusters, cmap_name)

    fig, axes = plt.subplots(nrows=len(clusters), ncols=len(benchmarks),
                             figsize=(2.9*len(benchmarks), 2.6*len(clusters)),
                             sharex='col', sharey=True, squeeze=False)
    fig.subplots_adjust(wspace=0.05, hspace=0.08)

    all_speedups = []
    for icol, (bench, reso) in enumerate(benchmarks):

        # the panels of a column share the numbers of nodes
        column_nodes = set()
        for cluster in clusters:
            if (bench, reso, cluster) in results:
                mpi_nodes, mpi_speedups, omp_nodes, omp_speedups = results[(bench, reso, cluster)]
                column_nodes.update(mpi_nodes + omp_nodes)

        for irow, cluster in enumerate(clusters):
            ax = axes[irow, icol]

            # add ideal scaling line
            if len(column_nodes)>0:
                ax.plot([min(column_nodes), max(column_nodes)], [min(column_nodes), max(column_nodes)],
                        color='lightgrey', lw=1.5, zorder=0)

            if (bench, reso, cluster) in results:
                mpi_nodes, mpi_speedups, omp_nodes, omp_speedups = results[(bench, reso, cluster)]
                ls = get_linestyle(cluster, bench)

                ax.plot(mpi_nodes, mpi_speedups, color=colors[cluster], ls=ls, lw=1, alpha=0.6,
                        marker='o', markersize=3)
                ax.plot(omp_nodes, omp_speedups, color=colors[cluster], ls=ls,
                        marker='o', markersize=4)
                # the best OpenMP mostly scales better, so its efficiency goes above the curve
                # compare the efficiencies on the highest number of nodes available for both
                common_nodes = set(mpi_nodes) & set(omp_nodes)
                if len(common_nodes)>0:
                    nnodes = max(common_nodes)
                    for nodes, speedups, offset in [(mpi_nodes, mpi_speedups, -4), (omp_nodes, omp_speedups, 4)]:
                        speedup = speedups[nodes.index(nnodes)]
                        annotate_efficiency(ax, nnodes, speedup, 100.*speedup/nnodes, colors[cluster], offset)
                all_speedups += mpi_speedups + omp_speedups
            else:
                ax.text(0.5, 0.5, 'no data', transform=ax.transAxes, ha='center', va='center',
                        color='grey')

            set_nodes_axis(ax, column_nodes)
            # more room on the right for the annotations
            if len(column_nodes)>0:
                ax.set_xlim(min(column_nodes)/1.4, max(column_nodes)*1.9)
            ax.grid(axis='y', which='major', alpha=0.3)
            # only label the outer panels
            if irow==0:
                ax.set_title(benchmark_label(bench, reso))
            if irow<len(clusters)-1:
                ax.set_xlabel('')
            if icol==0:
                ax.set_ylabel(cluster_label(cluster), color=colors[cluster], fontweight='bold')

    axes[0,0].set_yscale('log', base=2)
    # label every power of 2
    axes[0,0].yaxis.set_major_locator(mticker.LogLocator(base=2, numticks=20))
    axes[0,0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, pos: f'{value:g}'))
    axes[0,0].yaxis.set_minor_locator(mticker.NullLocator())
    # leave room above the highest points for the efficiency annotations
    axes[0,0].set_ylim(min(all_speedups)/1.4, max(all_speedups)*2.2)
    # common label left of the cluster names
    ylabel = fig.text(axes[0,0].get_position().x0-0.68/fig.get_figwidth(), 0.5,
                      'strong scaling speedup', rotation='vertical',
                      ha='right', va='center', fontsize='large')

    style_handles = [mlines.Line2D([], [], color='grey', lw=1, alpha=0.6, marker='o', markersize=3,
                                   label='MPI-only'),
                     mlines.Line2D([], [], color='grey', lw=1.5, marker='o', markersize=4,
                                   label='best hybrid'),
                     mlines.Line2D([], [], color='lightgrey', lw=1.5, label='ideal')]
    # the clusters are given by the rows, so only the line styles are in the legend
    legend = add_cluster_legend(fig, [], colors,
                                extra_handles=style_handles+older_version_handles(results),
                                y=axes[0,0].get_position().y1+0.035)

    print(fig_name)
    # legends outside of the axes are not taken into account by default to fit the figure
    plt.savefig(fig_name, bbox_inches='tight', bbox_extra_artists=[legend, ylabel], dpi=DPI)
    plt.close()

    return 0


if __name__ == '__main__':

    #--------- Get command line input ------------
    import argparse
    parser = argparse.ArgumentParser(
        description='Strong scaling of MPI-only and of the best MPI-OpenMP configuration, for several clusters and benchmarks')

    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'], help='Cluster names')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    fig_name=f'omp_best_strong_scaling_{args.timer}_{"_".join(args.clusters)}.png'

    error = plot_best_openmp_strong_scaling(args.clusters, timer=args.timer, fig_name=fig_name)
    if not error:
        print(f'Figure outputted to {fig_name}')
