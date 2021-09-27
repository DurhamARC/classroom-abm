import dataclasses
import datetime
import os
import pandas as pd
import sys

sys.path.append("../../MesaModel")

from run import run_model
from model.data_types import ModelParamType, DEFAULT_MODEL_PARAMS, VARIABLE_PARAM_NAMES

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please provide a CSV file and row number")
        sys.exit(1)

    parameter_csv = sys.argv[1]
    if not os.path.isfile(parameter_csv):
        print(f"No such file {sys.argv[1]}")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1], sep=",")
    row_number = int(sys.argv[2])
    row = df.iloc[row_number]

    model_param_dict = dataclasses.asdict(DEFAULT_MODEL_PARAMS)
    for k in row.keys():
        if k in model_param_dict:
            model_param_dict[k] = row[k]

    run_model(
        "../../classes_input/test_input_short.csv",
        f"../../classes_output/output{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
        1,
        all_classes=False,
        webserver=True,
        model_params=ModelParamType(**model_param_dict),
    )
