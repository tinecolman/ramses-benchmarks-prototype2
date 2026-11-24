TEST_TIME=00:20:00
# per-rank allocation of grids and particles for many MPI ranks,
# see adapt_ngridmax in ngridmax_tools.sh
ALLOC_GHOST_COEF=12

# memory estimate per MPI rank (see memory_tools.sh), fitted on the LUMI runs
# of the openmp branch of 2026-10/11: per allocated grid (kB), per allocated
# particle (bytes), fixed per rank (GB), per rank in the run (kB)
MEM_PER_GRID_KB=0.31
MEM_PER_PARTICLE_B=124
MEM_PER_RANK_GB=0.22
MEM_PER_RANK_IN_RUN_KB=17
