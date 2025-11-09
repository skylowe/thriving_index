ti_is_windows <- function() {
  identical(tolower(Sys.info()["sysname"]), "windows")
}

ti_setup_libpaths <- function() {
  if (!ti_is_windows()) {
    linux_lib <- "/home/skylowe/R/x86_64-pc-linux-gnu-library/4.3.3"
    if (dir.exists(linux_lib) && !linux_lib %in% .libPaths()) {
      .libPaths(c(linux_lib, .libPaths()))
    }
  }
}

ti_setup_libpaths()

ti_require_packages <- function() {
  pkgs <- c("jsonlite", "httr", "dplyr", "purrr", "readr", "stringr", "tidyr", "yaml", "tibble", "testthat", "readxl")
  for (pkg in pkgs) {
    if (!suppressWarnings(require(pkg, character.only = TRUE, quietly = TRUE))) {
      stop(sprintf("Package '%s' is required. Install it to %s before continuing.", pkg, paste(.libPaths(), collapse = ", ")))
    }
  }
  invisible(pkgs)
}

ti_require_packages()

ti_project_root <- local({
  cached <- NULL
  function() {
    if (!is.null(cached)) {
      return(cached)
    }
    env_root <- Sys.getenv("TI_PROJECT_ROOT", "")
    if (nzchar(env_root)) {
      cached <<- normalizePath(env_root, winslash = "/", mustWork = FALSE)
      return(cached)
    }
    candidate <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
    repeat {
      cfg <- file.path(candidate, "config", "regions.yml")
      if (file.exists(cfg)) {
        cached <<- candidate
        return(candidate)
      }
      parent <- dirname(candidate)
      if (identical(parent, candidate)) {
        stop("Unable to locate project root containing config/regions.yml")
      }
      candidate <- parent
    }
  }
})

ti_paths <- function() {
  root <- ti_project_root()
  list(
    root = root,
    data_raw = file.path(root, "data", "raw"),
    data_intermediate = file.path(root, "data", "intermediate"),
    data_processed = file.path(root, "data", "processed"),
    data_fake = file.path(root, "data", "fake"),
    config_regions = file.path(root, "config", "regions.yml"),
    config_candidates = file.path(root, "config", "comparison_candidates.yml"),
    config_weights = file.path(root, "config", "weights.yml")
  )
}

ti_offline <- function() {
  tolower(Sys.getenv("THRIVING_INDEX_OFFLINE", "0")) %in% c("1", "true", "yes")
}

ti_read_key <- function(name) {
  key <- Sys.getenv(name, unset = "")
  if (!nzchar(key)) {
    message(sprintf("[ti] Warning: API key '%s' is not set; attempting request without it if allowed.", name))
  }
  key
}

ti_write_csv <- function(df, path) {
  dir.create(dirname(path), showWarnings = FALSE, recursive = TRUE)
  readr::write_csv(df, path)
  invisible(path)
}

ti_clean_county_name <- function(name) {
  name %>%
    stringr::str_replace(pattern = " County.*$", replacement = "") %>%
    stringr::str_replace(pattern = " Parish.*$", replacement = "") %>%
    stringr::str_trim() %>%
    stringr::str_to_upper()
}

ti_region_config <- function() {
  cfg_path <- ti_paths()$config_regions
  cfg <- yaml::read_yaml(cfg_path)
  regions <- purrr::imap_dfr(cfg$regions, function(region, region_id) {
    tibble::tibble(
      region_id = region_id,
      region_name = region$name,
      county = region$counties
    )
  }) %>%
    dplyr::mutate(county_clean = ti_clean_county_name(county))
  counties <- ti_county_reference() %>%
    dplyr::select(region_name = zone_name, county_clean, county_fips) %>%
    dplyr::distinct(region_name, county_clean, .keep_all = TRUE)
  regions %>% dplyr::left_join(counties, by = c("region_name", "county_clean"))
}

ti_assign_regions <- function(df, county_col = "county_name") {
  regions <- ti_region_config()
  if ("county_fips" %in% names(df)) {
    df %>%
      dplyr::mutate(county_fips = stringr::str_pad(as.character(.data$county_fips), 5, pad = "0")) %>%
      dplyr::left_join(regions %>% dplyr::select(county_fips, region_id, region_name), by = "county_fips") %>%
      dplyr::distinct(county_fips, .keep_all = TRUE)
  } else {
    df %>%
      dplyr::mutate(county_clean = ti_clean_county_name(.data[[county_col]])) %>%
      dplyr::left_join(regions, by = "county_clean") %>%
      dplyr::distinct(county_clean, .keep_all = TRUE)
  }
}

ti_assign_regions_by_fips <- function(df, fips_col = "county_fips") {
  regions <- ti_region_config() %>% dplyr::select(region_id, region_name, county_fips)
  if (!"county_fips" %in% names(df)) {
    df <- df %>% dplyr::mutate(county_fips = .data[[fips_col]])
    fips_col <- "county_fips"
  }
  df %>%
    dplyr::left_join(regions, by = setNames("county_fips", fips_col)) %>%
    dplyr::distinct(county_fips, .keep_all = TRUE)
}

ti_region_summarise <- function(df, value_col, measure_id, year, weight_col = NULL, agg = c("mean", "weighted_mean", "sum")) {
  agg <- match.arg(agg)
  if (!"region_id" %in% names(df)) {
    stop("Data must include region_id before summarising.")
  }
  df <- df %>% dplyr::filter(!is.na(region_id))
  summarised <- if (agg == "weighted_mean" && !is.null(weight_col)) {
    df %>%
      dplyr::group_by(region_id, region_name) %>%
      dplyr::summarise(value = stats::weighted.mean(.data[[value_col]], w = .data[[weight_col]], na.rm = TRUE), .groups = "drop")
  } else if (agg == "sum") {
    df %>%
      dplyr::group_by(region_id, region_name) %>%
      dplyr::summarise(value = sum(.data[[value_col]], na.rm = TRUE), .groups = "drop")
  } else {
    df %>%
      dplyr::group_by(region_id, region_name) %>%
      dplyr::summarise(value = mean(.data[[value_col]], na.rm = TRUE), .groups = "drop")
  }
  summarised %>%
    dplyr::mutate(measure = measure_id, year = year)
}

ti_zscore <- function(x) {
  if (all(is.na(x))) return(rep(NA_real_, length(x)))
  if (length(stats::na.omit(x)) <= 1) {
    return(rep(0, length(x)))
  }
  sd_x <- stats::sd(x, na.rm = TRUE)
  if (isTRUE(all.equal(sd_x, 0))) {
    return(rep(0, length(x)))
  }
  (x - mean(x, na.rm = TRUE)) / sd_x
}

ti_standardize <- function(df, value_col = "value", group_cols = c("measure", "peer_group")) {
  df %>%
    dplyr::group_by(dplyr::across(all_of(group_cols))) %>%
    dplyr::mutate(z = ti_zscore(.data[[value_col]]), index_value = 100 + 100 * z) %>%
    dplyr::ungroup()
}

ti_component_weights <- function() {
  cfg <- yaml::read_yaml(ti_paths()$config_weights)
  list(
    component = cfg$components,
    measures = cfg$measures
  )
}

ti_workbook_path <- function() {
  path <- file.path(ti_project_root(), "Thriving_Index_Calculations.xlsx")
  if (!file.exists(path)) {
    stop("Workbook Thriving_Index_Calculations.xlsx not found at project root")
  }
  path
}

ti_clean_colnames <- function(cols) {
  cols <- tolower(cols)
  cols <- gsub("[^a-z0-9]+", "_", cols)
  cols <- gsub("^_+|_+$", "", cols)
  cols <- gsub("__+", "_", cols)
  cols
}

ti_zone_table <- local({
  cache <- NULL
  function() {
    if (!is.null(cache)) return(cache)
    raw <- readxl::read_excel(ti_workbook_path(), sheet = "ZONE TABLES", skip = 1)
    names(raw) <- ti_clean_colnames(names(raw))
    raw <- raw %>%
      dplyr::mutate(
        zone_name = stringr::str_trim(zone_name),
        zone_group = stringr::str_trim(zone_group)
      )
    cache <<- raw
    raw
  }
})

ti_zone_lookup <- local({
  cache <- NULL
  function() {
    if (!is.null(cache)) return(cache)
    df <- ti_zone_table() %>%
      dplyr::select(zone_name, zone = zone, zone_group) %>%
      dplyr::mutate(zone_number = readr::parse_number(zone)) %>%
      dplyr::filter(!is.na(zone_number))
    cache <<- df
    df
  }
})

ti_county_reference <- local({
  cache <- NULL
  function() {
    if (!is.null(cache)) return(cache)
    path <- ti_workbook_path()
    df <- readxl::read_excel(path, sheet = "RAW DATA (EDITS HERE ONLY)", range = "A3:D900", col_names = c("fips", "county", "state", "zone_label"))
    df <- df %>%
      dplyr::filter(state == "Nebraska", !is.na(fips)) %>%
      dplyr::mutate(
        county_fips = stringr::str_pad(as.integer(fips), 5, pad = "0"),
        county_clean = ti_clean_county_name(county),
        zone_number = readr::parse_number(zone_label)
      ) %>%
      dplyr::left_join(ti_zone_lookup() %>% dplyr::select(zone_number, zone_name), by = "zone_number", relationship = "many-to-many") %>%
      dplyr::mutate(zone_name = stringr::str_trim(zone_name)) %>%
      dplyr::distinct(county_fips, .keep_all = TRUE)
    cache <<- df
    df
  }
})

ti_region_zone_data <- local({
  cache <- NULL
  function() {
    if (!is.null(cache)) return(cache)
    regions <- ti_region_config() %>% dplyr::distinct(region_id, region_name)
    zone <- ti_zone_table() %>% dplyr::rename(region_name = zone_name)
    joined <- regions %>% dplyr::left_join(zone, by = "region_name") %>% dplyr::distinct(region_id, region_name, .keep_all = TRUE)
    cache <<- joined
    joined
  }
})

ti_zone_column <- function(column_name) {
  data <- ti_region_zone_data()
  if (!column_name %in% names(data)) {
    stop(sprintf("Column '%s' not found in zone table", column_name))
  }
  data %>%
    dplyr::select(region_id, region_name, value = dplyr::all_of(column_name))
}

ti_zone_measure_df <- function(measure_id, column_name, year = 2020) {
  ti_zone_column(column_name) %>%
    dplyr::mutate(measure = measure_id, year = year)
}
