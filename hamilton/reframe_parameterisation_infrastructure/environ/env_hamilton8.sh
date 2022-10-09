#!/bin/bash

# Load env for hamilton8

# User variables, change accordingly
export REFRAME_TEST="convergence-rate-best-value-3"
# if [ -z "$REFRAME_TEST" ]; then
#   export REFRAME_TEST="parameterisation_results"
# fi
export PARAMETERISATION_RESULTS_DIR=$NOBACKUP/classroom_abm/${REFRAME_TEST}

# Don't modify below this line

module purge
module load python/3.9.9

export STAGE_DIR=$NOBACKUP/reframe_stage
export OUTPUT_DIR=$NOBACKUP/reframe_output
export OUTPUT_SUBDIR=$OUTPUT_DIR/hamilton8/multi_cpu_shared/amd/
export RFM_SAVE_LOG_FILES=1
export config=../config/hamilton.py

export PYTHONPATH=$PYTHONPATH:~/classroom-abm/MesaModel/hamilton/reframe_parameterisation_infrastructure/reframe_tests
