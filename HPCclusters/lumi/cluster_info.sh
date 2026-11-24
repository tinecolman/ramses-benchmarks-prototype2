CLUSTER_SCRATCH=/scratch/${CLUSTER_ACCOUNT}
CLUSTER_CORES_PER_NODE=128

COMPILER_FLAVOR=CRAY
RUN_COMMAND="srun --cpu-bind=verbose"
MPIF90="ftn"
#MPIF90="ftn -fallow-argument-mismatch"
# mismatch flag needed to circumvent mpi_allreduce error.

# node types, smallest memory first (see launch_tools/memory_tools.sh): usable memory per
# node (GiB, as given by Slurm: sinfo -o "%m" in MiB / 1024) and maximum number
# of nodes per job (0: no limit), from sinfo (2026-11-24): 229376, 491520 and
# 1015808 MiB. The large memory nodes (largemem: 512 GiB, hugemem: 1 TiB) are
# in the small partition, which allows at most 4 nodes per job (see
# job_script_params.sh)
NODE_TYPES=(standard largemem hugemem)
NODE_MEMORY_GB=(224 480 992)
NODE_MAX_NODES=(0 4 4)
# memory of the MPI library per MPI process (GB), on top of the estimate of the setup
MPI_MEMORY_PER_PROCESS_GB=0
