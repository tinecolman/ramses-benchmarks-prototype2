
# Launch script details

Here we describe in more detail the benchmark launch script.

## Options

When running the benchmark launcher with
```bash
./launch_benchmark_suite.sh -c <cluster> -b <setup> -r "<resolutions>" -n "<numbers of nodes>" [options]
```
the compute cluster, simulation setup, setup resolutions and the number of nodes arguments are mandatory. If a cluster, setup or resolution does not exist, the launcher exits and a list with the available choices is printed.

The table below shows an overview of all available options. 

| Option | Meaning | Example |
|---|---|---|
| `-c` | Cluster (mandatory): a folder of `HPCclusters/`. | `-c lumi` |
| `-b` | Benchmark setup (mandatory): a folder of `setups/`. | `-b sedov` |
| `-r` | Resolutions (mandatory). The setup needs a namelist `setups/<setup>/<setup>_<resolution>.nml` for each. | `-r "256 512 1024"` |
| `-n` | Numbers of nodes (mandatory). | `-n "1 2 4 8"` |
| `-i` | Repeats: how many identical jobs to launch for every configuration (default 1). Use at least 3, so that outliers can be detected. | `-i 3` |
| `-m` | OpenMP threads per MPI process (default 0: MPI-only). | `-m "0 2 4 8 16"` |
| `-p` | MPI processes per node (default: as many as fit on the node, see below; 0: no MPI). | `-p "16 32"` |
| `-a` | Project account. If not given, your accounts are looked up and you are asked to choose when there are several. | `-a project_12345` |
| `-s` | Path to the RAMSES source code (instead of `RAMSES_SOURCE_DIR`). | `-s $HOME/other_ramses` |
| `-v` | Use mini-ramses (setups from `setups-mini-ramses/`, source from `MINI_RAMSES_SOURCE_DIR`). | `-v` |

If multiple values are given for an option, every combination is launched. For example, when using `-n "1 2" -m "0 4"`, the following combinations are launched:
```
-n 1 -m 0
-n 1 -m 4
-n 2 -m 0
-n 2 -m 4
```

## MPI and OpenMP configurations

Running with MPI-only on the full node is the default configuration, with one MPI rank per core. For example on a node with 128 cores, this is equivalent to using the options `-p 128 -m 0`.

When specifying a non-zero number of OpenMP threads (without `-p`), the number of MPI ranks per node is calculated so that
`N_mpi x N_omp = N_cores` with `N_cores` the number of cores on a node. For example with `-m 8` on a 128-core node, there are 16 MPI processes of 8 threads each.
To compare MPI-only with hybrid MPI+OpenMP on full nodes using different number of threads, use something like:
```bash
./launch_benchmark_suite.sh -c lumi -b sedov -r 1024 -n "1 2 4" -m "0 2 4 8 16" -i 3
```
Make sure your branch actually supports OpenMP.

Setting `-p` explicitly allows for specific configurations: `-p 0 -m 0` is a serial run, and `-p 0 - m "<values>"` gives OpenMP-only runs.
When using `0 < p < N_cores`, partial nodes can be used. This allows to check whether some setups perform better when leaving some cores idle (possibly due to memory access contention). For example, to scan the entire parameter space on one node:
```bash
./launch_benchmark_suite.sh -c meluxina -b collapse-MHD -r high -n "1" -p "0 1 2 4 8 16 32 64 128" -m "0 2 4 8 16 32 64 128"
```
This tries everything from serial to MPI-only, OpenMP-only and hybrid, on full and partial nodes. Combinations that need more cores than the node has are skipped. By default, runs on partial nodes are not used in the analysis figures: they only compare the configurations that use all cores of the node.


## What the launcher does

The launcher prepares and submits jobs for benchmarking the code. It is run on the login node of the cluster.

### 1. Check input
First, the options given to the launcher are checked: the mandatory options must be given, and the cluster (`-c`), setup (`-b`) and resolutions (`-r`) must exist. If not, the launcher stops and lists the available ones. Cluster and setup names cannot contain `_`.

The launcher then retrieved the information about the RAMSES repository: branch, commit, commit date, version and the uncommitted changes. **
> [!WARNING]
> Code info is **read at launch time**. Do not change branch or modify the code until the launcher has finished. 

If no account is given with `-a`, your project accounts are looked up with `sacctmgr`. A single account is used directly; if there are several, you are asked to choose.

### 2. Create results folder
The results folder of the cell is created in `$CLUSTER_SCRATCH`, if it does not exist yet:
`benchmark_<branch>_<commit date>_<commit>_<cluster>_<setup>/` (see
[Results data layout](result_data_layout.md)). With `-v` (mini-ramses), the name starts with
`mini-benchmark_`.

### 3. Compile the code
The launcher builds one executable per variant needed by the requested configurations: serial,
MPI, OpenMP or hybrid. The RAMSES make options are setup depended and read from `setups/<setup>/config.txt`. The compiler and modules are cluster dependent and set in `HPCclusters/<cluster>/cluster_info.sh` and `modules.sh`.

The compilation is done on a compute node, through a compile job script. The launcher waits until
the compile job is finished. The executables are stored in the `builds/` folder of the results,
together with:
- `<exe>.txt`: the make command, commit, compile date and the uncommitted changes;
- `<exe>.env`: the compiler version and the loaded modules;
- `<exe>.make.log`: the build log.

Later launches of the same setup and version reuse these executables. If an existing build was
made with another make command (for example after changing the compile flags), the launcher stops.
You need to manually delete the executable in `builds/` to recompile. The launcher also stops if a
compilation fails.

### 4. Record the launch
A line is added to `launches.txt` in the results folder: the date, the commit of this benchmark
repository (with `+` if it has uncommitted changes) and the command line.

### 5. Create run directories and adjust namelist
For every combination of resolution, number of nodes, OpenMP threads and MPI processes, the
launcher creates a run directory `reso<R>_nodes<N>_cores<C>_mpi<P>_omp<M>/` and copies the
namelist of the setup into it. The executable is not copied: the job runs it from `../builds/`.

RAMSES divides `ngridtot` (and `nparttot`) of the namelist over the MPI
ranks. With many ranks, the ghost zones take up a growing part of each rank's grids, until the run
stops with "Increase ngridmax". For setups that set `ALLOC_GHOST_COEF` in their
`scaling_config.sh`, the launcher replaces `ngridtot` by a per-rank `ngridmax` with room for the
ghost zones, when needed. The replaced line is marked with a comment in the namelist of the run
directory. Namelists that set `ngridmax` themselves are not changed.

### 6. Memory and node type
The memory needed per node is estimated for every configuration, from the grids (and particles)
allocated per rank in the namelist of the run directory, so after the adaptation above. The
constants of the estimate are set in `setups/<setup>/scaling_config.sh`, and the memory of the MPI
library in `HPCclusters/<cluster>/cluster_info.sh`. A safety factor of 1.1 is applied.

The smallest node type of the cluster with enough memory is selected (node types in
`HPCclusters/<cluster>/cluster_info.sh`, e.g. standard and large-memory nodes). A configuration
that fits on no node type is skipped with a warning. Setups without memory constants are run on
the first node type of the cluster.

### 7. Write and submit job scripts
One job script `job.sh` is written per configuration. It combines, in following order:
- the filled in job parameters template of the cluster (`HPCclusters/<cluster>/job_script_params.sh`)
- the OpenMP environment for runs with threads (`HPCclusters/<cluster>/openmp.sh`)
- the module load commands
- the writing of a header at the top of the run log (configuration, node list, ...)
- the run command for RAMSES
- the recording the Slurm accounting of the job to `slurm_<job id>.out`.

Nodes listed in `HPCclusters/<cluster>/bad_nodes.txt` are excluded from all
jobs, including the compile job (`sbatch --exclude`). The file has one node per line, with the
date and the reason; lines starting with `#` are ignored.

Each job script is submitted `-i` times. Each submission is a separate job, which writes its own
log `run_<date>_<job id>.log` in the same run directory. Repeating the runs helps to detect
outliers.
