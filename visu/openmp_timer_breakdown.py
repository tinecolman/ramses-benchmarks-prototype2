import os
import re
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.lines as mlines
from collections import defaultdict
from io_timings import get_info_from_subdir_name, parse_metadata, skip_compiler, set_node_ticks
from openmp_nthreads_execution_time import get_cores_per_node

# Timers that are shown together, as {timer: group name}
TIMER_GROUPS = {
    # 
    'hydro - rev ghostzones': 'hydro - communication',
    'hydro - ghostzones': 'hydro - communication',
    #
    'hydro - set uold': 'hydro - state copy',
    'hydro - set unew': 'hydro - state copy',
    # update of the particle positions and velocities
    'particles - move': 'particles - update',
    'particles - synchro': 'particles - update',
    # creation and destruction of the particle linked lists
    'particles - make tree': 'particles - book keeping',
    'particles - merge tree': 'particles - book keeping',
    'particles - kill tree': 'particles - book keeping',
}


''' Read the timer block printed at the end of a RAMSES log file.
    Returns a dictionary {timer name: time averaged over the MPI ranks}
    and the total time, or an empty dictionary if the run did not finish '''
def read_timer_block(logfile):
    timers = {}
    total = None
    in_block = False
    with open(logfile, 'r') as f:
        for line in f:
            tokens = line.split()
            if len(tokens)==0:
                continue
            if tokens[-1]=='TIMER':
                # start of the block, only keep the last one printed
                in_block = True
                timers = {}
                continue
            if not in_block:
                continue
            if tokens[-1]=='TOTAL':
                total = float(tokens[0])
                in_block = False
                continue
            # columns: minimum average maximum std std/av % rmn rmx name
            # the rank columns rmn and rmx merge (or show ****) for large rank
            # numbers, so they are stripped from the name instead of split
            match = re.match(r'\s*(\S+\s+){6}', line)
            if match is None:
                continue
            name = line[match.end():].lstrip('0123456789* ').strip()
            try:
                timers[name] = float(tokens[1])
            except ValueError:
                continue
    if total is None:
        return {}, None
    return group_timers(timers), total


''' Sum the timers that belong to the same group, see TIMER_GROUPS '''
def group_timers(timers):
    grouped = defaultdict(float)
    for name, value in timers.items():
        grouped[TIMER_GROUPS.get(name, name)] += value
    return dict(grouped)


''' Load the timer breakdown of all runs at the given resolution.
    Repeated runs of the same configuration are averaged. Each entry has the
    same keys as the ones produced by add_data, but 'timers' holds the
    breakdown and 'total' the total time '''
def load_timer_breakdown(benchmark_dirs, test_name, reso, exclude_compilers=None):

    gathered = defaultdict(lambda: {'timers': defaultdict(list), 'total': []})

    for benchmark_dir in benchmark_dirs:
        data_dir = os.path.join(benchmark_dir, test_name)
        if not os.path.isdir(data_dir):
            continue
        for item in os.listdir(data_dir):
            run_dir = os.path.join(data_dir, item)
            if not (os.path.isdir(run_dir) and item.startswith('reso')):
                continue
            run_reso, nodes, mpi, omp = get_info_from_subdir_name(item)
            if run_reso!=reso:
                continue
            for logname in os.listdir(run_dir):
                if not logname.endswith('.log'):
                    continue
                logfile = os.path.join(run_dir, logname)
                if skip_compiler(parse_metadata(logfile), exclude_compilers):
                    continue
                timers, total = read_timer_block(logfile)
                if total is None:
                    continue
                config = gathered[(int(nodes), int(mpi), int(omp))]
                for name, value in timers.items():
                    config['timers'][name].append(value)
                config['total'].append(total)

    entries = []
    for (nodes, mpi, omp), config in gathered.items():
        entries.append({
            'nodes': nodes,
            'resolution': reso,
            'mpi_procs_per_node': mpi,
            'omp_threads': omp,
            'timers': {name: np.mean(values) for name, values in config['timers'].items()},
            'total': np.mean(config['total'])
        })
    return entries


''' Keep only the runs that use the full node '''
def select_full_node(entries):
    if len(entries)==0:
        return []
    cores_per_node = max(get_cores_per_node(entry) for entry in entries)
    return [entry for entry in entries if get_cores_per_node(entry)==cores_per_node]


''' Select the timers that take at least a fraction 'threshold' of the total time
    in at least one of the runs, ordered from most to least expensive.
    The remaining timers are gathered under 'other' '''
def select_main_timers(entries, threshold=0.05):
    importance = defaultdict(float)
    for entry in entries:
        for name, value in entry['timers'].items():
            importance[name] = max(importance[name], value/entry['total'])
    names = [name for name in sorted(importance, key=importance.get, reverse=True)
             if importance[name]>=threshold]
    if len(names)<len(importance):
        names.append('other')
    return names


''' Time per selected timer for one run, the small timers summed into 'other' '''
def fold_timers(entry, timer_names):
    folded = {name: entry['timers'].get(name, 0.) for name in timer_names if name!='other'}
    if 'other' in timer_names:
        folded['other'] = sum(value for name, value in entry['timers'].items() if name not in folded)
    return folded


''' Color of each timer, consistent between figures '''
def get_timer_colors(timer_names):
    cmap = plt.get_cmap('tab10')
    colors = {name: cmap(i % 10) for i, name in enumerate(timer_names)}
    if 'other' in colors:
        colors['other'] = 'lightgrey'
    return colors


''' Label of an MPI-OpenMP configuration '''
def config_label(entry):
    if entry['omp_threads']==0:
        return 'MPI-only'
    if entry['mpi_procs_per_node']==0:
        return f'OMP-only ({entry["omp_threads"]})'
    return f'{entry["mpi_procs_per_node"]}×{entry["omp_threads"]}'


''' Stacked bars of the time spent in each part of the code, for the different
    MPI-OpenMP configurations filling the node, at a fixed number of nodes.
    The gain with respect to the MPI-only run is written on top of the bars. '''
def plot_timer_breakdown_configs(entries, nodes, timer_names, title='',
                                 outname='timer_breakdown.png'):

    entries = [entry for entry in select_full_node(entries) if entry['nodes']==nodes]
    if len(entries)<2:
        print('[Timer breakdown] Not enough configurations at', nodes, 'nodes')
        return 1

    # from MPI-only to many threads, OpenMP-only last
    entries = sorted(entries, key=lambda e: (e['mpi_procs_per_node']==0, e['omp_threads']))
    colors = get_timer_colors(timer_names)
    reference = [entry['total'] for entry in entries if entry['omp_threads']==0]

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(0.6*len(entries)+2.5, 4))

    xpos = np.arange(len(entries))
    bottom = np.zeros(len(entries))
    for name in timer_names:
        values = np.array([fold_timers(entry, timer_names)[name] for entry in entries])
        axes.bar(xpos, values, bottom=bottom, color=colors[name], label=name, width=0.7)
        bottom += values

    # gain with respect to MPI-only on top of each bar
    if len(reference)>0:
        for x, entry, height in zip(xpos, entries, bottom):
            if entry['omp_threads']==0:
                continue
            gain = 100.*(reference[0]-entry['total'])/reference[0]
            axes.text(x, height*1.01, f'{gain:+.0f}%', ha='center', va='bottom', fontsize=7)

    axes.set_xticks(xpos, labels=[config_label(entry) for entry in entries], rotation=45, ha='right')
    axes.set_xlabel('MPI processes × OMP threads per node')
    axes.set_ylabel('time [s]')
    axes.set_ylim(0, max(bottom)*1.1)
    axes.set_title(f'{title}, {nodes} node{"s" if nodes>1 else ""}')
    # most expensive timer on top of the legend, as in the bars
    handles, labels = axes.get_legend_handles_labels()
    axes.legend(handles[::-1], labels[::-1], loc='center left', bbox_to_anchor=(1., 0.5), fontsize=8)
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

    return 0


''' Time spent in each part of the code as a function of the number of nodes,
    for MPI-only (dashed) and the fastest MPI-OpenMP configuration (solid).
    This shows how the different modules scale and benefit from OpenMP. '''
def plot_timer_scaling(entries, timer_names, title='', outname='timer_scaling.png'):

    entries = select_full_node(entries)
    colors = get_timer_colors(timer_names)

    # MPI-only run and fastest hybrid run for every number of nodes
    variants = {'MPI-only': {}, 'best OpenMP': {}}
    for entry in entries:
        nodes = entry['nodes']
        if entry['omp_threads']==0:
            variants['MPI-only'][nodes] = entry
        else:
            best = variants['best OpenMP'].get(nodes)
            if best is None or entry['total']<best['total']:
                variants['best OpenMP'][nodes] = entry

    if len(variants['MPI-only'])<2 and len(variants['best OpenMP'])<2:
        print('[Timer scaling] Not enough numbers of nodes to show scaling')
        return 1

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6,4.5))

    all_nodes = set()
    for variant, style in zip(variants, ['--', '-']):
        arr_nodes = sorted(variants[variant])
        all_nodes.update(arr_nodes)
        for name in timer_names:
            values = [fold_timers(variants[variant][n], timer_names)[name] for n in arr_nodes]
            axes.plot(arr_nodes, values, ls=style, marker='o', markersize=3,
                      color=colors[name])

    axes.set_xscale('log')
    axes.set_yscale('log')
    set_node_ticks(axes, all_nodes)
    axes.set_xlabel('number of nodes')
    axes.set_ylabel('time [s]')
    axes.set_title(title)

    timer_handles = [mlines.Line2D([], [], color=colors[name], lw=2, label=name)
                     for name in timer_names]
    style_handles = [mlines.Line2D([], [], color='k', ls='--', label='MPI-only'),
                     mlines.Line2D([], [], color='k', ls='-', label='best OpenMP')]
    legend1 = axes.legend(handles=timer_handles, loc='upper left',
                          bbox_to_anchor=(1., 1.), fontsize=8, title='timer')
    axes.add_artist(legend1)
    legend2 = axes.legend(handles=style_handles, loc='lower left', bbox_to_anchor=(1., 0.), fontsize=8)
    # legends outside of the axes are not taken into account by default to fit the figure
    plt.savefig(outname, bbox_inches='tight', bbox_extra_artists=[legend1, legend2], dpi=200)
    plt.close()

    return 0


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Breakdown of the execution time in the different parts of the code, for different MPI-OpenMP configurations')

    parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
    parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
    parser.add_argument('-r', '--reso', required=True, help='Resolution')
    parser.add_argument('-n', '--nodes', type=int, default=1, help='Number of nodes for the bar chart')

    args = parser.parse_args()

    from tagged_data import get_latest_openmp_dirs, EXCLUDED_COMPILERS
    entries = load_timer_breakdown(get_latest_openmp_dirs(args.cluster), args.benchmark,
                                   args.reso, exclude_compilers=EXCLUDED_COMPILERS)
    timer_names = select_main_timers(select_full_node(entries))
    title = f'{args.benchmark} {args.reso} on {args.cluster}'

    plot_timer_breakdown_configs(entries, args.nodes, timer_names, title=title,
        outname=f'timer_breakdown_{args.benchmark}_{args.reso}_{args.nodes}nodes_{args.cluster}.png')
    plot_timer_scaling(entries, timer_names, title=title,
        outname=f'timer_scaling_{args.benchmark}_{args.reso}_{args.cluster}.png')
