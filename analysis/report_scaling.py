''' TODO write description
'''

from tagged_data import *
from resolutions import get_resolutions
from evolution_execution_time import plot_execution_time_multinode, table_execution_time
from scaling_strong import plot_strong_scaling, table_strong_scaling
from openmp_config_grid import plot_mpi_omp_grid
import argparse

# Get command line arguments
parser = argparse.ArgumentParser(
    description='Update benchmark page'
)
parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
args = parser.parse_args()

# We always want to display the total time for this page
timer='total'

# Load release data
benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, timer)

md = f"""# Benchmark: {args.benchmark} on {args.cluster}

[Benchmark description: {args.benchmark}](../setups/{args.benchmark}/description.md)

[Cluster info: {args.cluster}](../HPCclusters/{args.cluster}/cluster_description.md)

"""

#resos = get_resolutions(args.benchmark)
reso = get_resolutions(args.benchmark)[-1]

#for reso in reversed(resos):

# Evolution of execution time figure
figfile1 = f'../results/images/evo_exectime_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
plot_execution_time_multinode(
    benchmarks,
    release_labels,
    reso,
    outname=figfile1
)

table_md1 = table_execution_time( benchmarks, release_labels, reso, fmt='markdown')

# Make strong scaling figure
figfile2 = f'../results/images/strong_scaling_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
plot_strong_scaling(
    benchmarks,
    release_labels,
    reso,
    outname=figfile2
)

# Get strong scaling efficiency table
table_md2 = table_strong_scaling(benchmarks, release_labels, reso, fmt='markdown')


# Assemble markdown page string
md += f"""
## Evolution of execution time with code version

![Evolution execution time]({figfile1})

This figure shows the execution time for different versions of the code.
To guide the eye, the dotted line shows the time for the oldest version.
The table lists the time values, which are an average of multiple runs.
The last column informs of the speedup of the last version with 
respect to the first listed version. Unless otherwise stated,
the time listed is for runs with MPI-only using the full compute node.

{table_md1}

## Strong scaling

![Strong scaling]({figfile2})

This figure shows the strong scaling for different versions of the code.
The underlying timings are those from the previous section.
Ideal scaling is shown as a dotted line.
The table lists the corresponding strong scaling efficiency,
with respect to the minimal number of nodes.
Unless otherwise stated, data is for runs with MPI-only 
using the full compute node.

{table_md2}

"""


# Weak scaling



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

