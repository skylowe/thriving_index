source(file.path("R", "utils.R"))

load_candidate_regions <- function() {
  yaml::read_yaml(ti_paths()$config_candidates)$candidates
}

compute_peer_groups <- function(regions = NULL) {
  if (is.null(regions)) {
    regions <- ti_region_config() %>% dplyr::distinct(region_id, region_name)
  }
  zone_data <- ti_region_zone_data() %>%
    dplyr::select(region_name, zone_group)
  regions %>%
    dplyr::left_join(zone_data, by = "region_name") %>%
    dplyr::mutate(peer_group = dplyr::coalesce(zone_group, region_id)) %>%
    dplyr::select(region_id, peer_group)
}
