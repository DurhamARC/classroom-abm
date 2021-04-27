library("classroommlm")
library("R2MLwiN")


mlnscript_path <- Sys.getenv("MLNSCRIPT_PATH")
if (mlnscript_path == "") {
  mlnscript_path = '/opt/mln/mlnscript'
}

pupil_data <- read.table("../../../classes_input/test_input.csv", header=TRUE, sep=",")
null_summary <- classroommlm::null_model(pupil_data, mlnscript_path)
print(null_summary)

full_summary <- classroommlm::full_model(pupil_data, mlnscript_path)
print(null_summary)
