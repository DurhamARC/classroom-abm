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

INPUT_DIR=~/classroom-abm/hamilton/parameter_input
export REFRAME_TEST="convergence-rate-best-value-4"
export PARAMETERISATION_RESULTS_DIR=$NOBACKUP/classroom_abm/${REFRAME_TEST}

#export PARAMETER_FILE="${INPUT_DIR}/example_lhs_params.csv"
#export PARAMETER_FILE="${INPUT_DIR}/lhs_params.csv"
export PARAMETER_FILE="${INPUT_DIR}/next_lhs_params_2022-10-09_010041.csv"
export NUM_ITERATIONS=20
export NUM_REPEATS=2
export FEEDBACK_WEEKS=1
export CONVERGENCE_DAYS=30

./parameterisation.sh --with-medium-dataset
