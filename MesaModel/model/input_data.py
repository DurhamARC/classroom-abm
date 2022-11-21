import pandas as pd
import sys


class InputData:
    def __init__(self, input_filepath):
        all_data = pd.read_csv(input_filepath).dropna()
        self.grouped = all_data.groupby("class_id")
        if "school_id" in all_data:
            self.grouped_by_school = all_data.groupby("school_id")
        else:
            self.grouped_by_school = None

    def get_class_ids(self):
        return list(self.grouped.groups.keys())

    def get_school_ids(self):
        if self.grouped_by_school:
            return list(self.grouped_by_school.groups.keys())
        else:
            return []

    def get_school_id(self, class_id):
        school_id = 0
        if "school_id" in self.grouped.get_group(class_id).keys():
            school_ids = set(self.grouped.get_group(class_id)["school_id"])
            if len(school_ids) > 1:
                print("ERROR: Can not be more than 1 school for one class!!!")
                sys.exit(1)
            else:
                school_id = list(school_ids)[0]
        return school_id

    def get_class_data(self, class_id):
        return self.grouped.get_group(class_id)
