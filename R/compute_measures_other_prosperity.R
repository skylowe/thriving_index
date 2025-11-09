source(file.path("R", "utils.R"))
source(file.path("R", "fetch_bea.R"))

compute_nonfarm_proprietor_income <- function(year = 2020) {
  df <- bea_fetch_cainc5n(line_codes = c(72), years = year) %>%
    dplyr::filter(line_number == 72) %>%
    dplyr::rename(value = value)
  assigned <- ti_assign_regions_by_fips(df, fips_col = "county_fips")
  ti_region_summarise(assigned, value_col = "value", measure_id = "nonfarm_proprietor_income", year = year, agg = "sum")
}

compute_dir_income_share <- function(year = 2020) {
  df <- bea_fetch_cainc5n(line_codes = c(10, 46), years = year) %>%
    dplyr::mutate(metric = dplyr::case_when(
      line_number == 10 ~ "personal_income",
      line_number == 46 ~ "dir_income",
      TRUE ~ NA_character_
    )) %>%
    tidyr::drop_na(metric)

  wide <- df %>%
    tidyr::pivot_wider(names_from = metric, values_from = value)

  assigned <- ti_assign_regions_by_fips(wide, fips_col = "county_fips")

  assigned %>%
    dplyr::group_by(region_id, region_name) %>%
    dplyr::summarise(
      dir_income = sum(dir_income, na.rm = TRUE),
      personal_income = sum(personal_income, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      value = dplyr::if_else(personal_income > 0, dir_income / personal_income, NA_real_),
      measure = "dir_income_share",
      year = year
    ) %>%
    dplyr::select(region_id, region_name, value, measure, year)
}

compute_dir_income_growth <- function(current_year = 2020, base_year = 2017) {
  df <- bea_fetch_cainc5n(line_codes = c(46), years = c(base_year, current_year))

  wide <- df %>%
    dplyr::filter(line_number == 46) %>%
    tidyr::pivot_wider(names_from = year, values_from = value, names_prefix = "year_")

  base_col <- paste0("year_", base_year)
  current_col <- paste0("year_", current_year)

  wide <- wide %>%
    dplyr::mutate(
      growth = dplyr::if_else(.data[[base_col]] > 0, (.data[[current_col]] - .data[[base_col]]) / .data[[base_col]], NA_real_),
      weight = .data[[base_col]]
    )

  assigned <- ti_assign_regions_by_fips(wide, fips_col = "county_fips")
  ti_region_summarise(assigned, value_col = "growth", measure_id = "dir_income_growth", year = current_year, weight_col = "weight", agg = "weighted_mean")
}
