from io_timings import add_data
from visualisation import *

TAGS = {'9e7b310b':'dev2017-09', # mpi not functioning?
        #'':'dev2018-04',
        #'':'dev2018-10',
        #'':'dev2019-04',
        #'':'dev2019-10',
        #'':'dev2020-04',
        #'':'dev2020-10',
        #'':'dev2021-04',
        #'':'dev2021-10',
        #'7c2b0363':'dev2022-04', # broken
        #'cce4cf97':'dev2022-10', # broken
        'ebcb6769':'dev2023-03',
        '00717e77':'dev2023-10',
        #'d2c4c9e':'dev2024-04', # broken
        '7308417b':'dev2024-10'}
# broken ones all have floating point exeception error

# reference commits for the dev branch
def load_data_dev_branch(test, cluster='meluxina', timer='total'):
    print('Loading data for', test, 'benchmark on', cluster)

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = []
    mapping_commits = {}

    # DEV Reference of public ramses version
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_00717e77', test, which=timer)
    mapping_commits['00717e77'] = 'dev\n Oct 2023'

    # DEV Reference of public ramses version
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_7308417b', test, which=timer)
    #mapping_commits['7308417b'] = 'dev\n Oct 2024'

    # DEV Reference of public ramses version, before space (Nov 8, 2024)
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_8c72f569', test, which=timer)
    mapping_commits['8c72f569'] = 'dev\n Nov 2024' #'starting\n reference'

    # DEV Reference of public ramses version, after clean up etc (Apr 16, 2025)
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_9c518f8a', test, which=timer)
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_HEAD_9c518f8a', test, which=timer)
    mapping_commits['9c518f8a'] = 'dev\n Apr 2025'

    # nbor optims
    #data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_refactor_3cube_nbor_utils_e3a620c3', test, which=timer)
    #mapping_commits['e3a620c3'] = 'nbor\n optims'

    # DEV Reference of public ramses version, SNO meeting 2025
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_456b33e2', test, which=timer)
    mapping_commits['456b33e2'] = 'dev\n Nov 2025'

    # OPENMP Reference of public ramses version, SNO meeting 2025
    # full openMP implemenation for cosmo, including poisson multigrid and particles
    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_2b1a9794', test, which=timer, omp_nthr=4)
    mapping_commits['2b1a9794'] = 'OpenMP\n Nov 2025'

    return data, mapping_commits


# ---- Show SPACE project progress ----

''' Show evolution of execution time on EuroHPC systems '''
def dashboard_execution_time(clusters, arr_data, arr_commits, reso, arr_nodes, outname='dashboard.png'):

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8,5), sharey=True)

    for data, mapping_commits, cluster, ax in zip(arr_data, arr_commits, clusters, axes.flatten()):

        plot_execution_time_multinode(data, mapping_commits, reso,arr_nodes, ax)

        ax.set_title(cluster)

    axes[0].set_ylabel('execution time [s]')
    axes[1].set_ylabel('execution time [s]')
    axes[0].set_yscale('log')
    for ax in axes.flatten():
        ax.tick_params(axis='x', labelrotation=90)
    axes[1].legend()

    #fig.subplots_adjust(wspace=0.1)
    fig.tight_layout()
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

''' Show evolution of strong scaling on EuroHPC systems '''
def dashboard_strong_scaling(clusters, arr_data, arr_commits, reso, outname='dashboard.png'):

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8,5), sharex=True, sharey=True)

    for data, mapping_commits, cluster, ax in zip(arr_data, arr_commits, clusters, axes.flatten()):

        plot_strong_scaling_compare(data, mapping_commits, reso, input_axes=ax)

        ax.set_title(cluster)

    axes[0].set_ylabel('speedup')
    axes[1].set_ylabel('speedup')
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    axes[0].legend()
    axes[1].legend()

    #fig.subplots_adjust(wspace=0.1)
    fig.tight_layout()
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

''' Show evolution of strong scaling on EuroHPC systems '''
def dashboard_weak_scaling(clusters, arr_data, arr_commits, arr_nodes, resos, outname='dashboard.png'):

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8,5), sharex=True, sharey=True)

    for data, mapping_commits, cluster, ax in zip(arr_data, arr_commits, clusters, axes.flatten()):

        plot_weak_scaling_compare(data, mapping_commits, arr_nodes, resos, input_axes=ax)

        ax.set_title(cluster)

    axes[0].set_ylabel('speedup')
    axes[1].set_ylabel('speedup')
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    axes[0].legend()
    axes[1].legend()

    #fig.subplots_adjust(wspace=0.1)
    fig.tight_layout()
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

if __name__ == '__main__':

    test = 'cosmo'

    data_meluxina, commits_meluxina = load_data_dev_branch(test,'meluxina')
    data_marenostrum, commits_marenostrum = load_data_dev_branch(test,'marenostrum')

    clusters = ['MeluXina', 'MareNostrum']
    arr_data = [data_meluxina, data_marenostrum]
    arr_commits = [commits_meluxina, commits_marenostrum]
    dashboard_execution_time(clusters, arr_data, arr_commits, 
                             reso='1024', arr_nodes=[1,2,4,8,16,32],
                             outname=f'../results/images/eurohpc_dashboard_{test}_time.png')
    #dashboard_strong_scaling(clusters, arr_data, arr_commits, reso='1024',
    #                         outname=f'../results/images/eurohpc_dashboard_{test}_strong.png')
    #dashboard_weak_scaling(clusters, arr_data, arr_commits, arr_nodes=[1,8,64], resos=['256','512','1024'],
    #                         outname=f'../results/images/eurohpc_dashboard_{test}_weak.png')
