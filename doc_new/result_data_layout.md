# Results data layout

The results of a benchmark run can be found on the scratch of the cluster (`$CLUSTER_SCRATCH`, as set in `HPCclusters/<cluster>/cluster_info.sh`), in a folder specific to the version, cluster and setup (called a **cell**):

```
benchmark_<branch>_<commit date>_<commit_hash>_<cluster>_<setup>/
--- builds/
--- launches.txt
--- reso<R>_nodes<N>_cores<C>_mpi<P>_omp<M>/
```
The `builds/` folder contains
* the executables: `benchmark_exe_*3d` with * equal to ser, mpi, omp or hyb for the serial, mpi-only, openmp-only, or hybrid version
* the build info: `<exe>.txt`
* compiler and modules versions `<exe>.env`
* the build log `<exe>.make.log`.

The `launches.txt` file records the launch commands (`./launch_benchmark_suite.sh ...`) used for this cell. A new line is added each time the script is launched. It contains:
the date, the commit hash of the benchmark script repository (with `+` if it has uncommitted changes), and the launch command.
New runs are automatically added to the existing folder structure.

The `reso...` folders are the run directories for the configuration specified in the folder name:
* R = resolution, e.g. 1024
* N = number of nodes
* C = number of cores used per node (for when using partial nodes with `-p`)
* P = the number of MPI ranks per node (0 = pure OpenMP)
* M = the number of OpenMP threads per MPI process (0 = pure MPI, 1 = MPI with 1 OpenMP thread, for measuring OpenMP overhead)

Each run directory contains
```
reso<R>_nodes<N>_cores<C>_mpi<P>_omp<M>/
--- job.sh                       job script
--- <setup>_<R>.nml              namelist
--- run_<date>_<job id>.log      log file, one per repeat
--- slurm_<job id>.out           Slurm output, with job accounting
--- slurm_<job id>.err           Slurm error messages
```

The log files are those outputted by the RAMSES code. At the top, some additional metadata is added to help retrace the run conditions.