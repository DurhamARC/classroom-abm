import datetime
import sys

import click
from multilevel_analysis import run_multilevel_analysis

sys.path.append("../MesaModel")
from run import run_model


@click.command()
@click.option(
    "--input-file",
    "-i",
    default="../classes_input/test_input.csv",
    help="File path containing real data, relative to multilevel_analysis directory. Defaults to ../classes_input/test_input.csv",
)
@click.option(
    "--output-file",
    "-o",
    default=f"../classes_output/output{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
    help="Output file path, relative to current working directory.",
)
def run_model_and_mlm(input_file, output_file):
    run_model(input_file, output_file)
    mean_squared_error = run_multilevel_analysis(input_file, output_file)
    print(f"Mean squared error: {mean_squared_error}")
    return mean_squared_error


if __name__ == "__main__":
    run_model_and_mlm()