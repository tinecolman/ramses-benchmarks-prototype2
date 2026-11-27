# Adding a new benchmark setup

Each benchmark setup is defined by a folder in `setups/`. The folder name is the name used with
`-b` and in the name of the results folders, e.g. `sedov` or `cosmo-amr`. It should not contain `_`.
Variations of a setup get their own folder, e.g. `sedov` (uniform grid) and `sedov-amr`.

A setup folder contains:
- `description.md`: a description of the setup and which parts of the code it benchmarks.
- `config.txt`: the compilation parameters, same format as for the test suite.
- `<setup>_<resolution>.nml`: the RAMSES namelist, one per resolution
- `scaling_config.sh`: some additional run parameters, i.e. time limit, grid allocation and memory estimate.

Below we provide more details for each of these files. For examples, look into the existing setups in this repository.

After adding the new setup, test it in a variety of configurations..

## description.md

This file contains a short description of the setup. Describe what is being simulated and list the scientific or numerical purpose. List whether there are variations, and what this variation studies specifically.

Lists which RAMSES modules are used and where most of the time is spend, as shown by the RAMSES timers outputted at the end of the log or in individual outputs. If known, comment on the behaviour with OpenMP.

To register your setup, add a link to this description file in the list of setups on the `README.md` of this repository.


## config.txt

One line with the flags passed to `make` when compiling RAMSES, as for test cases:

```
FLAGS: NDIM=3 SOLVER=hydro NVECTOR=16
```

The launcher adds the compiler, MPI and OpenMP settings itself. A patch is given relative to the
`bin/` folder of RAMSES, e.g. `PATCH=../patch/hydro/merger`.

## Namelists

One namelist per resolution, named `<setup>_<resolution>.nml`. The resolution is the label used
with `-r` and in the run directory names, e.g. `sedov_1024.nml` for `-r 1024`.

- **Resolution labels:** for uniform grids, use the number of cells per dimension (`256`, `512`, `1024`). This makes configuration for weak scaling straighforward. Other examples could be `lowres` or `lvl8-12`, but these need interpretation before weak scaling can be measured.
  launching 
- **Fixed amount of work:** stop the run after a fixed number of steps (`nstepmax` in
  `&RUN_PARAMS`), so that every run does the same work. A benchmark run should last a few minutes.
- **No outputs:** set `foutput=0` in `&OUTPUT_PARAMS`, so that the time measures the computation and not the file system. This also avoid writing many big output files when doing many runs.
- **Grid allocation:** setting a general `ngridtot` or `ngridmax` that works for any number of nodes can be non-trivial. The benchmark launcher has been adapted to partially solve these issues by adapting the allocation per rank for runs with many ranks (see `ALLOC_GHOST_COEF` below). To use this, set `ngridtot` (and `nparttot`), the total over all MPI ranks, rather than `ngridmax`. A namelist that sets `ngridmax` is used as it is, whatever the number of ranks.
- **Initial conditions:** the run directory is `$CLUSTER_SCRATCH/<results folder>/<run dir>/`, and
  the namelist is read from there. Put the initial conditions in `$CLUSTER_SCRATCH/ICs/` on the
  cluster and refer to them relative to the run directory, e.g.
  `initfile(1)='../../ICs/cosmo_256/'`. The launcher does not copy them.

## scaling_config.sh

This file contains bash variables read by the launcher. For example:

```bash
TEST_TIME=00:15:00
ALLOC_GHOST_COEF=12

MEM_PER_GRID_KB=0.87
MEM_PER_PARTICLE_B=0
MEM_PER_RANK_GB=0.18
MEM_PER_RANK_IN_RUN_KB=12
```

| Variable | Mandatory | Meaning |
|---|---|---|
| `TEST_TIME` | yes | Time limit of the jobs (`hh:mm:ss`). Long enough for the slowest configuration (the smallest number of nodes at the largest resolution), with some margin. |
| `ALLOC_GHOST_COEF` | no | Enables the adaptation of the grid allocation per rank. `12` fits the uniform-grid sedov and cosmo setups. AMR setups have more complex domains and load imbalance; leave it out unless it has been determined for the setup. |
| `ALLOC_OCCUPANCY`, `ALLOC_TARGET` | no | Further parameters of that adaptation (defaults 0.7 and 0.8), see `launch_tools/ngridmax_tools.sh`. |
| `MEM_PER_GRID_KB` | no | Memory per allocated grid (kB). |
| `MEM_PER_PARTICLE_B` | no | Memory per allocated particle (bytes). |
| `MEM_PER_RANK_GB` | no | Fixed memory per MPI rank (GB). |
| `MEM_PER_RANK_IN_RUN_KB` | no | Memory per rank that grows with the total number of ranks in the run (kB per rank). |

**Grid allocation.** RAMSES divides `ngridtot` over the MPI ranks. With many ranks, the ghost zones
around each rank's domain take up a growing part of its grids, until the run stops with "Increase
ngridmax". With `ALLOC_GHOST_COEF` set, the launcher replaces `ngridtot` by a larger per-rank
`ngridmax` when needed. The formula is described in `launch_tools/ngridmax_tools.sh`.

**Memory estimate.** The `MEM_*` constants let the launcher estimate the memory per node of every
configuration, and pick a node type with enough memory (see
[What the launcher does](launch_script_details.md#6-memory-and-node-type)). The memory per rank
is

```
MEM_PER_GRID_KB × grids + MEM_PER_PARTICLE_B × particles + MEM_PER_RANK_GB
  + MEM_PER_RANK_IN_RUN_KB × number of ranks
```

with the grids and particles allocated per rank in the namelist. The constants are fitted on the
memory measured in runs of the setup: the `MaxRSS` of the Slurm accounting at the end of
`slurm_<job id>.out`, for several resolutions and numbers of ranks. Without `MEM_PER_RANK_GB`, no
estimate is made, and all jobs use the first node type of the cluster.



## Testing the new setup

1. Launch the smallest resolution on one node, MPI-only, one repeat:
   ```bash
   ./launch_benchmark_suite.sh -c <cluster> -b <setup> -r <resolution> -n 1
   ```
2. Check the end of the run log (`run_<date>_<job id>.log`): it ends with the timer table and a
   `TOTAL` line. Check the run time against `TEST_TIME`.
3. Launch the largest numbers of nodes you plan to use, to check the grid allocation with many
   ranks (no "Increase ngridmax"), and the largest resolution on the smallest number of nodes, to
   check the memory.
4. Launch the full campaign with 3 repeats and look at the [inspect runs figure](figures/inspect_runs.md).
