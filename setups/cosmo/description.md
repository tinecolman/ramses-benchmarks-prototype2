## Dark matter-only cosmological simulation, on a uniform grid

Benchmark type: Cosmological, DM-only

![2D dark matter density projections](cosmo_dm_projection.png)

*2D dark matter density projections: 128^3 after 100 steps (left), 128^3 after 200 steps (middle), 256^3 after 100 steps (right).*

### Description of the setup
Cosmological boxes help us understand and interpret large cosmological surveys and the evolution of structure in the Universe.
They are the largest simulations run with RAMSES and are typically "flagship" simulations.
These runs already use a few tens of thousands of cores and still take months to finish.
Good scaling is therefore needed to reach higher resolution in current-size volumes, larger volumes at current resolution, and shorter wall times in both cases.
Cosmological boxes scale relatively well with the number of cores, because the volume divides naturally into galaxies and their host dark matter halos.

A cosmological volume is a statistically accurate description of a patch of the Universe, in terms of the number density of dark matter halos and their spatial and mass distribution.
Two ingredients make this possible: realistic gravitational dynamics of dark matter (to first order), and initial conditions that are statistically identical to the observed power spectrum of density and temperature fluctuations in the cosmic microwave background.
Together, these lead to the collapse of matter into the so-called cosmic web.

The simulation starts at redshift z = 150, a few tens of millions of years after the Big Bang, when the Universe has almost no structure.
A production run would continue for more than 13 billion years, up to the present epoch.
This is far too expensive for a scaling test, so the benchmark runs only the first 10 coarse time steps.

The setup contains only dark matter particles: there is no hydrodynamics, gas cooling or star formation.
Additional physics makes exact comparisons between resolutions difficult.
For example, stars may form at different times and rates depending on the resolution, which makes the amount of computation uneven between runs.
Also, during the first few time steps there is not enough time for structures to form, so non-DM physics would remain negligible anyway.
The benchmark therefore tests the particle-in-cell (PIC) algorithm, gravity, load balancing and domain communication overheads.

Timers:
* `poisson - phi multigrid`: the multigrid solver for the gravitational potential
* `poisson - rho`: deposition of the particle mass onto the grid with Cloud-In-Cell (CIC) interpolation
* `particles - move` and `- synchro`, : particle trajectory integration
* `particles - make tree`, `- merge tree`, `- kill tree`: particle book-keeping

This benchmark corresponds to use-case 2 in the SPACE project.

### Generating initial conditions

The initial conditions are generated with the publicly available [MUSIC](https://www-n.oca.eu/ohahn/MUSIC/) software package, which is commonly used for most cosmological codes.
MUSIC takes as parameters:
* the comoving width of the cubic volume, L_box
* the number of DM particles per dimension, N_part, so that the total number of particles and coarse-grid cells is N_part^3
* the cosmological parameters
* a random seed for the generation of the density fluctuations. Changing only the seed produces different "instances" of a Universe with the same cosmological properties.

All resolutions use the same box size, cosmology and seed:

| N_part | L_box | z_start | Ω_m | Ω_Λ | H_0 | σ_8 | seed |
|---|---|---|---|---|---|---|---|
| 128, 256, 512, 1024, 2048 | 20 cMpc | 150 | 0.3175 | 0.6825 | 67.11 km s^-1 Mpc^-1 | 0.83 | 4721 |

The initial conditions are written in the `grafic` format, and the namelists expect them in `ICs/cosmo_<N_part>/`.

### This variation: uniform grid

In this default version of the cosmological benchmark, adaptive mesh refinement is not triggered (`levelmin` = `levelmax`), so the grid stays uniform.
Namelists are provided for 256^3 (`levelmin=8`), 512^3 (`levelmin=9`) and 1024^3 (`levelmin=10`) particles and cells.

Every run uses the same L_box and the same initial conditions.
A factor 2 increase in N_part therefore multiplies the number of particles and cells by 8.
We expect it to cover the same number of time steps with 8 times the computational load, which makes the setup suitable for both strong and weak scaling studies.

### Other versions

* [cosmo-amr](../cosmo-amr/description.md)


### OpenMP configuration guidelines

On a low number of nodes (1 - 8), this setup may be slightly slower with OpenMP.
The main module, the Poisson multigrid solver, performs similarly with or without OpenMP up to about 16 nodes.
The module `rho`, which performs the CIC deposition, is slower with OpenMP because depositing the particle mass on the grid requires atomic operations.
The routines that deal with particle also become slower when using many OpenMP threads.

For a high number of MPI processes, the scaling of the Poisson multigrid solver breaks down.
Here, using OpenMP gives significant speedups and improves the strong scaling efficiency.
For example, on MeluXina at 64 nodes, 32 MPI ranks × 4 OpenMP threads per node is 27% faster than MPI-only (5.27 s vs 7.18 s).
