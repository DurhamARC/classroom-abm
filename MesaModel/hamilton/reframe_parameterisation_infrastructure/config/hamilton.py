site_configuration = {
    "systems": [
        {
            "name": "hamilton",
            "descr": "hamilton ARC supercomputer",
            "hostnames": ["hamilton1.hpc.dur.ac.uk", "hamilton2.hpc.dur.ac.uk"],
            "modules_system": "tmod",
            "partitions": [
                {
                    "name": "login",
                    "descr": "login nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": ["intel"],
                    "max_jobs": 100,
                },
                {
                    "name": "multi_cpu_single_node",
                    "descr": "parallel jobs (Hamilton7) - single node",
                    "scheduler": "slurm",
                    "launcher": "local",
                    "access": ["-p par7.q"],
                    "environs": ["intel"],
                    "max_jobs": 100,
                },
            ],
        }
    ],
    "environments": [
        {
            "modules": ["miniconda2/4.1.11", "r/4.0.3"],
            "name": "intel",
            "cc": "icc",
            "cxx": "icpc",
            "ftn": "",
            "target_systems": ["hamilton"],
            "variables": [
                ["MLNSCRIPT_PATH", "/ddn/data/$USER/usr/bin/mlnscript"],
                ["LD_LIBRARY_PATH", "/ddn/data/$USER/usr/lib64"],
            ],
        }
    ],
    "logging": [
        {
            "level": "debug",
            "handlers": [
                {
                    "type": "stream",
                    "name": "stdout",
                    "level": "info",
                    "format": "%(message)s",
                },
                {
                    "type": "file",
                    "name": "reframe.log",
                    "level": "debug",
                    "format": "[%(asctime)s] %(levelname)s: %(check_info)s: %(message)s",  # noqa: E501
                    "append": False,
                },
            ],
            "handlers_perflog": [
                {
                    "type": "filelog",
                    "prefix": "%(check_system)s/%(check_partition)s",
                    "level": "info",
                    "format": (
                        "%(check_job_completion_time)s|reframe %(version)s|"
                        "%(check_info)s|jobid=%(check_jobid)s|"
                        "%(check_perf_var)s=%(check_perf_value)s|"
                        "ref=%(check_perf_ref)s "
                        "(l=%(check_perf_lower_thres)s, "
                        "u=%(check_perf_upper_thres)s)|"
                        "%(check_perf_unit)s"
                    ),
                    "append": True,
                }
            ],
        }
    ],
}
