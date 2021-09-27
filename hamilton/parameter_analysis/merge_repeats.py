import pandas as pd
import os
import sys


def merge_repeats(*args, output_dir=os.getcwd()):
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


if __name__ == "__main__":
    merge_repeats(*sys.argv[1:])
