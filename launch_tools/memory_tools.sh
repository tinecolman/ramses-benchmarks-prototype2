#!/bin/bash
#######################################################################
#
# Memory needed by a run and choice of the node type, used by
# launch_benchmark_suite.sh (sourced from it, it uses the variables of the
# launcher).
#
# estimate_memory:  memory per node needed by a run, from its namelist
# choose_node_type: smallest node type of the cluster with enough memory
#
# The memory per MPI rank is estimated as
#    MEM_PER_GRID_KB        x allocated grids per rank
#  + MEM_PER_PARTICLE_B     x allocated particles per rank
#  + MEM_PER_RANK_GB
#  + MEM_PER_RANK_IN_RUN_KB x number of ranks in the run
#  + MPI_MEMORY_PER_PROCESS_GB
# The first four are set in the scaling_config.sh of the setup (fitted on
# measured runs), the last one in the cluster_info.sh of the cluster (memory
# of the MPI library). The allocated grids and particles per rank are read
# from the namelist of the run: ngridmax (npartmax), or ngridtot (nparttot)
# divided over the ranks. The memory per node is that times the ranks per
# node, times MEM_SAFETY_FACTOR.
#
# The node types are set in the cluster_info.sh of the cluster, smallest
# memory first:
#    NODE_TYPES        names, used by job_script_params.sh of the cluster
#    NODE_MEMORY_GB    usable memory per node
#    NODE_MAX_NODES    maximum number of nodes per job (0: no limit)
#
#######################################################################

MEM_SAFETY_FACTOR=${MEM_SAFETY_FACTOR:-1.1}

# Value of parameter $2 in namelist $1 (empty if not set), without comment
namelist_value () {
   grep -i "^\s*$2\s*=" $1 | head -n 1 | sed 's/!.*//' | cut -d'=' -f2 | tr -d ' ' | tr 'dD' 'ee'
}

# Set MEM_ESTIMATE_GB to the memory per node needed by the run with namelist
# $1, $2 MPI ranks in total and $3 ranks per node (empty if the setup has no
# memory estimate)
estimate_memory () {
   local namelist=$1 nranks=$2 ranks_node=$3
   MEM_ESTIMATE_GB=""
   if [[ -z "$MEM_PER_RANK_GB" ]]; then
      return
   fi
   local ngridmax ngridtot npartmax nparttot
   ngridmax=$(namelist_value $namelist ngridmax)
   ngridtot=$(namelist_value $namelist ngridtot)
   npartmax=$(namelist_value $namelist npartmax)
   nparttot=$(namelist_value $namelist nparttot)
   MEM_ESTIMATE_GB=$(awk -v ngridmax="$ngridmax" -v ngridtot="$ngridtot" \
                         -v npartmax="$npartmax" -v nparttot="$nparttot" \
                         -v nranks=$nranks -v ranks_node=$ranks_node \
                         -v per_grid=${MEM_PER_GRID_KB:-0} -v per_part=${MEM_PER_PARTICLE_B:-0} \
                         -v per_rank=${MEM_PER_RANK_GB:-0} -v per_rank_run=${MEM_PER_RANK_IN_RUN_KB:-0} \
                         -v mpi=${MPI_MEMORY_PER_PROCESS_GB:-0} -v factor=$MEM_SAFETY_FACTOR 'BEGIN {
      grids = (ngridmax != "") ? ngridmax : ngridtot/nranks
      parts = (npartmax != "") ? npartmax : nparttot/nranks
      rank = per_grid*1e-6*grids + per_part*1e-9*parts + per_rank + per_rank_run*1e-6*nranks + mpi
      printf "%.0f\n", rank*ranks_node*factor
   }')
}

# Set NODE_TYPE to the first node type with enough memory for MEM_ESTIMATE_GB
# and allowing NBNODES nodes. Without node types or memory estimate, it is the
# first node type (empty if there are none). Returns 1 if no node type fits.
choose_node_type () {
   NODE_TYPE=${NODE_TYPES[0]:-}
   if [[ -z "$MEM_ESTIMATE_GB" || ${#NODE_TYPES[@]} -eq 0 ]]; then
      return 0
   fi
   local i max
   for i in "${!NODE_TYPES[@]}"; do
      max=${NODE_MAX_NODES[$i]:-0}
      if (( MEM_ESTIMATE_GB <= NODE_MEMORY_GB[i] && (max == 0 || NBNODES <= max) )); then
         NODE_TYPE=${NODE_TYPES[$i]}
         return 0
      fi
   done
   NODE_TYPE=""
   return 1
}
