
## How to add a new computing cluster

The information specific to each computing cluster is stored in the directory `HPCclusters`. There is a subdirectory for each cluster. To add a new cluster, create a new subdirectory with the name of the cluster. Following the example of the existing entries, add the following files:
   * `cluster_description.md`: Information on how to use the cluster.
   * `cluster_info.sh`: a set of bash variables that describe the configuration of the cluster
   * `modules.sh`: a list of commands that load the modules required to compile ramses
   * `job_script_params.sh`: A here document with a template of what the parameters that should be set at the top of the job script

Remark that currently only systems with the SLURM job scheduler are supported by the script (but this can be extended in the future).


### cluster_description.md

To make the life of future users easier, provide a short summary of information of the cluster:
* General info with links to the documentation
* A section on the procedure of how to activate your account
* A section on how to run RAMSES, including how to compile the code and submit a job.

### cluster_info.sh

There are some characteristics that need to be set for each cluster. Some can be retrieved automatically, others need to be set manually. This file contains all parameters that need to be set manually for all clusters. They are required for the operation of the benchmark launcher.
Here is an example for the Discoverer cluster:
```
CLUSTER_SCRATCH=/discofs/$USER
CLUSTER_CORES_PER_NODE=128
COMPILER_FLAVOR=GNU
RUN_COMMAND=srun
```
* `CLUSTER_SCRATCH`: What is the path to the scratch directory, from which to launch jobs.
* `CLUSTER_CORES_PER_NODE`: The amount of cores on a node. Used to define the number of tasks per node.
* `COMPILER_FLAVOR`: Which compiler family to use. Used to select the compiler in the makefile. Currently supporting GNU and INTEL.
* `RUN_COMMAND`: The parallel run command used in the job script. Usually srun or mpirun.


### modules.sh

In this file, we store the commands that will load the modules needed to compile the code on the cluster. Currently, these provide a working combination but maybe not the most performant one. They should be updated when the software stack of the cluster evolves.

In most cases we only need to select which compiler and MPI library to use, as is for example the case on MeluXina:
```
module load GCC/13.3.0
module load OpenMPI/5.0.3-GCC-13.3.0
```
However, sometimes additional packages are required, as for example on Discoverer:
```
module load gmp/6
module load gcc/latest
module load openmpi/5/gcc/latest
```
Our chosen script architecture leaves freedom to load as many packages as needed.

### job_script_params.sh

The first part of this file defines a set of required job script parameters specific to the cluster. Typically, this is where we set the cluster partition on which to launch jobs and the QoS. Doing this here allows to set a different partition or QoS depending on the number of nodes requested. For example, on Leonardo you can use only upto 16 nodes on the normal queue:
```
CLUSTER_QOS=normal
if [[ $NBNODES -gt 16 ]]; then
    CLUSTER_QOS=dcgp_qos_bprod
fi
```
The second part of this file contains a Here Document that will write the job script configuration to file. This type of bash construct allow to copy multiple lines of text, while filling in bash parameters. An example for the MareNostrum cluster:
```
cat <<JOBSCRIPT > "$OUTPUT_FILE"
#!/bin/bash -l
#SBATCH --job-name=${JOB_NAME}
#SBATCH --account=${CLUSTER_ALLOCATION_ID}
#SBATCH --partition=${CLUSTER_PARTITION}
#SBATCH --qos=${CLUSTER_QOS}
#SBATCH --nodes=${NBNODES}
#SBATCH --ntasks-per-node=${CLUSTER_CORES_PER_NODE}
#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --exclusive
#SBATCH --time=${TEST_TIME}
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

export KMP_AFFINITY=\"granularity=fine,compact,1,0\"

JOBSCRIPT
```

As a marker for the Here Document, we chose the string JOBSCRIPT. The lines inbetween the markers will be written to a file with the name `$OUTPUT_FILE`, which is a bash variable specified in the benchmark launch script. Remark that if `$OUTPUT_FILE` exists, it will be overwritten (as indicated by the single >).

What is inbetween the two JOBSCRIPT markers, is the structure for any job script on this cluster.
A job script should start with `#!/bin/bash -l`. Be careful to NOT leave an empty line before this statement, as this will cause the system to not recognize the file as a job script!
Then, we specify the needed job script parameters, in this example indicated by `#SBATCH` for the SLURM scheduler. The bash parameters are filled in automatically when the benchmark launch script is calling this file. In addition to the variables you defined in the top of this file, use the variable names
* `JOB_NAME`
* `CLUSTER_ALLOCATION_ID`
* `NBNODES`
* `CLUSTER_CORES_PER_NODE`
* `TEST_TIME`
which have been set by the main benchmark script, the cluster info file and the test info file.

In addition, also add any export statements needed for the job to the Here Document. You may want to specify a binding strategy as done in this example. For more info in binding/pinning MPI and OpenMP threads, see XXX.

The execution command will be added by the `launch_benchmark_suite.sh` script.