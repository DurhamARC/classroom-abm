import datetime
import os
import sys

import click
from mesa.batchrunner import BatchRunnerMP
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from model.data_types import (
    GridParamType,
    ModelParamType,
    ModelState,
)
from model.input_data import InputData
from model.output_data import OutputDataWriter
from model.SimModel import SimModel
from server import create_canvas_grid, sim_element, sim_chart


@click.command()
@click.option(
    "--input-file",
    "-i",
    default="../classes_input/test_input_short.csv",
    help="Input file path, relative to current working directory",
)
@click.option(
    "--output-file",
    "-o",
    default=f"../classes_output/output{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
    help="Output file path, relative to current working directory",
)
@click.option(
    "--n-processors",
    "-p",  # 'np' is avoided given the meaning this already has in MPI contexts
    default=2,
    help="Number of processors to be used by the batchrunner (used only if -a is set)",
)
@click.option(
    "--class_id", "-c", default=489, type=int, help="ID of class to run model for"
)
@click.option(
    "--all_classes",
    "-a",
    default=False,
    is_flag=True,
    help="Whether to run over all classes (overrides class_id; not available in webserver mode)",
)
@click.option(
    "--webserver",
    "-w",
    default=False,
    is_flag=True,
    help="Whether to run an interactive web server",
)
@click.option(
    "--test-mode",
    "-t",
    default=False,
    is_flag=True,
    help="Whether to run in test mode (only 10 ticks per day)",
)
def run_model_cli(
    input_file, output_file, n_processors, class_id, all_classes, webserver, test_mode
):
    run_model(
        input_file,
        output_file,
        n_processors,
        class_id,
        all_classes,
        webserver,
        test_mode,
    )


"""
run_model() has been separated from run_model_cli() so that it can be imported in
run_pipeline.py without the commandline argument infrastructure that is associated
with run_model_cli(). Therefore, run_model_cli() is simply a wrapper around run_model()
that facilitates the running of the model without the multilevel model postprocessing.
"""


def run_model(
    input_file,
    output_file,
    n_processors,
    class_id=None,
    all_classes=True,
    webserver=False,
    model_params=None,
    test_mode=False,
):
    input_filepath = os.path.join(os.getcwd(), input_file)
    all_data = InputData(input_filepath)

    class_ids = all_data.get_class_ids()
    if webserver:
        if all_classes:
            click.echo("Cannot run over all classes in webserver mode (yet!)")
            sys.exit(2)
    else:
        if not all_classes:
            if class_id not in class_ids:
                click.echo(
                    f"Invalid class ID {class_id}. Valid classes are: {class_ids}"
                )
                sys.exit(1)
            if not webserver:
                class_ids = [class_id]

    output_data_writer = OutputDataWriter(output_file)

    # Get data first to determine grid size
    model_initial_state = ModelState(0, 0, 0, 0, 0)
    click.echo(f"Running on class {class_ids}")

    if not model_params:
        model_params = ModelParamType(
            teacher_quality=2,
            teacher_control=2,
            random_select=2,
            school_learn_factor=0.12,
            home_learn_factor=0.0043,
            school_learn_mean_divisor=800,
            school_learn_sd=0.04,
            school_learn_random_proportion=0.2,
            ticks_per_school_day=100,
            ticks_per_home_day=330,
            number_of_holidays=2,
            weeks_per_holiday=2,
            group_size=5,
            group_by_ability=True,
        )

    if test_mode:
        model_params.ticks_per_school_day = 10
        model_params.ticks_per_home_day = 10

    if webserver:
        canvas_grid = create_canvas_grid(12, 12)
        server = ModularServer(
            SimModel,
            [canvas_grid, sim_element, sim_chart],
            "Classroom ABM",
            {
                "all_data": all_data,
                "model_initial_state": model_initial_state,
                "output_data_writer": output_data_writer,
                "model_params": model_params,
                "canvas_grid": canvas_grid,
                "instructions": UserSettableParameter(
                    "static_text",
                    value="Modify the parameters below then click Reset to update the model.",
                ),
                "class_id": UserSettableParameter(
                    "choice", "Class ID", value=class_ids[0], choices=class_ids
                ),
                "teacher_quality": UserSettableParameter(
                    "slider", "Teaching quality", 1.0, 0.00, 5.0, 1.0
                ),
                "teacher_control": UserSettableParameter(
                    "slider", "Teaching control", 2.0, 0.00, 5.0, 1.0
                ),
            },
        )

        server.launch()

    else:
        print(f"BatchRunnerMP will use {n_processors} processors")
        batch_run = BatchRunnerMP(
            SimModel,
            variable_parameters={"class_id": class_ids},
            fixed_parameters={
                "all_data": all_data,
                "model_initial_state": model_initial_state,
                "output_data_writer": output_data_writer,
                "model_params": model_params,
            },
            nr_processes=n_processors,
            iterations=1,
            max_steps=1000000,
            agent_reporters={
                "student_id": "student_id",
                "end_maths": "e_math",
                "start_maths": "s_math",
                "Ability": "ability",
                "Inattentiveness": "inattentiveness",
                "hyper_impulsive": "hyper_impulsive",
                "Deprivation": "deprivation",
            },
        )

        batch_run.run_all()


if __name__ == "__main__":
    run_model_cli()
