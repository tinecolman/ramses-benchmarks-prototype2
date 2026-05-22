# RAMSES benchmarks

As of 2025, we continuously assess the performance of RAMSES on various supercomputers for a selection of typical setups. The scripts to do so have been developed in the context of the SPACE CoE project and are stored in this repository. The goal of these script is to make benchmarking RAMSES easy:
* for users, that need scaling plots for proposals,
* for developers, that need to verify performance,
* for maintainers, to verify code quality of pull requests.


## Benchmark setups

Benchmarks can be divided into several categories, and each benchmark may have several variations.

Classical benchmarks
* SEDOV: a Sedov explosion in 3D
   * [sedov](setups/sedov/description.md): on a uniform grid (SPACE use-case 1)
   * [sedov-amr](setups/sedov-amr/description.md): using AMR


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


## Browsing benchmark results per setup

* [sedov benchmark results]()


## How to do your own benchmarking

* [How to use the benchmark script](doc/how_to_use_script.md)
* [How to process the results](doc/how_to_analyse_result.md)
* [How to add a setup](doc/how_to_add_setup.md)
* [How to add a cluster](doc/how_to_add_cluster.md)
