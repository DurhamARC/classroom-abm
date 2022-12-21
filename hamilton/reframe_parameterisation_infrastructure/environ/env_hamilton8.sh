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
