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


def get_num_learning(model):
    return len(
        [
            p
            for p in model.schedule.agents
            if p.learning_state == PupilLearningState.GREEN
        ]
    )


def compute_ave(model):
    return statistics.mean([agent.e_math for agent in model.schedule.agents])


def get_grid_size(n_agents, max_group_size):
    # Calculate squarest grid size that will fit the given number of agents in
    # the given number of groups
    if max_group_size > n_agents:
        max_group_size = n_agents

    n_groups = math.ceil(n_agents / max_group_size)
    n_full_groups = n_groups
    if n_groups * max_group_size != n_agents:
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
        n_group_cols=n_group_cols,
        n_group_rows=n_group_rows,
        group_width=group_width,
        group_height=group_height,
    )


def min_neighbour_count_to_modify_state(n_neighbours, group_size):
    # if 8 or more neighbours, state should change if 6 or more neighbours are
    # red/green
    if n_neighbours >= 8:
        return 6

    # otherwise we use the same proportion but round down so e.g. only 1 in a
    # pair will change behaviour
    return math.floor(group_size * 6 / 8)


def get_truncated_normal_value(mean, sd, lower, upper):
    # Return a random number using a truncated normal distribution with the
    # given mean  and standard deviation, and capped by the given lower and
    # upper limits
    generator = stats.truncnorm(
        (lower - mean) / sd, (upper - mean) / sd, loc=mean, scale=sd
    )
    return generator.rvs(1)[0]
