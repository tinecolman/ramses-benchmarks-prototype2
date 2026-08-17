'''
Functions to load/store the results of a benchmark run.
The timings are extracted from the logfiles and stored in JSON files,
ready to be uploaded to the git.
'''

import os
import subprocess
import json
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx

''' Parse meta data written at the top of the log file '''
def parse_metadata(logfile):
    meta = {}

    with open(logfile, "r") as f:
        start_meta = False
        end_meta = False
        nlines_header = 0
        for line in f:
            if (not start_meta) and line.startswith("##################"):
                # we have reached the start of the meta data
                start_meta = True
            elif start_meta and (not end_meta):
                if line.startswith("##################"):
                    # we have reached the end of the meta data
                    end_meta = True
                else:
                    # we are currently reading the meta data
                    line = line.strip()
                    try:
                        [key, value] = line.split(': ')
                        meta[key] = value
                    except:
                        continue
            else:
                # we are in the header printed by the code itself,
                # which contains the compilation info
                line = line.strip()
                if line.startswith('compile command'):
                    meta['compile command'] = line.split('=', 1)[1].strip()
                    meta['compiler'] = get_compiler(meta['compile command'])
                elif line.startswith('last commit'):
                    # end of the header printed by the code
                    break
                nlines_header += 1
                if nlines_header > 100:
                    # no compilation info in this log file
                    break
    return meta

''' Get the compiler (value of MPIF90) from the compile command in the log file '''
def get_compiler(compile_command):
    for part in compile_command.split():
        if part.startswith('MPIF90='):
            # strip the escaped whitespace preceding the compilation flags
            return part[len('MPIF90='):].rstrip('\\')
    return None

''' Check whether a run should be discarded because of the compiler it was built with '''
def skip_compiler(meta, exclude_compilers):
    if not exclude_compilers:
        return False
    return meta.get('compiler') in exclude_compilers


# -------- Helper functions for folder names -----------

''' Dissect name of the base benchmark directory:
    benchmark_<branch>_<commit> '''
def get_info_from_benchmark_dir_name(benchmark_dir, version=2):
    parts = benchmark_dir.split('/')
    # if dir name ends with /, remove last item which is empty
    if parts[-1]=='':
        parts.pop()
    commit = parts[-1][-8:]     # last 8 characters
    if version==2:
        date = parts[-1][-19:-9]
        branch = parts[-1][10:-20]
    else:
        branch = parts[-1][10:-9]
    return branch, commit

''' Dissect name of the benchmark configuration subdirectory:
    nodes<N>_<resolution>_omp<threads> '''
def get_info_from_subdir_name(subdir, version=2):
    #print(subdir)
    if version==1:
        # nodes<N>_reso<resolution>_omp<threads>
        [nodes, reso, omp] = subdir.split('_')
        nodes = int(nodes[5:])
        reso = reso[4:]
        omp = omp[3:]
        mpi = "max"
    else:
        # reso<resolution>_nodes<N>_mpi<tasks/node>_omp<threads/task>
        [reso, nodes, cores, mpi, omp] = subdir.split('_')
        nodes = int(nodes[5:])
        reso = reso[4:]
        omp = omp[3:]
        mpi = mpi[3:]
    return reso, nodes, mpi, omp

# -------- Reading ramses logs --------

''' Use grep to get the timings for a specified timer from all logfiles in a directory.
    Runs built with a compiler listed in exclude_compilers are ignored,
    the corresponding logfiles are appended to the skipped list. '''
def get_timings_from_log(run_dir, which='total', version="ramses", exclude_compilers=None, skipped=None):
    meta = {}
    times = []
    logfiles = []

    # go through all files, since different runs in the same directory
    # can have been built with a different compiler
    for item in os.listdir(run_dir):
        if not item.endswith('.log'):
            continue
        logfile = os.path.join(run_dir, item)
        if version=="ramses":
            file_meta = parse_metadata(logfile)
            if skip_compiler(file_meta, exclude_compilers):
                if skipped is not None:
                    skipped.append(logfile)
                continue
            meta = file_meta
        logfiles.append(logfile)

        if which=='total':
            # take the total time at the bottom
            #subprocess.call("grep --no-filename 'Total elapsed time' {}".format(logfile) +" | awk '{print $4}' > total_time.txt", shell=True)
            subprocess.call("grep --no-filename 'TOTAL' {}".format(logfile) +" | awk '{print $1}' > total_time.txt", shell=True)
            with open('total_time.txt', 'r') as file:
                times += [float(line.strip()) for line in file]
            os.remove('total_time.txt')
        else:
            # read the entire timing block
            if version=="ramses":
                timers = read_timers(logfile)
            elif version=="mini-ramses":
                timers = read_timers_miniramses(logfile)
            # store the data for the requested timer
            try:
                times.append(timers[which])
            except:
                continue
    #if len(times)>0:
    #    # check for outlyers
    #    max_time = max(times)
    #    min_time = min(times)
    #    if max_time > min_time*2:
    #        times.remove(max_time)
    #        print('WARNING: removed outlyer', max_time, 'from', times)

    # get memory consumption
    if len(times)>0:
        subprocess.call("grep --no-filename 'Used memory' {}".format(' '.join(logfiles)) +" | awk '{print $3, $4}' > memory.txt", shell=True)
        max_mem = 0
        with open('memory.txt', 'r') as file:
            for line in file:
                value, unit = line.strip().split(' ')
                value = float(value) # this is the max consumption amongst MPI procs for 1 proc
                # renormalize to MB
                if unit=='kB':
                    value = value/1e3
                elif unit=='GB':
                    value = value*1e3
                elif unit=='TB':
                    value = value*1e6
                max_mem = max(max_mem, value)
        os.remove('memory.txt')
        # Get the total memory for the node
        max_mem = max_mem * int(meta['MPI per node'])
        # convert to GB
        max_mem = max_mem / 1e3
        meta['max memory per node'] = str(max_mem) + ' GB'

    return times, meta

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

# -------- Reading mini-ramses logs --------

''' retrieve timers for individual parts of the code from the end of the logfile '''
def read_timers_miniramses(logfile):
    # get timers that are printed in between pattern STEP and TOTAL
    subprocess.call("awk '/STEP/{flag=1; next}/TOTAL/{flag=0} flag' " + logfile +" | awk '{print $1}' > indiv_times.txt", shell=True)
    subprocess.call("awk '/STEP/{flag=1; next}/TOTAL/{flag=0} flag' " + logfile +" | awk '{print substr($0,27,51)}' | sed 's/ //g' > timer_names.txt", shell=True)
    # read data and put into dict
    indiv_times = np.loadtxt('indiv_times.txt')
    timer_names = np.genfromtxt('timer_names.txt',dtype='str')
    timings = {}
    for timer_name, indiv_time in zip(timer_names, indiv_times):
        timings[timer_name] = indiv_time
    os.remove('indiv_times.txt')
    os.remove('timer_names.txt')
    return timings

# -------- database IO -----------

''' Load benchmark results for a specified test '''
def add_data(data, benchmark_dir, test_name, which='total', omp_nthr=None, version='ramses', cpu_per_node=128, bench_version=2, exclude_compilers=None):
    branch, commit = get_info_from_benchmark_dir_name(benchmark_dir)

    data_dir = benchmark_dir+'/'+test_name

    if(not os.path.isdir(data_dir)):
        return data

    # logfiles discarded because of the compiler they were built with
    skipped = []

    #TODO version dir name

    # list subdirectories in benchmark test
    for item in os.listdir(data_dir):
        name = os.path.join(data_dir, item)
        if bench_version==1:
            starter='nodes'
        else:# bench_version==2:
            starter='reso'
        if os.path.isdir(name) and item.startswith(starter):
            reso, nodes, mpi, omp = get_info_from_subdir_name(item,bench_version)
            if mpi=="max":
                mpi = cpu_per_node
            total_times,metadata = get_timings_from_log(name, which, version,
                                                        exclude_compilers=exclude_compilers,
                                                        skipped=skipped)
            if len(total_times)>0:
                metadata["branch"] = branch
                metadata["commit"] = commit
                new_entry = {
                    "nodes": int(nodes),
                    "resolution": reso,
                    "mpi_procs_per_node": int(mpi),
                    "omp_threads": int(omp),
                    "timings": total_times,
                    "metadata": metadata
                }
                if (omp_nthr==None) or (int(omp) in omp_nthr):
                    data.append(new_entry)

    print('Added data from', benchmark_dir)
    if len(skipped)>0:
        print('  skipped', len(skipped), 'run(s) built with compiler', exclude_compilers)

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


# -------- process timings -----------

# ---- Recipe for reducing data ----

''' Get average time and error bars from the gathered total times printed in the log files '''
def process_times(times):
    if len(times)>0:
        time = np.average(times)
        error_min = time-np.min(times)
        error_max = np.max(times)-time
    else:
        time = np.nan
        error_min=0
        error_max=0
    return time, error_min, error_max


# ---- helpers

''' Extract the results from the raw benchmark data '''
def scan_data(data, arr_nodes, arr_resos):
    times = []
    used_nodes = []
    used_resos = []
    configs = []
    for nodes,reso in zip(arr_nodes, arr_resos):

        # search best average time amongst mpi-omp configs
        best_entry, best_time = search_best_config(data,reso,nodes)

        if best_entry is not None:
            times.append(float(best_time))
            used_nodes.append(nodes)
            used_resos.append(reso)
            best_config = f'MPI={best_entry['mpi_procs_per_node']} OMP={best_entry['omp_threads']}'
            configs.append(best_config)

    return times, used_nodes, used_resos, configs


''' Search for the best average time amongst different MPI-OMP configurations'''
def search_best_config(data,reso,nodes):
    best_entry = None
    best_time = np.inf

    # search best time among mpi-omp configs
    for entry in data:
        if entry['resolution']!=reso:
            continue
        if entry['nodes']!=nodes:
            continue
        # reduce time data
        time, error_min, error_max = process_times(entry['timings'])

        # keep fastest config
        if time < best_time:
            best_time = time
            best_entry = entry

    return best_entry, best_time
    
''' create colors from a given colormap '''
def get_colors(labels,cmap_name):
    cmap = plt.get_cmap(cmap_name)
    cNorm  = colorsx.Normalize(vmin=0, vmax=len(labels))
    colorVals =  {}
    for val,commit in zip(range(1,len(labels)+1),labels):
        colorVals[commit] = cmap(cNorm(val))
    return colorVals


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description="Extract benchmark timings and save to file.")
    parser.add_argument('cluster', help="HPC system on which the benchmark has been run")
    parser.add_argument('benchmark_dir', help="test directory where the benchmarks have been executed")
    parser.add_argument('test_name', help="name of the benchmark setup")
    args = parser.parse_args()

    update_timings(args.cluster, args.benchmark_dir, args.test_name)
