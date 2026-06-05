# Benchmark: sedov on meluxina

Benchmark description: [sedov](../setups/sedov/description.md)

Cluster info: [meluxina](../HPCclusters/meluxina/cluster_description.md)

On this page:
* Strong and weak scaling of the latest code release (figure)
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* Weak scaling evolution (figure & table with efficiency)

## Strong and weak scaling of the latest code release (2026-05)

![Scaling](../results/images/scaling_combo_sedov_total_meluxina.png)

This figure shows the strong and weak scaling of the latest official release (2026-05).
Strong scaling can be inferred diagonally, while weak scaling is determined by reading horizontally.
Dotted lines show ideal scaling.

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_sedov_1024_total_meluxina.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2025-05 | 2025-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|---|---|
| 1 | 168.04 | 165.99 | 147.27 | 134.08 | 133.42 | 20.6 |
| 2 | 85.22 | 85.23 | 75.73 | 68.80 | 68.09 | 20.1 |
| 4 | 43.31 | 43.31 | 38.43 | 34.80 | 34.52 | 20.3 |
| 8 | 22.02 | 22.01 | 19.43 | 17.76 | 17.51 | 20.5 |
| 16 | 11.39 | 11.29 | 10.16 | 9.27 | 9.04 (MPI=64 OMP=2) | 20.6 |
| 32 | 5.82 | 5.86 | 5.22 | 4.79 | 4.69 | 19.4 |
| 64 | 3.19 | 3.22 | 2.97 | 2.84 | 2.82 (MPI=64 OMP=2) | 11.7 |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_sedov_1024_total_meluxina.png)

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | 2024-10 | 2025-05 | 2025-10 | 2026-05 | openmp (beta) |
|---|---|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2 | 0.986 | 0.974 | 0.972 | 0.974 | 0.980 |
| 4 | 0.970 | 0.958 | 0.958 | 0.963 | 0.966 |
| 8 | 0.954 | 0.943 | 0.947 | 0.944 | 0.952 |
| 16 | 0.922 | 0.919 | 0.906 | 0.904 | 0.922 (MPI=64 OMP=2) |
| 32 | 0.902 | 0.886 | 0.882 | 0.875 | 0.888 |
| 64 | 0.822 | 0.805 | 0.776 | 0.737 | 0.739 (MPI=64 OMP=2) |


## Weak scaling evolution

![Weak scaling](../results/images/weak_scaling_sedov_total_meluxina.png)

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | resolution | 2024-10 | 2025-05 | 2025-10 | 2026-05 | openmp (beta) |
|---|---|---|---|---|---|---|
| 1 | 256 | 1.000  | 1.000  | 1.000  | 1.000  | 1.000 (MPI=8 OMP=16) |
| 8 | 512 | 0.903  | 0.962  | 0.998  | 0.950  | 0.963 (MPI=32 OMP=4) |
| 64 | 1024 | 0.941  | 0.917  | 0.915  | 0.849  | 0.821 (MPI=64 OMP=2) |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit e9846974 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_sedov_256_total_meluxina.png)
![MPI-OMP](../results/images/mpi_omp_grid_sedov_512_total_meluxina.png)
![MPI-OMP](../results/images/mpi_omp_grid_sedov_1024_total_meluxina.png)
## Memory usage

![Memory usage](../results/images/memory_sedov_1024_meluxina.png)

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

| nodes | MPI-only | OMP=2 | OMP=4 | OMP=8 | OMP=16 | OMP=32 | OMP=64 | best |
|---|---|---|---|---|---|---|---|---|
| 1 | 207.74 GB | 198.98 GB | 195.07 GB | 192.91 GB | 191.70 GB | 191.00 GB | 190.53 GB | 91.7 % |
| 2 | 116.62 GB | 104.51 GB | 99.71 GB | 97.66 GB | 96.85 GB | - | - | 83.0 % |
| 4 | 67.35 GB | 58.27 GB | 52.29 GB | 50.02 GB | 49.22 GB | - | - | 73.1 % |
| 8 | 43.55 GB | 33.82 GB | 29.07 GB | 26.29 GB | 25.02 GB | - | - | 57.4 % |
| 16 | 32.88 GB | 21.89 GB | 16.86 GB | 14.63 GB | 13.13 GB | - | - | 39.9 % |
| 32 | 29.59 GB | 16.56 GB | 10.94 GB | 8.51 GB | 7.34 GB | - | - | 24.8 % |
| 64 | 33.18 GB | 14.89 GB | 8.25 GB | 5.50 GB | 4.29 GB | - | - | 12.9 % |


