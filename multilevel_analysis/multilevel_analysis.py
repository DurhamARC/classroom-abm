import subprocess

subprocess.run(
    ["Rscript", "-e", 'renv::load("R/run_mlm");source("R/run_mlm/run_classroommlm.R")']
)
