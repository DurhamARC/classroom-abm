import datetime
import os
import sys

import click
from mesa.batchrunner import BatchRunnerMP
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from model.data_types import (
    GridParamType,
    TeacherParamType,
    PupilParamType,
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
def run_model_cli(
    input_file, output_file, n_processors, class_id, all_classes, webserver
):
    run_model(input_file, output_file, n_processors, class_id, all_classes, webserver)


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
                "model_params": ModelParamType(
                    2, 0.12, 0.0043, 800, 0.04, 0.2, 100, 2, 2, 5, True
                ),
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
                "pupil_inattentiveness": UserSettableParameter(
                    "slider", "Use Pupil Inattentiveness ", 1.0, 0.00, 1.0, 1.0
                ),
                "pupil_hyper_impulsivity": UserSettableParameter(
                    "slider", "Use Pupil Hyperactivity ", 1.0, 0.00, 1.0, 1.0
                ),
                "pupil_attention_span": UserSettableParameter(
                    "slider", "Pupil Attention Span Limit", 5.0, 0.00, 5.0, 1.0
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
                "teacher_params": TeacherParamType(3.5, 3.5),
                "pupil_params": PupilParamType(0, 0, 2),
                "model_params": ModelParamType(
                    2, 0.12, 0.0043, 800, 0.04, 0.2, 100, 2, 2, 5, True
                ),
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
