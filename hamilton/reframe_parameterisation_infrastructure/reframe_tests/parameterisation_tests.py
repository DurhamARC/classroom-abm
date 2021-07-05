import datetime
import os
import csv
from multiprocessing import Lock

import reframe as rfm
import reframe.utility.sanity as sn

mutex = Lock()
with open(os.environ["PARAMETER_FILE"], "r") as f:
    csv_reader = csv.reader(f)
    ROWS = []
    TEST_IDS = []
    id = 0
    for row in list(csv_reader):
        if row[0] == str(id) or row[0] == "test_id":
            TEST_IDS.append(id)
            ROWS.append(row[1:])
        else:
            print(f"Parameter file does not contain params for test_id {id}")
            exit(1)
        id += 1

OUTPUT_FILE = f"../../mse_results_from_reframe/mse_output_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
with open(OUTPUT_FILE, "w") as output:
    output.write(",".join(ROWS[0]) + ",mean_squared_error\n")


@rfm.parameterized_test(
    *(
        [n_processors, test_id]
        for n_processors in [24]  # 24 only relevant for par7.q
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

        self.keep_files = [f"{execution_dir}/pupil_data_output_{test_id}.csv"]

        self.prerun_cmds = [f"pushd {execution_dir}", "source activate classroom_abm"]

        self.executable = "python run_pipeline.py"

        self.test_id = test_id
        params = " ".join(ROWS[self.test_id])

        self.executable_opts = [
            "--input-file",
            os.environ["DATASET"],
            "--output-file",
            f"pupil_data_output_{test_id}.csv",
            "--n-processors",
            f"{n_processors}",
            "--model-params",
            params,
        ]

    def extract_mse(self):
        target = "Mean squared error: "
        with open(os.path.join(str(self.stagedir), str(self.stdout)), "r") as data:
            for line in data:
                if target in line:
                    return line.strip(target)
        return ""

    @run_after("sanity")
    def add_mse_to_csv(self):
        with mutex:
            with open(OUTPUT_FILE, "a") as output:
                output.write(",".join(ROWS[self.test_id]) + ",")
                output.write(self.extract_mse().strip("\n"))
                output.write("\n")
