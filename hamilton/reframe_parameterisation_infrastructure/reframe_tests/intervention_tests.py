import datetime
import os
import csv
from multiprocessing import Lock

import reframe as rfm
import reframe.utility.sanity as sn

mutex = Lock()
parameter_file = os.environ["PARAMETER_FILE"]
with open(parameter_file, "r") as f:
    csv_reader = csv.reader(f)
    csv_headings = next(csv_reader)
    if 'teacher_quality_mean' in csv_headings\
    and 'teacher_quality_sd' in csv_headings\
    and 'teacher_control_mean' in csv_headings\
    and 'teacher_control_sd' in csv_headings:
        tqm_idx = csv_headings.index('teacher_quality_mean')-1
        tqsd_idx = csv_headings.index('teacher_quality_sd')-1
        tcm_idx = csv_headings.index('teacher_control_mean')-1
        tcsd_idx = csv_headings.index('teacher_control_sd')-1
        print(f"Indices: {tqm_idx}, {tqsd_idx}, {tcm_idx}, {tcsd_idx}")
    else:
        print(f"Parameter file does not contain data for teacher_quality_mean and/or teacher_control_mean")
        exit(1)
with open(parameter_file, "r") as f:
    csv_reader = csv.reader(f)
    ROWS = []
    TEST_IDS = []
    id = 0
    rows_list = list(csv_reader)
    for row in rows_list:
        if row[0] == str(id) or row[0] == "test_id":
            TEST_IDS.append(id)
            ROWS.append(row[1:])
        else:
            print(f"Parameter file does not contain params for test_id {id}")
            exit(2)
        print(f"[{id}] tq: {row[tqm_idx+1]}, {row[tqsd_idx+1]}; tc: {row[tcm_idx+1]}, {row[tcsd_idx+1]}")
        id += 1
    len_rows = len(ROWS)
    num_iter = int(os.environ["NUM_ITERATIONS"])
    num_incr = int(os.environ["NUM_INCREMENTS"])
    incr_factor = float(os.environ["INCR_FACTOR"])
    for test_id in range(1, len_rows):
        row = ROWS[test_id].copy()
        row_new = row.copy()
        for it in range(num_iter):
            for iq in range(0,num_incr):
                row_new[tqm_idx] = str(float(row[tqm_idx]) + incr_factor*(it*num_incr+iq)*float(row[tqsd_idx]))
                for ic in range(0,num_incr):
                    row_new[tcm_idx] = str(float(row[tcm_idx]) + incr_factor*(it*num_incr+ic)*float(row[tcsd_idx]))
                    TEST_IDS.append(id)
                    ROWS.append(row_new.copy())
                    print(f"[{id}] tq: {row_new[tqm_idx]}, {row_new[tqsd_idx]}; tc: {row_new[tcm_idx]}, {row_new[tcsd_idx]}")
                    id += 1
    for test_id in range(1, len(ROWS)-len_rows+1):
        print(f"[{test_id}] params = {ROWS[test_id+len_rows-1]}")

MSE_OUTPUT_FILE = os.environ.get(
    "MSE_OUTPUT_FILE",
    f"../../mse_results_from_reframe/mse_output_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
)
with open(MSE_OUTPUT_FILE, "w") as output:
    output.write("test_id,repeat_no," + ",".join(ROWS[0]) + ",mean_squared_error,avg_maths_score\n")


@rfm.parameterized_test(
    *(
        [test_id, repeat]
        for test_id in range(1, len(ROWS)-len_rows+1)
        for repeat in [
            i + 1 for i in range(int(os.environ["NUM_REPEATS"]))
        ]  # set to [1] for just one repeat
    )
)
class Intervention(rfm.RunOnlyRegressionTest):
    def __init__(self, test_id, repeat):
        if "short" in os.environ["DATASET"]:
            n_processors = 2
            self.time_limit = "30m"
        else:
            n_processors = 64 if self.current_system.name == "hamilton8" else 24
            self.time_limit = "1h" if "_25" in os.environ["DATASET"] else "1h30m"

        feedback_weeks = os.environ["FEEDBACK_WEEKS"]
        convergence_days = os.environ["CONVERGENCE_DAYS"]

        self.num_tasks = 1
        self.num_cpus_per_task = n_processors

        self.valid_prog_environs = ["intel", "amd"]
        self.valid_systems = [
            "hamilton:multi_cpu_single_node",
            "hamilton8:multi_cpu_shared",
        ]

        self.sanity_patterns = sn.assert_found(r"Average maths score:", self.stdout)

        execution_dir = os.environ["CLASSROOMABM_PATH"] + "/multilevel_analysis"
        pupil_data_filename = f"pupil_data_output_{test_id}_{repeat}"

        self.keep_files = [
            f"{execution_dir}/{pupil_data_filename}*.csv"
        ]

        self.prerun_cmds = [
            f"pushd {execution_dir}",
            f"rm -rf {pupil_data_filename}.csv",  # prevent appending to previous data
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
        self.repeat_no = repeat
        params = " ".join(ROWS[self.test_id+len_rows-1])

        self.executable_opts = [
            "--input-file",
            os.environ["DATASET"],
            "--output-file",
            f"{pupil_data_filename}.csv",
            "--n-processors",
            f"{n_processors}",
            "--model-params",
            params,
            "--feedback-weeks",
            f"{feedback_weeks}",
            "--convergence-days",
            f"{convergence_days}",
        ]

    def extract_data(self, target):
        with open(os.path.join(str(self.stagedir), str(self.stdout)), "r") as data:
            for line in data:
                if target in line:
                    return line.strip(target)
        return ""

    @run_after("sanity")
    def add_mse_to_csv(self):
        with mutex:
            with open(MSE_OUTPUT_FILE, "a") as output:
                output.write(
                    f"{self.test_id},{self.repeat_no},"
                    + ",".join(ROWS[self.test_id+len_rows-1])
                    + ","
                    + self.extract_data("Mean squared error: ").strip("\n")
                    + ","
                    + self.extract_data("Average maths score: ").strip("\n")
                    + "\n")
