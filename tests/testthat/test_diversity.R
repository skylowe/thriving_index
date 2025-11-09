test_that('diversity similarity returns 1 for identical distributions', {
  dist <- c(a = 0.4, b = 0.6)
  expect_equal(diversity_similarity(dist, dist), 1)
})

test_that('diversity similarity decreases with divergence', {
  a <- c(a = 0.9, b = 0.1)
  b <- c(a = 0.1, b = 0.9)
  expect_lt(diversity_similarity(a, b), 0.5)
})
