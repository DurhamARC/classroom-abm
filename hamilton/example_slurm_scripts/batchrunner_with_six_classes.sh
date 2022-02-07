#!/bin/bash
#SBATCH --cpus-per-task 6
#SBATCH --time=0:30:0
#SBATCH -J run_mesa_with_batchrunner
#SBATCH -o run_mesa_with_batchrunner.out
#SBATCH -e run_mesa_with_batchrunner.err
# Run on Hamilton8's queue for distributed work
#SBATCH -p shared

module purge
module load r/4.1.2
module load $R_BUILD_MODULES

source activate classroom_abm

pushd $HOME/classroom-abm/multilevel_analysis

# prepend 'time' to the following command if doing
# benchmarking work. Note: this runs all 6 classes in
# ../classes_input/test_input_short.csv but will not run
# the full pipeline (for that use the above structure
# on ../multilevel_analysis/run_pipeline.py). To run on
# the full dataset add -i ../classes_input/test_input.csv
# If you do this set -p to 24 to exploit all of the cores
# one of Hamilton's nodes.
python run.py --all_classes --n-processors 6
