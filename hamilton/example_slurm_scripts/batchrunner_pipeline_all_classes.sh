#!/bin/bash
#SBATCH --ntasks 64
#SBATCH --cpus-per-task 64
#SBATCH --time=2:0:0
#SBATCH -J run_mesa_with_batchrunner
#SBATCH -o run_mesa_with_batchrunner.out
#SBATCH -e run_mesa_with_batchrunner.err
# Run on Hamilton8's shared queue
#SBATCH -p shared

module purge
module load r/4.1.2
module load $R_BUILD_MODULES

source activate classroom_abm

pushd $HOME/classroom-abm/multilevel_analysis

# Change these paths to $HOME if that's where you installed mlwin
export MLNSCRIPT_PATH=$NOBACKUP/usr/bin/mlnscript
export LD_LIBRARY_PATH=$NOBACKUP/usr/lib64:$LD_LIBRARY_PATH

# prepend 'time' to the following command if doing
# benchmarking work. Note: this runs all 6 classes in
# ../classes_input/test_input_short.csv but will not run
# the full pipeline (for that use the above structure
# on ../multilevel_analysis/run_pipeline.py). To run on
# the full dataset add -i ../classes_input/test_input.csv
# If you do this set -p to 24 to exploit all of the cores
# one of Hamilton's nodes.
python run_pipeline.py -i ../classes_input/test_input.csv -p 64
