#!/bin/bash
module purge
module load python/3.6.8

export STAGE_DIR=/ddn/data/$USER/reframe_stage
export OUTPUT_DIR=/ddn/data/$USER/reframe_output
export RFM_SAVE_LOG_FILES=1
export config=../config/hamilton.py

export PYTHONPATH=$PYTHONPATH:~/classroom-abm/MesaModel/hamilton/reframe_parameterisation_infrastructure/reframe_tests
