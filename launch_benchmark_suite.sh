#!/bin/bash
#######################################################################
#
# Script to run the RAMSES performance benchmarks
#
# Usage:
#   ./launch_benchmark_suite.sh
#
# Options:
#   -c: (mandatory) specify on which cluster you are
#       ./launch_benchmark_suite.sh -c meluxina
#   -b: (mandatory) select benchmark
#       ./launch_benchmark_suite.sh -t sedov
#   -r: (mandatory) set a list of which resolutions to use
#       ./launch_benchmark_suite.sh -l "256 512 1024"
#   -n: (mandatory) set a list of which number of nodes to use
#       ./launch_benchmark_suite.sh -n "1 2 4"
#   -a: specify allocation ID
#       ./launch_benchmark_suite.sh -a EUR123456
#   -p: set the number of MPI processes used per node, allows to use partial nodes (0=no MPI)
#       ./launch_benchmark_suite.sh -r "1 32 64 128"
#   -m: run with openmp with different number of omp threads
#       ./launch_benchmark_suite.sh -m "1 2 4 8 16"
#   -i: how many runs to launch of a benchmark, to take the average time (default 3)
#       ./launch_benchmark_suite.sh -i 5
#   -d: do not clean up
#   -v: use mini-ramses
#   -s: don't recompile the code
#
#######################################################################

#######################################################################
# Parse input parameters
#######################################################################

RAMSES_SOURCE_DIR="$HOME/ramses_tine_github";
MINI_RAMSES_SOURCE_DIR="$HOME/mini-ramses";

# Default options
CLUSTER=""
TEST_NAME=""
RESO_LIST=""
NODES_LIST=""
CLUSTER_ALLOCATION_ID="none"
DELDATA=true
MPI_PROC_LIST="max"
OMP_THREAD_LIST="0"
ITERS=1
USE_MINIRAMSES=false
COMPILE=true

# Parse options
while getopts "c:a:b:n:r:p:m:i:dvs" OPTION; do
   case $OPTION in
      c) CLUSTER=$OPTARG ;;
      a) CLUSTER_ALLOCATION_ID=$OPTARG ;;
      b) TEST_NAME=$OPTARG ;;
      n) NODES_LIST=($OPTARG) ;;   # Convert input string into an array
      r) RESO_LIST=($OPTARG) ;;
      p) MPI_PROC_LIST=($OPTARG) ;;
      m) OMP_THREAD_LIST=($OPTARG) ;;
      i) ITERS=$OPTARG ;;
      d) DELDATA=false ;;
      v) USE_MINIRAMSES=true ;;
      s) COMPILE=false ;;
   esac
done

# Validate input
if [[ -z "$CLUSTER" ]]; then
   echo "ERROR: you must specify a cluster with -c (e.g. meluxina)" | tee log
   exit 1
fi
if [[ -z "$TEST_NAME" ]]; then
   echo "ERROR: you must specify a benchmark with -b (e.g. sedov)" | tee log
   exit 1
fi
if [[ -z "$RESO_LIST" ]]; then
   echo "ERROR: you must specify the resolutions with -r (e.g. \"256 512 1024\")" | tee log
   exit 1
fi
if [[ -z "$NODES_LIST" ]]; then
   echo "ERROR: you must specify the number of nodes to use with -n (e.g. \"1 2 4\")" | tee log
   exit 1
fi


#######################################################################
# Define paths and load additional info
#######################################################################

RAMSES_BENCHMARK_DIR=$(pwd)
CLUSTER_DIR="${RAMSES_BENCHMARK_DIR}/HPCclusters/${CLUSTER}"
CLUSTER_INFO="${CLUSTER_DIR}/cluster_info.sh"
MODULES="${CLUSTER_DIR}/modules.sh"
if $USE_MINIRAMSES ; then
   RAMSES_BIN_DIR="${MINI_RAMSES_SOURCE_DIR}/bin";
   SETUPS_DIR="setups-mini-ramses";
else
   RAMSES_BIN_DIR="${RAMSES_SOURCE_DIR}/bin";
   SETUPS_DIR="setups";
fi

EXECNAME="benchmark_exe_"

DATE=`date +%F`
LOGFILE="${RAMSES_BENCHMARK_DIR}/benchmark_suite.log";

# load cluster info
source ${CLUSTER_INFO}

# load benchmark configuration
source ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}/scaling_config.sh

#######################################################################
# Get code repository info
#######################################################################

cd $RAMSES_BIN_DIR

# list branches which contain this commit: git branch --contains 0f908c1
# check if dev is in the list, if yes-> set branch to dev.
COMMIT=$(git rev-parse --short HEAD)
COMMIT_DATE=$(git show --no-patch --format=%cd --date=format:'%Y-%m-%d')
GIT_URL=$(git config --get remote.origin.url | sed 's/git@github.com:/https:\/\/github.com\//g')
GIT_URL=${GIT_URL:0:$((${#GIT_URL}-4))}

BRANCH=$(git rev-parse --abbrev-ref HEAD)
# if detached HEAD, check if the commit is from on the dev branch
if [[ "$BRANCH" == "HEAD" ]]; then
   if git merge-base --is-ancestor "$COMMIT" origin/dev; then
      BRANCH="dev"
   else
      BRANCH="detached"
   fi
fi

#######################################################################
# Display info
#######################################################################

# begin logfile
echo > $LOGFILE;

# Welcome message
COLOR='\033[0;36m' #cyan
NC='\033[0m' # No Color
echo -e "${COLOR}################################################${NC}" | tee -a $LOGFILE
echo -e "${COLOR}#    Launching RAMSES performance benchmark    #${NC}" | tee -a $LOGFILE
echo -e "${COLOR}################################################${NC}" | tee -a $LOGFILE
echo "Repository url: ${GIT_URL}" | tee -a $LOGFILE
echo "Branch: ${BRANCH}" | tee -a $LOGFILE
echo "Commit hash: ${COMMIT}" | tee -a $LOGFILE
echo "Benchmark: ${TEST_NAME}" | tee -a $LOGFILE
echo "--------------------------------------------" >> $LOGFILE


#######################################################################
# Select project allocation to run on, if not given by user
#######################################################################

if [[ "$CLUSTER_ALLOCATION_ID" == "none" ]]; then

   # Get the list of project IDs for the current user (works only for slurm)
   #   - ignoring headers (tail -n +3)
   #   - taking care of long account names (format=Account%-40)
   #   - removing duplicates (sort -u)
   MY_PROJECTS=$(sacctmgr show associations user=$USER format=Account%-40 | tail -n +3 | awk '{print $1}' | sort -u)

   # Count the number of projects
   NUM_PROJECTS=$(echo "$MY_PROJECTS" | wc -l)

   # Process the number of projects
   if [[ $NUM_PROJECTS -eq 1 ]]; then
      CLUSTER_ALLOCATION_ID=$(echo "$MY_PROJECTS" | xargs)
      echo "Automatically selected allocation ID: $CLUSTER_ALLOCATION_ID" | tee -a $LOGFILE

   elif [[ $NUM_PROJECTS -gt 1 ]]; then
      # if multiple projects are found, present the user with a list to select from
      echo "Multiple projects found. Please select one:"
      select CLUSTER_ALLOCATION_ID in $MY_PROJECTS; do
         if [[ -n "$CLUSTER_ALLOCATION_ID" ]]; then
            CLUSTER_ALLOCATION_ID=$(echo "$CLUSTER_ALLOCATION_ID" | xargs)
            echo "You selected allocation ID: $CLUSTER_ALLOCATION_ID" | tee -a $LOGFILE
            break
         else
            echo "Invalid selection, please try again."
         fi
      done

   else
      echo "No valid allocation ID found." | tee -a $LOGFILE
      exit 1
   fi

fi


#######################################################################
# Layout resolver (MPI/OMP separation)
#######################################################################

resolve_layout () {
   local mpi=$1
   local omp=$2

   if [[ "$mpi" == "max" ]]; then
      if (( omp == 0 )); then
         mpi=$CLUSTER_CORES_PER_NODE
      else
         mpi=$(( CLUSTER_CORES_PER_NODE / omp ))
      fi
   fi

   echo "$mpi $omp"
}


#######################################################################
# Code compilation
#######################################################################

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


if ${COMPILE}; then

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
   # add compile commands
   if ${C_SERIAL}; then
      echo "" >> $OUTPUT_FILE
      echo "make clean >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
      echo "Compiling in serial mode..."  >> $LOGFILE 2>&1;
      echo "$MAKESTRING_SER >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
   fi
   if ${C_MPI}; then
      echo "" >> $OUTPUT_FILE
      echo "make clean >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
      echo "Compiling in MPI-only mode..."  >> $LOGFILE 2>&1;
      echo "$MAKESTRING_MPI >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
   fi
   if ${C_OPENMP}; then
      echo "" >> $OUTPUT_FILE
      echo "make clean >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
      echo "Compiling in OpenMP-only mode..."  >> $LOGFILE 2>&1;
      echo "$MAKESTRING_OMP >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
   fi
   if ${C_HYBRID}; then
      echo "" >> $OUTPUT_FILE
      echo "make clean >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
      echo "Compiling in hybrid MPI+OpenMP mode..."  >> $LOGFILE 2>&1;
      echo "$MAKESTRING_HYB >> $LOGFILE 2>&1;"  >> $OUTPUT_FILE
   fi

   set -e

   # submit the job script and wait until compilation is done
   compile_job_id=$(sbatch compile_job.sh | awk '{print $4}')
   echo "Compile job submitted with Job ID: $compile_job_id"
   echo "Waiting for compile job to finish..."
   # Poll the job status and wait until it's completed
   while true; do
      job_status=$(sacct --jobs=$compile_job_id --noheader --format=JobID,State | awk -v job_id="$compile_job_id" '$1 == job_id {print $2}')
      if [[ "$job_status" == "COMPLETED" ]]; then
         echo "Compile job completed successfully."
         break
      elif [[ "$job_status" == "FAILED" || "$job_status" == "CANCELLED" ]]; then
         echo "Compile job failed or was cancelled. Exiting..."
         exit 1
      fi
      # Sleep for a while before checking the status again
      sleep 15
   done
   set +e

fi

#######################################################################
# Create benchmark directory on scratch
#######################################################################

if $USE_MINIRAMSES ; then
   BENCHMARK_DIR=$CLUSTER_SCRATCH/mini-benchmark_${BRANCH}_${COMMIT_DATE}_${COMMIT};
else
   BENCHMARK_DIR=$CLUSTER_SCRATCH/benchmark_${BRANCH}_${COMMIT_DATE}_${COMMIT};
fi

set -e
mkdir -p ${BENCHMARK_DIR} >> $LOGFILE 2>&1;
set +e

# create subdirectory for setup
LAUNCH_DIR=$BENCHMARK_DIR/${TEST_NAME}
mkdir -p ${LAUNCH_DIR} >> $LOGFILE 2>&1;

#######################################################################
# Loop over configuration: create job scripts and run simulations
#######################################################################

cd ${LAUNCH_DIR}

JOB_NAME=$TEST_NAME

# Loop over configurations
for RESO in "${RESO_LIST[@]}"; do
for NBNODES in "${NODES_LIST[@]}"; do
for OMP_THREADS in "${OMP_THREAD_LIST[@]}"; do
for MPI_PROC in "${MPI_PROC_LIST[@]}"; do

   read ACT_MPI ACT_OMP <<< $(resolve_layout "$MPI_PROC" "$OMP_THREADS")

   # check which type of config and set the number of MPI processes
   if (( ACT_OMP == 0 )); then
      if (( ACT_MPI == 0 )); then
         # serial
         THIS_EXEC=$TEST_EXECUTABLE_SER
         NTASKS_PER_NODE=1
      else
         # MPI-only
         THIS_EXEC=$TEST_EXECUTABLE_MPI
         NTASKS_PER_NODE=$ACT_MPI
      fi
      CPUS_PER_TASK=1
   else
      if (( ACT_MPI == 0 )); then
         # OpenMP-only
         THIS_EXEC=$TEST_EXECUTABLE_OMP
         NTASKS_PER_NODE=1
      else
         # hybrid MPI+OpenMP
         THIS_EXEC=$TEST_EXECUTABLE_HYB
         NTASKS_PER_NODE=$ACT_MPI
      fi
      CPUS_PER_TASK=$ACT_OMP
   fi

   CORES_PER_NODE=$(($NTASKS_PER_NODE * $CPUS_PER_TASK))
   NUMPROCS=$(($NBNODES * $NTASKS_PER_NODE))

   # skip invalid configs
   if [ ${CORES_PER_NODE} -gt ${CLUSTER_CORES_PER_NODE} ]; then
      continue
   fi

   # make subdirectory
   RUN_DIR=reso${RESO}_nodes${NBNODES}_cores${CORES_PER_NODE}_mpi${ACT_MPI}_omp${ACT_OMP}
   mkdir -p ${RUN_DIR} >> $LOGFILE 2>&1;
   cd ${RUN_DIR}

   # Copy executable and input file
   cp ${RAMSES_BIN_DIR}/${THIS_EXEC} .
   TEST_NAMELIST=${TEST_NAME}_${RESO}.nml
   cp ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}/${TEST_NAMELIST} .

   #----------------------------------------------------------------------
   # Create job script
   #----------------------------------------------------------------------

   OUTPUT_FILE="job.sh"
   LOGFILE_RUN="run_\${DATE}_\${SLURM_JOBID}.log"

   # job parameters from template
   source ${RAMSES_BENCHMARK_DIR}/HPCclusters/${CLUSTER}/job_script_params.sh

   # export the date, which is used to add the execution timestamp to the name of the log-file of the simulation.
   echo "export DATE=\$(date +%F_%Hh%M)" >> "$OUTPUT_FILE"

   # OMP export statements
   # TODO: improve
   if (( $ACT_OMP != 0 )); then
      echo "export OMP_NUM_THREADS=$ACT_OMP" >> "$OUTPUT_FILE"
      #echo "export OMP_PLACES=cores" >> "$OUTPUT_FILE"
      #echo "export OMP_PROC_BIND=true" >> "$OUTPUT_FILE"
      echo "export OMP_STACKSIZE=2048M" >> "$OUTPUT_FILE"
   fi

   # modules to load
   cat $MODULES >> $OUTPUT_FILE
   echo "" >> "$OUTPUT_FILE"

   # add some additional info to the log
   echo "echo \"#########################################\" > ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Benchmark: ${TEST_NAME}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Resolution: ${RESO}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Cluster: ${CLUSTER}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Partition: ${CLUSTER_PARTITION}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Nodes: ${NBNODES}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"MPI per node: ${ACT_MPI}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"OMP threads: ${ACT_OMP}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Job ID: \${SLURM_JOBID}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"Node list: \${SLURM_JOB_NODELIST}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"#########################################\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "" >> "$OUTPUT_FILE"

   # run command
   if (( ACT_MPI == 0 )); then
      COMMANDSTRING="./${THIS_EXEC} ${TEST_NAMELIST} >> ${LOGFILE_RUN}"
   else
      COMMANDSTRING="$(eval echo ${RUN_COMMAND}) ./${THIS_EXEC} ${TEST_NAMELIST} >> ${LOGFILE_RUN}"
   fi   
   echo "$COMMANDSTRING" >> "$OUTPUT_FILE"
   echo "" >> "$OUTPUT_FILE"

   #----------------------------------------------------------------------
   # launch job multiple times
   #----------------------------------------------------------------------

   for iter in $(seq $ITERS); do
      SUBMIT_MESSAGE=$(sbatch job.sh)
      STRINGARRAY=($SUBMIT_MESSAGE)
      JOB_ID=${STRINGARRAY[-1]}
      echo "Launched ${TEST_NAME} ${RESO} on ${NBNODES} nodes with ${ACT_MPI} procs/node and ${ACT_OMP} threads/proc [JOB ID ${JOB_ID}]" | tee -a $LOGFILE;
   done

   cd ..

done
done
done
done


#######################################################################
# launch dependency job to gather results
#######################################################################

# TODO
#cd ${RAMSES_BENCHMARK_DIR}
#OUTPUT_FILE="io_${TEST_NAME}.sh"
#NBNODES=1
#NTASKS_PER_NODE=1
#CPUS_PER_TASK=1
#JOB_NAME=io-${TEST_NAME}
#source ${RAMSES_BENCHMARK_DIR}/HPCclusters/${CLUSTER}/job_script_params.sh
#source io_job.sh
#DEPS=$(squeue --noheader --format %i --name ${TEST_NAME} | paste -sd,)
#sbatch --dependency=${DEPS} $OUTPUT_FILE

#######################################################################
# Clean up
#######################################################################
if ${DELDATA} ; then
   cd ${RAMSES_BIN_DIR};
   make clean >> $LOGFILE 2>&1;
   #rm -f ${EXECNAME}*d;
fi

