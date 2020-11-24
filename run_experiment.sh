#!/bin/bash

# Request resources:
#SBATCH --cpus-per-task=4
#SBATCH --nodes=1
#SBATCH --mail-user=alison.r.clarke@durham.ac.uk
#SBATCH --mail-type=ALL
#SBATCH --time=10:0:0  # time (hours:minutes:seconds)

# Run on the queue for serial ("sequential") work
# (job will share node with other jobs)
#SBATCH -p par6.q

module load java/1.8.0

# Commands to be run:
../NetLogo\ 6.1.1/netlogo-headless.sh --model Classroom_mimic.nlogo \
  --setup-file experiment4runs.xml \
  --experiment experiment \
  --table experiment.csv \
  --threads 4
