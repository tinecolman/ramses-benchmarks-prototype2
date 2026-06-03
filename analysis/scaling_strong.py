import numpy as np
import io
from matplotlib import pyplot as plt
from visualisation import scan_data, get_colors

MAX_NNODES = 512


''' Plot evolution of execution time (different commits) for various number of nodes '''
def plot_strong_scaling(benchmarks, release_labels, reso, input_axes=None, 
                        outname='strong_scaling.png'):

    # create colors for different commits (lighter grey = older)
    colorVals = get_colors(release_labels,'gray_r')

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    # we will scan all possible number of nodes
    arr_nodes_in = range(MAX_NNODES+1)
    arr_resos_in = [reso]*len(arr_nodes_in) # resolution is the same for each number of nodes

    max_nodes = 1
    for data,label in zip(benchmarks,release_labels):

        times, arr_nodes, _, configs = scan_data(data, arr_nodes_in, arr_resos_in)

        if len(times)>0:
            axes.plot(arr_nodes,np.array(times[0])/np.array(times),
                  color=colorVals[label], marker='o', markersize=4, label=label)
            max_nodes = max(max_nodes,max(arr_nodes))

    # add ideal scaling line
    axes.plot([1,max_nodes],[1,max_nodes], c=(0.25,0.85,0.25),ls=':', lw=2, label='ideal')

    # layout of the figure
    if input_axes==None:
        axes.set_title(f'{data[0]['metadata']['Benchmark']} {reso} on {data[0]['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('speedup')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


''' Generate strong scaling efficiency table, in markdown or latex format '''
def table_strong_scaling(benchmarks, release_labels, reso, fmt='markdown'):

    out = io.StringIO()

    # ---------- Header ----------

    ncols = len(release_labels) + 1

    if fmt == 'markdown':
        header = "| nodes | " + " | ".join(release_labels) + " |"
        sep    = "|" + "---|"*ncols
        print(header, file=out)
        print(sep, file=out)

    elif fmt == 'latex':
        header = "nodes & " + " & ".join(release_labels) + r" \\"
        print(r"\begin{tabular}{" + "l"*ncols + "}", file=out)
        print(r"\hline", file=out)
        print(header, file=out)
        print(r"\hline", file=out)
    else:
        raise ValueError("[table_strong_scaling] fmt must be 'markdown' or 'latex'")

    # ---------- Gather table entries from all releases ----------

    # we will scan all possible number of nodes
    arr_nodes_in = range(MAX_NNODES+1)
    arr_resos_in = [reso]*len(arr_nodes_in) # resolution is the same for each number of nodes

    release_results = {}
    all_nodes = set()
    for data,label in zip(benchmarks,release_labels):

        # Extract results from the benchmark data 
        times, avail_nodes, avail_resos, configs = scan_data(data, arr_nodes_in, arr_resos_in)

        # If no data available, go to next release
        if len(avail_nodes)==0:
            continue

        col = {}
        for nodes, time, config in zip(avail_nodes, times, configs):
            # choose the lowest number of nodes available as reference
            efficiency = (times[0]/time) / (nodes/avail_nodes[0])
            # add optimal mpi-omp config unless it's mpi-only on full node
            if config=='MPI=128 OMP=0' or config=='MPI=112 OMP=0':
                col[nodes] = (f"{efficiency:.3f}")
            else:
                col[nodes] = (f"{efficiency:.3f} ({config})")
            # gather for which numbers of nodes we need to write an entry
            all_nodes.add(nodes)

        release_results[label] = col

    all_nodes = sorted(all_nodes)

    # ---------- Print table row by row ----------

    for nodes in all_nodes:
        row = [str(nodes)]

        for label in release_labels:
            value = release_results.get(label,{}).get(nodes, "")
            row.append(value)

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
        description='Produce strong scaling plot and table')

    parser.add_argument('-p', '--path', required=True, help='Path to the benchmark directory')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    #--------- Load benchmark data ------------
    from io_timings import add_data
    data = add_data([], args.path, args.benchmark, which=args.timer)
    release_label = args.path.split('/')[-2][10:]
    cluster = data[0]['metadata']['Cluster']

    #--------- Make figure ------------
    filename = f'strong_scaling_{args.benchmark}_{args.reso}_{args.timer}_{cluster}.png'
    plot_strong_scaling([data], [release_label], args.reso, outname=filename)
    print(f'Figure outputted to {filename}')

    #--------- Make table ------------
    print(f'{COLOR} Strong scaling efficiency for {args.benchmark} {args.reso} ({args.timer}){NC}')
    table = table_strong_scaling([data], [release_label], args.reso, fmt='latex')
    print(table)