#!/usr/bin/env bash
DATE_TO_FETCH=${DATE_TO_FETCH:-`date +"%Y-%m-%d"`}
TIME_TO_FETCH=${TIME_TO_FETCH:-"*"}

if [ -n "$START_TIME" ] && [ -n "$END_TIME" ]; then
  TIME_TO_FETCH="{$START_TIME..$END_TIME}"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd $SCRIPT_DIR/../../parameterisation_results > /dev/null

DIR_PREFIX="${DATE_TO_FETCH}_part_"
LAST_DIR=$((find * -type d -regex ".*${DIR_PREFIX}[0-9][0-9][0-9]") | tail -1)
LAST_DIR=${LAST_DIR:-${DIR_PREFIX}0}
n=$((1+${LAST_DIR##$DIR_PREFIX}))
NEW_DIR=$DIR_PREFIX$(printf "%03d" $n)
mkdir $NEW_DIR
pushd $NEW_DIR > /dev/null

echo "Fetching file(s): /ddn/data/${USER}/classroom_abm_parameterisation_results/${DATE_TO_FETCH}_${TIME_TO_FETCH}.zip"
scp -r ${USER}@hamilton.dur.ac.uk:/ddn/data/${USER}/classroom_abm_parameterisation_results/${DATE_TO_FETCH}_${TIME_TO_FETCH}.zip .

pwd

for f in *; do
  echo $f
  subdir=${f%%.*}
  mkdir $subdir
  pushd $subdir > /dev/null
  unzip ../${f}
  popd
done

python $SCRIPT_DIR/merge_best_results.py `pwd`
python $SCRIPT_DIR/plot_correlations.py `pwd` "best_mses.csv"

popd > /dev/null
popd > /dev/null
