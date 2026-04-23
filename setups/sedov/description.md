## Sedov blast wave benchmark

### Description of the setup
This test is a standard hydrodynamical test used for verification and benchmarking of gas dynamic codes. We run this test in 3D. 
The physical setup consists of a uniform density ($\rho=$ 1) and low-pressure ($P = 10^{-5}$) medium at rest (zero velocity) in which an internal energy pulse of amplitude 0.4 is put in the corners of the computational domain in order to check the good behaviour of the periodic boundary conditions.
The box size is 0.5.
The internal energy is progressively converted into kinetic energy, while the total energy is conserved. This test is purely hydrodynamical (no gravity).


### Default version, using uniform grid (SPACE)
The default version uses a uniform fixed grid, with resolutions ranging from 128^3 to 2048^3 grid cells. We integrate the code for a fixed number of 20 time steps.
It enables testing the performances of the hydrodynamical kernel and of the communication kernels of RAMSES without the overheads due to the adaptive mesh refinement. 
In addition, since this test has an analytic solution, it can also test the accuracy of the code. 

Here we use a uniform grid at level $l$ and the Lax-Friedrich Riemann solver. A unique load-balancing of the MPI domains is performed at the initialization of the run and no further load balancing is done during the simulation run.
In this use case, all time steps (or iterations) are equivalent in terms of computational cost.
Therefore, this scientific case is well-suited for memory-bound runs. In summary, this test provides an ideal environment to optimize the communications between MPI domains and we can conduct both strong and weak scaling studies.

### AMR version

In this variation, we enable adaptive mesh refinement. For this setup we want to reach a specified final output time, instead of simply running a fixed number of time steps. The target time is 10^-2 (code units).

![Sedov-Taylor blast wave at two different times](../sedov-amr/sedov.png)