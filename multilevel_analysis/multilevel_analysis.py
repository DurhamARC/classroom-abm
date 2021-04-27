import subprocess
import sys

completed = subprocess.run(
    ["Rscript", "-e", 'source("R/run_mlm/run_classroommlm.R")'],
    capture_output=True,
    text=True,
)
print(completed.stdout)

if completed.returncode:
    print("Error running R script:")
    print(completed.stderr)
    sys.exit(1)
else:
    print("Success")
