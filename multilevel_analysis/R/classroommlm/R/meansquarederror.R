# Mean squared error of classroom data

#' Calculate the mean squared error
#'
#' This function calculates the mean squared error between the given real and
#' simulated data frames. It runs the null and full models over each data frame,
#' then scales the means, variances and coefficients, before calculating the
#' mean squared error of the result.
#'
#' @param real_data a Data Frame containing the actual (real) data with headings:
#'        start_maths,student_id,class_id,school_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param simulated_data a Data Frame containing the simulated data with headings:
#'        start_maths,student_id,class_id,school_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param school_id a school id
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @param output_file_prefix the path and file prefix to output the full and null models.
#'        e.g. if passed '~/classroom_abm/classes_output/2021-09-06_output', will create files:
#'        '~/classroom_abm/classes_output/2021-09-06_output_null_model.csv' and
#'        '~/classroom_abm/classes_output/2021-09-06_output_full_model.csv'
#' @param level if 1 (default), runs \code{\link{simple_full_model}}; if 2,
#'        runs \code{\link{full_model_no_deprivation}} otherwise runs
#'        \code{\link{full_model}}
#' @return the mean squared error score
#' @export
classroom_mse <- function(real_data, simulated_data, mlwinpath, output_file_prefix, level = 1, school_id = 0) {
  # Filter dataframes by 'school_id' and exclude the 'school_id' column
  if(school_id > 0) {
    real_data <- real_data[real_data$school_id == school_id,]
  }
  real_data <- subset(real_data, select=-school_id)
  if(school_id > 0) {
    simulated_data <- simulated_data[simulated_data$school_id == school_id,]
  }
  simulated_data <- subset(simulated_data, select=-school_id)

  # Run models on real and simulated data
  real_null_model <- classroommlm::null_model(real_data, mlwinpath)
  sim_null_model <- classroommlm::null_model(simulated_data, mlwinpath)

  if (level == 1) {
    real_full_model <- classroommlm::simple_full_model(real_data, mlwinpath)
    sim_full_model <- classroommlm::simple_full_model(simulated_data, mlwinpath)
    pupil_properties = c('Start maths', 'Deprivation')
  } else if (level == 2) {
    real_full_model <- classroommlm::full_model_no_deprivation(real_data, mlwinpath)
    sim_full_model <- classroommlm::full_model_no_deprivation(simulated_data, mlwinpath)
    pupil_properties = c('Start maths', 'Inattention', 'Ability')
  } else {
    real_full_model <- classroommlm::full_model(real_data, mlwinpath)
    sim_full_model <- classroommlm::full_model(simulated_data, mlwinpath)
    pupil_properties = c('Start maths', 'Inattention', 'Ability', 'Deprivation')
  }

  if (school_id == 0){
    write.csv(sim_null_model, paste(output_file_prefix, "_null_model.csv", sep=""), row.names = TRUE)
    write.csv(sim_full_model, paste(output_file_prefix, "_full_model.csv", sep=""), row.names = TRUE)
  }
  # else {
  #   write.csv(sim_null_model, paste(output_file_prefix, "_null_model_", as.character(school_id), ".csv", sep=""), row.names = TRUE)
  #   write.csv(sim_full_model, paste(output_file_prefix, "_full_model_", as.character(school_id), ".csv", sep=""), row.names = TRUE)
  # }

  # Get SDs from data
  real_sds <- c(sd(real_data$start_maths), sd(real_data$Inattentiveness),
                sd(real_data$Ability), sd(real_data$Deprivation))

  # First calculate scaled values for real and simulated data
  real_scaled <- scaled_values(
    real_null_model['Constant (mean)', 'Actual'],
    real_null_model['Pupil variance', 'Actual'],
    real_null_model['Class variance', 'Actual'],
    real_full_model['Constant (mean)', 'Actual'],
    real_full_model[pupil_properties, 'Actual'],
    real_full_model['Pupil variance', 'Actual'],
    real_full_model['Class variance', 'Actual'],
    real_sds
  )

  sim_scaled <- scaled_values(
    sim_null_model['Constant (mean)', 'Actual'],
    sim_null_model['Pupil variance', 'Actual'],
    sim_null_model['Class variance', 'Actual'],
    sim_full_model['Constant (mean)', 'Actual'],
    sim_full_model[pupil_properties, 'Actual'],
    sim_full_model['Pupil variance', 'Actual'],
    sim_full_model['Class variance', 'Actual'],
    real_sds
  )

  # Calculate mean squared error
  Metrics::mse(real_scaled, sim_scaled)
}

#' Scale the given values in preparation for calculating the mean squared error
#' @return a vector of scaled values
#' @noRd
scaled_values <- function(null_mean, null_pupil_variance, null_class_variance, full_mean,
              full_coefficients, full_pupil_variance, full_class_variance, real_sds) {
  # The coefficients (beta values) are scaled according to the standard deviations
  # of the real data
  scaled_coefficients <- 2 * full_coefficients * real_sds
  # Means are not scaled; other values are scaled at 2 * the square root
  scaled <- c(
    null_mean,
    2 * sqrt(null_pupil_variance),
    2 * sqrt(null_class_variance),
    full_mean,
    scaled_coefficients,
    2 * sqrt(full_pupil_variance),
    2 * sqrt(full_class_variance)
  )
}
