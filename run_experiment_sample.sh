#!/bin/bash

# Request resources:
#SBATCH -n 4          # 4 CPU cores
#SBATCH --mem=1G      # 1 GB RAM
#SBATCH --time=0:15:0  # time (hours:minutes:seconds)

# Run on the queue for serial ("sequential") work
# (job will share node with other jobs)
#SBATCH -p test.q

module load java/1.8.0

# Commands to be run:
../NetLogo\ 6.1.1/netlogo-headless.sh --model Classroom_mimic.nlogo \
  --setup-file experiment.xml \
  --experiment experiment \
  --table classes_output/experiment`date +%Y-%m-%d_%H%M%S`.csv
