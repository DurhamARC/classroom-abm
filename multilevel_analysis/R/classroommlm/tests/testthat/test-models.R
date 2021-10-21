test_that("null model works", {
  expected_null_model = data.frame(
    "Actual"=c(39.5, 23.9, 79.0, 23.2),
    "StdErr"=c(0.114, 0.858, 0.563, NA),
    row.names=c("Constant (mean)", "Class variance", "Pupil variance",
                "% of variance at class level")
  )
  expect_equal(null_model(pupil_data, mlnscript_path), expected_null_model, tolerance=0.01)
})

test_that("full model works", {
  expected_full_model = data.frame(
    "Actual"=c(30.74, 0.58, -1.41, 2.50, -0.12, 19.4, 32.8, 36.4),
    "StdErr"=c(0.217, 0.008, 0.032, 0.068, 0.027, 0.643, 0.233, NA),
    row.names=c("Constant (mean)", "Start maths", "Inattention", "Ability",
                "Deprivation", "Class variance", "Pupil variance",
                "% of variance at class level")
  )
  expect_equal(full_model(pupil_data, mlnscript_path), expected_full_model, tolerance=0.01)
})

test_that("simple full model works", {
  expected_simple_full_model = data.frame(
    "Actual"=c(22.54, 0.899, -0.18, 19.0, 35.1, 35.0),
    "StdErr"=c(0.338, 0.009, 0.059, 1.36, 0.537, NA),
    row.names=c("Constant (mean)", "Start maths",
                "Deprivation", "Class variance", "Pupil variance",
                "% of variance at class level")
  )
  expect_equal(simple_full_model(sampled_pupil_data, mlnscript_path), expected_simple_full_model, tolerance=0.01)
})
