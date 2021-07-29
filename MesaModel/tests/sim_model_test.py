import datetime

from model.SimModel import SimModel


def test_calculate_holiday_weeks():
    d1 = datetime.date(2021, 2, 1)  # Monday 1st Feb
    d2 = datetime.date(2021, 4, 11)  # Sunday 11th April, 10 weeks later

    # No holidays should give an empty list
    assert SimModel.calculate_holiday_weeks(d1, d2, 0, 1) == []
    # 70 day period = 10 weeks
    # 1 holiday should be around week 5
    # 1 week holiday, terms would be weeks 0-4 and 6-9
    assert SimModel.calculate_holiday_weeks(d1, d2, 1, 1) == [5]
    # 2 week holiday, terms would be weeks 0-3 and 6-9
    assert SimModel.calculate_holiday_weeks(d1, d2, 1, 2) == [4, 5]
    # 3 week holiday, terms would be weeks 0-3 and 7-9
    assert SimModel.calculate_holiday_weeks(d1, d2, 1, 3) == [4, 5, 6]

    # 2 holidays should be around weeks 3 and 7
    # 1 week holiday, terms would be weeks 0-2, 4-6, 8-9
    assert SimModel.calculate_holiday_weeks(d1, d2, 2, 1) == [3, 7]
    # 2 week holiday, terms would be weeks 0-1, 4-5, 8-9
    assert SimModel.calculate_holiday_weeks(d1, d2, 2, 2) == [2, 3, 6, 7]
    # 3 week holiday, terms would be weeks 0-1, 5, 9
    assert SimModel.calculate_holiday_weeks(d1, d2, 2, 3) == [2, 3, 4, 6, 7, 8]

    # Check start and end dates are calculated correctly
    d3 = datetime.date(2021, 2, 4)  # Thursday 4th Feb - should count from start of week
    assert SimModel.calculate_holiday_weeks(d3, d2, 1, 1) == [5]

    d4 = datetime.date(2021, 2, 6)  # Saturday 6th Feb
    # Should count from start of following week, so term is a week shorter and holiday moves
    assert SimModel.calculate_holiday_weeks(d4, d2, 1, 1) == [4]

    d5 = datetime.date(2021, 4, 7)  # Weds 7th April - should count to end of week
    assert SimModel.calculate_holiday_weeks(d1, d5, 1, 1) == [5]

    d6 = datetime.date(2021, 4, 12)  # Monday 12th April - should add an extra week
    # Compare with d4 so we know the holiday has moved
    assert SimModel.calculate_holiday_weeks(d4, d6, 1, 1) == [5]
