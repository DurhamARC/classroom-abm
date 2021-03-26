library(R2MLwiN)

# Load data and remove any rows with missing/non-numeric values
original_pupil_data <- read.csv('../classes_input/test_input.csv')
numeric_pupil_data = suppressWarnings(transform(original_pupil_data, end_maths=as.numeric(end_maths)))
pupil_data = numeric_pupil_data[complete.cases(numeric_pupil_data),]
summary(pupil_data)
sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]

null_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id)
null_model <- runMLwiN(null_formula, data=sorted_pupil_data)

null_percentage_variance_class_level = null_model@RP[["RP2_var_Intercept"]] * 100 / 
  (null_model@RP[["RP1_var_Intercept"]] + null_model@RP[["RP2_var_Intercept"]])
null_summary_table <- data.frame(
  'Actual'=c(null_model@FP[["FP_Intercept"]], 
             null_model@RP[["RP2_var_Intercept"]], 
             null_model@RP[["RP1_var_Intercept"]],
             null_percentage_variance_class_level),
  row.names = c('Constant (mean)', 'Class variance', 'Pupil variance', '% variance at class level')
)

full_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Inattentiveness + Ability + Deprivation
full_model <- runMLwiN(full_formula, data=sorted_pupil_data)
full_percentage_variance_class_level = full_model@RP[["RP2_var_Intercept"]] * 100 / 
  (full_model@RP[["RP1_var_Intercept"]] + full_model@RP[["RP2_var_Intercept"]])
full_summary_table <- data.frame(
  'Actual'=c(full_model@FP[["FP_Intercept"]],
             full_model@FP[["FP_start_maths"]],
             full_model@FP[["FP_Inattentiveness"]],
             full_model@FP[["FP_Ability"]],
             full_model@FP[["FP_Deprivation"]],
             full_model@RP[["RP2_var_Intercept"]], 
             full_model@RP[["RP1_var_Intercept"]],
             full_percentage_variance_class_level),
  row.names = c('Constant (mean)',
                'Start maths',
                'Inattention',
                'Ability',
                'Deprivation',
                'Class variance', 
                'Pupil variance', 
                '% variance at class level')
)

print("Null model:")
print(null_summary_table)

print("Full model:")
print(full_summary_table)
