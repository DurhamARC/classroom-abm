#!/bin/bash
case "$1" in
    "--with-big-dataset")
        export DATASET=../classes_input/test_input.csv
        ;;
    "--with-small-dataset")
        export DATASET=../classes_input/test_input_short.csv
        ;;
    (*)
        echo "Please name a dataset for this job. Options are: "
        echo "--with-big-dataset (over 1hr per run), --with-small-dataset (under 5 mins)."
        exit 1
        ;;
esac

if [ -n "$PARAMETER_FILE" ]; then
  echo "Using parameter file specified as $PARAMETER_FILE"
else
  export PARAMETER_FILE=../../parameter_input/example_lhs_params.csv
  echo "Using default parameter file $PARAMETER_FILE"
fi

if [ -n "$NUM_REPEATS" ]; then
  echo "Each parameter set will be repeated $NUM_REPEATS times"
else
  export NUM_REPEATS=1
  echo "Using default number of repeats: $NUM_REPEATS"
fi

source ../environ/env_hamilton.sh

START_TIMESTAMP=`date +%s`

~/reframe/bin/reframe \
    --max-retries=0 \
    --exec-policy async \
    --stage $STAGE_DIR \
    --purge-env \
    -C $config \
    -c parameterisation_tests.py \
    -r \
    -v \
    --performance-report \
    -n \
    'Parameterisation' \
    --output $OUTPUT_DIR \
    --report-file=parameterisation.log

pushd ../../mse_results_from_reframe/

# Find output file based on start timestamp. Probably will be the same as the start timestamp above
# but there's a chance it's a second or two on.
FILE_TIMESTAMP=$START_TIMESTAMP
OUTPUT_FILE="notafile"
while [[ ! -f $OUTPUT_FILE ]]; do
  if [[ "$OSTYPE" == "darwin"* ]]; then
    DATE_ARGS="-r $FILE_TIMESTAMP"
  else
    DATE_ARGS="-d @$FILE_TIMESTAMP"
  fi

  let FILE_TIMESTAMP=$FILE_TIMESTAMP+1
  OUTPUT_FILE="mse_output_$( date $DATE_ARGS +"%Y-%m-%d_%H%M%S" ).csv"

  if [[ $(($FILE_TIMESTAMP - $START_TIMESTAMP)) -gt 3600 ]]; then
    echo "Could not find output file within 1 hour of timestamp $START_TIMESTAMP. Exiting."
    exit 1
  fi
done

ZIPFILE=${OUTPUT_FILE/.csv/.zip}
echo "Creating zip $ZIPFILE"
zip $ZIPFILE $OUTPUT_FILE
zip -j $ZIPFILE $PARAMETER_FILE
OUTPUT_DIR=`pwd`

pushd /ddn/data/$USER/reframe_output/hamilton/multi_cpu_single_node/intel/

zip -r $OUTPUT_DIR/$ZIPFILE Parameterisation_24_*

popd > /dev/null
popd > /dev/null
