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

    if completed.returncode:
        print("Error running R script:")
        print(completed.stderr)
        sys.exit(1)

    return completed.stdout


run_rscript("renv::restore()")
output = run_rscript('source("run_classroommlm.R")')
output_lines = output.splitlines()
try:
    mse = float(output_lines[-1])
except ValueError:
    print("Could not convert {mse} to float")
    sys.exit(2)

print(f"Mean squared error: {mse}")
