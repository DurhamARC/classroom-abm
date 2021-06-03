library("classroommlm")
library("R2MLwiN")


main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  cat(args, sep = "\n")
  real_filename <- args[1]
  simulated_filename <- args[2]
  if (!file.exists(real_filename)) {
    stop(paste("File", filename1, "does not exist"))
  }
  if (!file.exists(simulated_filename)) {
    stop(paste("File", simulated_filename, "does not exist"))
  }

  mlnscript_path <- Sys.getenv("MLNSCRIPT_PATH")
  if (mlnscript_path == "") {
    mlnscript_path = '/opt/mln/mlnscript'
  }

  pupil_data <- read.table(real_filename, header=TRUE, sep=",")
  altered_data <- read.table(simulated_filename, header=TRUE, sep=",")
  mse <- classroommlm::classroom_mse(pupil_data, altered_data, mlwinpath=mlnscript_path)
  cat(mse)
}

main()
