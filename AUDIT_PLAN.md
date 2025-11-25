# Thriving Index Project Audit Plan

This document tracks the step-by-step verification of the Thriving Index project, ensuring data integrity and methodological correctness from raw collection to final scoring.

## Phase 1: Data Collection Audit (Components 1-8)
**Objective:** Confirm that raw data for all 47 measures has been successfully collected for all 10 target states.

- [ ] **Step 1.1:** Cross-reference `API_MAPPING.md` with the file system to ensure raw data files exist for every measure in `data/raw/`.
- [ ] **Step 1.2:** Spot-check key raw data files (JSON/CSV) to verify they contain data for all 10 states (VA + 9 peers) and aren't empty or corrupted.
- [ ] **Step 1.3:** Verify that specific "fix" scripts (like `fix_households_children_data.py`) were run and their output integrated.

## Phase 2: Regional Definitions & Aggregation Audit
**Objective:** Ensure every county is correctly mapped to a region and that county-level data is aggregated correctly.

- [ ] **Step 2.1:** Verify `data/regions/*.csv` files to ensure complete coverage of the 10-state area (checking for missing counties).
- [ ] **Step 2.2:** Audit `scripts/aggregation_config.py`. Verify correct aggregation methods:
    - **Sum**: For absolute counts (e.g., population, jobs).
    - **Weighted Mean**: For rates/percentages (e.g., poverty rate weighted by population).
    - **Recalculate**: For complex ratios (e.g., growth rates derived from summed base/current values).
- [ ] **Step 2.3:** Check generated regional data files (`data/regional/*.csv`) to confirm they contain exactly 94 rows.

## Phase 3: Peer Matching Logic Audit
**Objective:** Verify that the "peer regions" for Virginia were selected using the correct methodology and data.

- [ ] **Step 3.1:** Review `scripts/gather_peer_matching_variables.py` to confirm the 7 matching variables (Population, Micropolitan %, etc.) are calculated correctly.
- [ ] **Step 3.2:** Verify `data/peer_regions_selected.csv` to ensure every rural Virginia region has exactly 5-8 assigned peer regions and that self-matching is excluded.

## Phase 4: Index Calculation & Scoring Audit
**Objective:** Re-verify the final math, ensuring the Z-score calculations and rankings are sound.

- [ ] **Step 4.1:** Final review of `scripts/calculate_thriving_index.py` (post-fix) to ensure no logic errors remain.
- [ ] **Step 4.2:** Verify that the "negative" measure inversion list is comprehensive and matches the definitions in `API_MAPPING.md`.
- [ ] **Step 4.3:** Spot-check a single region's score calculation manually against the raw data to "ground truth" the automated output.

## Phase 5: Final Artifact Verification
**Objective:** Ensure the final output files are ready for consumption.

- [ ] **Step 5.1:** Inspect `data/results/` files (`thriving_index_overall.csv`, etc.) for formatting, null values, or anomalies.
- [ ] **Step 5.2:** Briefly review `dashboard.py` to ensure it points to the correct, updated data files.