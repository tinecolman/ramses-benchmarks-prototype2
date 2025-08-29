
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx

# ---- Recipe for reducing data ----

''' Get average time and error bars from the gathered total times printed in the log files '''
def process_times(times):
    if len(times)>0:
        time = np.average(times)
        error_min = time-np.min(times)
        error_max = np.max(times)-time
    else:
        time = np.nan
        error_min=0
        error_max=0
    return time, error_min, error_max

# ---- CPU optimisation ----

''' Make a figure of the execution time comparing different commits '''
def plot_execution_time_cpu_speedup(data, mapping_commits, reso, nodes, outname='check_refactor.png'):

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))

    times = []
    labels = []
    for entry in data:
        if entry['resolution']!=reso:
            continue
        if entry['nodes']!=nodes:
            continue
        commit = entry['commit']
        # reduce time data
        time, error_min, error_max = process_times(entry['timings'])
        times.append(float(time))
        labels.append(mapping_commits[commit])
        axes.scatter(np.full(len(entry['timings']),mapping_commits[commit]),entry['timings'],marker='o',s=3,color='black')

    axes.errorbar(labels, times, fmt='x',markersize=10, color='black')

    # write overall performance gain to screen
    diff = (times[-1]-times[0])/times[0]*100
    print(f'performance diff: {diff} %')

    axes.tick_params(axis='x', labelrotation=90)
    axes.set_ylabel('time [s]')
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

''' Make a figure of the execution time comparing different commits '''
def plot_execution_time_cpu_speedup_multicluster(clusters, data_arr, mapping_commits_arr,
                                                 reso, nodes, outname='check_refactor.png', timer=''):

    colors = [(0.8,0.4,0.0),(0.1,0.3,0.8), 'red', 'green', 'yellow']

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6,4))

    for cluster,color,data,mapping_commits in zip(clusters,colors,data_arr,mapping_commits_arr):
        times = []
        labels = []
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            commit = entry['commit']
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))
            labels.append(mapping_commits[commit])
            axes.scatter(np.full(len(entry['timings']),mapping_commits[commit]),entry['timings'],marker='o',s=3,color=color)

        axes.errorbar(labels, times, fmt='x',markersize=10, color=color)

        # write overall performance gain to screen
        diff = (times[-1]-times[0])/times[0]*100
        speedup=(times[0])/times[-1]
        print(f'performance diff: {diff} %, speed up: {speedup}')

        axes.scatter([],[],marker='o',s=5,color=color, label=cluster)

    axes.tick_params(axis='x', labelrotation=90)
    axes.set_ylabel(f'{timer} time [s]')
    axes.legend(loc='center left')
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close() 

''' Spit out a latex table comparing two commits '''
def make_table_cpu_speedup(data, reso, arr_nodes, first_column=True):

    for nodes in arr_nodes:
        times = []
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))

        diff = (-1)*(times[-1]-times[0])/times[0]*100

        if first_column:
            space_report_string = '{} & {:.3f} & {:.3f} & {:.1f} \\\\ \\hline'.format(str(nodes).rjust(2),times[0],times[-1],diff)
        else:
            space_report_string = '{:.3f} & {:.3f} & {:.1f} \\\\ \\hline'.format(times[0],times[-1],diff)
        print(space_report_string)


