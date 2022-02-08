import csv
import os
import sys

import click
import numpy as np
from smt.sampling_methods import LHS

sys.path.append("../../MesaModel")
from model.data_types import VARIABLE_PARAM_NAMES

# list of dicts that map a parameter to its minimum value, rounding
# accuracy (number of decimal places), and maximum value. The form is:
#       {'param': (min,max,round)}

PARAM_DICT = {
    "teacher_quality_mean": (1, 5, 2),
    "teacher_quality_sd": (0.1, 0.5, 4),
    "teacher_quality_variation_sd": (0.0, 1, 5),
    "teacher_control_mean": (1, 5, 2),
    "teacher_control_sd": (0.1, 0.5, 4),
    "teacher_control_variation_sd": (0.0, 1, 7),
    "random_select": (1, 7, 1),
    "school_learn_factor": (0.01, 0.05, 5),
    "home_learn_factor": (0.0005, 0.0007, 7),
    "school_learn_mean_divisor": (500.0, 2000.0, 1),
    "school_learn_sd": (0.005, 0.01, 5),
    "school_learn_random_proportion": (0.1, 0.5, 4),
    "degradation_factor": (0.08, 0.1, 5),
    "conformity_factor": (0.99999, 0.999995, 9),
    "maths_ticks_mean": (289.0, 600.0, 0),
    "maths_ticks_sd": (1, 5, 2),
}

# Position indices to access tuples in the dict above:
P_START = 0
P_END = 1
P_ROUND = 2


@click.command()
@click.option(
    "--num-param-sets",
    "-ns",
    default=30,
    help="How many sets of params to generate (this will equal the number of ReFrame tests)",
)
@click.option(
    "--output-file",
    "-o",
    default="lhs_params.csv",
    help="Output file path, relative to current working directory",
)
@click.option(
    "--max-options-per-param",
    "-m",
    default=None,
    type=click.IntRange(
        1,
    ),
    help="""Generate no more than m different values per param. Creates a set of m distinct values within the range for
each parameter, then rounds the values found by the maximin LHS sampler to the nearest value. Note that this means the
output will not give a true maximin LHS sample.""",
)
def cli(num_param_sets, output_file, max_options_per_param):
    generate_lhs_params(num_param_sets, output_file, max_options_per_param)


def generate_lhs_params(
    num_param_sets=30,
    output_file="lhs_params.csv",
    max_options_per_param=None,
    param_limits=PARAM_DICT,
):
    limits = []
    rounding = []
    value_list = []
    for param_name in VARIABLE_PARAM_NAMES:
        try:
            param_range_data = param_limits[param_name]
        except KeyError:
            print(f"Parameter {param_name} is not in param_limits")
            sys.exit(1)

        limits.append([param_range_data[P_START], param_range_data[P_END]])
        rounding.append(param_range_data[P_ROUND])

        if max_options_per_param:
            step = (param_range_data[P_END] - param_range_data[P_START]) / (
                max_options_per_param - 1
            )
            values = []
            for i in list(range(max_options_per_param)):
                values.append(param_range_data[P_START] + i * step)
            value_list.append(values)

    sampling = LHS(criterion="maximin", xlimits=np.array(limits), random_state=5)

    raw_samples = sampling(num_param_sets)

    with open(output_file, "w", newline="") as out_file:
        csv_file = csv.writer(out_file, lineterminator=os.linesep)
        csv_file.writerow(["test_id"] + VARIABLE_PARAM_NAMES)
        for test_id, param_set in enumerate(raw_samples):
            rounded_params = []

            for param_num, param in enumerate(param_set):
                if max_options_per_param:
                    # Find the value in the list closest to the suggested param
                    value = min(value_list[param_num], key=lambda x: abs(x - param))
                else:
                    value = param

                rounded_params.append(round(value, rounding[param_num]))

            csv_file.writerow(
                [
                    test_id + 1,
                    *rounded_params,
                ]
            )


if __name__ == "__main__":
    cli()
