'''
Speedup t_MPI/t_hybrid of the total execution time for every hybrid
configuration and number of nodes, as heatmaps: one row per cluster and one
column per benchmark. It shows which configurations, besides the fastest one,
also perform well. The continuous color scale is that of the module figure
(continuous_speedup_scale in omp_module_gain_heatmap.py), the
speedup is written in every cell (two decimals below a factor 2, so that the
configurations close to MPI-only can be compared). The fastest configuration
on every number of nodes is framed with a thick line, and the configurations
within NEAR_OPTIMAL of its execution time with a thin line. Missing runs are
hatched.

The runs with one thread and the configurations in GRID_EXCLUDED_THREADS are
left out.

With --relative, the cells show instead the extra execution time t/t_best - 1
(in %) with respect to the fastest configuration on the same number of nodes,
on a sequential color scale (RELATIVE_BOUNDS), so that the difference with the
optimum is seen directly. Configurations more than 2% slower than MPI-only
(MPI_SLOWER) are blacked out.

Run from the visu directory:
    python omp_total_ratio_grid.py -c marenostrum lumi meluxina
    python omp_total_ratio_grid.py -c marenostrum lumi meluxina --relative
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import STYLE
from openmp_best_speedup import get_openmp_dirs, benchmark_label, cluster_label
from mpi_module_share import BENCHMARKS, DESCRIPTION_MODULES, order_modules
from omp_module_gain_heatmap import module_speed_ratios, continuous_speedup_scale, CMAP
# same width, cell shape and font sizes as the module figure
from omp_module_gain_paper import FIG_WIDTH, CELL_ASPECT, TITLE_SIZE, LABEL_SIZE, TICK_SIZE
# horizontal extent of the panels, as fractions of the figure width
LEFT = 0.1
RIGHT = 1.

# Numbers of OpenMP threads left out per cluster: the configurations spanning
# several NUMA domains on LUMI (except 4x32, to show the effect) and on MeluXina.
# 7x16 on MareNostrum 5 is kept, to show the effect of crossing the sockets.
GRID_EXCLUDED_THREADS = {
    'lumi': [64, 128],
    'meluxina': [32, 64, 128],
}
# configurations whose execution time is within this factor of the fastest one
# are framed with a thin line
NEAR_OPTIMAL = 1.02
# With --plain, stars mark the fastest configuration and those whose execution time
# is within these factors of it, as (factor, marker size in units of the cell width),
# the fastest one largest
STAR_LEVELS = [(1., 0.37), (1.02, 0.25), (1.05, 0.14)]
# On the relative scale, configurations slower than MPI-only by more than this factor
# are blacked out
MPI_SLOWER = 1.02
# Edges of the bins of the slowdown t/t_best with respect to the fastest configuration
RELATIVE_BOUNDS = [1., 1.02, 1.05, 1.1, 1.2, 1.5, 2.]



''' Discrete sequential color scale of the slowdown with respect to the fastest
    configuration: the loss side of CMAP, from white (optimal) to dark orange '''
def discrete_relative_scale():
    ncolors = len(RELATIVE_BOUNDS)
    cmap = mcolors.ListedColormap(plt.get_cmap(CMAP)(np.linspace(0.5, 0., ncolors)))
    cmap.set_bad((0., 0., 0., 0.))
    norm = mcolors.BoundaryNorm(RELATIVE_BOUNDS, ncolors=ncolors, extend='max')
    labels = [f'{100.*(bound-1.):.0f}' for bound in RELATIVE_BOUNDS]
    return cmap, norm, RELATIVE_BOUNDS, labels


''' Write the extra execution time with respect to the fastest configuration in
    every cell, in percent without sign or unit (12, 0 below 0.5%), and 'best'
    in bold in the cell of the fastest one '''
def write_relative_values(ax, slowdowns, best, slower_than_mpi):
    for iconf in range(slowdowns.shape[0]):
        for inode in range(slowdowns.shape[1]):
            slowdown = slowdowns[iconf, inode]
            if np.isnan(slowdown):
                continue
            extra = 100.*(slowdown-1.)
            text = 'best' if iconf==best[inode] else f'{extra:.0f}'
            dark = slowdown>=RELATIVE_BOUNDS[-2] or slower_than_mpi[iconf, inode]
            ax.text(inode, iconf, text, ha='center', va='center', fontsize=5.5, zorder=5,
                    fontweight='bold' if iconf==best[inode] else 'normal',
                    color='white' if dark else 'black')


''' Write the speedup in every cell, as ×1.12 for a gain and ÷1.12 for a loss,
    with two decimals below a factor 2. White text on the dark colors. '''
def write_all_values(ax, ratios, norm):
    for iconf in range(ratios.shape[0]):
        for inode in range(ratios.shape[1]):
            ratio = ratios[iconf, inode]
            if np.isnan(ratio):
                continue
            factor = max(ratio, 1./ratio)
            text = ('×' if ratio>=1. else '÷')+(f'{factor:.2f}' if factor<2. else f'{factor:.1f}')
            # white text on the darkest colors, at the ends of the color scale
            dark = abs(float(norm(ratio))-0.5)>0.3
            ax.text(inode, iconf, text, ha='center', va='center', fontsize=5.5,
                    color='white' if dark else 'black')


''' Speed ratio of the total time of every configuration (rows) and number of
    nodes (columns) for one cluster and benchmark '''
def total_speed_ratios(cluster, bench, reso):
    from tagged_data import EXCLUDED_COMPILERS
    entries = load_timer_breakdown(get_openmp_dirs(cluster, bench), bench, reso,
                                   exclude_compilers=EXCLUDED_COMPILERS)
    nodes, configs, ratios = module_speed_ratios(entries, order_modules(DESCRIPTION_MODULES[bench]),
                                                 GRID_EXCLUDED_THREADS.get(cluster, []))
    return nodes, configs, ratios['total']


''' With plain=True, the values and frames in the cells are replaced by stars for
    the fastest configuration and those close to it (STAR_LEVELS). '''
def plot_total_ratio_grid(clusters, benchmarks=BENCHMARKS, relative=False, plain=False,
                          outname='omp_total_ratio_grid.png'):

    data = {(cluster, bench): total_speed_ratios(cluster, bench, reso)
            for cluster in clusters for bench, reso in benchmarks}
    if relative:
        cmap, norm, bounds, bound_labels = discrete_relative_scale()
    else:
        # the color scale of the module figure, with the same limits and ticks
        cmap, norm, bounds, bound_labels = continuous_speedup_scale()
    # same numbers of nodes for all clusters in the column of a benchmark
    column_nodes = {bench: sorted({n for cluster in clusters for n in data[(cluster, bench)][0]})
                    for bench, reso in benchmarks}
    # configurations of a cluster, the same for all its benchmarks
    row_configs = {cluster: sorted({c for bench, reso in benchmarks for c in data[(cluster, bench)][1]},
                                   key=lambda config: config[1])
                   for cluster in clusters}

    # panel sizes proportional to their numbers of cells, so that all cells have the
    # same shape, CELL_ASPECT times as high as wide
    widths = [len(column_nodes[bench]) for bench, reso in benchmarks]
    heights = [len(row_configs[cluster]) for cluster in clusters]
    # the panels fill the figure between LEFT and RIGHT (fractions of FIG_WIDTH), so
    # that the figure has the width of the module figure; width of a cell in inches
    wspace = 0.08
    cell = FIG_WIDTH*(RIGHT-LEFT)/(sum(widths)+wspace*np.mean(widths)*(len(widths)-1))
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(FIG_WIDTH,
                                  CELL_ASPECT*cell*sum(heights)+0.9*len(clusters)+0.8))
        grid = fig.add_gridspec(len(clusters), len(benchmarks), width_ratios=widths,
                                height_ratios=heights, wspace=wspace, hspace=0.15,
                                left=LEFT, right=RIGHT)

        for irow, cluster in enumerate(clusters):
            configs = row_configs[cluster]
            for icol, (bench, reso) in enumerate(benchmarks):
                all_nodes = column_nodes[bench]
                nodes, bench_configs, values = data[(cluster, bench)]
                ratios = np.full((len(configs), len(all_nodes)), np.nan)
                for iconf, config in enumerate(bench_configs):
                    for inode, n in enumerate(nodes):
                        ratios[configs.index(config), all_nodes.index(n)] = values[iconf, inode]

                best = [np.nanargmax(ratios[:, inode]) if not np.all(np.isnan(ratios[:, inode])) else None
                        for inode in range(len(all_nodes))]
                if relative:
                    # slowdown t/t_best with respect to the fastest configuration
                    shown = np.nanmax(ratios, axis=0, initial=-np.inf)[np.newaxis, :]/ratios
                else:
                    shown = ratios

                ax = fig.add_subplot(grid[irow, icol])
                image = ax.imshow(shown, cmap=cmap, norm=norm, aspect=CELL_ASPECT, origin='lower', zorder=1)
                ax.add_patch(mpatches.Rectangle((-0.5, -0.5), len(all_nodes), len(configs), zorder=0,
                                                facecolor='white', edgecolor='#b0b0b0', hatch='////',
                                                linewidth=0))
                if relative:
                    # configurations clearly slower than MPI-only on the same number of nodes
                    # (by more than MPI_SLOWER, about the run-to-run variation) are blacked
                    # out, their extra time with respect to the best still written
                    slower_than_mpi = np.nan_to_num(ratios, nan=np.inf)*MPI_SLOWER<1.
                    for iconf, inode in np.argwhere(slower_than_mpi):
                        ax.add_patch(mpatches.Rectangle((inode-0.5, iconf-0.5), 1, 1, facecolor='black',
                                                        edgecolor='none', zorder=2))
                    write_relative_values(ax, shown, best, slower_than_mpi)
                elif not plain:
                    write_all_values(ax, ratios, norm)
                else:
                    # stars in the cells of the fastest configuration and of those within the
                    # factors of STAR_LEVELS of its execution time, smaller further from it
                    for inode in range(len(all_nodes)):
                        if best[inode] is None:
                            continue
                        for iconf in range(len(configs)):
                            slowdown = ratios[best[inode], inode]/ratios[iconf, inode]
                            if iconf==best[inode]:
                                size = STAR_LEVELS[0][1]
                            else:
                                sizes = [size for factor, size in STAR_LEVELS[1:] if slowdown<=factor]
                                if len(sizes)==0:
                                    continue
                                size = sizes[0]
                            # white stars on the darkest colors
                            color = 'white' if abs(float(norm(ratios[iconf, inode]))-0.5)>0.3 else 'black'
                            ax.plot(inode, iconf, marker='*', ms=size*cell*72., color=color, mew=0,
                                    zorder=4)
                # frame around the fastest configuration on every number of nodes (thick)
                # and, on the speedup scale, around those within NEAR_OPTIMAL of its
                # execution time (thin)
                for inode in range(len(all_nodes)):
                    if best[inode] is None or plain:
                        continue
                    for iconf in range(len(configs)):
                        if relative or iconf==best[inode] \
                           or not ratios[iconf, inode]*NEAR_OPTIMAL>=ratios[best[inode], inode]:
                            continue
                        ax.add_patch(mpatches.Rectangle((inode-0.44, iconf-0.44), 0.88, 0.88, fill=False,
                                                        edgecolor='black', linewidth=0.6, zorder=3))
                    # on the relative scale the fastest configuration is marked by 'best'
                    if not relative:
                        ax.add_patch(mpatches.Rectangle((inode-0.5, best[inode]-0.5), 1, 1, fill=False,
                                                        edgecolor='black', linewidth=1.3, zorder=4))
                ax.set_xticks(range(len(all_nodes)), labels=[str(n) for n in all_nodes], fontsize=TICK_SIZE)
                ax.set_yticks(range(len(configs)), labels=[f'{mpi}×{omp}' for mpi, omp in configs],
                              fontsize=TICK_SIZE)
                ax.grid(False)
                ax.tick_params(length=0)
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('black')
                    spine.set_linewidth(0.8)
                    spine.set_zorder(2)
                if irow==0:
                    ax.set_title(benchmark_label(bench, reso), fontsize=TITLE_SIZE)
                if irow==len(clusters)-1:
                    ax.set_xlabel('number of nodes', fontsize=LABEL_SIZE)
                if icol==0:
                    ax.set_ylabel(f'{cluster_label(cluster)}\nMPI × OMP', fontsize=LABEL_SIZE)
                else:
                    ax.set_yticklabels([])

        cbar = fig.colorbar(image, ax=fig.axes, orientation='horizontal', spacing='uniform',
                            shrink=0.8, aspect=50, pad=0.08, extend='max' if relative else 'neither')
        cbar.set_ticks(bounds, labels=bound_labels)
        cbar.ax.minorticks_off()
        if relative:
            cbar.set_label('extra time with respect to the fastest configuration, '
                           '$t/t_\\mathrm{best}-1$ [%]')
        else:
            cbar.set_label('slower ($t_\\mathrm{hybrid}/t_\\mathrm{MPI}$)   |   '
                           'faster ($t_\\mathrm{MPI}/t_\\mathrm{hybrid}$)')
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Speedup of the total time for every hybrid configuration, per cluster and benchmark')
    parser.add_argument('-c', '--clusters', nargs='+', default=['marenostrum', 'lumi', 'meluxina'],
                        help='Cluster names')
    parser.add_argument('--relative', action='store_true',
                        help='Show the extra time with respect to the fastest configuration instead')
    parser.add_argument('--plain', action='store_true',
                        help='Stars for the fastest and near-optimal configurations (STAR_LEVELS) '
                             'instead of values and frames')
    args = parser.parse_args()

    suffix = ('_relative' if args.relative else '')+('_plain' if args.plain else '')
    plot_total_ratio_grid(args.clusters, relative=args.relative, plain=args.plain,
                          outname=f'omp_total_ratio_grid{suffix}_{"_".join(args.clusters)}.png')
