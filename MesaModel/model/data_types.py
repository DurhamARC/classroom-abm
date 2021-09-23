"""
Global data types. These serve as containers for model parameters.
"""
import dataclasses
from dataclasses import dataclass
from enum import Enum


@dataclass(unsafe_hash=True)
class GridParamType:
    width: int
    height: int
    n_groups: int
    n_full_groups: int
    n_group_cols: int
    n_group_rows: int
    group_width: int
    group_height: int


@dataclass(unsafe_hash=True)
class ModelParamType:
    # For parameterisation
    teacher_quality_mean: float
    teacher_quality_sd: float
    teacher_control_mean: float
    teacher_control_sd: float
    random_select: float
    school_learn_factor: float
    home_learn_factor: float
    school_learn_mean_divisor: float
    school_learn_sd: float
    school_learn_random_proportion: float
    conformity_factor: float
    degradation_factor: float
    maths_ticks_mean: float
    maths_ticks_sd: float

    # For test purposes
    ticks_per_home_day: int

    # For user manipulation
    number_of_holidays: int
    weeks_per_holiday: int
    group_size: int
    group_by_ability: bool


# Default set of model parameters. Note: variable parameters must be added before
# static parameters!
DEFAULT_MODEL_PARAMS = ModelParamType(
    teacher_quality_mean=3.8767199999999997,
    teacher_quality_sd=0.09516000000000001,
    teacher_control_mean=2.95547,
    teacher_control_sd=0.30268,
    random_select=1.03267,
    school_learn_factor=0.02758,
    home_learn_factor=0.0006981,
    school_learn_mean_divisor=1011.05076,
    school_learn_sd=0.00675,
    school_learn_random_proportion=0.30291999999999997,
    conformity_factor=0.999992344,
    degradation_factor=0.08909,
    maths_ticks_mean=288.0,
    maths_ticks_sd=2.5622700000000003,
    ticks_per_home_day=330,
    number_of_holidays=2,
    weeks_per_holiday=2,
    group_size=5,
    group_by_ability=True,
)

# The last STATIC_PARAM_COUNT parameters in ModelParamType
# should not be modified when parameterising, but may be modified
# by web app users later on
STATIC_PARAM_COUNT = 5
STATIC_PARAMS = dataclasses.astuple(DEFAULT_MODEL_PARAMS)[-STATIC_PARAM_COUNT:]
VARIABLE_PARAM_NAMES = [
    field.name
    for field in dataclasses.fields(DEFAULT_MODEL_PARAMS)[0:-STATIC_PARAM_COUNT]
]


@dataclass(unsafe_hash=True)
class ModelState:
    learning_count: int
    disruptive_count: int
    red_state_count: int
    yellow_state_count: int
    green_state_count: int


class PupilLearningState(Enum):
    GREEN = 1
    YELLOW = 2
    RED = 3
