#!/bin/bash
module purge
module load python/3.9.9

export STAGE_DIR=$NOBACKUP/reframe_stage
export OUTPUT_DIR=$NOBACKUP/reframe_output
export PARAMETERISATION_RESULTS_DIR=$NOBACKUP/classroom_abm_parameterisation_results
export RFM_SAVE_LOG_FILES=1
export config=../config/hamilton8.py

export PYTHONPATH=$PYTHONPATH:~/classroom-abm/MesaModel/hamilton/reframe_parameterisation_infrastructure/reframe_tests
