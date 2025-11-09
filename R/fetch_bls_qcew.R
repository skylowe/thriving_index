source(file.path("R", "utils.R"))

qcew_get <- function(series_id, start_year = 2020, end_year = 2020) {
  if (ti_offline()) {
    return(qcew_fake(series_id, start_year, end_year))
  }
  base_url <- "https://api.bls.gov/publicAPI/v2/timeseries/data/"
  body <- list(
    seriesid = list(series_id),
    startyear = as.character(start_year),
    endyear = as.character(end_year),
    registrationkey = ti_read_key("BLS_API_KEY")
  )
  resp <- httr::POST(base_url, body = body, encode = "json")
  if (httr::http_error(resp)) {
    stop(sprintf("BLS request failed: %s", httr::content(resp, "text", encoding = "UTF-8")))
  }
  json <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
  tibble::as_tibble(json$Results$series[[1]]$data)
}

qcew_fake <- function(series_id, start_year, end_year) {
  tibble::tibble(
    seriesID = series_id,
    year = start_year:end_year,
    period = "Q2",
    periodName = "Second Quarter",
    value = runif(length(year), 600, 950)
  )
}

