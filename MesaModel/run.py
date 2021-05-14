import os
import sys

from mesa.visualization.ModularVisualization import ModularServer

from model.data_types import TeacherParamType, PupilParamType, ModelState
from model.input_data import InputData
from model.SimModel import SimModel
from server import create_canvas_grid, sim_element, sim_chart
from model.utils import get_grid_size


def launch_model(input_filepath, teacher_params, pupil_params, model_initial_state):
    # Get data first to determine grid size
    all_data = InputData(input_filepath)
    class_id = all_data.get_class_ids()[17]
    class_data = all_data.get_class_data(class_id)

    grid_params = get_grid_size(len(class_data))

    server = ModularServer(
        SimModel,
        [create_canvas_grid(grid_params), sim_element, sim_chart],
        "Classroom ABM",
        {
            "class_data": class_data,
            "grid_params": grid_params,
            "teacher_params": teacher_params,
            "pupil_params": pupil_params,
            "model_initial_state": model_initial_state,
        },
    )

    server.launch()


input_filename = "classes_input/test_input_short.csv"
if len(sys.argv) > 1:
    input_filename = sys.argv[1]
input_filepath = os.path.join(os.getcwd(), input_filename)

teacher_params = TeacherParamType(1, 1)
pupil_params = PupilParamType(0, 0, 2)
model_initial_state = ModelState(0, 0, 0, 0, 0)

launch_model(input_filepath, teacher_params, pupil_params, model_initial_state)
