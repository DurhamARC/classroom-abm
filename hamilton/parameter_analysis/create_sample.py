import pandas as pd
from numpy.random import default_rng


def create_sample(
    input_file="../../classes_input/test_input.csv",
    output_file=None,
    percentage_sample=25,
):
    if not output_file:
        output_file = f"../../classes_input/test_input_sampled_{percentage_sample}.csv"

    rng = default_rng()

    df = pd.read_csv(input_file)
    all_classes = pd.unique(df["class_id"])
    class_sample_size = round(len(all_classes) * percentage_sample / 100)
    sampled_classes = rng.choice(all_classes, class_sample_size)

    sampled_df = df[df.class_id.isin(sampled_classes)]

    sampled_df.to_csv(
        output_file, sep=",", encoding="utf-8", float_format="%g", index=False
    )
