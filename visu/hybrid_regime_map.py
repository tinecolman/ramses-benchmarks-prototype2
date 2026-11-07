'''
Regime map of the hybrid MPI-OpenMP version: in which regime is it faster than
MPI-only, and with how many threads per process. One panel per cluster (columns)
and benchmark (rows). Every run (resolution x number of nodes) is a point at
(number of nodes, number of cells per core). Its color is the speedup
t_MPI/t_hybrid of the fastest hybrid configuration, on the continuous scale of
the module figure (continuous_speedup_scale in omp_module_gain_heatmap.py) but
saturating at SPEEDUP_LIMIT, and
the number written in it is the number of OpenMP threads of that configuration.
The runs of the same resolution lie on a diagonal, which is labelled.

Only the unigrid benchmarks are shown, which have runs at several resolutions.

Run from the visu directory:
    python hybrid_regime_map.py -c marenostrum lumi meluxina
'''

import numpy as np
from matplotlib import pyplot as plt
from openmp_module_analysis import STYLE
from openmp_best_speedup import load_openmp_data, cluster_label
from omp_module_gain_heatmap import continuous_speedup_scale, EXCLUDED_THREADS

CORES_PER_NODE = {'marenostrum': 112, 'lumi': 128, 'meluxina': 128}
BENCHMARKS = ['sedov', 'cosmo']
# limit and ticks of the color scale, which saturates at a speedup (or slowdown) of 4
SPEEDUP_LIMIT = 4.
SPEEDUP_TICKS = [1.2, 1.5, 2., 3., 4.]
RESOLUTIONS = ['256', '512', '1024']


''' Speedup of the fastest hybrid configuration and its number of threads for every
    resolution and number of nodes, as a list of (resolution, nodes, cells per core,
    speedup, threads). Only runs that use the full node are taken into account. '''
def regime_points(cluster, bench):
    cores = CORES_PER_NODE[cluster]
    excluded = [1]+EXCLUDED_THREADS.get(cluster, [])
    times = {}
    for entry in load_openmp_data(cluster, bench):
        omp = entry['omp_threads']
        if entry['resolution'] not in RESOLUTIONS or len(entry['timings'])==0 or omp in excluded \
           or max(entry['mpi_procs_per_node'], 1)*max(omp, 1)!=cores:
            continue
        times.setdefault((entry['resolution'], entry['nodes']), {})[omp] = np.mean(entry['timings'])

    points = []
    for (reso, nodes), config_times in times.items():
        hybrid = {omp: time for omp, time in config_times.items() if omp>0}
        if 0 not in config_times or len(hybrid)==0:
            continue
        best = min(hybrid, key=hybrid.get)
        points.append((reso, nodes, int(reso)**3/(nodes*cores), config_times[0]/hybrid[best], best))
    return points


def plot_regime_map(clusters, benchmarks=BENCHMARKS, outname='hybrid_regime_map.png'):

    cmap, norm, bounds, bound_labels = continuous_speedup_scale(SPEEDUP_LIMIT, SPEEDUP_LIMIT, SPEEDUP_TICKS)
    data = {(cluster, bench): regime_points(cluster, bench) for cluster in clusters for bench in benchmarks}

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(nrows=len(benchmarks), ncols=len(clusters),
                                 figsize=(2.9*len(clusters), 2.6*len(benchmarks)),
                                 sharex=True, sharey=True, squeeze=False)
        fig.subplots_adjust(wspace=0.08, hspace=0.12)

        for irow, bench in enumerate(benchmarks):
            for icol, cluster in enumerate(clusters):
                ax = axes[irow, icol]
                points = data[(cluster, bench)]
                for reso in RESOLUTIONS:
                    line = sorted((nodes, cells) for r, nodes, cells, speedup, omp in points if r==reso)
                    if len(line)==0:
                        continue
                    ax.plot(*zip(*line), color='#cccccc', lw=0.8, zorder=1)
                    # label of the resolution at the end with the fewest nodes
                    ax.annotate(f'${reso}^3$', line[0], xytext=(-6, 0), textcoords='offset points',
                                ha='right', va='center', fontsize=6.5, color='#777777')
                for reso, nodes, cells, speedup, omp in points:
                    ax.scatter(nodes, cells, s=150, c=[speedup], cmap=cmap, norm=norm,
                               edgecolors='#555555', linewidths=0.5, zorder=2)
                    dark = abs(float(norm(speedup))-0.5)>0.3
                    ax.text(nodes, cells, str(omp), ha='center', va='center', fontsize=6, zorder=3,
                            color='white' if dark else 'black')
                ax.set_xscale('log', base=2)
                ax.set_yscale('log')
                ax.grid(True, which='major', color='#eeeeee', lw=0.6, zorder=0)
                if irow==0:
                    ax.set_title(cluster_label(cluster), fontweight='bold')
                if irow==len(benchmarks)-1:
                    ax.set_xlabel('number of nodes')
                if icol==0:
                    ax.set_ylabel(f'{bench}\ncells per core')
        nodes_ticks = sorted({nodes for points in data.values() for r, nodes, *rest in points})
        axes[0, 0].set_xticks(nodes_ticks, labels=[str(n) for n in nodes_ticks])
        axes[0, 0].set_xlim(min(nodes_ticks)/2.5, max(nodes_ticks)*1.6)
        axes[0, 0].minorticks_off()
        # room for the markers at the edges
        all_cells = [cells for points in data.values() for r, n, cells, *rest in points]
        axes[0, 0].set_ylim(min(all_cells)/2., max(all_cells)*2.)

        scalar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(scalar, ax=axes, orientation='horizontal', shrink=0.7, aspect=45, pad=0.16,
                            extend='both')
        cbar.set_ticks(bounds, labels=bound_labels, fontsize=8)
        cbar.ax.minorticks_off()
        cbar.set_label('speedup of the fastest hybrid configuration w.r.t. MPI-only '
                       '(number: OpenMP threads per process)')
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Regime map of the speedup of the fastest hybrid configuration and its number of threads')
    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'],
                        help='Cluster names')
    args = parser.parse_args()

    plot_regime_map(args.clusters, outname=f'hybrid_regime_map_{"_".join(args.clusters)}.png')
