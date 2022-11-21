import os
import sys
import pandas as pd

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../MesaModel")
)
from model.data_types import VARIABLE_PARAM_NAMES

DEFAULT_MSE_LIMIT = 3


def merge_best_results(directory, mse_limit=DEFAULT_MSE_LIMIT):
    print(f"Calling mse_results.prepare_next_run()...")
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
    print(f"Calling mse_results.merge_results()...")
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

    merged_dataframe = pd.concat(dataframes, axis=0).sort_values(
        by=["mean_squared_error"]
    )
    merged_dataframe.to_csv(output_file, sep=",", encoding="utf-8", index=False)
    return merged_dataframe


def get_best_means_dataframe(merged_dataframe, output_file=None, school_ids=[]):
    print(f"Calling mse_results.get_best_means_dataframe() on {output_file}...")
    columns_to_group = ["test_id"] + VARIABLE_PARAM_NAMES
    if "directory" in merged_dataframe.columns:
        columns_to_group.append("directory")
    dataframes = []
    school_means_dataframes = (
        []
    )  # = pd.DataFrame(columns = ['school_id'] + merged_dataframe.columns)
    output_file_exists = False
    if os.path.exists(output_file):
        output_file_exists = True

    dataframes.append(merged_dataframe)

    means_dataframe = (
        pd.concat(dataframes, axis=0)
        .groupby(list(columns_to_group))
        .mean()
        .sort_values(by=["mean_squared_error"])
        .reset_index()
    )
    means_dataframe.insert(0, "school_id", 0)

    if school_ids:
        school_means_dataframes.append(
            means_dataframe.drop(
                columns=[f"mse_{school}" for school in school_ids]
            ).head(1)
        )
        for school_id in school_ids:
            means_dataframe.sort_values(by=[f"mse_{school_id}"], inplace=True)
            means_dataframe.reset_index(drop=True, inplace=True)
            means_dataframe.loc[0, "school_id"] = school_id
            means_dataframe.loc[0, "mean_squared_error"] = means_dataframe[
                f"mse_{school_id}"
            ][0]
            school_means_dataframes.append(
                means_dataframe.drop(
                    columns=[f"mse_{school}" for school in school_ids]
                ).head(1)
            )

    if output_file_exists:
        school_means_dataframes.append(pd.read_csv(output_file, sep=","))
    # print(f"school_means_dataframes:\n{school_means_dataframes}\n")
    # print(f"best_means_dataframe:\n{pd.concat(school_means_dataframes, axis=0).sort_values(by=['school_id', 'mean_squared_error'])}\n")
    best_means_dataframe = (
        pd.concat(school_means_dataframes, axis=0)
        .sort_values(by=["school_id", "mean_squared_error"])
        .reset_index(drop=True)
    )
    if output_file_exists:
        best_means_dataframe = best_means_dataframe.iloc[::2]
    print(f"Best means:\n{best_means_dataframe}\n")

    if output_file:
        best_means_dataframe.to_csv(output_file, sep=",", encoding="utf-8", index=False)

    return best_means_dataframe


def merge_repeats(*args, output_dir=os.getcwd(), schools=0):
    print(f"Calling mse_results.merge_repeats()...")

    dataframes = []

    for arg in args:
        dataframes.append(pd.read_csv(arg, sep=","))

    merged_dataframe = pd.concat(dataframes, axis=0).sort_values(
        dataframes[0].columns[1 : -(1 + schools)].to_list()
    )

    # Write to `merged_mses.csv` (ordered by parameter values)
    merged_dataframe.to_csv(
        os.path.join(output_dir, "merged_mses.csv"),
        sep=",",
        encoding="utf-8",
        index=False,
    )

    # Write to `lowest_to_highest_mses.csv` (ordered by MSE)
    merged_dataframe.sort_values(by=["mean_squared_error"], inplace=True)
    merged_dataframe.to_csv(
        os.path.join(output_dir, "lowest_to_highest_mses.csv"),
        sep=",",
        encoding="utf-8",
        index=False,
    )

    return merged_dataframe


def get_means_dataframe(merged_dataframe, output_dir=os.getcwd()):
    print(f"Calling mse_results.get_means_dataframe()...")
    columns_to_group = ["test_id"] + VARIABLE_PARAM_NAMES
    if "directory" in merged_dataframe.columns:
        columns_to_group.append("directory")

    return (
        merged_dataframe.groupby(list(columns_to_group))
        .mean()
        .sort_values(by=["mean_squared_error"])
        .reset_index()
    )
