'''
Combined figure for the paper of the speedup of the hybrid MPI-OpenMP
configurations with respect to MPI-only, per module, for the Sedov, cosmo and
galaxy benchmarks on one cluster. The heatmaps are those of
omp_module_gain_heatmap.py, arranged on a 4x4 grid so that the same module of
different benchmarks is shown in neighbouring panels:

    sedov (2x2, top left)   | cosmo (2x2, top right)
    galaxy (2x4, bottom)

A frame with the name of the benchmark is drawn around its panels. All panels
share the same numbers of nodes and configurations, missing runs are hatched,
and a timer missing in the hybrid run counts as an infinite speedup.

Run from the visu directory:
    python omp_module_gain_paper.py -c marenostrum
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import STYLE
from openmp_best_speedup import get_openmp_dirs
from mpi_module_share import DESCRIPTION_MODULES, order_modules
from omp_module_gain_heatmap import (module_speed_ratios, continuous_speedup_scale,
                                     EXCLUDED_THREADS)

# Panels of every benchmark, as rows of module (timer group) names, None for an
# empty spot
LAYOUT = {
    ('sedov', '1024'): [['hydro - state copy', None],
                        ['hydro - godunov', 'hydro - communication']],
    ('cosmo', '1024'): [['particles - update', 'poisson - rho'],
                        ['particles - book keeping', 'poisson - phi multigrid']],
    ('galaxy', 'highres'): [['hydro - godunov', 'hydro - communication',
                             'particles - book keeping', 'poisson - phi multigrid'],
                            ['coarse levels', 'refine', 'load balance', 'poisson - rho']],
}
# position of the first panel of every benchmark on the 4x4 grid (row, column)
ORIGIN = {
    ('sedov', '1024'): (0, 0),
    ('cosmo', '1024'): (0, 2),
    ('galaxy', 'highres'): (2, 0),
}
# Numbers of OpenMP threads left out of this figure, in addition to EXCLUDED_THREADS,
# e.g. {'marenostrum': [16]} to leave out 7x16, which places one of the seven
# processes of a node on both sockets (shown separately by omp_numa_effect.py)
PAPER_EXCLUDED_THREADS = {}
# Clusters on which the configuration with one OpenMP thread per process is shown,
# to show the overhead of the OpenMP build
SINGLE_THREAD_CLUSTERS = ['marenostrum', 'lumi']

# width of the figure in inches, small enough for the gaps between the panels to stay
# narrow. The height follows from the panels and the spaces below.
FIG_WIDTH = 7.2
# height of a cell relative to its width
CELL_ASPECT = 0.65
# vertical spaces in inches: between the rows of panels (titles), extra space between
# the top and bottom benchmarks, above the panels (name of the benchmark) and below
# them (labels of the axes and colorbar)
ROW_GAP = 0.36
BENCHMARK_GAP = 0.3
TOP_MARGIN = 0.45
BOTTOM_MARGIN = 0.95
# space around the panels inside the frame of a benchmark, and above them for its name,
# in inches
FRAME_PAD = 0.06
FRAME_LABEL = 0.24
# font sizes of the panel titles, the axis labels and the tick labels
TITLE_SIZE = 9
LABEL_SIZE = 8.5
TICK_SIZE = 7.5
# space between the frame of galaxy and the colorbar, and height of the colorbar, in inches
CBAR_GAP = 0.12
CBAR_HEIGHT = 0.15

BENCHMARK_LABELS = {
    ('sedov', '1024'): 'sedov 1024',
    ('cosmo', '1024'): 'cosmo 1024',
    ('galaxy', 'highres'): 'galaxy',
}


''' Speed ratios of the modules of every benchmark, on the common numbers of nodes
    and configurations of all benchmarks (NaN where a run is missing) '''
def gather_ratios(cluster):
    from tagged_data import EXCLUDED_COMPILERS

    results = {}
    for bench, reso in LAYOUT:
        entries = load_timer_breakdown(get_openmp_dirs(cluster, bench), bench, reso,
                                       exclude_compilers=EXCLUDED_COMPILERS)
        modules = order_modules(DESCRIPTION_MODULES[bench])
        results[(bench, reso)] = (modules,)+module_speed_ratios(entries, modules,
                                                                EXCLUDED_THREADS.get(cluster, [])
                                                                +PAPER_EXCLUDED_THREADS.get(cluster, []),
                                                                single_thread=cluster in SINGLE_THREAD_CLUSTERS)

    all_nodes = sorted({n for modules, nodes, configs, ratios in results.values() for n in nodes})
    all_configs = sorted({c for modules, nodes, configs, ratios in results.values() for c in configs},
                         key=lambda config: config[1])

    common = {}
    for key, (modules, nodes, configs, ratios) in results.items():
        common[key] = (modules, {})
        for name, values in ratios.items():
            grid = np.full((len(all_configs), len(all_nodes)), np.nan)
            for iconf, config in enumerate(configs):
                for inode, n in enumerate(nodes):
                    grid[all_configs.index(config), all_nodes.index(n)] = values[iconf, inode]
            common[key][1][name] = grid

    return all_nodes, all_configs, common


''' 4x4 grid of heatmaps of the speedup per module, for all benchmarks '''
def plot_module_gain_paper(cluster, outname='omp_module_ratio_paper.png'):

    arr_nodes, configs, results = gather_ratios(cluster)
    cmap, norm, bounds, bound_labels = continuous_speedup_scale()

    with plt.rc_context(STYLE):
        # the panels fill the width, and their height follows from the shape of the cells
        # and the number of configurations
        left, right, wspace = 0.08, 0.98, 0.12
        panel_width = FIG_WIDTH*(right-left)/(4+3*wspace)
        panel_height = panel_width*CELL_ASPECT*len(configs)/len(arr_nodes)
        # the gridspec spaces the rows by a fraction of their mean height, so the gaps in
        # inches are converted to that
        heights = [panel_height, panel_height, BENCHMARK_GAP, panel_height, panel_height]
        mean_height = sum(heights)/len(heights)
        panels_height = sum(heights)+4*ROW_GAP
        height = panels_height+TOP_MARGIN+BOTTOM_MARGIN
        fig = plt.figure(figsize=(FIG_WIDTH, height))
        # one grid for all panels, so that the columns of galaxy line up with those of
        # Sedov and cosmo, with an empty row between the top and bottom benchmarks.
        # The columns are evenly spaced, the gap between them separates the Sedov and
        # cosmo frames
        grid = fig.add_gridspec(5, 4, height_ratios=heights, left=left, right=right,
                                bottom=BOTTOM_MARGIN/height, top=1.-TOP_MARGIN/height,
                                wspace=wspace, hspace=ROW_GAP/mean_height)

        for key, rows in LAYOUT.items():
            modules, ratios = results[key]
            labels = dict(modules)
            axes = []
            for irow, row in enumerate(rows):
                for icol, name in enumerate(row):
                    if name is None:
                        continue
                    row0, col0 = ORIGIN[key]
                    # skip the empty row between the top and bottom benchmarks
                    grid_row = row0+irow+(1 if row0>=2 else 0)
                    grid_col = col0+icol
                    ax = fig.add_subplot(grid[grid_row, grid_col])
                    axes.append(ax)
                    image = ax.imshow(ratios[name], cmap=cmap, norm=norm, aspect=CELL_ASPECT,
                                      origin='lower', zorder=1)
                    ax.add_patch(mpatches.Rectangle((-0.5, -0.5), len(arr_nodes), len(configs),
                                                    zorder=0, facecolor='white', edgecolor='#b0b0b0',
                                                    hatch='////', linewidth=0))
                    ax.set_title(labels[name], fontsize=TITLE_SIZE)
                    ax.set_xticks(range(len(arr_nodes)), labels=[str(n) for n in arr_nodes],
                                  fontsize=TICK_SIZE)
                    ax.set_yticks(range(len(configs)), labels=[f'{mpi}×{omp}' for mpi, omp in configs],
                                  fontsize=TICK_SIZE)
                    ax.grid(False)
                    ax.tick_params(length=0)
                    for spine in ax.spines.values():
                        spine.set_visible(True)
                        spine.set_color('black')
                        spine.set_linewidth(0.8)
                        spine.set_zorder(2)
                    # only label the outer panels of every benchmark
                    if irow<len(rows)-1:
                        ax.set_xticklabels([])
                    else:
                        ax.set_xlabel('number of nodes', fontsize=LABEL_SIZE)
                    # the rows of all benchmarks line up, so only the first panel of every
                    # row of the figure has labels
                    first = [i for i, other in enumerate(row) if other is not None][0]
                    if col0>0 or icol>first:
                        ax.set_yticklabels([])
                    else:
                        # short, to fit next to the panels with few configurations
                        ax.set_ylabel('MPI × OMP', fontsize=LABEL_SIZE)

            # frame around the panels of the benchmark, with its name
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            boxes = [ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted()) for ax in axes]
            x0 = min(box.x0 for box in boxes)-FRAME_PAD/FIG_WIDTH
            x1 = max(box.x1 for box in boxes)+FRAME_PAD/FIG_WIDTH
            y0 = min(box.y0 for box in boxes)-FRAME_PAD/height
            y1 = max(box.y1 for box in boxes)+FRAME_LABEL/height
            fig.patches.append(mpatches.FancyBboxPatch((x0, y0), x1-x0, y1-y0, transform=fig.transFigure,
                                                       boxstyle='round,pad=0,rounding_size=0.008',
                                                       fill=False, edgecolor='#555555', linewidth=1.))
            fig.text(x0+0.01, y1-0.04/height, BENCHMARK_LABELS[key], ha='left', va='top',
                     fontsize=10, fontweight='bold')

        # horizontal colorbar under the figure, as wide as the frames of the benchmarks
        cax = fig.add_axes([0.1, y0-(CBAR_GAP+CBAR_HEIGHT)/height, 0.8, CBAR_HEIGHT/height])
        cbar = fig.colorbar(image, cax=cax, orientation='horizontal', extend='both')
        cbar.set_ticks(bounds, labels=bound_labels)
        cbar.ax.minorticks_off()
        cbar.set_label('slower ($t_\\mathrm{hybrid}/t_\\mathrm{MPI}$)   |   '
                       'faster ($t_\\mathrm{MPI}/t_\\mathrm{hybrid}$)')

        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Speedup of the hybrid configurations per module, for all benchmarks (paper figure)')

    parser.add_argument('-c', '--cluster', default='marenostrum', help='Cluster name')

    args = parser.parse_args()

    plot_module_gain_paper(args.cluster, outname=f'omp_module_ratio_paper_{args.cluster}.png')
