import numpy as np
import io
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
from visualisation import process_times,search_best_config,scan_data


''' Plot evolution of execution time (different commits) for various number of nodes '''
def plot_execution_time_multinode(benchmarks, release_labels, reso,
                                  arr_nodes=[1,2,4,8,16,32,64], input_axes=None,
                                  outname='evo_exectime.png'):

    # create colors for different number of nodes
    # TODO use get_color utility
    cmap = plt.get_cmap('managua')
    cNorm  = colorsx.LogNorm(vmin=1, vmax=max(arr_nodes))
    colorVals = {}
    for val in arr_nodes:
        colorVals[val] = cmap(cNorm(val))

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4))
    else:
        axes = input_axes

    for nodes in arr_nodes:
        times = []
        labels = []

        for data,label in zip(benchmarks,release_labels):
            best_entry, best_time = search_best_config(data,reso,nodes)

            if best_entry is not None:
                times.append(float(best_time))
                labels.append(label)
                # plot individual timing points to verify there are no outlyers
                axes.scatter(np.full(len(best_entry['timings']),label), best_entry['timings'],
                             marker='o', s=3, color=colorVals[nodes])
            else:
                times.append(np.nan)
                labels.append(label)

        # plot evolution of time as a function of release
        axes.errorbar(labels, times, fmt='o',markersize=6,
                        color=colorVals[nodes], label=str(nodes))

        # plot a line from the first point to make comparison easier
        axes.plot([release_labels[0],release_labels[-1]], [times[0],times[0]],
                   ls=':', lw=1.3, color=colorVals[nodes])

    # layout of the figure
    if input_axes==None:
        # add legend next to figure
        axes.legend(title='nodes', loc='center left', bbox_to_anchor=(1., 0.5))

        axes.set_title(f'{data[0]['metadata']['Benchmark']} {reso} on {data[0]['metadata']['Cluster']}')
        axes.tick_params(axis='x', labelrotation=90)
        axes.set_ylabel('execution time [s]')
        axes.set_yscale('log')
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


''' Generate a table listing the execution time and speedup, in markdown or latex format '''
def table_execution_time(benchmarks, release_labels, reso, arr_nodes_in=[1,2,4,8,16,32,64], fmt='markdown'):

    out = io.StringIO()

    # ---------- Header ----------

    ncols = len(release_labels) + 2

    if fmt == 'markdown':
        header = ( "| nodes | "  + " | ".join(release_labels) + " | Δ [%] |")
        sep = "|" + "---|"*ncols
        print(header, file=out)
        print(sep, file=out)

    elif fmt == 'latex':
        header = ("nodes & " + " & ".join(release_labels) + r" & $\Delta$ [\%] \\")
        print(r"\begin{tabular}{" + "l"*ncols + "}", file=out)
        print(r"\hline", file=out)
        print(header, file=out)
        print(r"\hline", file=out)

    else:
        raise ValueError("[table_execution_time] fmt must be 'markdown' or 'latex'")

    # ---------- Gather table entries from all releases into a dictionary ----------

    release_results = {}
    for data, label in zip(benchmarks, release_labels):

        # Extract results from the benchmark data 
        times, avail_nodes, _, configs = scan_data(data, arr_nodes_in, [reso]*len(arr_nodes_in))

        # If no data available, go to next release
        if len(avail_nodes)==0:
            continue

        col = {}
        for nodes, time, config in zip(avail_nodes, times, configs):
            col[nodes] = {'time':time, 'config':config}

        release_results[label] = col


    # ---------- Print table row by row ----------

    for nodes in arr_nodes_in:
        row = [str(nodes)]

        for label in release_labels:

            # retrieve time and config for this entry, or put nan if the entry doesn't exists
            time = release_results.get(label,{}).get(nodes,{}).get('time',np.nan)
            config = release_results.get(label,{}).get(nodes,{}).get('config',"")

            # construct the table entry: time (config)
            if np.isfinite(time):
                # add optimal mpi-omp config unless it's mpi-only on full node
                if config=='MPI=128 OMP=0' or config=='MPI=112 OMP=0':
                    entry = (f"{time:.2f}")
                else:
                    entry = (f"{time:.2f} ({config})")
            else:
                # or put a dash when no entry is available
                entry = "-"

            row.append(entry)

        # compute % improvement of first versus last version of the code
        value_first = release_results.get(release_labels[0], {}).get(nodes,{}).get('time',np.nan)
        value_last  = release_results.get(release_labels[-1],{}).get(nodes,{}).get('time',np.nan)

        # add to the last column of the table
        if np.isfinite(value_first) and np.isfinite(value_last):
            diff = (-(value_last - value_first) / value_first * 100)
            row.append(f"{diff:.1f}")
        else:
            row.append("-")

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
        description='Plot benchmark execution time evolution')

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    #--------- Load benchmark data for releases ------------
    from tagged_data import load_release_data
    benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, args.timer)
    #TODO default should take two benchmarks to compare?

    #--------- Make figure ------------
    filename = f'evo_exectime_{args.benchmark}_{args.reso}_{args.timer}_{args.cluster}.png'
    plot_execution_time_multinode(benchmarks, release_labels, args.reso, outname=filename)
    print(f'Figure outputted to {filename}')

    #--------- Make table ------------
    print(f'{COLOR} Average execution time for {args.benchmark} {args.reso} ({args.timer}){NC}')
    table = table_execution_time(benchmarks, release_labels, args.reso, fmt='latex')
    print(table)

