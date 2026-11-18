#!/bin/bash

CLUSTER_PARTITION=dcgp_usr_prod
CLUSTER_QOS=normal
if [[ $NBNODES -gt 16 ]]; then
    CLUSTER_QOS=dcgp_qos_bprod
fi

# nodes running ~2x slower than the others (comma-separated list)
# lrdn4780: all timers ~1.9x slower, seen in cosmo and sedov runs of 2026-11-16/17
# lrdn4067: suspected bad network link; in all 8 slow cosmo 128-node runs of
#           2026-11-18 (multigrid 1.2-1.8x slower) and 2 slow 32-node runs, never in a normal run
EXCLUDE_NODES=lrdn4780,lrdn4067

cat <<JOBSCRIPT > "$OUTPUT_FILE"
#!/bin/bash -l
#SBATCH --job-name=${JOB_NAME}
#SBATCH --account=${CLUSTER_ALLOCATION_ID}
#SBATCH --partition=${CLUSTER_PARTITION}
#SBATCH --qos=${CLUSTER_QOS}
#SBATCH --nodes=${NBNODES}
#SBATCH --ntasks-per-node=${NTASKS_PER_NODE}
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --threads-per-core=1
#SBATCH --exclusive
#SBATCH --exclude=${EXCLUDE_NODES}
#SBATCH --time=${TEST_TIME}
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

JOBSCRIPT
