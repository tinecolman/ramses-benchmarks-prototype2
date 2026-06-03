
from io_timings import add_data
from resolutions import *
from scaling_strong import plot_strong_scaling, table_strong_scaling
from scaling_weak import plot_weak_scaling, table_weak_scaling
from scaling_combo import plot_scaling_combo_inverse
import argparse

COLOR='\033[0;36m' #cyan
NC='\033[0m' # No Color

#--------- Get command line input ------------
parser = argparse.ArgumentParser(
    description='Analyse benchmark by producing strong and weak scaling figures and tables'
)
parser.add_argument('-p', '--path', required=True, help='Path to the benchmark directory')
parser.add_argument('-b', '--benchmark', required=True, help='Benchmark setup name')
args = parser.parse_args()

#--------- Load benchmark data ------------
timer='total'
data = add_data([], args.path, args.benchmark, which=timer)
release_label = args.path.split('/')[-2][10:]
print()

#--------- Strong and weak scaling combo figure ------------
resos = get_resolutions(args.benchmark)
weak_scaling_map = get_weak_scaling_config2(args.benchmark)
plot_scaling_combo_inverse(data,resos,weak_scaling_map)

#--------- Strong scaling ------------
reso = resos[-1] # we show only the highest resolution
plot_strong_scaling([data], [release_label], reso)
print(f'{COLOR} Strong scaling efficiency for {args.benchmark} {reso} {NC}')
table = table_strong_scaling([data], [release_label], reso, fmt='latex')
print(table)

#--------- Weak scaling ------------
nodes, resos = get_weak_scaling_config(args.benchmark)
plot_weak_scaling([data], [release_label], nodes, resos)
print(f'{COLOR} Weak scaling efficiency for {args.benchmark} {reso} {NC}')
table = table_weak_scaling([data], [release_label], nodes, resos, fmt='latex')
print(table)
