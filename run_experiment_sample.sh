#!/bin/bash

# Request resources:
#SBATCH --nodes=1
#SBATCH --mail-type=ALL
#SBATCH --time=4:0:0  # time (hours:minutes:seconds)

# Run on the queue for serial ("sequential") work
# (job will share node with other jobs)
#SBATCH -p par7.q

module load java/1.8.0

# Commands to be run:
../NetLogo\ 6.1.1/netlogo-headless.sh --model Classroom_mimic.nlogo \
  --setup-file experiment-files/experiment-sample.xml \
  --experiment experiment \
  --table classes_output/experiment-`date +%Y-%m-%d_%H%M%S`-${SLURM_JOB_ID}.csv \
  --threads 24
