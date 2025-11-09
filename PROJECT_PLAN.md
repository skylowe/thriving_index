Thriving Index — Project Plan

Purpose
- Replicate the Nebraska Thriving Index in R, using the three provided references (Thriving_Index.pdf, Comparison_Regions.pdf, Thriving_Index_Calculations.xlsx) as the canonical source of definitions, methods, and benchmarks.
- Prioritize using public APIs for data acquisition where practicable; create clearly marked placeholder (fake) data for items without an accessible API.
- Produce an end‑to‑end, cross‑platform (Linux/Windows) pipeline that fetches data, computes measures, builds component indexes, assembles the overall index, and outputs region and component results with reproducible scripts and lightweight tests.

Key Outcomes
- Reproducible R pipeline with modular fetch/transform/compute steps.
- Component indexes and overall Thriving Index values matching the documented definitions.
- Peer region matching (Mahalanobis distance) and comparison outputs.
- Documentation and guidance for future contributors and agents.

Method Summary (from PDFs)
- Eight component indexes: Growth; Economic Opportunity & Diversity; Other Prosperity; Demographic Growth & Renewal; Education & Skill; Infrastructure & Cost of Doing Business; Quality of Life; Social Capital.
- Each component comprises specific measures (see Variables section). Final scoring: standardize measures within comparable peer groups, aggregate into component indexes, then average components to the aggregate Thriving Index. The scale targets 100 at peer mean; ±100 per standard deviation (0 → −1 SD; 200 → +1 SD).
- Peer groups are constructed using Mahalanobis distance on seven structural variables across 85 candidate regions (per Comparison_Regions.pdf).

Variables To Implement (grouped by component)
Note: Source and API plan listed for each; “Placeholder” indicates we will synthesize realistic interim data until we can automate or source a reliable dataset.

1) Growth Index
- Growth in Total Employment — BEA CAINC5 jobs (2017, 2020); API: BEA API.
- Private Employment (level) — BLS QCEW Private Employment, 2020; API: BLS QCEW (or BLS Data API if sufficient coverage).
- Growth in Private Wages per Job — BLS QCEW wages per job (2017, 2020); API: BLS QCEW.
- Growth in Households with Children — ACS S1101 (2011–2015 vs 2016–2020); API: Census.
- Growth in Dividends/Interest/Rent (DIR) Income — BEA CAINC5 (2017, 2020); API: BEA.

2) Economic Opportunity & Diversity Index
- Entrepreneurial Activity — Business births/deaths per person; API: Census BDS timeseries.
- Non‑Farm Proprietors per 1,000 Persons — BEA CAEMP25 + population; API: BEA + Census.
- Employer Establishments per 1,000 Residents — BLS QCEW establishments + population; API: BLS QCEW + Census.
- Share of Workers in Non‑Employer Establishments — CBP + Nonemployer Statistics Combined; API: Census (CBP + NES if/when available).
- Industry Diversity — Similarity index of regional NAICS employment shares to U.S.; API: Census CBP (2019).
- Occupation Diversity — Similarity index of SOC major groups shares to U.S.; API: ACS S2401 (2016–2020).
- Share of Telecommuters — ACS B08128 (works at home, exclude self‑employed & unpaid family); API: Census.

3) Other Prosperity Index
- Non‑Farm Proprietor Personal Income — BEA CAINC5 (2020); API: BEA.
- Personal Income Stability — Variability metric over 2006–2020 personal income; API: BEA, calculate CV/SD as per spreadsheet.
- Life Span (Life Expectancy at Birth) — IHME 1980–2014; API: none; Placeholder.
- Poverty Rate — ACS S1701 (2016–2020); API: Census.
- Share of Income from DIR — BEA CAINC5 (2020), DIR/total PI; API: BEA.

4) Demographic Growth & Renewal Index
- Long‑Run Population Growth — 2000 vs 2016–2020 ACS S0101; API: Census.
- Dependency Ratio — ACS S0101 (0–14 & 65+ vs 15–64); API: Census.
- Median Age — ACS S0101; API: Census.
- Millennial + Gen Z Balance Change (5‑year change in share born ≥1985) — ACS S0101 + B01001 over two periods; API: Census.
- Percent Hispanic — ACS B03003; API: Census.
- Percent Non‑White — ACS B02001; API: Census.

5) Education & Skill Index
- High School Attainment — ACS S1501; API: Census.
- Associate’s Degree Attainment — ACS S1501; API: Census.
- Bachelor’s Attainment — ACS S1501; API: Census.
- Labor Force Participation Rate — ACS DP03; API: Census.
- Percent of Knowledge Workers — Share employed in information, financial, prof/business services, health/education; ACS DP03; API: Census.

6) Infrastructure & Cost of Doing Business Index
- Broadband Internet Access (≥100/10 Mbps) — FCC Dec 2020; API: limited; Placeholder unless reliable API endpoint is identified.
- Presence of Interstate — County with interstate; API: none; Placeholder (derive from TIGER/Line or curated list later).
- Count of 4‑Year Colleges — NCES/IPEDS/Scorecard; API exists but key required; Placeholder, or integrate Scorecard later.
- Weekly Wage Rate — BLS QCEW Avg Weekly Wage Q2 2021; API: BLS QCEW.
- Top Marginal State Income Tax Rate — Tax Foundation 2022; API: none; Static table.
- Count of Qualified Opportunity Zones — CDFI Fund (2018); API: none; Static/placeholder.

7) Quality of Life Index
- Commute Time — ACS S0801; API: Census.
- Percent Housing Built Pre‑1960 — ACS DP04; API: Census.
- Relative Weekly Wage — Ratio of regional to statewide QCEW wages; API: BLS QCEW.
- Violent Crime Rate — FBI UCR 2018; API exists (api.usa.gov/crime/fbi/sapi), may need key; Placeholder initially.
- Property Crime Rate — FBI UCR 2018; API exists; Placeholder initially.
- Climate Amenities — USDA ERS Natural Amenities Scale; API: none; Static dataset later; Placeholder initially.
- Healthcare Access — Providers per person via CBP health care NAICS + population; API: CBP + Census.
- Count of National Parks — NPS API (key required); Placeholder initially.

8) Social Capital Index
- 501c3 Organizations per 1,000 — Tax Exempt World (2022); API: none; Placeholder initially.
- Volunteer Rate (state) — CNCS (2017); API: none; Placeholder initially.
- Volunteer Hours per Person (state) — CNCS (2017); API: none; Placeholder initially.
- Voter Turnout — 2018 general; API: none; Placeholder initially.
- Share of Tree City USA Counties — Arbor Day Foundation (2022); API: none; Placeholder initially.

Peer Regions and Matching
- Variables: population; % population in micropolitan area; % farm income; % ranch income; % manufacturing employment; distance to small MSA; distance to large MSA (per Comparison_Regions.pdf).
- Candidate pool: 85 regions across CO, IL, IA, KS, MN, MO, MT, NE, SD, WY (EDA regions outside NE, plus NE’s own regions where applicable).
- Method: compute a 7×7 covariance matrix on the matching variables; calculate Mahalanobis distance per candidate vs target region; select 5–7 closest peers. Output this set to comparisons.
- Initial implementation: curate candidate list in config, compute metrics from available sources; where distance inputs are unavailable via API, stub with documented values or placeholders and mark TODO.

Repository Structure
- R/ — modular functions by domain:
  - R/fetch_census_acs.R
  - R/fetch_bea.R
  - R/fetch_bls_qcew.R
  - R/fetch_census_cbp.R
  - R/fetch_census_bds.R
  - R/fetch_other_sources.R (FCC, CDFI, Tax Foundation, FBI, NPS; stub/placeholder helpers)
  - R/compute_measures_*.R (one per component) 
  - R/compute_diversity.R (industry/occupation similarity)
  - R/compute_peers.R (Mahalanobis logic)
  - R/compute_index.R (standardization, scaling, aggregation)
  - R/utils.R (keys, paths, logging, shared helpers)
- scripts/
  - scripts/run_all.R (orchestration)
  - scripts/fetch_all.R, scripts/build_indexes.R, scripts/validate.R
- config/
  - regions.yml (Nebraska region county lists)
  - comparison_candidates.yml (85 candidate EDA regions; metadata and sources)
  - weights.yml (if any weighting differs from equal weights; default equal)
- data/
  - data/raw/ (API pulls, snapshots)
  - data/intermediate/ (cleaned, derived inputs)
  - data/processed/ (component and aggregate index outputs)
  - data/fake/ (placeholders for hard‑to‑automate sources)
- tests/
  - tests/testthat/ (unit tests around transforms and index math)
- PROJECT_PLAN.md (this file; kept current as plan evolves)
- AGENTS.md and/or agents.md (agent guidance)

Environment and Keys
- R 4.3.x; use library path: /home/skylowe/R/x86_64-pc-linux-gnu-library/4.3.3 (see AGENTS.md for cross‑platform notes).
- API keys are read from .Renviron in the repo root via Sys.getenv(): CENSUS_KEY, BEA_API_KEY, BLS_API_KEY, FRED_API_KEY, EIA_API_KEY, NASSQS_TOKEN, and others present.
- Poppler utils (pdftotext) available and used for reference parsing only.

Data Acquisition Plan (API priority)
- Census (ACS/CBP/BDS): via Census API endpoints using CENSUS_KEY; minimize dependencies by using httr/jsonlite.
- BEA (CAINC5/CAEMP25): via BEA API using BEA_API_KEY (bea.R optional; default raw JSON via httr).
- BLS QCEW: via BLS (or direct QCEW API) using BLS_API_KEY.
- Items lacking robust APIs (FCC broadband, interstate presence, 4‑year colleges, OZs, climate amenities, social capital measures, crime, voter turnout, NPS) start as placeholders under data/fake/ with clear TODOs and schema to enable drop‑in replacement later.

Computation and Scoring
- Transform raw sources to county‑level metrics; aggregate to defined Nebraska regions (county lists in config/regions.yml).
- Compute each measure per definitions in the PDFs (time windows, ratios, growth rates, levels).
- Standardize measures within peer sets (z‑scores). For each component, average its measures. Aggregate components by simple mean to Thriving Index.
- Rescale: Index = 100 + 100 × z; cap extremes as needed for stability (TBD; match spreadsheet if present).

Testing and Validation
- Unit tests: verify each measure’s transform, standardization, and aggregation for known sample regions; ensure NA handling and reproducibility.
- Cross‑check: compare against any available values in Thriving_Index_Calculations.xlsx (where accessible) and figures in PDFs.

Initial Timeline and Milestones
1) Skeleton & configs (regions, candidate peers) — draft after plan approval.
2) Implement ACS/BEA/BLS/CBP/BDS fetchers and parsers.
3) Implement component computations (start with Growth, Education & Skill, Demographics).
4) Implement peer matching (Mahalanobis) and standardization logic.
5) Add placeholder datasets for non‑API sources with schemas.
6) Wire end‑to‑end run_all.R; produce first pass outputs.
7) Add tests around edge cases; tighten outputs and docs.

Open Questions for Sponsor
- Confirm whether the component and overall indexes use equal weighting throughout (the PDFs imply equal averages).
- Confirm exact diversity index formula (e.g., 1 − 0.5 × sum|p_r − p_us| vs cosine similarity). The spreadsheet sheet “Occupational Diversity” likely documents this; we will mirror its definition.
- Validate which set of EDA regions constitutes the 85‑region candidate pool used in 2022; if a reference list exists, please provide.
- Are there preferred proxy sources for crime, broadband, NPS, colleges, Tree City, and OZs beyond placeholders?

Change Log
- 2025-11-09: Initial plan drafted from source PDFs and workbook sheet names; API mapping and repo structure proposed.
- 2025-11-09: Scaffolded R modules, scripts, configs, placeholder data, and first subset of ACS-based measures; added offline-friendly pipeline and smoke-test scaffolding.
