import datetime
import os
import csv
from multiprocessing import Lock

import reframe as rfm
import reframe.utility.sanity as sn

project_path = os.environ["PROJECT_PATH"]
os.sys.path.append(project_path)
from MesaModel.model.input_data import InputData

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

MSE_OUTPUT_FILE = os.environ.get(
    "MSE_OUTPUT_FILE",
    f"../../mse_results_from_reframe/mse_output_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
)

input_file = os.path.join(project_path, "multilevel_analysis", os.environ["DATASET"])
school_ids = InputData(input_file).get_school_ids()
with open(MSE_OUTPUT_FILE, "w") as output:
    output.write("test_id,repeat_no," + ",".join(ROWS[0]) + ",mean_squared_error")
    for school_id in school_ids:
        output.write(f",mse_{school_id}")
    output.write("\n")


@rfm.parameterized_test(
    *(
        [test_id, iteration]
        for test_id in range(1, len(ROWS))
        for iteration in [
            i + 1 for i in range(int(os.environ["NUM_REPEATS"]))
        ]  # set to [1] for just one iterations
    )
)
class Parameterisation(rfm.RunOnlyRegressionTest):
    def __init__(self, test_id, iteration):
        if "short" in os.environ["DATASET"]:
            n_processors = 2
            self.time_limit = "30m"
        else:
            n_processors = 64 if self.current_system.name == "hamilton8" else 24
            self.time_limit = "1h" if "_25" in os.environ["DATASET"] else "5h"

        feedback_weeks = os.environ["FEEDBACK_WEEKS"]
        convergence_days = os.environ["CONVERGENCE_DAYS"]

        self.num_tasks = 1
        self.num_cpus_per_task = n_processors

        self.valid_prog_environs = ["intel", "amd"]
        self.valid_systems = [
            "hamilton:multi_cpu_single_node",
            "hamilton8:multi_cpu_shared",
        ]

        self.sanity_patterns = sn.assert_found(r"Mean squared error:", self.stdout)

        execution_dir = os.environ["PROJECT_PATH"] + "/multilevel_analysis"

        self.keep_files = [
            f"{execution_dir}/pupil_data_output_{test_id}_{iteration}*.csv"
        ]

        self.prerun_cmds = [
            f"pushd {execution_dir}",
            f"rm -rf pupil_data_output_{test_id}_{iteration}.csv",  # prevent appending to previous data
            "echo $PATH",
            "source $HOME/.bashrc",
            "conda init",
            "conda activate classroom_abm",
        ]

        if self.current_system.name == "hamilton8":
            # Need to manually load modules on hamilton8 as modules system isn't compatible with ReFrame
            self.prerun_cmds.extend(
                ["module load r/4.1.2", "module load $R_BUILD_MODULES"],
            )

        self.executable = "$CONDA_PREFIX/bin/python run_pipeline.py"

        self.test_id = test_id
        self.repeat_no = iteration
        params = " ".join(ROWS[self.test_id])

        self.executable_opts = [
            "--input-file",
            os.environ["DATASET"],
            "--output-file",
            f"pupil_data_output_{test_id}_{iteration}.csv",
            "--n-processors",
            f"{n_processors}",
            "--model-params",
            params,
            "--feedback-weeks",
            f"{feedback_weeks}",
            "--convergence-days",
            f"{convergence_days}",
        ]

    @run_before("run")
    def copy_to_stagedir(self):
        # Copy the latest best parameters file to the current reframe stage directory
        best_params_file = os.environ["BEST_PARAMETER_FILE"]
        if not os.path.exists(best_params_file):
            homedir = os.environ["HOME"]
            best_params_file = os.path.join(homedir, "best_params.csv")
        if os.path.exists(best_params_file):
            self.prerun_cmds.extend(
                [
                    f"cp {best_params_file} {self.stagedir}/best_params.csv",
                ],
            )
            best_params_file = os.path.join(str(self.stagedir), "best_params.csv")
            self.executable_opts.extend(
                [
                    "--best-params-file",
                    best_params_file,
                ],
            )

    def extract_data(self, target_string):
        # Search through all lines and extract all values following the given 'target_string'
        # Expected format of the sequence of all values for the given 'target_string' is
        # .. a sequence of lines characterising first the total value for all schools (indexed as [0]),
        # .. then partial values for individual schools indexed as [1], [2], and so on
        # 1) For the list of schools ("School: "):
        #   - [0] for all schools;
        #   - [1], [2], and so on denote indices for individual schools
        # 2) For the list of MSEs ("Mean squared error: "):
        #   - [0] the total MSE;
        #   - [1], [2], and so on partial MSEs for individual schools
        target = target_string
        values = []
        with open(os.path.join(str(self.stagedir), str(self.stdout)), "r") as data:
            for line in data:
                if target in line:
                    values.extend(
                        [line.strip(target)],
                    )
        if values:
            return values
        return ""

    # def extract_mse(self):
    #     target = "Mean squared error: "
    #     with open(os.path.join(str(self.stagedir), str(self.stdout)), "r") as data:
    #         for line in data:
    #             if target in line:
    #                 return line.strip(target)
    #     return ""

    @run_after("sanity")
    def add_mse_to_csv(self):
        with mutex:
            school_mses_list = self.extract_data("Mean squared error: ")
            with open(MSE_OUTPUT_FILE, "a") as output:
                output.write(
                    f"{self.test_id},{self.repeat_no}," + ",".join(ROWS[self.test_id])
                )
                for school_mse in school_mses_list:
                    school_mse = school_mse.strip("\n")
                    output.write(f",{school_mse}")
                output.write("\n")
