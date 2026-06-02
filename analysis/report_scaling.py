''' TODO write description
'''

from tagged_data import *
from resolutions import get_resolutions
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

resos = get_resolutions(args.benchmark)

# Load release data
benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, timer)

for reso in resos:

    # Make strong scaling figure
    figfile=f'../results/images/strong_scaling_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
    plot_strong_scaling(
        benchmarks,
        release_labels,
        reso,
        outname=figfile
    )

    # Get strong scaling efficiency table
    table_md = table_strong_scaling(benchmarks, release_labels, reso, fmt='markdown')


    # Get OMP-MPI grid
    data = load_latest_openmp_data(args.cluster, args.benchmark, timer)
    figfile_grid_omp = f'../results/images/mpi_omp_grid_{args.benchmark}_{reso}_{timer}_{args.cluster}.png'
    plot_mpi_omp_grid(data, reso, 
                        fig_name=figfile_grid_omp,
                        show_overhead=False)

    # Assemble markdown page string
    md = f"""# Benchmark: {args.benchmark} {reso} on {args.cluster}

## Strong scaling figure

![Strong scaling]({figfile})

## Strong scaling efficiency table

{table_md}

## MPI - OpenMP configuration on 1 node

![Strong scaling]({figfile_grid_omp})

"""

# Write markdown page
outfile = f"../results/results_{args.benchmark}_{args.cluster}.md"
with open(outfile, 'w') as f:
    f.write(md)
print(f"Wrote documentation page: {outfile}")

