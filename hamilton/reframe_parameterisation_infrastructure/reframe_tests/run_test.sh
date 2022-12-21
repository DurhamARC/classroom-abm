#!/bin/bash
set -e

#### Modify as you need
export RUN_CATEGORY="intervention" # options: parameterisation, intervention
####

source $HOME/.bashrc
HAMILTON_VERSION="hamilton8"
source ../environ/env_${HAMILTON_VERSION}.sh
echo "Loading env from ../environ/env_${HAMILTON_VERSION}.sh"
source ../environ/env_${RUN_CATEGORY}.sh
echo "Loading env for a(n) ${RUN_CATEGORY} run"

# A script to initialise environment variables for the parameterisation/intervention script and to run it
# (to avoid manually doing so every time)
#
# You can currently select from the following datasets
# (used in `parameterisation.sh`/`intervention.sh`):
#   --with-big-dataset
#   --with-medium-dataset
#   --with-test-dataset
#   --with-small-dataset
#   --with-tiny-dataset

./${RUN_CATEGORY}.sh --with-medium-dataset
