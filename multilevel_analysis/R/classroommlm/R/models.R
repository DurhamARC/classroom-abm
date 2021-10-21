# Multilevel model of classroom data

#' Create the null model
#'
#' This function creates a null model for the given pupil data.
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the null model
#' @export
null_model <- function(pupil_data, mlwinpath){
  # Create and summarise null model
  sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]
  null_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id)
  null_model <- R2MLwiN::runMLwiN(null_formula, data=sorted_pupil_data, MLwiNPath = mlwinpath)

  null_model.percentage_variance_class_level = null_model@RP[["RP2_var_Intercept"]] * 100 /
    (null_model@RP[["RP1_var_Intercept"]] + null_model@RP[["RP2_var_Intercept"]])

  null_model.summary_table <- data.frame(
    coef(null_model),
    sqrt(diag(vcov(null_model)))
  )
  names(null_model.summary_table) <- c("Actual", "StdErr")
  rownames(null_model.summary_table) = c('Constant (mean)', 'Class variance', 'Pupil variance')
  null_model.summary_table <- rbind(null_model.summary_table,
                                    "% of variance at class level" = c(
                                      null_model.percentage_variance_class_level,
                                      NA
                                    ))
  null_model.summary_table
}

#' Create the full model
#'
#' This function creates a full model for the given pupil data.
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the full model
#' @export
full_model <- function(pupil_data, mlwinpath){
  sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]
  full_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Inattentiveness + Ability + Deprivation
  full_model <- R2MLwiN::runMLwiN(full_formula, data=sorted_pupil_data, MLwiNPath = mlwinpath)
  full_model.percentage_variance_class_level = full_model@RP[["RP2_var_Intercept"]] * 100 /
    (full_model@RP[["RP1_var_Intercept"]] + full_model@RP[["RP2_var_Intercept"]])


  full_model.summary_table <- data.frame(
    coef(full_model),
    sqrt(diag(vcov(full_model)))
  )
  names(full_model.summary_table) <- c("Actual", "StdErr")
  rownames(full_model.summary_table) <- c(
    'Constant (mean)',
    'Start maths',
    'Inattention',
    'Ability',
    'Deprivation',
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

#' Create a simplified full model
#'
#' This function creates a simplified full model for the given pupil data, not including
#' Ability or Inattentiveness
#' @param pupil_data a Data Frame with headings:
#'        start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)
#' @param mlwinpath the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')
#' @return a Data Frame containing the summary data for the full model
#' @export
simple_full_model <- function(pupil_data, mlwinpath){
  sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]
  simple_full_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Deprivation
  simple_full_model <- R2MLwiN::runMLwiN(simple_full_formula, data=sorted_pupil_data, MLwiNPath = mlwinpath)
  simple_full_model.percentage_variance_class_level = simple_full_model@RP[["RP2_var_Intercept"]] * 100 /
    (simple_full_model@RP[["RP1_var_Intercept"]] + simple_full_model@RP[["RP2_var_Intercept"]])


  simple_full_model.summary_table <- data.frame(
    coef(simple_full_model),
    sqrt(diag(vcov(simple_full_model)))
  )
  names(simple_full_model.summary_table) <- c("Actual", "StdErr")
  rownames(simple_full_model.summary_table) <- c(
    'Constant (mean)',
    'Start maths',
    'Deprivation',
    'Class variance',
    'Pupil variance'
  )
  simple_full_model.summary_table <- rbind(simple_full_model.summary_table,
                                    "% of variance at class level" = c(
                                      simple_full_model.percentage_variance_class_level,
                                      NA
                                    ))
  simple_full_model.summary_table
}

