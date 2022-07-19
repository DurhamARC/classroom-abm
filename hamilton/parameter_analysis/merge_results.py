import os
import sys
import pandas as pd

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../MesaModel")
)
from model.data_types import VARIABLE_PARAM_NAMES

DEFAULT_MSE_LIMIT = 3


def merge_best_results(directory, mse_limit=DEFAULT_MSE_LIMIT):
    print(f"Merging best results in {directory} with limit {mse_limit}")
    output_path = os.path.join(directory, "best_mses.csv")
    merged_dataframe = merge_results(
        directory, "lowest_to_highest_mses", output_path, mse_limit
    )

    means_dataframe = get_means_dataframe(merged_dataframe)
    means_output_path = os.path.join(directory, "best_mse_means.csv")
    means_dataframe.to_csv(
        means_output_path,
        sep=",",
        encoding="utf-8",
        index=False,
    )


def merge_results(directory, filename_pattern, output_file, mse_limit=None):
    print(f"Merging results in {directory} with limit {mse_limit}")
    dataframes = []

    for dirpath, dirnames, filenames in os.walk(directory):
        if not (
            "corrupted" in dirpath
            or "interventions" in dirpath
            or "test_data" in dirpath
        ):
            for f in filenames:
                if filename_pattern in f:
                    full_path = os.path.join(dirpath, f)
                    df = pd.read_csv(full_path, sep=",")
                    if mse_limit:
                        df = df.loc[(df["mean_squared_error"] < mse_limit)]
                    relative_path = os.path.relpath(dirpath, directory)
                    df["directory"] = relative_path
                    dataframes.append(df)

    merged_dataframe = pd.concat(dataframes, axis=0)
    merged_dataframe = merged_dataframe.sort_values(by=["mean_squared_error"])
    merged_dataframe.to_csv(output_file, sep=",", encoding="utf-8", index=False)
    return merged_dataframe


def merge_previous_results(merged_dataframe, output_file):
    print("Merging current results with all previous ones")
    dataframes = []

    if os.path.exists(output_file):
        dataframes.append(pd.read_csv(output_file, sep=","))
    dataframes.append(merged_dataframe)

    merged_dataframe = pd.concat(dataframes, axis=0)
    merged_dataframe = merged_dataframe.sort_values(by=["mean_squared_error"])
    merged_dataframe.to_csv(output_file, sep=",", encoding="utf-8", index=False)

    return merged_dataframe


def merge_repeats(*args, output_dir=os.getcwd()):
    print(f"Saving dataframes from {[arg for arg in args]} in {output_dir}")

    dataframes = []

    for arg in args:
        dataframes.append(pd.read_csv(arg, sep=","))

    merged_dataframe = pd.concat(dataframes, axis=0).sort_values(
        dataframes[0].columns[1:-1].to_list()
    )
    merged_dataframe.to_csv(
        os.path.join(output_dir, "merged_mses.csv"),
        sep=",",
        encoding="utf-8",
        index=False,
    )

    # Sort dataframe from lowest MSE to highest MSE
    merged_dataframe = merged_dataframe.sort_values(by=["mean_squared_error"])
    merged_dataframe.to_csv(
        os.path.join(output_dir, "lowest_to_highest_mses.csv"),
        sep=",",
        encoding="utf-8",
        index=False,
    )
    return merged_dataframe


def get_means_dataframe(merged_dataframe):
    print("Grouping by parameters and sorting by mean MSE for each parameter set")
    columns_to_group = VARIABLE_PARAM_NAMES + ["test_id"]
    print(f"var: columns_to_group = {columns_to_group}")
    if "directory" in merged_dataframe.columns:
        columns_to_group.append("directory")

    return (
        merged_dataframe.groupby(list(columns_to_group))
        .mean()
        .sort_values(by=["mean_squared_error"])
        .reset_index()
    )
