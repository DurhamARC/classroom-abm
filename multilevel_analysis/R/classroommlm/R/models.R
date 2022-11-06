# Multilevel model of classroom data

#' Create the null model
#'
#' This function creates a null model for the given pupil data.
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,school_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the null model
#' @export
null_model <- function(pupil_data, school_id, mlwinpath){
  # Create and summarise null model
  if(school_id > 0) {
    pupil_data <- pupil_data[pupil_data$school_id == school_id,]
  }
  pupil_data <- subset(pupil_data, select=-school_id)
  formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id)
  features = c()
  run_mlm_with_features(pupil_data, mlwinpath, formula, features)
}

#' Create the full model
#'
#' This function creates a full model for the given pupil data.
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,school_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the full model
#' @export
full_model <- function(pupil_data, school_id, mlwinpath){
  if(school_id > 0) {
    pupil_data <- pupil_data[pupil_data$school_id == school_id,]
  }
  pupil_data <- subset(pupil_data, select=-school_id)
  formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Inattentiveness + Ability + Deprivation
  features = c('Start maths', 'Inattention', 'Ability', 'Deprivation')
  run_mlm_with_features(pupil_data, mlwinpath, formula, features)
}

#' Create a simplified full model
#'
#' This function creates a simplified full model for the given pupil data, not including
#' Ability or Inattentiveness
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,school_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the full model
#' @export
simple_full_model <- function(pupil_data, school_id, mlwinpath){
  if(school_id > 0) {
    pupil_data <- pupil_data[pupil_data$school_id == school_id,]
  }
  pupil_data <- subset(pupil_data, select=-school_id)
  sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]
  formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Deprivation
  features = c('Start maths', 'Deprivation')
  run_mlm_with_features(sorted_pupil_data, mlwinpath, formula, features)
}

#' Create a full model excluding the Deprivation marker
#'
#' This function creates a full model for the given pupil data, not including
#' Deprivation
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,school_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the full model
#' @export
full_model_no_deprivation <- function(pupil_data, school_id, mlwinpath){
  if(school_id > 0) {
    pupil_data <- pupil_data[pupil_data$school_id == school_id,]
  }
  pupil_data <- subset(pupil_data, select=-school_id)
  formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Inattentiveness + Ability
  features = c('Start maths', 'Inattention', 'Ability')
  run_mlm_with_features(pupil_data, mlwinpath, formula, features)
}

#' Create a full model excluding the Deprivation marker
#'
#' This function creates a full model for the given pupil data, not including
#' Deprivation
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @param formula the formula to use for the mlwin model
#' @param features the features to use in the output
#' @importFrom stats coef sd vcov
#' @importFrom utils write.csv
#' @return a Data Frame containing the summary data for the full model
run_mlm_with_features <- function(pupil_data, mlwinpath, formula, features){
  sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]
  full_model <- R2MLwiN::runMLwiN(formula, data=sorted_pupil_data, MLwiNPath = mlwinpath)
  full_model.percentage_variance_class_level = full_model@RP[["RP2_var_Intercept"]] * 100 /
    (full_model@RP[["RP1_var_Intercept"]] + full_model@RP[["RP2_var_Intercept"]])


  full_model.summary_table <- data.frame(
    coef(full_model),
    sqrt(diag(vcov(full_model)))
  )
  names(full_model.summary_table) <- c("Actual", "StdErr")
  rownames(full_model.summary_table) <- c(
    'Constant (mean)',
    features,
    'Class variance',
    'Pupil variance'
  )
  full_model.summary_table <- rbind(full_model.summary_table,
                                    "% of variance at class level" = c(
                                      full_model.percentage_variance_class_level,
                                      NA
                                    ))
  full_model.summary_table
}
