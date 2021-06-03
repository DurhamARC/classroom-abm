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
source activate classroom_abm
module load r/4.0.3

pushd <path-to-repo>/MesaModel

# prepend 'time' to the following command
# if doing benchmarking work
python run.py -a -npr 24