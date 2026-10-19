# Benchmark: cosmo on marenostrum

Benchmark description: [cosmo](../setups/cosmo/description.md)

Cluster info: [marenostrum](../HPCclusters/marenostrum/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_cosmo_1024_total_marenostrum.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 245.84 | 223.57 | 222.18 | 9.6 |
| 2 | 132.86 | 121.82 | 118.46 (MPI=16 OMP=7) | 10.8 |
| 4 | 72.77 | 65.59 | 59.01 (MPI=16 OMP=7) | 18.9 |
| 8 | 37.29 | 33.48 | 29.56 (MPI=16 OMP=7) | 20.7 |
| 16 | 19.08 | 17.28 | 14.89 (MPI=16 OMP=7) | 21.9 |
| 32 | 10.62 | 9.66 | 8.09 (MPI=16 OMP=7) | 23.8 |
| 64 | 8.43 | 8.34 | 4.78 (MPI=16 OMP=7) | 43.4 |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_cosmo_1024_total_marenostrum.png)

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
| 2 | 0.925 | 0.918 | 0.938 (MPI=16 OMP=7) |
| 4 | 0.845 | 0.852 | 0.941 (MPI=16 OMP=7) |
| 8 | 0.824 | 0.835 | 0.939 (MPI=16 OMP=7) |
| 16 | 0.806 | 0.809 | 0.932 (MPI=16 OMP=7) |
| 32 | 0.723 | 0.723 | 0.858 (MPI=16 OMP=7) |
| 64 | 0.456 | 0.419 | 0.727 (MPI=16 OMP=7) |
| 128 | - | - | 0.544 (MPI=16 OMP=7) |


## Weak scaling evolution

![Weak scaling](../results/images/weak_scaling_cosmo_total_marenostrum.png)

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | resolution | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|---|
| 1 | 256 | - | 1.000  | 1.000  |
| 8 | 512 | - | 0.674  | 0.784 (MPI=16 OMP=7) |
| 64 | 1024 | 1.000  | 0.346  | 0.598 (MPI=16 OMP=7) |


## Strong and weak scaling of the latest code release (2026-05)

![Scaling](../results/images/scaling_combo_cosmo_total_marenostrum.png)

This figure shows the strong and weak scaling of the latest official release (2026-05).
Strong scaling can be inferred diagonally, while weak scaling is determined by reading horizontally.
Dotted lines show ideal scaling.
For the values of strong and weak scaling efficiency, see the tables in the previous sections.

## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit f5b7b39b on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_cosmo_256_total_marenostrum.png)
![MPI-OMP](../results/images/mpi_omp_grid_cosmo_512_total_marenostrum.png)
![MPI-OMP](../results/images/mpi_omp_grid_cosmo_1024_total_marenostrum.png)
![OMP-speedup](../results/images/omp_speedup_cosmo_1024_marenostrum.png)
## Memory usage

![Memory usage](../results/images/memory_cosmo_1024_marenostrum.png)

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

| nodes | MPI-only | OMP=2 | OMP=4 | OMP=7 | OMP=8 | OMP=14 | OMP=16 | OMP=28 | best |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 374.86 GB | 290.14 GB | 263.73 GB | 254.54 GB | 253.89 GB | 249.30 GB | 249.32 GB | 247.48 GB | 66.0 % |
| 2 | 251.33 GB | 165.82 GB | 138.24 GB | 130.58 GB | 129.92 GB | 126.73 GB | 126.50 GB | 124.44 GB | 49.5 % |
| 4 | 163.86 GB | 102.98 GB | 76.36 GB | 67.14 GB | 67.31 GB | 64.52 GB | 64.36 GB | 63.13 GB | 38.5 % |
| 8 | 128.69 GB | 62.66 GB | 45.16 GB | 37.23 GB | 36.48 GB | 33.16 GB | 33.10 GB | 32.06 GB | 24.9 % |
| 16 | 114.51 GB | 40.20 GB | 26.59 GB | 21.41 GB | 20.92 GB | 18.12 GB | 17.77 GB | 16.50 GB | 14.4 % |
| 32 | 111.26 GB | - | - | 11.70 GB | - | - | - | - | 10.5 % |
| 64 | 114.06 GB | - | - | 7.68 GB | - | - | - | - | 6.7 % |
| 128 | 128.80 GB | - | - | 5.49 GB | - | - | - | - | 4.3 % |


