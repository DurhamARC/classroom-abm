import os
import sys

import pandas as pd
import seaborn as sns

sys.path.append("../../MesaModel")

from run import run_model
from model.data_types import ModelParamType, DEFAULT_MODEL_PARAMS, VARIABLE_PARAM_NAMES


def plot_correlations(input_filename, output_filename=None):
    print("Plotting correlations...")
    if output_filename is None:
        output_filename = os.path.join(
            os.path.dirname(input_filename), "correlations.png"
        )

    df = pd.read_csv(input_filename)
    try:
        df["is_min_mse"] = df.mean_squared_error == df.mean_squared_error.min()

        y_vars = ["mean_squared_error"]
        x_vars = [x for x in VARIABLE_PARAM_NAMES if x in list(df.columns.values)]
        print(f"var: x_vars = {x_vars}")

        grid = sns.PairGrid(df, x_vars=x_vars, y_vars=y_vars, hue="is_min_mse")
        grid = grid.map(sns.regplot, order=2)
        grid.add_legend()
        grid.tight_layout()
        grid.savefig(output_filename)
    except Exception as e:
        print("Could not generate correlations plots: " + str(e))


def plot_scores(input_filename, output_filename=None):
    print("Plotting scores...")
    if output_filename is None:
        output_filename = os.path.join(
            os.path.dirname(input_filename), "scores.png"
        )

    df = pd.read_csv(input_filename)
    try:
        df["is_max_score"] = df.avg_maths_score == df.avg_maths_score.max()

        y_vars = ["avg_maths_score"]
        x_vars = [x for x in VARIABLE_PARAM_NAMES if x in list(df.columns.values)]
        print(f"var: x_vars = {x_vars}")

        grid = sns.PairGrid(df, x_vars=x_vars, y_vars=y_vars, hue="is_max_score")
        grid = grid.map(sns.regplot, order=2)
        grid.add_legend()
        grid.tight_layout()
        grid.savefig(output_filename)
    except Exception as e:
        print("Could not generate scores plots: " + str(e))