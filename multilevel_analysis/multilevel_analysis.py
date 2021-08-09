import os
import subprocess
import sys

import click


def run_rscript(script=None, scriptname=None, args=None):
    params = ["Rscript"]
    if script:
        params.extend(["-e", script])
    elif scriptname:
        params.append(scriptname)
    else:
        print("script or filename must be specified")
        sys.exit(2)

    if args:
        params.extend(args)

    print(f"Running: {' '.join(params)}")
    completed = subprocess.run(
        params,
        capture_output=True,
        text=True,
        cwd="./R/run_mlm",
    )

    if completed.returncode:
        print("Error running R script:")
        print(completed.stdout)
        print(completed.stderr)
        sys.exit(1)

    return completed.stdout


@click.command()
@click.option(
    "--real-data-file",
    "-r",
    default="../classes_input/test_input.csv",
    help="File path containing real data, relative to multilevel_analysis directory. Defaults to ../classes_input/test_input.csv",
)
@click.option(
    "--simulated-data-file",
    "-s",
    required=True,
    help="Output file path, relative to current working directory",
)
def run_mlm(real_data_file, simulated_data_file):
    mse = run_multilevel_analysis(real_data_file, simulated_data_file)
    if mse is not None:
        click.echo(f"Mean squared error: {mse}")


def run_multilevel_analysis(real_data_file, simulated_data_file):
    here = os.path.dirname(os.path.realpath(__file__))
    real_data_path = os.path.join(
        here,
        real_data_file,
    )
    simulated_data_path = os.path.join(here, simulated_data_file)

    run_rscript(script="renv::restore()")
    output = run_rscript(
        scriptname="run_classroommlm.R", args=[real_data_path, simulated_data_path]
    )
    output_lines = output.splitlines()
    try:
        mse = float(output_lines[-1])
    except ValueError:
        print("Could not convert {mse} to float")
        sys.exit(2)

    return mse


if __name__ == "__main__":
    run_mlm()
