#!/usr/bin/env bash
set -euo pipefail
DATE_TO_FETCH=${DATE_TO_FETCH:-`date +"%Y-%m-%d"`}
TIME_TO_FETCH=${TIME_TO_FETCH:-"*"}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd $SCRIPT_DIR/../../parameterisation_results > /dev/null

# FIXME: avoid overwriting directory!
DIR_PREFIX="${DATE_TO_FETCH}_part_"
LAST_DIR=$((find $DIR_PREFIX* || echo "${DIR_PREFIX}0") | tail -1)
n=$((1+${LAST_DIR##$DIR_PREFIX}))
NEW_DIR=$DIR_PREFIX$(printf "%03d" $n)
mkdir $NEW_DIR

pushd $NEW_DIR > /dev/null
scp $USER@hamilton.dur.ac.uk:classroom-abm/hamilton/mse_results_from_reframe/mse_output_${DATE_TO_FETCH}_${TIME_TO_FETCH}.csv .
# FIXME: see if we can compress these files
scp -r $USER@hamilton.dur.ac.uk:/ddn/data/${USER}/reframe_output/hamilton/multi_cpu_single_node/intel/Parameterisation_24_*_1 .
scp $USER@hamilton.dur.ac.uk:classroom-abm/hamilton/parameter_input/lhs_params.csv .

DATA_DIR=`pwd`
MSE_OUTPUT_FILE=`ls mse_output_${DATE_TO_FETCH}_${TIME_TO_FETCH}*.csv`

python $SCRIPT_DIR/../mse_results_from_reframe/merge_repeats.py $DATA_DIR/$MSE_OUTPUT_FILE
python $SCRIPT_DIR/plot_correlations.py $DATA_DIR

popd > /dev/null
popd > /dev/null
