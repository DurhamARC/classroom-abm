import pandas as pd
import sys


if __name__ == "__main__":
    dataframes = []
    for arg in sys.argv[1:]:
        dataframes.append(pd.read_csv(arg, sep=","))

    merged_dataframe = pd.concat(dataframes, axis=0).sort_values(
        dataframes[0].columns[0:-1].to_list()
    )
    merged_dataframe.to_csv("merged_mses.csv", sep=",", encoding="utf-8", index=False)

    # Sort dataframe from lowest MSE to highest MSE
    merged_dataframe = merged_dataframe.sort_values(by=["mean_squared_error"])
    merged_dataframe.to_csv(
        "lowest_to_highest_mses.csv", sep=",", encoding="utf-8", index=False
    )
