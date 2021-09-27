#!/usr/bin/env bash
set -euo pipefail
DATE_TO_FETCH=${DATE_TO_FETCH:-`date +"%Y-%m-%d"`}
TIME_TO_FETCH=${TIME_TO_FETCH:-"*"}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd $SCRIPT_DIR/../../parameterisation_results > /dev/null

DIR_PREFIX="${DATE_TO_FETCH}_part_"
LAST_DIR=$((find * -type d -regex ".*${DIR_PREFIX}[0-9][0-9][0-9]") | tail -1)
LAST_DIR=${LAST_DIR:-${DIR_PREFIX}0}
n=$((1+${LAST_DIR##$DIR_PREFIX}))
NEW_DIR=$DIR_PREFIX$(printf "%03d" $n)
mkdir $NEW_DIR

pushd $NEW_DIR > /dev/null
scp $USER@hamilton.dur.ac.uk:classroom-abm/hamilton/mse_results_from_reframe/mse_output_${DATE_TO_FETCH}_${TIME_TO_FETCH}.zip .
unzip mse_output_${DATE_TO_FETCH}_${TIME_TO_FETCH}.zip

DATA_DIR=`pwd`
MSE_OUTPUT_FILE=`ls mse_output_${DATE_TO_FETCH}_${TIME_TO_FETCH}.csv`

python $SCRIPT_DIR/../parameter_analysis/merge_repeats.py $DATA_DIR/$MSE_OUTPUT_FILE
python $SCRIPT_DIR/plot_correlations.py $DATA_DIR "lowest_to_highest_mses.csv"

popd > /dev/null
popd > /dev/null
