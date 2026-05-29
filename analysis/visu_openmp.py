from visualisation import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colorsx


''' Plot the strong scaling for MPI+OpenMP versus MPI-only'''
def make_plot_openmp(data, reso, arr_nodes, omp_thrds=[0,2,4,8], outname='scaling_openmp.png', title=None):

    labels={0: 'MPI only',
            2: 'MPI + 2 OpenMP',
            4: 'MPI + 4 OpenMP',
            8: 'MPI + 8 OpenMP',
            16:'MPI + 16 OpenMP'}

    # create colors
    cmap = plt.get_cmap('Greens')
    cNorm  = colorsx.Normalize(vmin=0.50, vmax=4.1)
    colorVals = {0: (0.1,0.1,0.7, 1),
                 2: cmap(cNorm(1)),
                 4: cmap(cNorm(2)),
                 8: cmap(cNorm(3)),
                 16:cmap(cNorm(4))}

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4.5))

    ref_value = 1
    for omp in omp_thrds:
        mynodes = []
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
                if len(entry['timings'])>0:
                    time, error_min, error_max = process_times(entry['timings'])
                    times.append(float(time))
                    mynodes.append(nodes)
                    if omp==0 and nodes==1:
                        ref_value=float(time)
        axes.plot(mynodes,ref_value/np.array(times),label=labels[omp],color=colorVals[omp],marker='o',markersize=3)

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
    print('Figure outputted to', outname)


''' Spit out a latex table comparing different number of openMP threads '''
def make_table_openmp(data, reso, arr_nodes):

    nthr = [0,2,4,8,16]
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

''' Plot the strong scaling for MPI+OpenMP versus MPI-only'''
def make_plot_openmp_weak_scaling(data, resos, arr_nodes, outname='scaling_openmp.png'):

    labels=['MPI only', 'MPI + 2 OpenMP','MPI + 4 OpenMP','MPI + 8 OpenMP']

    # create colors
    cmap = plt.get_cmap('Greens')
    cNorm  = colorsx.Normalize(vmin=0.25, vmax=3.75)
    colorVals = {}
    colorVals = [(0.1,0.1,0.7)]
    for val in [1,2,3]:
        colorVals.append(cmap(cNorm(val)))

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4.5,4.5))

    ref_value = 1
    for omp,lab,col in zip([0,2,4,8],labels,colorVals):
        nodes = 1
        times = []
        for nodes,reso in zip(arr_nodes,resos):
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

        print(times)
        eff = np.array(times[0])/np.array(times)
        print(eff)
        axes.plot(arr_nodes,eff,label=lab,color=col,marker='o',markersize=3)

    axes.plot(arr_nodes,np.ones(len(arr_nodes)),color='black',lw=1,ls='--')

    axes.set_xscale('log')
    axes.set_yscale('log')
    axes.set_xlabel('nodes')
    axes.set_ylabel('spefficiencyeedup')
    axes.set_xticks([])
    axes.set_xticks([],minor=True)
    axes.set_xticks(arr_nodes, labels=arr_nodes)
    axes.set_xlim([min(arr_nodes), max(arr_nodes)])
    axes.legend()
    plt.savefig(outname, bbox_inches='tight', dpi=300)
    plt.close()