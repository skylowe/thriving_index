#!/usr/bin/env Rscript
source(file.path("R", "utils.R"))
source(file.path("R", "fetch_census_acs.R"))

ti_fetch_all <- function(year = 2020) {
  paths <- ti_paths()
  dir.create(paths$data_raw, showWarnings = FALSE, recursive = TRUE)

  message("[ti] Fetching ACS median age...")
  median_age <- acs_fetch_median_age(year)
  ti_write_csv(median_age, file.path(paths$data_raw, sprintf("acs_median_age_%s.csv", year)))

  message("[ti] Fetching ACS education attainment...")
  education <- acs_fetch_education_rates(year)
  ti_write_csv(education, file.path(paths$data_raw, sprintf("acs_education_%s.csv", year)))

  message("[ti] Fetching labor force participation...")
  labor <- acs_fetch_labor_force(year)
  ti_write_csv(labor, file.path(paths$data_raw, sprintf("acs_lfp_%s.csv", year)))

  message("[ti] Fetching poverty statistics...")
  poverty <- acs_fetch_poverty(year)
  ti_write_csv(poverty, file.path(paths$data_raw, sprintf("acs_poverty_%s.csv", year)))

  message("[ti] Fetching households with children (current)...")
  hh_children_current <- acs_fetch_households_children(year)
  ti_write_csv(hh_children_current, file.path(paths$data_raw, sprintf("acs_households_children_%s.csv", year)))

  base_year <- 2015
  message(sprintf("[ti] Fetching households with children (base %s)...", base_year))
  hh_children_base <- acs_fetch_households_children(base_year)
  ti_write_csv(hh_children_base, file.path(paths$data_raw, sprintf("acs_households_children_%s.csv", base_year)))

  message("[ti] Fetching telecommuter data...")
  telecommuters <- acs_fetch_telecommuters(year)
  ti_write_csv(telecommuters, file.path(paths$data_raw, sprintf("acs_telecommuters_%s.csv", year)))

  invisible(list(
    median_age = median_age,
    education = education,
    labor = labor,
    poverty = poverty,
    hh_children_current = hh_children_current,
    hh_children_base = hh_children_base,
    telecommuters = telecommuters
  ))
}

if (sys.nframe() == 0) {
  ti_fetch_all()
}

