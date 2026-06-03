import numpy as np
import io
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
from visualisation import search_best_config


''' Make a figure of the weak scaling comparing different commits '''
def plot_weak_scaling(benchmarks, release_labels, arr_nodes_in, resos,
                      input_axes=None, outname='evo_weak_scaling.png'):

    # create colors for different commits (lighter grey = older)
    cmap = plt.get_cmap('gray_r')
    cNorm  = colorsx.Normalize(vmin=0, vmax=len(release_labels))
    colorVals =  {}
    for val,commit in zip(range(1,len(release_labels)+1),release_labels):
        colorVals[commit] = cmap(cNorm(val))

    # create figure if none is given
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    max_nodes = 1
    for data,label in zip(benchmarks,release_labels):
        times = []
        arr_nodes = []
        configs = []
        for nodes,reso in zip(arr_nodes_in, resos):

            # search best average time amongst mpi-omp configs
            best_entry, best_time = search_best_config(data,reso,nodes)

            if best_entry is not None:
                times.append(float(best_time))
                arr_nodes.append(nodes)
                best_config = f'MPI={best_entry['mpi_procs_per_node']} OMP={best_entry['omp_threads']}'
                configs.append(best_config)

        if len(times)>0:
            axes.plot(arr_nodes, np.array(times[0])/np.array(times),
                  color=colorVals[label], marker='o', markersize=4, label=label)
            max_nodes = max(max_nodes,max(arr_nodes))

    # add ideal scaling line
    axes.plot([1,max_nodes],[1,1], c=(0.25,0.85,0.25), ls=':', lw=2)

    if input_axes==None:
        axes.set_title(f'{entry['metadata']['Benchmark']} {reso} on {entry['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('efficiency')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()


def table_weak_scaling(benchmarks, release_labels, arr_nodes_in, resos,
        fmt='markdown'):
    """
    Generate weak scaling efficiency table.

    Rows:
        (nodes, resolution)

    Columns:
        releases

    Entries:
        efficiency (MPI=x OMP=y)
    """

    out = io.StringIO()

    # ---------- HEADER ----------

    if fmt == 'markdown':

        header = (
            "| Nodes | Resolution | "
            + " | ".join(release_labels)
            + " |"
        )

        sep = "|" + "---|"*(len(release_labels)+2)

        print(header, file=out)
        print(sep, file=out)

    elif fmt == 'latex':

        ncols = len(release_labels) + 2

        print(r"\begin{tabular}{" + "l"*ncols + "}",
              file=out)
        print(r"\hline", file=out)

        header = (
            "Nodes & Resolution & "
            + " & ".join(release_labels)
            + r" \\"
        )

        print(header, file=out)
        print(r"\hline", file=out)

    else:
        raise ValueError(
            "fmt must be 'markdown' or 'latex'"
        )

    # ---------- PROCESS RELEASES ----------

    release_results = {}
    for data, label in zip(benchmarks, release_labels):
        best_per_case = {}

        for nodes, reso in zip(arr_nodes_in, resos):

            # search best average time amongst mpi-omp configs
            best_entry, best_time = search_best_config(data,reso,nodes)

            if best_entry is not None:

                config = (
                    f"MPI={best_entry['mpi_procs_per_node']} "
                    f"OMP={best_entry['omp_threads']}"
                )

                best_per_case[(nodes,reso)] = {
                    'time': float(best_time),
                    'config': config
                }

        # choose first AVAILABLE weak-scaling point as reference

        baseline_key = None

        for nodes, reso in zip(arr_nodes_in, resos):

            key = (nodes, reso)

            if key in best_per_case:
                baseline_key = key
                break

        if baseline_key is None:
            continue

        baseline_time = best_per_case[
            baseline_key
        ]['time']

        col = {}

        for nodes, reso in zip(arr_nodes_in, resos):

            key = (nodes, reso)

            if key not in best_per_case:
                continue

            runtime = best_per_case[key]['time']

            efficiency = baseline_time / runtime

            config = best_per_case[key]['config']

            if config=='MPI=128 OMP=0' or config=='MPI=112 OMP=0':
                col[key] = (
                    f"{efficiency:.3f} "
                )
            else:
                col[key] = (
                    f"{efficiency:.3f} "
                    f"({config})"
                )

        release_results[label] = col

    # ---------- EMIT TABLE ----------

    for nodes, reso in zip(arr_nodes_in,resos):

        row = [str(nodes), str(reso)]

        key = (nodes,reso)

        for label in release_labels:

            value = (
                release_results
                .get(label,{})
                .get(key,"-")
            )

            row.append(value)

        if fmt == 'markdown':

            print(
                "| " + " | ".join(row) + " |",
                file=out
            )

        elif fmt == 'latex':

            print(
                " & ".join(row)
                + r" \\ \hline",
                file=out
            )

    # ---------- FOOTER ----------

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

    table_md = table_weak_scaling(benchmarks, release_labels, nodes, resos, fmt='latex')
    print(table_md)