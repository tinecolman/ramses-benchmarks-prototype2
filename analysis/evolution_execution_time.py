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
    #print(header)

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

        #print(table_string)
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


''' Generate a table listing the execution time and speedup, in markdown or latex format '''
def table_execution_time(benchmarks, release_labels, reso, arr_nodes_in=[1,2,4,8,16,32,64], fmt='markdown'):

    out = io.StringIO()

    # ---------- Header ----------

    ncols = len(release_labels) + 2

    if fmt == 'markdown':
        header = ( "| Nodes | "  + " | ".join(release_labels) + " | Δ [%] |")
        sep = "|" + "---|"*ncols
        print(header, file=out)
        print(sep, file=out)

    elif fmt == 'latex':
        header = ("Nodes & " + " & ".join(release_labels) + r" & $\Delta$ [\%] \\")
        print(r"\begin{tabular}{" + "l"*ncols + "}", file=out)
        print(r"\hline", file=out)
        print(header, file=out)
        print(r"\hline", file=out)

    else:
        raise ValueError("fmt must be 'markdown' or 'latex'")

    # ---------- Gather table entries from all releases ----------

    release_results = {}
    release_results_time = {}
    for data, label in zip(benchmarks, release_labels):

        # Extract results from the benchmark data 
        times, avail_nodes, _, configs = scan_data(data, arr_nodes_in, [reso]*len(arr_nodes_in))

        # If no data available, go to next release
        if len(avail_nodes)==0:
            continue

        col = {}
        col_time = {}
        for nodes, time, config in zip(avail_nodes, times, configs):
            col_time[nodes] = time
            # add optimal mpi-omp config unless it's mpi-only on full node
            if config=='MPI=128 OMP=0' or config=='MPI=112 OMP=0':
                col[nodes] = (f"{time:.2f}")
            else:
                col[nodes] = (f"{time:.2f} ({config})")

        release_results[label] = col
        release_results_time[label] = col_time


    # ---------- Print table row by row ----------

    for nodes in arr_nodes_in:
        row = [str(nodes)]

        for label in release_labels:
            # get the entry or put a dash when no entry is available
            value = release_results.get(label,{}).get(nodes,"-")
            row.append(value)

        # compute % improvement of first versus last version of the code
        value_first = release_results_time.get(release_labels[0], {}).get(nodes, np.nan)
        value_last  = release_results_time.get(release_labels[-1],{}).get(nodes, np.nan)

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

