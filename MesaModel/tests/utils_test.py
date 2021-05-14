from model.data_types import GridParamType
from model import utils


def test_grid_size():
    # Go from 1-10 pupils which should cover most cases of just before/after a square number
    assert utils.get_grid_size(1) == GridParamType(1, 1)
    assert utils.get_grid_size(2) == GridParamType(2, 1)
    assert utils.get_grid_size(3) == GridParamType(2, 2)
    assert utils.get_grid_size(4) == GridParamType(2, 2)
    assert utils.get_grid_size(5) == GridParamType(3, 2)
    assert utils.get_grid_size(5) == GridParamType(3, 2)
    assert utils.get_grid_size(6) == GridParamType(3, 2)
    assert utils.get_grid_size(7) == GridParamType(3, 3)
    assert utils.get_grid_size(8) == GridParamType(3, 3)
    assert utils.get_grid_size(9) == GridParamType(3, 3)
    assert utils.get_grid_size(10) == GridParamType(4, 3)
