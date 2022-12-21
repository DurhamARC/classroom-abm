import os
import sys
import pandas as pd

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../MesaModel")
)
from model.data_types import VARIABLE_PARAM_NAMES

DEFAULT_MSE_LIMIT = 3


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


def get_best_means_dataframe(sorted_merged_dataframe, output_file=None):
    """Stores dataframe with best means calculated for every `test id` in `best_means_dataframe`:
    * Initial list of previous dataframes from $MSE_OUTPUT_FILE: dataframes = [`test_id`; `tq_m`, `tq_sd`, `tq_vsd`, `tq_cr`, `tq_ff`, `tc_m`, `tc_sd`, `tc_vsd`, `tc_cr`, `rs`, `sl_f`, `hl_f`, `sl_md`, `sl_sd`, `sl_rp`, `cf`, `df`, `mt_m`, `mt_sd`; `repeat_no`, `mse`] -> sorted by `mse` from `sorted_merged_dataframe`
    * Intermediate list of dataframes with means for every `test_id`: school_means_dataframes = [(`test_id`; `tq_m`, `tq_sd`, `tq_vsd`, `tq_cr`, `tq_ff`, `tc_m`, `tc_sd`, `tc_vsd`, `tc_cr`, `rs`, `sl_f`, `hl_f`, `sl_md`, `sl_sd`, `sl_rp`, `cf`, `df`, `mt_m`, `mt_sd`); `repeat_no`, `mse`] -> sorted by `mse`
    * Resulting dataframe with best mean: best_means_dataframe -> sorted by `mse`
    """
    print(f"Calling mse_results.get_best_means_dataframe() on {output_file}...")
    columns_to_group = ["test_id"] + VARIABLE_PARAM_NAMES
    dataframes = []
    means_dataframes = []  # = pd.DataFrame(columns = ['school_id'] + sorted_merged_dataframe.columns)

    output_file_exists = False
    if os.path.exists(output_file):
        output_file_exists = True
    dataframes.append(sorted_merged_dataframe)

    sorted_means_dataframe = (
        pd.concat(dataframes, axis=0)
        .groupby(list(columns_to_group))
        .mean()
        .sort_values(by=["mean_squared_error"])
        .reset_index().head(1)
    )

    means_dataframes.append(sorted_means_dataframe.head(1))
    if output_file_exists:
        means_dataframes.append(pd.read_csv(output_file, sep=","))

    best_means_dataframe = (
        pd.concat(means_dataframes, axis=0)
        .sort_values(by=["mean_squared_error"])
        .reset_index(drop=True)
    )
#    if output_file_exists:
    best_means_dataframe = best_means_dataframe.iloc[0]
    print(f"Best means:\n{best_means_dataframe}\n")

    if output_file:
        best_means_dataframe.to_csv(output_file, sep=",", encoding="utf-8", index=False)

    return best_means_dataframe


def merge_repeats(*args, output_dir=os.getcwd()):
    print(f"Calling mse_results.merge_repeats()...")

    dataframes = []

    for arg in args:
        dataframes.append(pd.read_csv(arg, sep=","))

    merged_dataframe = pd.concat(dataframes, axis=0).sort_values(
        dataframes[0].columns[1:-1].to_list()
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
