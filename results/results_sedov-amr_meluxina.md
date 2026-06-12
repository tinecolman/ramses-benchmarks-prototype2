# Benchmark: sedov-amr on meluxina

Benchmark description: [sedov-amr](../setups/sedov-amr/description.md)

Cluster info: [meluxina](../HPCclusters/meluxina/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_sedov-amr_lvl5-10_total_meluxina.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 149.19 | 136.34 | 102.96 (MPI=32 OMP=4) | 31.0 |
| 2 | 124.12 | 114.52 | 72.13 (MPI=16 OMP=8) | 41.9 |
| 4 | 130.04 | 125.38 | 56.51 (MPI=16 OMP=8) | 56.5 |
| 8 | - | - | 57.44 (MPI=16 OMP=8) | - |
| 16 | - | - | 73.87 (MPI=16 OMP=8) | - |
| 32 | - | - | 119.95 (MPI=16 OMP=8) | - |
| 64 | - | - | - | - |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_sedov-amr_lvl5-10_total_meluxina.png)

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 (MPI=32 OMP=4) |
| 2 | 0.601 | 0.595 | 0.714 (MPI=16 OMP=8) |
| 4 | 0.287 | 0.272 | 0.455 (MPI=16 OMP=8) |
| 8 | - | - | 0.224 (MPI=16 OMP=8) |
| 16 | - | - | 0.087 (MPI=16 OMP=8) |
| 32 | - | - | 0.027 (MPI=16 OMP=8) |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit e9846974 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_sedov-amr_lvl5-10_total_meluxina.png)
## Memory usage

![Memory usage](../results/images/memory_sedov-amr_lvl5-10_meluxina.png)

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
| 1 | 53.88 GB | 21.83 GB | 12.54 GB | 9.41 GB | 17.5 % |
| 2 | 60.45 GB | 20.37 GB | 9.51 GB | 6.01 GB | 9.9 % |
| 4 | 67.75 GB | 22.73 GB | 8.07 GB | 4.39 GB | 6.5 % |
| 8 | - | 22.41 GB | 8.58 GB | 4.04 GB | - |
| 16 | - | - | 8.24 GB | 3.74 GB | - |
| 32 | - | - | - | 3.47 GB | - |


