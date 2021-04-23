import math

from mesa import Agent

from utils import compute_ave_disruptive, compute_SD, compute_zscore


class Pupil(Agent):
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
