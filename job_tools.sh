#!/bin/bash
#######################################################################
#
# Job scripts of the benchmark runs, used by launch_benchmark_suite.sh
# (sourced from it, it uses the variables of the launcher).
#
# write_job_script: write job.sh in the run directory, for the current
#                   configuration of the loop over configurations
#
#######################################################################

# Write ${RUN_DIR}/job.sh (OUTPUT_FILE): job parameters of the cluster,
# OpenMP settings, modules, a header in the log file, the run command and
# the Slurm accounting of the run
write_job_script () {
   OUTPUT_FILE="${RUN_DIR}/job.sh"
   LOGFILE_RUN="run_\${DATE}_\${SLURM_JOBID}.log"

   # number of nodes up to which MPI-only uses the large memory nodes,
   # for this resolution
   LARGEMEM_MPI_NODES=0
   if [[ " $LARGEMEM_MPI_RESOS " == *" $RESO "* ]]; then
      LARGEMEM_MPI_NODES=$LARGEMEM_MPI_MAX_NODES
   fi

   # job parameters from template
   source ${RAMSES_BENCHMARK_DIR}/HPCclusters/${CLUSTER}/job_script_params.sh

   # export the date, which is used to add the execution timestamp to the name of the log-file of the simulation.
   echo "export DATE=\$(date +%F_%Hh%M)" >> "$OUTPUT_FILE"

   # OMP export statements (cluster specific)
   if (( $ACT_OMP != 0 )); then
      source ${RAMSES_BENCHMARK_DIR}/HPCclusters/${CLUSTER}/openmp.sh
   fi

   # modules to load
   cat $MODULES >> $OUTPUT_FILE
   echo "" >> "$OUTPUT_FILE"

   # header of the log file, with the configuration of the run
   # (\$ for the variables that are only known when the job runs)
   cat >> "$OUTPUT_FILE" <<EOF
{
   echo "#########################################"
   echo "Benchmark: ${TEST_NAME}"
   echo "Resolution: ${RESO}"
   echo "Cluster: ${CLUSTER}"
   echo "Partition: ${CLUSTER_PARTITION}"
   echo "Nodes: ${NBNODES}"
   echo "MPI per node: ${ACT_MPI}"
   echo "OMP threads: ${ACT_OMP}"
   echo "Job ID: \${SLURM_JOBID}"
   echo "Node list: \${SLURM_JOB_NODELIST}"
   echo "Excluded nodes: ${EXCLUDE_NODES:-none}"
   echo "Executable: builds/${THIS_EXEC}"
   echo "#########################################"
} > ${LOGFILE_RUN}

EOF

   # run command
   if (( ACT_MPI == 0 )); then
      COMMANDSTRING="${EXEC_PATH} ${TEST_NAMELIST} >> ${LOGFILE_RUN}"
   else
      COMMANDSTRING="$(eval echo ${RUN_COMMAND}) ${EXEC_PATH} ${TEST_NAMELIST} >> ${LOGFILE_RUN}"
   fi   
   echo "$COMMANDSTRING" >> "$OUTPUT_FILE"
   echo "" >> "$OUTPUT_FILE"

   # Slurm accounting of the run (time, state, memory, energy), written to the
   # standard output of the job, slurm_<jobid>.out, and not to the run log.
   # MaxRSS is the peak memory of the largest task (MPI process, with its
   # threads), on node MaxRSSNode; AveRSS is the average over the tasks.
   echo "sacct --jobs=\${SLURM_JOBID} --format=JobID,JobName,Elapsed,State,ExitCode,MaxRSS,MaxRSSNode,MaxRSSTask,AveRSS,ConsumedEnergy" >> "$OUTPUT_FILE"
}
