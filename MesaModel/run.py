from recordclass import recordclass

from server import canvas_element, sim_element, sim_chart
from mesa.visualization.ModularVisualization import ModularServer
from model.SimModel import SimModel


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


grid_struct = recordclass("grid_parameters", "height width")
teacher_struct = recordclass("teacher_parameters", "quality control")
pupil_struct = recordclass(
    "pupil_parameters", "inattentiveness hyper_impulsiveness attention_span"
)
model_init_struct = recordclass(
    "init_params",
    "learning_count disruptive_count red_state_count yellow_state_count green_state_count",
)

grid_params = grid_struct(6, 5)
teacher_params = teacher_struct(1, 3)
pupil_params = pupil_struct(0, 0, 0)
model_initial_state = model_init_struct(0, 0, 0, 0, 0)

launch_model(grid_params, teacher_params, pupil_params, model_initial_state)
