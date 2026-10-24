from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import matplotlib.ticker as mticker
from io_timings import process_times
from openmp_nthreads_execution_time import select_full_node_runs, collect_timings, pad_limits

# benchmarks shown in the figure, one column each
BENCHMARKS = [('sedov', '1024'), ('cosmo', '1024'), ('galaxy', 'highres')]

# marker shapes for the MPI×OMP configurations
MARKERS = ['8', 'h', 's', '^', 'P',
           '*', 'o', 'H', 'D', 'v', '.', '.']
# scaling of the marker sizes, so that all shapes look equally large
MARKER_SCALE = {'s': 0.8, 'D': 0.85, '*': 1.35}
MARKER_SIZE = 7

# colors of the clusters, marenostrum is the darkest while the other two are
# respectively darker and lighter than the grey of the legend markers
CLUSTER_COLORS = {'marenostrum': '#1F3A68', 'lumi': '#B5462F', 'meluxina': '#CC9124'}

# (cluster, benchmark) for which the latest OpenMP version has not been run,
# so the data of an older version is used instead. These are plotted dashed.
OLDER_VERSION_DIRS = {
    ('meluxina', 'sedov'): 'benchmark_openmp_2026-05-20_e9846974',
    ('meluxina', 'cosmo'): 'benchmark_openmp_2026-05-20_e9846974',
}
OLDER_VERSION_HOME = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE_OPENMP_DEV'


''' Benchmark directories holding the latest OpenMP version, or an older one if
    specified in OLDER_VERSION_DIRS '''
def get_openmp_dirs(cluster, bench):
    from tagged_data import get_latest_openmp_dirs

    if (cluster, bench) in OLDER_VERSION_DIRS:
        return [f'{OLDER_VERSION_HOME}/{cluster}/{OLDER_VERSION_DIRS[(cluster, bench)]}/']
    return get_latest_openmp_dirs(cluster)


''' Load the data of the latest OpenMP version, or of an older one if specified
    in OLDER_VERSION_DIRS '''
def load_openmp_data(cluster, bench, timer='total'):
    from tagged_data import EXCLUDED_COMPILERS
    from io_timings import add_data

    data = []
    for benchmark_dir in get_openmp_dirs(cluster, bench):
        data = add_data(data, benchmark_dir, bench, which=timer, exclude_compilers=EXCLUDED_COMPILERS)
    return data


''' Execution times of the MPI-only runs and of the fastest MPI-OpenMP
    configuration, for every number of nodes.
    Returns two dictionaries indexed by the number of nodes: the MPI-only times,
    and the (time, (mpi_procs_per_node, omp_threads)) of the fastest hybrid run. '''
def best_openmp_times(data, reso):

    # only compare configurations that use the full node
    entries, cores_per_node = select_full_node_runs(data, reso)
    timings = collect_timings(entries)

    # keep track of the number of MPI processes of every configuration
    mpi_procs = {(entry['nodes'], entry['omp_threads']): entry['mpi_procs_per_node']
                 for entry in entries}

    mpi_times = {}
    omp_times = {}
    for (nnodes, nthr), times in timings.items():
        avg_time, err_min, err_max = process_times(times)
        if nthr==0:
            mpi_times[nnodes] = avg_time
        # keep the fastest hybrid run
        elif nnodes not in omp_times or avg_time<omp_times[nnodes][0]:
            omp_times[nnodes] = (avg_time, (mpi_procs[(nnodes, nthr)], nthr))

    return mpi_times, omp_times


''' Gain in execution time of the fastest MPI-OpenMP configuration with respect
    to the MPI-only run using the same number of nodes.
    Returns the lists of numbers of nodes, gains in percent and configurations
    (mpi_procs_per_node, omp_threads) of the fastest run. '''
def best_openmp_speedup(data, reso):

    mpi_times, omp_times = best_openmp_times(data, reso)

    nodes = []
    speedups = []
    configs = []
    # the MPI-only run is the reference
    for nnodes in sorted(set(mpi_times) & set(omp_times)):
        best_time, best_config = omp_times[nnodes]
        nodes.append(nnodes)
        speedups.append(100.*(mpi_times[nnodes]-best_time)/mpi_times[nnodes])
        configs.append(best_config)

    return nodes, speedups, configs


''' Assign a marker shape to every MPI×OMP configuration of the given lists.
    The configurations are grouped by number of cores per node, then ordered by
    number of threads. Returns the markers and the grouped configurations, or
    None if there are not enough marker shapes. '''
def assign_config_markers(arr_configs):

    core_configs = {}
    for config in set(config for configs in arr_configs for config in configs):
        core_configs.setdefault(config[0]*config[1], []).append(config)
    for cores in core_configs:
        core_configs[cores].sort(key=lambda config: (config[1], config[0]))
    all_configs = [config for cores in sorted(core_configs) for config in core_configs[cores]]
    if len(all_configs)>len(MARKERS):
        print('[OMP best] Not enough marker shapes for all configurations')
        return None, None
    return dict(zip(all_configs, MARKERS)), core_configs


''' Colors of the clusters, taken from the colormap for unknown clusters '''
def get_cluster_colors(clusters, cmap_name='tab10'):
    cmap = plt.get_cmap(cmap_name)
    return {cluster: CLUSTER_COLORS.get(cluster, cmap(i)) for i, cluster in enumerate(clusters)}


''' Line style of the curves, dashed when the data comes from an older OpenMP version '''
def get_linestyle(cluster, bench):
    return '--' if (cluster, bench) in OLDER_VERSION_DIRS else '-'


''' Plot the points with the marker shape of their configuration '''
def plot_config_markers(ax, nodes, values, configs, markers, color):
    for nnodes, value, config in zip(nodes, values, configs):
        ax.plot(nnodes, value, marker=markers[config], markeredgewidth=0, alpha=0.8,
                markersize=MARKER_SIZE*MARKER_SCALE.get(markers[config], 1.), color=color)


''' Figure with one column per benchmark, sharing the y-axis '''
def create_benchmark_columns(benchmarks):
    fig, axes = plt.subplots(nrows=1, ncols=len(benchmarks), figsize=(3.6*len(benchmarks),4),
                             sharey=True, squeeze=False)
    fig.subplots_adjust(wspace=0.05)
    return fig, axes[0]


''' Log2 x-axis labelled with the numbers of nodes '''
def set_nodes_axis(ax, plotted_nodes):
    ax.set_xlabel('number of nodes')
    ax.set_xscale('log', base=2)
    if len(plotted_nodes)>0:
        ax.set_xticks(sorted(plotted_nodes))
        ax.set_xlim(min(plotted_nodes)/1.4, max(plotted_nodes)*1.4)
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.xaxis.set_minor_locator(mticker.NullLocator())


''' Invisible legend entry, to fill up or head a column '''
def blank_handle(label=''):
    return mlines.Line2D([], [], ls='', label=label)


''' Shared legend above the panels with the clusters, and the other line styles
    given in extra_handles. Its bottom is at height y, in figure coordinates '''
def add_cluster_legend(fig, clusters, colors, extra_handles=[], y=1.):

    blank = blank_handle

    cluster_handles = [mlines.Line2D([], [], color=colors[cluster], lw=2, label=cluster)
                       for cluster in clusters]
    if len(cluster_handles)+len(extra_handles)<=5:
        top_handles = cluster_handles + extra_handles
        top_ncol = len(top_handles)
    else:
        # too wide for one row: clusters on the first row, the other entries on the second.
        # The legend is filled column by column, so interleave both rows
        top_ncol = max(len(cluster_handles), len(extra_handles))
        top_handles = []
        for row1, row2 in zip(cluster_handles+[blank('')]*(top_ncol-len(cluster_handles)),
                              extra_handles+[blank('')]*(top_ncol-len(extra_handles))):
            top_handles += [row1, row2]

    return fig.legend(handles=top_handles, loc='lower center', bbox_to_anchor=(0.5, y),
                      ncol=top_ncol, frameon=False)


''' Legend of the configurations inside the given axes, with one column per
    number of cores per node '''
def add_config_legend(ax, core_configs, markers, loc='lower center'):

    blank = blank_handle

    # one column per number of cores per node, headed by an invisible handle
    nrows = max(len(configs) for configs in core_configs.values())
    config_handles = []
    for cores in sorted(core_configs):
        config_handles.append(blank(f'{cores} cores/node'))
        for config in core_configs[cores]:
            config_handles.append(mlines.Line2D([], [], color='grey', ls='', marker=markers[config],
                                                markersize=0.85*MARKER_SIZE*MARKER_SCALE.get(markers[config], 1.),
                                                markeredgewidth=0, label=f'{config[0]}×{config[1]}'))
        config_handles += [blank('')]*(nrows-len(core_configs[cores]))

    legend = ax.legend(handles=config_handles, title='MPI×OMP', loc=loc,
                       ncol=len(core_configs), fontsize=8, title_fontsize=8,
                       handletextpad=0.2, columnspacing=1., labelspacing=0.3)
    # left align the column headers, which have no marker
    for handle, text in zip(legend.legend_handles, legend.get_texts()):
        if handle.get_marker() in ['None', None, '']:
            text.set_position((-15, 0))

    return legend


''' Legend entry for the curves of an older OpenMP version, if any is plotted '''
def older_version_handles(keys):
    if any((cluster, bench) in OLDER_VERSION_DIRS for bench, reso, cluster in keys):
        return [mlines.Line2D([], [], color='black', lw=2, ls='--', label='older OpenMP version')]
    return []


''' Plot the gain in execution time of the best MPI-OpenMP configuration with
    respect to MPI-only, as a function of the number of nodes. There is one
    column per benchmark and one color per cluster, while the marker shape
    shows which MPI×OMP configuration is the fastest. '''
def plot_best_openmp_speedup(clusters, benchmarks=BENCHMARKS, timer='total',
                             cmap_name='tab10', fig_name='omp_best_speedup.png'):

    # gather the results of all clusters and benchmarks first, to assign
    # the same marker to a configuration in all panels
    results = {}
    for bench, reso in benchmarks:
        for cluster in clusters:
            data = load_openmp_data(cluster, bench, timer)
            nodes, speedups, configs = best_openmp_speedup(data, reso)
            if len(speedups)==0:
                print('[OMP best speedup] No data to compare for', cluster, bench, reso)
                continue
            results[(bench, reso, cluster)] = (nodes, speedups, configs)

    if len(results)==0:
        print('[OMP best speedup] No data available')
        return 1

    markers, core_configs = assign_config_markers([configs for nodes, speedups, configs in results.values()])
    if markers is None:
        return 1
    colors = get_cluster_colors(clusters, cmap_name)

    fig, axes = create_benchmark_columns(benchmarks)

    all_speedups = []
    for ax, (bench, reso) in zip(axes, benchmarks):
        # the MPI-only run is the reference
        ax.axhline(0., color='black', linestyle='--', linewidth=1, zorder=0)

        plotted_nodes = set()
        for cluster in clusters:
            if (bench, reso, cluster) not in results:
                continue
            nodes, speedups, configs = results[(bench, reso, cluster)]

            ax.plot(nodes, speedups, color=colors[cluster], ls=get_linestyle(cluster, bench))
            plot_config_markers(ax, nodes, speedups, configs, markers, colors[cluster])
            all_speedups += speedups
            plotted_nodes.update(nodes)

        ax.set_title(f'{bench} {reso}')
        set_nodes_axis(ax, plotted_nodes)
        ax.grid(axis='y', which='major', alpha=0.3)

    axes[0].set_ylabel('speedup of best OpenMP w.r.t. MPI-only [%]')
    # linear in between -1% and 1%, logarithmic outside of it
    axes[0].set_yscale('symlog', linthresh=1, linscale=0.2)
    axes[0].yaxis.set_minor_locator(mticker.SymmetricalLogLocator(base=10, linthresh=1,
                                                                  subs=range(2,10)))
    # write the percentages as 1, 10, 100 instead of 10^0, 10^1, 10^2
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, pos: f'{value:g}'))
    # the automatic limits round up to the nearest tick, which cuts the markers.
    # Go down to at least -10% to have a label below -1%
    axes[0].set_ylim(pad_limits(axes[0].yaxis, min(min(all_speedups), -10), max(all_speedups)))

    # shared legends, clusters above the panels and configurations in the last panel
    legend1 = add_cluster_legend(fig, clusters, colors, extra_handles=older_version_handles(results))
    legend2 = add_config_legend(axes[-1], core_configs, markers)

    print(fig_name)
    # legends outside of the axes are not taken into account by default to fit the figure
    plt.savefig(fig_name, bbox_inches='tight', bbox_extra_artists=[legend1, legend2], dpi=200)
    plt.close()

    return 0


if __name__ == '__main__':

    #--------- Get command line input ------------
    import argparse
    parser = argparse.ArgumentParser(
        description='Speedup of the best MPI-OpenMP configuration with respect to MPI-only as a function of the number of nodes, for several clusters and benchmarks')

    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'], help='Cluster names')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    fig_name=f'omp_best_speedup_{args.timer}_{"_".join(args.clusters)}.png'

    error = plot_best_openmp_speedup(args.clusters, timer=args.timer, fig_name=fig_name)
    if not error:
        print(f'Figure outputted to {fig_name}')
