#!/bin/bash

# Request resources:
#SBATCH --nodes=1
#SBATCH --mail-type=ALL
#SBATCH --time=24:0:0  # time (hours:minutes:seconds)

# Run on the queue for serial ("sequential") work
# (job will share node with other jobs)
#SBATCH -p par7.q
#SBATCH --array=1-6

module load java/1.8.0

# Commands to be run:
../NetLogo\ 6.1.1/netlogo-headless.sh --model Classroom_mimic.nlogo \
  --setup-file experiment-files/experiment4runs.xml \
  --experiment experiment${SLURM_ARRAY_TASK_ID} \
  --table classes_output/experiment${SLURM_ARRAY_TASK_ID}`date +%Y-%m-%d_%H%M%S`.csv \
  --threads 24
