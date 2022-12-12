#!/bin/bash

# Load env for hamilton8

module purge
module load python/3.9.9

export STAGE_DIR=$NOBACKUP/reframe_stage
export OUTPUT_DIR=$NOBACKUP/reframe_output
export OUTPUT_SUBDIR=$OUTPUT_DIR/hamilton8/multi_cpu_shared/amd/
export RFM_SAVE_LOG_FILES=1
export config=../config/hamilton.py

export CLASSROOMABM_PATH=~/Projects/classroom-abm
export PYTHONPATH=$PYTHONPATH:$CLASSROOMABM_PATH/MesaModel/hamilton/reframe_parameterisation_infrastructure/reframe_tests

INPUT_DIR=$CLASSROOMABM_PATH/hamilton/parameter_input
export PARAMETERISATION_RESULTS_DIR=$NOBACKUP/classroom_abm/${REFRAME_TEST}
export PARAMETER_FILE="${INPUT_DIR}/example_lhs_params.csv"
#export PARAMETER_FILE="${INPUT_DIR}/lhs_params.csv"
#export PARAMETER_FILE="${INPUT_DIR}/next_lhs_params_2022-12-07_015419.csv"
