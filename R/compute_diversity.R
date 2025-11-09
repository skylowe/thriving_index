source(file.path("R", "utils.R"))

diversity_similarity <- function(region_shares, reference_shares) {
  shared_keys <- intersect(names(region_shares), names(reference_shares))
  if (length(shared_keys) == 0) {
    return(NA_real_)
  }
  sum_abs <- sum(abs(region_shares[shared_keys] - reference_shares[shared_keys]), na.rm = TRUE)
  1 - 0.5 * sum_abs
}

compute_diversity_placeholder <- function() {
  tibble::tibble(region_id = character(), measure = character(), value = double())
}

