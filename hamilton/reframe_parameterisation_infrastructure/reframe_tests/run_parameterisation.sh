#!/bin/bash
set -e

# A script to initialise environment variables for the parameterisation script and to run it
# (to avoid manually doing so every time)
#
# For parameterisation, you can currently select from the following datasets
# (used in `parameterisation.sh`):
#   --with-big-dataset
#   --with-medium-dataset
#   --with-test-dataset
#   --with-small-dataset
#   --with-tiny-dataset

export REFRAME_TEST="variation-with-feedback"

export NUM_ITERATIONS=15
export NUM_REPEATS=2
export FEEDBACK_WEEKS=1
export CONVERGENCE_DAYS=30

./parameterisation.sh --with-medium-dataset
