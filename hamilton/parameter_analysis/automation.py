import dataclasses
import os
import shutil
import sys

this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_dir)
sys.path.append(os.path.join(this_dir, "../../MesaModel"))
sys.path.append(os.path.join(this_dir, "../parameter_input"))

from model.data_types import ModelParamType, DEFAULT_MODEL_PARAMS, VARIABLE_PARAM_NAMES
import lhs_sampling
import merge_results
import plot_correlations

CUSTOM_ROUNDING = {
    "home_learn_factor": 7,
    "conformity_factor": 9,
    "maths_ticks_mean": 0,
}

CUSTOM_LIMITS = {"random_select": (1, None), "conformity_factor": (None, 1)}

CUSTOM_PERCENTAGE_CHANGE = {
    "random_select": 100,
    "conformity_factor": 0.001,
    "maths_ticks_sd": 25,
}
DEFAULT_PERCENTAGE_CHANGE = 10


def generate_new_param_file(best_params, output_filename, iteration_number):
    """Generates a new set of parameters based on a range around `best_params`,
    using LHS sampling.
    The range is determined by iteration_number and decreases as iteration_number increases.
    """
    print("Determining next parameter ranges:")
    param_dict = {}
    valid_keys = dataclasses.asdict(DEFAULT_MODEL_PARAMS).keys()
    for k in best_params.keys():
        if k in valid_keys:
            percentage_change = (
                CUSTOM_PERCENTAGE_CHANGE.get(k, DEFAULT_PERCENTAGE_CHANGE)
                / 1.2 ** iteration_number
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


def prepare_next_run(
    timestamp, output_csv, reframe_data_dir, parameterisation_data_dir, iteration_number
):
    """Prepares for the next run by:
    * Creating a subdirectory of `parameterisation_data_dir` using `timestamp`
    * Copying `output_csv` to the directory
    * Creating an ordered CSV and a correlations plot
    * Generating a new set of parameters based on the previous best results, saving to file
      `next_lhs_params_<timestamp>.csv`
    """
    current_data_dir = os.path.join(parameterisation_data_dir, timestamp)
    if os.path.exists(current_data_dir):
        print(f"Directory {current_data_dir} already exists. Exiting.")
        sys.exit(1)

    os.mkdir(current_data_dir)
    shutil.copy(output_csv, current_data_dir)

    merged_dataframe = merge_results.merge_repeats(
        output_csv, output_dir=current_data_dir
    )
    plot_correlations.plot_correlations(
        os.path.join(current_data_dir, "lowest_to_highest_mses.csv")
    )

    # Group by parameters and sort by mean MSE for each parameter set
    means_dataframe = merge_results.get_means_dataframe(merged_dataframe)
    best_params = means_dataframe.iloc[0]

    next_param_file = os.path.join(current_data_dir, f"next_lhs_params_{timestamp}.csv")
    generate_new_param_file(best_params, next_param_file, iteration_number)
