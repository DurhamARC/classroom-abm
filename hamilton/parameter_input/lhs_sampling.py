import csv
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
    "teacher_quality_mean": (3.0, 4.0, 1),
    "teacher_quality_sd": (1.0, 2.0, 1),
    "teacher_control_mean": (0.07, 0.11, 2),
    "teacher_control_sd": (1.0, 2.0, 1),
    "random_select": (0, 4, 1),  # not from Peter; range is a guess
    "school_learn_factor": (0.07, 0.11, 2),
    "home_learn_factor": (
        0.3,
        0.5,
        2,
    ),  # Peter only gives this a single value of 0.0043
    "school_learn_mean_divisor": (1000, 2500, 0),
    "school_learn_sd": (0.03, 0.05, 2),
    "school_learn_random_proportion": (0.1, 0.4, 2),
    "degradation_factor": (0.05, 0.1, 2),
    "conformity_factor": (0.999990, 0.999995, 6),
    "ticks_per_school_day": (170, 330, 0),
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
def cli(num_param_sets, output_file):
    limits = []
    rounding = []
    for param_name in VARIABLE_PARAM_NAMES:
        try:
            param_range_data = PARAM_DICT[param_name]
        except KeyError:
            print(f"Parameter {param_name} is not in PARAM_DICT")
            sys.exit(1)

        limits.append([param_range_data[P_START], param_range_data[P_END]])
        rounding.append(param_range_data[P_ROUND])

    sampling = LHS(criterion="maximin", xlimits=np.array(limits), random_state=5)

    raw_samples = sampling(num_param_sets)

    with open(output_file, "w") as out_file:
        csv_file = csv.writer(out_file)
        csv_file.writerow(["test_id"] + VARIABLE_PARAM_NAMES)
        for test_id, param_set in enumerate(raw_samples):
            rounded_params = []

            for param_num, param in enumerate(param_set):
                rounded_params.append(round(param, rounding[param_num]))

            csv_file.writerow(
                [
                    test_id,
                    *rounded_params,
                ]
            )


if __name__ == "__main__":
    cli()
