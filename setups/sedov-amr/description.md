## Sedov blast wave on a uniform grid benchmark

Benchmark type: Classical, Sedov

![Sedov-Taylor blast wave with AMR](sedov.png)

### Description of the setup
See [sedov](../sedov/description.md)


### This variation: AMR

In this variation, we enable adaptive mesh refinement. The mesh is refined using a pressure gradient criterion. For this setup, we want to reach a specified final output time instead of running a fixed number of time steps. The target time is 10^-2 (code units).

### Other versions

* [sedov](../sedov/description.md)
