import pytest

from model.data_types import ModelParamType


def test_type_casting():
    # Create tuple of floats to use as params
    float_params = [1.5] * 19
    model_params = ModelParamType(*float_params)

    # Check non-float params have been cast to correct types
    assert isinstance(model_params.ticks_per_home_day, int)
    assert isinstance(model_params.number_of_holidays, int)
    assert isinstance(model_params.weeks_per_holiday, int)
    assert isinstance(model_params.group_size, int)
    assert isinstance(model_params.group_by_ability, bool)

    # Try passing an invalid type
    float_params[0] = "thisisnotafloat"
    with pytest.raises(ValueError) as excinfo:
        model_params = ModelParamType(*float_params)

    assert (
        "Could not cast 'thisisnotafloat' value for teacher_quality_mean to be <class 'float'>"
        in str(excinfo.value)
    )
