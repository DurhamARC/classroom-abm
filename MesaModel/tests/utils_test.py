from model.data_types import GridParamType
from model import utils


def test_grid_size():
    # Go from 1-10 pupils with a large group size, to check width/height of
    # a single group. Group width and height will be same as overall width
    # and height
    assert utils.get_grid_size(1, 30) == GridParamType(1, 1, 1, 1, 1, 1, 1, 1)
    assert utils.get_grid_size(2, 30) == GridParamType(2, 1, 1, 1, 1, 1, 2, 1)
    assert utils.get_grid_size(3, 30) == GridParamType(2, 2, 1, 1, 1, 1, 2, 2)
    assert utils.get_grid_size(4, 30) == GridParamType(2, 2, 1, 1, 1, 1, 2, 2)
    assert utils.get_grid_size(5, 30) == GridParamType(3, 2, 1, 1, 1, 1, 3, 2)
    assert utils.get_grid_size(5, 30) == GridParamType(3, 2, 1, 1, 1, 1, 3, 2)
    assert utils.get_grid_size(6, 30) == GridParamType(3, 2, 1, 1, 1, 1, 3, 2)
    assert utils.get_grid_size(7, 30) == GridParamType(3, 3, 1, 1, 1, 1, 3, 3)
    assert utils.get_grid_size(8, 30) == GridParamType(3, 3, 1, 1, 1, 1, 3, 3)
    assert utils.get_grid_size(9, 30) == GridParamType(3, 3, 1, 1, 1, 1, 3, 3)
    assert utils.get_grid_size(10, 30) == GridParamType(4, 3, 1, 1, 1, 1, 4, 3)

    # Try groups of 4 pupils in various class sizes
    # 4 pupils in a single square group
    assert utils.get_grid_size(4, 4) == GridParamType(2, 2, 1, 1, 1, 1, 2, 2)
    # 16 pupils into 4 groups of 4 arranged in a square
    assert utils.get_grid_size(16, 4) == GridParamType(5, 5, 4, 4, 2, 2, 2, 2)
    # 15 pupils - same arrangement (but 1 group will have only 3 pupils)
    assert utils.get_grid_size(15, 4) == GridParamType(5, 5, 4, 3, 2, 2, 2, 2)
    # 13 pupils - same arrangement (but 3 groups will have only 3 pupils)
    assert utils.get_grid_size(13, 4) == GridParamType(5, 5, 4, 1, 2, 2, 2, 2)

    # Try a class of 30 in different group sizes
    # Groups of 2 pupils - should be split into 15 groups
    # arranged in a 4 x 4 grid of groups
    assert utils.get_grid_size(30, 2) == GridParamType(11, 7, 15, 15, 4, 4, 2, 1)
    # Groups of 5 pupils - should be split into 6 groups
    # arranged in a 2 x 3 grid of groups
    #   1234567
    # 1|XX  XX |
    # 2|XXX XXX|
    # 3|       |
    # 4|XX  XX |
    # 5|XXX XXX|
    # 6|       |
    # 7|XX  XX |
    # 8|XXX XXX|
    assert utils.get_grid_size(30, 5) == GridParamType(7, 8, 6, 6, 2, 3, 3, 2)
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
    assert utils.get_grid_size(30, 6) == GridParamType(7, 8, 5, 5, 2, 3, 3, 2)


def test_min_neighbour_count_to_modify_state():
    # if 8 or more neighbours, group size does not matter
    assert utils.min_neighbour_count_to_modify_state(8, 1) == 6
    assert utils.min_neighbour_count_to_modify_state(8, 100) == 6
    assert utils.min_neighbour_count_to_modify_state(80, 1) == 6
    assert utils.min_neighbour_count_to_modify_state(80, 100) == 6

    # otherwise it depends on group size
    assert utils.min_neighbour_count_to_modify_state(1, 2) == 1
    assert utils.min_neighbour_count_to_modify_state(2, 3) == 2
    assert utils.min_neighbour_count_to_modify_state(3, 4) == 3
    assert utils.min_neighbour_count_to_modify_state(4, 5) == 3
    assert utils.min_neighbour_count_to_modify_state(5, 6) == 4
    assert utils.min_neighbour_count_to_modify_state(6, 7) == 5
    assert utils.min_neighbour_count_to_modify_state(7, 8) == 6
