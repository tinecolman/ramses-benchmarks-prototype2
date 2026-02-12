## AGORA Galaxy benchmark

This benchmark models the evolution of an isolated Milky Way-mass galaxy embedded in a dark matter halo. As part of the [AGORA code comparison project](https://sites.google.com/site/santacruzcomparisonproject/), this setup was studied in their [paper II](https://ui.adsabs.harvard.edu/abs/2016ApJ...833..202K/abstract). 


### Scientific relevance
Isolated galaxy setups are widely used to study galaxy-scale physics in a controlled environment, without the complications of cosmological accretion or mergers.

### Benchmark focus
For this benchmark, the simulation is evolved for a limited number of coarse timesteps with simplified thermochemistry and no star formation or feedback, to ensure reproducibility and to focus on numerical performance rather than detailed galaxy evolution physics.. Adaptive mesh refinement is driven by a quasi-Lagrangian mass criterion (and a Jeans-length condition), resulting in strong refinement in the dense galactic disk while the low-density halo remains coarse. As a consequence, most of the computational work is concentrated in a small fraction of the domain, making this setup particularly demanding for **load balancing, domain decomposition, and AMR communication**. 

### Modules benchmarked
* hydrodynamics
* self-gravity
* particles
* AMR
* load balancing
* communication


### How to generate the initial conditions

The initial conditions are generated with MAKEDISK, originally written by Volker Springel and adapted to make ICs readable for RAMSES (see [Rosdahl et al. 2015](https://ui.adsabs.harvard.edu/abs/2015MNRAS.451...34R/abstract)). The IC generation code is written in C and is part of the public version of the RAMSES code (under ramses/utils/ic/galaxy ic/galics). 
  
The setup consists of a dark matter halo with an NFW density profile (Navarro et al. 1997) in which the galaxy is embedded and the galaxy itself which is composed of an exponential disk of stars and gas, and a stellar bulge with a Hernquist (1990) profile. The total mass of the system is divided amongst its components as follows (set in the IC generator):
* bulge mass fraction = 0.004
* disk mass fraction = 0.04
* gas fraction in the disk $f_\mathrm{gas}=0.2$

Further properties that either need to be set, or are calculated by the IC code, are
* Dark matter halo
   * rotational velocity $v_{c,200} = 150$ km/s
   * virial mass $M_{200} = v_{c,200}^{3} / (10 G H_0) = 1.074 \times 10^{12}$ Msun (calculated)
   * virial radius $R_{200} = 205.5$ kpc (calculated)
   * concentration $c = 10$
   * spin $\lambda = 0.04$
* Stellar disk
   * disk stellar mass $M_{d,*} = 3.438 \times 10^{10}$ Msun (calculated)
   * scale radius $r_d = 3.43$ kpc (calculated)
   * scale height $z_d = 0.1 r_d$
* gass disk
   * disk gas mass $M_{d,g} = 8.593 \times 10^{9}$ Msun (calculated)
* Stellar bulge
   * mass $M_{b,*} = 4.297 \times 10^{9}$ Msun (calculated)
   * scale length $r_b = 0.1 r_d$




The box size of the compational domain is set to 400 kpc. The resolution and computational cost is defined by a combination of the number of particles for each component (dark matter -- DM, stellar disk -- SD, stellar bulge -- SB) and the resolution of the grid as set by the minimum and maximum refinement level (ℓ_min and ℓ_max). We specify three setups:

| Parameter | Low resolution | Medium resolution | High resolution |
|----------|----------------|-------------------|-----------------|
| N_DM      | 1.25 × 10⁵     | 10⁶               | 8 × 10⁶         |
| N_SD      | 1.25 × 10⁵     | 10⁶               | 8 × 10⁶         |
| N_SB      | 1.25 × 10⁴     | 10⁵               | 8 × 10⁵         |
| ℓ_min     | 7              | 8                 | 9               |
| ℓ_max     | 12             | 13                | 14              |
| Δx_max   | 3125 pc        | 1562 pc           | 781 pc          |
| Δx_min   | 98 pc          | 49 pc             | 24.5 pc         |

