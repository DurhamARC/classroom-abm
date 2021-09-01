#!/usr/bin/env bash
DATE_TO_FETCH=${DATE_TO_FETCH:-`date +"%Y-%m-%d"`}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd $SCRIPT_DIR/../../parameterisation_results > /dev/null
mkdir $DATE_TO_FETCH
pushd $DATE_TO_FETCH > /dev/null
scp $USER@hamilton.dur.ac.uk:classroom-abm/hamilton/mse_results_from_reframe/mse_output_${DATE_TO_FETCH}*.csv .
# FIXME: see if we can compress these files
scp -r $USER@hamilton.dur.ac.uk:/ddn/data/${USER}/reframe_output/hamilton/multi_cpu_single_node/intel/Parameterisation_24_*_1 .
scp $USER@hamilton.dur.ac.uk:classroom-abm/hamilton/parameter_input/lhs_params.csv .

DATA_DIR=`pwd`
MSE_OUTPUT_FILE=`ls mse_output_${DATE_TO_FETCH}*.csv`

python $SCRIPT_DIR/../mse_results_from_reframe/merge_repeats.py $DATA_DIR/$MSE_OUTPUT_FILE
python $SCRIPT_DIR/plot_correlations.py $DATA_DIR

popd > /dev/null
popd > /dev/null
