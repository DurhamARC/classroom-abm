import numpy as np
from scipy import stats
from statistics import stdev
import statistics
import math

from model.data_types import GridParamType, PupilLearningState


def get_num_disruptors(model):
    return len(
        [p for p in model.schedule.agents if p.learning_state == PupilLearningState.RED]
    )


def get_num_passive(model):
    return len(
        [
            p
            for p in model.schedule.agents
            if p.learning_state == PupilLearningState.YELLOW
        ]
    )


def get_num_learning(model):
    return len(
        [
            p
            for p in model.schedule.agents
            if p.learning_state == PupilLearningState.GREEN
        ]
    )


def get_pupil_data(model, student_id):
    for p in model.schedule.agents:
        if int(p.student_id) == student_id:
            return round(p.e_math, 2)


def compute_ave(model):
    return round(statistics.mean([agent.e_math for agent in model.schedule.agents]), 2)


def get_grid_size(n_agents, max_group_size):
    # Calculate squarest grid size that will fit the given number of agents in
    # the given number of groups
    if max_group_size > n_agents:
        max_group_size = n_agents

    n_groups = math.ceil(n_agents / max_group_size)
    n_full_groups = n_groups
    if n_groups * max_group_size != n_agents:
        # With very large groups the difference between n_groups * max_group_size
        # and n_agents can be more than the number of groups, so to get evenly-sized
        # groups we need to decrease the max group size.
        while n_groups * max_group_size - n_agents > n_groups:
            max_group_size -= 1
        n_full_groups = n_agents % n_groups

    n_group_rows = math.ceil(math.sqrt(n_groups))
    n_group_cols = math.ceil(n_groups / n_group_rows)
    group_width = math.ceil(math.sqrt(max_group_size))
    group_height = math.ceil(max_group_size / group_width)

    grid_width = n_group_cols * (group_width + 1) - 1
    grid_height = n_group_rows * (group_height + 1) - 1
    return GridParamType(
        width=grid_width,
        height=grid_height,
        n_groups=n_groups,
        n_full_groups=n_full_groups,
        max_group_size=max_group_size,
        n_group_cols=n_group_cols,
        n_group_rows=n_group_rows,
        group_width=group_width,
        group_height=group_height,
    )


def min_neighbour_count_to_modify_state(n_neighbours, default_threshold, group_size):
    # if 8 or more neighbours, state should change if 6 or more neighbours are
    # red/green
    if n_neighbours >= 8:
        return default_threshold

    # otherwise we use the same proportion but round down so e.g. only 1 in a
    # pair will change behaviour
    return max(1, math.floor(group_size * default_threshold / 8))


def get_start_state_weights(inattentiveness, hyper_impulsive):
    # Calculate weights for a pupil's starting state, based on their
    # inattentiveness and hyper_impulsive scores.
    # A high inattentiveness score gives a greater chance of being yellow than
    # green; a high hyper_impulsive score gives a greater chance of being red
    # than yellow
    # Returns an array of weights for [green, yellow, red] states
    green_weight = (6 - inattentiveness) / 10
    red_weight = hyper_impulsive / 10
    yellow_weight = 1 - green_weight - red_weight
    return [green_weight, yellow_weight, red_weight]
