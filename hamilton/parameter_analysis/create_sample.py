import os
import pandas as pd
from numpy.random import default_rng


def create_sample(
    input_file="../../classes_input/test_input.csv",
    output_file=None,
    percentage_sample=25,
    exclude_samples=None,
):
    if not output_file:
        exclude = ""
        if exclude_samples:
            excluded_names = [
                os.path.splitext(os.path.basename(x))[0].replace(
                    "test_input_sampled_", ""
                )
                for x in exclude_samples
            ]
            exclude = f"_exclude_{'_'.join(excluded_names)}"
        output_file = (
            f"../../classes_input/test_input_sampled_{percentage_sample}{exclude}.csv"
        )

    rng = default_rng()

    input_df = pd.read_csv(input_file)
    all_classes = pd.unique(input_df["class_id"])

    excluded_classes = set()
    for f in exclude_samples:
        df = pd.read_csv(f)
        excluded_classes = excluded_classes.union(pd.unique(df["class_id"]))

    classes_to_sample = list(set(all_classes) - excluded_classes)
    class_sample_size = round(len(all_classes) * percentage_sample / 100)
    sampled_classes = rng.choice(classes_to_sample, class_sample_size)
    sampled_df = input_df[input_df.class_id.isin(sampled_classes)]

    sampled_df.to_csv(
        output_file, sep=",", encoding="utf-8", float_format="%g", index=False
    )
