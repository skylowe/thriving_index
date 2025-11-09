source(file.path("R", "utils.R"))

load_candidate_regions <- function() {
  yaml::read_yaml(ti_paths()$config_candidates)$candidates
}

compute_peer_groups <- function(regions = NULL) {
  if (is.null(regions)) {
    regions <- ti_region_config() %>% dplyr::distinct(region_id, region_name)
  }
  tibble::tibble(
    region_id = regions$region_id,
    peer_group = regions$region_id
  )
}

