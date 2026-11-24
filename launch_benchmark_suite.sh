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
#   -a: project account to run on (if not given, it is looked up or asked)
#       ./launch_benchmark_suite.sh -a EUR123456
#   -p: set the number of MPI processes used per node, allows to use partial nodes (0=no MPI)
#       ./launch_benchmark_suite.sh -p "1 32 64 128"
#   -m: run with openmp with different number of omp threads
#       ./launch_benchmark_suite.sh -m "1 2 4 8 16"
#   -i: how many runs to launch of a benchmark, to take the average time (default 1)
#       ./launch_benchmark_suite.sh -i 3
#   -v: use mini-ramses
#   -s: path to the RAMSES (or mini-ramses with -v) source code
#       (otherwise taken from environment variable RAMSES_SOURCE_DIR or MINI_RAMSES_SOURCE_DIR)
#       The version used is the one currently checked out by git.
#       ./launch_benchmark_suite.sh -s $HOME/my_ramses
#
#######################################################################

#######################################################################
# Parse input parameters
#######################################################################

# command line as typed, for launches.txt (arguments with spaces in quotes)
COMMAND_LINE="$0"
for arg in "$@"; do
   if [[ "$arg" == *" "* ]]; then
      COMMAND_LINE+=" \"$arg\""
   else
      COMMAND_LINE+=" $arg"
   fi
done

# location of the source code, if not set in the environment (see -s)
RAMSES_SOURCE_DIR="${RAMSES_SOURCE_DIR:-$HOME/ramses}"
MINI_RAMSES_SOURCE_DIR="${MINI_RAMSES_SOURCE_DIR:-$HOME/mini-ramses}"

# Default options
CLUSTER=""
TEST_NAME=""
RESO_LIST=""
NODES_LIST=""
CLUSTER_ACCOUNT="none"
MPI_PROC_LIST="max"
OMP_THREAD_LIST="0"
ITERS=1
USE_MINIRAMSES=false
SOURCE_DIR_OPTION=""

# Parse options
while getopts "c:a:b:n:r:p:m:i:vs:" OPTION; do
   case $OPTION in
      c) CLUSTER=$OPTARG ;;
      a) CLUSTER_ACCOUNT=$OPTARG ;;
      b) TEST_NAME=$OPTARG ;;
      n) NODES_LIST=($OPTARG) ;;   # Convert input string into an array
      r) RESO_LIST=($OPTARG) ;;
      p) MPI_PROC_LIST=($OPTARG) ;;
      m) OMP_THREAD_LIST=($OPTARG) ;;
      i) ITERS=$OPTARG ;;
      v) USE_MINIRAMSES=true ;;
      s) SOURCE_DIR_OPTION=$OPTARG ;;
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

# directory of this script, holding the setups and cluster settings
RAMSES_BENCHMARK_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CLUSTER_DIR="${RAMSES_BENCHMARK_DIR}/HPCclusters/${CLUSTER}"
CLUSTER_INFO="${CLUSTER_DIR}/cluster_info.sh"
MODULES="${CLUSTER_DIR}/modules.sh"
if $USE_MINIRAMSES ; then
   RAMSES_BIN_DIR="${SOURCE_DIR_OPTION:-$MINI_RAMSES_SOURCE_DIR}/bin";
   SETUPS_DIR="setups-mini-ramses";
else
   RAMSES_BIN_DIR="${SOURCE_DIR_OPTION:-$RAMSES_SOURCE_DIR}/bin";
   SETUPS_DIR="setups";
fi
SETUP_DIR="${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}"

# Names of the subdirectories of $1 that contain the file $2, on one line
available () {
   local d
   for d in $1/*/; do
      [[ -f $d/$2 ]] && echo -n "$(basename $d) "
   done
}

# check that the cluster, the benchmark and its resolutions exist
if [[ ! -f "${CLUSTER_DIR}/cluster_info.sh" ]]; then
   echo "ERROR: unknown cluster '${CLUSTER}' (-c), available: $(available ${RAMSES_BENCHMARK_DIR}/HPCclusters cluster_info.sh)" >&2
   exit 1
fi
if [[ ! -f "${SETUP_DIR}/scaling_config.sh" ]]; then
   echo "ERROR: unknown benchmark '${TEST_NAME}' (-b), available: $(available ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR} scaling_config.sh)" >&2
   exit 1
fi
for reso in "${RESO_LIST[@]}"; do
   if [[ ! -f "${SETUP_DIR}/${TEST_NAME}_${reso}.nml" ]]; then
      resos=$(cd ${SETUP_DIR} && ls ${TEST_NAME}_*.nml 2>/dev/null | sed "s/^${TEST_NAME}_//; s/\.nml$//" | tr '\n' ' ')
      echo "ERROR: no namelist ${TEST_NAME}_${reso}.nml for resolution '${reso}' (-r), available: ${resos}" >&2
      exit 1
   fi
done

EXECNAME="benchmark_exe_"

LOGFILE="${RAMSES_BENCHMARK_DIR}/benchmark_suite.log";

# print a message and add it to the logfile (arguments as for echo)
log () {
   echo "$@" | tee -a $LOGFILE
}

# MPI-only runs up to this number of nodes use the large memory nodes of the
# cluster, if it has them (see job_script_params.sh of the cluster), for the
# resolutions in LARGEMEM_MPI_RESOS (none if empty). Both can be overwritten
# in scaling_config.sh
LARGEMEM_MPI_MAX_NODES=0
LARGEMEM_MPI_RESOS=""

# load benchmark configuration
source ${SETUP_DIR}/scaling_config.sh

#######################################################################
# Get code repository info
#######################################################################

if [[ ! -d "$RAMSES_BIN_DIR" ]]; then
   log "ERROR: RAMSES bin directory ${RAMSES_BIN_DIR} not found"
   log "       Give the path to the source code with -s, or set RAMSES_SOURCE_DIR"
   exit 1
fi

# git in the RAMSES repository, without changing directory
ramses_git () {
   git -C "$RAMSES_BIN_DIR" "$@"
}

COMMIT=$(ramses_git rev-parse --short HEAD)
COMMIT_DATE=$(ramses_git show --no-patch --format=%cd --date=format:'%Y-%m-%d')
GIT_URL=$(ramses_git config --get remote.origin.url | sed 's/git@github.com:/https:\/\/github.com\//g')
GIT_URL=${GIT_URL%.git}

# uncommitted changes to the tracked files, recorded with the builds; taken
# now, since the source may be edited while the compile job is waiting
GIT_DIFF=$(ramses_git diff HEAD)
if [[ -z "$GIT_DIFF" ]]; then
   UNCOMMITTED="no"
else
   UNCOMMITTED="yes"
fi

# commit of these benchmark scripts ("+": uncommitted changes), for launches.txt
BENCHMARKS_COMMIT=$(git -C "$RAMSES_BENCHMARK_DIR" rev-parse --short HEAD 2>/dev/null)
if [[ -z "$BENCHMARKS_COMMIT" ]]; then
   BENCHMARKS_COMMIT="unknown"
elif ! git -C "$RAMSES_BENCHMARK_DIR" diff --quiet HEAD; then
   BENCHMARKS_COMMIT+="+"
fi

# fingerprint of the setup files (compile flags, scaling configuration and
# namelists, not the initial conditions), to recognise runs made with the
# same setup across versions of the benchmark scripts
SETUP_HASH=$(cat ${SETUP_DIR}/config.txt ${SETUP_DIR}/scaling_config.sh ${SETUP_DIR}/*.nml | sha256sum | cut -c1-12)

BRANCH=$(ramses_git rev-parse --abbrev-ref HEAD)
# if detached HEAD, check if the commit is from on the dev branch
if [[ "$BRANCH" == "HEAD" ]]; then
   if ramses_git merge-base --is-ancestor "$COMMIT" origin/dev; then
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
log -e "${COLOR}################################################${NC}"
log -e "${COLOR}#    Launching RAMSES performance benchmark    #${NC}"
log -e "${COLOR}################################################${NC}"
log "Repository url: ${GIT_URL}"
log "Branch: ${BRANCH}"
log "Commit hash: ${COMMIT}"
log "Benchmark: ${TEST_NAME}"
echo "--------------------------------------------" >> $LOGFILE


#######################################################################
# Select project account to run on, if not given by user
#######################################################################

source ${RAMSES_BENCHMARK_DIR}/slurm_tools.sh

if [[ "$CLUSTER_ACCOUNT" == "none" ]]; then
   select_account
fi

# load cluster info (to be done after the account is set)
source ${CLUSTER_INFO}

# nodes to keep out of the jobs, from bad_nodes.txt of the cluster (read_bad_nodes)
read_bad_nodes

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

mkdir -p ${BUILD_DIR} || { log "ERROR: cannot create ${BUILD_DIR}"; exit 1; }


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

JOB_NAME=$TEST_NAME

# record this launch in the setup directory: date, commits of the benchmark
# scripts and of RAMSES ("+": uncommitted changes), and the command line
LAUNCHES_FILE=${LAUNCH_DIR}/launches.txt
if [[ ! -f $LAUNCHES_FILE ]]; then
   echo "# date time  commits of the benchmark scripts and of RAMSES (+: uncommitted changes)  command" > $LAUNCHES_FILE
fi
RAMSES_COMMIT=${COMMIT}
[[ "$UNCOMMITTED" == "yes" ]] && RAMSES_COMMIT+="+"
echo "$(date '+%F %T')  benchmarks=${BENCHMARKS_COMMIT}  ramses=${RAMSES_COMMIT}  ${COMMAND_LINE}" >> $LAUNCHES_FILE

# per-rank ngridmax (npartmax) in the namelists for many MPI ranks (adapt_ngridmax)
source ${RAMSES_BENCHMARK_DIR}/ngridmax_tools.sh

# job script of a run (write_job_script)
source ${RAMSES_BENCHMARK_DIR}/job_tools.sh

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
   RUN_DIR=${LAUNCH_DIR}/reso${RESO}_nodes${NBNODES}_cores${CORES_PER_NODE}_mpi${ACT_MPI}_omp${ACT_OMP}
   mkdir -p ${RUN_DIR} || { log "ERROR: cannot create ${RUN_DIR}"; exit 1; }

   # the executable is run from the builds (path relative to the run
   # directory, where the job runs), only the input file is copied
   EXEC_PATH=../builds/${THIS_EXEC}
   TEST_NAMELIST=${TEST_NAME}_${RESO}.nml
   cp ${RAMSES_BENCHMARK_DIR}/${SETUPS_DIR}/${TEST_NAME}/${TEST_NAMELIST} ${RUN_DIR}/
   # leave room for the ghost zones when there are many MPI ranks
   adapt_ngridmax ${RUN_DIR}/${TEST_NAMELIST} $(( NBNODES * (ACT_MPI > 0 ? ACT_MPI : 1) ))

   #----------------------------------------------------------------------
   # Create job script (see job_tools.sh)
   #----------------------------------------------------------------------

   write_job_script

   #----------------------------------------------------------------------
   # launch job multiple times
   #----------------------------------------------------------------------

   for iter in $(seq $ITERS); do
      SUBMIT_MESSAGE=$(sbatch ${SBATCH_EXCLUDE} --chdir=${RUN_DIR} ${OUTPUT_FILE})
      STRINGARRAY=($SUBMIT_MESSAGE)
      JOB_ID=${STRINGARRAY[-1]}
      log "Launched ${TEST_NAME} ${RESO} on ${NBNODES} nodes with ${ACT_MPI} procs/node and ${ACT_OMP} threads/proc [JOB ID ${JOB_ID}]"
   done

done
done
done
done
