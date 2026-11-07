from matplotlib import pyplot as plt
import matplotlib.lines as mlines
from resolutions import get_weak_scaling_config2
from openmp_best_speedup import (load_openmp_data, best_openmp_times, get_cluster_colors,
                                 get_linestyle, set_nodes_axis, older_version_handles, cluster_label)
from openmp_best_scaling import annotate_efficiency

# benchmarks shown in the figure, one column each. The galaxy benchmark has no weak scaling.
WEAK_BENCHMARKS = ['sedov', 'cosmo']


# resolution of the saved figures, high enough to stay sharp in the paper
DPI = 400


''' Weak scaling efficiency of the MPI-only runs and of the fastest MPI-OpenMP
    configuration, each with respect to its own smallest number of nodes, in percent.
    The resolution increases with the number of nodes following weak_scaling_map.
    The gain of OpenMP with respect to MPI-only on the same number of nodes
    is shown in the figure of openmp_best_speedup.py.
    Returns the numbers of nodes and efficiencies of MPI-only and of the best
    MPI-OpenMP runs. '''
def best_openmp_weak_scaling(data, weak_scaling_map):

    mpi_times = {}
    omp_times = {}
    for reso, nnodes in weak_scaling_map.items():
        mpi_reso, omp_reso = best_openmp_times(data, reso)
        if nnodes in mpi_reso:
            mpi_times[nnodes] = mpi_reso[nnodes]
        if nnodes in omp_reso:
            omp_times[nnodes] = omp_reso[nnodes][0]

    curves = []
    for times in [mpi_times, omp_times]:
        nodes = sorted(times)
        curves += [nodes, [100.*times[nodes[0]]/times[nnodes] for nnodes in nodes]]

    return curves


''' Plot the weak scaling efficiency of MPI-only (thin lines) and of the best
    MPI-OpenMP configuration (thick lines) as a function of the number of nodes.
    There is one column per benchmark and one row per cluster. '''
def plot_best_openmp_weak_scaling(clusters, benchmarks=WEAK_BENCHMARKS, timer='total',
                                  cmap_name='tab10', fig_name='omp_best_weak_scaling.png'):

    results = {}
    for bench in benchmarks:
        weak_scaling_map = get_weak_scaling_config2(bench)
        for cluster in clusters:
            data = load_openmp_data(cluster, bench, timer)
            mpi_nodes, mpi_effs, omp_nodes, omp_effs = best_openmp_weak_scaling(data, weak_scaling_map)
            if len(mpi_nodes)==0 or len(omp_nodes)==0:
                print('[OMP best weak scaling] No data to compare for', cluster, bench)
                continue
            results[(bench, cluster)] = (mpi_nodes, mpi_effs, omp_nodes, omp_effs)

    if len(results)==0:
        print('[OMP best weak scaling] No data available')
        return 1

    colors = get_cluster_colors(clusters, cmap_name)

    fig, axes = plt.subplots(nrows=len(clusters), ncols=len(benchmarks),
                             figsize=(2.1*len(benchmarks), 2.0*len(clusters)),
                             sharex='col', sharey=True, squeeze=False)
    fig.subplots_adjust(wspace=0.08, hspace=0.08)

    for icol, bench in enumerate(benchmarks):
        weak_scaling_map = get_weak_scaling_config2(bench)

        # the panels of a column share the numbers of nodes
        column_nodes = set()
        for cluster in clusters:
            if (bench, cluster) in results:
                mpi_nodes, mpi_effs, omp_nodes, omp_effs = results[(bench, cluster)]
                column_nodes.update(mpi_nodes + omp_nodes)

        for irow, cluster in enumerate(clusters):
            ax = axes[irow, icol]

            # ideal weak scaling
            ax.axhline(100., color='lightgrey', lw=1.5, zorder=0)

            if (bench, cluster) in results:
                mpi_nodes, mpi_effs, omp_nodes, omp_effs = results[(bench, cluster)]
                ls = get_linestyle(cluster, bench)

                ax.plot(mpi_nodes, mpi_effs, color=colors[cluster], ls=ls, lw=1, alpha=0.6,
                        marker='o', markersize=3)
                ax.plot(omp_nodes, omp_effs, color=colors[cluster], ls=ls,
                        marker='o', markersize=4)
                # compare the efficiencies on the highest number of nodes available for both
                common_nodes = set(mpi_nodes) & set(omp_nodes)
                if len(common_nodes)>0:
                    nnodes = max(common_nodes)
                    mpi_eff = mpi_effs[mpi_nodes.index(nnodes)]
                    omp_eff = omp_effs[omp_nodes.index(nnodes)]
                    # write the lowest efficiency below its point
                    annotate_efficiency(ax, nnodes, mpi_eff, mpi_eff, colors[cluster],
                                        -4 if mpi_eff<=omp_eff else 4)
                    annotate_efficiency(ax, nnodes, omp_eff, omp_eff, colors[cluster],
                                        4 if mpi_eff<=omp_eff else -4)
            else:
                ax.text(0.5, 0.5, 'no data', transform=ax.transAxes, ha='center', va='center',
                        color='grey')

            set_nodes_axis(ax, column_nodes)
            # more room on the right for the annotations
            if len(column_nodes)>0:
                ax.set_xlim(min(column_nodes)/2.2, max(column_nodes)*2.8)
            ax.grid(axis='y', which='major', alpha=0.3)
            # only label the outer panels
            if irow==0:
                ax.set_title(bench)
            if irow<len(clusters)-1:
                ax.set_xlabel('')
            else:
                # write the resolution under the number of nodes
                nodes_reso = {nnodes: reso for reso, nnodes in weak_scaling_map.items()}
                ax.set_xticks(ax.get_xticks(), labels=[f'{nnodes:g}\n({nodes_reso.get(nnodes, "")})'
                                                       for nnodes in ax.get_xticks()], fontsize=8.5)
                ax.set_xlabel('number of nodes\n(resolution)')
            if icol==0:
                ax.set_ylabel(cluster_label(cluster), color=colors[cluster], fontweight='bold')

    axes[0,0].set_ylim(0, 119)
    axes[0,0].set_yticks([0, 25, 50, 75, 100])

    # common label left of the cluster names
    ylabel = fig.text(axes[0,0].get_position().x0-0.68/fig.get_figwidth(), 0.5,
                      'weak scaling efficiency [%]', rotation='vertical',
                      ha='right', va='center', fontsize='large')

    style_handles = [mlines.Line2D([], [], color='grey', lw=1, alpha=0.6, marker='o', markersize=3,
                                   label='MPI-only'),
                     mlines.Line2D([], [], color='grey', lw=1.5, marker='o', markersize=4,
                                   label='best hybrid'),
                     mlines.Line2D([], [], color='lightgrey', lw=1.5, label='ideal')]
    # the clusters are given by the rows, so only the line styles are in the legend,
    # on two rows to fit above the two columns
    handles = style_handles + older_version_handles([(bench, None, cluster) for bench, cluster in results])
    legend = fig.legend(handles=handles, loc='lower center', ncol=(len(handles)+1)//2, frameon=False, fontsize=9,
                        bbox_to_anchor=(0.5, axes[0,0].get_position().y1+0.03))

    print(fig_name)
    # legends outside of the axes are not taken into account by default to fit the figure
    plt.savefig(fig_name, bbox_inches='tight', bbox_extra_artists=[legend, ylabel], dpi=DPI)
    plt.close()

    return 0


if __name__ == '__main__':

    #--------- Get command line input ------------
    import argparse
    parser = argparse.ArgumentParser(
        description='Weak scaling of MPI-only and of the best MPI-OpenMP configuration, for several clusters and benchmarks')

    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'], help='Cluster names')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    fig_name=f'omp_best_weak_scaling_{args.timer}_{"_".join(args.clusters)}.png'

    error = plot_best_openmp_weak_scaling(args.clusters, timer=args.timer, fig_name=fig_name)
    if not error:
        print(f'Figure outputted to {fig_name}')
