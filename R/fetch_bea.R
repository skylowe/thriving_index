source(file.path("R", "utils.R"))
bea_cache <- new.env(parent = emptyenv())
bea_throttle <- function(iter = 0) {
  if (!ti_offline()) {
    Sys.sleep(0.15 + iter * 0.1)
  }
}

bea_request <- function(params, retries = 5) {
  for (i in seq_len(retries)) {
    bea_throttle(i - 1)
    resp <- httr::GET("https://apps.bea.gov/api/data", query = params)
    if (httr::http_error(resp)) {
      if (i == retries) {
        stop(sprintf("BEA request failed: %s", httr::content(resp, "text", encoding = "UTF-8")))
      }
      next
    }
    json <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
    err <- json$BEAAPI$Results$Error
    if (!is.null(err)) {
      if (err$APIErrorCode == "7" && i < retries) {
        Sys.sleep(1.5 * i)
        next
      }
      stop(sprintf("BEA API error (%s): %s", err$APIErrorCode, err$APIErrorDescription))
    }
    return(json)
  }
  stop("BEA request failed after retries")
}

bea_fetch_cainc5n <- function(line_codes, years, counties = NULL) {
  if (is.null(counties)) {
    counties <- ti_region_config() %>%
      dplyr::distinct(county_fips, county_clean) %>%
      dplyr::filter(!is.na(county_fips))
  }
  purrr::map_dfr(line_codes, function(line_code) {
    if (ti_offline()) {
      return(dplyr::bind_rows(purrr::map(counties$county_fips, function(fips) {
        county_name <- counties$county_clean[counties$county_fips == fips][1]
        bea_fake_county(fips, county_name, line_code, years)
      })))
    }
    key <- paste(line_code, paste(years, collapse = ":"), "ALL", sep = "|")
    if (exists(key, envir = bea_cache, inherits = FALSE)) {
      data <- get(key, envir = bea_cache)
    } else {
      params <- list(
        UserID = ti_read_key("BEA_API_KEY"),
        method = "GETDATA",
        datasetname = "Regional",
        TableName = "CAINC5N",
        GeoFips = "COUNTY",
        LineCode = line_code,
        Year = paste(years, collapse = ","),
        ResultFormat = "json"
      )
      json <- bea_request(params)
      data <- json$BEAAPI$Results$Data
      assign(key, data, envir = bea_cache)
    }
    if (is.null(data)) {
      return(tibble::tibble())
    }
    tibble::as_tibble(data) %>%
      dplyr::mutate(
        county_fips = GeoFips,
        county_name = ti_clean_county_name(GeoName),
        year = as.integer(TimePeriod),
        line_code = Code,
        line_number = as.numeric(stringr::str_extract(Code, "(?<=-)\\d+$")),
        value_raw = readr::parse_number(DataValue),
        unit_mult = suppressWarnings(as.numeric(UNIT_MULT)),
        value = value_raw * (10 ^ dplyr::if_else(is.na(unit_mult), 0, unit_mult))
      ) %>%
      dplyr::filter(county_fips %in% counties$county_fips) %>%
      dplyr::select(county_fips, county_name, year, line_code, line_number, value)
  })
}

bea_fake_county <- function(fips, county_name, line_code, years) {
  grid <- expand.grid(line_code = line_code, year = years, stringsAsFactors = FALSE)
  seed_val <- sum(as.integer(charToRaw(paste(fips, line_code, collapse = ""))))
  set.seed((seed_val %% .Machine$integer.max))
  tibble::as_tibble(grid) %>%
    dplyr::mutate(
      line_code = paste0("CAINC5N-", line_code),
      line_number = as.numeric(stringr::str_extract(line_code, "(?<=-)\\d+$")),
      county_fips = fips,
      county_name = county_name,
      value = runif(dplyr::n(), min = 1e5, max = 5e5)
    ) %>%
    dplyr::select(county_fips, county_name, year, line_code, line_number, value)
}
