from io_timings import add_data
from analyse_progress import *

# MERGED Optimization of getcubefather (on meluxina)
def load_data_refactor_nbor_utils(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='total'

    bench_home = '/home/tcolman/Dropbox/SPACE/benchmarks_progress_SPACE'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_prep_omp_cosmo_9084cb47',test, which=timer)
    mapping_commits['9084cb47'] = 'reference'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_prep_omp_cosmo_26a79555',test, which=timer)
    mapping_commits['26a79555'] = 'split\n routine'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_prep_omp_cosmo_787d197d',test, which=timer)
    mapping_commits['787d197d'] = 'remove\n 2nd filter'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_prep_omp_cosmo_0b69fe71/'+test)
    #mapping_commits['0b69fe71'] = 'refactor\n getcubefather'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_prep_omp_cosmo_34e77be2/'+test)
    #mapping_commits['34e77be2'] = 'merge in\n getcubefather'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_prep_omp_cosmo_b0eb822b/'+test)
    #mapping_commits['b0eb822b'] = 'rebase'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_nvector_ind_76fa57a9',test, which=timer)
    mapping_commits['76fa57a9'] = 'no filter'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_nvector_ind_43ecde03/'+test)
    #mapping_commits['43ecde03'] = 'fetch index\n (again)'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_nvector_ind_cc0f971b/'+test)
    #mapping_commits['cc0f971b'] = 'swap index\n order'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_refactor_3cube_nbor_utils_921c030e',test, which=timer)
    mapping_commits['921c030e'] = 'FINAL'

    return data, mapping_commits


if __name__ == '__main__':

    data, mapping_commits = load_data_refactor_nbor_utils('cosmo','meluxina')
    plot_execution_time_cpu_speedup(data, mapping_commits, 
                                    reso='1024', nodes=1, outname='progress_nbor_cosmo_1024_N1_meluxina.png')