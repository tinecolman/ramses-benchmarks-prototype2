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
# write its description (<exe>.txt); the compiler version and modules
# (<exe>.env) and the build log (<exe>.make.log) written by the compile job
# stay next to it
install_build () {
   local exe=$1 makestring=$2
   local makelog=${BUILD_DIR}/${exe}.make.log
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
      echo "build log: ${exe}.make.log"
      echo "compiler and modules: ${exe}.env"
      echo "######## uncommitted changes (git diff HEAD)"
      if [[ -n "$GIT_DIFF" ]]; then echo "$GIT_DIFF"; else echo "none"; fi
   } > ${BUILD_DIR}/${exe}.txt
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

      # write a job script to compile the code, in the RAMSES bin directory
      # where it runs
      OUTPUT_FILE="${RAMSES_BIN_DIR}/compile_job.sh"
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

      # submit the job script and wait until compilation is done
      compile_job_id=$(sbatch ${SBATCH_EXCLUDE} --chdir=${RAMSES_BIN_DIR} ${OUTPUT_FILE} | awk '{print $4}')
      if [[ -z "$compile_job_id" ]]; then
         log "ERROR: submission of the compile job failed (see the sbatch message above)"
         exit 1
      fi
      log "Compile job submitted with Job ID: $compile_job_id"
      log "Waiting for compile job to finish..."
      # wait_for_job: see slurm_tools.sh
      if wait_for_job $compile_job_id; then
         log "Compile job completed successfully."
      else
         log "Compile job ended with state ${JOB_STATE}. Exiting..."
         # end of the build log of the variant that failed (the last one written)
         makelog=$(ls -t ${BUILD_DIR}/*.make.log 2>/dev/null | head -n 1)
         if [[ -n "$makelog" ]]; then
            log "End of $makelog:"
            log "$(tail -n 20 $makelog)"
         fi
         exit 1
      fi

      ${B_SERIAL} && install_build $TEST_EXECUTABLE_SER "$MAKESTRING_SER"
      ${B_MPI}    && install_build $TEST_EXECUTABLE_MPI "$MAKESTRING_MPI"
      ${B_OPENMP} && install_build $TEST_EXECUTABLE_OMP "$MAKESTRING_OMP"
      ${B_HYBRID} && install_build $TEST_EXECUTABLE_HYB "$MAKESTRING_HYB"

   fi
}
