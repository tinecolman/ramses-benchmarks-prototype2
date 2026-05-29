import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
from visualisation import process_times
import argparse
from tagged_data import *

''' Plot evolution of execution time (different commits) for various number of nodes '''
def plot_execution_time_multinode(benchmarks, release_labels, reso,
                                  arr_nodes=[1,2,4,8,16,32,64], input_axes=None,
                                  outname='evo_exectime.png'):

    # create colors for different number of nodes
    cmap = plt.get_cmap('managua')
    cNorm  = colorsx.LogNorm(vmin=1, vmax=max(arr_nodes))
    colorVals = {}
    for val in arr_nodes:
        colorVals[val] = cmap(cNorm(val))

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    # print table header
    header = "Nodes"
    for label in release_labels:
        header = header + " & " + label
    print(header)

    for nodes in arr_nodes:
        times = []
        labels = []
        table_string = '{}'.format(str(nodes).rjust(2))

        for data,label in zip(benchmarks,release_labels):
            best_entry = None
            best_time = np.inf
            for entry in data:
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                # reduce time data
                time, error_min, error_max = process_times(entry['timings'])

                # keep fastest config
                if time < best_time:
                    best_time = time
                    best_entry = entry

            if best_entry is not None:
                times.append(float(best_time))
                labels.append(label)
                best_config = f'MPI={best_entry['mpi_procs_per_node']} OMP={best_entry['omp_threads']}'
                # plot individual timing points to verify there are no outlyers
                axes.scatter(np.full(len(best_entry['timings']),label),best_entry['timings'],marker='o',s=3,color=colorVals[nodes])

                table_string+= ' & {:.3f} ({})'.format(best_time, best_config)
            else:
                times.append(np.nan)
                labels.append(label)
                table_string+= ' & - '

        diff = (-1)*(times[-1] - times[0])/times[0] * 100
        table_string = table_string + ' & {:.1f} \\\\ \\hline'.format(diff)

        print(table_string)
        # plot evolution of time as a function of release, for this number of nodes
        axes.errorbar(labels, times, fmt='o',markersize=6, color=colorVals[nodes], label=str(nodes)+'nodes')

        # plot a line from the last point to make comparison easier
        if len(times)>0:
            axes.plot([release_labels[0],release_labels[-1]], [times[0],times[0]], ls=':', lw=1.3, color=colorVals[nodes])

    # layout of the figure
    if input_axes==None:
        axes.set_title(f'{entry['metadata']['Benchmark']} {reso} on {entry['metadata']['Cluster']}')
        axes.tick_params(axis='x', labelrotation=90)
        axes.set_ylabel('execution time [s]')
        axes.set_yscale('log')
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Plot benchmark execution time evolution'
    )

    parser.add_argument(
        '-c', '--cluster',
        required=True,
        help='Cluster name'
    )

    parser.add_argument(
        '-b', '--benchmark',
        required=True,
        help='Benchmark setup name'
    )

    parser.add_argument(
        '-r', '--reso',
        required=True,
        help='Resolution'
    )

    parser.add_argument(
        '-t', '--timer',
        default='total',
        help='Subtimer to analyse'
    )

    args = parser.parse_args()

    benchmarks, release_labels = load_release_data(
        args.cluster,
        args.benchmark,
        args.timer
    )

    plot_execution_time_multinode(
        benchmarks,
        release_labels,
        args.reso,
        outname=f'images/evo_exectime_{args.benchmark}_{args.reso}_{args.timer}_{args.cluster}.png'
    )

#python evolution_execution_time.py -c meluxina -b sedov -r 1024
#python evolution_execution_time.py -c meluxina -b sedov-amr -r lvl5-10

#python evolution_execution_time.py -c discoverer -b sedov -r 1024
#python evolution_execution_time.py -c discoverer -b sedov-amr -r lvl5-10
