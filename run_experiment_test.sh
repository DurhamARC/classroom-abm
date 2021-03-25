#!/bin/bash

# Request resources:
#SBATCH --mail-type=ALL
#SBATCH --time=0:5:0 # time (hours:minutes:seconds)

# Run on the queue for serial ("sequential") work
# (job will share node with other jobs)
#SBATCH -p test.q
#SBATCH --array=1-2

module load java/1.8.0

# Commands to be run:
../NetLogo\ 6.1.1/netlogo-headless.sh --model Classroom_mimic.nlogo \
  --setup-file experiment-files/experiment.xml \
  --experiment experiment${SLURM_ARRAY_TASK_ID} \
  --table classes_output/experiment-${SLURM_JOB_ID}-${SLURM_ARRAY_TASK_ID}.csv \
  --threads 1
