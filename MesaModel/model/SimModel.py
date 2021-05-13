import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from scipy import stats as stats

from .Pupil import Pupil
from .utils import (
    compute_ave,
    compute_ave_disruptive,
    get_num_disruptors,
    get_num_learning,
)


class SimModel(Model):
    def __init__(
        self,
        input_filepath,
        grid_params,
        teacher_params,
        pupil_params,
        model_initial_state,
    ):

        self.grid_params = grid_params
        self.teacher_params = teacher_params
        self.pupil_params = pupil_params
        self.model_state = model_initial_state

        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(
            self.grid_params.height, self.grid_params.width, torus=True
        )

        # Load data
        all_data = pd.read_csv(input_filepath)
        grouped = all_data.groupby("class_id")

        # For now, just get first class.
        data = grouped.get_group((list(grouped.groups)[0]))

        maths = data["start_maths"].to_numpy()
        ability_zscore = stats.zscore(maths)
        inattentiveness = data["Inattentiveness"].to_numpy()
        hyper_impulsive = data["hyper_impulsive"].to_numpy()

        # Set up agents

        counter = 0
        for cell_content, x, y in self.grid.coord_iter():
            # Initial State for all student is random
            agent_type = self.random.randint(1, 3)
            ability = ability_zscore[counter]

            # create agents form data
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
            self.grid.position_agent(agent, (x, y))
            # print("agent pos:", x, y)
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
