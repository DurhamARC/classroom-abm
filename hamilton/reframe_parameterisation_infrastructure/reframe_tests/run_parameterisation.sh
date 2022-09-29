#!/bin/bash
set -e

# A script to extend the existing input file $INPUT_PARAMETER_FILE
# with a new column $COLUMN_NAME with its initial value $COLUMN_VALUE and
# run `parameterisation.sh` with the predefined env variables
# Modify the env variables according to your needs:
#   $REFRAME_TEST
#   $NUM_ITERATIONS
#   $NUM_REPEATS
# For parameterisation, you can currently select from the following datasets
# (see parameterisation.sh):
#   --with-big-dataset
#   --with-medium-dataset
#   --with-test-dataset
#   --with-small-dataset

INPUT_DIR=~/classroom-abm/hamilton/parameter_input

export PARAMETER_FILE="${INPUT_DIR}/example_lhs_params.csv"
#export PARAMETER_FILE="${INPUT_DIR}/lhs_params_rate.csv"
#export PARAMETER_FILE="${INPUT_DIR}/next_lhs_params_2022-09-25_224053.csv"
export NUM_ITERATIONS=10
export NUM_REPEATS=2
export FEEDBACK_WEEKS=1
export CONVERGENCE_DAYS=30

./parameterisation.sh --with-medium-dataset
