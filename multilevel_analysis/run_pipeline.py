import datetime
import sys

import click
from multilevel_analysis import run_multilevel_analysis

sys.path.append("../MesaModel")
from run import run_model
from MesaModel.model.data_types import TeacherParamType, PupilParamType


@click.command()
@click.option(
    "--input-file",
    "-i",
    default="../classes_input/test_input.csv",
    help="File path containing real data, relative to multilevel_analysis directory. Defaults to ../classes_input/test_input.csv",
)
@click.option(
    "--output-file",
    "-o",
    default=f"../classes_output/output{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
    help="Output file path, relative to current working directory.",
)
@click.option(
    "--n-processors",
    "-p",  # 'np' is avoided given the meaning this already has in MPI contexts
    default=2,
    help="Number of processors to be used by the batchrunner",
)
@click.option(
    "--teacher-params",
    default=TeacherParamType(1, 1),
    help="A set of parameters contained in TeacherParamType (for definition see MesaModel/model/data_types.py)",
)
@click.option(
    "--pupil-params",
    default=PupilParamType(0, 0, 2),
    help="A set of parameters contained in PupilParamType (for definition see MesaModel/model/data_types.py)",
)
def run_model_and_mlm(
    input_file, output_file, n_processors, teacher_params, pupil_params
):
    run_model(
        input_file,
        output_file,
        n_processors,
        teacher_params=teacher_params,
        pupil_params=pupil_params,
    )
    mean_squared_error = run_multilevel_analysis(input_file, output_file)
    print(f"Mean squared error: {mean_squared_error}")
    return mean_squared_error


if __name__ == "__main__":
    run_model_and_mlm()
