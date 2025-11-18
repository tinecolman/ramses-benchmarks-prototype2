## How to add a new benchmark setup

To add a new benchmark setup, add a new subdirectory with the name in the `setups` directory. It should contain the following files:
   * `description.md`: a description of the setup and  which parts of the code it benchmarks
   * `config.txt`: the compilation parameters, (like for the test suite)
   * `<testname>_<reso>.nml` a series of RAMSES namelists for different resolutions
   * `scaling_config.sh`: parameters that specify which resolution to use for strong and weak scaling tests, as well as the execution time needed.

   