from io_timings import add_data
from visualisation import *

# OpenMP in virtual boundaries: swap loop order
def load_data_openmp_virtual(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='total'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_1f94f355', test, which=timer)
    mapping_commits['1f94f355'] = 'dev'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_virtual_afe600e8', test, which=timer)
    mapping_commits['afe600e8'] = 'swap loops'

    return data, mapping_commits

# OpenMP in rho_fine: refactor to reduce atomics
def load_data_openmp_virtual(test, cluster='meluxina'):
    data = []
    mapping_commits = {}
    timer='rho'

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_dev_1f94f355', test, which=timer)
    mapping_commits['1f94f355'] = 'dev'

    data = add_data(data, bench_home+'/'+cluster+'/'+'benchmark_openmp_virtual_afe600e8', test, which=timer)
    mapping_commits['afe600e8'] = 'swap loops'

    return data, mapping_commits


if __name__ == '__main__':

    data, mapping_commits = load_data_openmp_virtual('sedov','meluxina')
    plot_execution_time_cpu_speedup(data, mapping_commits, reso='1024', nodes=1)

