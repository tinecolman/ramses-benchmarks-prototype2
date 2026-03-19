from io_timings import add_data
from visualisation import *

#def plot_time_vs_nodes(data, mapping_commits, reso, nodes, outname='compare.png'):
   

if __name__ == '__main__':
    
    test='cosmo'
    cluster='meluxina'
    timer='total'
    reso="1024"

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data_ramses = add_data([], bench_home+'/'+cluster+'/'+'benchmark_openmp_5560e020',
                           test, which=timer, omp_nthr=[0])
    data_ramses_omp2 = add_data([], bench_home+'/'+cluster+'/'+'benchmark_openmp_5560e020',
                           test, which=timer, omp_nthr=[2])
    data_ramses_omp4 = add_data([], bench_home+'/'+cluster+'/'+'benchmark_openmp_5560e020',
                           test, which=timer, omp_nthr=[4])
    data_ramses_omp8 = add_data([], bench_home+'/'+cluster+'/'+'benchmark_openmp_5560e020',
                           test, which=timer, omp_nthr=[8])

    data_miniramses = add_data([], bench_home+'/'+cluster+'/'+'mini-benchmark_develop_3b48347b',
                               test, which=timer, version="mini-ramses")

    data_sets = [data_ramses,
                 data_ramses_omp8,
                 data_miniramses]
    labels = ['ramses MPI-only',
              'ramses MPI + 8 OMP',
              'mini-ramses']
    show_ideal=[1,0,1]
    lines=['-','-','-']
    colorVals =["#182e8f", "#3f86c9", "#a035c0"]

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))

    for data,label,ideal,color,ls in zip(data_sets, labels, show_ideal, colorVals, lines):
        arr_times = []
        arr_nodes = []
        labels = []
        for nodes in range(1,512):
            for entry in data:
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                commit = entry['commit']
                # reduce time data
                time, error_min, error_max = process_times(entry['timings'])
                arr_times.append(float(time))
                arr_nodes.append(nodes)

        axes.plot(arr_nodes, arr_times, marker='o', ls=ls, color=color, markersize=3, label=label)
        if ideal:
            axes.plot([arr_nodes[0],arr_nodes[-1]], [arr_times[0],arr_times[0]/arr_nodes[-1]],
                lw=1, ls=':', color='grey')

    axes.set_xlabel('number of nodes')
    axes.set_ylabel('time [s]')
    axes.set_xscale('log')
    axes.set_yscale('log')
    axes.legend()
    axes.set_title(f'{test} {reso} ({cluster})')

    plt.savefig(f'mini-ramses_{test}_{cluster}.png', bbox_inches='tight', dpi=200)
    plt.close()