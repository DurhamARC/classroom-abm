from model.SimModel import SimModel


def test_calculate_holiday_weeks():
    # No holidays should give an empty list
    assert SimModel.calculate_holiday_weeks(100, 0, 1) == []
    # 70 day period = 10 weeks
    # 1 holiday should be around week 5
    # 1 week holiday, terms would be weeks 0-4 and 6-9
    assert SimModel.calculate_holiday_weeks(70, 1, 1) == [5]
    # 2 week holiday, terms would be weeks 0-3 and 6-9
    assert SimModel.calculate_holiday_weeks(70, 1, 2) == [4, 5]
    # 3 week holiday, terms would be weeks 0-3 and 7-9
    assert SimModel.calculate_holiday_weeks(70, 1, 3) == [4, 5, 6]

    # 2 holidays should be around weeks 3 and 7
    # 1 week holiday, terms would be weeks 0-2, 4-6, 8-9
    assert SimModel.calculate_holiday_weeks(70, 2, 1) == [3, 7]
    # 2 week holiday, terms would be weeks 0-1, 4-5, 8-9
    assert SimModel.calculate_holiday_weeks(70, 2, 2) == [2, 3, 6, 7]
    # 3 week holiday, terms would be weeks 0-1, 5, 9
    assert SimModel.calculate_holiday_weeks(70, 2, 3) == [2, 3, 4, 6, 7, 8]
