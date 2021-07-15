import datetime
import math

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation

from .data_types import PupilLearningState
from .Pupil import Pupil
from .utils import (
    compute_ave,
    get_num_disruptors,
    get_num_learning,
    get_grid_size,
    get_truncated_normal_value,
)


class SimModel(Model):
    def __init__(
        self,
        all_data,
        model_initial_state,
        output_data_writer,
        model_params,
        class_id=None,
        **kwargs,
    ):
        self.data = all_data
        self.model_state = model_initial_state
        self.output_data_writer = output_data_writer
        self.class_id = class_id
        self.model_params = model_params
        self.write_file = False

        if "teacher_quality" in kwargs:
            self.model_params.teacher_quality_mean = kwargs["teacher_quality"]

        if "teacher_control" in kwargs:
            self.model_params.teacher_control_mean = kwargs["teacher_control"]

        if "class_id" in kwargs:
            self.class_id = kwargs["class_id"]
        elif not self.class_id:
            self.class_id = 489

        if "write_file" in kwargs:
            self.write_file = kwargs["write_file"]

        self.class_data = self.data.get_class_data(self.class_id)
        self.class_size = len(self.class_data)

        self.teacher_control = self.random.normalvariate(
            self.model_params.teacher_control_mean,
            self.model_params.teacher_control_sd,
        )
        self.teacher_quality = self.random.normalvariate(
            self.model_params.teacher_quality_mean,
            self.model_params.teacher_quality_sd,
        )

        self.schedule = RandomActivation(self)

        # Calculate steps per day and holidays
        self.home_learning_steps = 0
        # Calculate number of days from 1st September to 16th July inclusive
        self.start_date = datetime.date(2021, 9, 1)
        self.current_date = self.start_date
        self.end_date = datetime.date(2022, 7, 16)

        self.ticks_per_school_day = round(
            get_truncated_normal_value(
                self.model_params.maths_ticks_mean,
                self.model_params.maths_ticks_sd,
                10,
                300,
            )
        )

        self.holiday_week_numbers = self.calculate_holiday_weeks(
            self.start_date,
            self.end_date,
            self.model_params.number_of_holidays,
            self.model_params.weeks_per_holiday,
        )

        # Create grid with torus = False - in a real class students at either ends of classroom don't interact
        self.grid_params = get_grid_size(
            len(self.class_data), self.model_params.group_size
        )
        self.grid = SingleGrid(
            self.grid_params.width, self.grid_params.height, torus=False
        )

        sorted_pupils = []
        if self.model_params.group_by_ability:
            sorted_pupils = self.class_data.sort_values("Ability")
        else:
            sorted_pupils = self.class_data.sample(frac=1)

        # Set up agents
        pupil_counter = 0
        for i in range(self.grid_params.n_groups):
            group_size = self.model_params.group_size
            if i >= self.grid_params.n_full_groups:
                group_size -= 1

            group_pupils = sorted_pupils.iloc[
                pupil_counter : pupil_counter + group_size
            ]
            group_x = math.floor(i / self.grid_params.n_group_rows)
            group_y = i % self.grid_params.n_group_rows

            for j, row in enumerate(group_pupils.iterrows()):
                index, pupil_data = row

                # Work out position on grid
                x = (group_x * self.grid_params.group_width + group_x) + math.floor(
                    j / self.grid_params.group_height
                )
                y = (group_y * self.grid_params.group_height + group_y) + (
                    j % self.grid_params.group_height
                )

                # create agents from data
                agent = Pupil(
                    (x, y),
                    self,
                    pupil_data.student_id,
                    PupilLearningState.YELLOW,
                    pupil_data.Inattentiveness,
                    pupil_data.hyper_impulsive,
                    pupil_data.Deprivation,
                    pupil_data.start_maths,
                    pupil_data.Ability,
                    group_size,
                )
                # Place Agents on grid
                self.grid.position_agent(agent, x, y)
                self.schedule.add(agent)

            pupil_counter += group_size

        # Collecting data while running the model
        self.model_datacollector = DataCollector(
            model_reporters={
                "Learning Students": get_num_learning,
                "Disruptive Students": get_num_disruptors,
                "Average End Math": compute_ave,
            }
        )
        self.model_datacollector.collect(self)
        self.mean_maths = compute_ave(self)

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

    @staticmethod
    def calculate_holiday_weeks(
        start_date, end_date, number_of_holidays, weeks_per_holiday
    ):
        """Calculate which weeks should be holidays given the total number of
        days from start to end of the school year, and the number and length
        of holidays

        Returns an array of week numbers which are holidays
        """
        # Get start of first week of term
        # Go back to start of week
        start_week = start_date - datetime.timedelta(days=start_date.weekday())
        if start_date.weekday() >= 5:
            # start_date is weekend so go to following Monday
            start_week += datetime.timedelta(weeks=1)

        # Get difference from following week after end day
        total_weeks = math.ceil(
            (end_date + datetime.timedelta(days=1) - start_week).days / 7
        )

        n_terms = number_of_holidays + 1
        n_holiday_weeks = number_of_holidays * weeks_per_holiday
        n_school_weeks = total_weeks - n_holiday_weeks
        min_weeks_per_term = math.floor(n_school_weeks / n_terms)
        remainder_weeks = n_school_weeks % n_terms

        weeks_per_term = []
        for i in range(n_terms):
            term_weeks = min_weeks_per_term
            if i < remainder_weeks:
                term_weeks += 1
            weeks_per_term.append(term_weeks)

        holiday_week_numbers = []
        current_week = 0
        for term_weeks in weeks_per_term[:-1]:
            start_week = current_week + term_weeks
            holiday_week_numbers.extend(
                list(range(start_week, start_week + weeks_per_holiday))
            )
            current_week += term_weeks + weeks_per_holiday
        return holiday_week_numbers

    def update_school_time(self):
        time_in_day = self.schedule.steps % self.ticks_per_school_day

        if time_in_day == self.ticks_per_school_day - 1:
            # Last tick of school day, so add home learning time
            home_learning_days = 1

            # If it's Friday add 2 more days' home learning for the weekend
            if self.current_date.weekday() == 4:
                home_learning_days += 2

                # Is it a holiday?
                week_number = math.floor((self.current_date - self.start_date).days / 7)
                if week_number in self.holiday_week_numbers:
                    # Add holiday weeks
                    home_learning_days += 7 * self.model_params.weeks_per_holiday

            self.home_learning_steps = (
                home_learning_days * self.model_params.ticks_per_home_day
            )

            # Update current date
            self.current_date += datetime.timedelta(days=home_learning_days)
        else:
            self.home_learning_steps = 0

            if time_in_day == 0 and self.current_date.weekday() == 0:
                # First tick of the week so reset all pupils to Yellow
                for pupil in self.schedule.agents:
                    pupil.learning_state = PupilLearningState.YELLOW

    def step(self):
        # Reset counter of learning and disruptive agents
        self.model_state.learning_count = 0
        self.model_state.disruptive_count = 0

        # Advance the model by one step
        self.schedule.step()

        self.update_school_time()

        # collect data
        self.model_datacollector.collect(self)
        self.mean_maths = compute_ave(self)

        if self.current_date > self.end_date or self.running == False:
            self.running = False
            self.agent_datacollector.collect(self)
            agent_data = self.agent_datacollector.get_agent_vars_dataframe()
            self.output_data_writer.write_data(
                agent_data, self.class_id, self.class_size
            )
