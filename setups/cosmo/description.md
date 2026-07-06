## Dark matter-only cosmological simulation, on a uniform grid

Benchmark type: Cosmological, DM-only

TODO image

### Description of the setup

TODO

Timers:
* `poisson`:
* `particles`:
* `rho`:

### Generating initial conditions

TODO

### This variation: uniform grid

### Other versions

* [cosmo-amr](../cosmo-amr/description.md)

### Benchmark results

This setup has been benchmarked on the following clusters:



### OpenMP configuration guidelines

It is not worth running this setup with OpenMP for a low number of nodes.
The main module, the poisson multigrid solver, performs similary with or without MPI upto about 16 nodes.
The module rho, which performs the CIC, is slower with openMP due to the necesity of atomic operations when depositing the mass of particles on the grid.
The routines that deal with particle book-keeping (make tree, synchro and move) also become slower when using many openMP threads.

For a high number of MPI processes, the scaling of the poisson multigrid solver breaks down.
Here, using OpenMP gives significant speedups and 
