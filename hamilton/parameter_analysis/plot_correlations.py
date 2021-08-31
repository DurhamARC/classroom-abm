import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


if __name__ == "__main__":
    dir = sys.argv[1]
    filename = "lowest_to_highest_mses.csv"
    file_path = os.path.join(dir, filename)
    df = pd.read_csv(file_path)
    y_vars = ["mean_squared_error"]
    x_vars = list(df.columns.values)[:-1]
    pp = sns.pairplot(data=df, y_vars=y_vars, x_vars=x_vars)
    pp.savefig(os.path.join(dir, "correlations.png"))
    plt.show()
