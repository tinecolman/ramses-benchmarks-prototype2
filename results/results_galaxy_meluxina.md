# Benchmark: galaxy on meluxina

Benchmark description: [galaxy](../setups/galaxy/description.md)

Cluster info: [meluxina](../HPCclusters/meluxina/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

## Evolution of execution time with code version

![Evolution execution time](../results/images/evo_exectime_galaxy_highres_total_meluxina.png)

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) | Δ [%] |
|---|---|---|---|---|
| 1 | 506.99 | 425.20 | 231.83 (MPI=8 OMP=16) | 54.3 |
| 2 | 272.63 | 226.39 | 180.51 (MPI=4 OMP=32) | 33.8 |
| 4 | 160.83 | 134.10 | 130.33 (MPI=64 OMP=2) | 19.0 |
| 8 | 104.02 | 87.72 | 76.25 (MPI=32 OMP=4) | 26.7 |
| 16 | 80.90 | 72.45 | 50.60 (MPI=32 OMP=4) | 37.5 |
| 32 | 86.88 | 82.58 | 40.76 (MPI=32 OMP=4) | 53.1 |
| 64 | - | - | 45.25 (MPI=32 OMP=4) | - |


## Strong scaling evolution

![Strong scaling](../results/images/strong_scaling_galaxy_highres_total_meluxina.png)

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

| nodes | 2024-10 | 2026-05 | openmp (beta) |
|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 (MPI=8 OMP=16) |
| 2 | 0.930 | 0.939 | 0.642 (MPI=4 OMP=32) |
| 4 | 0.788 | 0.793 | 0.445 (MPI=64 OMP=2) |
| 8 | 0.609 | 0.606 | 0.380 (MPI=32 OMP=4) |
| 16 | 0.392 | 0.367 | 0.286 (MPI=32 OMP=4) |
| 32 | 0.182 | 0.161 | 0.178 (MPI=32 OMP=4) |
| 64 | - | - | 0.080 (MPI=32 OMP=4) |


## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit 2e39ba97 on branch openmp)
, corresponding to the version used for the previous figures.

![MPI-OMP](../results/images/mpi_omp_grid_galaxy_mediumres_total_meluxina.png)
![MPI-OMP](../results/images/mpi_omp_grid_galaxy_highres_total_meluxina.png)
## Memory usage

![Memory usage](../results/images/memory_galaxy_highres_meluxina.png)

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
| 1 | 497.41 GB | 371.39 GB | 303.30 GB | 269.14 GB | 252.15 GB | 243.91 GB | - | 49.0 % |
| 2 | 379.39 GB | 254.91 GB | 185.54 GB | 152.03 GB | 134.74 GB | 126.39 GB | 122.14 GB | 32.2 % |
| 4 | 320.64 GB | 194.75 GB | 127.10 GB | 92.74 GB | 76.09 GB | 67.64 GB | - | 21.1 % |
| 8 | 292.86 GB | 165.76 GB | 98.05 GB | 63.54 GB | 46.84 GB | 38.24 GB | 34.00 GB | 11.6 % |
| 16 | 284.93 GB | 152.58 GB | 82.50 GB | 48.90 GB | 32.08 GB | - | - | 11.3 % |
| 32 | 289.15 GB | 148.86 GB | 77.66 GB | 41.54 GB | - | - | - | 14.4 % |
| 64 | - | 148.54 GB | 73.31 GB | 37.89 GB | - | - | - | - |


