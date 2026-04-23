from io_timings import add_data
from visualisation import *
from visu_openmp import *


def load_data(cluster, test, timer):

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

    data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_openmp_2nd_collapse_b0f9456b', test, which=timer)

    return data

if __name__ == '__main__':

    cluster='meluxina'
    test='collapse-MHD'
    timer='total'
    reso='med'

    data = load_data(cluster, test, timer)

    plot_mpi_omp_grid(data, reso, 
                      fig_name=f'mpi_omp_grid_{test}_{reso}_{cluster}.png',
                      show_overhead=False)
