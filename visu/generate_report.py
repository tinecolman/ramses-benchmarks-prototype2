''' Construct a markdown page gathering the benchmark results
    from a given benchmark setup on a given cluster 
'''

from tagged_data import *
from resolutions import *
from evolution_execution_time import plot_execution_time_multinode, table_execution_time
from scaling_strong import plot_strong_scaling, table_strong_scaling
from scaling_weak import plot_weak_scaling, table_weak_scaling
from scaling_combo import plot_scaling_combo_inverse
from openmp_config_grid import plot_mpi_omp_grid
from openmp_nthreads_execution_time import plot_openmp_speedup_nthreads
from memory import plot_memory, table_memory
import argparse


#---------- Text of the markdown page ------------


def text_section_intro(args):
    return f"""# Benchmark: {args.benchmark} on {args.cluster}

Benchmark description: [{args.benchmark}](../setups/{args.benchmark}/description.md)

Cluster info: [{args.cluster}](../HPCclusters/{args.cluster}/cluster_description.md)

On this page:
* Evolution of execution time with code version (figure & table with speedup)
* Strong scaling evolution (figure & table with efficiency)
* [if unigrid] Weak scaling evolution (figure & table with efficiency)
* [if unigrid] Combination of strong and weak scaling of the latest code release (figure)
* Optimal MPI-OpenMP configuration (figures)
* Memory usage (figure & table)

"""


def text_section_scaling_combo(release_label,figfile):
    return f"""## Strong and weak scaling of the latest code release ({release_label})

![Scaling]({figfile})

This figure shows the strong and weak scaling of the latest official release ({release_label}).
Strong scaling can be inferred diagonally, while weak scaling is determined by reading horizontally.
Dotted lines show ideal scaling.
For the values of strong and weak scaling efficiency, see the tables in the previous sections.

"""


def text_section_execution_time(figfile, table_md):
    return f"""## Evolution of execution time with code version

![Evolution execution time]({figfile})

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

{table_md}

"""


def text_section_strong_scaling(figfile, table_md):
    return f"""## Strong scaling evolution

![Strong scaling]({figfile})

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

{table_md}

"""


def text_section_weak_scaling(figfile, table_md):
    return f"""## Weak scaling evolution

![Weak scaling]({figfile})

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

{table_md}

"""


def text_section_ompmpi_grid(data):
    return f"""## OpenMP configuration guidelines
    
The figures below give inside in the behaviour of OpenMP for different resolutions of this setup.
Shows is which MPI - OpenMP configuration is most optimal in terms of execution time.
The data is for the latest OpenMP version 
(commit {data[0]['metadata']['commit']} on branch {data[0]['metadata']['branch']})
, corresponding to the version used for the previous figures.

""" 


def text_section_memory(filename,table_md):
    return f"""## Memory usage

![Memory usage]({filename})

This figure shows the approximate memory per node needed to perform the simulation,
as derived from the log-file outputted by the code. Remark that the actual memory
allocated for the run on the node will be higher, depending on the percentage of 
the allocated ngridmax grids is actually used.
We show the consumption for a different number of OpenMP threads. 
Memory consumption is lower with OMP, due to
the reduced number of ghostzone cells needed to describe the boundaries of the 
MPI-domains.

The table lists the corresponding memory values in GB.
The last column lists the improvement of the OpenMP version with respect to the 
MPI-only version, that is the most optimistic fraction of the MPI-only memory that is needed 
when running with hybrid parallelisation.

Unless otherwise stated, data is for runs using full compute nodes.

{table_md}

"""


#---------- INPUT ------------

# Get command line arguments
parser = argparse.ArgumentParser(
    description='Update benchmark page'
)
parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
args = parser.parse_args()

# We always want to display the total time for this page
timer='total'
# get list of what resolutions are available for this benchmark
resos = get_resolutions(args.benchmark)
# get list of which node-resolution combinations to use for weak scaling
weak_scaling_map = get_weak_scaling_config2(args.benchmark)

# Write text with table of content
md = text_section_intro(args)


#--------- In this part, we deal with the time evolution between versions ------------

benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, timer)
reso = resos[-1] # we show only the highest resolution

if len(benchmarks)>0:

    # Execution time evolution
    figfile = f'../results/images/evo_exectime_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
    plot_execution_time_multinode(benchmarks, release_labels, reso, outname=figfile)
    table_md = table_execution_time(benchmarks, release_labels, reso, fmt='markdown')
    md += text_section_execution_time(figfile, table_md)

    # Strong scaling evolution
    figfile = f'../results/images/strong_scaling_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
    plot_strong_scaling(benchmarks, release_labels, reso, outname=figfile)
    table_md = table_strong_scaling(benchmarks, release_labels, reso, fmt='markdown')
    md += text_section_strong_scaling(figfile, table_md)

if len(benchmarks)>0 and args.benchmark in ['sedov', 'cosmo']:

    # Weak scaling evolution
    nodes, resos = get_weak_scaling_config(args.benchmark)
    figfile = f'../results/images/weak_scaling_{args.benchmark}_{timer}_{args.cluster}.png'
    plot_weak_scaling(benchmarks, release_labels, nodes, resos, outname=figfile)
    table_md = table_weak_scaling(benchmarks, release_labels, nodes, resos, fmt='markdown')
    md += text_section_weak_scaling(figfile, table_md)


#--------- In this part, we deal with the latest official release ------------

data, release_label = load_latest_release_data(args.cluster, args.benchmark, timer)

if len(data)>0 and args.benchmark in ['sedov', 'cosmo']:

    # Strong and weak scaling combo figure
    figfile = f'../results/images/scaling_combo_{args.benchmark}_{timer}_{args.cluster}.png'
    plot_scaling_combo_inverse(data,resos,weak_scaling_map, outname=figfile)
    md += text_section_scaling_combo(release_label,figfile)


#--------- In this part, we deal with the latest OpenMP version ------------

data = load_latest_openmp_data(args.cluster, args.benchmark, timer)

if len(data)>0:

    # MPI-OpenMP config grid for execution time on 1 node
    md += text_section_ompmpi_grid(data)
    for reso in resos:
        figfile_grid_omp = f'../results/images/mpi_omp_grid_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
        error = plot_mpi_omp_grid(data, reso, fig_name=figfile_grid_omp, show_overhead=False)
        if not error:
            md += f"""![MPI-OMP]({figfile_grid_omp})
"""

    # gain with respect to MPI-only on multiple nodes
    reso = resos[-1]
    figfile_omp_speedup = f'../results/images/omp_speedup_{args.benchmark}_{reso}_{args.cluster}.png'
    error = plot_openmp_speedup_nthreads(data, reso, fig_name=figfile_omp_speedup)
    if not error:
        md += f"""![OMP-speedup]({figfile_omp_speedup})
"""

    # Memory
    reso = resos[-1]
    filename = f'../results/images/memory_{args.benchmark}_{reso}_{args.cluster}.png'
    plot_memory(data, reso, outname=filename)
    table_md = table_memory(data, reso, fmt='markdown')
    md += text_section_memory(filename,table_md)


#--------- Output markdown page ------------

outfile = f"../results/results_{args.benchmark}_{args.cluster}.md"
with open(outfile, 'w') as f:
    f.write(md)
print(f"Wrote documentation page: {outfile}")

