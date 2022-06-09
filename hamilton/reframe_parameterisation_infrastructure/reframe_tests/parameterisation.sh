#!/bin/bash
set -e

case "$1" in
    "--with-big-dataset")
        export DATASET=../classes_input/test_input.csv
        ;;
    "--with-medium-dataset")
        export DATASET=../classes_input/test_input_sampled_25.csv
        ;;
    "--with-test-dataset")
        export DATASET=../classes_input/test_input_sampled_25_test.csv
        ;;
    "--with-small-dataset")
        export DATASET=../classes_input/test_input_short.csv
        ;;
    (*)
        echo "Please name a dataset for this job. Options are: "
        echo "--with-big-dataset (up to 1hr per run), --with-medium-dataset (under 45 mins), --with-small-dataset (under 5 mins)."
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

if [[ $HOSTNAME == *ham8.dur.ac.uk ]]; then
  export HAMILTON_VERSION="hamilton8"
else
  export HAMILTON_VERSION="hamilton7"
fi

source $HOME/.bashrc

echo "Loading env from ../environ/env_${HAMILTON_VERSION}.sh"
source ../environ/env_${HAMILTON_VERSION}.sh

# A file to store all previous concatenated merged_mses.csv
export MERGE_FILE="../../mse_results_from_reframe/all_merged_mses.csv"
[ -f $MERGE_FILE ] && rm $MERGE_FILE
echo "Using ${MERGE_FILE} for storing all previous parameter sets with mean MSEs for narrowing down the parameter range set"

for i in $(seq $NUM_ITERATIONS); do
  START_DATETIME=`date +'%Y-%m-%d_%H%M%S'`
  if [ -n $OUTPUT_FILE ]; then
    export OUTPUT_FILE="../../mse_results_from_reframe/mse_output_${START_DATETIME}.csv"
  fi
  echo "Outputting CSV to $OUTPUT_FILE"

  export PATH=/apps/infrastructure/modules/default/default/default/Modules/default/bin/:$PATH
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
  if [[ $HAMILTON_VERSION == "hamilton7" ]]; then
    module load miniconda2/4.1.11
  else
    source $HOME/.bashrc
    conda init
  fi

  source activate classroom_abm
  python ../../parameter_analysis/cli.py prepare-next-run -t $START_DATETIME -r $OUTPUT_FILE -rd $OUTPUT_DIR -pd $PARAMETERISATION_RESULTS_DIR -it $i -m $MERGE_FILE

  # Reset modules for reframe
  module purge
  module load python

  pushd $PARAMETERISATION_RESULTS_DIR/$START_DATETIME > /dev/null
  cp $PARAMETER_FILE parameters.csv

  ZIPFILE=$PARAMETERISATION_RESULTS_DIR/$START_DATETIME.zip
  echo "Creating zip $ZIPFILE"
  zip $ZIPFILE *

  pushd $OUTPUT_SUBDIR > /dev/null

  zip -r $ZIPFILE Parameterisation_*

  popd > /dev/null
  popd > /dev/null

  if [[ "$i" -lt "$(($NUM_ITERATIONS - 1))" ]]; then
    export PARAMETER_FILE="$PARAMETERISATION_RESULTS_DIR/$START_DATETIME/next_lhs_params_$START_DATETIME.csv"
  fi
done
