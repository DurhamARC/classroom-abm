import os
import sys

import pandas as pd
import seaborn as sns


if __name__ == "__main__":
    dir = sys.argv[1]
    filename = sys.argv[2]
    file_path = os.path.join(dir, filename)
    df = pd.read_csv(file_path)
    y_vars = ["mean_squared_error"]

    if filename.endswith("best_mses.csv"):
        x_vars = list(df.columns.values)[0:-3]
    else:
        x_vars = list(df.columns.values)[1:-1]

    pp = sns.pairplot(data=df, kind="reg", y_vars=y_vars, x_vars=x_vars)
    pp.savefig(os.path.join(dir, "correlations.png"))
