site_configuration = {
    "systems": [
        {
            "name": "hamilton8",
            "descr": "hamilton8 ARC supercomputer",
            "hostnames": ["login1.ham8.dur.ac.uk"],
            "modules_system": "tmod",
            "partitions": [
                {
                    "name": "login",
                    "descr": "login nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": ["amd"],
                    "max_jobs": 100,
                },
                {
                    "name": "multi_cpu_shared",
                    "descr": "parallel jobs (Hamilton8) - shared queue",
                    "scheduler": "slurm",
                    "launcher": "local",
                    "access": ["-p shared"],
                    "environs": ["amd"],
                    "max_jobs": 100,
                },
            ],
        }
    ],
    "environments": [
        {
            "modules": ["r/4.1.2", "$R_BUILD_MODULES"],
            "name": "amd",
            "cc": "icc",
            "cxx": "icpc",
            "ftn": "",
            "target_systems": ["hamilton8"],
            "variables": [
                ["MLNSCRIPT_PATH", "$NOBACKUP/usr/bin/mlnscript"],
                ["LD_LIBRARY_PATH", "$NOBACKUP/usr/lib64:$LD_LIBRARY_PATH"],
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
