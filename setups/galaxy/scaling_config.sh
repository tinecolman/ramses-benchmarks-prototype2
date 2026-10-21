TEST_TIME=00:20:00
# MPI-only highres does not fit in the memory of a standard node up to 4 nodes,
# see LARGEMEM_MPI_MAX_NODES in launch_benchmark_suite.sh
LARGEMEM_MPI_MAX_NODES=4
LARGEMEM_MPI_RESOS="highres"
