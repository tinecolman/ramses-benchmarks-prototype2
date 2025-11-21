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

# Finished openmp for SEDOV and COSMO
def load_data_openmp_v2(test, cluster='meluxina', timer='total'):
    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = []
    mapping_commits = {}

    # full openMP implemenation for cosmo, including poisson multigrid and particles
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_2b1a9794', test, which=timer)

    return data, mapping_commits


if __name__ == '__main__':

    # ---- D2.6 ----

    #data, mapping_commits = load_data_cpu_progress_D26('sedov','meluxina','hydro-godunov')
    #make_table_cpu_speedup(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])

    #particles, poisson-savephi, poisson-rho, poisson-phimultigrid, poisson-force
    #data, mapping_commits = load_data_openmp('cosmo','meluxina','poisson-phimultigrid')
    #make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    #make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64], outname='scaling_openmp_cosmo_phimultigrid.png')

    # ---- Nov 2025 ----

    #particles, poisson-savephi, poisson-rho, poisson-phimultigrid, poisson-force
    data, mapping_commits = load_data_openmp_v2('cosmo','meluxina','total')
    #make_table_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64])
    make_plot_openmp(data, reso='1024', arr_nodes=[1,2,4,8,16,32,64], outname='scaling_openmp_cosmo.png')