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
        self,
        class_data,
        model_initial_state,
        output_data,
        grid_params,
        fixed_params=None,
        **kwargs
    ):
        self.model_state = model_initial_state
        self.grid_params = grid_params
        self.output_data = output_data

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

        self.class_size = len(class_data)
        self.class_id = class_data["class_id"].iloc[0]
        maths = class_data["start_maths"].to_numpy()
        student_id = class_data["student_id"].to_numpy()
        ability_zscore = stats.zscore(maths)
        inattentiveness = class_data["Inattentiveness"].to_numpy()
        hyper_impulsive = class_data["hyper_impulsive"].to_numpy()
        deprivation = class_data["Deprivation"].to_numpy()

        # Work out how many rows should be full - we spread the gaps
        # across rows rather than the last row being nearly empty
        rows_with_gaps = self.grid.width * self.grid.height - self.class_size
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
                student_id[counter],
                agent_type,
                inattentiveness[counter],
                hyper_impulsive[counter],
                deprivation[counter],
                maths[counter],
                ability,
            )
            # Place Agents on grid
            self.grid.position_agent(agent, x, y)
            self.schedule.add(agent)
            counter += 1

        # Collecting data while running the model
        self.model_datacollector = DataCollector(
            model_reporters={
                "Learning Students": get_num_learning,
                "Disruptive Students": get_num_disruptors,
                "Average End Math": compute_ave,
                "disruptiveTend": compute_ave_disruptive,
            }
        )

        self.agent_datacollector = DataCollector(
            agent_reporters={
                "student_id": "student_id",
                "end_maths": "e_math",
                "start_maths": "s_math",
                "Ability": "ability",
                "Inattentiveness": "inattentiveness",
                "hyper_impulsive": "hyper_impulsive",
                "Deprivation": "deprivation",
            }
        )

        self.running = True

    def step(self):

        # Reset counter of learning and disruptive agents
        self.model_state.learning_count = 0
        self.model_state.disruptive_count = 0

        # Advance the model by one step
        self.schedule.step()

        # collect data
        self.model_datacollector.collect(self)

        if self.schedule.steps == 8550.0 or self.running == False:
            self.running = False
            self.agent_datacollector.collect(self)
            agent_data = self.agent_datacollector.get_agent_vars_dataframe()
            self.output_data.append_data(agent_data, self.class_id, self.class_size)
