#!/bin/bash
#######################################################################
#
# Builds of the benchmark executables, used by launch_benchmark_suite.sh
# (sourced from it, it uses the variables of the launcher).
#
# select_builds:  which variants are needed (serial, MPI, OpenMP, hybrid),
#                 their make commands and executable names
# prepare_builds: reuse the existing builds in BUILD_DIR, compile the missing
#                 ones in a compile job and store them with their description
#
#######################################################################

# Variants needed for the requested MPI x OpenMP layouts, their make commands
# (MAKESTRING_*) and executable names (TEST_EXECUTABLE_*)
select_builds () {
   # Check which types of compilation configurations are requested
   C_SERIAL=false;
   C_MPI=false;
   C_OPENMP=false;
   C_HYBRID=false;

   for MPI_PROC in "${MPI_PROC_LIST[@]}"; do
      for OMP_THREADS in "${OMP_THREAD_LIST[@]}"; do

         # Resolve actual layout
         read ACT_MPI ACT_OMP <<< $(resolve_layout "$MPI_PROC" "$OMP_THREADS")

         if (( $ACT_OMP == 0 )); then
            if (( $ACT_MPI == 0 )); then
               # compile serial
               C_SERIAL=true;
            else
               # compile MPI-only
               C_MPI=true;
            fi
         else
            if (( $ACT_MPI == 0 )); then
               # compile OpenMP-only
               C_OPENMP=true;
            else
               # compile MPI+OpenMP hybrid
               C_HYBRID=true;
            fi
         fi
      done
   done

   # Read test configuration file
   FLAGS=$(grep FLAGS ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}/config.txt | cut -d ':' -f2);

   # Define make strings and executable names for different combinations of MPI/OMP compilation
   MAKESTRING_SER="make EXEC=${EXECNAME}ser COMPILER=${COMPILER_FLAVOR} MPI=0 OPENMP=0 MPIF90=\"${MPIF90}\" MACHINE=${CLUSTER} ${FLAGS}";
   TEST_EXECUTABLE_SER=${EXECNAME}ser3d

   MAKESTRING_MPI="make EXEC=${EXECNAME}mpi COMPILER=${COMPILER_FLAVOR} MPI=1 OPENMP=0 MPIF90=\"${MPIF90}\" MACHINE=${CLUSTER} ${FLAGS}";
   TEST_EXECUTABLE_MPI=${EXECNAME}mpi3d

   MAKESTRING_OMP="make EXEC=${EXECNAME}omp COMPILER=${COMPILER_FLAVOR} MPI=0 OPENMP=1 MPIF90=\"${MPIF90}\" MACHINE=${CLUSTER} ${FLAGS}";
   TEST_EXECUTABLE_OMP=${EXECNAME}omp3d

   MAKESTRING_HYB="make EXEC=${EXECNAME}hyb COMPILER=${COMPILER_FLAVOR} MPI=1 OPENMP=1 MPIF90=\"${MPIF90}\" MACHINE=${CLUSTER} ${FLAGS}";
   TEST_EXECUTABLE_HYB=${EXECNAME}hyb3d
}

# Value of a field ("key: value") in the description of a build
build_field () {
   sed -n "s/^$2: //p" $1 | head -n 1
}

# Decide whether a requested variant must be compiled, by setting the variable
# named $1 to true or false. An existing build is reused; the script stops if
# it was made with another make command (e.g. other flags in config.txt).
check_build () {
   local var=$1 exe=$2 makestring=$3
   local info=${BUILD_DIR}/${exe}.txt
   if [[ ! -f ${BUILD_DIR}/${exe} ]]; then
      printf -v $var true
      return
   fi
   if [[ -f $info && "$(build_field $info make)" != "$makestring" ]]; then
      log "ERROR: existing build ${BUILD_DIR}/${exe} was made with another make command:"
      log "       $(build_field $info make)"
      log "       Delete it to recompile."
      exit 1
   fi
   log "Reusing existing build ${exe}"
   printf -v $var false
}

# Copy a fresh executable from the RAMSES bin directory to the builds and
# write its description, from the files left by the compile job
install_build () {
   local exe=$1 makestring=$2
   local makelog=${BUILD_DIR}/${exe}.make.log
   local envfile=${BUILD_DIR}/${exe}.env
   if [[ ! -f ${RAMSES_BIN_DIR}/${exe} ]]; then
      log "ERROR: compilation of ${exe} failed, end of the build log:"
      log "$(tail -n 20 $makelog)"
      exit 1
   fi
   cp ${RAMSES_BIN_DIR}/${exe} ${BUILD_DIR}/${exe}
   {
      echo "executable: ${exe}"
      echo "repository: ${GIT_URL}"
      echo "branch: ${BRANCH}"
      echo "commit: ${COMMIT}"
      echo "uncommitted changes: ${UNCOMMITTED}"
      echo "benchmark: ${TEST_NAME}"
      echo "cluster: ${CLUSTER}"
      echo "make: ${makestring}"
      echo "compile date: $(date '+%F %T')"
      cat $envfile
      echo "######## uncommitted changes (git diff HEAD)"
      if [[ -n "$GIT_DIFF" ]]; then echo "$GIT_DIFF"; else echo "none"; fi
      echo "######## build log"
      cat $makelog
   } > ${BUILD_DIR}/${exe}.txt
   rm -f $makelog $envfile
   log "Stored build ${BUILD_DIR}/${exe}"
}


# Reuse the existing builds, compile the missing ones
prepare_builds () {
   # Check which versions need compiling
   B_SERIAL=false; B_MPI=false; B_OPENMP=false; B_HYBRID=false
   ${C_SERIAL} && check_build B_SERIAL $TEST_EXECUTABLE_SER "$MAKESTRING_SER"
   ${C_MPI}    && check_build B_MPI    $TEST_EXECUTABLE_MPI "$MAKESTRING_MPI"
   ${C_OPENMP} && check_build B_OPENMP $TEST_EXECUTABLE_OMP "$MAKESTRING_OMP"
   ${C_HYBRID} && check_build B_HYBRID $TEST_EXECUTABLE_HYB "$MAKESTRING_HYB"

   # Compile code
   if ${B_SERIAL} || ${B_MPI} || ${B_OPENMP} || ${B_HYBRID}; then

      cd ${RAMSES_BIN_DIR};

      # write a job script to compile the code
      # name of the job script file
      OUTPUT_FILE="compile_job.sh"
      # set jobscript params
      NBNODES=1
      NTASKS_PER_NODE=1
      CPUS_PER_TASK=1
      JOB_NAME=compile
      TEST_TIME="00:15:00"
      # write SBATCH parameters block for current cluster
      source ${CLUSTER_DIR}/job_script_params.sh
      # append modules to load to jobscript
      cat $MODULES >> $OUTPUT_FILE
      # directory receiving the build logs, used by the commands below
      echo "" >> $OUTPUT_FILE
      echo "BUILD_DIR=${BUILD_DIR}" >> $OUTPUT_FILE

      # add the compile commands of one variant: the make output and the compiler
      # version and modules are written next to the builds, for install_build
      add_compile_commands () {
         local exe=$1 makestring=$2 label=$3
         echo "" >> $OUTPUT_FILE
         echo "make clean >> $LOGFILE 2>&1;" >> $OUTPUT_FILE
         echo "rm -f ${exe};" >> $OUTPUT_FILE
         echo "Compiling in ${label} mode..." >> $LOGFILE 2>&1;
         # compiler version and loaded modules, for the description of the build
         local compiler=${MPIF90%% *}   # first word of MPIF90, without the flags
         local envfile=\${BUILD_DIR}/${exe}.env
         echo "echo '######## compiler' > $envfile;" >> $OUTPUT_FILE
         echo "$compiler --version 2>&1 | head -n 3 >> $envfile;" >> $OUTPUT_FILE
         echo "echo '######## modules' >> $envfile;" >> $OUTPUT_FILE
         echo "module list >> $envfile 2>&1;" >> $OUTPUT_FILE
         # compile; stop the job at the first failure, which marks it as failed
         echo "$makestring > \${BUILD_DIR}/${exe}.make.log 2>&1 || exit 1;" >> $OUTPUT_FILE
      }
      ${B_SERIAL} && add_compile_commands $TEST_EXECUTABLE_SER "$MAKESTRING_SER" serial
      ${B_MPI}    && add_compile_commands $TEST_EXECUTABLE_MPI "$MAKESTRING_MPI" MPI-only
      ${B_OPENMP} && add_compile_commands $TEST_EXECUTABLE_OMP "$MAKESTRING_OMP" OpenMP-only
      ${B_HYBRID} && add_compile_commands $TEST_EXECUTABLE_HYB "$MAKESTRING_HYB" "hybrid MPI+OpenMP"

      set -e

      # submit the job script and wait until compilation is done
      compile_job_id=$(sbatch compile_job.sh | awk '{print $4}')
      log "Compile job submitted with Job ID: $compile_job_id"
      log "Waiting for compile job to finish..."
      # Poll the job status and wait until it's completed
      while true; do
         job_status=$(sacct --jobs=$compile_job_id --noheader --format=JobID,State | awk -v job_id="$compile_job_id" '$1 == job_id {print $2}')
         if [[ "$job_status" == "COMPLETED" ]]; then
            log "Compile job completed successfully."
            break
         elif [[ "$job_status" == "FAILED" || "$job_status" == "CANCELLED" ]]; then
            log "Compile job failed or was cancelled. Exiting..."
            # end of the build log of the variant that failed (the last one written)
            makelog=$(ls -t ${BUILD_DIR}/*.make.log 2>/dev/null | head -n 1)
            if [[ -n "$makelog" ]]; then
               log "End of $makelog:"
               log "$(tail -n 20 $makelog)"
            fi
            exit 1
         fi
         # Sleep for a while before checking the status again
         sleep 15
      done
      set +e

      ${B_SERIAL} && install_build $TEST_EXECUTABLE_SER "$MAKESTRING_SER"
      ${B_MPI}    && install_build $TEST_EXECUTABLE_MPI "$MAKESTRING_MPI"
      ${B_OPENMP} && install_build $TEST_EXECUTABLE_OMP "$MAKESTRING_OMP"
      ${B_HYBRID} && install_build $TEST_EXECUTABLE_HYB "$MAKESTRING_HYB"

   fi
}
