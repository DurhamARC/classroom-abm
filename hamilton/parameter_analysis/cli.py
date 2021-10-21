import os
import click
import pandas as pd

import automation
import create_sample as cs
import merge_results
import mlm_analysis
import plot_correlations as pc
import run_webserver_with_params as rwwp


@click.group(help="CLI tool providing utils for parameterisation")
def cli():
    pass


@cli.command()
@click.option(
    "--input-file",
    "-i",
    type=str,
    required=True,
    help="Input CSV file path. CSV should be in the output format produced by reframe or one of the tools here.",
)
@click.option(
    "--output-file",
    "-o",
    default=None,
    help="Output file path, relative to current working directory. If not provided, will create file correlations.png in same directory as input file.",
)
def plot_correlations(input_file, output_file):
    """Creates a set of basic correlation plots from each parameter type to MSE."""
    pc.plot_correlations(input_file, output_file)


@cli.command()
@click.argument("files", nargs=-1)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    help="Directory to output merged CSV, relative to current working directory. If not provided, will create file in the current directory.",
)
def merge_repeats(files, output_dir):
    """Merges the MSE csvs produced by ReFrame's postrun command.
    Creates 2 output CSVs: `merged_mses.csv` (ordered by parameter values)
    and `lowest_to_highest_mses.csv` (ordered by MSE)"""
    merge_results.merge_repeats(*files, output_dir=output_dir)


@cli.command()
@click.option(
    "--directory",
    "-d",
    type=str,
    required=True,
    help="Directory to search for best MSE values",
)
@click.option(
    "--limit",
    "-l",
    type=float,
    default=merge_results.DEFAULT_MSE_LIMIT,
    help="Limit for mean squared error values: only values below the limit will be put in the output file",
)
def merge_best_results(directory, limit):
    """Combines the best results from each set in the given directory into a single dataframe, and plots the correlations"""
    merge_results.merge_best_results(directory, limit)


@cli.command()
@click.option(
    "--directory",
    "-d",
    type=str,
    default="../../parameterisation_results",
    help="Parameterisation results directory (defaults to ../../parameterisation_results)",
)
def analyse_mlms(directory):
    full_models, simple_models = mlm_analysis.get_mlms(directory)
    mlm_analysis.plot_mlm_correlations(
        full_models, os.path.join(directory, "full_model_correlations.png")
    )
    mlm_analysis.plot_mlm_correlations(
        simple_models, os.path.join(directory, "simple_model_correlations.png")
    )


@cli.command()
@click.option(
    "--input-file",
    "-i",
    type=str,
    required=True,
    help="File to extract best params (will use first row)",
)
@click.option(
    "--output-file",
    "-o",
    type=str,
    required=True,
    help="File to write new params",
)
@click.option(
    "--iteration",
    "-it",
    type=int,
    required=True,
    help="Iteration number",
)
def generate_next_params(input_file, output_file, iteration):
    """Generates a new set of parameters based on a range around the input values, using LHS sampling.
    The range is determined by iteration_number and decreases as iteration_number increases.
    """
    best_params = pd.read_csv(input_file).iloc[0]
    automation.generate_new_param_file(best_params, output_file, iteration)


@cli.command()
@click.option(
    "--timestamp",
    "-t",
    type=str,
    required=True,
    help="Timestamp to use in filepaths",
)
@click.option(
    "--reframe-csv",
    "-r",
    type=str,
    required=True,
    help="CSV file with MSE results from reframe",
)
@click.option(
    "--reframe-data-dir",
    "-rd",
    type=str,
    required=True,
    help="Data dir with full results from reframe",
)
@click.option(
    "--parameterisation-data-dir",
    "-pd",
    type=str,
    required=True,
    help="Data dir to output results and new param file",
)
@click.option(
    "--iteration",
    "-it",
    type=int,
    required=True,
    help="Iteration number",
)
def prepare_next_run(
    timestamp, reframe_csv, reframe_data_dir, parameterisation_data_dir, iteration
):
    """Prepares for the next run by:
    * Creating a subdirectory of `parameterisation_data_dir` using `timestamp`
    * Copying `output_csv` to the directory
    * Creating an ordered CSV and a correlations plot
    * Generating a new set of parameters based on the previous best results, saving to file
      `next_lhs_params_<timestamp>.csv`
    """
    automation.prepare_next_run(
        timestamp, reframe_csv, reframe_data_dir, parameterisation_data_dir, iteration
    )


@cli.command()
@click.option(
    "--csv-file",
    "-f",
    type=str,
    required=True,
    help="CSV file from which to get parameters",
)
@click.option(
    "--row-number",
    "-r",
    type=int,
    default=0,
    help="Row number in CSV to use parameters (defaults to first row (-r 0))",
)
def run_webserver_with_params(csv_file, row_number):
    """Runs the Mesa model in webserver mode, defaulting to the parameters from a given row in a given CSV"""
    rwwp.run_webserver_with_params(csv_file, row_number)


@cli.command()
@click.option(
    "--input-file",
    "-i",
    type=str,
    default="../../classes_input/test_input.csv",
    help="Input CSV file. Defaults to ../../classes_input/test_input.csv",
)
@click.option(
    "--output-file",
    "-o",
    default=None,
    help="Output CSV file. Defaults to ../../classes_input/test_input_sampled_<percentage_sample>.csv",
)
@click.option(
    "--percentage-sample",
    "-p",
    type=int,
    required=True,
    help="Percentage of input CSV to sample",
)
def create_sample(input_file, output_file, percentage_sample):
    cs.create_sample(input_file, output_file, percentage_sample)


if __name__ == "__main__":
    cli()
