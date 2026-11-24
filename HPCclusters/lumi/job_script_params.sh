#!/bin/bash

CLUSTER_PARTITION=standard
MEM_LINE=""

# The large memory nodes (512GB and 1TB) are in the small partition, and are
# allocated when requesting more memory than a standard node (256GB) has.
# They are used for the runs on 1 node (except the compilation job), and for
# MPI-only up to LARGEMEM_MPI_NODES nodes (set per resolution in
# launch_benchmark_suite.sh from scaling_config.sh), as MPI-only needs the
# most memory per node. The small partition allows at most 4 nodes per job.
MPI_ONLY=$(( CPUS_PER_TASK == 1 && NTASKS_PER_NODE > 1 ))
LARGEMEM_NODES=$(( ${LARGEMEM_MPI_NODES:-0} < 4 ? ${LARGEMEM_MPI_NODES:-0} : 4 ))
if (( (NBNODES == 1 && NTASKS_PER_NODE * CPUS_PER_TASK > 1) || (MPI_ONLY && NBNODES <= LARGEMEM_NODES) )); then
    CLUSTER_PARTITION=small
    MEM_LINE="#SBATCH --mem=480G"
fi

cat <<JOBSCRIPT > "$OUTPUT_FILE"
#!/bin/bash -l
#SBATCH --job-name=${JOB_NAME}
#SBATCH --account=${CLUSTER_ALLOCATION_ID}
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
