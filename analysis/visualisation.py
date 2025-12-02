
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

# ---- CPU optimisation ----

''' Make a figure of the execution time comparing different commits '''
def plot_execution_time_cpu_speedup(data, mapping_commits, reso, nodes, outname='check_refactor.png'):

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))

    times = []
    labels = []
    for entry in data:
        if entry['resolution']!=reso:
            continue
        if entry['nodes']!=nodes:
            continue
        commit = entry['commit']
        # reduce time data
        time, error_min, error_max = process_times(entry['timings'])
        times.append(float(time))
        labels.append(mapping_commits[commit])
        axes.scatter(np.full(len(entry['timings']),mapping_commits[commit]),entry['timings'],marker='o',s=3,color='black')

    axes.errorbar(labels, times, fmt='x',markersize=10, color='black')

    # write overall performance gain to screen
    diff = (times[-1]-times[0])/times[0]*100
    print(f'performance diff: {diff} %')

    axes.tick_params(axis='x', labelrotation=90)
    axes.set_ylabel('time [s]')
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

''' Make a figure of the execution time comparing different commits '''
def plot_execution_time_cpu_speedup_multicluster(clusters, data_arr, mapping_commits_arr,
                                                 reso, nodes, outname='check_refactor.png', timer=''):

    colors = [(0.8,0.4,0.0),(0.1,0.3,0.8), 'red', 'green', 'yellow']

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6,4))

    for cluster,color,data,mapping_commits in zip(clusters,colors,data_arr,mapping_commits_arr):
        times = []
        labels = []
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            commit = entry['commit']
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))
            labels.append(mapping_commits[commit])
            axes.scatter(np.full(len(entry['timings']),mapping_commits[commit]),entry['timings'],marker='o',s=3,color=color)

        axes.errorbar(labels, times, fmt='x',markersize=10, color=color)

        # write overall performance gain to screen
        diff = (times[-1]-times[0])/times[0]*100
        speedup=(times[0])/times[-1]
        print(f'performance diff: {diff} %, speed up: {speedup}')

        axes.scatter([],[],marker='o',s=5,color=color, label=cluster)

    axes.tick_params(axis='x', labelrotation=90)
    axes.set_ylabel(f'{timer} time [s]')
    axes.legend(loc='center left')
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close() 

''' Plot evolution of execution time for different number of nodes '''
''' Make a figure of the execution time comparing different commits '''
def plot_execution_time_multinode(data, mapping_commits, reso, arr_nodes, input_axes=None, outname='check_refactor.png'):

    # create colors
    cmap = plt.get_cmap('managua')
    cNorm  = colorsx.LogNorm(vmin=1, vmax=max(arr_nodes))
    colorVals = {}
    for val in arr_nodes:
        colorVals[val] = cmap(cNorm(val))

    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    for nodes in arr_nodes:
        times = []
        labels = []
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            commit = entry['commit']
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))
            labels.append(mapping_commits[commit])
            axes.scatter(np.full(len(entry['timings']),mapping_commits[commit]),entry['timings'],marker='o',s=3,color=colorVals[nodes])

        axes.errorbar(labels, times, fmt='o',markersize=6, color=colorVals[nodes], label=str(nodes)+'nodes')

        # plot a line from the last point to make comparison easier
        if len(labels)>0:
            axes.plot([labels[0],labels[-1]], [times[0],times[0]], ls=':', lw=1.3, color=colorVals[nodes])


        # write overall performance gain to screen
        #diff = (times[-1]-times[0])/times[0]*100
        #print(f'performance diff: {diff} %')

    if input_axes==None:
        axes.tick_params(axis='x', labelrotation=90)
        axes.set_ylabel('time [s]')
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()

''' Spit out a latex table comparing two commits '''
def make_table_cpu_speedup(data, reso, arr_nodes, first_column=True):

    for nodes in arr_nodes:
        times = []
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))

        diff = (-1)*(times[-1]-times[0])/times[0]*100

        if first_column:
            space_report_string = '{} & {:.3f} & {:.3f} & {:.1f} \\\\ \\hline'.format(str(nodes).rjust(2),times[0],times[-1],diff)
        else:
            space_report_string = '{:.3f} & {:.3f} & {:.1f} \\\\ \\hline'.format(times[0],times[-1],diff)
        print(space_report_string)

''' Make a figure of the strong scaling comparing different commits '''
def plot_strong_scaling_compare(data, mapping_commits, reso, input_axes=None, outname='check_refactor.png'):

    ls = {0:'-', 4:'--', 8:'--'}

    # create colors
    cmap = plt.get_cmap('gray_r')
    cNorm  = colorsx.Normalize(vmin=0, vmax=len(mapping_commits))
    colorVals =  {}
    for val,commit in zip(range(1,len(mapping_commits)+1),mapping_commits):
        colorVals[commit] = cmap(cNorm(val))

    # create figure if none is given
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    max_nodes = 1
    for commit in mapping_commits:
        omp=set([])
        times = []
        arr_nodes=[]
        for nodes in range(512):
            # search the entry
            for entry in data:
                if entry['commit']!=commit:
                    continue
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                #if entry['omp_threads']!=0:
                #    continue
                # reduce time data
                time, error_min, error_max = process_times(entry['timings'])
                times.append(float(time))
                arr_nodes.append(nodes)
                max_nodes=max(max_nodes,nodes)
                omp.add(entry['omp_threads'])
        if len(arr_nodes)>0:
            omp = sorted(list(omp))
            if len(omp)>1:
                print('waring: various omp threads in this data')
            axes.plot(arr_nodes,np.array(times[0])/np.array(times), ls=ls[omp[0]],
                  color=colorVals[commit], marker='o', markersize=4, label=mapping_commits[commit])

    # add ideal scaling line
    axes.plot([1,max_nodes],[1,max_nodes], c=(0.25,0.85,0.25),ls=':', lw=2)

    if input_axes==None:
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('speedup')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()

''' Make a figure of the strong scaling comparing different commits '''
def plot_weak_scaling_compare(data, mapping_commits, arr_nodes_in, resos, input_axes=None, outname='check_refactor.png'):

    ls = {0:'-', 4:'--'}

    # create colors
    cmap = plt.get_cmap('gray_r')
    cNorm  = colorsx.Normalize(vmin=0, vmax=len(mapping_commits))
    colorVals =  {}
    for val,commit in zip(range(1,len(mapping_commits)+1),mapping_commits):
        colorVals[commit] = cmap(cNorm(val))

    # create figure if none is given
    if input_axes==None:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
    else:
        axes = input_axes

    max_nodes = 1
    for commit in mapping_commits:
        omp=set([])
        times = []
        arr_nodes=[]
        for nodes,reso in zip(arr_nodes_in, resos):
            # search the entry
            for entry in data:
                if entry['commit']!=commit:
                    continue
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                #if entry['omp_threads']!=0:
                #    continue
                # reduce time data
                time, error_min, error_max = process_times(entry['timings'])
                times.append(float(time))
                arr_nodes.append(nodes)
                max_nodes=max(max_nodes,nodes)
                omp.add(entry['omp_threads'])
        if len(times)>0:
            omp = sorted(list(omp))
            if len(omp)>1:
                print('waring: various omp threads in this data')
            eff = np.array(times[0])/np.array(times)
            axes.plot(arr_nodes,eff, ls=ls[omp[0]],
                  color=colorVals[commit], marker='o', markersize=4,
                  label=mapping_commits[commit])

    # add ideal scaling line
    axes.plot([1,max_nodes],[1,1], c=(0.25,0.85,0.25), ls=':', lw=2)

    if input_axes==None:
        axes.set_xlabel('number of nodes')
        axes.set_ylabel('efficiency')
        axes.set_xscale('log')
        axes.set_yscale('log')
        axes.legend()
        plt.savefig(outname, bbox_inches='tight', dpi=200)
        plt.close()

# ---- OpenMP implementation ----

''' Plot the strong scaling for MPI+OpenMP versus MPI-only'''
def make_plot_openmp(data, reso, arr_nodes, outname='scaling_openmp.png', title=None):

    #labels=['MPI only', 'MPI + 2 OpenMP','MPI + 4 OpenMP','MPI + 8 OpenMP']
    labels=['MPI only', 'MPI + 4 OpenMP']

    # create colors
    cmap = plt.get_cmap('Greens')
    cNorm  = colorsx.Normalize(vmin=0.25, vmax=3.75)
    colorVals = {}
    colorVals = [(0.1,0.1,0.7)]
    for val in [1,2,3]:
        colorVals.append(cmap(cNorm(val)))

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4.5))

    ref_value = 1
    for omp,lab,col in zip([0,4],labels,colorVals):
        times = []
        for nodes in arr_nodes:
            for entry in data:
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                if entry['omp_threads']!=omp:
                    continue
                # reduce time data
                time, error_min, error_max = process_times(entry['timings'])
                times.append(float(time))
                if omp==0 and nodes==1:
                    ref_value=float(time)
        axes.plot(arr_nodes,ref_value/np.array(times),label=lab,color=col,marker='o',markersize=3)

    axes.plot(arr_nodes,arr_nodes,color='black',lw=1,ls='--')

    axes.set_xscale('log')
    axes.set_yscale('log')
    axes.set_xlabel('nodes')
    axes.set_ylabel('speedup')
    axes.set_xticks([])
    axes.set_xticks([],minor=True)
    axes.set_xticks(arr_nodes, labels=arr_nodes)
    axes.legend()
    if title!=None:
        axes.set_title(title)
    plt.savefig(outname, bbox_inches='tight', dpi=200)
    plt.close()

''' Spit out a latex table comparing different number of openMP threads '''
def make_table_openmp(data, reso, arr_nodes):

    nthr = [0,2,4,8]
    space_report_string = 'Nodes & MPI '
    for i in range(1,len(nthr)):
        space_report_string = space_report_string + f'& omp {nthr[i]}'
    space_report_string = space_report_string + '& diff'
    print(space_report_string)

    ref = 0
    for nodes in arr_nodes:
        times = []
        for omp in nthr:
            for entry in data:
                if entry['resolution']!=reso:
                    continue
                if entry['nodes']!=nodes:
                    continue
                if entry['omp_threads']!=omp:
                    continue
                # reduce time data
                time, error_min, error_max = process_times(entry['timings'])
                times.append(float(time))

        if nodes==1:
            ref = min(times)

        # nodes MPI 2th 4th 8thr gain
        space_report_string = '{} & {:.3f}'.format(str(nodes).rjust(2),times[0])
        best_time = 1e10
        if len(times)>1:
            for i in range(1,len(nthr)):
                best_time = min(best_time,times[i])
                space_report_string = space_report_string + '& {:.3f}'.format(times[i])
            diff = (-1)*(best_time - times[0])/times[0] * 100
            space_report_string = space_report_string + '& {:.1f} \\\\ \\hline'.format(diff)
        print(space_report_string)

    print('scaling efficiencity at', arr_nodes[-1], 'nodes:', ref/times[1]/arr_nodes[-1])

''' make a simple strong scaling plot of a benchmark'''
def plot_strong_scaling(axes, data, reso):

    times = []
    arr_nodes=[]
    for nodes in range(512):
        # search the entry
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            if entry['omp_threads']!=0:
                continue
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))
            arr_nodes.append(nodes)
    axes.plot(arr_nodes,np.array(times[0])/np.array(times),
              color='black', marker='o', markersize=4)

    axes.plot(arr_nodes,arr_nodes,color='black',lw=1,ls='--')

    print('Strong scaling efficiency at nodes', arr_nodes)
    print(np.array(times[0])/np.array(times)/arr_nodes)

    axes.set_xscale('log')
    axes.set_yscale('log')
    axes.set_xlabel('nodes')
    axes.set_ylabel('speedup')
    axes.set_xticks([])
    axes.set_xticks([],minor=True)
    axes.set_xticks(arr_nodes, labels=arr_nodes)
    axes.set_xlim([min(arr_nodes), max(arr_nodes)])
    axes.set_ylim([min(arr_nodes), max(arr_nodes)])
    axes.set_title('strong scaling')

''' make a simple weak scaling plot of a benchmark'''
def plot_weak_scaling(axes, data,resos):

    nodes = 1
    times = []
    arr_nodes = []
    for reso in resos:
        for entry in data:
            if entry['resolution']!=reso:
                continue
            if entry['nodes']!=nodes:
                continue
            if entry['omp_threads']!=0:
                continue
            # reduce time data
            time, error_min, error_max = process_times(entry['timings'])
            times.append(float(time))
            arr_nodes.append(nodes)
        nodes = nodes*8
    
    eff = np.array(times[0])/np.array(times)
    axes.plot(arr_nodes,eff, 
              color='black', marker='o', markersize=4)

    axes.plot(arr_nodes,np.ones(len(arr_nodes)),color='black',lw=1,ls='--')

    print('Weak scaling efficiency at nodes', arr_nodes)
    print(eff)

    axes.set_xscale('log')
    axes.set_yscale('log')
    axes.set_xlabel('nodes')
    axes.set_ylabel('efficiency')
    axes.set_xticks([])
    axes.set_xticks([],minor=True)
    axes.set_xlim([min(arr_nodes), max(arr_nodes)])
    axes.set_ylim([min(eff)*0.8, 1.1])
    axes.set_xticks(arr_nodes, labels=arr_nodes)
    axes.set_title('weak scaling')