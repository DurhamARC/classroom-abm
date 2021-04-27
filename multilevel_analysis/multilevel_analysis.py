import subprocess
import sys


def run_rscript(script):
    completed = subprocess.run(
        ["Rscript", "-e", script],
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
