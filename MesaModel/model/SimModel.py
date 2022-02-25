import dataclasses
import datetime
import logging
import math

import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation

from .data_types import PupilLearningState, ModelParamType
from .Pupil import Pupil
from .teacher_variable import TeacherVariable
from .truncated_normal_generator import TruncatedNormalGenerator
from .utils import (
    compute_ave,
    get_date_for_chart,
    get_num_disruptors,
    get_num_passive,
    get_num_learning,
    get_grid_size,
    get_pupil_data,
)

logger = logging.getLogger(__name__)


class SimModel(Model):
    def __init__(
        self,
        all_data,
        model_initial_state,
        output_data_writer,
        model_params,
        class_id_and_rng=None,
        class_id=None,
        speedup=1,
        **kwargs,
    ):
        self.data = all_data
        self.model_state = model_initial_state
        self.output_data_writer = output_data_writer

        if class_id_and_rng:
            (self.class_id, self.rng) = class_id_and_rng
        else:
            self.rng = np.random.default_rng()
            if class_id:
                self.class_id = class_id

        logger.info("Modelling class %s", self.class_id)

        self.model_params = model_params
        self.speedup = speedup
        self.write_file = False

        # Update any parameters passed as kwargs
        param_dict = dataclasses.asdict(self.model_params)
        update_params = False
        for kw in kwargs:
            if kw in param_dict:
                param_dict[kw] = kwargs[kw]
                update_params = True

        if update_params:
            self.model_params = ModelParamType(**param_dict)

        if "class_id" in kwargs:
            self.class_id = kwargs["class_id"]
        elif not self.class_id:
            self.class_id = 489

        if "write_file" in kwargs:
            self.write_file = kwargs["write_file"]

        # Get summary data to display to users
        self.class_summary_data = None
        if "summary_data" in kwargs and kwargs["summary_data"] is not None:
            summary_df = kwargs["summary_data"]
            class_summary_data = summary_df[summary_df["class_id"] == self.class_id]
            if not class_summary_data.empty:
                self.class_summary_data = class_summary_data

        self.class_data = self.data.get_class_data(self.class_id)
        self.class_size = len(self.class_data)

        self.schedule = RandomActivation(self)

        # Calculate steps per day and holidays
        self.home_learning_steps = 0
        # Calculate number of days from 1st September to 16th July inclusive
        self.start_date = datetime.date(2021, 9, 1)
        self.current_date = self.start_date
        self.end_date = datetime.date(2022, 7, 16)
        self.total_days = (self.end_date - self.start_date).days

        self.ticks_per_school_day = round(
            TruncatedNormalGenerator.get_single_value(
                self.model_params.maths_ticks_mean,
                self.model_params.maths_ticks_sd,
                10,
                600,
            )
        )
        self.ticks_per_home_day = self.model_params.ticks_per_home_day

        self.set_speedup()
        logger.debug("%s ticks per school day", self.ticks_per_school_day)

        self.holiday_week_numbers = self.calculate_holiday_weeks(
            self.start_date,
            self.end_date,
            self.model_params.number_of_holidays,
            self.model_params.weeks_per_holiday,
        )

        # Create truncnorm generators for school and home learning random
        # increments
        # Use batch sizes as total days * class_size * ticks per day
        # (overestimate to ensure we only generate values once)
        batch_multiplier = self.total_days * self.class_size
        self.school_learning_random_gen = TruncatedNormalGenerator(
            5 / self.model_params.school_learn_mean_divisor,
            self.model_params.school_learn_sd,
            lower=0,
            batch_size=self.ticks_per_school_day * batch_multiplier,
        )
        self.home_learning_random_gen = TruncatedNormalGenerator(
            5 / 2000,
            0.08,
            lower=0,
            batch_size=self.ticks_per_home_day * batch_multiplier,
        )

        # Create TeacherVariable instances for quality and control
        self.teacher_control_variable = TeacherVariable(
            self.model_params.teacher_control_mean,
            self.model_params.teacher_control_sd,
            self.model_params.teacher_control_variation_sd,
            self.rng,
            self.total_days,
        )
        self.teacher_quality_variable = TeacherVariable(
            self.model_params.teacher_quality_mean,
            self.model_params.teacher_quality_sd,
            self.model_params.teacher_quality_variation_sd,
            self.rng,
            self.total_days,
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
            group_size = self.grid_params.max_group_size
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
        self.pupil_state_datacollector = DataCollector(
            model_reporters={
                "Learning Students": get_num_learning,
                "Passive Students": get_num_passive,
                "Disruptive Students": get_num_disruptors,
            }
        )
        self.pupil_state_datacollector.collect(self)
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

        # Monitor mean maths score
        self.maths_datacollector = DataCollector(
            {
                "Date": get_date_for_chart,
                "Mean Score": compute_ave,
            }
        )
        self.maths_datacollector.collect(self)
        self.running = True

    def set_speedup(self):
        if self.speedup > 1:
            min_ticks = min(self.ticks_per_school_day, self.ticks_per_home_day)
            # Can't have fewer than 1 tick per school day so reduce the speedup accordingly
            if self.speedup > min_ticks:
                self.speedup = min_ticks
            # Speedup should be divisible by self.ticks_per_school_day
            # e.g. if 10 ticks per day
            # Can't have speedup more than 10 as we need 1 tick per days
            # If speedup is 5 then we have 2 ticks per day
            # If speedup is 8 then we would have 10/8 = 1.25 ticks per day
            # Round that to 1, then speedup would be 10 (=10/1) not 8
            # If speedup is 6 then we would have 10/6 = 1.67 ticks per day
            # Round that to 2, then speedup would be 5 (=10/2) not 6
            speedup_ticks_per_school_day = round(
                self.ticks_per_school_day / self.speedup
            )
            self.speedup = self.ticks_per_school_day / speedup_ticks_per_school_day
            self.ticks_per_school_day = speedup_ticks_per_school_day

            speedup_ticks_per_home_day = round(self.ticks_per_home_day / self.speedup)
            self.home_speedup = self.ticks_per_home_day / speedup_ticks_per_home_day
            self.ticks_per_home_day = speedup_ticks_per_school_day
        else:
            self.home_speedup = 1

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
        if (
            time_in_day == self.ticks_per_school_day - 1
            or self.ticks_per_school_day == 1
        ):
            # Have just finished the penultimate tick of school day, so add
            # home learning time ready for the next tick
            self.home_learning_days = 1

            # If it's Friday add 2 more days' home learning for the weekend
            if self.current_date.weekday() == 4:
                self.home_learning_days += 2

                # Is it a holiday?
                week_number = math.floor((self.current_date - self.start_date).days / 7)
                if week_number in self.holiday_week_numbers:
                    # Add holiday weeks
                    self.home_learning_days += 7 * self.model_params.weeks_per_holiday

            self.home_learning_steps = self.home_learning_days * self.ticks_per_home_day

        else:
            self.home_learning_steps = 0

        if time_in_day == 0:
            # Update current date by self.home_learning days now we've completed the last tick of the day
            self.current_date += datetime.timedelta(days=self.home_learning_days)
            self.home_learning_days = 0

            # Update teacher control/teacher_quality
            self.teacher_control_variable.update_current_value()
            self.teacher_quality_variable.update_current_value()

            # Reset all pupils's states ready for the next day
            for pupil in self.schedule.agents:
                pupil.resetState()

    def step(self):
        # Reset counter of learning and disruptive agents
        self.model_state.learning_count = 0
        self.model_state.disruptive_count = 0

        # Advance the model by one step
        self.schedule.step()

        self.update_school_time()

        # collect data
        self.maths_datacollector.collect(self)
        self.pupil_state_datacollector.collect(self)
        self.mean_maths = compute_ave(self)

        if self.current_date > self.end_date or self.running == False:
            logger.debug("Finished run; collecting data")
            self.running = False

            # Remove tngs
            self.school_learning_random_gen = None
            self.home_learning_random_gen = None
            for pupil in self.schedule.agents:
                pupil.school_learning_ability_random_gen = None
                pupil.home_learning_ability_random_gen = None

            self.agent_datacollector.collect(self)
            agent_data = self.agent_datacollector.get_agent_vars_dataframe()
            logger.debug("Got agent data")
            self.output_data_writer.write_data(
                agent_data, self.class_id, self.class_size
            )
            logger.debug("Written to output file")
            self.agent_datacollector = None
            self.maths_datacollector = None
            self.pupil_state_datacollector = None
            self.home_learning_random_gen = None
            self.school_learning_random_gen = None
            logger.info("Completed run for class %s", self.class_id)
