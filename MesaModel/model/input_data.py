import pandas as pd


class InputData:
    def __init__(self, input_filepath):
        all_data = pd.read_csv(input_filepath).dropna()
        self.grouped = all_data.groupby("class_id")

    def get_class_ids(self):
        return list(self.grouped.groups.keys())

    def get_class_data(self, class_id):
        return self.grouped.get_group(class_id)
