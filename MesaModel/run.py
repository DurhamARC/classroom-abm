from recordclass import recordclass

from server import canvas_element, sim_element, sim_chart
from mesa.visualization.ModularVisualization import ModularServer
from model.SimModel import SimModel

"""
Global data types. These serve as containers for model parameters and resemble C/C++ structs.
"""
GRID_STRUCT = recordclass("grid_parameters", "height width")
TEACHER_STRUCT = recordclass("teacher_parameters", "quality control")
PUPIL_STRUCT = recordclass(
    "pupil_parameters", "inattentiveness hyper_impulsiveness attention_span"
)
MODEL_INIT_STRUCT = recordclass(
    "init_params",
    "learning_count disruptive_count red_state_count yellow_state_count green_state_count",
)


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


grid_params = GRID_STRUCT(6, 5)
teacher_params = TEACHER_STRUCT(0, 0)
pupil_params = PUPIL_STRUCT(0, 0, 2)
model_initial_state = MODEL_INIT_STRUCT(0, 0, 0, 0, 0)

launch_model(grid_params, teacher_params, pupil_params, model_initial_state)
