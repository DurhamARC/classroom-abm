import datetime
import os
import sys

import click
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from model.data_types import TeacherParamType, PupilParamType, ModelState
from model.input_data import InputData
from model.output_data import OutputData
from model.SimModel import SimModel
from server import create_canvas_grid, sim_element, sim_chart
from model.utils import get_grid_size


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
    "--class_id", "-c", default=489, type=int, help="ID of class to run model for"
)
@click.option(
    "--all_classes",
    "-a",
    default=False,
    is_flag=True,
    help="Whether to run over all classes (overrides class_id)",
)
@click.option(
    "--webserver",
    "-w",
    default=False,
    is_flag=True,
    help="Whether to run an interactive web server",
)
def run_model(input_file, output_file, class_id, all_classes, webserver):
    input_filepath = os.path.join(os.getcwd(), input_file)
    all_data = InputData(input_filepath)

    class_ids = all_data.get_class_ids()
    if not all_classes:
        if class_id not in class_ids:
            click.echo(f"Invalid class ID {class_id}. Valid classes are: {class_ids}")
            sys.exit(1)
        class_ids = [class_id]
    elif webserver:
        click.echo("Cannot run over all classes in webserver mode (yet!)")

    output_data = OutputData(output_file)

    for class_id in class_ids:
        click.echo(f"Running on class {class_id}")

        # Get data first to determine grid size
        class_data = all_data.get_class_data(class_id)
        grid_params = get_grid_size(len(class_data))
        model_initial_state = ModelState(0, 0, 0, 0, 0)

        if webserver:
            server = ModularServer(
                SimModel,
                [create_canvas_grid(grid_params), sim_element, sim_chart],
                "Classroom ABM",
                {
                    "class_data": class_data,
                    "model_initial_state": model_initial_state,
                    "output_data": output_data,
                    "grid_params": grid_params,
                    "teacher_quality": UserSettableParameter(
                        "slider", "Teaching quality", 5.0, 0.00, 5.0, 1.0
                    ),
                    "teacher_control": UserSettableParameter(
                        "slider", "Teaching control", 5.0, 0.00, 5.0, 1.0
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
            teacher_params = TeacherParamType(1, 1)
            pupil_params = PupilParamType(0, 0, 2)

            model = SimModel(
                class_data,
                model_initial_state,
                output_data,
                grid_params,
                fixed_params=(teacher_params, pupil_params),
            )
            model.run_model()

    output_data.write_file()


if __name__ == "__main__":
    run_model()
