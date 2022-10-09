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
    max_group_size: int
    n_group_cols: int
    n_group_rows: int
    group_width: int
    group_height: int


@dataclass(unsafe_hash=True)
class ModelParamType:
    # For parameterisation (with ranges as comments)
    teacher_quality_mean: float  # [0, 5]
    teacher_quality_sd: float  # (0, *)
    teacher_quality_variation_sd: float  # (0, *)
    teacher_quality_convergence_rate: float  # (0, 1)

    # a random feedback factor for variation of the teacher quality variable
    teacher_quality_feedback_factor: float  # (0, 1)

    teacher_control_mean: float  # [0, 5]
    teacher_control_sd: float  # (0, *)
    teacher_control_variation_sd: float  # (0, *)
    teacher_control_convergence_rate: float  # (0, 1)

    random_select: float  # [0, 5]
    school_learn_factor: float  # (0, *)
    home_learn_factor: float  # (0, *)
    school_learn_mean_divisor: float  # (0, *)
    school_learn_sd: float  # (0, *)
    school_learn_random_proportion: float  # (0, 1)
    conformity_factor: float  # (0, 1)
    degradation_factor: float  # (0, 1)

    # maths_ticks reflects actual minute per day spent in school on Maths
    maths_ticks_mean: float  # [170, 660]
    maths_ticks_sd: float  # (0, *)

    # Note: For tuning of teacher variables (quality and control, separately),
    # convergence rates were introduced (see above); they determine,
    # how fast a teacher variable converges towards its best/mean value in one school

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
    teacher_quality_mean=2.56743,
    teacher_quality_sd=0.06792,
    teacher_quality_variation_sd=0.05491,
    teacher_quality_feedback_factor=0.05,
    teacher_quality_convergence_rate=0.05,
    teacher_control_mean=1.17235,
    teacher_control_sd=0.51857,
    teacher_control_variation_sd=0.0003906,
    teacher_control_convergence_rate=0.05,
    random_select=1.64603,
    school_learn_factor=0.01139,
    home_learn_factor=0.0003391,
    school_learn_mean_divisor=1862.0242,
    school_learn_sd=0.03677,
    school_learn_random_proportion=0.16003,
    conformity_factor=0.999994468,
    degradation_factor=0.04403,
    maths_ticks_mean=302.0,
    maths_ticks_sd=6.15693,
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
