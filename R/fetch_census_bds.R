source(file.path("R", "utils.R"))

bds_get <- function(year = 2019, geo = "county") {
  if (ti_offline()) {
    return(bds_fake(year))
  }
  base_url <- "https://api.census.gov/data/bds/2019/kauffman"
  query <- list(
    get = "firmbirths,firmdeaths,region",
    time = year,
    key = ti_read_key("CENSUS_KEY")
  )
  resp <- httr::GET(base_url, query = query)
  if (httr::http_error(resp)) {
    stop(sprintf("BDS request failed: %s", httr::content(resp, "text", encoding = "UTF-8")))
  }
  parsed <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
  header <- parsed[1, ]
  rows <- parsed[-1, , drop = FALSE]
  df <- tibble::as_tibble(rows)
  names(df) <- header
  df
}

bds_fake <- function(year) {
  tibble::tibble(
    firmbirths = sample(10:50, 8, replace = TRUE),
    firmdeaths = sample(10:50, 8, replace = TRUE),
    region = sprintf("R%s", seq_len(8)),
    time = year
  )
}

