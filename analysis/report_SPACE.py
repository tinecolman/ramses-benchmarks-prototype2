from io_timings import add_data
from visualisation import *

# D2.6: Progress CPU optimisation
def load_data_cpu_progress_D26(test, cluster='meluxina', timer='total'):
    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = []
    mapping_commits = {}

    # DEV Reference of public ramses version, before space (Nov 8, 2024)
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_8c72f569', test, which=timer)
    mapping_commits['8c72f569'] = 'dev\n Nov 2024' #'starting\n reference'

    # DEV Reference of public ramses version, after clean up etc (Apr 16, 2025)
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_9c518f8a/'+test, which=timer)
    #mapping_commits['9c518f8a'] = 'dev\n Apr 2025'

    # nbor optims
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_refactor_3cube_nbor_utils_e3a620c3', test, which=timer)
    mapping_commits['e3a620c3'] = 'nbor\n optims'

    return data, mapping_commits

# D2.6: Progress OpenMP implementation
def load_data_openmp(test, cluster='meluxina', timer='total'):
    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = []
    mapping_commits = {}

    # full openMP implemenation of sedov, as pushed to ramses-romain
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_hydro_bis_a0a34a7f/'+test, which=timer)

    # full openMP implemenation of multigrid for cosmo
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_cosmo_0c73de54', test, which=timer)

    return data, mapping_commits


# D 1.6: Finished openmp for SEDOV and COSMO
def load_data_openmp_d16(test, cluster='meluxina', timer='total'):
    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = []

    # hack to get plot for meluxina cosmo
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_456b33e2', test, which=timer, omp_nthr=[0])
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_5560e020', test, which=timer, omp_nthr=[4])

    # full openMP implemenation for cosmo, including poisson multigrid and particles
    # corresponds to 990b027e on ramses_organisation
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_5560e020', test, which=timer)

    return data

if __name__ == '__main__':

    ''' Sedov timers:
    hydro-godunov         &  courant
    hydro-setunew        &  hydro-setuold  
    hydro-revghostzones  &  hydro-ghostzones '''

    ''' Cosmo timers:
    coarse levels        & courant
    particles-maketree   &  particles-killtree
    particles-synchro    &  particles-move
    poisson-savephi      &  poisson-phimultigrid
    poisson-rho          &  poisson-force   '''

    # ---- D2.6 ----

    #data = load_data_cpu_progress_D26('sedov','meluxina','hydro-godunov')
    #make_table_cpu_speedup(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])

    #particles, poisson-savephi, poisson-rho, poisson-phimultigrid, poisson-force
    #data = load_data_openmp('cosmo','meluxina','poisson-phimultigrid')
    #make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    #make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64], outname='scaling_openmp_cosmo_phimultigrid.png')

    # ---- D1.6 and D2.7 (Dec 2025) ----
    #data = load_data_openmp_d16('sedov','marenostrum','total')
    #make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    #make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64],
    #                 outname='../results/images/openmp_strong_scaling_sedov_marenostrum.png',
    #                 title='Sedov on MareNostrum')
    #make_plot_openmp_weak_scaling(data, resos=['512','1024','2048'], arr_nodes=[1,8,64],
    #                 outname='../results/images/openmp_weak_scaling_sedov_marenostrum.png')
    
    #data = load_data_openmp_d16('sedov','meluxina','hydro-ghostzones')
    #make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    #make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64],
    #                 outname='../results/images/openmp_strong_scaling_sedov_meluxina.png',
    #                 title='Sedov on MeluXina')

    #data = load_data_openmp_d16('cosmo','marenostrum','total')
    #make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    #make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64],
    #                 outname='../results/images/openmp_strong_scaling_cosmo_marenostrum.png',
    #                 title='Cosmo on MareNostrum')
    
    data = load_data_openmp_d16('cosmo','meluxina','total')
    make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64],
                     outname='../results/images/openmp_strong_scaling_cosmo_meluxina.png',
                     title='Cosmo on MeluXina')


