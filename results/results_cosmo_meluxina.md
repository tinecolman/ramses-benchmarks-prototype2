# Benchmark: cosmo on meluxina

Benchmark description: [cosmo](../setups/cosmo/description.md)

Cluster info: [meluxina](../HPCclusters/meluxina/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_cosmo_1024_total_meluxina.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 299.39 | 269.43 | 268.47 | 10.3 |
| 2 | 153.43 | 137.75 | 138.15 | 10.0 |
| 4 | 76.45 | 69.02 | 68.98 | 9.8 |
| 8 | 39.50 | 35.41 | 35.67 | 9.7 |
| 16 | 20.41 | 18.17 | 18.07 (MPI=32 OMP=4) | 11.5 |
| 32 | 11.71 | 9.59 | 9.23 (MPI=32 OMP=4) | 21.2 |
| 64 | 8.08 | 7.18 | 5.27 (MPI=32 OMP=4) | 34.8 |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_cosmo_1024_total_meluxina.png)

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
| 2 | 0.976 | 0.978 | 0.972 |
| 4 | 0.979 | 0.976 | 0.973 |
| 8 | 0.947 | 0.951 | 0.941 |
| 16 | 0.917 | 0.927 | 0.929 (MPI=32 OMP=4) |
| 32 | 0.799 | 0.878 | 0.909 (MPI=32 OMP=4) |
| 64 | 0.579 | 0.587 | 0.796 (MPI=32 OMP=4) |


## Weak scaling evolution

![Weak scaling](../results/images/weak_scaling_cosmo_total_meluxina.png)

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | resolution | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|---|
| 1 | 256 | - | 1.000  | 1.000  |
| 8 | 512 | - | 0.894  | 0.919  |
| 64 | 1024 | 1.000  | 0.559  | 0.760 (MPI=32 OMP=4) |


## Strong and weak scaling of the latest code release (2026-05)

![Scaling](../results/images/scaling_combo_cosmo_total_meluxina.png)

This figure shows the strong and weak scaling of the latest official release (2026-05).
Strong scaling can be inferred diagonally, while weak scaling is determined by reading horizontally.
Dotted lines show ideal scaling.
For the values of strong and weak scaling efficiency, see the tables in the previous sections.

## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit e9846974 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_cosmo_256_total_meluxina.png)
![MPI-OMP](../results/images/mpi_omp_grid_cosmo_1024_total_meluxina.png)
## Memory usage

![Memory usage](../results/images/memory_cosmo_1024_meluxina.png)

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
| 1 | 263.04 GB | 259.52 GB | 254.46 GB | 251.07 GB | 95.5 % |
| 2 | 146.69 GB | 137.22 GB | 130.85 GB | 127.82 GB | 87.1 % |
| 4 | 86.64 GB | 75.46 GB | 68.35 GB | 65.50 GB | 75.6 % |
| 8 | 56.79 GB | 44.17 GB | 37.60 GB | 34.42 GB | 60.6 % |
| 16 | 43.34 GB | 29.55 GB | 23.45 GB | 18.88 GB | 43.6 % |
| 32 | 114.43 GB | 22.21 GB | 15.09 GB | 11.36 GB | 9.9 % |
| 64 | 47.26 GB | 21.23 GB | 11.24 GB | 7.98 GB | 16.9 % |


