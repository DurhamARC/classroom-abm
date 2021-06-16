import os
import csv

import reframe as rfm
import reframe.utility.sanity as sn

with open("../../lhs_sampling/lhs_params.csv", "r") as f:
    csv_reader = csv.reader(f)
    ROWS = [",".join(row[1:]) for row in list(csv_reader)]


@rfm.parameterized_test(
    *(
        [n_processors, test_id]
        for n_processors in [8, 16, 24]  # 24 only relevant for par7.q
        for test_id in range(1, len(ROWS))
    )
)
class Parameterisation(rfm.RunOnlyRegressionTest):
    def __init__(self, n_processors, test_id):
        if n_processors == 8:
            self.time_limit = "1h45m"
        elif n_processors == 16:
            self.time_limit = "1h30m"
        else:
            # big dataset has taken 62 mins
            # in testing with 24 cores
            self.time_limit = "1h15m"

        self.num_tasks = 1
        self.num_cpus_per_task = n_processors

        self.valid_prog_environs = ["intel"]
        self.valid_systems = ["hamilton:multi_cpu_single_node"]

        self.sanity_patterns = sn.assert_found(r"Mean squared error:", self.stdout)

        execution_dir = (
            "/ddn/home/" + os.environ["USER"] + "/classroom-abm/multilevel_analysis"
        )

        self.keep_files = [f"{execution_dir}/pupil_data_output.csv"]

        self.prerun_cmds = [f"pushd {execution_dir}", "source activate classroom_abm"]

        self.executable = "python run_pipeline.py"

        params = ROWS[test_id]

        self.executable_opts = [
            "--input-file",
            os.environ["DATASET"],
            "--output-file",
            "pupil_data_output.csv",
            "--n-processors",
            f"{n_processors}",
            "--model-params",
            params,
        ]
