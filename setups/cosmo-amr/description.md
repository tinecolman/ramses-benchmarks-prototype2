## Dark matter-only cosmological simulation, with refinement

Benchmark type: Cosmological, DM-only

TODO image

### Description of the setup
See [cosmo](../cosmo/description.md)


### Generating initial conditions
See [cosmo](../cosmo/description.md)


### This variation: AMR

In this variation, we enable adaptive mesh refinement. The mesh is refined using a mass refinement criterion, for level 8 to level 12. For this setup, we want to reach a specified final output time instead of running a fixed number of time steps. The target expansion factor is a=0.09 (code units).

The majority of the time is distributed between following modules:


### Other versions

* [cosmo](../cosmo/description.md)


### Benchmark results

This setup has been benchmarked on the following clusters:



### OpenMP configuration guidelines

