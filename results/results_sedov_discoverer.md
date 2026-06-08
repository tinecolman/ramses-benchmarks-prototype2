# Benchmark: sedov on discoverer

Benchmark description: [sedov](../setups/sedov/description.md)

Cluster info: [discoverer](../HPCclusters/discoverer/cluster_description.md)

On this page:
* [if unigrid] Strong and weak scaling of the latest code release (figure)
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Strong and weak scaling of the latest code release (2026-05)

![Scaling](../results/images/scaling_combo_sedov_total_discoverer.png)

This figure shows the strong and weak scaling of the latest official release (2026-05).
Strong scaling can be inferred diagonally, while weak scaling is determined by reading horizontally.
Dotted lines show ideal scaling.

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_sedov_1024_total_discoverer.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 215.45 | 169.80 | 169.69 | 21.2 |
| 2 | 108.10 | 87.25 | 86.31 | 20.2 |
| 4 | 54.47 | 43.33 | 43.29 | 20.5 |
| 8 | 27.63 | 22.17 | 22.03 | 20.3 |
| 16 | 16.23 | 11.68 | 11.41 | 29.7 |
| 32 | 7.89 | 5.99 | 5.99 | 24.1 |
| 64 | 3.80 | 3.19 | 3.16 | 16.9 |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_sedov_1024_total_discoverer.png)

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 |
| 2 | 0.997 | 0.973 | 0.983 |
| 4 | 0.989 | 0.980 | 0.980 |
| 8 | 0.975 | 0.957 | 0.963 |
| 16 | 0.830 | 0.909 | 0.929 |
| 32 | 0.853 | 0.886 | 0.885 |
| 64 | 0.886 | 0.832 | 0.840 |


## Weak scaling evolution

![Weak scaling](../results/images/weak_scaling_sedov_total_discoverer.png)

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | resolution | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|---|
| 1 | 256 | - | - | - |
| 8 | 512 | - | - | - |
| 64 | 1024 | 1.000  | 1.000  | 1.000  |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit e9846974 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_sedov_1024_total_discoverer.png)
## Memory usage

![Memory usage](../results/images/memory_sedov_1024_discoverer.png)

This figure shows the approximate memory per node needed to perform the simulation,
as derived from the log-file outputted by the code. Remark that the actual memory
allocated for the run on the node will be higher, depending on the percentage of 
the allocated ngridmax grids is actually used.
We show the consumption for a different number of OpenMP threads. 
Memory consumption is lower with OMP, due to
the reduced number of ghostzone cells needed to describe the boundaries of the 
MPI-domains.

The table lists the corresponding memory values in GB.
The last column lists the improvement of the OpenMP version with respect to the 
MPI-only version, that is the most optimistic fraction of the MPI-only memory that is needed 
when running with hybrid parallelisation.

Unless otherwise stated, data is for runs using full compute nodes.

| nodes | MPI-only | OMP=2 | OMP=4 | OMP=8 | best |
|---|---|---|---|---|---|
| 1 | 210.30 GB | 200.83 GB | 195.97 GB | 193.41 GB | 92.0 % |
| 2 | 118.78 GB | 106.11 GB | 100.70 GB | 99.23 GB | 83.5 % |
| 4 | 69.63 GB | 59.63 GB | 52.99 GB | 50.46 GB | 72.5 % |
| 8 | 45.75 GB | 35.07 GB | 29.83 GB | 26.64 GB | 58.2 % |
| 16 | 34.98 GB | 23.19 GB | 17.54 GB | 15.02 GB | 42.9 % |
| 32 | 31.62 GB | 17.76 GB | 11.56 GB | 8.88 GB | 28.1 % |
| 64 | 34.96 GB | 16.08 GB | 8.90 GB | 5.92 GB | 16.9 % |


