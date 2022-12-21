#!/bin/bash

# Load env for parameterisations

export PARAMETER_FILE="${CLASSROOMABM_PATH}/hamilton/parameter_input/lhs_params.csv"
#export PARAMETER_FILE="hamilton/parameter_input/next_lhs_params_2022-12-07_015419.csv"
export BEST_PARAMETER_FILE="best_params.csv"

export REFRAME_TEST="variation-with-feedback"
export PARAMETERISATION_RESULTS_DIR="$NOBACKUP/classroom_abm/${RUN_CATEGORY}s/${REFRAME_TEST}"

export NUM_ITERATIONS=10
export NUM_REPEATS=2
export FEEDBACK_WEEKS=1
export CONVERGENCE_DAYS=30
