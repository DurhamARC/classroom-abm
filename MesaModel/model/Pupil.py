from mesa import Agent

from .data_types import PupilLearningState
from .truncated_normal_generator import TruncatedNormalGenerator
from .utils import min_neighbour_count_to_modify_state


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
        group_size,
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

        neighbour_count = self.getNeighbourCount()[0]
        self.yellow_state_change_threshold = min_neighbour_count_to_modify_state(
            neighbour_count, 6, group_size
        )
        self.red_green_state_change_threshold = min_neighbour_count_to_modify_state(
            neighbour_count, 2, group_size
        )

        # Create truncnorm generators for learning increments based on pupil's ability
        self.school_learning_ability_random_gen = TruncatedNormalGenerator(
            (5 + self.ability) / self.model.model_params.school_learn_mean_divisor,
            self.model.model_params.school_learn_sd,
            lower=0,
            batch_size=self.model.total_days * self.model.ticks_per_school_day,
        )
        self.home_learning_ability_random_gen = TruncatedNormalGenerator(
            (5 + self.ability) / 2000,
            0.08,
            lower=0,
            batch_size=self.model.total_days
            * self.model.model_params.ticks_per_home_day,
        )

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
        # Generate a random number between 1 and random_select
        self.randomised_agent_attribute = (
            self.model.model_params.random_select * self.model.rng.random() + 1
        )

        # Change the state
        self.changeState()

        # Update the end maths score
        self.learn_in_school()

        for i in range(self.model.home_learning_steps):
            self.learn_at_home()

    def changeState(self):
        total_count, red_count, yellow_count, green_count = self.getNeighbourCount()

        if self.learning_state == PupilLearningState.GREEN:
            # if state is green change to yellow if:
            # 3 neighbours or more are red
            # at random but more likely if the teaching quality is low
            if (
                red_count > self.red_green_state_change_threshold
                and self.randomised_agent_attribute > self.model.teacher_quality
            ):
                self.learning_state = PupilLearningState.YELLOW

        elif self.learning_state == PupilLearningState.YELLOW:
            # change to disruptive (red) at random if already passive (yellow)
            # more likely if control is low and hyper-impulsive is high
            if (
                self.randomised_agent_attribute > self.model.teacher_control
                and self.randomised_agent_attribute < self.hyper_impulsive
            ):
                self.learning_state = PupilLearningState.RED
            # start teaching and passive students switch to learning mode (green)
            # if teaching is good and they are not too inattentive
            elif (
                self.randomised_agent_attribute < self.model.teacher_quality
                and self.randomised_agent_attribute > self.inattentiveness
            ):
                self.learning_state = PupilLearningState.GREEN
            # if patch is yellow change to red if min_neighbour_count_to_modify_state
            # (e.g. 6) neighbours or more are red
            elif red_count >= self.yellow_state_change_threshold:
                self.learning_state = PupilLearningState.RED
            # if patch is yellow change to green if min_neighbour_count_to_modify_state
            # (e.g. 6) neighbours or more are green
            elif green_count >= self.yellow_state_change_threshold:
                self.learning_state = PupilLearningState.GREEN

        elif self.learning_state == PupilLearningState.RED:
            # change from disruptive to passive if:
            # - control is good at random
            # - 3 or more neighbours are green
            if (
                green_count > self.red_green_state_change_threshold
                and self.randomised_agent_attribute < self.model.teacher_control
            ):
                self.learning_state = PupilLearningState.YELLOW

    """
    Calculate the end maths score
    """

    def learn_in_school(self):
        params = self.model.model_params

        if self.learning_state == PupilLearningState.GREEN:
            # Calculate proportion of increment that is due to cognitive
            # ability
            # (1 - params.school_learn_random_proportion) gives the
            # proportion which is due to ability as opposed to a
            # random increment.
            # Use a normal distribution which has a mean equal to
            # the ability plus 5 (to avoid it being negative, as the ability
            # values are in range [-2.5, 4.3]
            ability_increment = (
                1 - params.school_learn_random_proportion
            ) * self.school_learning_ability_random_gen.get_value()

            # This is the amount of learning as a random increment to go
            # alongside the amount related to ability. It follows the same
            # process as ability_increment but replaces ability with a constant 5
            # (unmodified by ability)
            random_increment = (
                params.school_learn_random_proportion
                * self.model.school_learning_random_gen.get_value()
            )
            self.e_math += params.school_learn_factor * (
                ability_increment + random_increment
            )

        # degrade the start_maths measure by a random amount on each tock
        self.e_math += params.degradation_factor * (
            self.random.random() - 0.5
        )  # this did not work alone so now in combination with conformity
        # try reducing the extremes - pull everyone back to the middle
        self.e_math = self.model.mean_maths + params.conformity_factor * (
            self.e_math - self.model.mean_maths
        )

    def learn_at_home(self):
        params = self.model.model_params

        self.e_math += (
            params.home_learn_factor
            * ((6 - self.deprivation) / 3) ** 0.01
            * (
                self.home_learning_ability_random_gen.get_value()
                + self.model.home_learning_random_gen.get_value()
            )
        )

    def get_learning_state(self):
        return self.learning_state
