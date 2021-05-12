from dataclasses import dataclass
from collections import namedtuple


from server import canvas_element, sim_element, sim_chart
from mesa.visualization.ModularVisualization import ModularServer
from model.SimModel import SimModel

"""
Global data types. These serve as containers for model parameters. Where our 
containers are intended to be mutable we use dataclasse, where non-mutability
is required we use namedtuple.
"""
GridParamType = namedtuple("grid_parameters", "height width")
TeacherParamType = namedtuple("teacher_parameters", "quality control")
PupilParamType = namedtuple(
    "pupil_parameters", "inattentiveness hyper_impulsiveness attention_span"
)


@dataclass(unsafe_hash=True)
class ModelState:
    learning_count: int
    disruptive_count: int
    red_state_count: int
    yellow_state_count: int
    green_state_count: int


def launch_model(grid_params, teacher_params, pupil_params, model_initial_state):

    server = ModularServer(
        SimModel,
        [canvas_element, sim_element, sim_chart],
        "Classroom ABM",
        {
            "grid_params": grid_params,
            "teacher_params": teacher_params,
            "pupil_params": pupil_params,
            "model_initial_state": model_initial_state,
        },
    )

    server.launch()


grid_params = GridParamType(6, 5)
teacher_params = TeacherParamType(1, 1)
pupil_params = PupilParamType(0, 0, 2)
model_initial_state = ModelState(0, 0, 0, 0, 0)

launch_model(grid_params, teacher_params, pupil_params, model_initial_state)
