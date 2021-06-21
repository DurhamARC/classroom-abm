#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 24
#SBATCH --time=1:0:0
#SBATCH -J run_mesa_with_batchrunner
#SBATCH -o run_mesa_with_batchrunner.out
#SBATCH -e run_mesa_with_batchrunner.err
#SBATCH --exclusive
# Run on Hamilton7's queue for distributed work
#SBATCH -p par7.q

module purge
module load miniconda2/4.1.11
module load r/4.0.3

source activate classroom_abm

pushd <path-to-repo>/MesaModel

# prepend 'time' to the following command if doing
# benchmarking work. Note: this runs all 6 classes in
# ../classes_input/test_input_short.csv but will not run
# the full pipeline (for that use the above structure
# on ../multilevel_analysis/run_pipeline.py). To run on
# the full dataset add -i ../classes_input/test_input.csv
# If you do this set -p to 24 to exploit all of the cores
# one of Hamilton's nodes.
python run.py --all_classes --n-processors 6
