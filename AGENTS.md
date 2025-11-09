Thriving Index — Agents Guide

Overview
- Goal: Implement the Nebraska Thriving Index in R using the provided PDFs and workbook as the ground truth. Prefer public APIs for data; where APIs aren’t readily available, generate well‑documented placeholder datasets with the same schema so the pipeline runs end‑to‑end.
- This file gives LLM agents (ChatGPT Codex, Claude Code, etc.) concrete guidance: repo structure, coding conventions, data sources, environment setup, execution, testing, and how to evolve the plan.

Environment
- OS: Must run on Linux or Windows.
- R version: 4.3.x recommended.
- Library path (Linux): All R packages should be installed and loaded from `/home/skylowe/R/x86_64-pc-linux-gnu-library/4.3.3`. Always prepend it in scripts:
  - In R: `.libPaths(c("/home/skylowe/R/x86_64-pc-linux-gnu-library/4.3.3", .libPaths()))`
- Library path (Windows): Use the default R user library. Do not attempt to use the Linux path on Windows; guard with `if (tolower(Sys.info()["sysname"]) == "windows")`.
- API keys: Read from the repo‑root `.Renviron` via `Sys.getenv()`; keys present include `CENSUS_KEY`, `BEA_API_KEY`, `BLS_API_KEY`, `FRED_API_KEY`, `EIA_API_KEY`, `NASSQS_TOKEN`, plus others. Never hardcode keys.
- Tools available: `poppler-utils` (use `pdftotext` to inspect the source PDFs if needed during development), standard shell utilities, and Rscript.

Repo Structure (authoritative)
- `R/` — R modules
  - `fetch_census_acs.R`, `fetch_bea.R`, `fetch_bls_qcew.R`, `fetch_census_cbp.R`, `fetch_census_bds.R`, `fetch_other_sources.R`
  - `compute_measures_*.R` (one per component), `compute_diversity.R`, `compute_peers.R`, `compute_index.R`, `utils.R`
- `scripts/` — Orchestration entry points
  - `run_all.R`, `fetch_all.R`, `build_indexes.R`, `validate.R`
- `config/` — YAML configs
  - `regions.yml`, `comparison_candidates.yml`, `weights.yml`
- `data/` — Data lifecycle
  - `raw/`, `intermediate/`, `processed/`, `fake/`
- `tests/testthat/` — Unit tests
- `PROJECT_PLAN.md` — Living plan to be kept current
- `AGENTS.md` and `agents.md` — This guidance

Execution
- Full pipeline: `Rscript scripts/run_all.R`
- Fetch only: `Rscript scripts/fetch_all.R`
- Build/compute only: `Rscript scripts/build_indexes.R`
- Validate & smoke tests: `Rscript scripts/validate.R`

Coding Conventions
- Keep functions pure and composable. Separate fetch → clean → compute → aggregate.
- Logging: Use simple `message()` and return structured data frames/tibbles.
- Inputs/outputs: Prefer tibbles with explicit `region_id`, `county_fips`, `year`, `measure`, `value` columns.
- Namespacing: Prefix exported helpers by domain (e.g., `acs_`, `bea_`, `qcew_`, `cbp_`, `bds_`).
- Error handling: Fail fast on missing keys; gracefully handle empty API responses and rate limits via retries with backoff.
- Cross‑platform paths: Use `file.path()` and avoid hardcoded separators.

Data Sources and API Usage
- Census ACS (tables S0101, S1101, S1501, DP03, DP04, S2401, B01001, B02001, B03003, B08128): query via Census API using `CENSUS_KEY`. Keep requests at county level; aggregate to regions by county lists.
- BEA (CAINC5, CAEMP25): query via BEA API using `BEA_API_KEY`.
- BLS QCEW (employment, wages, establishments): use the QCEW API (or BLS API if sufficient). Requires `BLS_API_KEY`.
- CBP and Nonemployer Stats: use Census API endpoints where available; otherwise pre‑downloaded CSVs can be integrated later. Until then, mock data.
- BDS (Business Dynamics Statistics): use Census timeseries API for births/deaths per capita.
- Items without straightforward APIs (FCC broadband, interstate presence, 4‑year colleges, Tax Foundation top rate, OZs, crime, climate amenities, NPS, social capital measures): create clearly marked placeholders in `data/fake/` with columns: `county_fips`, `year`, `measure`, `value`, `source = "placeholder"`. Keep schemas identical to the real counterparts for drop‑in replacement.

Computation Rules (align with PDFs)
- Region definitions: `config/regions.yml` lists counties per Nebraska region.
- Diversity indices: implement similarity to U.S. distribution across NAICS 2‑digit (industry) and SOC major groups (occupation). Suggested formula: `similarity = 1 - 0.5 * sum(abs(p_region - p_us))`. Match the workbook if it specifies differently.
- Measure transforms: follow time windows and formulas exactly (growth rates, shares, levels) per Thriving_Index.pdf.
- Standardization: compute z‑scores within each peer group for each measure; rescale to Index scale: `index = 100 + 100 * z`.
- Component aggregation: simple average of standardized measures within component. Aggregate index: simple average across components (unless `config/weights.yml` states otherwise).

Peer Matching
- Implement Mahalanobis distance using seven structural variables (population, % micropolitan, % farm income, % ranch income, % manufacturing employment, distance to small/large MSAs) across ~85 candidate regions (see Comparison_Regions.pdf).
- If any inputs lack APIs, stub from documented values or placeholders and flag TODOs. Persist peer sets per Nebraska region for reproducibility.

Testing
- Use `testthat`. Add targeted tests for:
  - Parsing and shaping of each API response
  - Correct aggregation from county → region
  - Diversity index math on small known examples
  - Standardization and rescaling (z to 100±100)
  - End‑to‑end smoke run producing non‑empty outputs

Updating the Plan
- Keep `PROJECT_PLAN.md` current. When scope or sequencing changes, append a succinct update under “Change Log” and ensure steps remain feasible.
- For multi‑step work, maintain a lightweight task list via the CLI plan tool; mark steps completed as you progress.

Agent Workflow Tips (Codex/Claude)
- Prefer `rg` to search, `pdftotext` to inspect PDFs, and apply small, targeted patches via the CLI patch tool. Read files in ≤250 line chunks.
- Be surgical: don’t refactor unrelated code or rename files without clear benefit.
- Validate locally where possible; if network is restricted, skip calls and rely on placeholder data.
- Never echo secrets; reference them via `Sys.getenv()` only.

Cross‑Platform Notes
- Paths: always use `file.path()` in R and avoid OS‑specific assumptions.
- Library path: enforce `/home/skylowe/R/x86_64-pc-linux-gnu-library/4.3.3` only on Linux. On Windows, do not set this path; use default R user library.
- Line endings: write text files with LF; tests should be robust to CRLF on Windows.

When to Ask for Help
- If a dataset’s definition from the PDFs is ambiguous or conflicts with the workbook, pause and ask for clarification with a concise pointer (file path and line).
- If an API requires credentials not present in `.Renviron`, implement a placeholder and request the missing key only if essential to proceed.

