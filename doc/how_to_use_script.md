
## How to use the benchmark script

### Content of the package
* `launch_benchmark_suite.sh`: the script for launching the benchmarks
* `setups/`: a directory containing the different predefined benchmark setups.
* `HPCclusters/`: a directory containing presets for different machines.
* `analysis/`: python scripts to extract the results from the log files and make figures
* `results/`: directory where the results are gathered
* `doc/`: collection of markdown files containing with documentation on how to use and extend the package

### Launching the benchmarks
The benchmark script works similar to the test suite script.
To run all benchmarks on one of the predefined clusters, execute the command
```
./launch_benchmark_suite.sh -c cluster_name
```
where you replace `cluster_name` by the name of the computing cluster you are currently on. To see which clusters are supported, check the subdirectory `HPCclusters`.
The script is going to compiler the code and create and submit job scripts to run all the benchmarks on different number of nodes.
The path to RAMSES is specified as a variable in the beginning of the `launch_benchmark_suite.sh script. You may need to update it.
```
RAMSES_SOURCE_DIR="$HOME/ramses";
```
The version of ramses that will be used is the one currently checked out by git. Make sure to checkout the correct branch or commit hash and make sure your copy is clean!

The resulting log files are stored in the directory with the structure
```
benchmark_<branch_name>_<commit_hash>/
--- <setup_name1>
   --- nodes<num_nodes1>_reso<stringA>_omp<num_threads0>
```

### Options
* **`-t`**: By default, all benchmarks defined in the `setups` subdirectory will be executed. To launch a specific benchmark, use the command line argument `-t`. For example, to run only the Sedov test (currently the second in the alphabetical list) on the MeluXina cluster:
`./launch_benchmark_suite.sh -c meluxina -t 2`

* **`-a`**: The script will try to automatically recover your project allocation ID and presents you with a choice if multiple options are found. If you want to set it manually, you can use the option `-a my_allocation_id`.

* To choose the number of nodes, use the option  **`-n`** or  **`-l`**: 
   * **`-n`**: set maximum number of nodes.
   * **`-l`**: set a list of which number of nodes to use.
For example, setting `-n 4` is equivalent to `-l "1 2 4"`.

* **`-w`**: To also perform weak scaling, that is execute the benchmark setup with different resolutions, use the option `-w`. For this, the weak scaling configuration needs to be specified in the setup `scaling_config.sh`.

* **`-i`**: For each configuration, a number of identical jobs can be launched to get more statistics on the execution time and detect outliers. To activate this, use the option `-i`. For example `-i 3` will repeat each run three times.

* **`-m`**: To use OpenMP, specify the number of threads using the option `-m`, for example `-m "2 4 8"`. Remark that with this, the code will be compiled with OpenMP!

* **`-d`**: Do not clean up.
