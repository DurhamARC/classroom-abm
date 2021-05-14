import numpy as np
from statistics import stdev
import statistics
import math

from model.data_types import GridParamType


def get_num_disruptors(model):
    return model.model_state.disruptive_count


def get_num_learning(model):
    return model.model_state.learning_count


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
    agent_inattentiveness = [agent.inattentiveness for agent in model.schedule.agents]
    print("Calculate variance", agent_inattentiveness)
    SD = stdev(agent_inattentiveness)
    mean = statistics.mean(agent_inattentiveness)
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


def get_grid_size(n_agents):
    # Calculate squarest grid size that will fit the given number of agents
    grid_width = math.ceil(math.sqrt(n_agents))
    grid_height = math.ceil(n_agents / grid_width)
    return GridParamType(grid_width, grid_height)
