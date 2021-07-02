import csv

import click
import numpy as np
from smt.sampling_methods import LHS

# list of dicts that map a parameter to its minimum value, rounding
# accuracy (number of decimal places), and maximum value. The form is:
#       {'param': (min,round,max)}

PARAM_DICT = {
    "teacher_control_mean": (0.07, 2, 0.11),
    "teacher_quality_mean": (3.0, 1, 4.0),
    "random_select": (0, 1, 4),  # not from Peter; range is a guess
    "school_learn_factor": (0.07, 2, 0.11),
    "home_learn_factor": (
        0.3,
        2,
        0.5,
    ),  # Peter only gives this a single value of 0.0043
    "school_learn_mean_divisor": (1000, 0, 2500),
    "school_learn_sd": (0.03, 2, 0.05),
    "school_learn_random_proportion": (0.1, 2, 0.4),
    "ticks_per_school_day": (170, 0, 330),
}

# On ticks_per_school_day: the values and range are what was proposed for time on maths;
# worth checking if it really refers to ticks per day

PARAM_DATA = list(PARAM_DICT.values())
# Position indexes to access tuples in the dict above:
P_START = 0
P_ROUND = 1
P_END = 2


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
    for param_range_data in PARAM_DATA:
        limits.append([param_range_data[P_START], param_range_data[P_END]])

    limits = np.array(limits)
    sampling = LHS(criterion="maximin", xlimits=limits)

    raw_samples = sampling(num_param_sets)

    with open(output_file, "w") as out_file:
        csv_file = csv.writer(out_file)
        csv_file.writerow(
            [
                "test_id",
                "teacher_control_mean",
                "teacher_quality_mean",
                "random_select",
                "school_learn_factor",
                "home_learn_factor",
                "school_learn_mean_divisor",
                "school_learn_sd",
                "school_learn_random_proportion",
                "ticks_per_school_day",
            ]
        )
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
