import numpy as np
import io
from matplotlib import pyplot as plt
from visualisation import scan_data, get_colors


''' Make a figure of the weak scaling comparing different commits '''
def plot_weak_scaling(benchmarks, release_labels, arr_nodes_in, resos,
                      input_axes=None, outname='evo_weak_scaling.png'):

    # create colors for different commits (lighter grey = older)
    colorVals = get_colors(release_labels,'gray_r')

    # create figure if none is given
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    max_nodes = 1
    for data,label in zip(benchmarks,release_labels):
        times, avail_nodes, avail_resos, configs = scan_data(data, arr_nodes_in, resos)

        if len(times)>0:
            axes.plot(avail_nodes, np.array(times[0])/np.array(times),
                  color=colorVals[label], marker='o', markersize=4, label=label)
            max_nodes = max(max_nodes,max(avail_nodes))

    # add ideal scaling line
    axes.plot([1,max_nodes],[1,1], c=(0.25,0.85,0.25), ls=':', lw=2)

    if input_axes==None:
        axes.set_title(f'{data[0]['metadata']['Benchmark']} on {data[0]['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('efficiency')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


''' Generate weak scaling efficiency table, in markdown or latex format '''
def table_weak_scaling(benchmarks, release_labels, arr_nodes_in, resos, fmt='markdown'):

    out = io.StringIO()

    # ---------- Header ----------

    ncols = len(release_labels) + 2

    if fmt == 'markdown':
        header = ("| nodes | resolution | " + " | ".join(release_labels) + " |")
        sep = "|" + "---|"*ncols
        print(header, file=out)
        print(sep, file=out)

    elif fmt == 'latex':
        header = ("nodes & resolution & " + " & ".join(release_labels) + r" \\")
        print(r"\begin{tabular}{" + "l"*ncols + "}", file=out)
        print(r"\hline", file=out)
        print(header, file=out)
        print(r"\hline", file=out)
    else:
        raise ValueError("[table_weak_scaling] fmt must be 'markdown' or 'latex'")

    # ---------- Gather table entries from all releases ----------

    release_results = {}
    for data, label in zip(benchmarks, release_labels):
    
        # Extract results from the benchmark data 
        times, avail_nodes, avail_resos, configs = scan_data(data, arr_nodes_in, resos)

        # If no data available, go to next release
        if len(avail_nodes)==0:
            continue

        col = {}
        for nodes, reso, time, config in zip(avail_nodes, avail_resos, times, configs):
            # choose the lowest number of nodes available as reference
            efficiency = times[0] / time
            # add optimal mpi-omp config unless it's mpi-only on full node
            if config=='MPI=128 OMP=0' or config=='MPI=112 OMP=0':
                col[nodes] = (f"{efficiency:.3f} ")
            else:
                col[nodes] = (f"{efficiency:.3f} ({config})")

        release_results[label] = col

    # ---------- Print table row by row ----------

    for nodes, reso in zip(arr_nodes_in,resos):
        row = [str(nodes), str(reso)]

        for label in release_labels:
            # get the entry or put a dash when no entry is available
            value = release_results.get(label,{}).get(nodes,"-")
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

    import argparse
    parser = argparse.ArgumentParser(
        description='Plot benchmark weak scaling'
    )

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    from resolutions import get_weak_scaling_config
    nodes, resos = get_weak_scaling_config(args.benchmark)

    from tagged_data import load_release_data
    benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, args.timer)

    plot_weak_scaling(
        benchmarks,
        release_labels,
        nodes, resos,
        outname=f'weak_scaling_{args.benchmark}_{args.timer}_{args.cluster}.png'
    )

    table = table_weak_scaling(benchmarks, release_labels, nodes, resos, fmt='latex')
    print(table)