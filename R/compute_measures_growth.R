source(file.path("R", "utils.R"))
source(file.path("R", "fetch_census_acs.R"))

compute_telecommuters_share <- function(year = 2020) {
  df <- acs_fetch_telecommuters(year) %>%
    dplyr::mutate(
      total_workers = as.numeric(.data[["B08128_001E"]]),
      worked_home = as.numeric(.data[["B08128_061E"]]),
      self_inc = as.numeric(.data[["B08128_064E"]]),
      self_not_inc = as.numeric(.data[["B08128_069E"]]),
      unpaid = as.numeric(.data[["B08128_070E"]]),
      eligible = pmax(worked_home - self_inc - self_not_inc - unpaid, 0),
      share = dplyr::if_else(total_workers > 0, eligible / total_workers, NA_real_)
    )

  df %>%
    ti_assign_regions(county_col = "county_name") %>%
    ti_region_summarise(value_col = "share", measure_id = "telecommuters_share", year = year)
}

compute_commute_time <- function(year = 2020) {
  df <- acs_fetch_commute(year) %>%
    dplyr::mutate(value = as.numeric(.data[["S0801_C01_046E"]]))
  df %>%
    ti_assign_regions(county_col = "NAME") %>%
    ti_region_summarise(value_col = "value", measure_id = "commute_time", year = year)
}

compute_housing_pre1960 <- function(year = 2020) {
  df <- acs_fetch_housing_age(year) %>%
    dplyr::mutate(
      pct = as.numeric(.data[["DP04_0024PE"]]) + as.numeric(.data[["DP04_0025PE"]]) + as.numeric(.data[["DP04_0026PE"]])
    )
  df %>%
    ti_assign_regions(county_col = "NAME") %>%
    ti_region_summarise(value_col = "pct", measure_id = "housing_pre_1960", year = year)
}
