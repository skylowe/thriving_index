source(file.path("R", "utils.R"))

cbp_get <- function(year = 2019, geo = "county:*") {
  if (ti_offline()) {
    return(cbp_fake(year))
  }
  base_url <- sprintf("https://api.census.gov/data/%s/cbp", year)
  query <- list(
    get = "EMP,ESTAB,NAICS2017,NAME",
    `for` = geo,
    key = ti_read_key("CENSUS_KEY")
  )
  resp <- httr::GET(base_url, query = query)
  if (httr::http_error(resp)) {
    stop(sprintf("CBP request failed: %s", httr::content(resp, "text", encoding = "UTF-8")))
  }
  parsed <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
  header <- parsed[1, ]
  rows <- parsed[-1, , drop = FALSE]
  df <- tibble::as_tibble(rows)
  names(df) <- header
  df
}

cbp_fake <- function(year) {
  counties <- ti_region_config() %>% dplyr::distinct(county)
  tibble::tibble(
    EMP = sample(100:500, nrow(counties), replace = TRUE),
    ESTAB = sample(10:50, nrow(counties), replace = TRUE),
    NAICS2017 = "00",
    NAME = paste0(counties$county, " County"),
    state = "31",
    county = stringr::str_pad(seq_len(nrow(counties)), 3, pad = "0")
  )
}

