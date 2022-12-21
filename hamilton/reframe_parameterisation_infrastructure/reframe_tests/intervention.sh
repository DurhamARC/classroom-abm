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
    "--with-tiny-dataset")
        export DATASET=../classes_input/test_input_2_classes.csv
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
  export PARAMETER_FILE=$CLASSROOMABM_PATH/parameter_input/example_lhs_params.csv
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

if [ -n "$FEEDBACK_WEEKS" ]; then
  echo "Teacher quality will be reassessed every $FEEDBACK_WEEKS week(s)"
else
  echo "Teacher quality will be reassessed every week"
fi

if [ -n "$CONVERGENCE_DAYS" ]; then
  echo "Teacher standard deviation will be reduced by teacher_convergence_rate every $CONVERGENCE_DAYS day(s)"
else
  echo "Teacher standard deviation will be reduced by teacher_convergence_rate every 30 days"
fi

###############################################################################

export START_DATETIME=`date +'%Y-%m-%d_%H%M%S'`
if [ -n $MSE_OUTPUT_FILE ]; then
  export MSE_OUTPUT_FILE="../../mse_results_from_reframe/mse_output_${START_DATETIME}.csv"
fi
echo
echo "Outputting CSV to $MSE_OUTPUT_FILE"

export PATH=/apps/infrastructure/modules/default/default/default/Modules/default/bin/:$PATH
~/reframe/bin/reframe \
    --max-retries=0 \
    --exec-policy async \
    --stage $STAGE_DIR \
    --purge-env \
    -C $config \
    -c intervention_tests.py \
    -r \
    -v \
    --performance-report \
    -n \
    'Intervention' \
    --output $OUTPUT_DIR \
    --report-file=intervention.log

# Work out what next parameters should be
mkdir -p $INTERVENTION_RESULTS_DIR

# Set up conda env to save the latest results
module purge
source $HOME/.bashrc
conda init
conda activate classroom_abm
python ../../parameter_analysis/cli.py prepare-next-run -t $START_DATETIME -r $MSE_OUTPUT_FILE -rd $INTERVENTION_RESULTS_DIR

# Reset modules for reframe
module purge
module load python

pushd $INTERVENTION_RESULTS_DIR/$START_DATETIME > /dev/null
cp $PARAMETER_FILE parameters.csv

ZIPFILE=$INTERVENTION_RESULTS_DIR/$START_DATETIME.zip
echo
echo "Creating zip $ZIPFILE"
zip $ZIPFILE *

pushd $OUTPUT_SUBDIR > /dev/null

zip -r $ZIPFILE Intervention_*

popd > /dev/null
popd > /dev/null
