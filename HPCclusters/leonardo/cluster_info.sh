CLUSTER_SCRATCH=$SCRATCH
CLUSTER_CORES_PER_NODE=112

COMPILER_FLAVOR=INTEL
RUN_COMMAND="srun --cpu-bind=verbose"
MPIF90="mpiifort -march=native -qopt-zmm-usage=high"