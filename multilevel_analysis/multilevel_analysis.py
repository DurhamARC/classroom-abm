import subprocess
import sys


def run_rscript(script):
    params = ["Rscript", "-e", script]
    print(f"Running: {' '.join(params)}")
    completed = subprocess.run(
        params,
        capture_output=True,
        text=True,
        cwd="./R/run_mlm",
    )
    print(completed.stdout)

    if completed.returncode:
        print("Error running R script:")
        print(completed.stderr)
        sys.exit(1)
    else:
        print("Success")


run_rscript("renv::restore()")
run_rscript('source("run_classroommlm.R")')
