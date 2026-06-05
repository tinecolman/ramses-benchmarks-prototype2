import numpy as np
import io
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx

MAX_NNODES = 512
MAX_CORES = 128

''' Extract memory data '''
def gather_memory_results(data, reso):

    results = {}
    for omp in range(0,MAX_CORES+1):
        used_nodes = []
        memory_usage = []

        for nodes in range(MAX_NNODES+1):

            for entry in data:
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                if entry['omp_threads']!=omp:
                    continue

                # use only data that uses the full node
                used_cores = max(entry['mpi_procs_per_node'],1) * max(entry['omp_threads'],1)
                if used_cores not in [128,112]:
                    continue

                mem_string = entry['metadata']['max memory per node']
                mem_value = float(mem_string.split(' ')[0])
                memory_usage.append(mem_value)
                used_nodes.append(nodes)

        if len(used_nodes)>0:
            results[omp] = (used_nodes, memory_usage)

    return results

''' Plot the memory consumption per node as a function of the number of nodes,
    for different number of OpenMP threads '''
def plot_memory(data, reso, input_axes=None, outname='memory.png'):

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    # extract plottable results from data
    results = gather_memory_results(data,reso)
    used_omp = sorted(results.keys())

    # remove entries for which only the 1-node data point is available
    for omp in used_omp:
        if results[omp][0]==[1]:
            results.pop(omp)
    used_omp = sorted(results.keys())

    # create colors
    cmap = plt.get_cmap('inferno')
    cNorm  = colorsx.LogNorm(vmin=1, vmax=max(used_omp)*1.5)

    max_nodes = 0
    reference = np.inf
    for omp in used_omp:
        used_nodes = results[omp][0]
        memory_usage = results[omp][1]

        if len(memory_usage)>1:
            if omp==0:
                axes.plot(used_nodes, memory_usage, color='black',
                          marker='o', markersize=4, markerfacecolor='none', label='MPI-only')
            else:
                axes.plot(used_nodes, memory_usage, color=cmap(cNorm(omp)),
                          marker='o', markersize=4, label=f'OMP={omp}')
            max_nodes = max(max_nodes, max(used_nodes))
            reference = min(reference, memory_usage[0])

    # add ideal scaling
    axes.plot([1,max_nodes],[reference,reference/max_nodes],
               c='black',ls=':', lw=2, label='ideal', zorder=1)

    # layout of the figure
    if input_axes==None:
        axes.set_title(f'{data[0]['metadata']['Benchmark']} {reso} on {data[0]['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('memory per node [GB]')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


''' '''
def table_memory(data, reso, fmt='markdown'):

    out = io.StringIO()

    # ---------- Gather table entries for all number of OMP threads ----------

    # extract results from data
    results = gather_memory_results(data,reso)
    # remove OMP-only entries, since the memory isn't outputted when running without MPI
    if 112 in results.keys():
        results.pop(112)
    if 128 in results.keys():
        results.pop(128)
    used_omp = sorted(results.keys())


    # gather number of nodes
    arr_nodes = []
    for omp in used_omp:
        arr_nodes = arr_nodes + results[omp][0]
    arr_nodes = set(arr_nodes)
    arr_nodes = sorted(list(arr_nodes))

    # ---------- Header ----------

    omp_labels = [f'OMP={omp}' for omp in used_omp]
    if omp_labels[0]=='OMP=0':
        omp_labels[0] = 'MPI-only'

    ncols = len(used_omp) + 2

    if fmt == 'markdown':
        header = ( "| nodes | "  + " | ".join(omp_labels) + " | best |")
        sep = "|" + "---|"*ncols
        print(header, file=out)
        print(sep, file=out)

    elif fmt == 'latex':
        header = ("nodes & " + " & ".join(omp_labels) + r" & best \\")
        print(r"\begin{tabular}{" + "l"*ncols + "}", file=out)
        print(r"\hline", file=out)
        print(header, file=out)
        print(r"\hline", file=out)

    else:
        raise ValueError("[table_execution_time] fmt must be 'markdown' or 'latex'")


    # ---------- Print table row by row ----------

    for nodes in arr_nodes:
        row = [str(nodes)]

        min_memory = np.inf
        for omp in used_omp:
            # get the entry or put a dash when no entry is available
            try:
                index = results[omp][0].index(nodes)
                mem = results[omp][1][index]
                # assemble entry
                if mem==0: # can happen in case of OMP-only or serial
                    value = '-'
                else:
                    value = f'{mem:.2f} GB'
                    min_memory = min(min_memory, mem)
            except:
                value = '-'
            row.append(value)

        # compute % improvement of OMP w.r.t. MPI-only
        try:
            index = results[0][0].index(nodes)
            improvement = min_memory/results[0][1][index] * 100
            row.append(f'{improvement:.1f} %')
        except:
            row.append('-')


        if fmt == 'markdown':
            print("| " + " | ".join(row) + " |", file=out)
        elif fmt == 'latex':
            print(" & ".join(row) + r" \\", file=out)

    # ---------- Footer for latex table ----------

    if fmt == 'latex':
        print(r"\end{tabular}", file=out)

    return out.getvalue()

if __name__ == '__main__':

    COLOR='\033[0;36m' #cyan
    NC='\033[0m' # No Color

    #--------- Get command line input ------------
    import argparse
    parser = argparse.ArgumentParser(
        description='Analyse memory consumption')

    parser.add_argument('-p', '--path', required=True, help='Path to the benchmark directory')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')

    args = parser.parse_args()

    #--------- Load benchmark data ------------
    from io_timings import add_data
    data = add_data([], args.path, args.benchmark, which='total')
    cluster = data[0]['metadata']['Cluster']

    #--------- Make figure ------------
    filename = f'memory_{args.benchmark}_{args.reso}_{cluster}.png'
    plot_memory(data, args.reso, outname=filename)
    print(f'Figure outputted to {filename}')

    #--------- Make table ------------
    print(f'{COLOR} Memory usage per node for {args.benchmark} {args.reso}{NC}')
    table = table_memory(data, args.reso, fmt='latex')
    print(table)