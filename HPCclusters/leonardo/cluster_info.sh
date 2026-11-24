CLUSTER_SCRATCH=$SCRATCH
CLUSTER_CORES_PER_NODE=112

COMPILER_FLAVOR=INTEL
RUN_COMMAND="srun --cpu-bind=verbose"
MPIF90="mpiifort -march=native -qopt-zmm-usage=high"

# node types, smallest memory first (see memory_tools.sh): usable memory per
# node (GiB, as given by Slurm: sinfo -o "%m" in MiB / 1024) and maximum number
# of nodes per job (0: no limit). DCGP nodes: 514000 MiB (sinfo, 2026-11-24)
NODE_TYPES=(standard)
NODE_MEMORY_GB=(502)
NODE_MAX_NODES=(0)
# memory of the MPI library per MPI process (GB), on top of the estimate of the
# setup (measured on the MPI-only runs, compared with LUMI)
MPI_MEMORY_PER_PROCESS_GB=0.4
