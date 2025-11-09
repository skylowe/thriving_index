source(file.path("R", "utils.R"))
source(file.path("R", "fetch_census_acs.R"))

compute_education_attainment <- function(year = 2020) {
  df <- acs_fetch_education_rates(year)
  df <- df %>%
    dplyr::mutate(
      hs = as.numeric(.data[["S1501_C02_009E"]]),
      associates = as.numeric(.data[["S1501_C02_011E"]]),
      bachelors = as.numeric(.data[["S1501_C02_012E"]])
    )

  assigned <- ti_assign_regions(df, county_col = "county_name")

  list(
    ti_region_summarise(assigned, value_col = "hs", measure_id = "hs_attainment", year = year),
    ti_region_summarise(assigned, value_col = "associates", measure_id = "associates_attainment", year = year),
    ti_region_summarise(assigned, value_col = "bachelors", measure_id = "bachelors_attainment", year = year)
  ) %>%
    dplyr::bind_rows()
}

compute_labor_force_participation <- function(year = 2020) {
  df <- acs_fetch_labor_force(year) %>%
    dplyr::mutate(value = as.numeric(.data[["DP03_0002PE"]]))
  df %>%
    ti_assign_regions(county_col = "county_name") %>%
    ti_region_summarise(value_col = "value", measure_id = "labor_force_participation", year = year)
}

