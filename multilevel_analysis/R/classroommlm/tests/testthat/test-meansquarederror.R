test_that("mse works", {
  pupil_data <- read.csv("../../../../../classes_input/test_input.csv")
  pupil_data <- suppressWarnings(transform(pupil_data, end_maths=as.numeric(end_maths)))
  pupil_data <- pupil_data[complete.cases(pupil_data),]

  # Mean squared error between real data and  itself should be 0
  expect_equal(classroom_mse(pupil_data, pupil_data, '/opt/mln/mlnscript'), 0)

  # If we add 1 to each Maths score the mean squared error will increase
  pupil_data_amended <- transform(pupil_data, end_maths=end_maths+1)
  expect_equal(classroom_mse(pupil_data, pupil_data_amended, '/opt/mln/mlnscript'), 0.2)

  # If we add 10 to each Maths score the mean squared error will increase further
  pupil_data_amended <- transform(pupil_data, end_maths=end_maths+10)
  expect_equal(classroom_mse(pupil_data, pupil_data_amended, '/opt/mln/mlnscript'), 20)
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
