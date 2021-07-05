import csv
import sys

import click
import numpy as np
from smt.sampling_methods import LHS

from MesaModel.model.data_types import VARIABLE_PARAM_NAMES

# list of dicts that map a parameter to its minimum value, rounding
# accuracy (number of decimal places), and maximum value. The form is:
#       {'param': (min,max,round)}

PARAM_DICT = {
    "teacher_quality_mean": (3.0, 4.0, 1),
    "teacher_control_mean": (0.07, 0.11, 2),
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
    "ticks_per_school_day": (170, 330, 0),
}

PARAM_DATA = list(PARAM_DICT.values())
# Position indexes to access tuples in the dict above:
P_START = 0
P_END = 1
P_ROUND = 2


def check_parameter_dictionary():
    for parameter in VARIABLE_PARAM_NAMES:
        if parameter not in PARAM_DICT:
            print(
                f"Error! Parameter dictionary is incomplete: no values for {parameter}"
            )
            sys.exit(1)
    if len(VARIABLE_PARAM_NAMES) != len(PARAM_DICT):
        print("Error! Parameter dictionary is missing values")
        sys.exit(1)
    for key in PARAM_DICT.keys():
        if key not in VARIABLE_PARAM_NAMES:
            print(f"Error! Parameter dictionary contains an outdated key: {key}")
            sys.exit(1)


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
    check_parameter_dictionary()

    limits = []
    for param_range_data in PARAM_DATA:
        limits.append([param_range_data[P_START], param_range_data[P_END]])

    limits = np.array(limits)
    sampling = LHS(criterion="maximin", xlimits=limits, random_state=5)

    raw_samples = sampling(num_param_sets)

    with open(output_file, "w") as out_file:
        csv_file = csv.writer(out_file)
        csv_file.writerow(["test_id"] + VARIABLE_PARAM_NAMES)
        test_id = 0
        for param_set in raw_samples:
            param_num = 0
            rounded_params = []

            for param in param_set:
                rounded_params.append(round(param, PARAM_DATA[param_num][P_ROUND]))
                param_num += 1

            csv_file.writerow(
                [
                    test_id,
                    *rounded_params,
                ]
            )
            test_id += 1


if __name__ == "__main__":
    cli()
