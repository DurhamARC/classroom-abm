import os

import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from scipy import stats as stats

from Pupil import Pupil
from utils import compute_ave, compute_ave_disruptive


class SimModel(Model):
    def __init__(
        self,
        height=6,
        width=6,
        quality=1,
        Inattentiveness=0,
        control=3,
        hyper_Impulsive=0,
        AttentionSpan=0,
    ):

        self.height = height
        self.width = width
        self.quality = quality
        self.Inattentiveness = Inattentiveness
        self.control = control
        self.hyper_Impulsive = hyper_Impulsive
        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(width, height, torus=True)
        self.AttentionSpan = AttentionSpan

        self.learning = 0
        self.distruptive = 0
        self.redState = 0
        self.yellowState = 0
        self.greenState = 0

        # Load data

        data = pd.read_csv(os.path.join(os.getcwd(), "Input/DataSample.csv"))
        maths = data["s_maths"].to_numpy()
        ability_zscore = stats.zscore(maths)
        behave = data["behav1"].to_numpy()
        behav2 = data["behav2"].to_numpy()

        # Set up agents

        counter = 0
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]

            # Initial State for all student is random
            agent_type = self.random.randint(1, 3)
            ability = ability_zscore[counter]

            # create agents form data
            agent = Pupil(
                (x, y),
                self,
                agent_type,
                behave[counter],
                behav2[counter],
                maths[counter],
                ability,
            )
            # Place Agents on grid
            self.grid.position_agent(agent, (x, y))
            print("agent pos:", x, y)
            self.schedule.add(agent)
            counter += 1

        # Collecting data while running the model
        self.datacollector = DataCollector(
            model_reporters={
                "Distruptive Students": "distruptive",
                "Learning Students": "learning",
                "Average End Math": compute_ave,
                "disruptiveTend": compute_ave_disruptive,
            },
            # Model-level count of learning agent
            agent_reporters={
                "x": lambda a: a.pos[0],
                "y": lambda a: a.pos[1],
                "Inattentiveness_score": "behave",
                "Hyber_Inattinteveness": "behave_2",
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

        self.learning = 0  # Reset counter of learing and disruptive agents
        self.distruptive = 0
        self.datacollector.collect(self)
        self.schedule.step()

        # collect data
        self.datacollector.collect(self)
        if self.schedule.steps == 8550.0 or self.running == False:
            self.running = False
            dataAgent = self.datacollector.get_agent_vars_dataframe()
            dataAgent.to_csv("Simulation.csv")
