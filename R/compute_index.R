source(file.path("R", "utils.R"))
source(file.path("R", "compute_peers.R"))

measure_component_map <- function() {
  tibble::tibble(
    measure = c(
      "median_age",
      "poverty_rate",
      "households_with_children_growth",
      "hs_attainment",
      "associates_attainment",
      "bachelors_attainment",
      "labor_force_participation",
      "telecommuters_share",
      "dir_income_share",
      "dir_income_growth",
      "nonfarm_proprietor_income"
    ),
    component = c(
      "demographic",
      "other_prosperity",
      "growth",
      "education_skill",
      "education_skill",
      "education_skill",
      "education_skill",
      "economic_opportunity",
      "other_prosperity",
      "growth",
      "other_prosperity"
    )
  )
}

compute_index_scores <- function(measures_df) {
  peer_groups <- compute_peer_groups()
  mapped <- measures_df %>%
    dplyr::left_join(peer_groups, by = "region_id") %>%
    dplyr::mutate(peer_group = dplyr::coalesce(peer_group, region_id))

  standardized <- ti_standardize(mapped, value_col = "value", group_cols = c("measure", "peer_group"))

  component_map <- measure_component_map()
  components <- standardized %>%
    dplyr::left_join(component_map, by = "measure") %>%
    dplyr::filter(!is.na(component)) %>%
    dplyr::group_by(region_id, region_name, component, year) %>%
    dplyr::summarise(component_index = mean(index_value, na.rm = TRUE), .groups = "drop")

  aggregate <- components %>%
    dplyr::group_by(region_id, region_name, year) %>%
    dplyr::summarise(thriving_index = mean(component_index, na.rm = TRUE), .groups = "drop")

  list(
    standardized_measures = standardized,
    components = components,
    aggregate = aggregate
  )
}
