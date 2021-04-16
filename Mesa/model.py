import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import pandas as pd
import scipy.stats as stats
import numpy as np
from statistics import stdev
import statistics
import math


def compute_ave(model):
    agent_maths = [agent.e_math for agent in model.schedule.agents]
    x = sum(agent_maths)
    N = len(agent_maths)
    B = x / N
    print("the AVARAGE of end math", B, agent_maths)
    return B


def compute_ave_disruptive(model):
    agent_disruptiveTend = [agent.disruptiveTend for agent in model.schedule.agents]
    print("Calculate disrubtive tend original", agent_disruptiveTend)
    # B = statistics.mean(agent_disruptiveTend)
    B = np.mean(agent_disruptiveTend)
    print("Calculate disrubtive tend after mean", agent_disruptiveTend)
    print("the AVARAGE of disruptive", B, agent_disruptiveTend)
    return B


def compute_zscore(model, x):
    agent_behave = [agent.behave for agent in model.schedule.agents]
    print("Calculate variance", agent_behave)
    SD = stdev(agent_behave)
    mean = statistics.mean(agent_behave)
    zscore = (x - mean) / SD
    return zscore


def compute_SD(model, x):
    agent_disruptiveTend = [agent.disruptiveTend for agent in model.schedule.agents]
    print("Calculate variance", agent_disruptiveTend)
    b = [float(s) for s in agent_disruptiveTend]
    SD = stdev(b)
    mean = statistics.mean(b)
    zscore = (x - mean) / SD
    if zscore > 1:
        return 1
    else:
        return 0


def normal(agent_ability, x):

    minValue = min(agent_ability)
    maxValue = max(agent_ability)
    rescale = (x - minValue) / maxValue - minValue
    # We want to test rescaling into a different range [1,20]
    a = 0
    b = 1
    rescale = ((b - a) * (x - minValue) / (maxValue - minValue)) + a
    return rescale


def gen_random():
    arr1 = np.random.randint(0, 21, 14)
    arr2 = np.random.randint(21, 69, 14)
    mid = [20, 21]
    i = ((np.sum(arr1 + arr2) + 41) - (20 * 30)) / 69
    decm, intg = math.modf(i)
    args = np.argsort(arr2)
    arr2[args[-70:-1]] -= int(intg)
    arr2[args[-1]] -= int(np.round(decm * 69))
    return np.concatenate((arr1, mid, arr2))


class SimClassAgent(Agent):
    # 1 Initialization
    def __init__(self, pos, model, agent_type, behave, behave_2, math, ability):
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.behave = behave
        self.behave_2 = behave_2
        self.s_math = math
        self.e_math = math

        self.ability = ability

        self.agent_state = self.random.randint(2, 8)
        self.greenState = 0
        self.redState = 0
        self.yellowState = 0
        self.disrubted = 0
        self.countLearning = 0
        self.disruptiveTend = behave

    # self.greenState = 0

    def neighbour(self):
        neighbourCount = 0
        red = 0
        green = 0
        yellow = 0
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            neighbourCount += 1
            if neighbor.type == 3:
                red += 1
            elif neighbor.type == 2:
                yellow += 1
            else:
                green += 1

        return neighbourCount, red, yellow, green

    # define the step function
    def step(self):
        #   self.disrubted += 1
        # self.changeState()
        print(self.model.schedule.steps)
        print("Agent position", self.pos)
        if self.redStateCange() == 1:
            # self.model.distruptive += 1
            self.changeState()
            if self.type == 3:
                self.model.distruptive += 1
            self.set_disruptive_tend()
            self.agent_state = self.random.randint(2, 6)

            return
        elif self.greenStateCange == 1:
            self.changeState()
            self.set_disruptive_tend()
            self.agent_state = self.random.randint(2, 6)

            return

        elif self.yellowStateCange() == 1:
            self.set_disruptive_tend()
            self.changeState()
            if self.type == 3:
                self.model.distruptive += 1
            self.agent_state = self.random.randint(2, 6)

            return

        self.agent_state = self.random.randrange(2, 6)

    def redStateCange(self):
        count, red, yellow, green = self.neighbour()

        if red > 5 and self.type == 2:
            self.type = 3
            self.model.distruptive += 1
            self.disrubted += 1
            self.redState += 1
            self.yellowState = 0
            self.greenState = 0
            return 1

        if red > self.agent_state + 1 and self.disruptiveTend > compute_ave_disruptive(
            self.model
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1
        # if Inattentiveness is on and quality is low
        if (
            self.model.Inattentiveness == 1
            and self.model.quality <= self.agent_state + 1
            and self.behave > self.agent_state
        ):
            self.type = 3
            self.model.distruptive += 1
            self.disrubted += 1
            self.redState += 1
            self.yellowState = 0
            self.greenState = 0
            return 1
        # If both is high and student is disruptive
        if (
            self.model.Inattentiveness == 1
            and self.model.control <= self.agent_state + 1
            and self.behave > self.agent_state
        ):
            self.type = 3
            self.model.distruptive += 1
            self.disrubted += 1
            self.redState += 1
            self.yellowState = 0
            self.greenState = 0
            return 1

        if (
            self.model.hyper_Impulsive == 1
            and self.model.control <= self.agent_state
            and self.behave_2 > self.agent_state
        ):
            self.type = 3
            self.model.distruptive += 1
            self.disrubted += 1
            self.redState += 1
            self.yellowState = 0
            self.greenState = 0
            return 1

    def yellowStateCange(self):

        count, red, yellow, green = self.neighbour()
        if (
            self.model.Inattentiveness == 1
            and self.model.quality >= self.agent_state
            and self.behave <= self.agent_state
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1
        if self.model.Inattentiveness == 0 and self.behave > self.agent_state:
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1
        if (
            compute_SD(self.model, self.disruptiveTend)
            and self.model.control >= self.agent_state
            and self.behave_2 <= self.agent_state
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1
        if self.model.quality > self.agent_state and self.behave > self.agent_state:
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        # if control is less than student state
        if self.model.control <= self.agent_state and self.type == 1:
            self.type = 2
            if self.model.learning > 0:
                self.model.learning -= 1
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return
        # At general if control is high turn into passive
        if self.model.control > self.agent_state and self.behave_2 > self.agent_state:
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if red > 3 and self.type == 1:
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            if self.model.learning > 0:
                self.model.learning -= 1
            return 1

        # Change state based on majority of neighbours' color and agent's current color state

    @property
    def greenStateCange(self):

        count, red, yellow, green = self.neighbour()

        if green > 5 and self.type == 2:
            self.type = 1
            self.model.learning += 1
            self.set_start_math()
            self.redState = 0
            self.yellowState = 0
            self.greenState += 1
            return 1

        if (
            self.model.Inattentiveness != 0
            or self.model.quality <= self.agent_state
            or self.behave >= self.agent_state
        ):
            if (
                self.model.Inattentiveness == 0
                and self.model.quality > self.agent_state
            ):
                self.type = 1
                self.model.learning += 1
                self.set_start_math()
                self.redState = 0
                self.yellowState = 0
                self.greenState += 1
                return 1

            if (
                self.model.hyper_Impulsive == 0
                and self.model.control > self.agent_state >= self.behave_2
            ):
                self.type = 1
                self.model.learning += 1
                self.set_start_math()
                self.redState = 0
                self.yellowState = 0
                self.greenState += 1
                return 1
            if self.model.control > self.agent_state and self.type == 2:
                self.type = 1
                self.model.learning += 1
                self.set_start_math()
                self.redState = 0
                self.yellowState = 0
                self.greenState += 1
                return 1
            return
        self.type = 1
        self.model.learning += 1
        self.set_start_math()
        self.redState = 0
        self.yellowState = 0
        self.greenState += 1
        return 1

    def neighbourState(self):
        count, red, yellow, green = self.neighbour()
        # calculate the probability of each colour
        Pturn_red = red / count
        Pturn_green = green / count
        Pturn_yellow = yellow / count

        if self.type == 3:
            Pturn_red += 0.2
        elif self.type == 2:
            Pturn_yellow += 0.2
        else:
            Pturn_green += 0.2
        colour = max(Pturn_red, Pturn_green, Pturn_yellow)
        if Pturn_red == colour:
            self.type = 3
            self.model.distruptive += 1
            return
        if Pturn_yellow == colour:
            self.type = 2
            return
        if Pturn_green == colour:
            self.type = 1
            self.model.learning += 1
            self.set_start_math()
            return

    def changeState(self):

        # Change to attentive (green) teaching quality or control is high and state is passive for long
        if (
            self.model.quality or self.model.control
        ) > self.agent_state and self.yellowState >= self.agent_state:
            self.type = 1
            self.redState = 0
            self.yellowState = 0
            self.greenState += 1
            self.model.learning += 1
            self.set_start_math()
            return 1

        if (
            self.behave_2 < self.agent_state
            and self.model.control <= self.agent_state
            and self.yellowState > self.agent_state
        ):
            self.type = 1
            self.redState = 0
            self.yellowState = 0
            self.greenState += 1
            self.model.learning += 1
            self.set_start_math()

            return 1
        # Similar to above but red for long
        if (
            self.behave_2 < self.agent_state < self.redState
            and self.model.control <= self.agent_state
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if (
            self.behave < self.agent_state < self.redState
            and self.model.quality <= self.agent_state
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if (
            self.behave < self.agent_state
            and self.model.quality <= self.agent_state
            and self.yellowState > self.agent_state
        ):
            self.type = 1
            self.redState = 0
            self.yellowState = 0
            self.greenState += 1
            self.model.learning += 1
            # self.set_start_math()

            return 1

        if (
            self.behave > self.agent_state
            and self.model.quality > self.agent_state
            and self.redState > self.agent_state
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if (
            self.behave_2 > self.agent_state - 1
            and self.model.control > self.agent_state - 1
            and self.redState > 3
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if self.model.control > self.agent_state and self.redState > 2:
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if (
            self.behave_2 <= self.agent_state
            and self.model.quality <= self.agent_state
            and self.redState > 2
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1
        if (
            self.behave_2 <= self.agent_state - 1
            and self.model.control <= self.agent_state - 1
            and self.redState > self.agent_state
        ):
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1
        if (
            self.behave < self.agent_state
            and self.model.quality < self.agent_state
            and self.redState > self.agent_state
        ):
            self.type = 2
            self.disrubted += 1
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            return 1

        if (
            self.redState > self.agent_state
            and (self.model.quality or self.model.control) >= self.agent_state
        ):
            self.type = 1
            if self.model.distruptive > 0:
                self.model.distruptive -= 1
            self.redState = 0
            self.yellowState = 0
            self.greenState += 1
            self.model.learning += 1
            self.set_start_math()
            return 1
        if self.greenState > self.model.AttentionSpan:
            self.type = 2
            self.redState = 0
            self.yellowState += 1
            self.greenState = 0
            if self.model.learning > 0:
                self.model.learning -= 1
            return 1

    def set_start_math(self):
        # Increment the learning counter
        self.countLearning += 1

        # Scale Smath before using it to calculate end math score
        # 8550t = 7.621204857

        Scaled_Smath = (2.718281828 ** self.s_math) ** (1 / 7.621204857)
        total_learn = self.countLearning + Scaled_Smath
        self.e_math = (7.621204857 * math.log(total_learn)) + self.ability

    def get_type(self):
        return self.type

    def set_disruptive_tend(self):

        self.initialDisrubtiveTend = compute_zscore(self.model, self.behave)

        print("HERE AFTER Z SCORE", self.initialDisrubtiveTend)
        if self.model.schedule.steps == 0:
            self.model.schedule.steps = 1

        self.disruptiveTend = (
            (self.disrubted / self.model.schedule.steps)
            - (self.countLearning / self.model.schedule.steps)
        ) + self.initialDisrubtiveTend

    def test(self):
        print("HI I am test function ##############################")


class SimClass(Model):
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

        data = pd.read_csv("Input/DataSample.csv")
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
            agent = SimClassAgent(
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
