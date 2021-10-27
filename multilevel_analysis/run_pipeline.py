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
    type=(
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
    ),
    default=dataclasses.astuple(DEFAULT_MODEL_PARAMS)[:-STATIC_PARAM_COUNT],
    help="""Space separated model params for parameterisation, e.g. 2 2 0.12 0.0043 800 ...

Full parameter list (defined in data_type.ModelParamType) is:

    teacher_quality_mean: float
    teacher_quality_sd: float
    teacher_control_mean: float
    teacher_control_sd: float
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
""",
)
@click.option(
    "--all-params",
    "-ap",
    nargs=len(dataclasses.astuple(DEFAULT_MODEL_PARAMS)),
    type=(
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
    ),
    default=None,
    help="""Space separated model params for entire parameter space, e.g. 2 2 0.12 0.0043 800 ...

Overrides model-params if both are set.

Full parameter list (defined in data_type.ModelParamType) is:

    teacher_quality_mean
    teacher_quality_sd
    teacher_control_mean
    teacher_control_sd
    random_select
    school_learn_factor
    home_learn_factor
    school_learn_mean_divisor
    school_learn_sd
    school_learn_random_proportion
    conformity_factor
    degradation_factor
    maths_ticks_mean
    maths_ticks_sd
    ticks_per_home_day
    number_of_holidays
    weeks_per_holiday
    group_size
    group_by_ability
""",
)
@click.option(
    "--test-mode",
    "-t",
    default=False,
    is_flag=True,
    help="Whether to run in test mode (only 10 ticks per day)",
)
def run_model_and_mlm(
    input_file, output_file, n_processors, model_params, all_params, test_mode
):
    if not all_params:
        all_params = model_params + STATIC_PARAMS
    run_model(
        input_file,
        output_file,
        n_processors,
        model_params=ModelParamType(*all_params),
        test_mode=test_mode,
    )
    mean_squared_error = run_multilevel_analysis(input_file, output_file)
    print(f"Mean squared error: {mean_squared_error}")
    return mean_squared_error


if __name__ == "__main__":
    run_model_and_mlm()
