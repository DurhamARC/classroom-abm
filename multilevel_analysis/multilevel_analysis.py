import subprocess
import sys

completed = subprocess.run(
    ["Rscript", "-e", 'renv::status();source("run_classroommlm.R")'],
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
