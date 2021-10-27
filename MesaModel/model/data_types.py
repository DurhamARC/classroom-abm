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

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            try:
                setattr(self, field.name, field.type(value))
            except ValueError as e:
                raise ValueError(
                    f"Could not cast {repr(value)} value for {field.name} to be {field.type}",
                    e,
                )


# Default set of model parameters. Note: variable parameters must be added before
# static parameters!
DEFAULT_MODEL_PARAMS = ModelParamType(
    teacher_quality_mean=2,
    teacher_quality_sd=1.26,
    teacher_control_mean=2,
    teacher_control_sd=1.08,
    random_select=6,
    school_learn_factor=0.12,
    home_learn_factor=0.0043,
    school_learn_mean_divisor=800,
    school_learn_sd=0.04,
    school_learn_random_proportion=0.2,
    conformity_factor=0.999993,
    degradation_factor=0.08,
    maths_ticks_mean=150.0,
    maths_ticks_sd=50.0,
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
