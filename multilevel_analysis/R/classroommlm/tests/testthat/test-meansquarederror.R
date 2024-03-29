test_that("mse works", {
  output_prefix <- file.path(getwd(),"test")
  null_path <- paste(output_prefix, "_null_model.csv", sep="")
  full_path <- paste(output_prefix, "_full_model.csv", sep="")
  expect_false(file.exists(null_path))
  expect_false(file.exists(full_path))
  # Mean squared error between real data and  itself should be 0
  expect_equal(classroom_mse(pupil_data, pupil_data, mlnscript_path, output_prefix), 0)

  # Model outputs should be created
  browser()
  expect_true(file.exists(null_path))
  expect_true(file.exists(full_path))

  # If we add 1 to each Maths score the mean squared error will increase
  pupil_data_amended <- transform(pupil_data, end_maths=end_maths+1)
  expect_equal(classroom_mse(pupil_data, pupil_data_amended, mlnscript_path, output_prefix), 0.2)

  # If we add 10 to each Maths score the mean squared error will increase further
  pupil_data_amended <- transform(pupil_data, end_maths=end_maths+10)
  expect_equal(classroom_mse(pupil_data, pupil_data_amended, mlnscript_path, output_prefix), 20)

  file.remove(null_path)
  file.remove(full_path)
})

test_that("simple mse works", {
  output_prefix <- file.path(getwd(),"test")

  # Mean squared error between real data and  itself should be 0
  expect_equal(classroom_mse(pupil_data, pupil_data, mlnscript_path, output_prefix, TRUE), 0)

  # If we add 1 to each Maths score the mean squared error will increase
  pupil_data_amended <- transform(pupil_data, end_maths=end_maths+1)
  expect_equal(classroom_mse(pupil_data, pupil_data_amended, mlnscript_path, output_prefix, TRUE), 0.2)

  # If we add 10 to each Maths score the mean squared error will increase further
  pupil_data_amended <- transform(pupil_data, end_maths=end_maths+10)
  expect_equal(classroom_mse(pupil_data, pupil_data_amended, mlnscript_path, output_prefix, TRUE), 20)
})

test_that("scaling works as expected", {

  # Simple values
  expect_equal(
    scaled_values(
      1, 4, 9, 1,
      c(1, 2, 3),
      16,
      25,
      c(4, 5, 6)
    ),
    c(1, 4, 6, 1, 8, 20, 36, 8, 10)
  )

  # Values from example spreadsheet
  expect_equal(
    scaled_values(
      31.4,
      46.4,
      128.9,
      14.1,
      c(0.99, -1.23, 1.7, -0.07),
      27.6,
      50.1,
      c(8.07, 1.04, 0.9, 1.36)
    ),
    c(
      31.4,
      13.6,
      22.7,
      14.1,
      15.98,
      -2.56,
      3.37,
      -0.19,
      10.5,
      14.2
    ),
    tolerance=0.01
  )
})
