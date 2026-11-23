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
#       ./launch_benchmark_suite.sh -b sedov
#   -r: (mandatory) set a list of which resolutions to use
#       ./launch_benchmark_suite.sh -r "256 512 1024"
#   -n: (mandatory) set a list of number of nodes to use
#       ./launch_benchmark_suite.sh -n "1 2 4"
#   -a: specify allocation ID
#       ./launch_benchmark_suite.sh -a EUR123456
#   -p: set the number of MPI processes used per node, allows to use partial nodes (0=no MPI)
#       ./launch_benchmark_suite.sh -p "1 32 64 128"
#   -m: run with openmp with different number of omp threads
#       ./launch_benchmark_suite.sh -m "1 2 4 8 16"
#   -i: how many runs to launch of a benchmark, to take the average time (default 1)
#       ./launch_benchmark_suite.sh -i 3
#   -v: use mini-ramses
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
MPI_PROC_LIST="max"
OMP_THREAD_LIST="0"
ITERS=1
USE_MINIRAMSES=false

# Parse options
while getopts "c:a:b:n:r:p:m:i:v" OPTION; do
   case $OPTION in
      c) CLUSTER=$OPTARG ;;
      a) CLUSTER_ALLOCATION_ID=$OPTARG ;;
      b) TEST_NAME=$OPTARG ;;
      n) NODES_LIST=($OPTARG) ;;   # Convert input string into an array
      r) RESO_LIST=($OPTARG) ;;
      p) MPI_PROC_LIST=($OPTARG) ;;
      m) OMP_THREAD_LIST=($OPTARG) ;;
      i) ITERS=$OPTARG ;;
      v) USE_MINIRAMSES=true ;;
   esac
done

# Validate input
if [[ -z "$CLUSTER" ]]; then
   echo "ERROR: you must specify a cluster with -c (e.g. meluxina)" >&2
   exit 1
fi
if [[ -z "$TEST_NAME" ]]; then
   echo "ERROR: you must specify a benchmark with -b (e.g. sedov)" >&2
   exit 1
fi
if [[ -z "$RESO_LIST" ]]; then
   echo "ERROR: you must specify the resolutions with -r (e.g. \"256 512 1024\")" >&2
   exit 1
fi
if [[ -z "$NODES_LIST" ]]; then
   echo "ERROR: you must specify the number of nodes to use with -n (e.g. \"1 2 4\")" >&2
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

LOGFILE="${RAMSES_BENCHMARK_DIR}/benchmark_suite.log";

# MPI-only runs up to this number of nodes use the large memory nodes of the
# cluster, if it has them (see job_script_params.sh of the cluster), for the
# resolutions in LARGEMEM_MPI_RESOS (none if empty). Both can be overwritten
# in scaling_config.sh
LARGEMEM_MPI_MAX_NODES=0
LARGEMEM_MPI_RESOS=""

# load benchmark configuration
source ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}/scaling_config.sh

#######################################################################
# Get code repository info
#######################################################################

cd $RAMSES_BIN_DIR

COMMIT=$(git rev-parse --short HEAD)
COMMIT_DATE=$(git show --no-patch --format=%cd --date=format:'%Y-%m-%d')
GIT_URL=$(git config --get remote.origin.url | sed 's/git@github.com:/https:\/\/github.com\//g')
GIT_URL=${GIT_URL%.git}

# uncommitted changes to the tracked files, recorded with the builds; taken
# now, since the source may be edited while the compile job is waiting
GIT_DIFF=$(git diff HEAD)
if [[ -z "$GIT_DIFF" ]]; then
   UNCOMMITTED="no"
else
   UNCOMMITTED="yes"
fi

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

# load cluster info (to be done after allocation is set)
source ${CLUSTER_INFO}

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
# Create benchmark directory on scratch
#######################################################################

if $USE_MINIRAMSES ; then
   BENCHMARK_DIR=$CLUSTER_SCRATCH/mini-benchmark_${BRANCH}_${COMMIT_DATE}_${COMMIT};
else
   BENCHMARK_DIR=$CLUSTER_SCRATCH/benchmark_${BRANCH}_${COMMIT_DATE}_${COMMIT};
fi

# subdirectory for the setup, holding the run directories and the builds
LAUNCH_DIR=$BENCHMARK_DIR/${TEST_NAME}
BUILD_DIR=$LAUNCH_DIR/builds

set -e
mkdir -p ${BUILD_DIR} >> $LOGFILE 2>&1;
set +e


#######################################################################
# Builds (see build_tools.sh)
#######################################################################

source ${RAMSES_BENCHMARK_DIR}/build_tools.sh

# variants needed, their make commands and executable names
select_builds

# reuse the existing builds, compile the missing ones
prepare_builds

#######################################################################
# Loop over configuration: create job scripts and run simulations
#######################################################################

cd ${LAUNCH_DIR}

JOB_NAME=$TEST_NAME

# per-rank ngridmax (npartmax) in the namelists for many MPI ranks (adapt_ngridmax)
source ${RAMSES_BENCHMARK_DIR}/ngridmax_tools.sh

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

   # the executable is run from the builds, only the input file is copied
   EXEC_PATH=../builds/${THIS_EXEC}
   TEST_NAMELIST=${TEST_NAME}_${RESO}.nml
   cp ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}/${TEST_NAMELIST} .
   # leave room for the ghost zones when there are many MPI ranks
   adapt_ngridmax ${TEST_NAMELIST} $(( NBNODES * (ACT_MPI > 0 ? ACT_MPI : 1) ))

   #----------------------------------------------------------------------
   # Create job script
   #----------------------------------------------------------------------

   OUTPUT_FILE="job.sh"
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
   echo "echo \"Executable: builds/${THIS_EXEC}\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "echo \"#########################################\" >> ${LOGFILE_RUN}" >> "$OUTPUT_FILE"
   echo "" >> "$OUTPUT_FILE"

   # run command
   if (( ACT_MPI == 0 )); then
      COMMANDSTRING="${EXEC_PATH} ${TEST_NAMELIST} >> ${LOGFILE_RUN}"
   else
      COMMANDSTRING="$(eval echo ${RUN_COMMAND}) ${EXEC_PATH} ${TEST_NAMELIST} >> ${LOGFILE_RUN}"
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
