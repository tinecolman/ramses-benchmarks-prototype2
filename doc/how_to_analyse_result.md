## How to process the results

To avoid dependence on the python distribution on the cluster, it is recommended to simply download the full benchmark directory to your local computer and run the analysis scripts locally.

In the directory `analysis/` you can find a collection of scripts to extract, analyse and visulaize the results:
*  io_timings.py: routines to extract timings from log files and add them to a database
* visualisation.py: 

### Gathering the results [TODO]

After launching all jobs for a benchmark case, an additional dependency job is launched on one node to gather the resulting timings from the log files. This job will wait until all jobs with the name of the test have finished. It get the total execution time from the logs, creates a commit and pushes the updated data file to the `ramses-benchmarks` repository. To gain write access to this repository, contact one of its admins.

Inside the `ramses-benchmarks` repository, there is a file for each combination of cluster and setup. Inside a file, one line contains one data entry, for example:
```
2025-02-27,ebcb6769,1024,1,[155.512386617 153.174278465 155.66211]
```
In order, we have the execution date of the benchmark, the commit hash, the resolution of the setup, the number of nodes used, and finally a list with the total execution times.

Visualizing this data can be done using the `analyse_benchmark.py` script, which produces figures like the ones in the previous section.
The CI/CD of this submodule will automatically update the figures when new timings are committed to the repository.
