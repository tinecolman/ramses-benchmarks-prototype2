from io_timings import add_data
from visualisation import *
from visu_openmp import *

def load_data(test, cluster='meluxina', timer='total'):
    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = []
    mapping_commits = {}

    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_fix_galic_8bc34c39', test, which=timer)

    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_330a43ad', test, which=timer)
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_36f2c9e8', test, which=timer)
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_1b118924', test, which=timer, omp_nthr=[0])
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_7bb705d5', test, which=timer, omp_nthr=[0])
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_b3f89924', test, which=timer, omp_nthr=[0])
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_80e77b94', test, which=timer, omp_nthr=[0])

    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_refine_07765e30', test, which=timer,omp_nthr=[4])
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_misc_38ccdc6b', test, which=timer, omp_nthr=[0])
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_optims_36dcc349', test, which=timer)
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_galaxy_optims_2754a146', test, which=timer)
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_refine_13b91aa4', test, which=timer)#,omp_nthr=[4])


    # V2 format
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_d79d1585', test, which=timer)


    return data, mapping_commits


def ana_subtimers(cluster, test, reso):

    #data, mapping_commits = load_data('galaxy-agora',cluster,'total')
    #print(data)
    #make_table_openmp(data, reso='highres', arr_nodes=[1,2,4])
    #make_plot_openmp(data, reso='highres', arr_nodes=[1,2,4,8,16],
    #                 outname='../results/images/scaling_openmp_'+test+'_'+cluster+'.png')
    
    #timers = ['total', 'coarselevels', 'refine', 'loadbalance', 'particles-maketree',
    #          'poisson-rho', 'particles-killtree', 'poisson-hydro', 'particles-mergetree',
    #          'poisson-phimultigrid', 'poisson-force', 'particles-synchro','particles-move', 'poisson-phicg',
    #          'poisson-boundaries', 'courant', 'hydro-setunew', 'hydro-godunov',
    #          'hydro-revghostzones', 'hydro-setuold', 'hydrouploadfine', 'cooling',
    #          'hydro-ghostzones', 'flag']
    #timers = ['total', 'particles-maketree', 'particles-killtree', 'particles-mergetree', 'poisson-rho','refine','loadbalance']
    timers = ['total']
    for timer in timers:
        print('timer: '+timer)
        data, mapping_commits = load_data(test,cluster,timer)
        make_table_openmp(data, reso='highres', arr_nodes=[1,2,4,8,16,32,64])
        make_plot_openmp(data, reso='highres', arr_nodes=[1,2,4,8,16,32,64],
                     outname='../results/images/scaling_openmp_'+test+'_'+cluster+'_'+timer+'.png')
        print('')



if __name__ == '__main__':

    cluster='meluxina'
    test='galaxy-agora'
    timer='total'

    data, mapping_commits = load_data(test, cluster, timer)

    reso='mediumres'
    plot_mpi_omp_grid(data, reso, 
                      fig_name=f'mpi_omp_grid_{test}_{reso}_{cluster}.png',
                      show_overhead=False)
    
    reso='highres'
    make_plot_openmp(data, reso='highres', arr_nodes=[1,2,4,8,16,32,64],
                     outname='../results/images/scaling_openmp_'+test+'_'+cluster+'_'+timer+'.png')
    make_table_openmp(data, reso='highres', arr_nodes=[1,2,4,8,16,32,64])

