# Running benchmarks

This page is a quick start on how to run your own benchmarks. We will assume your simulation setup is already defined in the `setups` folder and the cluster you are running on is listed in the `HPCclusters` folder. If this is not the case, consult the pages [Adding a setup](adding_a_setup.md) or [Adding a cluster](adding_a_cluster.md).

The process goes as follows

```
login ─> launch ─> retrieve ─> verify ─> analyse
            ^                      |
            │                      |
            └──────────────────────┘
```

## Before you start

Login to the cluster and git clone this benchmark package and RAMSES, if not already done so.
Set the path to the RAMSES source code with:
```bash
export RAMSES_SOURCE_DIR=my_stuff/my_ramses
```
It is recommended to add this export line to your `.bashrc`.

> [!WARNING]
> The launcher will compile the version of RAMSES that is currently checked out in your RAMSES repository, **including uncommitted changes**. Check out the branch or commit you want to benchmark, and clean unwanted changes. Uncommitted changes are recorded with the build, but the results will be assigned to the checked out commit.


## Launch benchmarks

The benchmark launcher script is run on the login node of the cluster, from this repository:

```bash
cd my_stuff/my_ramses-benchmarks
./launch_benchmark_suite.sh -c <cluster> -b <setup> -r "<resolutions>" -n "<numbers of nodes>" [options]
```
For example, the Sedov setup at resolution 1024 on 1 to 8 nodes on LUMI, MPI-only, 3 repeats:

```bash
./launch_benchmark_suite.sh -c lumi -b sedov -r 1024 -n "1 2 4 8" -i 3
```
For more launch options, see [Launch script options](launch_script_details.md#options). For more details on how to run with different OpenMP threads and MPI ranks, see [MPI and OpenMP configurations](launch_script_details.md#MPI-and-OpenMP-configurations)

This script will compile the code, create run directories, write job scripts and launch the jobs. For more details, see [What the launcher does](launch_script_details.md#what-the-launcher-does).

## Retrieve results

The results can be found on the scratch of the cluster (`$CLUSTER_SCRATCH`, as set in `HPCclusters/<cluster>/cluster_info.sh`). They are gathered in a folder specific to the code version, cluster and setup:
```
benchmark_<branch>_<commit date>_<commit_hash>_<cluster>_<setup>/
```

Retrieve the results by copying the whole folder, keeping its name, for example:
```bash
rsync -av <cluster>:<scratch>/benchmark_openmp_2026-10-14_f5b7b39b_lumi_sedov ~/archive/
```

For more info on what this folder contains, see [Results data layout](result_data_layout.md).

## Verify and relaunch

Make the [inspect runs figures](figures/inspect_runs.md), for example:

```bash
python openmp/inspect_runs.py ~/archive/benchmark_openmp_2026-10-14_f5b7b39b_lumi_sedov
```

These figures visualize the time of every repeat, the repeats rejected as outliers and the number of repeats kept per point. Look for:

- **Red numbers** (fewer than 2 repeats kept): these indicate data points that rests on a single run. Relaunch this configuration to verify outliers.
- **Missing points:** these indicate configurations that crashed or did not finish. Check the end of the log and the `slurm_*.err` file before relaunching.
- **Many rejected repeats or large scatter**: this may hint at bad nodes or network issues. Investigate using the guidelines in [inspect runs](figures/inspect_runs.md#how-to-deal-with-outliers).

To **relaunch**, run the launcher again for the same version, with only the missing
configurations. The new repeats go to the same run folders, next to the existing ones, and the
builds are reused. For example, two more repeats of 16×8 on 64 and 128 nodes:

```bash
./launch_benchmark_suite.sh -c lumi -b sedov -r 1024 -n "64 128" -m 8 -i 2
```

Then retrieve the cell again and make the figure again, until every point has at least 2 kept
repeats.


## Analyse

Once you are happy with the collected data, you can start analysing it. This package includes scripts for reading, processing and visualising the data. For an overview of the types of analysis that can be done, see [Figures](figures/README.md).
