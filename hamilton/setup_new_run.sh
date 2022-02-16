cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null
SCRIPT_DIR=`pwd`

module purge
module load miniconda2/4.1.11
module load r/4.0.3
source activate classroom_abm

cd parameter_input
python lhs_sampling.py
export PARAMETER_FILE=`pwd`/lhs_params.csv
export HAMILTON_VERSION=hamilton8
echo "Will run with the following parameters: "
column -s, -t $PARAMETER_FILE


echo "If this looks OK, run the following commands to set off the batch jobs:"
echo "cd $SCRIPT_DIR/reframe_parameterisation_infrastructure/reframe_tests"
echo "export PARAMETER_FILE=`pwd`/lhs_params.csv"
echo "./parameterisation.sh --with-big-dataset"
