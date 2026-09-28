CLUSTER_SCRATCH=/scratch/${CLUSTER_ALLOCATION_ID}
CLUSTER_CORES_PER_NODE=128

COMPILER_FLAVOR=CRAY
RUN_COMMAND=srun
MPIF90="ftn"
#MPIF90="ftn -fallow-argument-mismatch"
# mismatch flag needed to circumvent mpi_allreduce error.
