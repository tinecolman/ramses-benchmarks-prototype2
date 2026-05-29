from scaling_strong import plot_strong_scaling, table_strong_scaling
import argparse

# Get command line arguments
parser = argparse.ArgumentParser(
    description='Plot benchmark strong scaling'
)
parser.add_argument('-c', '--cluster', required=True, help='Cluster name')
parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
parser.add_argument('-r', '--reso', required=True, help='Resolution')
parser.add_argument('-t', '--timer', default='total', help='Subtimer to analyse')
args = parser.parse_args()

# Load release data
from tagged_data import load_release_data
benchmarks, release_labels = load_release_data(args.cluster, args.benchmark, args.timer)

# Make strong scaling figure
figfile=f'../results/images/strong_scaling_{args.benchmark}_{args.reso}_{args.timer}_{args.cluster}.png'
plot_strong_scaling(
    benchmarks,
    release_labels,
    args.reso,
    outname=figfile
)

# Get strong scaling efficiency table
table_md = table_strong_scaling(benchmarks, release_labels, args.reso, fmt='markdown')


# Assemble markdown page string
md = f"""# Benchmark results: {args.benchmark} on {args.cluster}

## Strong scaling figure

![Strong scaling]({figfile})

## Strong scaling efficiency table

{table_md}
"""

# Write markdown page
outfile = f"../results/results_{args.benchmark}_{args.cluster}.md"
with open(outfile, 'w') as f:
    f.write(md)
print(f"Wrote documentation page: {outfile}")

