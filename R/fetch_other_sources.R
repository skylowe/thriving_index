source(file.path("R", "utils.R"))

ti_read_placeholder <- function(filename) {
  path <- file.path(ti_paths()$data_fake, filename)
  if (!file.exists(path)) {
    stop(sprintf("Placeholder file %s is missing.", path))
  }
  readr::read_csv(path, show_col_types = FALSE)
}

placeholder_broadband <- function() ti_read_placeholder("broadband.csv")
placeholder_interstate <- function() ti_read_placeholder("interstate.csv")
placeholder_four_year_colleges <- function() ti_read_placeholder("four_year_colleges.csv")
placeholder_opportunity_zones <- function() ti_read_placeholder("opportunity_zones.csv")
placeholder_crime <- function() ti_read_placeholder("crime.csv")
placeholder_crime_property <- function() ti_read_placeholder("crime_property.csv")
placeholder_climate <- function() ti_read_placeholder("climate.csv")
placeholder_nps <- function() ti_read_placeholder("nps.csv")
placeholder_tree_city <- function() ti_read_placeholder("tree_city.csv")
placeholder_volunteering <- function() ti_read_placeholder("volunteering.csv")
placeholder_volunteering_hours <- function() ti_read_placeholder("volunteering_hours.csv")
placeholder_voter_turnout <- function() ti_read_placeholder("voter_turnout.csv")

