from io_timings import add_data
from visualisation import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colorsx
from collections import defaultdict
from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_mpi_omp_grid(data, reso, show_overhead=False):
    """
    Create a 2D heatmap of execution time:
    - X axis: OpenMP threads
    - Y axis: MPI processes per node
    Thanks, chatgpt.
    """

    # Step 1: aggregate results
    grid = defaultdict(list)

    for entry in data:
        if entry["resolution"]!=reso:
            continue
        mpi = entry["mpi_procs_per_node"]
        omp = entry["omp_threads"]

        avg_time, err_min, err_max = process_times(entry["timings"])
        grid[(mpi, omp)].append(avg_time)

    # Step 2: get sorted unique values
    mpi_vals = sorted(set(k[0] for k in grid.keys()))
    omp_vals = sorted(set(k[1] for k in grid.keys()))

    # remove entries that have either 1 MPI process or 1 OMP thread
    # these are for checking overhead
    if not show_overhead:
        mpi_vals.remove(1)
        omp_vals.remove(1)

    # Step 3: build matrix
    matrix = np.full((len(mpi_vals), len(omp_vals)), np.nan)

    for i, mpi in enumerate(mpi_vals):
        for j, omp in enumerate(omp_vals):
            if (mpi, omp) in grid:
                matrix[i, j] = np.mean(grid[(mpi, omp)])

    # Step 4: plot heatmap
    fig, ax = plt.subplots(figsize=(6, 5))

    cmap = plt.cm.RdYlGn_r  # green = fast, red = slow
    #im = ax.imshow(matrix, cmap=cmap, aspect='auto')
    im = ax.imshow(matrix, cmap=cmap, norm=colorsx.LogNorm())

    # Step 5: ticks & labels
    ax.set_xticks(range(len(omp_vals)))
    ax.set_yticks(range(len(mpi_vals)))

    ax.set_xticklabels(omp_vals)
    ax.set_yticklabels(mpi_vals)

    ax.set_xlabel("OpenMP threads per MPI")
    ax.set_ylabel("MPI processes")
    #ax.set_title("Execution time heatmap")

    # Step 6: annotate each cell
    for i in range(len(mpi_vals)):
        for j in range(len(omp_vals)):
            val = matrix[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}",
                        ha="center", va="center",
                        color="black", fontsize=8)

    # Step 7: colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label("execution time")
    cbar.set_ticks([])

    plt.tight_layout()
    plt.savefig('collapse_grid.png',dpi=150)



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

    plot_mpi_omp_grid(data, reso)
