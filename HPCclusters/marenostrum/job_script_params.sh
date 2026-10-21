#!/bin/bash

CLUSTER_PARTITION=gpp
CLUSTER_QOS=gp_ehpc
MEM_NODE=lowmem

# highmem nodes for the runs on 1 node, and for MPI-only up to
# LARGEMEM_MPI_MAX_NODES nodes (set in scaling_config.sh)
MPI_ONLY=$(( CPUS_PER_TASK == 1 && NTASKS_PER_NODE > 1 ))
if (( NBNODES == 1 || (MPI_ONLY && NBNODES <= ${LARGEMEM_MPI_MAX_NODES:-0}) )); then
    MEM_NODE=highmem
fi

cat <<JOBSCRIPT > "$OUTPUT_FILE"
#!/bin/bash -l
#SBATCH --job-name=${JOB_NAME}
#SBATCH --account=${CLUSTER_ALLOCATION_ID}
#SBATCH --partition=${CLUSTER_PARTITION}
#SBATCH --qos=${CLUSTER_QOS}
#SBATCH --constraint=${MEM_NODE}
#SBATCH --nodes=${NBNODES}
#SBATCH --ntasks-per-node=${NTASKS_PER_NODE}
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --threads-per-core=1
#SBATCH --exclusive
#SBATCH --time=${TEST_TIME}
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

export KMP_AFFINITY="granularity=fine,compact,1,0"

JOBSCRIPT
