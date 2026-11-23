#!/bin/bash
#######################################################################
#
# Slurm helpers, used by launch_benchmark_suite.sh (sourced from it, it uses
# the variables of the launcher).
#
# select_allocation: choose the project allocation (account) to run on,
#                    when it is not given with -a
# wait_for_job:      wait until a job has ended, and tell whether it completed
#
#######################################################################

# Set CLUSTER_ALLOCATION_ID from the projects of the user: the only one, or
# the one chosen from a list
select_allocation () {
   # Get the list of project IDs for the current user (works only for slurm)
   #   - ignoring headers (tail -n +3)
   #   - taking care of long account names (format=Account%-40)
   #   - removing duplicates (sort -u)
   local MY_PROJECTS NUM_PROJECTS
   MY_PROJECTS=$(sacctmgr show associations user=$USER format=Account%-40 | tail -n +3 | awk '{print $1}' | sort -u)

   # Count the number of projects (echo of an empty list gives one line)
   if [[ -z "$MY_PROJECTS" ]]; then
      NUM_PROJECTS=0
   else
      NUM_PROJECTS=$(echo "$MY_PROJECTS" | wc -l)
   fi

   # Process the number of projects
   if [[ $NUM_PROJECTS -eq 1 ]]; then
      CLUSTER_ALLOCATION_ID=$(echo "$MY_PROJECTS" | xargs)
      log "Automatically selected allocation ID: $CLUSTER_ALLOCATION_ID"

   elif [[ $NUM_PROJECTS -gt 1 ]]; then
      # if multiple projects are found, present the user with a list to select from
      echo "Multiple projects found. Please select one:"
      select CLUSTER_ALLOCATION_ID in $MY_PROJECTS; do
         if [[ -n "$CLUSTER_ALLOCATION_ID" ]]; then
            CLUSTER_ALLOCATION_ID=$(echo "$CLUSTER_ALLOCATION_ID" | xargs)
            log "You selected allocation ID: $CLUSTER_ALLOCATION_ID"
            break
         else
            echo "Invalid selection, please try again."
         fi
      done

   else
      log "No valid allocation ID found."
      exit 1
   fi
}

# Wait until job $1 has ended. Returns 0 if it completed successfully and 1
# otherwise; JOB_STATE holds the final state.
wait_for_job () {
   local job_id=$1
   while true; do
      JOB_STATE=$(sacct --jobs=$job_id --noheader --format=JobID,State | awk -v job_id="$job_id" '$1 == job_id {print $2}')
      case "$JOB_STATE" in

         # finished successfully
         COMPLETED)
            return 0
            ;;

         # not finished yet (empty: not yet known to sacct)
         "" | PENDING | CONFIGURING | RUNNING | COMPLETING | REQUEUED | SUSPENDED)
            ;;

         # any other state: FAILED, CANCELLED, TIMEOUT, OUT_OF_MEMORY, NODE_FAIL, ...
         *)
            return 1
            ;;

      esac
      # Sleep for a while before checking the status again
      sleep 15
   done
}
