import datetime
import logging
import os
import sys

import click
from mesa.batchrunner import BatchRunnerMP
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
import numpy as np

from model.data_types import ModelState, DEFAULT_MODEL_PARAMS
from model.input_data import InputData
from model.output_data import OutputDataWriter
from model.SimModel import SimModel
from server import create_canvas_grid, sim_element, sim_chart, PupilMonitorElement

# Set up logging
loglevel = os.getenv("CLASSROOM_ABM_LOG_LEVEL", "INFO")
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: %s" % loglevel)
logfile = os.getenv("CLASSROOM_ABM_LOG_FILE")
logging.basicConfig(
    format="[%(asctime)s: %(levelname)s/%(processName)s %(name)s] %(message)s",
    level=numeric_level,
    filename=logfile,
)


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
@click.option(
    "--speedup",
    "-s",
    default=1,
    help="By how much to speed up the model run",
)
def run_model_cli(
    input_file,
    output_file,
    n_processors,
    class_id,
    all_classes,
    webserver,
    test_mode,
    speedup,
):
    run_model(
        input_file,
        output_file,
        n_processors,
        class_id=class_id,
        all_classes=all_classes,
        webserver=webserver,
        test_mode=test_mode,
        speedup=speedup,
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
    speedup=1,
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
    logging.info("Running on classes: %s", ", ".join([str(i) for i in class_ids]))

    if not model_params:
        model_params = DEFAULT_MODEL_PARAMS

    if test_mode:
        model_params.maths_ticks_mean = 10
        model_params.maths_ticks_sd = 0.1
        model_params.ticks_per_home_day = 10

    # To ensure each thread in the BatchProcessor gets a different random
    # number generator, we use a seed sequence to generate a new seed for
    # each instance of SimModel (one per class), as they run on parallel
    # processors in batch mode, and we need to ensure they don't all produce
    # the same numbers

    # We use a non-reproducible seed sequence to ensure changes to parameters
    # are not masked by the random numbers generated
    ss = np.random.SeedSequence()

    # If we want the rngs to be reproducible in batch mode, we can use the
    # following to get a SeedSequence (see
    # https://albertcthomas.github.io/good-practices-random-number-generators/)
    # random_number_generator = np.random.default_rng(2021)
    # ss = random_number_generator.bit_generator._seed_seq

    # Create an rng for each class
    rngs = [np.random.default_rng(s) for s in ss.spawn(len(class_ids))]

    if webserver:
        canvas_grid = create_canvas_grid(14, 14)
        pupil_element = PupilMonitorElement()
        max_speedup = round(model_params.maths_ticks_mean / 100) * 100
        server = ModularServer(
            SimModel,
            [sim_element, pupil_element, canvas_grid, sim_chart],
            "Classroom ABM",
            {
                "all_data": all_data,
                "model_initial_state": model_initial_state,
                "output_data_writer": output_data_writer,
                "model_params": model_params,
                "canvas_grid": canvas_grid,
                "instructions": UserSettableParameter(
                    "static_text",
                    value="Modify the parameters below then click Reset to update the model."
                    " Setting 'Frames Per Second' to 0 runs the model at maximum speed",
                ),
                "class_id": UserSettableParameter(
                    "choice", "Class ID", value=class_ids[0], choices=class_ids
                ),
                "teacher_quality_mean": UserSettableParameter(
                    "slider",
                    "Teaching quality mean",
                    model_params.teacher_quality_mean,
                    0,
                    5.0,
                    0.1,
                ),
                "teacher_control_mean": UserSettableParameter(
                    "slider",
                    "Teaching control mean",
                    model_params.teacher_control_mean,
                    0.00,
                    5.0,
                    0.1,
                ),
                "random_select": UserSettableParameter(
                    "slider",
                    "Mean for random number used at each step",
                    model_params.random_select,
                    0.00,
                    10.0,
                    0.1,
                ),
                "group_size": UserSettableParameter(
                    "slider",
                    "Size of each group of pupils",
                    model_params.group_size,
                    1,
                    40,
                    1,
                ),
                "group_by_ability": UserSettableParameter(
                    "checkbox",
                    "Group pupils by ability (rather than at random)",
                    model_params.group_by_ability,
                ),
                "speedup": UserSettableParameter(
                    "slider",
                    "How much to speed up (and approximate) the simulation",
                    1,
                    1,
                    max_speedup,
                ),
            },
        )

        port = int(os.getenv("PORT", 4200))
        server.launch(port=port, open_browser=False)

    else:
        print(f"BatchRunnerMP will use {n_processors} processors")
        batch_run = BatchRunnerMP(
            SimModel,
            variable_parameters={
                "class_id_and_rng": list(zip(class_ids, rngs)),
            },
            fixed_parameters={
                "all_data": all_data,
                "model_initial_state": model_initial_state,
                "output_data_writer": output_data_writer,
                "model_params": model_params,
                "speedup": speedup,
            },
            nr_processes=n_processors,
            iterations=1,
            max_steps=1000000,
        )

        batch_run.run_all()


if __name__ == "__main__":
    run_model_cli()
