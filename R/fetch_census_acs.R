source(file.path("R", "utils.R"))

acs_dataset_from_table <- function(table) {
  table <- toupper(table)
  if (stringr::str_starts(table, "S")) {
    return("subject")
  }
  if (stringr::str_starts(table, "DP")) {
    return("profile")
  }
  "detail"
}

acs_get <- function(table, variables, year = 2020, state_fips = "31", county = "*") {
  dataset <- acs_dataset_from_table(table)
  if (ti_offline()) {
    return(acs_fake(table, variables, year))
  }
  base_url <- if (dataset == "detail") {
    sprintf("https://api.census.gov/data/%s/acs/acs5", year)
  } else {
    sprintf("https://api.census.gov/data/%s/acs/acs5/%s", year, dataset)
  }
  vars <- unique(c("NAME", variables))
  query <- list(
    get = paste(vars, collapse = ","),
    `for` = sprintf("county:%s", county),
    `in` = sprintf("state:%s", state_fips)
  )
  key <- ti_read_key("CENSUS_KEY")
  if (nzchar(key)) {
    query$key <- key
  }
  resp <- httr::GET(base_url, query = query)
  if (httr::http_error(resp)) {
    stop(sprintf("ACS request failed for table %s: %s", table, httr::content(resp, "text", encoding = "UTF-8")))
  }
  parsed <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))
  header <- parsed[1, ]
  rows <- parsed[-1, , drop = FALSE]
  df <- as.data.frame(rows, stringsAsFactors = FALSE)
  names(df) <- header
  df <- tibble::as_tibble(df) %>%
    dplyr::mutate(
      county_fips = paste0(state, county),
      county_name = ti_clean_county_name(NAME)
    )
  df
}

acs_fake <- function(table, variables, year) {
  counties <- ti_region_config() %>% dplyr::distinct(county_clean, county)
  seed_val <- sum(as.integer(charToRaw(paste(table, year, collapse = ""))))
  set.seed(seed_val %% .Machine$integer.max)
  tibble::tibble(
    NAME = paste0(stringr::str_to_title(stringr::str_to_lower(counties$county_clean)), " County, Nebraska"),
    state = "31",
    county = stringr::str_pad(seq_len(nrow(counties)), 3, pad = "0"),
    county_fips = paste0(state, county),
    county_name = counties$county
  ) %>%
    dplyr::bind_cols(
      purrr::map_dfc(variables, function(v) {
        tibble::tibble(!!v := round(runif(nrow(counties), min = 0, max = 100), 2))
      })
    )
}

acs_fetch_median_age <- function(year = 2020) {
  acs_get("S0101", c("S0101_C01_032E"), year = year)
}

acs_fetch_education_rates <- function(year = 2020) {
  vars <- c(
    hs = "S1501_C02_009E",
    associates = "S1501_C02_011E",
    bachelors = "S1501_C02_012E"
  )
  df <- acs_get("S1501", unname(vars), year = year)
  df$hs <- as.numeric(df[[vars[["hs"]]]])
  df$associates <- as.numeric(df[[vars[["associates"]]]])
  df$bachelors <- as.numeric(df[[vars[["bachelors"]]]])
  df
}

acs_fetch_labor_force <- function(year = 2020) {
  acs_get("DP03", c("DP03_0002PE"), year = year)
}

acs_fetch_poverty <- function(year = 2020) {
  acs_get("S1701", c("S1701_C03_001E"), year = year)
}

acs_fetch_households_children <- function(year = 2020) {
  acs_get("S1101", c("S1101_C01_001E", "S1101_C01_010E"), year = year)
}

acs_fetch_telecommuters <- function(year = 2020) {
  acs_get("B08128", c("B08128_001E", "B08128_061E", "B08128_064E", "B08128_069E", "B08128_070E"), year = year)
}

acs_fetch_dependency <- function(year = 2020) {
  acs_get("S0101", c("S0101_C01_001E", "S0101_C01_022E", "S0101_C01_030E"), year = year)
}

acs_fetch_race <- function(year = 2020) {
  acs_get("B02001", c("B02001_001E", "B02001_002E"), year = year)
}

acs_fetch_hispanic <- function(year = 2020) {
  acs_get("B03003", c("B03003_001E", "B03003_003E"), year = year)
}

acs_fetch_commute <- function(year = 2020) {
  acs_get("S0801", c("S0801_C01_046E"), year = year)
}

acs_fetch_housing_age <- function(year = 2020) {
  acs_get("DP04", c("DP04_0024PE", "DP04_0025PE", "DP04_0026PE"), year = year)
}
