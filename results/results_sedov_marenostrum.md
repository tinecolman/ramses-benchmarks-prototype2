# Benchmark: sedov on marenostrum

Benchmark description: [sedov](../setups/sedov/description.md)

Cluster info: [marenostrum](../HPCclusters/marenostrum/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_sedov_1024_total_marenostrum.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 128.42 | 102.38 | 99.58 (MPI=16 OMP=7) | 22.5 |
| 2 | 69.34 | 53.81 | 49.36 (MPI=16 OMP=7) | 28.8 |
| 4 | 34.39 | 27.35 | 24.97 (MPI=16 OMP=7) | 27.4 |
| 8 | 18.10 | 14.63 | 12.66 (MPI=16 OMP=7) | 30.1 |
| 16 | 9.00 | 7.26 | 6.38 (MPI=16 OMP=7) | 29.1 |
| 32 | 4.60 | 3.89 | 3.27 (MPI=8 OMP=14) | 28.9 |
| 64 | 2.60 | 2.06 | 1.67 (MPI=16 OMP=7) | 35.7 |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_sedov_1024_total_marenostrum.png)

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 (MPI=16 OMP=7) |
| 2 | 0.926 | 0.951 | 1.009 (MPI=16 OMP=7) |
| 4 | 0.934 | 0.936 | 0.997 (MPI=16 OMP=7) |
| 8 | 0.887 | 0.875 | 0.984 (MPI=16 OMP=7) |
| 16 | 0.892 | 0.881 | 0.976 (MPI=16 OMP=7) |
| 32 | 0.873 | 0.822 | 0.952 (MPI=8 OMP=14) |
| 64 | 0.771 | 0.775 | 0.930 (MPI=16 OMP=7) |


## Weak scaling evolution

![Weak scaling](../results/images/weak_scaling_sedov_total_marenostrum.png)

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | resolution | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|---|
| 1 | 256 | 1.000  | 1.000  | 1.000 (MPI=16 OMP=7) |
| 8 | 512 | 0.989  | 1.054  | 0.935 (MPI=16 OMP=7) |
| 64 | 1024 | 0.872  | 0.879  | 0.885 (MPI=16 OMP=7) |


## Strong and weak scaling of the latest code release (2026-05)

![Scaling](../results/images/scaling_combo_sedov_total_marenostrum.png)

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

![MPI-OMP](../results/images/mpi_omp_grid_sedov_256_total_marenostrum.png)
![MPI-OMP](../results/images/mpi_omp_grid_sedov_512_total_marenostrum.png)
![MPI-OMP](../results/images/mpi_omp_grid_sedov_1024_total_marenostrum.png)
![OMP-speedup](../results/images/omp_speedup_sedov_1024_marenostrum.png)
## Memory usage

![Memory usage](../results/images/memory_sedov_1024_marenostrum.png)

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

| nodes | MPI-only | OMP=2 | OMP=4 | OMP=7 | OMP=8 | OMP=14 | OMP=16 | OMP=28 | OMP=56 | best |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 291.09 GB | 225.34 GB | 203.87 GB | 195.98 GB | 195.48 GB | 192.56 GB | 192.56 GB | 191.34 GB | 190.66 GB | 65.5 % |
| 2 | 188.94 GB | 129.42 GB | 107.41 GB | 100.18 GB | 100.18 GB | 97.60 GB | 97.38 GB | 96.26 GB | 95.71 GB | 50.7 % |
| 4 | 115.25 GB | 80.75 GB | 59.19 GB | 51.74 GB | 52.07 GB | 49.75 GB | 49.61 GB | 48.71 GB | 48.18 GB | 41.8 % |
| 8 | 75.59 GB | 49.03 GB | 35.48 GB | 28.70 GB | 28.10 GB | 25.74 GB | 25.58 GB | 24.78 GB | 24.39 GB | 32.3 % |
| 16 | 51.05 GB | - | - | 16.77 GB | - | 13.82 GB | - | 12.86 GB | 12.45 GB | 24.4 % |
| 32 | 40.38 GB | - | - | 9.29 GB | - | 8.19 GB | - | 6.94 GB | 6.49 GB | 16.1 % |
| 64 | 45.93 GB | - | - | 6.25 GB | - | 4.53 GB | - | 4.06 GB | 3.54 GB | 7.7 % |


