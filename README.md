# RAMSES benchmarks

As of 2025, we continuously assess the performance of RAMSES on various supercomputers for a selection of typical setups. The scripts to do so have been developed in the context of the SPACE CoE project and are stored in this repository. The goal of these script is to make benchmarking RAMSES easy:
* for users, that need scaling plots for proposals,
* for developers, that need to verify performance,
* for maintainers, to verify code quality of pull requests.


## Browsing benchmark results

| Cluster     | sedov        | sedov-amr    | cosmo        | cosmo-amr    | galaxy       |
| ----------- | :-----------:| :----------: | :----------: | :----------: | :----------: |
| Meluxina    | [✓][SED-MEL] | [✓][SAM-MEL] | [✓][COS-MEL] | [✓][CAM-MEL] | [✓][GAL-MEL] |
| Marenostrum | [✓][SED-MAR] | [✓][SAM-MAR] | [][COS-MAR] | [][CAM-MAR] | [][GAL-MAR] |

[SED-MEL]: results/results_sedov_meluxina.md
[SAM-MEL]: results/results_sedov-amr_meluxina.md
[COS-MEL]: results/results_cosmo_meluxina.md
[CAM-MEL]: results/results_cosmo-amr_meluxina.md
[GAL-MEL]: results/results_galaxy_meluxina.md

[SED-MAR]: results/results_sedov_marenostrum.md
[SAM-MAR]: results/results_sedov-amr_marenostrum.md
[COS-MAR]: results/results_cosmo_marenostrum.md
[CAM-MAR]: results/results_cosmo-amr_marenostrum.md
[GAL-MAR]: results/results_galaxy_marenostrum.md


## Benchmark setups

Benchmarks can be divided into several categories, and each benchmark may have several variations.

Classical benchmarks
* SEDOV: a Sedov explosion in 3D
   * [sedov](setups/sedov/description.md): on a uniform grid (SPACE use-case 1)
   * [sedov-amr](setups/sedov-amr/description.md): using AMR

Cosmological volumes
* COSMO: a dark matter-only simulation
   * [cosmo](setups/cosmo/description.md): using a uniform grid (SPACE use-case 2)
   * [cosmo-amr](setups/cosmo-amr/description.md): using an AMR grid

Isolated galaxies
* GALAXY: agora galaxy setup
   * [galaxy](setups/galaxy/description.md): gas, stars and DM with refinement, but no star formation (SPACE use-case 3)


Interstellar mediumm

Prestellar cores
* COLLAPSE: Boss-Bodenheimer setup of a gravitationally collapsing core forming a binary
   * [COLLAPSE-mhd](setups/collapse-MHD/description.md): 


## Computing clusters

EuroHPC
* [LUMI](HPCclusters/lumi/cluster_description.md)
* [Leonardo](HPCclusters/leonardo/cluster_description.md)
* [MareNostrum](HPCclusters/marenostrum/cluster_description.md)
* [MeluXina](HPCclusters/meluxina/cluster_description.md)
* [Discoverer](HPCclusters/discoverer/cluster_description.md)
* [Vega](HPCclusters/vega/cluster_description.md)
* [Karolina](HPCclusters/karolina/cluster_description.md)
* [Deucalion](HPCclusters/deucalion/cluster_description.md)


## How to do your own benchmarking

* [How to use the benchmark script](doc/how_to_use_script.md)
* [How to process the results](doc/how_to_analyse_result.md)
* [How to add a setup](doc/how_to_add_setup.md)
* [How to add a cluster](doc/how_to_add_cluster.md)
