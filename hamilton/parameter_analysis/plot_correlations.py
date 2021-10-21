import os
import sys

import pandas as pd
import seaborn as sns

sys.path.append("../../MesaModel")

from run import run_model
from model.data_types import ModelParamType, DEFAULT_MODEL_PARAMS, VARIABLE_PARAM_NAMES


def plot_correlations(input_filename, output_filename=None):
    if output_filename is None:
        output_filename = os.path.join(
            os.path.dirname(input_filename), "correlations.png"
        )

    df = pd.read_csv(input_filename)
    df["is_min_mse"] = df.mean_squared_error == df.mean_squared_error.min()

    y_vars = ["mean_squared_error"]
    x_vars = [x for x in VARIABLE_PARAM_NAMES if x in list(df.columns.values)]

    pp = sns.pairplot(
        data=df,
        kind="reg",
        y_vars=y_vars,
        x_vars=x_vars,
        diag_kind=None,
        hue="is_min_mse",
    )
    pp.savefig(output_filename)
