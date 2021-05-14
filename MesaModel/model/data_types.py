"""
Global data types. These serve as containers for model parameters. Where our
containers are intended to be mutable we use dataclasse, where non-mutability
is required we use namedtuple.
"""
from dataclasses import dataclass
from collections import namedtuple


GridParamType = namedtuple("grid_parameters", "height width")
TeacherParamType = namedtuple("teacher_parameters", "quality control")
PupilParamType = namedtuple(
    "pupil_parameters", "inattentiveness hyper_impulsiveness attention_span"
)


@dataclass(unsafe_hash=True)
class ModelState:
    learning_count: int
    disruptive_count: int
    red_state_count: int
    yellow_state_count: int
    green_state_count: int
