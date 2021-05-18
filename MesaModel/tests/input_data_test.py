import os

from model.input_data import InputData


def test_input_data():
    input_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "../../classes_input/test_input_short.csv",
    )

    data = InputData(input_path)
    class_ids = data.get_class_ids()
    assert len(class_ids) == 6
    assert class_ids == [489, 1005, 1122, 1477, 2201, 2480]

    class1 = data.get_class_data(489)
    assert len(class1) == 37
    pupil1 = class1.iloc[0]
    assert pupil1["start_maths"] == 29
    assert pupil1["student_id"] == 13063
    pupil2 = class1.iloc[1]
    assert pupil2["start_maths"] == 23
    assert pupil2["student_id"] == 28767

    class2 = data.get_class_data(2201)
    assert len(class2) == 39
