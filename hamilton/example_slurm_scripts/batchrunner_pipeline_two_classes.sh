#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 2
#SBATCH --time=0:15:0
#SBATCH -J run_mesa_with_batchrunner
#SBATCH -o run_mesa_with_batchrunner.out
#SBATCH -e run_mesa_with_batchrunner.err
# Run on test queue for distributed work
#SBATCH -p test

module purge
module load r/4.0.3

source activate classroom_abm

pushd $HOME/classroom-abm/multilevel_analysis

# Change these paths to /ddn/home if that's where you installed mlwin
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
python run_pipeline.py -t -i ../classes_input/test_input_2_classes.csv
