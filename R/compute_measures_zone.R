source(file.path("R", "utils.R"))

compute_growth_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("total_employment_growth", "total_employment_growth_2014_2017", year),
    ti_zone_measure_df("private_employment", "private_employment_2017", year),
    ti_zone_measure_df("private_wage_growth", "private_wages_per_job_growth_2014_2017", year)
  )
}

compute_opportunity_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("entrepreneurial_activity", "entrepreneurship_activity_business_births_plus_deaths_per_capita_2014_2015", year),
    ti_zone_measure_df("nonfarm_proprietors_per_capita", "nonfarm_proprietorships_per_1_000_residents_2017", year),
    ti_zone_measure_df("employer_establishments_per_capita", "private_employer_establishments_per_1_000_residents_2017", year),
    ti_zone_measure_df("nonemployer_worker_share", "share_of_workers_in_non_employer_establishments_2016", year),
    ti_zone_measure_df("industry_diversity", "industry_diversity_2017", year),
    ti_zone_measure_df("occupation_diversity", "occupational_diversity_2013_2017", year)
  )
}

compute_other_prosperity_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("personal_income_volatility", "total_personal_income_volatility_2003_2017", year),
    ti_zone_measure_df("life_expectancy", "life_expectancy_2014", year)
  )
}

compute_demographic_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("population_change", "population_change_since_2000_to_2013_2017", year),
    ti_zone_measure_df("millennial_genz_change", "millenial_and_gen_z_balance_change_09_13_to_14_18", year)
  )
}

compute_education_zone_measures <- function(year = 2020) {
  ti_zone_measure_df("knowledge_workers_share", "percent_of_knowledge_workers_2013_2017", year)
}

compute_infrastructure_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("broadband_access", "broadband_internet_access_2018", year),
    ti_zone_measure_df("interstate_presence", "presence_of_interstate_2018", year),
    ti_zone_measure_df("weekly_wage_rate", "weekly_wage_rates_q2_2018", year),
    ti_zone_measure_df("top_marginal_tax_rate", "top_marginal_personal_income_tax_rate_jan_1_2019", year),
    ti_zone_measure_df("four_year_colleges", "weighted_count_of_4_year_colleges_2019", year),
    ti_zone_measure_df("opportunity_zones", "count_of_qualified_opportunity_zones_2018", year)
  )
}

compute_quality_of_life_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("relative_weekly_wage", "weekly_wages_state_average_q2_2018", year),
    ti_zone_measure_df("healthcare_access", "health_care_practitioners_per_capita_2017", year),
    ti_zone_measure_df("climate_amenities", "natural_climate_amenities_permanent", year),
    ti_zone_measure_df("national_parks_access", "national_park_service_deisgnated_areas_2019", year),
    ti_zone_measure_df("violent_crime_rate", "violent_crime_rate_per_100_000_inhabitants_2017_fbi_ucr", year),
    ti_zone_measure_df("property_crime_rate", "property_crime_rate_per_100_000_inhabitants_2017_fbi_ucr", year)
  )
}

compute_social_capital_zone_measures <- function(year = 2020) {
  dplyr::bind_rows(
    ti_zone_measure_df("nonprofit_density", "501c3_organizations", year),
    ti_zone_measure_df("volunteer_hours", "volunteer_hours_per_resident_2015", year),
    ti_zone_measure_df("volunteer_rate", "volunteer_rate_2015", year),
    ti_zone_measure_df("voter_turnout", "voter_turnout", year),
    ti_zone_measure_df("tree_city_share", "percent_of_population_in_counties_with_tree_city_community_2018", year)
  )
}

compute_zone_based_measures <- function(year = 2020) {
  dplyr::bind_rows(
    compute_growth_zone_measures(year),
    compute_opportunity_zone_measures(year),
    compute_other_prosperity_zone_measures(year),
    compute_demographic_zone_measures(year),
    compute_education_zone_measures(year),
    compute_infrastructure_zone_measures(year),
    compute_quality_of_life_zone_measures(year),
    compute_social_capital_zone_measures(year)
  )
}
