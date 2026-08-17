
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colorsx

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
