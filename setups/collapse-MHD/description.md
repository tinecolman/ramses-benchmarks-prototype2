## Collapse

This setup models an idealised collapsing core which forms a single protostar in the center. An analytical equation of state is used to mimic the temperature increase due to the gas becoming optically thick for its own radiation at a specific density. This creates the first Larson core, a clearly defined round structure in hydrostatic equilibrium. As the density in the center increases further, the temperature for hydrogren dissociation is reached, slowing down the heating of the core. This causes a second collapse, in which the second Larson core, the actual protostar, is formed.


This type of simulation uses a very deep AMR grid. This is particulary challenging for the gravity solver, which prefers large regions with uniform refinement. It alos presents challenges in load balancing, once symmetry breaks due to the generatation of spiral structures through gravitational instability.