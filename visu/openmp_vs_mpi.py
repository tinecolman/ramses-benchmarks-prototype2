import numpy as np
from matplotlib import pyplot as plt
import matplotlib.lines as mlines
from matplotlib.legend import Legend
from io_timings import search_best_config, set_node_ticks
from scaling_combo import plot_scaling_combo_inverse
from openmp_nthreads_execution_time import get_cores_per_node

MAX_NNODES = 512


''' Split the data in MPI-only runs and hybrid MPI-OpenMP runs, keeping only
    the runs that use the full node. Passing both to the functions that search
    for the best configuration then compares MPI-only with the best OpenMP run. '''
def split_mpi_omp(data):
    if len(data)==0:
        return [], []
    cores_per_node = max(get_cores_per_node(entry) for entry in data)
    full_node = [entry for entry in data if get_cores_per_node(entry)==cores_per_node]
    data_mpi = [entry for entry in full_node if entry['omp_threads']==0]
    data_omp = [entry for entry in full_node if entry['omp_threads']>0]
    return data_mpi, data_omp


''' Numbers of nodes for which there is data at the given resolution '''
def get_available_nodes(data, reso):
    return sorted(set(entry['nodes'] for entry in data if entry['resolution']==reso))


''' Label of the best configuration, e.g. 16×7 '''
def short_config(entry):
    return f'{entry["mpi_procs_per_node"]}×{entry["omp_threads"]}'


''' Execution time as a function of the number of nodes, for all resolutions.
    Dashed lines are MPI-only, solid lines are the fastest MPI-OpenMP
    configuration, which is written next to each point. '''
def plot_time_mpi_vs_omp(data_mpi, data_omp, resos, input_axes=None,
                         outname='time_mpi_vs_omp.png'):

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6,5))
    else:
        axes = input_axes

    reso_cmaps = ['Purples','Blues','Greens','Oranges','Reds']

    all_nodes = set()
    reso_handles = []
    for reso, cmap in zip(resos, reso_cmaps):
        color = plt.get_cmap(cmap)(0.7)
        plotted = False

        for data, style in zip([data_mpi, data_omp], ['--', '-']):
            arr_nodes = []
            times = []
            configs = []
            for nodes in range(MAX_NNODES+1):
                best_entry, best_time = search_best_config(data, reso, nodes)
                if best_entry is not None:
                    arr_nodes.append(nodes)
                    times.append(best_time)
                    configs.append(short_config(best_entry))

            if len(times)==0:
                continue
            axes.plot(arr_nodes, times, ls=style, marker='o', markersize=4, color=color)
            all_nodes.update(arr_nodes)
            plotted = True

            # show which configuration is the fastest
            if data is data_omp:
                for nodes, time, config in zip(arr_nodes, times, configs):
                    axes.annotate(config, (nodes, time), textcoords='offset points',
                                  xytext=(0,-11), ha='center', fontsize=6, color=color)

        if plotted:
            reso_handles.append(mlines.Line2D([], [], color=color, lw=2, label=reso))

    if len(all_nodes)==0:
        print('[Time MPI vs OMP] No data available')
        return 1

    # layout of the figure
    if input_axes==None:
        style_handles = [mlines.Line2D([], [], color='k', ls='--', label='MPI-only'),
                         mlines.Line2D([], [], color='k', ls='-', label='best OpenMP')]
        legend1 = axes.legend(handles=reso_handles, title='Resolution',
                              loc='upper left', bbox_to_anchor=(1., 1.))
        axes.add_artist(legend1)
        legend2 = axes.legend(handles=style_handles, loc='lower left', bbox_to_anchor=(1., 0.))

        axes.set_title(f'{data_omp[0]['metadata']['Benchmark']} on {data_omp[0]['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('execution time [s]')
        axes.set_xscale('log')
        axes.set_yscale('log')
        set_node_ticks(axes, all_nodes)
        # legends outside of the axes are not taken into account by default to fit the figure
        plt.savefig(outname, bbox_inches='tight', bbox_extra_artists=[legend1, legend2], dpi=200)
        plt.close()

    return 0


''' Combined strong and weak scaling plot (performance = 1/time), with MPI-only
    in the left panel and the fastest MPI-OpenMP configuration in the right panel,
    sharing the axes to compare both directly. '''
def plot_scaling_combo_mpi_vs_omp(data_mpi, data_omp, resos, weak_scaling_map,
                                  outname='scaling_combo_mpi_vs_omp.png'):

    if len(data_mpi)==0 or len(data_omp)==0:
        print('[Scaling combo MPI vs OMP] Missing MPI-only or OpenMP data')
        return 1

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(11,5), sharex=True, sharey=True)

    for ax, data, label in zip(axes, [data_mpi, data_omp], ['MPI-only', 'best OpenMP']):
        plot_scaling_combo_inverse(data, resos, weak_scaling_map, input_axes=ax)
        ax.set_title(label)

    # the legends are the same for both panels, only keep them on the right
    for child in axes[0].get_children():
        if isinstance(child, Legend):
            child.remove()
    axes[1].set_ylabel('')

    # label the numbers of nodes of both panels
    all_nodes = set(entry['nodes'] for entry in data_mpi+data_omp if entry['resolution'] in resos)
    set_node_ticks(axes[0], all_nodes)

    fig.suptitle(f'{data_omp[0]['metadata']['Benchmark']} on {data_omp[0]['metadata']['Cluster']}')
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Compare the execution time of MPI-only with the best MPI-OpenMP configuration')

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    from tagged_data import load_latest_openmp_data
    from resolutions import get_resolutions
    data = load_latest_openmp_data(args.cluster, args.benchmark, args.timer)
    data_mpi, data_omp = split_mpi_omp(data)

    fig_name = f'time_mpi_vs_omp_{args.benchmark}_{args.timer}_{args.cluster}.png'
    error = plot_time_mpi_vs_omp(data_mpi, data_omp, get_resolutions(args.benchmark), outname=fig_name)
    if not error:
        print(f'Figure outputted to {fig_name}')
