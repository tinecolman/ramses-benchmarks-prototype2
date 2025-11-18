from io_timings import add_data
from visualisation import *

# MERGED optimize godunov solver: ctoprim
def load_data_refactoring_ctoprim(test, cluster='meluxina'):
    data = []
    mapping_commits = {}

    if cluster=='meluxina':
        bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_9c518f8a',test)
        mapping_commits['9c518f8a'] = 'dev'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_ctoprim_6fe0c7ba',test)
        mapping_commits['6fe0c7ba'] = 'ctoprim\nremove c'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_ctoprim_14dba807',test)
        mapping_commits['14dba807'] = 'ctoprim\nstore-load'

    if cluster=='marenostrum':
        bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_f1c9a9d4',test)
        mapping_commits['f1c9a9d4'] = 'dev'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_85a70538',test)
        mapping_commits['85a70538'] = 'ctoprim\nremove c'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_ctoprim_f9c4bd8b',test)
        mapping_commits['f9c4bd8b'] = 'ctoprim\nstore-load'

    return data, mapping_commits

# MERGED optimize godunov solver: uslope
def load_data_refactoring_uslope(test, cluster='meluxina'):
    data = []
    mapping_commits = {}

    if cluster=='meluxina':
        bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_9c518f8a/'+test)
        mapping_commits['9c518f8a'] = 'dev'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_refactor_uslope_35224b31/'+test)
        mapping_commits['35224b31'] = 'slope_type\n module'
        #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_refactor_uslope_c1276394/'+test)
        #mapping_commits['c1276394'] = 'slope\n function pointer'
        #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_refactor_uslope_3ec6375d/'+test)
        #mapping_commits['3ec6375d'] = 'slope\n fix'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_41f8c9a9/'+test)
        mapping_commits['41f8c9a9'] = 'slope\n store optim'

    if cluster=='marenostrum':
        bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'
        timer='hydro-godunov'
        # THis looks ok now
        # so why is it slow when merged into gather_sedov_optims?
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_9c518f8a/'+test, which=timer)
        mapping_commits['9c518f8a'] = 'dev'
        '''
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_35224b31/'+test, which=timer)
        mapping_commits['35224b31'] = 'slope_type\n module'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_41f8c9a9/'+test, which=timer)
        mapping_commits['41f8c9a9'] = 'slope\n store optim'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_58cbe70f/'+test, which=timer)
        mapping_commits['58cbe70f'] = 'slope\n inline'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_6a30556d/'+test, which=timer)
        mapping_commits['6a30556d'] = 'merge dev'
        '''

        # try merging the changes into optim_uslope to see which combo breaks
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_debug_optim_uslope_6a30556d/'+test, which=timer)
        mapping_commits['6a30556d'] = 'uslope\n optims'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_debug_optim_uslope_1d66d2f4/'+test, which=timer)
        mapping_commits['1d66d2f4'] = 'merge\n ctoprim' #OK
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_debug_optim_uslope_7e49c5ee/'+test, which=timer)
        mapping_commits['7e49c5ee'] = 'merge\n unigrid' #NOT OK
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_debug_optim_uslope_53d95b3e/'+test, which=timer)
        mapping_commits['53d95b3e'] = 'revert\n stencil csts' #didn't help
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_debug_optim_uslope_9c5aff11/'+test, which=timer)
        mapping_commits['9c5aff11'] = 'revert\n stencil funcs' # did help -> is it because of the function call to get_stencil?
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_debug_optim_uslope_ccb58e0c/'+test, which=timer)
        mapping_commits['ccb58e0c'] = 'force\n unigrid stencil' # 

        # nbor optims
        #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_f1c9a9d4/'+test)
        #mapping_commits['f1c9a9d4'] = 'ref'
        #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_17f9db0b/'+test)
        #mapping_commits['17f9db0b'] = 'slope\n store optim'


    return data, mapping_commits

# optimize godunov solver: trace3d
def load_data_refactoring_trace3d(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='hydro-godunov'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'
    # ran on Meluxina and marenostrum

    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_b779df55/'+test, which=timer)
    #mapping_commits['b779df55'] = 'dev'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_trace3d_2d685d32/'+test, which=timer)
    #mapping_commits['2d685d32'] = 'trace3d\n reduce operations'
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_ef26503c/'+test, which=timer)
    #mapping_commits['ef26503c'] = 'trace\n change access pattern'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_1f94f355/'+test, which=timer)
    mapping_commits['1f94f355'] = 'dev'
    '''
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_d0ea0fcf/'+test, which=timer)
    mapping_commits['d0ea0fcf'] = 'trace\n rewrite'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_a074b55d/'+test, which=timer)
    mapping_commits['a074b55d'] = 'remove\n unroll'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_27cbe09f/'+test, which=timer)
    mapping_commits['27cbe09f'] = 'dvar 2d->1d'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_74409398/'+test, which=timer)
    mapping_commits['74409398'] = 'unroll'
    '''
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_1fa45f4d/'+test, which=timer)
    mapping_commits['1fa45f4d'] = 'unroll intel'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_bis_2c9140b6/'+test, which=timer)
    mapping_commits['2c9140b6'] = 'dvar2D unroll'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_bis_a2163929/'+test, which=timer)
    mapping_commits['a2163929'] = 'swap indices'
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_bis_1441f1ad/'+test, which=timer)
    mapping_commits['1441f1ad'] = 'no swap indices'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_bis_5eb732a5/'+test, which=timer)
    mapping_commits['5eb732a5'] = 'vectorization'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_bis_11d08556/'+test, which=timer)
    mapping_commits['11d08556'] = 'save'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_bis_84c4bed8/'+test, which=timer)
    mapping_commits['84c4bed8'] = 'no save'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_final_3a8b9a0a/'+test, which=timer)
    mapping_commits['3a8b9a0a'] = 'final'
    #'''

    return data, mapping_commits

# optimize godunov solver: work towards combi uslope trace
def load_data_refactoring_uslope_cont(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='hydro-godunov'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_38ee62a7/'+test, which=timer)
    mapping_commits['38ee62a7'] = 'old PR'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_dc40e966/'+test, which=timer)
    mapping_commits['dc40e966'] = 'if inside' # No slowdown for marenostrum

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_7b83dc6c/'+test, which=timer)
    mapping_commits['7b83dc6c'] = 'subroutine'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_f681d747/'+test, which=timer)
    mapping_commits['f681d747'] = 'pure'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_29700d0c/'+test, which=timer)
    mapping_commits['29700d0c'] = 'force inline'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_87734828/'+test, which=timer)
    mapping_commits['87734828'] = 'clean'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_58928d8e/'+test, which=timer)
    mapping_commits['58928d8e'] = 'put back n'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_optim_uslope_bis_33dedf23/'+test, which=timer)
    mapping_commits['33dedf23'] = 'remove !DIR$'

    return data, mapping_commits

# optimize godunov solver: work towards combi uslope trace
def load_data_combine_trace_uslope(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='hydro-godunov'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_rewrite_trace_final_3a8b9a0a/'+test, which=timer)
    #mapping_commits['3a8b9a0a'] = 'optim trace'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_combo_trace_uslope_b76baa57/'+test, which=timer)
    mapping_commits['b76baa57'] = 'optim\n trace & uslope'#'optim uslope'

    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_combo_trace_uslope_d9e74a7a/'+test, which=timer)
    #mapping_commits['d9e74a7a'] = 'move var loop'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_combo_trace_uslope_026ab3f8/'+test, which=timer)
    mapping_commits['026ab3f8'] = 'call uslope\n in trace'

    return data, mapping_commits

# optimize godunov solver: godfine1
def load_data_refactoring_godfine1(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='hydro-godunov'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'
    if cluster=='meluxina':
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_f1c9a9d4/'+test, which=timer)
        mapping_commits['f1c9a9d4'] = 'dev'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_godunov_unigrid_optims_84f604b5/'+test, which=timer)
        mapping_commits['84f604b5'] = 'unigrid'
    if cluster=='marenostrum':
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_unigrid_v2_f1c9a9d4/'+test, which=timer)
        mapping_commits['f1c9a9d4'] = 'ref'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_unigrid_v2_6d9289cf/'+test, which=timer)
        mapping_commits['6d9289cf'] = 'consts'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_unigrid_v2_e7c98f68/'+test, which=timer)
        mapping_commits['e7c98f68'] = 'stencil to func'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_unigrid_v2_01b3c605/'+test, which=timer)
        mapping_commits['01b3c605'] = 'remove unused loc'
        data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_unigrid_v2_41517d79/'+test, which=timer)
        mapping_commits['41517d79'] = '-ipo'

    return data, mapping_commits

# Optimisation of godfine1 by Mattieu
def load_data_matt_godfine(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='hydro-godunov'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_a15bcb5a/'+test, which=timer)
    mapping_commits['a15bcb5a'] = 'dev'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_matt_godfine_361e5449/'+test, which=timer)
    mapping_commits['361e5449'] = 'godfine\nmem access'

    return data, mapping_commits

def load_data_gather_all(test, cluster='meluxina',timer='total'):
    data = []
    mapping_commits = {}

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    # DEV Reference of public ramses version, before space (Nov 8, 2024)
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_8c72f569', test, which=timer)
    mapping_commits['8c72f569'] = 'dev\n Nov 2024' #'starting\n reference'

    # nbor optims
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_f1c9a9d4', test, which=timer)
    mapping_commits['f1c9a9d4'] = 'nbor \n (merged)'

    # unsplit - cmpfluxm optims
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_53727500', test, which=timer)
    mapping_commits['53727500'] = 'unsplit\n (merged)'

    # ctoprim: remove soundspeed computation and store-hit-load dependency
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_bis_b94481de', test, which=timer)
    mapping_commits['b94481de'] = 'ctoprim\n (merged)'

    # uslope: refactor and prefetch center value
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_bis_1a8645b9', test, which=timer)
    mapping_commits['1a8645b9'] = 'uslope 1\n (merged)'

    # trace: refactor to remove code duplication and less math operations
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_bis_b9bfafe9', test, which=timer)
    mapping_commits['b9bfafe9'] = 'trace\n (draft)'

    # uslope: refactor further
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_bis_7616d7b1,', test, which=timer)
    mapping_commits['7616d7b1'] = 'uslope 2\n (merged)'

    # call uslope in trace
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_bis_c3cc0b3a', test, which=timer)
    mapping_commits['c3cc0b3a'] = 'slope \nin trace\n (draft)'

    # godfine1: stencil gathering for unigrid
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_bis_55193e9d', test, which=timer)
    mapping_commits['55193e9d'] = 'unigrid \nstencil\n (merged)'

    # godfine1: stencil gathering for unigrid
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_godunov_unigrid_optims_8a3f336b/'+test, which=timer)
    #mapping_commits['8a3f336b'] = 'unigrid\n stencil'

    # ctoprim: remove soundspeed computation and store-hit-load dependency
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_771f27ad/'+test, which=timer)
    #mapping_commits['771f27ad'] = 'optim\n ctoprim'

    # uslope: refactor and prefetch center value
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_4b5bf9ce/'+test, which=timer)
    #mapping_commits['4b5bf9ce'] = 'optim\n uslope'

    # uslope: refactor and prefetch center value
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_gather_sedov_optims_6b23608c/'+test, which=timer)
    #mapping_commits['6b23608c'] = 'intel fix' # this makes things worse

    return data, mapping_commits

if __name__ == '__main__':

    #data, mapping_commits = load_data_refactoring_ctoprim('sedov','meluxina')
    #plot_execution_time_cpu_speedup(data, mapping_commits, 
    #                                reso='1024', nodes=1, outname='progress_sedov_1024_N1_meluxina.png')

    data1, mapping_commits1 = load_data_gather_all('sedov','meluxina','hydro-godunov')
    data2, mapping_commits2 = load_data_gather_all('sedov','marenostrum','hydro-godunov')
    plot_execution_time_cpu_speedup_multicluster(['meluxina','marenostrum'],
                    [data1,data2], [mapping_commits1,mapping_commits2], 
                    reso='1024', nodes=1, 
                    outname='progress_sedov_1024_N1.png',
                    timer='hydro-godunov')






