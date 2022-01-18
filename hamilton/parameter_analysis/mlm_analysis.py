import os
import re
import sys

import pandas as pd
import seaborn as sns

sys.path.append("../../MesaModel")

from run import run_model
from model.data_types import ModelParamType, DEFAULT_MODEL_PARAMS, VARIABLE_PARAM_NAMES


def get_mlms(directory):
    full_models = pd.DataFrame()
    simple_models = pd.DataFrame()
    param_df = None
    param_dir = None
    test_id_dir_pattern = re.compile(r".*_(\d+)_\d+$")

    for dirpath, dirnames, filenames in os.walk(directory):
        if not (
            dirpath.endswith("corrupted")
            or dirpath.endswith("interventions")
            or dirpath.endswith("test_data")
        ):
            for f in filenames:
                if f.startswith("mse_output_") and f.endswith(".csv"):
                    full_path = os.path.join(dirpath, f)
                    param_df = pd.read_csv(full_path, sep=",", index_col=0)
                    if param_df.index.name == "test_id":
                        param_dir = dirpath
                    else:
                        print(f"No test_id in {full_path}")
                        param_dir = None
                        param_df = None

                elif f.endswith("full_model.csv"):
                    full_path = os.path.join(dirpath, f)
                    if param_df is not None and dirpath.startswith(param_dir):
                        df = pd.read_csv(full_path, sep=",", index_col=0)
                        mlm_series = df["Actual"]

                        m = test_id_dir_pattern.match(dirpath)
                        if m:
                            test_id = int(m.group(1))
                            if test_id in param_df.index:
                                param_series = param_df.loc[test_id]
                                row = pd.concat([param_series, mlm_series])
                                row.name = os.path.relpath(full_path, directory)

                                if "Ability" in mlm_series.index:
                                    full_models = full_models.append(row)
                                else:
                                    simple_models = simple_models.append(row)
                            else:
                                print(f"Could not find test id {test_id} in param_df")
                        else:
                            print(f"Could not find test id in {dirpath}")
                    else:
                        print(f"No valid MSE output file found for {full_path}")

    full_models.to_csv(
        os.path.join(directory, "all_full_models.csv"),
        sep=",",
        encoding="utf-8",
        index=False,
    )
    simple_models.to_csv(
        os.path.join(directory, "all_simple_models.csv"),
        sep=",",
        encoding="utf-8",
        index=False,
    )
    return (full_models, simple_models)


def plot_mlm_correlations(models_df, output_filename):
    # y vars are the parameter names
    y_vars = VARIABLE_PARAM_NAMES

    # Set x vars are the first columns up to the param names
    x_vars = list(models_df.columns.values)[0 : -(len(VARIABLE_PARAM_NAMES) + 1)]

    pp = sns.pairplot(
        data=models_df, kind="reg", y_vars=y_vars, x_vars=x_vars, diag_kind=None
    )
    pp.savefig(output_filename)
