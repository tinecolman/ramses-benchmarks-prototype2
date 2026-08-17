from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
import matplotlib.ticker as mticker
from collections import defaultdict
from io_timings import process_times

''' Number of cores occupied on a node by a run.
    An MPI-only run has omp_threads=0 and an OpenMP-only run mpi_procs_per_node=0,
    in both cases the switched-off parallelisation corresponds to a single
    process/thread '''
def get_cores_per_node(entry):
    return max(entry["mpi_procs_per_node"],1) * max(entry["omp_threads"],1)

''' Select the runs at the requested resolution that fill the entire node.
    The size of a node is not stored in the data, so it is determined as the
    largest number of cores per node occupied by the runs of this benchmark '''
def select_full_node_runs(data, reso):
    entries = [entry for entry in data if entry["resolution"]==reso]
    if len(entries)==0:
        return [], 0
    cores_per_node = max(get_cores_per_node(entry) for entry in entries)
    entries = [entry for entry in entries if get_cores_per_node(entry)==cores_per_node]
    return entries, cores_per_node

''' Gather the timings of all runs sharing the same (#nodes, #threads)
    configuration, so repeated runs of the same config are averaged together '''
def collect_timings(entries):
    timings = defaultdict(list)
    for entry in entries:
        timings[(entry["nodes"], entry["omp_threads"])] += entry["timings"]
    return timings


''' Add some room around the data range, taking into account the (possibly
    non-linear) scale of the axis '''
def pad_limits(axis, vmin, vmax, margin=0.06):
    transform = axis.get_transform()
    low, high = transform.transform([vmin, vmax])
    pad = margin*(high-low)
    if pad==0:
        pad = margin*max(abs(low),1.)
    return transform.inverted().transform([low-pad, high+pad])


''' Plot the gain in execution time with respect to the MPI-only run using the
    same number of nodes, as a function of the number of nodes and for different
    number of threads, so we see which nthreads is best for different #nodes.
    A positive percentage means the hybrid MPI-OpenMP run is faster.
    The numbers of nodes and of threads are taken from the data itself. '''
def plot_openmp_speedup_nthreads(data, reso, input_axes=None, cmap_name='turbo',
                                 fig_name='openmp_speedup_nthreads.png'):

    # only compare configurations that use the full node
    entries, cores_per_node = select_full_node_runs(data, reso)
    if len(entries)==0:
        print('[OMP speedup] No data available for this resolution:', reso)
        return 1

    timings = collect_timings(entries)

    # numbers of nodes and of threads present in the data
    arr_nodes = sorted(set(nodes for nodes,nthr in timings.keys()))
    arr_threads = sorted(set(nthr for nodes,nthr in timings.keys() if nthr>0))

    # MPI-only reference time for every number of nodes
    ref_times = {}
    for nnodes in arr_nodes:
        if (nnodes, 0) in timings:
            ref_times[nnodes], err_min, err_max = process_times(timings[(nnodes, 0)])

    if len(arr_threads)==0 or len(ref_times)==0:
        print('[OMP speedup] Missing OpenMP runs or MPI-only reference for resolution:', reso)
        return 1

    # create colors for different number of threads
    # TODO use get_color utility
    # the colors are spread evenly over the (ordered) thread counts present in the
    # data, so that close values such as 2 and 4 threads remain distinguishable.
    # A colormap covering many hues works best here, a sequential one such as
    # inferno gives too similar colors for neighbouring thread counts.
    cmap = plt.get_cmap(cmap_name)
    cNorm  = colorsx.Normalize(vmin=0, vmax=max(len(arr_threads)-1,1))
    colorVals = {}
    for index, val in enumerate(arr_threads):
        colorVals[val] = cmap(0.05+0.9*cNorm(index))

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4))
    else:
        axes = input_axes

    # the MPI-only run is the reference
    axes.axhline(0., color='black', linestyle='--', linewidth=1, zorder=0)

    all_speedups = []
    plotted_nodes = set()
    for nthr in arr_threads:
        speedups = []
        nodes = []

        for nnodes in arr_nodes:
            if (nnodes, nthr) not in timings:
                continue
            if nnodes not in ref_times:
                continue

            avg_time, err_min, err_max = process_times(timings[(nnodes, nthr)])
            # relative gain in execution time, in percent
            speedups.append(100.*(ref_times[nnodes]-avg_time)/ref_times[nnodes])
            nodes.append(nnodes)

        if len(speedups)>0:
            axes.plot(nodes, speedups, marker='o', markersize=6,
                        color=colorVals[nthr], label=str(nthr))
            all_speedups += speedups
            plotted_nodes.update(nodes)

    if len(all_speedups)==0:
        print('[OMP speedup] No hybrid MPI-OpenMP run to compare for resolution:', reso)
        return 1

    # layout of the figure
    if input_axes==None:
        # add legend next to figure
        axes.legend(title=f'OMP threads\n({cores_per_node} cores/node)',
                    loc='center left', bbox_to_anchor=(1., 0.5))

        axes.set_title(f'{entries[0]['metadata']['Benchmark']} {reso} on {entries[0]['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('speedup w.r.t. MPI-only [%]')
        axes.set_xscale('log', base=2)
        axes.set_xticks(sorted(plotted_nodes))
        axes.xaxis.set_major_formatter(mticker.ScalarFormatter())
        axes.xaxis.set_minor_locator(mticker.NullLocator())
        axes.set_xlim(min(plotted_nodes)/1.4, max(plotted_nodes)*1.4)
        # linear in between -1% and 1%, logarithmic outside of it
        axes.set_yscale('symlog', linthresh=1, linscale=0.5)
        axes.yaxis.set_minor_locator(mticker.SymmetricalLogLocator(base=10, linthresh=1,
                                                                   subs=range(2,10)))
        # write the percentages as 1, 10, 100 instead of 10^0, 10^1, 10^2
        axes.yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, pos: f'{value:g}'))
        axes.grid(axis='y', which='major', alpha=0.3)
        # the automatic limits round up to the nearest tick, which cuts the markers
        axes.set_ylim(pad_limits(axes.yaxis, min(all_speedups), max(all_speedups)))
        print(fig_name)
        plt.savefig(fig_name, bbox_inches='tight', dpi=200)
        plt.close()

    return 0


if __name__ == '__main__':

    COLOR='\033[0;36m' #cyan
    NC='\033[0m' # No Color

    #--------- Get command line input ------------
    import argparse
    parser = argparse.ArgumentParser(
        description='Speedup with respect to MPI-only as a function of the number of nodes, for different number of OMP threads')

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    from tagged_data import load_latest_openmp_data
    data = load_latest_openmp_data(args.cluster, args.benchmark, args.timer)

    fig_name=f'omp_speedup_{args.benchmark}_{args.reso}_{args.timer}_{args.cluster}.png'

    error = plot_openmp_speedup_nthreads(data, args.reso, fig_name=fig_name)
    if not error:
        print(f'Figure outputted to {fig_name}')
