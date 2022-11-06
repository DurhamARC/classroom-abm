library("classroommlm")
library("R2MLwiN")
library("tools")


main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  cat(args, sep = "\n")
  real_filename <- args[1]
  simulated_filename <- args[2]
  school_id <- args[3]
  if (!file.exists(real_filename)) {
    stop(paste("File", filename1, "does not exist"))
  }
  if (!file.exists(simulated_filename)) {
    stop(paste("File", simulated_filename, "does not exist"))
  }
  if (length(args) > 3) {
    level = strtoi(args[4])
  } else {
    level = 1
  }
  print(paste("Level: ", level))

  mlnscript_path <- Sys.getenv("MLNSCRIPT_PATH")
  if (mlnscript_path == "") {
    mlnscript_path = '/opt/mln/mlnscript'
  }

  pupil_data <- read.table(real_filename, header=TRUE, sep=",")
  altered_data <- read.table(simulated_filename, header=TRUE, sep=",")
  output_path_prefix <- file_path_sans_ext(simulated_filename)
  mse <- classroommlm::classroom_mse(pupil_data, altered_data, mlnscript_path, output_path_prefix, level, school_id)
  cat(mse)
}

main()
