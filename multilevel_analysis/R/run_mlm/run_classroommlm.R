library("classroommlm")
library("R2MLwiN")


mlnscript_path <- Sys.getenv("MLNSCRIPT_PATH")
if (mlnscript_path == "") {
  mlnscript_path = '/opt/mln/mlnscript'
}

pupil_data <- read.table("../../../classes_input/test_input.csv", header=TRUE, sep=",")
altered_data <- transform(pupil_data,
                          end_maths=end_maths+rnorm(nrow(pupil_data), mean=0, sd=10))
mse <- classroommlm::classroom_mse(pupil_data, altered_data, mlwinpath=mlnscript_path)
cat(mse)
