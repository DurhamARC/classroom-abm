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

source ../environ/env_hamilton.sh

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

