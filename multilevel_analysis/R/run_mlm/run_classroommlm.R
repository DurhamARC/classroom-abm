library("classroommlm")
library("R2MLwiN")

pupil_data <- read.table("/Users/ksvf48/Documents/dev/classroom-abm/classes_input/test_input.csv", header=TRUE, sep=",")
null_summary <- classroommlm::null_model(pupil_data, '/opt/mln/mlnscript')
print(null_summary)

full_summary <- classroommlm::full_model(pupil_data, '/opt/mln/mlnscript')
print(null_summary)
