# Benchmark: cosmo-amr on marenostrum

Benchmark description: [cosmo-amr](../setups/cosmo-amr/description.md)

Cluster info: [marenostrum](../HPCclusters/marenostrum/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_cosmo-amr_lvl8-12_total_marenostrum.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 289.01 | 210.70 | 210.04 | 27.3 |
| 2 | 180.75 | 134.29 | - | - |
| 4 | 141.35 | 115.67 | - | - |
| 8 | 125.70 | 113.13 | - | - |
| 16 | 145.39 | 140.33 | - | - |
| 32 | - | - | - | - |
| 64 | - | - | - | - |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_cosmo-amr_lvl8-12_total_marenostrum.png)

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
| 2 | 0.799 | 0.784 | - |
| 4 | 0.511 | 0.455 | - |
| 8 | 0.287 | 0.233 | - |
| 16 | 0.124 | 0.094 | - |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit 2e39ba97 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_cosmo-amr_lvl8-12_total_marenostrum.png)
## Memory usage

![Memory usage](../results/images/memory_cosmo-amr_lvl8-12_marenostrum.png)

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
| 1 | 100.37 GB | 66.25 GB | 52.61 GB | 47.47 GB | 46.86 GB | 44.67 GB | 44.43 GB | 43.42 GB | 42.64 GB | 42.5 % |


