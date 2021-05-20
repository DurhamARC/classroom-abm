import math

from mesa import Agent

from .utils import compute_ave_disruptive, compute_SD, compute_zscore


class Pupil(Agent):
    # 1 Initialization
    def __init__(
        self,
        pos,
        model,
        student_id,
        agent_type,
        inattentiveness,
        hyper_impulsive,
        deprivation,
        math,
        ability,
    ):
        super().__init__(pos, model)
        self.pos = pos
        self.student_id = student_id
        self.type = agent_type
        self.inattentiveness = inattentiveness
        self.hyper_impulsive = hyper_impulsive
        self.deprivation = deprivation
        self.s_math = math
        self.e_math = math

        self.ability = ability

        self.randomised_agent_attribute = self.random.randint(2, 8)
        self.time_in_green_state = 0
        self.time_in_red_state = 0
        self.time_in_yellow_state = 0
        self.disruptive = 0
        self.countLearning = 0
        self.disruptiveTend = inattentiveness

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
        # print(self.model.schedule.steps)
        # print("Agent position", self.pos)
        if self.redStateCange() == 1:
            self.changeState()
            if self.type == 3:
                self.model.model_state.disruptive_count += 1
            self.set_disruptive_tend()
            self.randomised_agent_attribute = self.random.randint(2, 6)

            return

        elif self.greenStateChange == 1:
            self.changeState()
            self.set_disruptive_tend()
            self.randomised_agent_attribute = self.random.randint(2, 6)

            return

        elif self.yellowStateCange() == 1:
            self.set_disruptive_tend()
            self.changeState()
            if self.type == 3:
                self.model.model_state.disruptive_count += 1
            self.randomised_agent_attribute = self.random.randint(2, 6)

            return

        self.randomised_agent_attribute = self.random.randrange(2, 6)

    def redStateCange(self):
        count, red, yellow, green = self.neighbour()

        if red > 5 and self.type == 2:
            self.type = 3
            self.model.model_state.disruptive_count += 1
            self.disruptive += 1
            self.time_in_red_state += 1
            self.time_in_yellow_state = 0
            self.time_in_green_state = 0
            return 1

        if (
            red > self.randomised_agent_attribute + 1
            and self.disruptiveTend > compute_ave_disruptive(self.model)
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1
        # if Inattentiveness is on and quality is low
        if (
            self.model.pupil_params.inattentiveness == 1
            and self.model.teacher_params.quality <= self.randomised_agent_attribute + 1
            and self.inattentiveness > self.randomised_agent_attribute
        ):
            self.type = 3
            self.model.model_state.disruptive_count += 1
            self.disruptive += 1
            self.time_in_red_state += 1
            self.time_in_yellow_state = 0
            self.time_in_green_state = 0
            return 1
        # If both is high and student is disruptive
        if (
            self.model.pupil_params.inattentiveness == 1
            and self.model.teacher_params.control <= self.randomised_agent_attribute + 1
            and self.inattentiveness > self.randomised_agent_attribute
        ):
            self.type = 3
            self.model.model_state.disruptive_count += 1
            self.disruptive += 1
            self.time_in_red_state += 1
            self.time_in_yellow_state = 0
            self.time_in_green_state = 0
            return 1

        if (
            self.model.pupil_params.hyper_impulsivity == 1
            and self.model.teacher_params.control <= self.randomised_agent_attribute
            and self.hyper_impulsive > self.randomised_agent_attribute
        ):
            self.type = 3
            self.model.model_state.disruptive_count += 1
            self.disruptive += 1
            self.time_in_red_state += 1
            self.time_in_yellow_state = 0
            self.time_in_green_state = 0
            return 1

    def yellowStateCange(self):

        count, red, yellow, green = self.neighbour()
        if (
            self.model.pupil_params.inattentiveness == 1
            and self.model.teacher_params.quality >= self.randomised_agent_attribute
            and self.inattentiveness <= self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1
        if (
            self.model.pupil_params.inattentiveness == 0
            and self.inattentiveness > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1
        if (
            compute_SD(self.model, self.disruptiveTend)
            and self.model.teacher_params.control >= self.randomised_agent_attribute
            and self.hyper_impulsive <= self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1
        if (
            self.model.teacher_params.quality > self.randomised_agent_attribute
            and self.inattentiveness > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        # if control is less than student state
        if (
            self.model.teacher_params.control <= self.randomised_agent_attribute
            and self.type == 1
        ):
            self.type = 2
            if self.model.model_state.learning_count > 0:
                self.model.model_state.learning_count -= 1
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return
        # At general if control is high turn into passive
        if (
            self.model.teacher_params.control > self.randomised_agent_attribute
            and self.hyper_impulsive > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if red > 3 and self.type == 1:
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            if self.model.model_state.learning_count > 0:
                self.model.model_state.learning_count -= 1
            return 1

        # Change state based on majority of neighbours' color and agent's current color state

    @property
    def greenStateChange(self):

        count, red, yellow, green = self.neighbour()

        if green > 5 and self.type == 2:
            self.type = 1
            self.model.model_state.learning_count += 1
            self.set_start_math()
            self.time_in_red_state = 0
            self.time_in_yellow_state = 0
            self.time_in_green_state += 1
            return 1

        if (
            self.model.pupil_params.inattentiveness != 0
            or self.model.teacher_params.quality <= self.randomised_agent_attribute
            or self.inattentiveness >= self.randomised_agent_attribute
        ):
            if (
                self.model.pupil_params.inattentiveness == 0
                and self.model.teacher_params.quality > self.randomised_agent_attribute
            ):
                self.type = 1
                self.model.model_state.learning_count += 1
                self.set_start_math()
                self.time_in_red_state = 0
                self.time_in_yellow_state = 0
                self.time_in_green_state += 1
                return 1

            if (
                self.model.pupil_params.hyper_impulsivity == 0
                and self.model.teacher_params.control
                > self.randomised_agent_attribute
                >= self.hyper_impulsive
            ):
                self.type = 1
                self.model.model_state.learning_count += 1
                self.set_start_math()
                self.time_in_red_state = 0
                self.time_in_yellow_state = 0
                self.time_in_green_state += 1
                return 1
            if (
                self.model.teacher_params.control > self.randomised_agent_attribute
                and self.type == 2
            ):
                self.type = 1
                self.model.model_state.learning_count += 1
                self.set_start_math()
                self.time_in_red_state = 0
                self.time_in_yellow_state = 0
                self.time_in_green_state += 1
                return 1
            return
        self.type = 1
        self.model.model_state.learning_count += 1
        self.set_start_math()
        self.time_in_red_state = 0
        self.time_in_yellow_state = 0
        self.time_in_green_state += 1
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
            self.model.model_state.disruptive_count += 1
            return
        if Pturn_yellow == colour:
            self.type = 2
            return
        if Pturn_green == colour:
            self.type = 1
            self.model.model_state.learning_count += 1
            self.set_start_math()
            return

    def changeState(self):

        # Change to attentive (green) teaching quality or control is high and state is passive for long
        if (
            (self.model.teacher_params.quality or self.model.teacher_params.control)
            > self.randomised_agent_attribute
            and self.time_in_yellow_state >= self.randomised_agent_attribute
        ):
            self.type = 1
            self.time_in_red_state = 0
            self.time_in_yellow_state = 0
            self.time_in_green_state += 1
            self.model.model_state.learning_count += 1
            self.set_start_math()
            return 1

        if (
            self.hyper_impulsive < self.randomised_agent_attribute
            and self.model.teacher_params.control <= self.randomised_agent_attribute
            and self.time_in_yellow_state > self.randomised_agent_attribute
        ):
            self.type = 1
            self.time_in_red_state = 0
            self.time_in_yellow_state = 0
            self.time_in_green_state += 1
            self.model.model_state.learning_count += 1
            self.set_start_math()

            return 1
        # Similar to above but red for long
        if (
            self.hyper_impulsive
            < self.randomised_agent_attribute
            < self.time_in_red_state
            and self.model.teacher_params.control <= self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if (
            self.inattentiveness
            < self.randomised_agent_attribute
            < self.time_in_red_state
            and self.model.teacher_params.quality <= self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if (
            self.inattentiveness < self.randomised_agent_attribute
            and self.model.teacher_params.quality <= self.randomised_agent_attribute
            and self.time_in_yellow_state > self.randomised_agent_attribute
        ):
            self.type = 1
            self.time_in_red_state = 0
            self.time_in_yellow_state = 0
            self.time_in_green_state += 1
            self.model.model_state.learning_count += 1
            # self.set_start_math()

            return 1

        if (
            self.inattentiveness > self.randomised_agent_attribute
            and self.model.teacher_params.quality > self.randomised_agent_attribute
            and self.time_in_red_state > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if (
            self.hyper_impulsive > self.randomised_agent_attribute - 1
            and self.model.teacher_params.control > self.randomised_agent_attribute - 1
            and self.time_in_red_state > 3
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if (
            self.model.teacher_params.control > self.randomised_agent_attribute
            and self.time_in_red_state > 2
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if (
            self.hyper_impulsive <= self.randomised_agent_attribute
            and self.model.teacher_params.quality <= self.randomised_agent_attribute
            and self.time_in_red_state > 2
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1
        if (
            self.hyper_impulsive <= self.randomised_agent_attribute - 1
            and self.model.teacher_params.control <= self.randomised_agent_attribute - 1
            and self.time_in_red_state > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1
        if (
            self.inattentiveness < self.randomised_agent_attribute
            and self.model.teacher_params.quality < self.randomised_agent_attribute
            and self.time_in_red_state > self.randomised_agent_attribute
        ):
            self.type = 2
            self.disruptive += 1
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        if (
            self.time_in_red_state > self.randomised_agent_attribute
            and (self.model.teacher_params.quality or self.model.teacher_params.control)
            >= self.randomised_agent_attribute
        ):
            self.type = 1
            if self.model.model_state.disruptive_count > 0:
                self.model.model_state.disruptive_count -= 1
            self.time_in_red_state = 0
            self.time_in_yellow_state = 0
            self.time_in_green_state += 1
            self.model.model_state.learning_count += 1
            self.set_start_math()
            return 1
        if self.time_in_green_state > self.model.pupil_params.attention_span:
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            if self.model.model_state.learning_count > 0:
                self.model.model_state.learning_count -= 1
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

        self.initial_disruptive_tend = compute_zscore(self.model, self.inattentiveness)

        if self.model.schedule.steps == 0:
            self.model.schedule.steps = 1

        self.disruptiveTend = (
            (self.disruptive / self.model.schedule.steps)
            - (self.countLearning / self.model.schedule.steps)
        ) + self.initial_disruptive_tend
