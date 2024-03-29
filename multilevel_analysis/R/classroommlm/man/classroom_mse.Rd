% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/meansquarederror.R
\name{classroom_mse}
\alias{classroom_mse}
\title{Calculate the mean squared error}
\usage{
classroom_mse(
  real_data,
  simulated_data,
  mlwinpath,
  output_file_prefix,
  level = 1
)
}
\arguments{
\item{real_data}{a Data Frame containing the actual (real) data with headings:
start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)}

\item{simulated_data}{a Data Frame containing the simulated data with headings:
start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)}

\item{mlwinpath}{the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')}

\item{output_file_prefix}{the path and file prefix to output the full and null models.
e.g. if passed '~/classroom_abm/classes_output/2021-09-06_output', will create files:
'~/classroom_abm/classes_output/2021-09-06_output_null_model.csv' and
'~/classroom_abm/classes_output/2021-09-06_output_full_model.csv'}

\item{level}{if 1 (default), runs \code{\link{simple_full_model}}; if 2,
runs \code{\link{full_model_no_deprivation}} otherwise runs
\code{\link{full_model}}}
}
\value{
the mean squared error score
}
\description{
This function calculates the mean squared error between the given real and
simulated data frames. It runs the null and full models over each data frame,
then scales the means, variances and coefficients, before calculating the
mean squared error of the result.
}
