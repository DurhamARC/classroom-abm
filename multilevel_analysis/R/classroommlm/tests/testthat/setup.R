# Run before any test
pupil_data <- read.csv("../test_input.csv")
pupil_data <- suppressWarnings(transform(pupil_data, end_maths=as.numeric(end_maths)))
pupil_data <- pupil_data[complete.cases(pupil_data),]

mlnscript_path <- Sys.getenv("MLNSCRIPT_PATH", unset = "/opt/mln/mlnscript")

# Run after all tests
withr::defer(remove(pupil_data), teardown_env())
