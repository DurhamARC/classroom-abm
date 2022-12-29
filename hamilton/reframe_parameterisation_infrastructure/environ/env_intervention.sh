#!/bin/bash

# Load env for interventions

export PARAMETER_FILE="${CLASSROOMABM_PATH}/hamilton/parameter_input/parameters_intervention.csv"

export REFRAME_TEST="variation-with-feedback"
export INTERVENTION_RESULTS_DIR="$NOBACKUP/classroom_abm/${RUN_CATEGORY}s/${REFRAME_TEST}"

export NUM_ITERATIONS=5
export NUM_INCREMENTS=5
export NUM_REPEATS=5
export INCR_FACTOR=0.2
export FEEDBACK_WEEKS=1
export CONVERGENCE_DAYS=30
