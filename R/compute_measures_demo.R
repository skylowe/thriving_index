source(file.path("R", "utils.R"))
source(file.path("R", "fetch_census_acs.R"))

compute_median_age <- function(year = 2020) {
  df <- acs_fetch_median_age(year) %>%
    dplyr::mutate(value = as.numeric(.data[["S0101_C01_032E"]]))
  df %>%
    ti_assign_regions(county_col = "county_name") %>%
    ti_region_summarise(value_col = "value", measure_id = "median_age", year = year)
}

compute_poverty_rate <- function(year = 2020) {
  df <- acs_fetch_poverty(year) %>%
    dplyr::mutate(value = as.numeric(.data[["S1701_C03_001E"]]))
  df %>%
    ti_assign_regions(county_col = "county_name") %>%
    ti_region_summarise(value_col = "value", measure_id = "poverty_rate", year = year)
}

compute_dependency_ratio <- function(year = 2020) {
  df <- acs_fetch_dependency(year) %>%
    dplyr::mutate(
      total = as.numeric(.data[["S0101_C01_001E"]]),
      under18 = as.numeric(.data[["S0101_C01_022E"]]),
      over65 = as.numeric(.data[["S0101_C01_030E"]]),
      dependents = under18 + over65,
      working_age = total - dependents,
      value = dplyr::if_else(working_age > 0, dependents / working_age, NA_real_)
    )
  df %>%
    ti_assign_regions(county_col = "county_name") %>%
    ti_region_summarise(value_col = "value", measure_id = "dependency_ratio", year = year)
}

compute_percent_nonwhite <- function(year = 2020) {
  df <- acs_fetch_race(year) %>%
    dplyr::mutate(
      total = as.numeric(.data[["B02001_001E"]]),
      white = as.numeric(.data[["B02001_002E"]]),
      value = dplyr::if_else(total > 0, 1 - (white / total), NA_real_)
    )
  df %>%
    ti_assign_regions(county_col = "NAME") %>%
    ti_region_summarise(value_col = "value", measure_id = "percent_nonwhite", year = year)
}

compute_percent_hispanic <- function(year = 2020) {
  df <- acs_fetch_hispanic(year) %>%
    dplyr::mutate(
      total = as.numeric(.data[["B03003_001E"]]),
      hispanic = as.numeric(.data[["B03003_003E"]]),
      value = dplyr::if_else(total > 0, hispanic / total, NA_real_)
    )
  df %>%
    ti_assign_regions(county_col = "NAME") %>%
    ti_region_summarise(value_col = "value", measure_id = "percent_hispanic", year = year)
}

compute_households_with_children_growth <- function(current_year = 2020, base_year = 2015) {
  current <- acs_fetch_households_children(current_year) %>%
    dplyr::mutate(
      total = as.numeric(.data[["S1101_C01_001E"]]),
      households_children = as.numeric(.data[["S1101_C01_010E"]]),
      share = households_children / dplyr::if_else(total == 0, NA_real_, total)
    ) %>%
    dplyr::select(county_fips, county_name, share_current = share)

  base <- acs_fetch_households_children(base_year) %>%
    dplyr::mutate(
      total = as.numeric(.data[["S1101_C01_001E"]]),
      households_children = as.numeric(.data[["S1101_C01_010E"]]),
      share = households_children / dplyr::if_else(total == 0, NA_real_, total)
    ) %>%
    dplyr::select(county_fips, share_base = share)

  combined <- current %>%
    dplyr::left_join(base, by = "county_fips") %>%
    dplyr::mutate(
      growth = (share_current / share_base) - 1
    )

  combined %>%
    ti_assign_regions(county_col = "county_name") %>%
    ti_region_summarise(value_col = "growth", measure_id = "households_with_children_growth", year = current_year)
}
