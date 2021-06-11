import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.parameterized_test(
    *(
        [n_processors, teacher_params, pupil_params]
        for n_processors in [
            8,
            16,
            24,
        ]  # end on 24 as par7.q on Hamilton has 24 cores per node
        for teacher_params in [
            "1_1",
            "1_1",
        ]  # params according to data_types.py that will be read out of a csv following LHS
        for pupil_params in ["0_0_2", "1_1_1"]
    )
)  # accepts an arbitrary number of parameters
class Parameterisation(rfm.RunOnlyRegressionTest):
    def __init__(self, n_processors, teacher_params, pupil_params):
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

        self.executable_opts = [
            "--input-file",
            os.environ["DATASET"],
            "--output-file",
            "pupil_data_output.csv",
            "--n-processors",
            f"{n_processors}",
            "--teacher-params",
            teacher_params,
            "--pupil-params",
            pupil_params,
        ]
