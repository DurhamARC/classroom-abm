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
        self.count_learning = 0
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

        # If more than 5 neighbours are disruptive and pupil is passive,
        # pupil will also become disruptive
        if red > 5 and self.type == 2:
            self.type = 3
            self.model.model_state.disruptive_count += 1
            self.disruptive += 1
            self.time_in_red_state += 1
            self.time_in_yellow_state = 0
            self.time_in_green_state = 0
            return 1

        # If more neighbours are disruptive than a randomly generated
        # number and the pupil is more disruptive than the mean
        # disruptive tendency of all pupils, pupil will become passive
        if (
            red > self.randomised_agent_attribute + 1
            and self.disruptiveTend > compute_ave_disruptive(self.model)
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        # If the pupil cohort is inattentive and the teacher cohort is of
        # a lower quality than a random number and the pupil's inattentiveness
        # is greater than a random number, pupil will become disruptive
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

        # If the pupil cohort is inattentive and the teacher cohort has less control
        # of the class than a random number and the pupil's inattentiveness exceeds
        # a random number, then the pupil will become disruptive
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

        # If the pupil cohort is hyperactive-impulsive and the teacher cohort has less
        # control than a random number and the pupil's hyperactive-impulsive nature is
        # greater than a random number, then the pupil will become disruptive
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

        # If the pupil cohort is inattentive and the teacher cohort is of
        # a lower quality than a random number and the pupil's inattentiveness
        # is lower than a random number, then the pupil will become passive
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

        # If the pupil cohort is not inattentive and the pupil's inattentiveness
        # is greater than a random number, pupil will become passive
        if (
            self.model.pupil_params.inattentiveness == 0
            and self.inattentiveness > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        # If a function on the relationship between the pupil cohort's disruptiveness and
        # the pupil's own disruptiveness is greater than 1 and the teacher cohort's
        # control is greater than a random number and the pupil's hyperactive-impulsiveness
        # is less than a random number, then pupil will become passive
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

        # If the teacher cohort's quality is greater than a random number and the pupil
        # is more inattentive than a random number, the pupil will become passive
        if (
            self.model.teacher_params.quality > self.randomised_agent_attribute
            and self.inattentiveness > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        # If the teacher cohort's control is less than a random number and pupil is
        # currently learning, then pupil will become passive
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

        # If the teacher cohort's control is greater than a random number and
        # the pupil's hyperactive-impulsivenesss is greater than a random number,
        # then pupil will become passive
        if (
            self.model.teacher_params.control > self.randomised_agent_attribute
            and self.hyper_impulsive > self.randomised_agent_attribute
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        # If pupil is surrounded by 3 disruptive pupil's and it is currently learning,
        # pupil will move to a passive state.
        if red > 3 and self.type == 1:
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            if self.model.model_state.learning_count > 0:
                self.model.model_state.learning_count -= 1
            return 1

    @property
    def greenStateChange(self):

        count, red, yellow, green = self.neighbour()

        # If more than 5 of the pupil's neighbours are learning and pupil is passive,
        # then pupil will be in a learning state.
        if green > 5 and self.type == 2:
            self.type = 1
            self.model.model_state.learning_count += 1
            self.set_end_math()
            self.time_in_red_state = 0
            self.time_in_yellow_state = 0
            self.time_in_green_state += 1
            return 1

        # If the pupil's cohort are not inattentive or the quality of the teacher
        # cohort is less than a random number or the pupil's inattentiveness is
        # greater than a random number, then the following conditions are considered:
        if (
            self.model.pupil_params.inattentiveness != 0
            or self.model.teacher_params.quality <= self.randomised_agent_attribute
            or self.inattentiveness >= self.randomised_agent_attribute
        ):
            # If the pupil's cohort is inattentive and the teacher cohort's quality is
            # greater than a random number, then the pupil will be in a learning state.
            if (
                self.model.pupil_params.inattentiveness == 0
                and self.model.teacher_params.quality > self.randomised_agent_attribute
            ):
                self.type = 1
                self.model.model_state.learning_count += 1
                self.set_end_math()
                self.time_in_red_state = 0
                self.time_in_yellow_state = 0
                self.time_in_green_state += 1
                return 1
            # If the pupil cohort is not hyperactive-impulsive and the teacher cohort's
            # level of control is greater than a random number which is greater than the
            # pupil's hyperactive-intensiveness, then the pupil will be in a learning state
            if (
                self.model.pupil_params.hyper_impulsivity == 0
                and self.model.teacher_params.control
                > self.randomised_agent_attribute
                >= self.hyper_impulsive
            ):
                self.type = 1
                self.model.model_state.learning_count += 1
                self.set_end_math()
                self.time_in_red_state = 0
                self.time_in_yellow_state = 0
                self.time_in_green_state += 1
                return 1
            # If the teacher cohort's control is greater than a random number
            # and the student is currently passive, then the student will enter
            # a learning state
            if (
                self.model.teacher_params.control > self.randomised_agent_attribute
                and self.type == 2
            ):
                self.type = 1
                self.model.model_state.learning_count += 1
                self.set_end_math()
                self.time_in_red_state = 0
                self.time_in_yellow_state = 0
                self.time_in_green_state += 1
                return 1
            return
        self.type = 1
        self.model.model_state.learning_count += 1
        self.set_end_math()
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
            self.set_end_math()
            return

    def changeState(self):

        # If the teacher cohort or teacher cohort control is greater than a random number
        # and the time spent by the pupil in a passive state is greater than a random
        # number, pupil will enter a learning state
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
            self.set_end_math()
            return 1

        # If the pupil's hyperactive-impulsiveness is less than a random number and
        # the teacher cohort's level of control is less than a random number and
        # the pupil's time in a passive state is greater than a random number
        # then the pupil will enter a learning state
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
            self.set_end_math()

            return 1
        # If the pupil's hyperactive-impulsive nature is less than a random number which
        # is less than the time the pupil has spent in a disruptive state and the teacher
        # cohort's control is less than a random number, the pupil will enter a passive
        # state
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

        # If the pupil's inattentiveness is lower than a random number which is less
        # than the time the pupil has spent in a red state and, further to that,
        # the teacher cohort's quality is lower than a random number the pupil will
        # be in a passive state
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

        # If the pupil's inattentiveness is less than a random number and the teacher cohort
        # has a lower quality than a random number and the pupil's time in a passive state is
        # greater than a random number then the pupil will be in a learning state
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

        # If the pupil's inattentiveness is greater than a random number and the teacher
        # cohort's quality is greater than a random number and the pupil's time in a
        # disruptive state is greater than a random number the pupil will be in a
        # passive state
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

        # If the pupil's hyperactive-impulsiveness is greater than a random number
        # and the teacher cohort's level of control is greater than a random number
        # and the pupil has been disruptive for more than three steps, then the
        # pupil will be passive
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

        # If the teacher cohort's level of control is greater than a random number
        # and the pupil has been in a disruptive state for more than two steps,
        # then the pupil will be passive
        if (
            self.model.teacher_params.control > self.randomised_agent_attribute
            and self.time_in_red_state > 2
        ):
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            return 1

        # If the pupil's hyperactive-impulsiveness is less than a random number
        # and the teacher cohort's quality is less than a random number and
        # the pupil has been in a disruptive state for more than two steps,
        # then the pupil will be in a passive state
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

        # If the pupil's hyperactive-impulsiveness is less than a random number
        # and the teacher cohort's level of control is less than a random number
        # and the pupil's time in a disruptive state is greater than a random
        # number then the pupil will enter a passive state
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

        # If the pupil's inattentiveness is less than a random number and the
        # teacher cohort's quality is less than a random number and the pupil's
        # time in a disruptive state is greater than a random number, then pupil will
        # enter a passive state
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

        # If the pupil's time in a disruptive state is greater than a random number
        # and the teacher cohort's quality or control is greater than a random number
        # then the pupil will enter a learning state
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
            self.set_end_math()
            return 1

        # If the pupil's time in a learning state is greater than the pupil cohort's
        # attention span, then the pupil will be in a passive state
        if self.time_in_green_state > self.model.pupil_params.attention_span:
            self.type = 2
            self.time_in_red_state = 0
            self.time_in_yellow_state += 1
            self.time_in_green_state = 0
            if self.model.model_state.learning_count > 0:
                self.model.model_state.learning_count -= 1
            return 1

    # Calculate the end maths score based on the time spent by a pupil in
    # a learning state and the pupil's starting maths score
    def set_end_math(self):
        # Increment the learning counter
        self.count_learning += 1

        scaled_s_math = (2.718281828 ** self.s_math) ** (1 / 7.621204857)
        total_learn = self.count_learning + scaled_s_math
        self.e_math = (7.621204857 * math.log(total_learn)) + self.ability

    def get_type(self):
        return self.type

    # Compute the pupil's disruptive tendency
    def set_disruptive_tend(self):

        self.initial_disruptive_tend = compute_zscore(self.model, self.inattentiveness)

        if self.model.schedule.steps == 0:
            self.model.schedule.steps = 1

        self.disruptiveTend = (
            (self.disruptive / self.model.schedule.steps)
            - (self.count_learning / self.model.schedule.steps)
        ) + self.initial_disruptive_tend
