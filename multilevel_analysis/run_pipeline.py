import dataclasses
import datetime
import sys

import click
from multilevel_analysis import run_multilevel_analysis

sys.path.append("../MesaModel")
from run import run_model
from model.data_types import (
    ModelParamType,
    DEFAULT_MODEL_PARAMS,
    STATIC_PARAM_COUNT,
    STATIC_PARAMS,
)


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
    "--model-params",
    "-mp",
    type=tuple(
        float for _ in dataclasses.astuple(DEFAULT_MODEL_PARAMS)[:-STATIC_PARAM_COUNT]
    ),
    default=dataclasses.astuple(DEFAULT_MODEL_PARAMS)[:-STATIC_PARAM_COUNT],
    help="""Space separated model params, e.g. 2 2 0.12 0.0043 800 ...

Full parameter list (defined in data_type.ModelParamType) is:

    teacher_quality_mean: float
    teacher_quality_sd: float
    teacher_quality_variation_sd: float
    teacher_control_mean: float
    teacher_control_sd: float
    teacher_control_variation_sd: float
    random_select: float
    school_learn_factor: float
    home_learn_factor: float
    school_learn_mean_divisor: float
    school_learn_sd: float
    school_learn_random_proportion: float
    conformity_factor: float
    degradation_factor: float
    maths_ticks_mean: float
    maths_ticks_sd: float
    teacher_quality_factor: float
""",
)
@click.option(
    "--test-mode",
    "-t",
    default=False,
    is_flag=True,
    help="Whether to run in test mode (only 10 ticks per day)",
)
@click.option(
    "--feedback-period",
    "-f",
    default=1,
    help="Feedback period in weeks how often the teacher quality is reassessed in the model",
)
def run_model_and_mlm(
    input_file, output_file, n_processors, model_params, test_mode, feedback_period
):
    model_params = model_params + STATIC_PARAMS
    run_model(
        input_file,
        output_file,
        n_processors,
        model_params=ModelParamType(*model_params),
        test_mode=test_mode,
        feedback_period=feedback_period,
    )
    mean_squared_error = run_multilevel_analysis(input_file, output_file)
    print(f"Mean squared error: {mean_squared_error}")
    return mean_squared_error


if __name__ == "__main__":
    run_model_and_mlm()
