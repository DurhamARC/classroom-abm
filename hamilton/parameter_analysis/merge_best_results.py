import os
import pandas as pd
import sys

DEFAULT_MSE_LIMIT = 3

if __name__ == "__main__":
    dataframes = []

    if len(sys.argv) < 2:
        print("Please provide the directory to search")
        exit(1)

    if len(sys.argv) > 2:
        mse_limit = float(sys.argv[2])
    else:
        mse_limit = DEFAULT_MSE_LIMIT

    for d in os.listdir(sys.argv[1]):
        full_path = os.path.join(sys.argv[1], d)
        if os.path.isdir(full_path) and not d.endswith("corrupted"):
            f = os.path.join(full_path, "lowest_to_highest_mses.csv")
            if os.path.isfile(f):
                df = pd.read_csv(f, sep=",")
                df = df.loc[(df["mean_squared_error"] < mse_limit)]
                df["directory"] = d
                dataframes.append(df)
            else:
                print(f"No such file {f}")

    merged_dataframe = pd.concat(dataframes, axis=0)
    merged_dataframe = merged_dataframe.sort_values(by=["mean_squared_error"])
    output_path = os.path.join(sys.argv[1], "best_mses.csv")
    merged_dataframe.to_csv(output_path, sep=",", encoding="utf-8", index=False)
