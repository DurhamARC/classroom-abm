import statistics

from mesa import Agent

from .data_types import PupilLearningState


class Pupil(Agent):
    # 1 Initialization
    def __init__(
        self,
        pos,
        model,
        student_id,
        learning_state,
        inattentiveness,
        hyper_impulsive,
        deprivation,
        math,
        ability,
    ):
        super().__init__(pos, model)
        self.pos = pos
        self.student_id = student_id
        self.learning_state = learning_state
        self.inattentiveness = inattentiveness
        self.hyper_impulsive = hyper_impulsive
        self.deprivation = deprivation
        self.ability = ability
        self.s_math = math
        self.e_math = math
        self.randomised_agent_attribute = 0

    def getNeighbourCount(self):
        neighbourCount = 0
        red = 0
        green = 0
        yellow = 0
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            neighbourCount += 1
            if neighbor.learning_state == PupilLearningState.RED:
                red += 1
            elif neighbor.learning_state == PupilLearningState.YELLOW:
                yellow += 1
            else:
                green += 1

        return neighbourCount, red, yellow, green

    # define the step function
    def step(self):
        self.randomised_agent_attribute = (
            self.random.randint(0, self.model.model_params.random_select) + 1
        )

        # Change the state
        self.changeState()

        # Update the end maths score
        self.learn()

    def changeState(self):
        total_count, red_count, yellow_count, green_count = self.getNeighbourCount()

        if self.learning_state == PupilLearningState.GREEN:
            # if state is green change to yellow if:
            # 3 neighbours or more are red
            # at random but more likely if the teaching quality is low
            if (
                red_count > 2
                or self.randomised_agent_attribute > self.model.teacher_params.quality
            ):
                self.learning_state = PupilLearningState.YELLOW

        elif self.learning_state == PupilLearningState.YELLOW:
            # change to disruptive (red) at random if already passive (yellow)
            # more likely if control is low or hyper-impulsive is high
            if (
                self.randomised_agent_attribute > self.model.teacher_params.control
                or self.randomised_agent_attribute < self.hyper_impulsive
            ):
                self.learning_state = PupilLearningState.RED
            # start teaching and passive students switch to learning mode (green)
            # if teaching is good or they are not too inattentive
            elif (
                self.randomised_agent_attribute < self.model.teacher_params.quality
                or self.randomised_agent_attribute > self.inattentiveness
            ):
                self.learning_state = PupilLearningState.GREEN
            # if patch is yellow change to red if 6 neighbours or more are red
            elif red_count > 5:
                self.learning_state = PupilLearningState.RED
            # if patch is yellow change to green if 6 neighbours or more are red
            elif green_count > 5:
                self.learning_state = PupilLearningState.GREEN

        elif self.learning_state == PupilLearningState.RED:
            # change from disruptive to passive if:
            # - control is good at random
            # - 3 or more neighbours are green
            if (
                green_count > 2
                or self.randomised_agent_attribute < self.model.teacher_params.control
            ):
                self.learning_state = PupilLearningState.YELLOW

    """
    Calculate the end maths score
    """

    def learn(self):
        params = self.model.model_params

        if self.model.is_school_time:
            if self.learning_state == PupilLearningState.GREEN:
                ability_increment = (
                    1 - params.school_learn_random_proportion
                ) * self.random.normalvariate(
                    (5 + self.ability) / params.school_learn_mean_divisor,
                    params.school_learn_sd,
                )
                random_increment = (
                    params.school_learn_random_proportion
                    * self.random.normalvariate(
                        (0.5 * 5) / params.school_learn_mean_divisor,
                        params.school_learn_sd,
                    )
                )
                self.e_math += params.school_learn_factor * (
                    ability_increment + random_increment
                )
        else:
            # by getting older maths changes
            self.e_math += (
                params.home_learn_factor
                * ((6 - self.deprivation) / 3) ** 0.01
                * (
                    self.random.normalvariate((5 + self.ability) / 2000, 0.08)
                    + self.random.normalvariate((5 / 2000), 0.08)
                )
            )

            # ditto to adjustment
            # add deprivation to a power to reduce its spread
            # NB the last two rows of code have been adjusted by extensive trial
            # and error on one class to give suitable growth overall and correlations between variables
            # by getting older ability changes
            # degrade the start_maths measure by a random amount on each tock
            # FIXME: should this be done at every step rather than just in home learning?
            self.e_math += 0.08 * (
                self.random.random() - 0.5
            )  # this did not work alone so now in combination with conformity
            # try reducing the extremes - pull everyone back to the middle
            mean_maths = statistics.mean(
                [agent.e_math for agent in self.model.schedule.agents]
            )
            self.e_math = mean_maths + 0.999993 * (self.e_math - mean_maths)

    def get_learning_state(self):
        return self.learning_state
