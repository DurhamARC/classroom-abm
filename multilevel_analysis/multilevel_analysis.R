library(R2MLwiN)

# Load data and remove any rows with missing/non-numeric values
original_pupil_data <- read.csv('../classes_input/test_input.csv')
numeric_pupil_data = suppressWarnings(transform(original_pupil_data, end_maths=as.numeric(end_maths)))
pupil_data = numeric_pupil_data[complete.cases(numeric_pupil_data),]
summary(pupil_data)
sorted_pupil_data <- pupil_data[order(pupil_data$class_id),]

# Create and summarise null model
null_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id)
null_model <- runMLwiN(null_formula, data=sorted_pupil_data)

null_model.percentage_variance_class_level = null_model@RP[["RP2_var_Intercept"]] * 100 / 
  (null_model@RP[["RP1_var_Intercept"]] + null_model@RP[["RP2_var_Intercept"]])

null_model.summary_table <- data.frame(
  coef(null_model),
  sqrt(diag(vcov(null_model)))
)
names(null_model.summary_table) <- c("Actual", "Std Err")
rownames(null_model.summary_table) = c('Constant (mean)', 'Class variance', 'Pupil variance')
null_model.summary_table <- rbind(null_model.summary_table, 
                                  "% of variance at class level" = c(
                                    null_model.percentage_variance_class_level,
                                    NA
                                  ))

# Create and summarise full model
full_formula <- end_maths ~ 1 + (1 | class_id) + (1 | student_id) + start_maths + Inattentiveness + Ability + Deprivation
full_model <- runMLwiN(full_formula, data=sorted_pupil_data)
full_model.percentage_variance_class_level = full_model@RP[["RP2_var_Intercept"]] * 100 / 
  (full_model@RP[["RP1_var_Intercept"]] + full_model@RP[["RP2_var_Intercept"]])


full_model.summary_table <- data.frame(
  coef(full_model),
  sqrt(diag(vcov(full_model)))
)
names(full_model.summary_table) <- c("Actual", "Std Err")
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

print("Null model:")
print(round(null_model.summary_table,2))

print("Full model:")
print(round(full_model.summary_table,2))
