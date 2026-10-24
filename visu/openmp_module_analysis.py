'''
Behaviour of the main modules of the code for the different MPI-OpenMP
configurations, to explain where the gain (or loss) of the hybrid runs
with respect to MPI-only comes from.

Three figures are produced, all for the runs that use the full node:
  * module_ratio:  time of every module relative to MPI-only, as a function
                   of the MPI-OpenMP configuration, for a few numbers of nodes
  * gain_decomposition: contribution of every module to the gain with respect
                   to MPI-only, as a function of the number of nodes, for the
                   chosen configuration(s)
  * module_share:  fraction of the total time spent in every module as a function
                   of the number of nodes, for MPI-only (solid) and a hybrid
                   configuration (dashed)

The modules shown depend on the benchmark, see MODULES_PER_BENCHMARK.
The timers are averaged over the MPI processes, as in openmp_timer_breakdown.py.
Remark that the first communication after a load imbalanced module (e.g. the
reverse ghost zones after godunov) also contains the time waiting for the slowest
process.

Run from the visu directory:
    python openmp_module_analysis.py -c marenostrum -b sedov -r 1024
    python openmp_module_analysis.py -c marenostrum -b sedov -r 1024 -m "7 2" -n "1 16 128"
'''

import numpy as np
from matplotlib import pyplot as plt
from openmp_timer_breakdown import load_timer_breakdown, select_full_node, config_label
from io_timings import set_node_ticks

# Modules shown separately, as {timer (group) name: label}.
# Timer groups are defined in TIMER_GROUPS of openmp_timer_breakdown.py.
# A key can also be a tuple of timer (group) names, which are then summed.
# All other timers are summed under 'other'.
MODULES = {
    'hydro - godunov': 'godunov',
    'hydro - communication': 'communication',
    'hydro - state copy': 'state copy',
    'courant': 'courant',
}

# Modules per benchmark setup, MODULES is used for the setups not listed here
MODULES_PER_BENCHMARK = {
    'sedov': MODULES,
    'cosmo': {
        'poisson - phi multigrid': 'multigrid',
        'poisson - rho': 'rho (CIC)',
        'particles - update': 'particles - update',
        'particles - book keeping': 'particles - book keeping',
    },
    'galaxy': {
        'poisson - phi multigrid': 'multigrid',
        ('refine', 'flag'): 'AMR (refine, flag)',
        'load balance': 'load balance',
        'hydro - godunov': 'godunov',
        'hydro - communication': 'hydro - communication',
        'poisson - rho': 'rho (CIC)',
        'particles - book keeping': 'particles - book keeping',
        'coarse levels': 'coarse levels',
    },
}

# Color of every module, the same in all benchmarks. One hue per part of the code
# (blue: hydro, green: gravity, orange: particles, yellow: AMR), dark for the main
# module of that part and light for the secondary one. The order is also the
# order in which the modules are stacked in mpi_module_share.py.
MODULE_COLORS = {
    'hydro - godunov': '#1f4e9c',
    'hydro - communication': '#6fa8dc',
    'hydro - state copy': '#0b8a8a',
    'poisson - phi multigrid': '#2e7d32',
    'poisson - rho': '#8bc34a',
    'particles - update': '#e65100',
    'particles - book keeping': '#f5a35c',
    'refine': '#b8860b',
    'coarse levels': '#e6c35c',
    'flag': '#c49c94',
    ('refine', 'flag'): '#b8860b',
    'load balance': '#8c564b',
    'courant': '#e87ba4',
}
# Colors of the modules not listed in MODULE_COLORS, and of 'other'
EXTRA_COLORS = ['#e87ba4', '#e34948', '#6250d6', '#008300']
OTHER_COLOR = '#a3a3a3'
# Colors of the lines for different numbers of nodes (max 3)
NODE_COLORS = ['#2a78d6', '#eb6834', '#1baf7a']

STYLE = {'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
         'axes.edgecolor': '#888888', 'axes.grid': True,
         'grid.color': '#e6e6e6', 'grid.linewidth': 0.6}


''' Timer (group) names that make up a module '''
def module_timer_names(module):
    return module if isinstance(module, tuple) else (module,)


''' Time spent in one module for one run '''
def module_time(entry, module):
    return sum(entry['timers'].get(name, 0.) for name in module_timer_names(module))


''' Time per module for one run, the remaining timers summed into 'other' '''
def module_times(entry, modules=MODULES):
    times = {module: module_time(entry, module) for module in modules}
    used = {name for module in modules for name in module_timer_names(module)}
    times['other'] = sum(value for name, value in entry['timers'].items() if name not in used)
    return times


''' Index the full-node runs as {(nodes, omp_threads): entry} '''
def index_runs(entries):
    return {(entry['nodes'], entry['omp_threads']): entry for entry in select_full_node(entries)}


''' Labels and colors of the modules, 'other' last '''
def module_labels_colors(modules=MODULES):
    labels = dict(modules)
    labels['other'] = 'other'
    unknown = [name for name in modules if name not in MODULE_COLORS]
    if len(unknown)>len(EXTRA_COLORS):
        print('[Modules] Too many modules without a color in MODULE_COLORS, colors are reused')
    colors = {name: MODULE_COLORS[name] for name in modules if name in MODULE_COLORS}
    colors.update({name: EXTRA_COLORS[i % len(EXTRA_COLORS)] for i, name in enumerate(unknown)})
    colors['other'] = OTHER_COLOR
    return labels, colors


''' Number of OMP threads of the fastest hybrid configuration on most numbers of nodes '''
def most_frequent_best_config(runs):
    best = {}
    for (nodes, omp), entry in runs.items():
        if omp==0:
            continue
        if nodes not in best or entry['total']<runs[(nodes, best[nodes])]['total']:
            best[nodes] = omp
    values, counts = np.unique(list(best.values()), return_counts=True)
    return int(values[np.argmax(counts)])


''' Time of every module relative to MPI-only on the same number of nodes, as a
    function of the MPI-OpenMP configuration. One panel per module, one line per
    number of nodes. The configurations in 'highlight' (OMP threads) get bold labels. '''
def plot_module_ratio(entries, nodes_list, title='', highlight=(), modules=MODULES,
                      outname='module_ratio.png'):

    runs = index_runs(entries)
    nodes_list = [nodes for nodes in nodes_list if (nodes, 0) in runs]
    if len(nodes_list)==0:
        print('[Module ratio] No MPI-only reference for the requested numbers of nodes')
        return 1
    # configurations available on any of the requested numbers of nodes, MPI-only first.
    # Missing runs leave a gap in the lines.
    omps = sorted({omp for (n, omp) in runs if n in nodes_list})
    xlabels = [config_label(next(runs[(n, omp)] for n in nodes_list if (n, omp) in runs)) for omp in omps]
    labels, _ = module_labels_colors(modules)
    # colors follow the number of nodes, max 3 lines for colorblind safety
    line_colors = NODE_COLORS
    if len(nodes_list)>3:
        print('[Module ratio] Only the first 3 numbers of nodes are shown')
        nodes_list = nodes_list[:3]

    with plt.rc_context(STYLE):
        # at most 4 panels per row
        ncols = min(4, len(modules))
        nrows = int(np.ceil(len(modules)/ncols))
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(3.25*ncols, 3.3*nrows+0.3), squeeze=False)
        axes = axes.flatten()
        for ax in axes[len(modules):]:
            ax.set_visible(False)
        for ax, name in zip(axes, modules):
            for color, nodes in zip(line_colors, nodes_list):
                ref = module_time(runs[(nodes, 0)], name)
                if ref<=0:
                    continue
                ratio = [module_time(runs[(nodes, omp)], name)/ref if (nodes, omp) in runs else np.nan
                         for omp in omps]
                ax.plot(range(len(omps)), ratio, '-o', color=color, lw=2, ms=5,
                        label=f'{nodes} node{"s" if nodes>1 else ""}')
            ax.axhline(1, color='#555555', lw=1, ls='--')
            ax.set_title(labels[name], loc='left', fontweight='bold')
            ax.set_xticks(range(len(omps)), labels=xlabels, rotation=45, ha='right', fontsize=7)
            for tick, omp in zip(ax.get_xticklabels(), omps):
                if omp in highlight:
                    tick.set_fontweight('bold')
        for ax in axes[::ncols]:
            ax.set_ylabel('time / MPI-only time')
        handles, labels_nodes = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels_nodes, frameon=False, loc='upper right', ncol=len(handles), fontsize=9)
        fig.suptitle(f'{title}: time per module relative to MPI-only (MPI processes × OMP threads per node)',
                     x=0.01, ha='left', fontsize=10)
        fig.tight_layout(rect=(0, 0, 1, 1-0.1/nrows))
        plt.savefig(outname, dpi=180)
        plt.close()

    return 0


''' Contribution of every module to the gain with respect to MPI-only, in percent
    of the MPI-only total time, as a function of the number of nodes. One panel per
    configuration in omp_list (number of OMP threads). Positive means the module is
    faster than in MPI-only. The markers give the net gain. '''
def plot_gain_decomposition(entries, omp_list, title='', modules=MODULES,
                            outname='gain_decomposition.png'):

    runs = index_runs(entries)
    labels, colors = module_labels_colors(modules)
    names = list(modules)+['other']

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(nrows=1, ncols=len(omp_list), figsize=(6*len(omp_list), 4), squeeze=False)
        for ax, omp in zip(axes[0], omp_list):
            arr_nodes = sorted(n for (n, o) in runs if o==omp and (n, 0) in runs)
            if len(arr_nodes)==0:
                print('[Gain decomposition] No runs with', omp, 'threads')
                continue
            xpos = np.arange(len(arr_nodes))
            pos_bottom = np.zeros(len(arr_nodes))
            neg_bottom = np.zeros(len(arr_nodes))
            for name in names:
                gain = np.array([100.*(module_times(runs[(n, 0)], modules)[name]
                                       - module_times(runs[(n, omp)], modules)[name])/runs[(n, 0)]['total']
                                 for n in arr_nodes])
                pos = np.where(gain>0, gain, 0.)
                neg = np.where(gain<0, gain, 0.)
                ax.bar(xpos, pos, bottom=pos_bottom, color=colors[name], width=0.65,
                       edgecolor='white', lw=1, label=labels[name])
                ax.bar(xpos, neg, bottom=neg_bottom, color=colors[name], width=0.65,
                       edgecolor='white', lw=1)
                pos_bottom += pos
                neg_bottom += neg
            net = [100.*(runs[(n, 0)]['total']-runs[(n, omp)]['total'])/runs[(n, 0)]['total'] for n in arr_nodes]
            ax.plot(xpos, net, 'D', color='black', ms=6, label='net gain', zorder=5)
            for x, value in zip(xpos, net):
                ax.text(x+0.2, value, f'{value:+.0f}%', fontsize=8, va='center')
            ax.set_ylim(min(neg_bottom.min(), min(net))-1.5, max(pos_bottom.max(), max(net))+2)
            ax.axhline(0, color='#333333', lw=1)
            ax.set_xticks(xpos, labels=arr_nodes)
            ax.set_xlabel('number of nodes')
            ax.set_title(config_label(runs[(arr_nodes[0], omp)]), loc='left', fontweight='bold')
        axes[0][0].set_ylabel('contribution to gain vs MPI-only\n[% of MPI-only total time]')
        # most expensive module on top of the legend, net gain first
        handles, leg_labels = axes[0][-1].get_legend_handles_labels()
        axes[0][-1].legend(handles[::-1], leg_labels[::-1], frameon=False, fontsize=8,
                           loc='center left', bbox_to_anchor=(1., 0.5))
        fig.suptitle(f'{title}: where the hybrid gain comes from (positive = module faster than in MPI-only)',
                     x=0.01, ha='left', fontsize=10)
        fig.tight_layout()
        plt.savefig(outname, dpi=180, bbox_inches='tight')
        plt.close()

    return 0


''' Fraction of the total time spent in every module as a function of the number of
    nodes, for MPI-only (solid) and the configuration with omp threads (dashed) '''
def plot_module_share(entries, omp, title='', modules=MODULES, outname='module_share.png'):

    runs = index_runs(entries)
    labels, colors = module_labels_colors(modules)
    names = list(modules)+['other']

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 3.8))
        all_nodes = set()
        for variant, style, lw in [(0, '-o', 2), (omp, '--', 1.2)]:
            arr_nodes = sorted(n for (n, o) in runs if o==variant)
            all_nodes.update(arr_nodes)
            for name in names:
                share = [100.*module_times(runs[(n, variant)], modules)[name]/runs[(n, variant)]['total']
                         for n in arr_nodes]
                ax.plot(arr_nodes, share, style, color=colors[name], lw=lw, ms=5,
                        label=labels[name] if variant==0 else None)
        ax.set_xscale('log')
        set_node_ticks(ax, all_nodes)
        ax.set_xlabel('number of nodes')
        ax.set_ylabel('% of total time')
        example = [entry for (n, o), entry in runs.items() if o==omp]
        hybrid = config_label(example[0]) if len(example)>0 else f'OMP={omp}'
        ax.set_title(f'{title}\nshare of total time: MPI-only (solid) vs {hybrid} (dashed)', loc='left', fontsize=10)
        ax.legend(frameon=False, fontsize=8, loc='center left', bbox_to_anchor=(1., 0.5))
        fig.tight_layout()
        plt.savefig(outname, dpi=180, bbox_inches='tight')
        plt.close()

    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Behaviour of the main modules of the code for the different MPI-OpenMP configurations')

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-m', '--omp', default=None,
                        help='OMP threads of the configurations for the gain decomposition, e.g. "7 2". '
                             'Default: the fastest configuration on most numbers of nodes')
    parser.add_argument('-n', '--nodes', default=None,
                        help='Numbers of nodes for the module ratio figure (max 3), e.g. "1 16 128". '
                             'Default: lowest, middle and highest')
    parser.add_argument('-p', '--path', default=None,
                        help='Benchmark directory, instead of the latest OpenMP version in tagged_data.py')

    args = parser.parse_args()

    from tagged_data import get_latest_openmp_dirs, EXCLUDED_COMPILERS
    benchmark_dirs = [args.path] if args.path is not None else get_latest_openmp_dirs(args.cluster)
    entries = load_timer_breakdown(benchmark_dirs, args.benchmark, args.reso,
                                   exclude_compilers=EXCLUDED_COMPILERS)
    runs = index_runs(entries)
    if len(runs)==0:
        print('No full-node runs found')
        exit(1)

    if args.omp is None:
        omp_list = [most_frequent_best_config(runs)]
    else:
        omp_list = [int(omp) for omp in args.omp.split()]

    if args.nodes is None:
        mpi_nodes = sorted(n for (n, o) in runs if o==0)
        nodes_list = sorted({mpi_nodes[0], mpi_nodes[len(mpi_nodes)//2], mpi_nodes[-1]})
    else:
        nodes_list = [int(n) for n in args.nodes.split()]

    modules = MODULES_PER_BENCHMARK.get(args.benchmark, MODULES)
    title = f'{args.benchmark} {args.reso} on {args.cluster}'
    suffix = f'{args.benchmark}_{args.reso}_{args.cluster}'

    plot_module_ratio(entries, nodes_list, title=title, highlight=omp_list, modules=modules,
                      outname=f'omp_module_ratio_{suffix}.png')
    plot_gain_decomposition(entries, omp_list, title=title, modules=modules,
                            outname=f'omp_gain_decomposition_{suffix}.png')
    plot_module_share(entries, omp_list[0], title=title, modules=modules,
                      outname=f'omp_module_share_{suffix}.png')
