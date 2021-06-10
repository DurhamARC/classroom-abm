"""
Global data types. These serve as containers for model parameters.
"""
from dataclasses import dataclass
from enum import Enum


@dataclass(unsafe_hash=True)
class GridParamType:
    height: int
    width: int


@dataclass(unsafe_hash=True)
class TeacherParamType:
    quality: float
    control: float


@dataclass(unsafe_hash=True)
class PupilParamType:
    inattentiveness: float
    hyper_impulsivity: float
    attention_span: float


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
