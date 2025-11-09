#!/usr/bin/env Rscript
source(file.path("R", "utils.R"))
source(file.path("R", "compute_measures_demo.R"))
source(file.path("R", "compute_measures_education.R"))
source(file.path("R", "compute_measures_growth.R"))
source(file.path("R", "compute_index.R"))

ti_build_indexes <- function(year = 2020) {
  paths <- ti_paths()
  dir.create(paths$data_intermediate, showWarnings = FALSE, recursive = TRUE)
  dir.create(paths$data_processed, showWarnings = FALSE, recursive = TRUE)

  message("[ti] Computing measures...")
  measures <- dplyr::bind_rows(
    compute_median_age(year),
    compute_poverty_rate(year),
    compute_households_with_children_growth(current_year = year, base_year = 2015),
    compute_education_attainment(year),
    compute_labor_force_participation(year),
    compute_telecommuters_share(year)
  )

  ti_write_csv(measures, file.path(paths$data_intermediate, sprintf("measures_%s.csv", year)))

  message("[ti] Building index scores...")
  results <- compute_index_scores(measures)

  ti_write_csv(results$standardized_measures, file.path(paths$data_processed, sprintf("standardized_measures_%s.csv", year)))
  ti_write_csv(results$components, file.path(paths$data_processed, sprintf("component_scores_%s.csv", year)))
  ti_write_csv(results$aggregate, file.path(paths$data_processed, sprintf("thriving_index_%s.csv", year)))

  invisible(results)
}

if (sys.nframe() == 0) {
  ti_build_indexes()
}

