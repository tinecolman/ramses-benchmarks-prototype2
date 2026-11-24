#!/bin/bash

CLUSTER_PARTITION=standard
MEM_LINE=""

# Large memory nodes, as chosen by the launcher (NODE_TYPE, see cluster_info.sh):
# the 512 GiB and 1 TiB nodes are in the small partition, and are allocated
# when requesting more memory than a smaller node has
case "$NODE_TYPE" in
    largemem)
        CLUSTER_PARTITION=small
        MEM_LINE="#SBATCH --mem=480G"
        ;;
    hugemem)
        CLUSTER_PARTITION=small
        MEM_LINE="#SBATCH --mem=992G"
        ;;
esac

cat <<JOBSCRIPT > "$OUTPUT_FILE"
#!/bin/bash -l
#SBATCH --job-name=${JOB_NAME}
#SBATCH --account=${CLUSTER_ACCOUNT}
#SBATCH --partition=${CLUSTER_PARTITION}
${MEM_LINE}
#SBATCH --nodes=${NBNODES}
#SBATCH --ntasks-per-node=${NTASKS_PER_NODE}
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --threads-per-core=1
#SBATCH --exclusive
#SBATCH --hint=nomultithread
#SBATCH --time=${TEST_TIME}
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

export FI_CXI_RX_MATCH_MODE=hybrid

JOBSCRIPT
