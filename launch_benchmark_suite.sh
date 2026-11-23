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
#   -i: how many runs to launch of a benchmark, to take the average time (default 3)
#       ./launch_benchmark_suite.sh -i 5
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

# defaults for the per-rank allocation of grids and particles, which can be
# overwritten in scaling_config.sh (see adapt_allocation below)
ALLOC_GHOST_COEF=""
ALLOC_OCCUPANCY=0.7
ALLOC_TARGET=0.8

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

# list branches which contain this commit: git branch --contains 0f908c1
# check if dev is in the list, if yes-> set branch to dev.
COMMIT=$(git rev-parse --short HEAD)
COMMIT_DATE=$(git show --no-patch --format=%cd --date=format:'%Y-%m-%d')
GIT_URL=$(git config --get remote.origin.url | sed 's/git@github.com:/https:\/\/github.com\//g')
GIT_URL=${GIT_URL:0:$((${#GIT_URL}-4))}

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
# Per-rank allocation of grids and particles
#######################################################################

# RAMSES divides ngridtot (nparttot) of the namelist over the MPI ranks.
# With many ranks, the ghost zones around the domain of each rank take up a
# growing fraction of the allocated grids, until the run fails with
# "Increase ngridmax". For setups that set ALLOC_GHOST_COEF in their
# scaling_config.sh, ngridtot is replaced by a per-rank ngridmax that leaves
# room for the ghost zones, when ngridtot/nranks is too small:
#    own      = ALLOC_OCCUPANCY * ngridtot / nranks   (grids owned per rank)
#    need     = own * (1 + ALLOC_GHOST_COEF * own^(-1/3))
#    ngridmax = need / ALLOC_TARGET
# The same is done for nparttot. ALLOC_GHOST_COEF=12 fits the unigrid cosmo
# and sedov runs. AMR setups have more complex domains and load imbalance,
# so the coefficient would have to be determined for each of them.

# Per-rank allocation for a total over all ranks, or nothing if the total
# divided over the ranks is large enough
per_rank_allocation () {
   local total=$1
   local nranks=$2
   awk -v total=$total -v nranks=$nranks -v occupancy=$ALLOC_OCCUPANCY \
       -v coef=$ALLOC_GHOST_COEF -v target=$ALLOC_TARGET 'BEGIN {
      base = total/nranks
      own = occupancy*base
      need = own*(1 + coef*own^(-1./3.))
      if (need/target > base) printf "%d\n", need/target + 0.5
   }'
}

# Replace ngridtot (nparttot) in the namelist by ngridmax (npartmax) if needed
adapt_allocation () {
   local namelist=$1
   local nranks=$2
   if [[ -z "$ALLOC_GHOST_COEF" ]]; then
      return
   fi
   local total_name per_rank_name total per_rank
   for total_name in ngridtot nparttot; do
      per_rank_name=${total_name/tot/max}
      # skip if the namelist sets the per-rank value itself
      if grep -qi "^\s*${per_rank_name}\s*=" $namelist; then
         continue
      fi
      # value without trailing comment, e.g. "ngridtot=220000000 !comment"
      total=$(grep -i "^\s*${total_name}\s*=" $namelist | sed 's/!.*//' | cut -d'=' -f2 | tr -d ' ')
      if [[ -z "$total" ]]; then
         continue
      fi
      per_rank=$(per_rank_allocation $total $nranks)
      if [[ -n "$per_rank" ]]; then
         sed -i "s/^\(\s*\)${total_name}\s*=.*/\1${per_rank_name}=${per_rank} ! instead of ${total_name}=${total} for ${nranks} MPI ranks/I" $namelist
         echo "   ${total_name}=${total} replaced by ${per_rank_name}=${per_rank} for ${nranks} MPI ranks" | tee -a $LOGFILE
      fi
   done
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
   adapt_allocation ${TEST_NAMELIST} $(( NBNODES * (ACT_MPI > 0 ? ACT_MPI : 1) ))

   # TO TEST
   ## adjust the test time if needed
   #TIME_SCALE=$(awk "BEGIN {print ${CLUSTER_CORES_PER_NODE}/${CORES_PER_NODE}}")
   ## convert reference time to seconds
   #IFS=: read HH MM SS <<< "$FULL_NODE_TIME"
   #BASE_SECONDS=$((10#$HH * 3600 + 10#$MM * 60 + 10#$SS))
   #SCALED_SECONDS=$(awk "BEGIN {print int(${BASE_SECONDS} * ${TIME_SCALE})}")
   ## convert back to HH:MM:SS
   #TEST_TIME=$(printf '%02d:%02d:%02d' \
   #   $((SCALED_SECONDS/3600)) \
   #   $(((SCALED_SECONDS%3600)/60)) \
   #   $((SCALED_SECONDS%60)))

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
