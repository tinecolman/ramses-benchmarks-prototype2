from io_timings import add_data
from visualisation import *

BENCH_HOME = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE'

if __name__ == '__main__':

    cluster='meluxina'
    test='sedov'
    bench = 'benchmark_dev_456b33e2'

    data = []

    # DEV Reference of public ramses version, before space (Nov 8, 2024)
    data = add_data(data, f'{BENCH_HOME}/{cluster}/{bench}',
                    test, which='total')

    # Strong scaling plot
    reso='1024'
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4.5))
    plot_strong_scaling(axes, data, reso)
    plt.savefig(f'../results/images/strong_scaling_{cluster}_{test}_{reso}.png', 
                bbox_inches='tight', dpi=150)
    plt.close()

    # Weak scaling plot
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4.5))
    plot_weak_scaling(axes,data, resos=['256','512','1024'])
    plt.savefig(f'../results/images/weak_scaling_{cluster}_{test}_{reso}.png',
                bbox_inches='tight', dpi=150)
    plt.close()
