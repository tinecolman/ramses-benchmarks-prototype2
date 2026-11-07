'''
Effect on the modules of a hybrid configuration whose MPI processes span
several NUMA domains, compared with a neighbouring configuration whose
processes each fit in one NUMA domain. The speed ratio t_reference/t_test of
every module and of the total time is shown as a heatmap (modules x numbers of
nodes) per benchmark, with the discrete color scale of omp_module_gain_heatmap.py:
orange means that the configuration spanning NUMA domains is slower.

Two figures are made:
  * MareNostrum 5 (2 NUMA domains of 56 cores per node): 7x16, where one of the
    seven processes of a node spans both sockets, against 8x14.
  * LUMI (8 NUMA domains of 16 cores per node): 4x32, where every process spans
    two NUMA domains, against 8x16. Since this also doubles the number of
    threads, the same comparison without crossing NUMA domains is shown below
    as a control: 4x28 against 8x14 on MareNostrum 5.

Run from the visu directory:
    python omp_numa_effect.py
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import STYLE, index_runs, module_times
from openmp_best_speedup import get_openmp_dirs
from mpi_module_share import DESCRIPTION_MODULES, order_modules
from omp_module_gain_heatmap import discrete_speedup_scale

BENCHMARKS = [('sedov', '1024'), ('cosmo', '1024'), ('galaxy', 'highres')]
BENCHMARK_LABELS = {'sedov': 'Sedov $1024^3$', 'cosmo': 'cosmo $1024^3$',
                    'galaxy': 'galaxy'}
# modules left out, as in the paper figure of omp_module_gain_paper.py
EXCLUDED_MODULES = {
    'sedov': ['coarse levels'],
    'cosmo': ['coarse levels'],
}

# comparisons: (cluster, MPI x OMP of the test configuration, of the reference, title)
FIGURES = {
    'marenostrum': [('marenostrum', (7, 16), (8, 14), 'MareNostrum 5: 7×16 compared with 8×14')],
    'lumi': [('lumi', (4, 32), (8, 16), 'LUMI: 4×32 compared with 8×16'),
             ('marenostrum', (4, 28), (8, 14), 'control, MareNostrum 5: 4×28 compared with 8×14')],
}


''' Speed ratio t_reference/t_test of every module and of the total time, as a 2D
    array [module, number of nodes], NaN where a run or a timer is missing.
    Returns the numbers of nodes, the module names and the array. '''
def comparison_ratios(cluster, bench, reso, test_omp, ref_omp):
    from tagged_data import EXCLUDED_COMPILERS
    entries = load_timer_breakdown(get_openmp_dirs(cluster, bench), bench, reso,
                                   exclude_compilers=EXCLUDED_COMPILERS)
    runs = index_runs(entries)
    modules = order_modules({name: label for name, label in DESCRIPTION_MODULES[bench].items()
                             if name not in EXCLUDED_MODULES.get(bench, [])})
    nodes = sorted(n for (n, o) in runs if o==test_omp and (n, ref_omp) in runs)
    names = list(modules)+['total']

    ratios = np.full((len(names), len(nodes)), np.nan)
    for inode, n in enumerate(nodes):
        ref = module_times(runs[(n, ref_omp)], modules)
        ref['total'] = runs[(n, ref_omp)]['total']
        test = module_times(runs[(n, test_omp)], modules)
        test['total'] = runs[(n, test_omp)]['total']
        for iname, name in enumerate(names):
            if ref[name]>0 and test[name]>0:
                ratios[iname, inode] = ref[name]/test[name]

    labels = [modules[name] for name in modules]+['total time']
    return nodes, labels, ratios


''' One row of heatmaps per comparison and one column per benchmark '''
def plot_numa_effect(comparisons, outname='omp_numa_effect.png'):

    cmap, norm, bounds, bound_labels = discrete_speedup_scale()
    data = {(icomp, bench): comparison_ratios(cluster, bench, reso, test[1], ref[1])
            for icomp, (cluster, test, ref, title) in enumerate(comparisons)
            for bench, reso in BENCHMARKS}

    # panel sizes proportional to their numbers of cells, so that all cells are square
    widths = [max(len(data[(icomp, bench)][0]) for icomp in range(len(comparisons)))
              for bench, reso in BENCHMARKS]
    heights = [max(len(data[(icomp, bench)][1]) for bench, reso in BENCHMARKS)
               for icomp in range(len(comparisons))]
    cell = 0.24
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(cell*sum(widths)+4.5, cell*sum(heights)+1.6*len(comparisons)+0.8))
        grid = fig.add_gridspec(len(comparisons), len(BENCHMARKS), width_ratios=widths,
                                height_ratios=heights, wspace=0.75, hspace=0.45)

        rows_axes = []
        for icomp, (cluster, test, ref, title) in enumerate(comparisons):
            row_axes = []
            rows_axes.append(row_axes)
            for ibench, (bench, reso) in enumerate(BENCHMARKS):
                nodes, labels, ratios = data[(icomp, bench)]
                ax = fig.add_subplot(grid[icomp, ibench])
                row_axes.append(ax)
                image = ax.imshow(ratios, cmap=cmap, norm=norm, aspect='equal', zorder=1)
                ax.add_patch(mpatches.Rectangle((-0.5, -0.5), len(nodes), len(labels), zorder=0,
                                                facecolor='white', edgecolor='#b0b0b0', hatch='////',
                                                linewidth=0))
                # line between the modules and the total time
                ax.axhline(len(labels)-1.5, color='black', linewidth=0.8, zorder=2)
                ax.set_xticks(range(len(nodes)), labels=[str(n) for n in nodes], fontsize=6.5)
                ax.set_yticks(range(len(labels)), labels=labels, fontsize=7)
                ax.get_yticklabels()[-1].set_fontweight('bold')
                ax.set_xlabel('number of nodes', fontsize=8)
                ax.set_title(BENCHMARK_LABELS[bench], fontsize=9)
                ax.grid(False)
                ax.tick_params(length=0)
                # panels of different heights aligned at their x-axis
                ax.set_anchor('S')
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('black')
                    spine.set_linewidth(0.8)
                    spine.set_zorder(2)
        cbar = fig.colorbar(image, ax=fig.axes, orientation='horizontal', spacing='uniform',
                            shrink=0.6, aspect=40, pad=0.12)
        cbar.set_ticks(bounds, labels=bound_labels)
        cbar.ax.minorticks_off()
        cbar.set_label('slower ($t_\\mathrm{test}/t_\\mathrm{reference}$)   |   '
                       'faster ($t_\\mathrm{reference}/t_\\mathrm{test}$)')

        # title of every comparison above its row of panels, once the colorbar has
        # taken its space and the panels have their final position
        fig.canvas.draw()
        for (cluster, test, ref, title), row_axes in zip(comparisons, rows_axes):
            top = max(ax.get_position().y1 for ax in row_axes)
            fig.text(0.5, top+0.3/fig.get_figheight(), title, ha='center', va='bottom',
                     fontsize=10, fontweight='bold')
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Effect of MPI processes spanning several NUMA domains on the modules')
    parser.add_argument('-c', '--clusters', nargs='+', default=list(FIGURES),
                        help='Figures to make: ' + ', '.join(FIGURES))
    args = parser.parse_args()

    for name in args.clusters:
        plot_numa_effect(FIGURES[name], outname=f'omp_numa_effect_{name}.png')
