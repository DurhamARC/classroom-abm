import dataclasses
import os
import shutil
import sys
import csv

this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_dir)
sys.path.append(os.path.join(this_dir, "../../MesaModel"))
sys.path.append(os.path.join(this_dir, "../parameter_input"))

from model.data_types import VARIABLE_PARAM_NAMES
import lhs_sampling
import merge_results
import plot_correlations

CUSTOM_ROUNDING = {
    "teacher_control_variation_sd": 7,
    "home_learn_factor": 7,
    "conformity_factor": 9,
    "maths_ticks_mean": 0,
    "teacher_quality_factor": 5,
}

CUSTOM_LIMITS = {
    "random_select": (1, None),
    "conformity_factor": (None, 1),
    "teacher_quality_variation_sd": (0, None),
    "teacher_control_variation_sd": (0, None),
    "teacher_quality_factor": (0.0, 1.0),
}

CUSTOM_PERCENTAGE_CHANGE = {
    "random_select": 100,
    "conformity_factor": 0.001,
    "teacher_quality_factor": 50,
}
DEFAULT_PERCENTAGE_CHANGE = 8

# Determines how quickly the ranges narrow down; 1 would not change the range;
# 2 would halve the range on each iteration
RANGE_NARROWING_RATE = 1.2


def generate_new_param_file(best_params, output_filename, iteration_number):
    """Generates a new set of parameters based on a range around `best_params`,
    using LHS sampling.
    The range is determined by iteration_number and decreases as iteration_number increases.
    """
    print("Determining next parameter ranges...")
    param_dict = {}
    valid_keys = VARIABLE_PARAM_NAMES
    for k in best_params.keys():
        if k in valid_keys:
            percentage_change = (
                CUSTOM_PERCENTAGE_CHANGE.get(k, DEFAULT_PERCENTAGE_CHANGE)
                / RANGE_NARROWING_RATE**iteration_number
            )
            min_val, max_val = CUSTOM_LIMITS.get(k, (None, None))

            lower_bound = best_params[k] * (1 - percentage_change / 100)
            if min_val is not None:
                lower_bound = max(min_val, lower_bound)

            upper_bound = best_params[k] * (1 + percentage_change / 100)
            if max_val is not None:
                upper_bound = min(max_val, upper_bound)

            param_dict[k] = (lower_bound, upper_bound, CUSTOM_ROUNDING.get(k, 5))

            print(f"{k}: {param_dict[k]}")

    lhs_sampling.generate_lhs_params(
        num_param_sets=25, output_file=output_filename, param_limits=param_dict
    )
    print(
        f"automation.generate_new_param_file(): a new set of 25 parameters in {output_filename} using LHS sampling generated"
    )


def prepare_next_run(
    timestamp,
    output_csv,
    reframe_data_dir,
    parameterisation_data_dir,
    iteration_number,
    merge_csv=None,
):
    """Prepares for the next run by:
    * Creating a subdirectory of `parameterisation_data_dir` using `timestamp`
    * Copying `output_csv` to the directory
    * Creating an ordered CSV and a correlations plot
    * Generating a new set of parameters based on the previous best results, saving to file
      `next_lhs_params_<timestamp>.csv`
    """
    print("Preparing for the next run...")
    current_data_dir = os.path.join(parameterisation_data_dir, timestamp)
    if os.path.exists(current_data_dir):
        print(f"Directory {current_data_dir} already exists. Exiting.")
        sys.exit(1)

    os.mkdir(current_data_dir)
    print(f"automation.prepare_next_run(): {current_data_dir} created")
    shutil.copy(output_csv, current_data_dir)
    print(f"automation.prepare_next_run(): {output_csv} copied")

    # Get dataframes from $OUTPUT_FILE and
    # .. save them in the current merged_mses.csv in the folder of the current iteration
    merged_dataframe = merge_results.merge_repeats(
        output_csv, output_dir=current_data_dir
    )
    print(
        f"automation.prepare_next_run(): dataframes from lowest MSE to highest MSE sorted"
    )
    plot_correlations.plot_correlations(
        os.path.join(current_data_dir, "lowest_to_highest_mses.csv")
    )
    print(f"automation.prepare_next_run(): correlations plotted")

    # Merge the current dataframe with all concatenated merged_mses.csv from previous iterations
    # .. (kept as $MERGE_FILE) and update the $MERGE_FILE
    if merge_csv:
        merged_dataframe = merge_results.merge_previous_results(
            merged_dataframe, merge_csv
        )

    # Group by parameters and sort by mean MSE for each parameter set
    means_dataframe = merge_results.get_means_dataframe(merged_dataframe)
    print(f"automation.prepare_next_run(): the best mean results sorted")
    best_params = means_dataframe.iloc[0]

    next_param_file = os.path.join(current_data_dir, f"next_lhs_params_{timestamp}.csv")
    generate_new_param_file(best_params, next_param_file, iteration_number)
    print(
        f"automation.prepare_next_run(): a new param file `next_lhs_params_{timestamp}.csv` generated"
    )
