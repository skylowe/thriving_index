test_that('region summarise averages counties', {
  stub <- tibble::tibble(
    county_name = c('Madison', 'Pierce'),
    value = c(1, 3)
  ) %>%
    ti_assign_regions(county_col = 'county_name')
  result <- ti_region_summarise(stub, value_col = 'value', measure_id = 'demo', year = 2020)
  expect_true(any(abs(result$value - 2) < 1e-6))
})
