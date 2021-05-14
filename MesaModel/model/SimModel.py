import pandas as pd
import math
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from scipy import stats as stats

from .data_types import TeacherParamType, PupilParamType
from .Pupil import Pupil
from .utils import (
    compute_ave,
    compute_ave_disruptive,
    get_num_disruptors,
    get_num_learning,
    get_grid_size,
)


class SimModel(Model):
    def __init__(
        self, class_data, model_initial_state, grid_params, fixed_params=None, **kwargs
    ):
        self.model_state = model_initial_state
        self.grid_params = grid_params

        if fixed_params:
            self.teacher_params, self.pupil_params = fixed_params
        else:
            if "teacher_quality" in kwargs and "teacher_control" in kwargs:
                self.teacher_params = TeacherParamType(
                    kwargs["teacher_quality"], kwargs["teacher_control"]
                )
            else:
                self.teacher_params = TeacherParamType(0, 0)

            if (
                "pupil_inattentiveness" in kwargs
                and "pupil_hyper_impulsivity" in kwargs
                and "pupil_attention_span" in kwargs
            ):
                self.pupil_params = PupilParamType(
                    kwargs["pupil_inattentiveness"],
                    kwargs["pupil_hyper_impulsivity"],
                    kwargs["pupil_attention_span"],
                )
            else:
                self.pupil_params = PupilParamType(0, 0, 2)

        self.schedule = RandomActivation(self)

        # Create grid with torus = False - in a real class students at either ends of classroom don't interact
        self.grid = SingleGrid(
            self.grid_params.width, self.grid_params.height, torus=False
        )

        class_size = len(class_data)
        maths = class_data["start_maths"].to_numpy()
        ability_zscore = stats.zscore(maths)
        inattentiveness = class_data["Inattentiveness"].to_numpy()
        hyper_impulsive = class_data["hyper_impulsive"].to_numpy()

        # Work out how many rows should be full - we spread the gaps
        # across rows rather than the last row being nearly empty
        rows_with_gaps = self.grid.width * self.grid.height - class_size
        full_rows = self.grid.height - rows_with_gaps

        # Set up agents
        counter = 0
        for cell_content, x, y in self.grid.coord_iter():
            if y >= full_rows and x == self.grid.width - 1:
                continue

            # Initial State for all student is random
            agent_type = self.random.randint(1, 3)
            ability = ability_zscore[counter]

            # create agents from data
            agent = Pupil(
                (x, y),
                self,
                agent_type,
                inattentiveness[counter],
                hyper_impulsive[counter],
                maths[counter],
                ability,
            )
            # Place Agents on grid
            self.grid.position_agent(agent, x, y)
            self.schedule.add(agent)
            counter += 1

        # Collecting data while running the model
        self.datacollector = DataCollector(
            model_reporters={
                "Learning Students": get_num_learning,
                "Disruptive Students": get_num_disruptors,
                "Average End Math": compute_ave,
                "disruptiveTend": compute_ave_disruptive,
            },
            # Model-level count of learning agent
            agent_reporters={
                "x": lambda a: a.pos[0],
                "y": lambda a: a.pos[1],
                "Inattentiveness_score": "inattentiveness",
                "Hyper_Impulsivity": "hyper_impulsive",
                "S_math": "s_math",
                "S_read": "s_read",
                "E_math": "e_math",
                "E_read": "e_read",
                "ability": "ability",
                "LearningTime": "countLearning",
                "disruptiveTend": "disruptiveTend",
            },
        )

        self.running = True

    def step(self):

        # Reset counter of learning and disruptive agents
        self.model_state.learning_count = 0
        self.model_state.disruptive_count = 0
        self.datacollector.collect(self)

        # Advance the model by one step
        self.schedule.step()

        # collect data
        self.datacollector.collect(self)
        if self.schedule.steps == 8550.0 or self.running == False:
            self.running = False
            dataAgent = self.datacollector.get_agent_vars_dataframe()
            dataAgent.to_csv("Simulation.csv")
