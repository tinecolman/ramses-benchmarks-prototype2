'''
Generate a markdown page on the performance of the OpenMP implementation,
using the latest OpenMP version only. The first part helps to choose the
MPI-OpenMP configuration, the second part compares the best configuration
with MPI-only.
Run from the visu directory:
    python generate_openmp_report.py -c marenostrum -b cosmo
'''

from collections import Counter
from tagged_data import load_latest_openmp_data, get_latest_openmp_dirs, EXCLUDED_COMPILERS
from resolutions import *
from evolution_execution_time import table_execution_time
from scaling_strong import plot_strong_scaling, table_strong_scaling
from scaling_weak import plot_weak_scaling, table_weak_scaling
from openmp_config_grid import plot_mpi_omp_grid
from openmp_nthreads_execution_time import plot_openmp_speedup_nthreads
from openmp_timer_breakdown import (load_timer_breakdown, select_full_node, select_main_timers,
                                    plot_timer_breakdown_configs, plot_timer_scaling)
from openmp_vs_mpi import (split_mpi_omp, get_available_nodes, plot_time_mpi_vs_omp,
                           plot_scaling_combo_mpi_vs_omp)
from memory import plot_memory, table_memory
import argparse

VARIANT_LABELS = ['MPI-only', 'best OpenMP']


#---------- Text of the markdown page ------------


def text_section_intro(args, data):
    return f"""# OpenMP performance: {args.benchmark} on {args.cluster}

Benchmark description: [{args.benchmark}](../setups/{args.benchmark}/description.md)

Cluster info: [{args.cluster}](../HPCclusters/{args.cluster}/cluster_description.md)

OpenMP version: commit {data[0]['metadata']['commit']} on branch {data[0]['metadata']['branch']}

This page looks at the hybrid MPI-OpenMP parallelisation of RAMSES.
The first part identifies the best MPI-OpenMP configuration,
which may depend on the number of nodes, and explains why.
The second part compares the best configuration with MPI-only.
Unless otherwise stated, all runs use the full compute node.
For the comparison with previous code versions, see the
[main benchmark page](results_{args.benchmark}_{args.cluster}.md).

On this page:
* Choosing the MPI-OpenMP configuration
    * Configuration grid on one node (figures)
    * Gain per number of threads (figures)
    * Timer breakdown (figures)
    * Memory usage (figure & table)
* OpenMP versus MPI-only
    * Execution time (figure & tables)
    * Strong scaling (figures & tables)
    * [if unigrid] Weak scaling (figure & table)
    * [if unigrid] Combination of strong and weak scaling (figure)

"""


def text_section_config():
    return """# Choosing the MPI-OpenMP configuration

"""


def text_section_grid():
    return """## Configuration grid on one node

These figures show the execution time on a single node for the combinations
of MPI processes and OpenMP threads per MPI process that use the full node,
which lie on the anti-diagonal. Green is fast, red is slow.

"""


def text_section_omp_speedup():
    return """## Gain per number of threads

These figures show the gain in execution time of the hybrid runs with respect to
the MPI-only run on the same number of nodes, for different numbers of OpenMP threads
per MPI process. A positive value means the hybrid run is faster.
The optimal number of threads may change with the number of nodes.

"""


def text_section_timer_breakdown(reso):
    return f"""## Timer breakdown

The different parts of the code do not benefit equally from OpenMP,
and do not scale equally with the number of nodes. This explains why the
optimal configuration depends on the number of nodes.
The timers are averaged over the MPI processes. Some timers are grouped:
"particles - update" (move and synchro) updates the positions and velocities of the particles,
"particles - book keeping" (make, merge and kill tree) maintains the particle linked lists.
Timers that never exceed 5% of the total time are grouped under "other".

The bar charts show the time spent in each part of the code for all configurations
on a given number of nodes (resolution {reso}). The number on top of each bar is
the gain with respect to MPI-only.

"""


def text_section_timer_scaling(figfile):
    return f"""The figure below shows how the time spent in each part of the code evolves
with the number of nodes, for MPI-only (dashed) and for the fastest
MPI-OpenMP configuration on that number of nodes (solid).

![Timer scaling]({figfile})

"""


def text_section_memory(figfile, table_md):
    return f"""## Memory usage

![Memory usage]({figfile})

This figure shows the approximate memory per node needed to perform the simulation,
as derived from the log file. Remark that the actual memory allocated for the run
will be higher, depending on which fraction of the allocated ngridmax grids is used.
Memory consumption is lower with OpenMP, due to the reduced number of ghost zone
cells needed to describe the boundaries of the MPI domains.

The table lists the memory in GB. The last column lists the lowest memory
of the hybrid runs as a fraction of the MPI-only memory.

{table_md}

"""


def text_section_comparison():
    return """# OpenMP versus MPI-only

In this part, MPI-only is compared with the fastest MPI-OpenMP configuration
for every number of nodes and resolution.

"""


def text_section_execution_time(figfile):
    return f"""## Execution time

![Execution time]({figfile})

This figure shows the execution time of MPI-only (dashed) and of the fastest
MPI-OpenMP configuration (solid), which is written below each point as
MPI processes × OpenMP threads per node.
The tables list the time values, which are an average of multiple runs when available.
The last column gives the gain of the best OpenMP configuration with respect to MPI-only.

"""


def text_section_strong_scaling():
    return """## Strong scaling

These figures show the strong scaling of MPI-only and of the best MPI-OpenMP
configuration. Each is normalised to its own time on the lowest number of nodes,
so a better scaling does not necessarily mean a lower execution time.
Ideal scaling is shown as a dotted line.
The tables list the strong scaling efficiency, with the best configuration in brackets.

"""


def text_section_weak_scaling(figfile, table_md):
    return f"""## Weak scaling

![Weak scaling]({figfile})

This figure shows the weak scaling of MPI-only and of the best MPI-OpenMP
configuration, each normalised to its own time on the lowest number of nodes.
Ideal scaling is shown as a dotted line.
The table lists the weak scaling efficiency, with the best configuration in brackets.

{table_md}

"""


def text_section_scaling_combo(figfile):
    return f"""## Strong and weak scaling combined

![Scaling combo]({figfile})

This figure combines strong and weak scaling for MPI-only (left) and for the best
MPI-OpenMP configuration (right), with the performance defined as 1/time.
Strong scaling can be read diagonally, weak scaling horizontally.
Dotted lines show ideal scaling. Both panels share the same axes.

"""


''' Choose the numbers of nodes to show in the bar charts: the lowest and highest
    numbers of nodes, and in between the one with most configurations '''
def choose_breakdown_nodes(entries):
    counts = Counter(entry['nodes'] for entry in select_full_node(entries))
    candidates = sorted(nodes for nodes, count in counts.items() if count>=2)
    if len(candidates)<=3:
        return candidates
    middle = max(candidates[1:-1], key=lambda nodes: (counts[nodes], nodes))
    return [candidates[0], middle, candidates[-1]]


#---------- INPUT ------------

# Get command line arguments
parser = argparse.ArgumentParser(
    description='Generate markdown page on the performance of the OpenMP implementation')
parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
parser.add_argument('-n', '--breakdown-nodes', type=int, nargs='+', default=None,
                    help='Numbers of nodes for the timer breakdown bar charts (default: automatic)')
args = parser.parse_args()

# We always want to display the total time for this page
timer = 'total'
# get list of what resolutions are available for this benchmark
resos = get_resolutions(args.benchmark)

data = load_latest_openmp_data(args.cluster, args.benchmark, timer)
if len(data)==0:
    print(f'No OpenMP data for {args.benchmark} on {args.cluster}')
    exit(1)
data_mpi, data_omp = split_mpi_omp(data)

imgdir = '../results/images'
md = text_section_intro(args, data)


#--------- Part 1: choosing the MPI-OpenMP configuration ------------

md += text_section_config()

# MPI-OpenMP config grid for execution time on 1 node
md += text_section_grid()
for reso in resos:
    figfile = f'{imgdir}/mpi_omp_grid_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
    error = plot_mpi_omp_grid(data, reso, fig_name=figfile, show_overhead=False)
    if not error:
        md += f"![MPI-OMP grid {reso}]({figfile})\n"
md += "\n"

# gain with respect to MPI-only for different numbers of threads
md += text_section_omp_speedup()
for reso in resos:
    figfile = f'{imgdir}/omp_speedup_{args.benchmark}_{reso}_{args.cluster}.png'
    error = plot_openmp_speedup_nthreads(data, reso, fig_name=figfile)
    if not error:
        md += f"![OMP speedup {reso}]({figfile})\n"
md += "\n"

# timer breakdown for the highest resolution
reso = resos[-1]
entries = load_timer_breakdown(get_latest_openmp_dirs(args.cluster), args.benchmark, reso,
                               exclude_compilers=EXCLUDED_COMPILERS)
if len(entries)>0:
    timer_names = select_main_timers(select_full_node(entries))
    title = f'{args.benchmark} {reso} on {args.cluster}'
    md += text_section_timer_breakdown(reso)

    breakdown_nodes = args.breakdown_nodes or choose_breakdown_nodes(entries)
    for nodes in breakdown_nodes:
        figfile = f'{imgdir}/omp_timer_breakdown_{args.benchmark}_{reso}_{nodes}nodes_{args.cluster}.png'
        error = plot_timer_breakdown_configs(entries, nodes, timer_names, title=title, outname=figfile)
        if not error:
            md += f"![Timer breakdown {nodes} nodes]({figfile})\n"
    md += "\n"

    figfile = f'{imgdir}/omp_timer_scaling_{args.benchmark}_{reso}_{args.cluster}.png'
    error = plot_timer_scaling(entries, timer_names, title=title, outname=figfile)
    if not error:
        md += text_section_timer_scaling(figfile)

# memory for the highest resolution
reso = resos[-1]
figfile = f'{imgdir}/memory_{args.benchmark}_{reso}_{args.cluster}.png'
plot_memory(data, reso, outname=figfile)
table_md = table_memory(data, reso, fmt='markdown')
md += text_section_memory(figfile, table_md)


#--------- Part 2: OpenMP versus MPI-only ------------

md += text_section_comparison()
benchmarks = [data_mpi, data_omp]

# execution time
figfile = f'{imgdir}/omp_time_mpi_vs_omp_{args.benchmark}_{timer}_{args.cluster}.png'
error = plot_time_mpi_vs_omp(data_mpi, data_omp, resos, outname=figfile)
if not error:
    md += text_section_execution_time(figfile)
    for reso in resos:
        arr_nodes = get_available_nodes(data_mpi+data_omp, reso)
        if len(arr_nodes)==0:
            continue
        md += f"Resolution {reso}:\n\n"
        md += table_execution_time(benchmarks, VARIANT_LABELS, reso, arr_nodes_in=arr_nodes, fmt='markdown')
        md += "\n"

# strong scaling, for the resolutions where both variants have several numbers of nodes
md += text_section_strong_scaling()
for reso in resos:
    if min(len(get_available_nodes(d, reso)) for d in benchmarks)<2:
        continue
    figfile = f'{imgdir}/omp_strong_scaling_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
    plot_strong_scaling(benchmarks, VARIANT_LABELS, reso, outname=figfile)
    md += f"![Strong scaling {reso}]({figfile})\n\n"
    md += table_strong_scaling(benchmarks, VARIANT_LABELS, reso, fmt='markdown')
    md += "\n"

# weak scaling
if args.benchmark in ['sedov', 'cosmo']:
    nodes, weak_resos = get_weak_scaling_config(args.benchmark)
    figfile = f'{imgdir}/omp_weak_scaling_{args.benchmark}_{timer}_{args.cluster}.png'
    plot_weak_scaling(benchmarks, VARIANT_LABELS, nodes, weak_resos, outname=figfile)
    table_md = table_weak_scaling(benchmarks, VARIANT_LABELS, nodes, weak_resos, fmt='markdown')
    md += text_section_weak_scaling(figfile, table_md)

    # strong and weak scaling combined
    figfile = f'{imgdir}/omp_scaling_combo_{args.benchmark}_{timer}_{args.cluster}.png'
    error = plot_scaling_combo_mpi_vs_omp(data_mpi, data_omp, resos,
                                          get_weak_scaling_config2(args.benchmark), outname=figfile)
    if not error:
        md += text_section_scaling_combo(figfile)


#--------- Output markdown page ------------

outfile = f"../results/results_openmp_{args.benchmark}_{args.cluster}.md"
with open(outfile, 'w') as f:
    f.write(md)
print(f"Wrote documentation page: {outfile}")
