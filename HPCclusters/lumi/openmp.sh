#!/bin/bash

cat <<JOBSCRIPT >> "$OUTPUT_FILE"

export SRUN_CPUS_PER_TASK=\${SLURM_CPUS_PER_TASK}
export OMP_NUM_THREADS=\${SLURM_CPUS_PER_TASK}
export OMP_PLACES=cores
export OMP_PROC_BIND=close
export OMP_STACKSIZE=2048M
export OMP_DISPLAY_AFFINITY=TRUE
# srun --cpu-bind=verbose also shows each rank's cores

JOBSCRIPT