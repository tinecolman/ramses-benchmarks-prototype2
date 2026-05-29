from io_timings import add_data


''' Load data of current and previous releases of RAMSES '''
def load_release_data(cluster, test, timer='total'):

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE_RELEASE'

    benchmarks = []
    release_labels = []

    # "Official" releases

    # code broken
    #data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_dev_2024-04-29_d2c4c9e3/',
    #                test, which=timer)
    #release_labels.append("2024-04")
    #benchmarks.append(data)

    data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_dev_2024-10-17_7308417b/',
                    test, which=timer)
    release_labels.append("2024-10")
    benchmarks.append(data)

    data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_dev_2025-05-21_2d87442e/',
                    test, which=timer)
    release_labels.append("2025-05")
    benchmarks.append(data)

    data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_dev_2025-10-03_456b33e2/',
                    test, which=timer)
    release_labels.append("2025-10")
    benchmarks.append(data)

    data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_dev_2026-05-20_7050a55b/',
                   test, which=timer)
    release_labels.append("2026-05")
    benchmarks.append(data)

    # current development
    data = load_latest_openmp_data(cluster, test, timer)
    release_labels.append("openmp")
    benchmarks.append(data)

    return benchmarks, release_labels

def load_latest_openmp_data(cluster, test, timer='total'):

    bench_home = '/home/tcolman/Dropbox/SPACE/DATA_ARCHIVE_WIP_OPENMP'

    data = add_data([], bench_home+'/'+cluster+'/'+'benchmark_openmp_2026-05-20_e9846974/',
                   test, which=timer)
    
    return data