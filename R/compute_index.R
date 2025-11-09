source(file.path("R", "utils.R"))
source(file.path("R", "compute_peers.R"))

measure_component_map <- function() {
  mapping <- c(
    median_age = "demographic",
    poverty_rate = "other_prosperity",
    households_with_children_growth = "growth",
    hs_attainment = "education_skill",
    associates_attainment = "education_skill",
    bachelors_attainment = "education_skill",
    labor_force_participation = "education_skill",
    telecommuters_share = "economic_opportunity",
    dir_income_share = "other_prosperity",
    dir_income_growth = "growth",
    nonfarm_proprietor_income = "other_prosperity",
    total_employment_growth = "growth",
    private_employment = "growth",
    private_wage_growth = "growth",
    entrepreneurial_activity = "economic_opportunity",
    nonfarm_proprietors_per_capita = "economic_opportunity",
    employer_establishments_per_capita = "economic_opportunity",
    nonemployer_worker_share = "economic_opportunity",
    industry_diversity = "economic_opportunity",
    occupation_diversity = "economic_opportunity",
    personal_income_volatility = "other_prosperity",
    life_expectancy = "other_prosperity",
    dependency_ratio = "demographic",
    population_change = "demographic",
    millennial_genz_change = "demographic",
    percent_nonwhite = "demographic",
    percent_hispanic = "demographic",
    knowledge_workers_share = "education_skill",
    broadband_access = "infrastructure_cost",
    interstate_presence = "infrastructure_cost",
    weekly_wage_rate = "infrastructure_cost",
    top_marginal_tax_rate = "infrastructure_cost",
    four_year_colleges = "infrastructure_cost",
    opportunity_zones = "infrastructure_cost",
    commute_time = "quality_of_life",
    housing_pre_1960 = "quality_of_life",
    relative_weekly_wage = "quality_of_life",
    healthcare_access = "quality_of_life",
    climate_amenities = "quality_of_life",
    national_parks_access = "quality_of_life",
    violent_crime_rate = "quality_of_life",
    property_crime_rate = "quality_of_life",
    nonprofit_density = "social_capital",
    volunteer_hours = "social_capital",
    volunteer_rate = "social_capital",
    voter_turnout = "social_capital",
    tree_city_share = "social_capital"
  )
  tibble::tibble(
    measure = names(mapping),
    component = unname(mapping)
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
