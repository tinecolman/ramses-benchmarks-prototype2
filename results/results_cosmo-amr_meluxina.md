# Benchmark: cosmo-amr on meluxina

Benchmark description: [cosmo-amr](../setups/cosmo-amr/description.md)

Cluster info: [meluxina](../HPCclusters/meluxina/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_cosmo-amr_lvl8-12_total_meluxina.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 345.94 | 262.53 | 243.59 (MPI=32 OMP=4) | 29.6 |
| 2 | 212.77 | 165.12 | 147.29 (MPI=32 OMP=4) | 30.8 |
| 4 | 148.72 | 119.89 | 98.18 (MPI=32 OMP=4) | 34.0 |
| 8 | 129.32 | 112.20 | 75.40 (MPI=32 OMP=4) | 41.7 |
| 16 | 161.32 | 148.70 | 71.52 (MPI=32 OMP=4) | 55.7 |
| 32 | - | - | - | - |
| 64 | - | - | - | - |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_cosmo-amr_lvl8-12_total_meluxina.png)

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
| 2 | 0.813 | 0.795 | 0.827 (MPI=32 OMP=4) |
| 4 | 0.582 | 0.547 | 0.620 (MPI=32 OMP=4) |
| 8 | 0.334 | 0.292 | 0.404 (MPI=32 OMP=4) |
| 16 | 0.134 | 0.110 | 0.213 (MPI=32 OMP=4) |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit e9846974 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_cosmo-amr_lvl8-12_total_meluxina.png)
![OMP-speedup](../results/images/omp_speedup_cosmo-amr_lvl8-12_meluxina.png)
## Memory usage

![Memory usage](../results/images/memory_cosmo-amr_lvl8-12_meluxina.png)

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
| 1 | 79.50 GB | 58.32 GB | 48.32 GB | 44.82 GB | 43.45 GB | 42.88 GB | 42.51 GB | 53.5 % |
| 2 | 58.23 GB | 37.25 GB | 28.07 GB | 23.94 GB | - | - | - | 41.1 % |
| 4 | 48.41 GB | 26.44 GB | 17.67 GB | 13.82 GB | - | - | - | 28.5 % |
| 8 | 45.25 GB | 21.36 GB | 11.86 GB | 8.45 GB | - | - | - | 18.7 % |
| 16 | 46.16 GB | 19.13 GB | 9.26 GB | 6.08 GB | - | - | - | 13.2 % |


