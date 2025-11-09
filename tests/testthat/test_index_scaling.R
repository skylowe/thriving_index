test_that('z-score converts to index scale correctly', {
  values <- c(1, 2, 3)
  z <- ti_zscore(values)
  idx <- 100 + 100 * z
  expect_equal(mean(z), 0)
  expect_equal(length(idx), 3)
})

