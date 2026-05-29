import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
from visualisation import process_times
import io

''' Plot evolution of execution time (different commits) for various number of nodes '''
def plot_strong_scaling(benchmarks, release_labels, reso, input_axes=None, 
                        outname='evo_exectime.png'):

    # create colors for different commits (lighter grey = older)
    cmap = plt.get_cmap('gray_r')
    cNorm  = colorsx.Normalize(vmin=0, vmax=len(release_labels))
    colorVals =  {}
    for val,commit in zip(range(1,len(release_labels)+1),release_labels):
        colorVals[commit] = cmap(cNorm(val))

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    max_nodes = 1
    for data,label in zip(benchmarks,release_labels):
        times = []
        arr_nodes = []
        configs = []
        for nodes in range(512):
            best_entry = None
            best_time = np.inf

            # search best time among mpi-omp configs
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
                arr_nodes.append(nodes)
                best_config = f'MPI={best_entry['mpi_procs_per_node']} OMP={best_entry['omp_threads']}'
                configs.append(best_config)

        if len(times)>0:
            axes.plot(arr_nodes,np.array(times[0])/np.array(times),
                  color=colorVals[label], marker='o', markersize=4, label=label)
            max_nodes = max(max_nodes,max(arr_nodes))

    # add ideal scaling line
    axes.plot([1,max_nodes],[1,max_nodes], c=(0.25,0.85,0.25),ls=':', lw=2)

    # layout of the figure
    if input_axes==None:
        axes.set_title(f'{entry['metadata']['Benchmark']} {reso} on {entry['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('speedup')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


def table_strong_scaling(
        benchmarks,
        release_labels,
        reso,
        fmt='markdown'):
    """
    Print strong scaling efficiency table.

    Parameters
    ----------
    fmt : str
        'markdown' or 'latex'
    """

    release_results = {}
    all_nodes = set()

    for data, label in zip(benchmarks, release_labels):

        best_per_node = {}

        # find fastest config per node
        for nodes in range(512):

            best_entry = None
            best_time = np.inf

            for entry in data:

                if entry['resolution'] != reso:
                    continue

                if entry['nodes'] != nodes:
                    continue

                time, error_min, error_max = process_times(entry['timings'])

                if time < best_time:
                    best_time = time
                    best_entry = entry

            if best_entry is not None:

                best_per_node[nodes] = {
                    'time': float(best_time),
                    'config':
                        f"MPI={best_entry['mpi_procs_per_node']} "
                        f"OMP={best_entry['omp_threads']}"
                }

        if len(best_per_node) == 0:
            continue

        baseline_nodes = min(best_per_node.keys())
        baseline_time = best_per_node[baseline_nodes]['time']

        col = {}

        for nodes in sorted(best_per_node.keys()):

            runtime = best_per_node[nodes]['time']

            speedup = baseline_time / runtime
            efficiency = speedup / (nodes / baseline_nodes)

            config = best_per_node[nodes]['config']

            col[nodes] = f"{efficiency:.3f} ({config})"

            all_nodes.add(nodes)

        release_results[label] = col

    all_nodes = sorted(all_nodes)

    out = io.StringIO()

    # ---------- Markdown ----------
    if fmt == 'markdown':

        header = "| nodes | " + " | ".join(release_labels) + " |"
        sep    = "|" + "---|"*(len(release_labels)+1)

        print(header, file=out)
        print(sep, file=out)

        for nodes in all_nodes:

            row = [str(nodes)]

            for label in release_labels:
                value = release_results.get(label, {}).get(nodes, "")
                row.append(value)

            print("| " + " | ".join(row) + " |", file=out)

    # ---------- LaTeX ----------
    elif fmt == 'latex':

        ncols = len(release_labels) + 1

        print(r"\begin{tabular}{" + "l"*ncols + "}", file=out)
        print(r"\hline", file=out)

        header = "nodes & " + " & ".join(release_labels) + r" \\"
        print(header, file=out)

        print(r"\hline", file=out)

        for nodes in all_nodes:

            row = [str(nodes)]

            for label in release_labels:
                value = release_results.get(label, {}).get(nodes, "")
                row.append(value)

            print(" & ".join(row) + r" \\", file=out)

        print(r"\hline", file=out)
        print(r"\end{tabular}", file=out)

    else:
        raise ValueError("fmt must be 'markdown' or 'latex'")
    
    return out.getvalue()

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Plot benchmark strong scaling'
    )

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    from tagged_data import load_release_data
    benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, args.timer)

    plot_strong_scaling(
        benchmarks,
        release_labels,
        args.reso,
        outname=f'images/strong_scaling_{args.benchmark}_{args.reso}_{args.timer}_{args.cluster}.png'
    )

    #table = table_strong_scaling(benchmarks, release_labels, args.reso, fmt='markdown')
    table = table_strong_scaling(benchmarks, release_labels, args.reso, fmt='latex')
    print(table)


#python scaling_strong.py -c meluxina -b sedov -r 1024
#python scaling_strong.py -c meluxina -b sedov-amr -r lvl5-10

#python scaling_strong.py -c discoverer -b sedov -r 1024
#python scaling_strong.py -c discoverer -b sedov-amr -r lvl5-10
