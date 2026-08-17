import numpy as np
import io
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
from visualisation import process_times,search_best_config,scan_data

''' Plot the evolution of execution time with the number of nodes for different
    number of threads, so we see which nthreads is best for different #nodes '''
def plot_openmp_time_nthreads(data, reso, arr_threads=[0,2,4,8,16,32,64], 
                              input_axes=None, fig_name='openmp_time_nthreads.png'):


    # create colors for different number of threads
    # TODO use get_color utility
    cmap = plt.get_cmap('inferno')
    cNorm  = colorsx.LogNorm(vmin=1, vmax=max(arr_threads))
    colorVals = {}
    for val in arr_threads:
        colorVals[val] = cmap(cNorm(val))
    colorVals[0] = 'black'

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4))
    else:
        axes = input_axes

    for nthr in arr_threads:
        times = []
        nodes = []

        for nnodes in [1,2,4,8,16,32,64]:
            for entry in data:
                if entry["resolution"]!=reso:
                    continue
                if entry["nodes"]!=nnodes:
                    continue
                if entry["omp_threads"]!=nthr:
                    continue
                mpi = entry["mpi_procs_per_node"]
                if mpi*nthr not in [112, 128] and nthr!=0:
                    continue

                avg_time, err_min, err_max = process_times(entry["timings"])
                times.append(avg_time)
                nodes.append(nnodes)

        if len(times)>0:
            axes.plot(nodes, times, marker='o',markersize=6,
                        color=colorVals[nthr], label=str(nthr))

    # layout of the figure
    if input_axes==None:
        # add legend next to figure
        axes.legend(title='OMP threads', loc='center left', bbox_to_anchor=(1., 0.5))

        axes.set_title(f'{data[0]['metadata']['Benchmark']} {reso} on {data[0]['metadata']['Cluster']}')
        axes.tick_params(axis='x', labelrotation=90)
        axes.set_ylabel('execution time [s]')
        axes.set_yscale('log')
        print(fig_name)
        plt.savefig(fig_name, bbox_inches='tight', dpi=200)
        plt.close()


if __name__ == '__main__':

    COLOR='\033[0;36m' #cyan
    NC='\033[0m' # No Color

    #--------- Get command line input ------------
    import argparse
    parser = argparse.ArgumentParser(
        description='Execution time as a function of the number of nodes, for different number of OMP threads')

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    from tagged_data import load_latest_openmp_data
    data = load_latest_openmp_data(args.cluster, args.benchmark, args.timer)

    fig_name=f'omp_time_{args.benchmark}_{args.reso}_{args.timer}_{args.cluster}.png'

    plot_openmp_time_nthreads(data, args.reso, fig_name=fig_name)
    print(f'Figure outputted to {fig_name}')


