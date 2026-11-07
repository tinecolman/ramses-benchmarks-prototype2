'''
Speedup of the hybrid MPI-OpenMP configurations with respect to MPI-only, for
every module of the code, as a function of the number of nodes and of the
configuration. One heatmap per module, plus 'other' (and optionally the total
time), to show how each module on its own responds to OpenMP. Small modules
can be left out per benchmark in EXCLUDED_PANELS.

The speedup t_MPI / t_hybrid is shown with a discrete color scale: teal bins
for a gain and orange bins for a loss, symmetric on a logarithmic scale, with
a neutral bin within RATIO_BOUNDS[0] of MPI-only. Missing runs are hatched. A
timer that is missing in the hybrid run (too small to be written in the log)
counts as an infinite speedup, shown in the darkest teal.
Optionally the value is written in the cells: a gain as the speedup (×2.3) and
a loss as the slowdown t_hybrid/t_MPI (÷1.4), so that both are larger than one.

The modules are those of DESCRIPTION_MODULES in mpi_module_share.py.

Run from the visu directory:
    python omp_module_gain_heatmap.py -c marenostrum -b cosmo -r 1024
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from openmp_timer_breakdown import load_timer_breakdown
from openmp_module_analysis import STYLE, index_runs, module_times
from openmp_best_speedup import get_openmp_dirs
from mpi_module_share import DESCRIPTION_MODULES, order_modules

# Edges of the bins of the color scale, for a gain (t_MPI/t_hybrid) and the same
# for a loss (t_hybrid/t_MPI). Within the first edge, the cell is neutral (white).
# The neutral bin is narrow, so that small but important losses (e.g. the Godunov
# solver in Sedov, 7-12% slower) remain visible. Five shades on each side.
RATIO_BOUNDS = [1.05, 1.2, 1.5, 2., 3.]
# speed ratio used for a timer that is missing (too small to be written) in one run
INFINITE_RATIO = 1e6
# orange for a loss and teal for a gain, distinguishable with red-green colour
# blindness. One color per bin, from the largest loss to the largest gain
CMAP = mcolors.LinearSegmentedColormap.from_list('OrTl', [
    '#7f3b08', '#b35806', '#e08214', '#fdb863', '#fee0b6', '#f7f7f7',
    '#c7eae5', '#80cdc1', '#35978f', '#01665e', '#003c30'])

# Panels left out per benchmark: modules taking a small part of the time, and
# 'other' when it brings no additional insight
EXCLUDED_PANELS = {
    'sedov': ['other'],
    'cosmo': ['coarse levels', 'other'],
    'galaxy': ['other'],
}

# Numbers of OpenMP threads left out per cluster. On LUMI and MeluXina, only 4x32
# is kept of the configurations spanning several NUMA domains, to illustrate the problem.
EXCLUDED_THREADS = {
    'lumi': [64, 128],
    'meluxina': [64, 128],
}


''' Speed ratio t_MPI/t_hybrid of every module, of 'other' and of the total, as
    {name: 2D array [configuration, number of nodes]}, NaN where a run is missing
    and INFINITE_RATIO (or its inverse) where a timer is missing in one of the runs.
    Also returns the numbers of nodes and the configurations (mpi, omp), the
    configurations ordered by increasing number of threads. The runs with a single
    OpenMP thread, which only show the overhead of the OpenMP build, are left out
    unless single_thread is set. '''
def module_speed_ratios(entries, modules, excluded_threads=(), single_thread=False):
    runs = {key: entry for key, entry in index_runs(entries).items() if key[1] not in excluded_threads}
    arr_nodes = sorted({n for (n, o) in runs if o==0})
    min_threads = 1 if single_thread else 2
    configs = sorted({(entry['mpi_procs_per_node'], o) for (n, o), entry in runs.items() if o>=min_threads},
                     key=lambda config: config[1])

    names = list(modules)+['other', 'total']
    ratios = {name: np.full((len(configs), len(arr_nodes)), np.nan) for name in names}
    for inode, nodes in enumerate(arr_nodes):
        ref = module_times(runs[(nodes, 0)], modules)
        ref['total'] = runs[(nodes, 0)]['total']
        for iconf, (mpi, omp) in enumerate(configs):
            if (nodes, omp) not in runs:
                continue
            times = module_times(runs[(nodes, omp)], modules)
            times['total'] = runs[(nodes, omp)]['total']
            for name in names:
                if ref[name]>0 and times[name]>0:
                    ratios[name][iconf, inode] = ref[name]/times[name]
                # a timer too small to be written in the log of one of the two runs:
                # infinite speedup (or slowdown), shown in the darkest color. A finite
                # value is used, since infinite values are masked like missing runs.
                elif ref[name]>0:
                    ratios[name][iconf, inode] = INFINITE_RATIO
                elif times[name]>0:
                    ratios[name][iconf, inode] = 1./INFINITE_RATIO
                else:
                    ratios[name][iconf, inode] = 1.

    return arr_nodes, configs, ratios


# Continuous color scale of the speedup (continuous_speedup_scale): white within
# NEUTRAL_RATIO of MPI-only, saturated beyond GAIN_LIMIT for a gain and beyond
# LOSS_LIMIT (t_hybrid/t_MPI) for a loss, so that both sides use their full range of
# colors. The color follows |ln S| - ln NEUTRAL_RATIO to the power SCALE_GAMMA, which
# stretches the range near one, so that losses of 10% are still visible.
NEUTRAL_RATIO = 1.02
GAIN_LIMIT = 10.
LOSS_LIMIT = 10.
SCALE_GAMMA = 0.5
# labelled factors of the colorbar, for a gain and the same for a loss
SCALE_TICKS = [1.2, 2., 5., 10., 20., 30., 100.]


''' Continuous color scale of the speedup: the colormap, its norm, and the ticks and
    labels of the colorbar. Missing values are transparent, to show the hatching
    underneath. '''
def continuous_speedup_scale(gain_limit=None, loss_limit=None, ticks=None):
    gain_limit = GAIN_LIMIT if gain_limit is None else gain_limit
    loss_limit = LOSS_LIMIT if loss_limit is None else loss_limit
    ticks = SCALE_TICKS if ticks is None else ticks
    cmap = plt.get_cmap(CMAP).copy()
    cmap.set_bad((0., 0., 0., 0.))
    neutral = np.log(NEUTRAL_RATIO)
    # distance from white of a factor, and of the limits on both sides
    stretch = lambda log_factor: np.maximum(log_factor-neutral, 0.)**SCALE_GAMMA
    gain_end, loss_end = stretch(np.log(gain_limit)), stretch(np.log(loss_limit))
    def forward(ratio):
        # keep the missing runs masked, so that they stay transparent
        mask = np.ma.getmaskarray(ratio)
        with np.errstate(divide='ignore', invalid='ignore'):
            log = np.log(np.ma.getdata(ratio))
            value = np.where(log>=0., stretch(log)/gain_end, -stretch(-log)/loss_end)
        return np.ma.masked_array(value, mask=mask|~np.isfinite(value))
    def inverse(value):
        value = np.asarray(value, dtype=float)
        log_gain = (np.abs(value)*gain_end)**(1./SCALE_GAMMA)+neutral
        log_loss = (np.abs(value)*loss_end)**(1./SCALE_GAMMA)+neutral
        return np.where(value>=0., np.exp(log_gain), np.exp(-log_loss))
    norm = mcolors.FuncNorm((forward, inverse), vmin=1./loss_limit, vmax=gain_limit)
    gains = [tick for tick in ticks if tick<=gain_limit]
    losses = [tick for tick in ticks if tick<=loss_limit]
    bounds = [1./tick for tick in losses[::-1]]+[1.]+gains
    labels = [f'÷{tick:g}' for tick in losses[::-1]]+['1']+[f'×{tick:g}' for tick in gains]
    return cmap, norm, bounds, labels


''' Discrete color scale of the speedup: the colormap, its norm and the labels of
    the bin edges. Missing values are transparent, to show the hatching underneath. '''
def discrete_speedup_scale():
    bounds = [1./bound for bound in RATIO_BOUNDS[::-1]]+RATIO_BOUNDS
    # one color per bin, plus the bins beyond the last edges, with white in the middle
    ncolors = len(bounds)+1
    cmap = mcolors.ListedColormap(plt.get_cmap(CMAP)(np.linspace(0., 1., ncolors)))
    cmap.set_bad((0., 0., 0., 0.))
    norm = mcolors.BoundaryNorm(bounds, ncolors=ncolors, extend='both')
    labels = [f'÷{bound:g}' for bound in RATIO_BOUNDS[::-1]]+[f'×{bound:g}' for bound in RATIO_BOUNDS]
    return cmap, norm, bounds, labels


''' One heatmap per module of the speedup of the hybrid configurations with
    respect to MPI-only. The total time is only shown with include_total, and
    the values are only written in the cells with show_values. '''
def plot_module_gain_heatmap(entries, modules, title='', excluded=(), excluded_threads=(),
                             include_total=False, show_values=False, outname='omp_module_ratio.png'):

    arr_nodes, configs, ratios = module_speed_ratios(entries, modules, excluded_threads)
    if len(configs)==0:
        print('[Module gain heatmap] No hybrid runs found')
        return 1
    labels = dict(modules)
    labels.update({'other': 'other', 'total': 'total time'})
    names = [name for name in ratios if (include_total or name!='total') and name not in excluded]
    cmap, norm, bounds, bound_labels = discrete_speedup_scale()

    # grid as square as possible
    ncols = int(np.ceil(np.sqrt(len(names))))
    nrows = int(np.ceil(len(names)/ncols))
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, squeeze=False,
                                 figsize=(0.32*len(arr_nodes)*ncols+1.5,
                                          max(0.28*len(configs), 1.8)*nrows+1.),
                                 sharex=True, sharey=True)
        for ax in axes.flatten()[len(names):]:
            ax.set_visible(False)

        for ax, name in zip(axes.flatten(), names):
            # configurations with more threads higher up
            image = ax.imshow(ratios[name], cmap=cmap, norm=norm, aspect='auto', origin='lower',
                              zorder=1)
            ax.add_patch(mpatches.Rectangle((-0.5, -0.5), len(arr_nodes), len(configs), zorder=0,
                                            facecolor='white', edgecolor='#b0b0b0', hatch='////',
                                            linewidth=0))
            if show_values:
                write_values(ax, ratios[name], norm)
            ax.set_title(labels[name], fontsize=9, fontweight='bold' if name=='total' else 'normal')
            ax.set_xticks(range(len(arr_nodes)), labels=[str(n) for n in arr_nodes], fontsize=7)
            ax.set_yticks(range(len(configs)), labels=[f'{mpi}×{omp}' for mpi, omp in configs], fontsize=7)
            ax.grid(False)
            ax.tick_params(length=0)
            # black frame around every heatmap
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('black')
                spine.set_linewidth(0.8)
                spine.set_zorder(2)
        # label the x-axis of the lowest panel in every column
        for icol in range(ncols):
            visible = [ax for ax in axes[:, icol] if ax.get_visible()]
            visible[-1].set_xlabel('number of nodes')
            visible[-1].xaxis.set_tick_params(labelbottom=True)
        for ax in axes[:, 0]:
            ax.set_ylabel('MPI × OMP per node')

        # bins of equal size in the colorbar, labelled at their edges
        cbar = fig.colorbar(image, ax=axes, shrink=0.8, pad=0.02, spacing='uniform')
        cbar.set_ticks(bounds, labels=bound_labels)
        cbar.ax.minorticks_off()
        cbar.set_label('slower ($t_\\mathrm{hybrid}/t_\\mathrm{MPI}$)   |   '
                       'faster ($t_\\mathrm{MPI}/t_\\mathrm{hybrid}$)')
        if title!='':
            fig.suptitle(title, fontsize=10)
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.close()

    print(outname)
    return 0


''' Write the speedup in the cells, as ×2.3 for a gain and ÷1.4 for a loss, and
    nothing in the neutral cells. White text on the dark colors. '''
def write_values(ax, ratios, norm):
    for iconf in range(ratios.shape[0]):
        for inode in range(ratios.shape[1]):
            ratio = ratios[iconf, inode]
            if np.isnan(ratio) or max(ratio, 1./ratio)<RATIO_BOUNDS[0]:
                continue
            if max(ratio, 1./ratio)>=INFINITE_RATIO:
                text = '×∞' if ratio>1. else '÷∞'
            else:
                text = f'×{ratio:.1f}' if ratio>=1. else f'÷{1./ratio:.1f}'
            dark = max(ratio, 1./ratio)>=RATIO_BOUNDS[-2]
            ax.text(inode, iconf, text, ha='center', va='center', fontsize=6.5,
                    color='white' if dark else 'black')


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Speedup of the hybrid MPI-OpenMP configurations with respect to MPI-only, per module')

    parser.add_argument('-c', '--cluster', default='marenostrum', help='Cluster name')
    parser.add_argument('-b', '--benchmark', default='cosmo', help='Benchmark setup name')
    parser.add_argument('-r', '--reso', default='1024', help='Resolution')
    parser.add_argument('--total', action='store_true', help='Also show the total time')
    parser.add_argument('--values', action='store_true', help='Write the speedup in the cells')

    args = parser.parse_args()

    from tagged_data import EXCLUDED_COMPILERS
    entries = load_timer_breakdown(get_openmp_dirs(args.cluster, args.benchmark), args.benchmark,
                                   args.reso, exclude_compilers=EXCLUDED_COMPILERS)
    modules = order_modules(DESCRIPTION_MODULES[args.benchmark])
    plot_module_gain_heatmap(entries, modules, excluded=EXCLUDED_PANELS.get(args.benchmark, ()),
                             excluded_threads=EXCLUDED_THREADS.get(args.cluster, ()),
                             include_total=args.total, show_values=args.values,
                             title=f'{args.benchmark} {args.reso} on {args.cluster}',
                             outname=f'omp_module_ratio_{args.benchmark}_{args.reso}_{args.cluster}.png')
