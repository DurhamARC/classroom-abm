#!/bin/bash
set -e

case "$1" in
    "--with-big-dataset")
        export DATASET=../classes_input/test_input.csv
        ;;
    "--with-medium-dataset")
        export DATASET=../classes_input/test_input_sampled_25.csv
        ;;
    "--with-small-dataset")
        export DATASET=../classes_input/test_input_short.csv
        ;;
    (*)
        echo "Please name a dataset for this job. Options are: "
        echo "--with-big-dataset (up to 1hr per run), --with-medium-dataset (under 15 mins), --with-small-dataset (under 5 mins)."
        exit 1
        ;;
esac

if [ -n "$PARAMETER_FILE" ]; then
  echo "Using parameter file specified as $PARAMETER_FILE (to start)"
else
  export PARAMETER_FILE=../../parameter_input/example_lhs_params.csv
  echo "Using default parameter file $PARAMETER_FILE (to start)"
fi

if [ -n "$NUM_REPEATS" ]; then
  echo "Each parameter set will be repeated $NUM_REPEATS times"
else
  export NUM_REPEATS=1
  echo "Using default number of repeats: $NUM_REPEATS"
fi

if [ -n "$NUM_ITERATIONS" ]; then
  echo "Will generate new parameters and run $NUM_ITERATIONS times"
else
  export NUM_ITERATIONS=1
  echo "Will run one set of parameters."
fi


source ../environ/env_hamilton.sh

for i in $(seq $NUM_ITERATIONS); do
  START_DATETIME=`date +'%Y-%m-%d_%H%M%S'`
  if [ -n $OUTPUT_FILE ]; then
    export OUTPUT_FILE="../../mse_results_from_reframe/mse_output_${START_DATETIME}.csv"
  fi
  echo "Outputting CSV to $OUTPUT_FILE"


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

  # Work out what next parameters should be
  mkdir -p $PARAMETERISATION_RESULTS_DIR

  # Set up conda env to run generate_next_params
  module purge
  module load miniconda2/4.1.11
  source activate classroom_abm
  python ../../parameter_analysis/generate_next_params.py $START_DATETIME $OUTPUT_FILE $OUTPUT_DIR $PARAMETERISATION_RESULTS_DIR

  # Reset modules for reframe
  module purge
  module load python/3.6.8

  pushd $PARAMETERISATION_RESULTS_DIR/$START_DATETIME > /dev/null
  cp $PARAMETER_FILE parameters.csv

  ZIPFILE=$PARAMETERISATION_RESULTS_DIR/$START_DATETIME.zip
  echo "Creating zip $ZIPFILE"
  zip $ZIPFILE *

  pushd $OUTPUT_DIR/hamilton/multi_cpu_single_node/intel/ > /dev/null

  zip -r $ZIPFILE Parameterisation_24_*

  popd > /dev/null
  popd > /dev/null

  if [[ "$i" -lt "$(($NUM_ITERATIONS - 1))" ]]; then
    export PARAMETER_FILE="$PARAMETERISATION_RESULTS_DIR/$START_DATETIME/next_lhs_params_$START_DATETIME.csv"
  fi
done
