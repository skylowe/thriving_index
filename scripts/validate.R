#!/usr/bin/env Rscript
source(file.path("R", "utils.R"))

ti_validate_outputs <- function(year = 2020) {
  paths <- ti_paths()
  files <- list(
    measures = file.path(paths$data_intermediate, sprintf("measures_%s.csv", year)),
    standardized = file.path(paths$data_processed, sprintf("standardized_measures_%s.csv", year)),
    components = file.path(paths$data_processed, sprintf("component_scores_%s.csv", year)),
    aggregate = file.path(paths$data_processed, sprintf("thriving_index_%s.csv", year))
  )

  for (name in names(files)) {
    if (!file.exists(files[[name]])) {
      stop(sprintf("Validation failed: %s not found", files[[name]]))
    }
  }

  aggregate <- readr::read_csv(files$aggregate, show_col_types = FALSE)
  if (nrow(aggregate) == 0) {
    stop("Validation failed: aggregate results are empty")
  }
  if (any(!is.finite(aggregate$thriving_index))) {
    stop("Validation failed: aggregate index contains non-finite values")
  }

  message("[ti] Validation passed for year ", year)
  invisible(TRUE)
}

if (sys.nframe() == 0) {
  ti_validate_outputs()
}

