% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/models.R
\name{simple_full_model}
\alias{simple_full_model}
\title{Create a simplified full model}
\usage{
simple_full_model(pupil_data, mlwinpath)
}
\arguments{
\item{pupil_data}{a Data Frame with headings:
start_maths,student_id,class_id,N_in_class,Ability,Inattentiveness,hyper_impulsive,Deprivation,end_maths)}

\item{mlwinpath}{the path where mlnscript is installed (e.g. '/opt/mln/mlnscript')}
}
\value{
a Data Frame containing the summary data for the full model
}
\description{
This function creates a simplified full model for the given pupil data, not including
Ability or Inattentiveness
}
