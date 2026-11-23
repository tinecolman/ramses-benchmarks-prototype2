#!/bin/bash
#######################################################################
#
# Per-rank allocation of grids and particles, used by
# launch_benchmark_suite.sh (sourced from it, after the scaling_config.sh
# of the setup, whose values of the parameters below are kept).
#
#######################################################################

# defaults, used for the parameters not set in scaling_config.sh
ALLOC_GHOST_COEF=${ALLOC_GHOST_COEF:-}   # empty: no adaptation
ALLOC_OCCUPANCY=${ALLOC_OCCUPANCY:-0.7}
ALLOC_TARGET=${ALLOC_TARGET:-0.8}

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
per_rank_ngridmax () {
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
adapt_ngridmax () {
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
      per_rank=$(per_rank_ngridmax $total $nranks)
      if [[ -n "$per_rank" ]]; then
         sed -i "s/^\(\s*\)${total_name}\s*=.*/\1${per_rank_name}=${per_rank} ! instead of ${total_name}=${total} for ${nranks} MPI ranks/I" $namelist
         log "   ${total_name}=${total} replaced by ${per_rank_name}=${per_rank} for ${nranks} MPI ranks"
      fi
   done
}
