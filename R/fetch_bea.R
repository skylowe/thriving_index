source(file.path("R", "utils.R"))

bea_get <- function(table_name = "CAINC5", line_code = 70, geo_fips = "31*", year = 2020) {
  if (ti_offline()) {
    return(bea_fake(table_name, line_code, geo_fips, year))
  }
  base_url <- "https://apps.bea.gov/api/data"
  params <- list(
    UserID = ti_read_key("BEA_API_KEY"),
    datasetname = "Regional",
    TableName = table_name,
    LineCode = line_code,
    GeoFips = geo_fips,
    Year = year,
    ResultFormat = "json"
  )
  resp <- httr::GET(base_url, query = params)
  if (httr::http_error(resp)) {
    stop(sprintf("BEA request failed: %s", httr::content(resp, "text", encoding = "UTF-8")))
  }
  json <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
  tibble::as_tibble(json$BEAAPI$Results$Data)
}

bea_fake <- function(table_name, line_code, geo_fips, year) {
  counties <- ti_region_config() %>% dplyr::distinct(county)
  seed_val <- sum(as.integer(charToRaw(paste(table_name, line_code, year, collapse = ""))))
  set.seed(seed_val %% .Machine$integer.max)
  tibble::tibble(
    GeoFips = sprintf("31%03d", seq_len(nrow(counties))),
    GeoName = counties$county,
    LineCode = line_code,
    TimePeriod = year,
    DataValue = round(runif(nrow(counties), 1000, 5000), 0)
  )
}

