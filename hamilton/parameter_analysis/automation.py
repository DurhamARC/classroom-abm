import dataclasses
import os
import shutil
import sys
import csv

this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_dir)
sys.path.append(os.path.join(this_dir, "../../MesaModel"))
sys.path.append(os.path.join(this_dir, "../parameter_input"))

from model.data_types import VARIABLE_PARAM_NAMES, BEST_PARAM_NAMES
from model.input_data import InputData
import lhs_sampling
import mse_results as mse_results
import plot_correlations

CUSTOM_ROUNDING = {
    "teacher_quality_convergence_rate": 5,
    "teacher_quality_feedback_factor": 5,
    "teacher_control_variation_sd": 7,
    "teacher_control_convergence_rate": 5,
    "home_learn_factor": 7,
    "conformity_factor": 9,
    "maths_ticks_mean": 0,
}

CUSTOM_LIMITS = {
    "random_select": (1, None),
    "conformity_factor": (None, 1),
    "teacher_quality_variation_sd": (0, None),
    "teacher_quality_convergence_rate": (0.0, 1.0),
    "teacher_quality_feedback_factor": (0.0, 1.0),
    "teacher_control_variation_sd": (0, None),
    "teacher_control_convergence_rate": (0.0, 1.0),
}

CUSTOM_PERCENTAGE_CHANGE = {
    "teacher_quality_feedback_factor": 50,
    "teacher_quality_convergence_rate": 50,
    "teacher_control_convergence_rate": 50,
    "random_select": 100,
    "conformity_factor": 0.001,
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
    print(f"Calling automation.generate_new_param_file()...")
    # print()
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


#    print(f"automation.generate_new_param_file(): a new set of 25 parameters in {output_filename} using LHS sampling generated")


def save_best_param_file(best_params, output_file="best_params.csv"):
    """Saves the best parameters:
    * Saving the overall values (shool_id==0) as well as for each school individually (with their school ids) as `best_params`
    """
    print(f"Calling automation.save_best_param_file()...")
    # params = []
    with open(output_file, "w", newline="") as out_file:
        csv_file = csv.writer(out_file, lineterminator=os.linesep)
        csv_file.writerow(["school_id", "test_id"] + BEST_PARAM_NAMES)
        valid_keys = BEST_PARAM_NAMES

        for school_id in best_params.keys():
            params = []
            test_id = int(best_params[school_id]["test_id"])
            for k in best_params[school_id].keys():
                if k in valid_keys:
                    value = best_params[school_id][k]
                    params.append(value)
            csv_file.writerow(
                [
                    school_id,
                    test_id,
                    *params,
                ]
            )


def prepare_next_run(
    timestamp,
    mse_output_csv,
    parameterisation_data_dir,
    iteration_number,
    merge_csv=None,
):
    """Prepares for the next run by:
    * Creating a subdirectory of `parameterisation_data_dir` using `timestamp`
    * Copying the resulting `mse_output_csv` of the last parameterisation test to `parameterisation_data_dir`
    * Creating an ordered CSV and a correlations plot
    * Generating and saving a new set of parameters based on the previous best results as `next_lhs_params_<timestamp>.csv`
    """
    print(f"Calling automation.prepare_next_run()...")
    current_data_dir = os.path.join(parameterisation_data_dir, timestamp)
    if os.path.exists(current_data_dir):
        print(f"Directory {current_data_dir} already exists. Exiting.")
        sys.exit(1)

    os.mkdir(current_data_dir)
    shutil.copy(mse_output_csv, current_data_dir)
    input_file = os.path.join(
        os.environ["PROJECT_PATH"], "multilevel_analysis", os.environ["DATASET"]
    )
    school_ids = InputData(input_file).get_school_ids()

    # Get dataframes from $MSE_OUTPUT_FILE and
    # .. save them in the current merged_mses.csv in the folder of the current iteration
    merged_dataframe = mse_results.merge_repeats(
        mse_output_csv, output_dir=current_data_dir, schools=len(school_ids)
    )
    plot_correlations.plot_correlations(
        os.path.join(current_data_dir, "lowest_to_highest_mses.csv")
    )

    # Merge the current dataframe with all previously calculated best means for every school
    # ($MERGE_FILE stores the best means up-to-date)

    # Group by parameters and sort by mean MSE for each parameter set
    means_dataframe = mse_results.get_best_means_dataframe(
        merged_dataframe, output_file=merge_csv, school_ids=school_ids
    )

    #    means_dataframe = mse_results.get_means_dataframe(school_dataframe, output_dir=current_data_dir)
    means_by_school = means_dataframe.groupby("school_id")
    school_ids = list(means_by_school.groups.keys())
    print(f"school_ids: {school_ids}")
    best_params = dict()
    for i, school_id in enumerate(school_ids):
        nrows = i  # * iteration_number * int(os.environ["NUM_PARAMETERS"])
        best_params[school_id] = means_dataframe.iloc[nrows]

    next_param_file = os.path.join(current_data_dir, f"next_lhs_params_{timestamp}.csv")
    best_param_file = os.path.join(current_data_dir, f"best_params.csv")
    save_best_param_file(best_params, best_param_file)
    generate_new_param_file(best_params[0], next_param_file, iteration_number)
