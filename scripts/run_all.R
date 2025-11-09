#!/usr/bin/env Rscript
source(file.path("scripts", "fetch_all.R"))
source(file.path("scripts", "build_indexes.R"))
source(file.path("scripts", "validate.R"))

run_all <- function(year = 2020) {
  message("[ti] Starting full pipeline (year=", year, ")...")
  ti_fetch_all(year)
  ti_build_indexes(year)
  ti_validate_outputs(year)
  message("[ti] Pipeline complete.")
}

if (sys.nframe() == 0) {
  run_all()
}

