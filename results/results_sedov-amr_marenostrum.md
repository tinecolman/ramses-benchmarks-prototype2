# Benchmark: sedov-amr on marenostrum

Benchmark description: [sedov-amr](../setups/sedov-amr/description.md)

Cluster info: [marenostrum](../HPCclusters/marenostrum/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_sedov-amr_lvl5-10_total_marenostrum.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 130.37 | 119.82 | 89.56 (MPI=8 OMP=14) | 31.3 |
| 2 | 133.62 | 122.96 | 58.96 (MPI=8 OMP=14) | 55.9 |
| 4 | 165.02 | 161.75 | 44.00 (MPI=8 OMP=14) | 73.3 |
| 8 | - | - | - | - |
| 16 | - | - | - | - |
| 32 | - | - | - | - |
| 64 | - | - | - | - |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_sedov-amr_lvl5-10_total_marenostrum.png)

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 (MPI=8 OMP=14) |
| 2 | 0.488 | 0.487 | 0.759 (MPI=8 OMP=14) |
| 4 | 0.198 | 0.185 | 0.509 (MPI=8 OMP=14) |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit e9846974 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_sedov-amr_lvl5-10_total_marenostrum.png)
## Memory usage

![Memory usage](../results/images/memory_sedov-amr_lvl5-10_marenostrum.png)

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
| 1 | 44.99 GB | 23.67 GB | 14.58 GB | 11.00 GB | 10.35 GB | 8.50 GB | 8.46 GB | 7.82 GB | 7.43 GB | 16.5 % |
| 2 | 40.59 GB | 18.75 GB | 10.25 GB | 7.37 GB | 6.80 GB | 5.37 GB | 5.08 GB | 4.29 GB | 3.98 GB | 9.8 % |
| 4 | 33.57 GB | 18.74 GB | 8.50 GB | 5.24 GB | 4.82 GB | 3.59 GB | 3.31 GB | 2.70 GB | - | 8.1 % |


