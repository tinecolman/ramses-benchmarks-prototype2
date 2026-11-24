CLUSTER_SCRATCH=/gpfs/scratch/${CLUSTER_ACCOUNT}
CLUSTER_CORES_PER_NODE=112

COMPILER_FLAVOR=INTEL
RUN_COMMAND=srun
MPIF90="mpif90 -march=native -qopt-zmm-usage=high"

# node types, smallest memory first (see launch_tools/memory_tools.sh): usable memory per
# node (GB) and maximum number of nodes per job (0: no limit). The names are
# the constraints of job_script_params.sh
NODE_TYPES=(lowmem highmem)
NODE_MEMORY_GB=(240 1000)
NODE_MAX_NODES=(0 0)
# memory of the MPI library per MPI process (GB), on top of the estimate of the
# setup (measured on the MPI-only runs, compared with LUMI)
MPI_MEMORY_PER_PROCESS_GB=0.6
