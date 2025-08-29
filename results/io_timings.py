'''
Functions to load/store the results of a benchmark run.
The timings are extracted from the logfiles and stored in JSON files,
ready to be uploaded to the git.
'''

import os
import subprocess
import json
import numpy as np


# -------- Helper functions for folder names -----------

''' Dissect name of the base benchmark directory:
    benchmark_<branch>_<commit> '''
def get_info_from_benchmark_dir_name(benchmark_dir):
    parts = benchmark_dir.split('/')
    commit = parts[-1][-8:]     # last 8 characters
    branch = parts[-1][10:-9]
    return branch, commit

''' Dissect name of the benchmark configuration subdirectory:
    nodes<N>_<resolution>_omp<threads> '''
def get_info_from_subdir_name(subdir):
    [nodes, reso, omp] = subdir.split('_')
    nodes = int(nodes[5:])
    reso = reso[4:]
    omp = omp[3:]
    return nodes, reso, omp

# -------- Reading ramses logs --------

''' Use grep to get the timings for a specified timer from all logfiles in a directory '''
def get_timings_from_log(run_dir, which='total'):
    if which=='total':
        # take the total time at the bottom
        subprocess.call("grep --no-filename 'Total elapsed time' {}/*.log".format(run_dir) +" | awk '{print $4}' > total_time.txt", shell=True)
        with open('total_time.txt', 'r') as file:
            times = [float(line.strip()) for line in file]
        os.remove('total_time.txt')
    else:
        # go through all files, to read the entire timing block
        times = []
        for item in os.listdir(run_dir):
            if item.endswith('.log'):
                timers = read_timers(os.path.join(run_dir, item))
                # store the data for the requested timer
                try:
                    times.append(timers[which])
                except:
                    continue
    return times

''' retrieve timers for individual parts of the code from the end of the logfile '''
def read_timers(logfile):
    # get timers that are printed in between pattern TIMER and TOTAL
    subprocess.call("awk '/TIMER/{flag=1; next}/TOTAL/{flag=0} flag' " + logfile +" | awk '{print $2}' > indiv_times.txt", shell=True)
    subprocess.call("awk '/TIMER/{flag=1; next}/TOTAL/{flag=0} flag' " + logfile +" | awk '{print substr($0,91,104)}' | sed 's/ //g' > timer_names.txt", shell=True)
    # read data and put into dict
    indiv_times = np.loadtxt('indiv_times.txt')
    timer_names = np.genfromtxt('timer_names.txt',dtype='str')
    timings = {}
    for timer_name, indiv_time in zip(timer_names, indiv_times):
        timings[timer_name] = indiv_time
    os.remove('indiv_times.txt')
    os.remove('timer_names.txt')
    # add total time
    #subprocess.call("grep --no-filename 'Total elapsed time' {}".format(logfile) +" | awk '{print $4}' > total_time.txt", shell=True)
    #total_time = np.loadtxt('total_time.txt', unpack=True)
    #timings['total'] = total_time
    return timings


# -------- database IO -----------

''' Load benchmark results for a specified test '''
def add_data(data, benchmark_dir, test_name, which='total'):
    """Extract new benchmark data and add it to the dataset efficiently."""
    branch, commit = get_info_from_benchmark_dir_name(benchmark_dir)

    data_dir = benchmark_dir+'/'+test_name

    if(not os.path.isdir(data_dir)):
        return data

    # list subdirectories in benchmark test
    for item in os.listdir(data_dir):
        name = os.path.join(data_dir, item)
        if os.path.isdir(name) and item.startswith('nodes'):
            nodes, reso, omp = get_info_from_subdir_name(item)
            total_times = get_timings_from_log(name, which)

            new_entry = {
                "branch": branch,
                "commit": commit,
                "nodes": int(nodes),
                "resolution": reso,
                "omp_threads": int(omp),
                "timings": total_times
            }
            data.append(new_entry)

    return data

''' Write data dictionary to disk as a structured JSON list '''
def write_data(benchmark_file, data):
    with open(benchmark_file, 'w') as f:
        json.dump(data, f, indent=4)
    print("Updated", benchmark_file)

'''' Load previous data dictionary from JSON file '''
def load_data(benchmark_file):
    try: 
        with open(benchmark_file, 'r') as f:
            data= json.load(f)
    except FileNotFoundError:
        print(benchmark_file,"not found. No data to load.")
        data = []
    return data

''' Update the timings with a new benchmark '''
def update_timings(cluster, benchmark_dir, test_name):
    database_file = f'data_wip/timings_{cluster}_{test_name}.json'
    # load existing database
    data = load_data(database_file)
    # add/update benchmark entry
    data = add_data(data, benchmark_dir)
    # update file
    write_data(database_file, data)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description="Extract benchmark timings and save to file.")
    parser.add_argument('cluster', help="HPC system on which the benchmark has been run")
    parser.add_argument('benchmark_dir', help="test directory where the benchmarks have been executed")
    parser.add_argument('test_name', help="name of the benchmark setup")
    args = parser.parse_args()

    update_timings(args.cluster, args.benchmark_dir, args.test_name)
