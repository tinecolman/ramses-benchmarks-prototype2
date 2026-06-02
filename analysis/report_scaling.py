''' TODO write description
'''

from tagged_data import *
from resolutions import *
from evolution_execution_time import plot_execution_time_multinode, table_execution_time
from scaling_strong import plot_strong_scaling, table_strong_scaling
from scaling_weak import plot_weak_scaling, table_weak_scaling
from scaling_combo import plot_scaling_combo_inverse
from openmp_config_grid import plot_mpi_omp_grid
import argparse

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

md = f"""# Benchmark: {args.benchmark} on {args.cluster}

[Benchmark description: {args.benchmark}](../setups/{args.benchmark}/description.md)

[Cluster info: {args.cluster}](../HPCclusters/{args.cluster}/cluster_description.md)

"""

resos = get_resolutions(args.benchmark)

weak_scaling_map = get_weak_scaling_config2(args.benchmark)

######### In this part, we deal with the latest official release #########
benchmark, release_label = load_latest_release_data(args.cluster, args.benchmark, timer)

#--------- Strong and weak scaling combo figure ------------

figfile = f'../results/images/scaling_combo_{args.benchmark}_{timer}_{args.cluster}.png'
plot_scaling_combo_inverse(
        benchmark,
        resos,
        weak_scaling_map,
        outname=figfile
)

# Assemble markdown page string
md += f"""## Strong and weak scaling of the latest code release

![Scaling]({figfile})

This figure shows the strong and weak scaling of the latest official release ({release_label}).
Strong scaling can be inferred diagonally, while weak scaling is determined by reading horizontally.
Dotted lines show ideal scaling.

"""

######### In this part, we deal with the time evolution between versions #########
benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, timer)
reso = resos[-1] # we show only the highest resolution

#--------- Execution time evolution ------------

figfile = f'../results/images/evo_exectime_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
plot_execution_time_multinode(benchmarks, release_labels, reso, outname=figfile)

table_md = table_execution_time(benchmarks, release_labels, reso, fmt='markdown')

md += f"""## Evolution of execution time with code version

![Evolution execution time]({figfile})

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

{table_md}

"""


#--------- Strong scaling evolution ------------

figfile = f'../results/images/strong_scaling_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
plot_strong_scaling(benchmarks, release_labels, reso, outname=figfile)

table_md = table_strong_scaling(benchmarks, release_labels, reso, fmt='markdown')

md += f"""## Strong scaling evolution

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

#--------- Weak scaling evolution ------------

nodes, resos = get_weak_scaling_config(args.benchmark)

figfile = f'../results/images/weak_scaling_{args.benchmark}_{timer}_{args.cluster}.png'
plot_weak_scaling(benchmarks, release_labels, nodes, resos, outname=figfile)

table_md = table_weak_scaling(benchmarks, release_labels, nodes, resos, fmt='markdown')


md += f"""## Weak scaling evolution

![Weak scaling]({figfile})

This figure shows the weak scaling for different versions of the code.
Ideal scaling is shown as a dotted line.
The table lists the corresponding weak scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

{table_md}

"""



# OpenMP insights

# Get OMP-MPI grid
#data = load_latest_openmp_data(args.cluster, args.benchmark, timer)
#figfile_grid_omp = f'../results/images/mpi_omp_grid_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
#plot_mpi_omp_grid(data, reso, 
#                    fig_name=figfile_grid_omp,
#                    show_overhead=False)

"""
## MPI - OpenMP configuration on 1 node

![MPI-OMP]({figfile_grid_omp})

This figure gives inside in the behaviour of OpenMP for this setup.
It shows which MPI - OpenMP configuration is most optimal
in terms of execution time, for this setup at this resolution.
The data is for the latest OpenMP version, corresponding to the one
used for the previous figures.

"""

# Write markdown page
outfile = f"../results/results_{args.benchmark}_{args.cluster}.md"
with open(outfile, 'w') as f:
    f.write(md)
print(f"Wrote documentation page: {outfile}")

