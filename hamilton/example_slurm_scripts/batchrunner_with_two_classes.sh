#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 2
#SBATCH --time=0:15:0
#SBATCH -J run_mesa_with_batchrunner
#SBATCH -o run_mesa_with_batchrunner.out
#SBATCH -e run_mesa_with_batchrunner.err
# Run on test queue for distributed work
#SBATCH -p test.q

module purge
module load miniconda2/4.1.11
module load r/4.0.3

source activate classroom_abm

pushd /ddn/home/$USER/classroom-abm/multilevel_analysis

# prepend 'time' to the following command if doing
# benchmarking work. Note: this runs all 6 classes in
# ../classes_input/test_input_short.csv but will not run
# the full pipeline (for that use the above structure
# on ../multilevel_analysis/run_pipeline.py). To run on
# the full dataset add -i ../classes_input/test_input.csv
# If you do this set -p to 24 to exploit all of the cores
# one of Hamilton's nodes.
python run.py -a -i ../classes_input/test_input_2_classes.csv
