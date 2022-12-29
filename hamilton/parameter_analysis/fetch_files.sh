#!/usr/bin/env bash

# The script to run locally to fetch data from the remote machine

DATE_TO_FETCH=${DATE_TO_FETCH:-`date +"%Y-%m-%d"`}
TIME_TO_FETCH=${TIME_TO_FETCH:-"*"}

if [ -n "$START_TIME" ] && [ -n "$END_TIME" ]; then
  TIME_TO_FETCH="{$START_TIME..$END_TIME}"
fi

DATE_DIR=$DATE_TO_FETCH
if [ -n "$START_DAY" ] && [ -n "$END_DAY" ]; then
  DATE_TO_FETCH="${DATE_TO_FETCH::8}{$START_DAY..$END_DAY}"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -n "$LOCAL_RESULTS_DIR" ]; then
  pushd $LOCAL_RESULTS_DIR > /dev/null
else
  pushd $SCRIPT_DIR/../../results > /dev/null
fi

DIR_PREFIX="${DATE_DIR}_part_"
LAST_DIR=$((find * -type d -regex ".*${DIR_PREFIX}[0-9][0-9][0-9]") | tail -1)
LAST_DIR=${LAST_DIR:-${DIR_PREFIX}0}
n=$((1+${LAST_DIR##$DIR_PREFIX}))
NEW_DIR=$DIR_PREFIX$(printf "%03d" $n)
mkdir $NEW_DIR
pushd $NEW_DIR > /dev/null

echo "Fetching results file(s) from the ${RUN_CATEGORY} run: /nobackup/${USER}/${REMOTE_RESULTS_DIR}/${DATE_TO_FETCH}_${TIME_TO_FETCH}.zip"
scp -r ${USER}@hamilton8:/nobackup/${USER}/${REMOTE_RESULTS_DIR}/${DATE_TO_FETCH}_${TIME_TO_FETCH}.zip .

pwd

for f in *; do
  echo $f
  subdir=${f%%.*}
  mkdir $subdir
  pushd $subdir > /dev/null
  unzip ../${f}
  popd
done

if [ "$RUN_CATEGORY" == "parameterisation" ]; then
  python $SCRIPT_DIR/cli.py merge-best-results -d `pwd` -l 10
  python $SCRIPT_DIR/cli.py plot-correlations -i `pwd`/"best_mses.csv"
  python $SCRIPT_DIR/cli.py plot-correlations -i `pwd`/"best_mse_means.csv" -o `pwd`/means_correlations.png
elif [ "$RUN_CATEGORY" == "intervention" ]; then
  python $SCRIPT_DIR/cli.py merge-best-results -d `pwd` -s "avg_maths_score" -l 0
  python $SCRIPT_DIR/cli.py plot-scores -i `pwd`/"avg_maths_scores.csv"
  python $SCRIPT_DIR/cli.py plot-scores -i `pwd`/"avg_maths_score_means.csv" -o `pwd`/means_scores.png
fi

popd > /dev/null
popd > /dev/null
