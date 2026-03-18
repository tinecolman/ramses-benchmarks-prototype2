from io_timings import add_data
from visualisation import *

#def plot_time_vs_nodes(data, mapping_commits, reso, nodes, outname='compare.png'):
   

if __name__ == '__main__':
    
    test='sedov'
    cluster='meluxina'
    timer='total'
    reso="1024"

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data_ramses = []
    data_ramses = add_data(data_ramses, bench_home+'/'+cluster+'/'+'benchmark_dev_456b33e2',
                           test, which=timer)

    data_miniramses = []
    data_miniramses = add_data(data_miniramses, bench_home+'/'+cluster+'/'+'mini-benchmark_develop_3b48347b',
                               test, which=timer, version="mini-ramses")

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))

    # ramses
    arr_times = []
    arr_nodes = []
    labels = []
    for nodes in range(1,512):
        for entry in data_ramses:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            commit = entry['commit']
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            arr_times.append(float(time))
            arr_nodes.append(nodes)

    axes.plot(arr_nodes, arr_times, marker='o', markersize=4, label='ramses')
    axes.plot([arr_nodes[0],arr_nodes[-1]], [arr_times[0],arr_times[0]/arr_nodes[-1]],
               lw=1, ls=':', color='grey')

    # mni-ramses
    arr_times = []
    arr_nodes = []
    labels = []
    for nodes in range(1,512):
        for entry in data_miniramses:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            commit = entry['commit']
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            arr_times.append(float(time))
            arr_nodes.append(nodes)

    axes.plot(arr_nodes, arr_times, marker='o', markersize=4, label='mini-ramses')
    axes.plot([arr_nodes[0],arr_nodes[-1]], [arr_times[0],arr_times[0]/arr_nodes[-1]],
               lw=1, ls=':', color='grey', label='ideal')

    axes.set_xlabel('number of nodes')
    axes.set_ylabel('time [s]')
    axes.set_xscale('log')
    axes.set_yscale('log')
    axes.legend()
    axes.set_title('Sedov 1024 (MeluXina)')

    plt.savefig("mini-ramses.png", bbox_inches='tight', dpi=200)
    plt.close()