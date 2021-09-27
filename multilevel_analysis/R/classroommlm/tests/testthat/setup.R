# Run before any test
pupil_data <- read.csv("../test_input.csv")
pupil_data <- suppressWarnings(transform(pupil_data, end_maths=as.numeric(end_maths)))
pupil_data <- pupil_data[complete.cases(pupil_data),]

sampled_pupil_data <- read.csv("../test_input_sampled_25.csv")
sampled_pupil_data <- suppressWarnings(transform(sampled_pupil_data, end_maths=as.numeric(end_maths)))
sampled_pupil_data <- sampled_pupil_data[complete.cases(sampled_pupil_data),]

mlnscript_path <- Sys.getenv("MLNSCRIPT_PATH", unset = "/opt/mln/mlnscript")

# Run after all tests
test_cleanup <- function(pd, spd) {
  remove(pd, spd)
  output_prefix <- file.path(getwd(),"test")
  null_path <- paste(output_prefix, "_null_model.csv", sep="")
  full_path <- paste(output_prefix, "_full_model.csv", sep="")
  if (file.exists(null_path)) {
    file.remove(null_path)
  }
  if (file.exists(full_path)) {
    file.remove(full_path)
  }
}
withr::defer(test_cleanup(pupil_data, sampled_pupil_data), teardown_env())
