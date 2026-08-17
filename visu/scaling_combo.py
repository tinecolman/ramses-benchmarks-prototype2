import numpy as np
import io
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx
import matplotlib.lines as mlines
from visualisation import search_best_config

''' Plot evolution of execution time (different commits) for various number of nodes '''
def plot_scaling_combo1(benchmarks, release_labels, resos, input_axes=None, 
                        outname='scaling.png'):

    # create figure if none provided
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    for reso, cmap in zip(resos, ['Purples', 'Blues', 'Greens']):

        # create colors for different commits (lighter grey = older)
        cmap = plt.get_cmap(cmap)
        cNorm  = colorsx.Normalize(vmin=0, vmax=len(release_labels))
        colorVals =  {}
        for val,commit in zip(range(1,len(release_labels)+1),release_labels):
            colorVals[commit] = cmap(cNorm(val))

        max_nodes = 1
        for data,label in zip(benchmarks,release_labels):
            times = []
            arr_nodes = []
            configs = []
            for nodes in range(512):
                # search best average time amongst mpi-omp configs
                best_entry, best_time = search_best_config(data,reso,nodes)

                if best_entry is not None:
                    times.append(float(best_time))
                    arr_nodes.append(nodes)
                    best_config = f'MPI={best_entry['mpi_procs_per_node']} OMP={best_entry['omp_threads']}'
                    configs.append(best_config)

            if len(times)>0:
                axes.plot(arr_nodes,np.array(times),
                    color=colorVals[label], marker='o', markersize=4, label=label)
                max_nodes = max(max_nodes,max(arr_nodes))

        # add ideal scaling line
        #axes.plot([1,max_nodes],[1,max_nodes], c=(0.25,0.85,0.25),ls=':', lw=2)

    # layout of the figure
    if input_axes==None:
        axes.set_title(f'{data[0]['metadata']['Benchmark']} {reso} on {data[0]['metadata']['Cluster']}')
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('time')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()



def plot_scaling_combo2(
        benchmarks,
        release_labels,
        resos,
        input_axes=None,
        outname='scaling.png'):

    if input_axes is None:
        fig, ax = plt.subplots(figsize=(7,5))
    else:
        ax = input_axes

    markers = ['o', 's', '^', 'D', 'v']

    weak_scaling_points = {}

    # ---------- COMMIT COLORS ----------
    cmap = plt.get_cmap('viridis')
    norm = colorsx.Normalize(vmin=0, vmax=len(release_labels)-1)

    commit_colors = {
        label: cmap(norm(i))
        for i, label in enumerate(release_labels)
    }

    # ---------- MAIN LOOP ----------
    for ireso, reso in enumerate(resos):

        marker = markers[ireso % len(markers)]

        for data, label in zip(benchmarks, release_labels):

            times = []
            arr_nodes = []

            for nodes in range(512):

                # search best average time amongst mpi-omp configs
                best_entry, best_time = search_best_config(data,reso,nodes)

                if best_entry is not None:

                    times.append(best_time)
                    arr_nodes.append(nodes)

                    # store for weak scaling connection
                    weak_key = (label, nodes*reso)

                    weak_scaling_points.setdefault(weak_key, [])
                    weak_scaling_points[weak_key].append(
                        (nodes, best_time)
                    )

            # ---------- STRONG SCALING ----------
            if times:
                ax.plot(
                    arr_nodes,
                    times,
                    color=commit_colors[label],
                    marker=marker,
                    lw=2,
                    label=None
                )

    # ---------- WEAK SCALING CONNECTIONS ----------
    for key, pts in weak_scaling_points.items():

        if len(pts) < 2:
            continue

        pts = sorted(pts)

        xs, ys = zip(*pts)

        ax.plot(
            xs,
            ys,
            '--',
            color='0.5',
            lw=1,
            alpha=0.7
        )

    # ---------- LEGENDS ----------

    commit_handles = [
        mlines.Line2D(
            [], [], color=commit_colors[label],
            lw=2,
            label=label
        )
        for label in release_labels
    ]

    reso_handles = [
        mlines.Line2D(
            [], [],
            color='k',
            marker=markers[i],
            linestyle='None',
            label=f"reso={reso}"
        )
        for i, reso in enumerate(resos)
    ]

    weak_handle = mlines.Line2D(
        [], [],
        color='0.5',
        linestyle='--',
        label='weak scaling'
    )

    legend1 = ax.legend(
        handles=commit_handles,
        title='Commit',
        loc='upper right'
    )

    ax.add_artist(legend1)

    ax.legend(
        handles=reso_handles + [weak_handle],
        title='Style',
        loc='lower left'
    )

    # ---------- AXES ----------
    ax.set_xlabel('nodes')
    ax.set_ylabel('time')

    ax.set_xscale('log')
    ax.set_yscale('log')

    if input_axes is None:

        sample = benchmarks[0][0]

        ax.set_title(
            f"{sample['metadata']['Benchmark']} "
            f"on {sample['metadata']['Cluster']}"
        )

        plt.savefig(
            outname,
            bbox_inches='tight',
            dpi=200
        )
        plt.close()


def plot_scaling_combo3(benchmarks, release_labels, resos, weak_scaling_map,
        input_axes=None, outname='scaling.png'):

    # ---------- FIGURE ----------
    if input_axes is None:
        fig, ax = plt.subplots(figsize=(6,5))
    else:
        ax = input_axes
        fig = ax.figure

    # ---------- RESOLUTION COLORMAPS ----------
    resolution_cmaps = {
        reso: cmap
        for reso, cmap in zip(
            resos,
            ['Purples','Blues','Greens','Oranges','Reds']
        )
    }

    commit_norm = colorsx.Normalize(
        vmin=-0.6,
        vmax=len(release_labels)-0.75
    )

    colorvals = {}

    for reso in resos:

        cmap = plt.get_cmap(
            resolution_cmaps[reso]
        )

        colorvals[reso] = {

            label: cmap(commit_norm(i))

            for i, label in enumerate(
                release_labels
            )
        }

    weak_groups = {}

    # ---------- MAIN PLOT ----------
    for reso in resos:

        for data, label in zip(
                benchmarks,
                release_labels):

            arr_nodes = []
            times = []

            for nodes in range(512):

                # search best average time amongst mpi-omp configs
                best_entry, best_time = search_best_config(data,reso,nodes)

                if best_entry is None:
                    continue

                arr_nodes.append(nodes)
                times.append(best_time)

                # weak scaling grouping
                reference_nodes = (
                    nodes /
                    weak_scaling_map[reso]
                )

                weak_key = (
                    label,
                    reference_nodes
                )

                weak_groups.setdefault(
                    weak_key,
                    []
                )

                weak_groups[weak_key].append(
                    (
                        nodes,
                        best_time,
                        reso
                    )
                )

            # ---------- STRONG SCALING ----------
            if times:
                ax.plot(
                    arr_nodes,
                    times,
                    '-o',
                    color=colorvals[reso][label],
                    lw=1.7,
                    ms=4,
                    zorder=3
                )

                # reference line
                ax.plot([arr_nodes[0],arr_nodes[-1]],[times[0],times[0]/arr_nodes[-1]],
                         lw=0.8, ls=':', color='black', zorder=1)

    # ---------- WEAK SCALING ----------
    for key, pts in weak_groups.items():

        if len(pts) < 2:
            continue

        pts = sorted(pts)

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]

        ax.plot(
            xs,
            ys,
            '--',
            color='0.25',
            lw=1.3,
            #alpha=0.75,
            zorder=2
        )

        # reference line
        ax.plot([xs[0],xs[-1]],[ys[0],ys[0]], lw=0.8, ls=':', color='black', zorder=1)

    # ---------- LEGEND 1 : RELEASE ----------
    grey_cmap = plt.get_cmap('Greys')

    commit_handles = [

        mlines.Line2D(
            [],
            [],
            color=grey_cmap(
                commit_norm(i)
            ),
            lw=2,
            label=label
        )

        for i, label in enumerate(
            release_labels
        )
    ]

    # ---------- LEGEND 2 : RESOLUTION ----------
    reso_handles = []

    for reso in resos:

        cmap = plt.get_cmap(
            resolution_cmaps[reso]
        )

        reso_handles.append(

            mlines.Line2D(
                [],
                [],
                color=cmap(0.65),
                lw=2,
                label=reso
            )
        )

    # ---------- LEGEND 3 : SCALING TYPE ----------
    style_handles = [

        mlines.Line2D(
            [],
            [],
            color='k',
            lw=2,
            linestyle='-',
            label='strong scaling'
        ),

        mlines.Line2D(
            [],
            [],
            color='0.45',
            lw=2,
            linestyle='--',
            label='weak scaling'
        )
    ]

    # ---------- LEGEND LAYOUT ----------
    fig.subplots_adjust(right=0.72)

    leg1 = ax.legend(
        handles=commit_handles,
        title='Release age',
        loc='upper left',
        bbox_to_anchor=(1.02,1.00)
    )

    ax.add_artist(leg1)

    leg2 = ax.legend(
        handles=reso_handles,
        title='Resolution',
        loc='upper left',
        bbox_to_anchor=(1.02,0.62)
    )

    ax.add_artist(leg2)

    ax.legend(
        handles=style_handles,
        title='Scaling',
        loc='upper left',
        bbox_to_anchor=(1.02,0.34)
    )

    # ---------- AXES ----------
    ax.set_xlabel('number of nodes')
    ax.set_ylabel('time')

    ax.set_xscale('log')
    ax.set_yscale('log')

    # ---------- TITLE ----------
    if benchmarks and benchmarks[0]:

        sample = benchmarks[0][0]

        ax.set_title(
            f"{sample['metadata']['Benchmark']} "
            f"on {sample['metadata']['Cluster']}"
        )

    # ---------- SAVE ----------
    if input_axes is None:

        plt.savefig(
            outname,
            bbox_inches='tight',
            dpi=200
        )

        plt.close()


def plot_scaling_combo_inverse(
        benchmark,
        resos,
        weak_scaling_map,
        input_axes=None,
        outname='scaling_combo.png'):

    # ---------- FIGURE ----------
    if input_axes is None:
        fig, ax = plt.subplots(figsize=(6,5))
    else:
        ax = input_axes
        fig = ax.figure

    # ---------- RESOLUTION COLORS ----------
    resolution_cmaps = {
        reso: cmap
        for reso, cmap in zip(
            resos,
            ['Purples','Blues','Greens','Oranges','Reds']
        )
    }

    weak_groups = {}

    xmin = np.inf
    xmax = 0

    # ---------- MAIN PLOT ----------
    for reso in resos:

        cmap = plt.get_cmap(
            resolution_cmaps[reso]
        )

        color = cmap(0.7)

        arr_nodes = []
        throughputs = []

        for nodes in range(512):

            # search best average time amongst mpi-omp configs
            best_entry, best_time = search_best_config(benchmark,reso,nodes)

            if best_entry is None:
                continue

            throughput = 1.0 / best_time

            arr_nodes.append(nodes)
            throughputs.append(throughput)

            xmin = min(xmin, nodes)
            xmax = max(xmax, nodes)

            # weak scaling grouping
            reference_nodes = (
                nodes /
                weak_scaling_map[reso]
            )

            weak_key = reference_nodes

            weak_groups.setdefault(
                weak_key,
                []
            )

            weak_groups[weak_key].append(
                (
                    nodes,
                    throughput,
                    reso
                )
            )

        # ---------- STRONG SCALING ----------
        if throughputs:

            ax.plot(
                arr_nodes,
                throughputs,
                '-o',
                color=color,
                lw=1.7,
                ms=4,
                zorder=3
            )

            # ideal strong scaling
            ref_x = arr_nodes[0]
            ref_y = throughputs[0]

            xguide = np.array([xmin, xmax])

            yguide = ref_y * xguide / ref_x

            ax.plot(
                xguide,
                yguide,
                ':',
                lw=0.8,
                color='black',
                zorder=1
            )

    # ---------- WEAK SCALING ----------
    for key, pts in weak_groups.items():

        if len(pts) < 2:
            continue

        pts = sorted(pts)

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]

        ax.plot(
            xs,
            ys,
            '--',
            color='0.15',
            lw=1.3,
            zorder=2
        )

        # ideal weak scaling
        ax.hlines(
            ys[0],
            xmin,
            xmax,
            ls=':',
            lw=0.8,
            color='0.25',
            zorder=1
        )

    # ---------- LEGEND : RESOLUTION ----------
    reso_handles = []

    for reso in resos:

        cmap = plt.get_cmap(
            resolution_cmaps[reso]
        )

        reso_handles.append(

            mlines.Line2D(
                [],
                [],
                color=cmap(0.7),
                lw=2,
                label=reso
            )
        )

    # ---------- LEGEND : SCALING ----------
    style_handles = [

        mlines.Line2D(
            [],
            [],
            color='k',
            lw=2,
            linestyle='-',
            label='strong'
        ),

        mlines.Line2D(
            [],
            [],
            color='0.15',
            lw=2,
            linestyle='--',
            label='weak'
        ),

        mlines.Line2D(
            [],
            [],
            color='0.25',
            lw=1,
            linestyle=':',
            label='ideal'
        )
    ]

    leg1 = ax.legend(
        handles=reso_handles,
        title='Resolution',
        loc='lower center'
    )

    ax.add_artist(leg1)

    ax.legend(
        handles=style_handles,
        title='Scaling',
        loc='lower right'
    )

    # ---------- AXES ----------
    ax.set_xlabel('number of nodes')
    ax.set_ylabel('performance (1/time)')

    ax.set_xscale('log')
    ax.set_yscale('log')

    # ---------- TITLE ----------
    if benchmark:

        sample = benchmark[0]

        ax.set_title(
            f"{sample['metadata']['Benchmark']} "
            f"on {sample['metadata']['Cluster']}"
        )

    # ---------- SAVE ----------
    if input_axes is None:

        plt.savefig(
            outname,
            bbox_inches='tight',
            dpi=200
        )

        plt.close()

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Plot benchmark strong scaling'
    )

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')

    args = parser.parse_args()

    from resolutions import get_weak_scaling_config
    nodes, resos = get_weak_scaling_config(args.benchmark)

    #plot_scaling_combo(
    #    benchmarks,
    #    release_labels,
    #    resos,
    #    outname=f'images/scaling_combo_{args.benchmark}_{args.timer}_{args.cluster}.png'
    #)

    weak_scaling_map = {
        "256": 1,
        "512": 8,
        "1024": 64
    }

    #from tagged_data import load_release_data
    #benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, args.timer)

    #plot_scaling_combo(
    #    benchmarks,
    #    release_labels,
    #    resos,
    #    weak_scaling_map,
    #    outname=f'images/scaling_combo_{args.benchmark}_{args.timer}_{args.cluster}.png'
    #)

    from tagged_data import load_latest_release_data
    benchmark, release_label = load_latest_release_data(args.cluster, args.benchmark, args.timer)

    #plot_scaling_combo3(
    #    [benchmark],
    #    [release_label],
    #    resos,
    #    weak_scaling_map,
    #    outname=f'images/scaling_combo_{args.benchmark}_{args.timer}_{args.cluster}.png'
    #)

    plot_scaling_combo_inverse(
            benchmark,
            resos,
            weak_scaling_map,
            outname=f'images/scaling_combo_{args.benchmark}_{args.timer}_{args.cluster}.png'
    )