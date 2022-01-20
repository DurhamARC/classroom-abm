import pytest

from model.data_types import GridParamType
from model import utils


def test_grid_size():
    # Go from 1-10 pupils with a large group size, to check width/height of
    # a single group. Group width and height will be same as overall width
    # and height
    assert utils.get_grid_size(1, 30) == GridParamType(1, 1, 1, 1, 1, 1, 1, 1, 1)
    assert utils.get_grid_size(2, 30) == GridParamType(2, 1, 1, 1, 2, 1, 1, 2, 1)
    assert utils.get_grid_size(3, 30) == GridParamType(2, 2, 1, 1, 3, 1, 1, 2, 2)
    assert utils.get_grid_size(4, 30) == GridParamType(2, 2, 1, 1, 4, 1, 1, 2, 2)
    assert utils.get_grid_size(5, 30) == GridParamType(3, 2, 1, 1, 5, 1, 1, 3, 2)
    assert utils.get_grid_size(6, 30) == GridParamType(3, 2, 1, 1, 6, 1, 1, 3, 2)
    assert utils.get_grid_size(7, 30) == GridParamType(3, 3, 1, 1, 7, 1, 1, 3, 3)
    assert utils.get_grid_size(8, 30) == GridParamType(3, 3, 1, 1, 8, 1, 1, 3, 3)
    assert utils.get_grid_size(9, 30) == GridParamType(3, 3, 1, 1, 9, 1, 1, 3, 3)
    assert utils.get_grid_size(10, 30) == GridParamType(4, 3, 1, 1, 10, 1, 1, 4, 3)

    # Try groups of 4 pupils in various class sizes
    # 4 pupils in a single square group
    assert utils.get_grid_size(4, 4) == GridParamType(2, 2, 1, 1, 4, 1, 1, 2, 2)
    # 16 pupils into 4 groups of 4 arranged in a square
    assert utils.get_grid_size(16, 4) == GridParamType(5, 5, 4, 4, 4, 2, 2, 2, 2)
    # 15 pupils - same arrangement (but 1 group will have only 3 pupils)
    assert utils.get_grid_size(15, 4) == GridParamType(5, 5, 4, 3, 4, 2, 2, 2, 2)
    # 13 pupils - same arrangement (but 3 groups will have only 3 pupils)
    assert utils.get_grid_size(13, 4) == GridParamType(5, 5, 4, 1, 4, 2, 2, 2, 2)

    # Try a class of 30 in different group sizes
    # Groups of 2 pupils - should be split into 15 groups
    # arranged in a 4 x 4 grid of groups
    assert utils.get_grid_size(30, 2) == GridParamType(11, 7, 15, 15, 2, 4, 4, 2, 1)
    # Groups of 5 pupils - should be split into 6 groups
    # arranged in a 2 x 3 grid of groups
    #   1234567
    # 1|XXX  XX |
    # 2|XXX XXX|
    # 3|       |
    # 4|XX  XX |
    # 5|XXX XXX|
    # 6|       |
    # 7|XX  XX |
    # 8|XXX XXX|
    assert utils.get_grid_size(30, 5) == GridParamType(7, 8, 6, 6, 5, 2, 3, 3, 2)
    # Groups of 6 pupils - should be split into 5 groups
    # arranged in a 2 x 3 grid of groups
    #   1234567
    # 1|XXX    |
    # 2|XXX    |
    # 3|       |
    # 4|XXX XXX|
    # 5|XXX XXX|
    # 6|       |
    # 7|XXX XXX|
    # 8|XXX XXX|
    assert utils.get_grid_size(30, 6) == GridParamType(7, 8, 5, 5, 6, 2, 3, 3, 2)

    # Try a class of 31 in larger group sizes
    # Groups of 13 pupils - should be split into 3 groups (11, 10, 10)
    # arranged in a 2 x 2 grid of groups
    #   123456789
    # 1|XXXX XXXX|
    # 2|XXXX XXX |
    # 3|XXX  XXX |
    # 4|         |
    # 5|XXXX     |
    # 6|XXX      |
    # 7|XXX      |
    assert utils.get_grid_size(31, 13) == GridParamType(9, 7, 3, 1, 11, 2, 2, 4, 3)


def test_min_neighbour_count_to_modify_state():
    # Threshold of 6
    # if 8 or more neighbours, group size does not matter
    assert utils.min_neighbour_count_to_modify_state(8, 6, 1) == 6
    assert utils.min_neighbour_count_to_modify_state(8, 6, 100) == 6
    assert utils.min_neighbour_count_to_modify_state(80, 6, 1) == 6
    assert utils.min_neighbour_count_to_modify_state(80, 6, 100) == 6

    # otherwise it depends on group size
    assert utils.min_neighbour_count_to_modify_state(1, 6, 2) == 1
    assert utils.min_neighbour_count_to_modify_state(2, 6, 3) == 2
    assert utils.min_neighbour_count_to_modify_state(3, 6, 4) == 3
    assert utils.min_neighbour_count_to_modify_state(4, 6, 5) == 3
    assert utils.min_neighbour_count_to_modify_state(5, 6, 6) == 4
    assert utils.min_neighbour_count_to_modify_state(6, 6, 7) == 5
    assert utils.min_neighbour_count_to_modify_state(7, 6, 8) == 6

    # Threshold of 2
    # if 8 or more neighbours, group size does not matter
    assert utils.min_neighbour_count_to_modify_state(8, 2, 1) == 2
    assert utils.min_neighbour_count_to_modify_state(8, 2, 100) == 2
    assert utils.min_neighbour_count_to_modify_state(80, 2, 1) == 2
    assert utils.min_neighbour_count_to_modify_state(80, 2, 100) == 2

    # otherwise it depends on group size - for a low threshold we
    # should only reach the threshold with groups of 8
    assert utils.min_neighbour_count_to_modify_state(1, 2, 2) == 1
    assert utils.min_neighbour_count_to_modify_state(2, 2, 3) == 1
    assert utils.min_neighbour_count_to_modify_state(3, 2, 4) == 1
    assert utils.min_neighbour_count_to_modify_state(4, 2, 5) == 1
    assert utils.min_neighbour_count_to_modify_state(5, 2, 6) == 1
    assert utils.min_neighbour_count_to_modify_state(6, 2, 7) == 1
    assert utils.min_neighbour_count_to_modify_state(7, 2, 8) == 2


@pytest.mark.parametrize(
    "inattentiveness,hyper_impulsive,expected_weights",
    [
        (1, 1, [0.5, 0.4, 0.1]),
        (5, 5, [0.1, 0.4, 0.5]),
        (3, 3, [0.3, 0.4, 0.3]),
        (1, 5, [0.5, 0.0, 0.5]),
        (5, 1, [0.1, 0.8, 0.1]),
        (2, 4, [0.4, 0.2, 0.4]),
        (4, 3, [0.2, 0.5, 0.3]),
    ],
)
def test_get_start_state_weights(inattentiveness, hyper_impulsive, expected_weights):
    assert utils.get_start_state_weights(
        inattentiveness, hyper_impulsive
    ) == pytest.approx(expected_weights)
