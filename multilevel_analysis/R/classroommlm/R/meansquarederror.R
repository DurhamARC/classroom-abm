# Mean squared error of classroom data

#' Calculate the mean squared error
#'
#' This function calculates the mean squared error between the given real and
#' simulated data frames. It runs the null and full models over each data frame,
#' then scales the means, variances and coefficients, before calculating the
#' mean squared error of the result.
#'
#' @param real_data a Data Frame containing the actual (real) data with headings:
#'        start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param simulated_data a Data Frame containing the simulated data with headings:
#'        start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return the mean squared error score
#' @export
classroom_mse <- function(real_data, simulated_data, mlwinpath) {
  # Run models on real and simulated data
  real_null_model <- classroommlm::null_model(real_data, mlwinpath)
  real_full_model <- classroommlm::full_model(real_data, mlwinpath)
  sim_null_model <- classroommlm::null_model(simulated_data, mlwinpath)
  sim_full_model <- classroommlm::full_model(simulated_data, mlwinpath)

  # Get SDs from data
  real_sds <- c(sd(real_data$start_maths), sd(real_data$Inattentiveness),
                sd(real_data$Ability), sd(real_data$Deprivation))

  # First calculate scaled values for real and simulated data
  real_scaled <- scaled_values(
    real_null_model['Constant (mean)', 'Actual'],
    real_null_model['Pupil variance', 'Actual'],
    real_null_model['Class variance', 'Actual'],
    real_full_model['Constant (mean)', 'Actual'],
    real_full_model[c('Start maths', 'Inattention', 'Ability', 'Deprivation'), 'Actual'],
    real_full_model['Pupil variance', 'Actual'],
    real_full_model['Class variance', 'Actual'],
    real_sds
  )

  sim_scaled <- scaled_values(
    sim_null_model['Constant (mean)', 'Actual'],
    sim_null_model['Pupil variance', 'Actual'],
    sim_null_model['Class variance', 'Actual'],
    sim_full_model['Constant (mean)', 'Actual'],
    sim_full_model[c('Start maths', 'Inattention', 'Ability', 'Deprivation'), 'Actual'],
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
