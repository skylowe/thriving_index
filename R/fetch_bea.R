source(file.path("R", "utils.R"))

bea_fetch_cainc5n <- function(line_codes, years, counties = NULL) {
  if (is.null(counties)) {
    counties <- ti_region_config() %>%
      dplyr::distinct(county_fips, county_clean) %>%
      dplyr::filter(!is.na(county_fips))
  }
  purrr::map_dfr(counties$county_fips, function(fips) {
    county_name <- counties$county_clean[counties$county_fips == fips][1]
    if (ti_offline()) {
      return(bea_fake_county(fips, county_name, line_codes, years))
    }
    params <- list(
      UserID = ti_read_key("BEA_API_KEY"),
      method = "GETDATA",
      datasetname = "Regional",
      TableName = "CAINC5N",
      GeoFips = fips,
      LineCode = paste(line_codes, collapse = ","),
      Year = paste(years, collapse = ","),
      ResultFormat = "json"
    )
    resp <- httr::GET("https://apps.bea.gov/api/data", query = params)
    if (httr::http_error(resp)) {
      stop(sprintf("BEA request failed for county %s: %s", fips, httr::content(resp, "text", encoding = "UTF-8")))
    }
    json <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
    data <- json$BEAAPI$Results$Data
    if (is.null(data)) {
      return(tibble::tibble())
    }
    tibble::as_tibble(data) %>%
      dplyr::mutate(
        county_fips = fips,
        county_name = county_name,
        year = as.integer(TimePeriod),
        line_code = Code,
        line_number = as.numeric(stringr::str_extract(Code, "(?<=-)\\d+$")),
        value_raw = readr::parse_number(DataValue),
        unit_mult = suppressWarnings(as.numeric(UNIT_MULT)),
        value = value_raw * (10 ^ dplyr::if_else(is.na(unit_mult), 0, unit_mult))
      ) %>%
      dplyr::select(county_fips, county_name, year, line_code, line_number, value)
  })
}

bea_fake_county <- function(fips, county_name, line_codes, years) {
  grid <- expand.grid(line_code = line_codes, year = years, stringsAsFactors = FALSE)
  seed_val <- sum(as.integer(charToRaw(paste(fips, collapse = ""))))
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
