# Virginia Rural Thriving Index - Project Plan

## Project Overview
Create a Thriving Index for rural regions in Virginia, modeled after the Nebraska Thriving Index. The project will:
- Collect county-level data for ALL counties in 10 states: Virginia, Pennsylvania, Maryland, Delaware, West Virginia, Kentucky, Tennessee, North Carolina, South Carolina, and Georgia
- Implement data collection for all 47 measures across 8 component indexes
- Later aggregate county data into regions and identify peer regions using Mahalanobis distance matching
- Calculate component indexes and overall thriving scores

**Current Focus**: County-level data collection. Regional aggregation and peer matching will occur in a later phase.

## Project Objectives
- Collect complete county-level data for all 47 measures (see API_MAPPING.md for details)
- Use Python for all data collection and analysis (cross-platform: Linux/Windows compatible)
- Work component by component, ensuring complete data retrieval before proceeding to next component
- Store all raw API responses and processed data for reproducibility

## Project Structure
```
thriving_index/
├── scripts/
│   ├── api_clients/      # API wrapper classes (BEA, BLS, Census, etc.)
│   ├── data_collection/  # Data collection scripts by component
│   ├── processing/       # Data cleaning and processing
│   └── analysis/         # Index calculation and analysis
├── data/
│   ├── raw/             # Raw API responses by source
│   ├── processed/       # Cleaned and processed data
│   └── results/         # Calculated indexes and scores
├── API_MAPPING.md       # Comprehensive variable and API mapping (47 measures)
├── PROJECT_PLAN.md      # This file - current status and task tracking
├── CLAUDE.md            # Project knowledge base
└── .Renviron            # API keys storage
```

## Geographic Scope
- **All counties** in these 10 states:
  - Virginia (VA)
  - Pennsylvania (PA)
  - Maryland (MD)
  - Delaware (DE)
  - West Virginia (WV)
  - Kentucky (KY)
  - Tennessee (TN)
  - North Carolina (NC)
  - South Carolina (SC)
  - Georgia (GA)

## Component Indexes
The project implements 8 component indexes with 47 total measures. See **API_MAPPING.md** for complete details on each measure, data source, API endpoints, and calculation methods.

1. **Growth Index** (5 measures)
2. **Economic Opportunity & Diversity Index** (7 measures)
3. **Other Prosperity Index** (5 measures)
4. **Demographic Growth & Renewal Index** (6 measures)
5. **Education & Skill Index** (5 measures)
6. **Infrastructure & Cost of Doing Business Index** (6 measures)
7. **Quality of Life Index** (8 measures)
8. **Social Capital Index** (5 measures)

## Implementation Phases

### Phase 0: Project Setup
**Status**: ✓ Completed
- [x] Review Nebraska Thriving Index documentation
- [x] Review comparison regions methodology
- [x] Review API mapping documentation
- [x] Create project structure (scripts/ and data/ folders)
- [x] Create PROJECT_PLAN.md
- [x] Create CLAUDE.md
- [x] User review and approval to proceed

### Phase 1: Component Index 1 - Growth Index
**Status**: ✓ Completed
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-15

Data collection tasks (5 measures - see API_MAPPING.md for details):
- [x] Set up API clients (BEA, QCEW, Census) with keys from .Renviron
- [x] Collect Growth in Total Employment (BEA CAINC5) - **2,322 records**
- [x] Collect Private Employment (BLS QCEW) - **2,406 records**
- [x] Collect Growth in Private Wages Per Job (BLS QCEW) - **included in above**
- [x] Collect Growth in Households with Children (Census ACS) - **1,604 records**
- [x] Collect Growth in Dividends, Interest and Rent Income (BEA CAINC5) - **2,322 records**

**Total Records Collected**: 8,654 records for 802 counties across all 10 states

**Data Collected**:
- BEA Employment (2020-2022): 774 counties × 3 years = 2,322 records ✓
- BEA DIR Income (2020-2022): 774 counties × 3 years = 2,322 records ✓
- Census Households with Children (2017, 2022): 802 counties × 2 periods = 1,604 records ✓
- BLS QCEW Private Employment & Wages (2020-2022): 802 counties × 3 years = 2,406 records ✓
  - Note: Uses BLS downloadable data files, not Time Series API
  - Files cached locally (~500MB per year)

**Files Created**:
- `data/raw/bea/bea_employment_2020_2022.json`
- `data/raw/bea/bea_dir_income_2020_2022.json`
- `data/raw/census/census_households_children_[STATE]_[YEAR].json` (20 files)
- `data/raw/qcew/qcew_private_employment_wages_2020_2022.csv`
- `data/raw/qcew/cache/[YEAR]_annual_singlefile.csv` (3 cache files)
- `data/processed/bea_employment_processed.csv`
- `data/processed/bea_dir_income_processed.csv`
- `data/processed/census_households_children_processed.csv`
- `data/processed/qcew_private_employment_wages_2020_2022.csv`
- `data/processed/component1_collection_summary.json`

**Notes**:
- QCEW client uses downloadable ZIP files (~500MB each) rather than Time Series API
- Data includes all private sector employment and wages (measures 1.2 and 1.3 combined)
- 802 unique counties identified across all 10 states
- BEA data returns 774 counties (some smaller counties may not have separate BEA reporting)

### Phase 2: Component Index 2 - Economic Opportunity & Diversity Index
**Status**: ✓ Completed (7 of 7 measures collected)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-16

Data collection tasks (7 measures - see API_MAPPING.md for details):
- [x] Set up API clients (BDS, CBP, Nonemployer, extended BEA and Census)
- [x] Collect Entrepreneurial Activity (Census BDS) - **802 records**
- [x] Collect Non-Farm Proprietors (BEA CAINC4) - **774 records**
- [x] Collect Employer Establishments (Census CBP) - **802 records**
- [x] Collect Share of Non-Employer Workers (Census NES) - **802 records**
- [x] Collect Industry Diversity (Census CBP) - **19 NAICS sectors, 346-801 records each**
- [x] Collect Occupation Diversity (Census ACS) - **802 records**
- [x] Collect Share of Telecommuters (Census ACS) - **802 records**

**Data Collected**:
- Census BDS Business Dynamics (2021): 802 counties ✓
- BEA Nonfarm Proprietors Income (2022): 774 counties ✓
- Census CBP Establishments (2021): 802 counties ✓
- Census Nonemployer Statistics (2021): 802 counties ✓
- Census CBP Industry Employment (2021): 19 NAICS sectors ✓
- Census ACS Occupation Data (2022): 802 counties ✓
- Census ACS Telecommuter Data (2022): 802 counties ✓

**Files Created**:
- `data/raw/bds/bds_business_dynamics_[STATE]_2021.json` (10 files)
- `data/raw/bea/bea_proprietors_2022.json`
- `data/raw/cbp/cbp_establishments_[STATE]_2021.json` (10 files)
- `data/raw/nonemp/nonemp_firms_[STATE]_2021.json` (10 files)
- `data/raw/cbp/cbp_industry_employment_[STATE]_2021.json` (10 files)
- `data/raw/census/census_occupation_[STATE]_2022.json` (10 files)
- `data/raw/census/census_telecommuter_[STATE]_2022.json` (10 files)
- `data/processed/bds_business_dynamics_2021.csv`
- `data/processed/bea_proprietors_2022.csv`
- `data/processed/cbp_establishments_2021.csv`
- `data/processed/nonemp_firms_2021.csv`
- `data/processed/cbp_industry_naics[XX]_2021.csv` (19 files, one per NAICS sector)
- `data/processed/census_occupation_2022.csv`
- `data/processed/census_telecommuter_2022.csv`
- `data/processed/component2_collection_summary.json`

**Notes**:
- BDS API uses `YEAR` parameter instead of `time` parameter
- Used BEA CAINC4 table (proprietors INCOME) instead of CAEMP25 (employment) because CAEMP25 table does not exist in BEA Regional API
- Nonemployer Statistics API variable names changed in 2021+: use NESTAB (not NONEMP) and NRCPTOT (not RCPTOT)
- Successfully collected all 7 measures (100% completion rate)
- All 802 counties covered where data available (BEA returns 774 counties due to Virginia independent city aggregation)

### Phase 3: Component Index 3 - Other Economic Prosperity Index
**Status**: ✓ Completed (4 of 5 measures collected)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-16

Data collection tasks (4 of 5 measures - see API_MAPPING.md for details):
- [x] Set up CAINC1 support in BEA client for income stability
- [x] Collect Non-Farm Proprietor Income (BEA CAINC4) - **774 records**
- [x] Collect Personal Income Stability (BEA CAINC1, 15 years) - **774 records**
- [ ] Collect Life Expectancy (County Health Rankings bulk download) - **DEFERRED**
- [x] Collect Poverty Rate (Census ACS S1701) - **802 records**
- [x] Collect Share of DIR Income (BEA CAINC5N + CAINC1) - **774 records**

**Data Collected**:
- BEA Proprietor Income (2022): 774 counties ✓
- BEA Income Stability (2008-2022): 774 counties, 15 years of data ✓
- Census Poverty Rate (2022): 802 counties ✓
- BEA DIR Income Share (2022): 774 counties ✓

**Files Created**:
- `data/raw/bea/bea_proprietor_income_2022.json`
- `data/raw/bea/bea_personal_income_2008_2022.json`
- `data/raw/census/census_poverty_[STATE]_2022.json` (10 files)
- `data/raw/bea/bea_dir_income_share_2022.json`
- `data/raw/bea/bea_total_income_share_2022.json`
- `data/processed/bea_proprietor_income_2022.csv`
- `data/processed/bea_income_stability_2008_2022.csv`
- `data/processed/census_poverty_2022.csv`
- `data/processed/bea_dir_income_share_2022.csv`
- `data/processed/component3_collection_summary.json`

**Notes**:
- Successfully collected 4 of 5 measures (100% of API-based measures)
- Measure 3.3 (Life Expectancy) requires bulk download from County Health Rankings - will be collected separately
- All 774 counties have complete 15-year data for income stability calculation
- Average coefficient of variation (CV) for income stability: 0.1734
- Average poverty rate: 15.92%
- Average DIR income share: 14.93%
- BEA data returns 774 counties (Virginia independent cities aggregated)

### Phase 4: Component Index 4 - Demographic Growth & Renewal Index
**Status**: Not Started
- [ ] Collect data for 6 measures (Census, IRS)
- [ ] Validate and clean data

### Phase 5: Component Index 5 - Education & Skill Index
**Status**: Not Started
- [ ] Collect data for 5 measures (Census ACS, State Dept of Education)
- [ ] Validate and clean data

### Phase 6: Component Index 6 - Infrastructure & Cost of Doing Business Index
**Status**: Not Started
- [ ] Collect data for 6 measures (FCC, HUD, Census)
- [ ] Validate and clean data

### Phase 7: Component Index 7 - Quality of Life Index
**Status**: Not Started
- [ ] Collect data for 8 measures (Census ACS, CDC, FBI)
- [ ] Validate and clean data

### Phase 8: Component Index 8 - Social Capital Index
**Status**: Not Started
- [ ] Collect data for 5 measures (State Election Data, Census CBP)
- [ ] Validate and clean data

### Phase 9: Regional Aggregation and Peer Selection
**Status**: Not Started
- [ ] Define Virginia rural regions (aggregate counties)
- [ ] Define comparison regions in other 9 states
- [ ] Gather 6 matching variables for Mahalanobis distance
- [ ] Implement Mahalanobis distance matching algorithm
- [ ] Select 5-8 peer regions for each Virginia region

### Phase 10: Index Calculation and Analysis
**Status**: Not Started
- [ ] Implement index scoring methodology (100 = peer average, ±100 = ±1 SD)
- [ ] Calculate all 8 component indexes
- [ ] Calculate overall Thriving Index scores
- [ ] Generate comparison rankings
- [ ] Create visualizations and reports

## Current Status
**Phase**: Phase 4 - Component Index 4 (Ready to Start)
**Date**: 2025-11-16

**Completed**:
- ✓ Phase 0: Project setup and infrastructure
- ✓ Phase 1: Component Index 1 - Growth Index (8,654 records collected)
  - ✓ API clients created and tested (BEA, QCEW, Census)
  - ✓ All 5 measures collected for 802 counties across 10 states
  - ✓ QCEW client implemented using downloadable data files
  - ✓ Data cached for efficient reprocessing
- ✓ Phase 2: Component Index 2 - Economic Opportunity & Diversity Index (ALL 7 measures complete)
  - ✓ Created BDS, CBP, and Nonemployer API clients
  - ✓ Extended BEA client for proprietors data (CAINC4 table)
  - ✓ Extended Census client for occupation and telecommuter data
  - ✓ Collected 802 counties for BDS business dynamics (births and deaths)
  - ✓ Collected 774 counties for BEA proprietors income
  - ✓ Collected 802 counties for CBP establishments
  - ✓ Collected 802 counties for Nonemployer Statistics
  - ✓ Collected 19 NAICS industry sectors via CBP (industry diversity)
  - ✓ Collected 802 counties for ACS occupation and telecommuter data
- ✓ Phase 3: Component Index 3 - Other Economic Prosperity Index (4 of 5 measures complete)
  - ✓ Extended BEA client for CAINC1 table (total personal income)
  - ✓ Collected 774 counties for proprietor income (BEA)
  - ✓ Collected 774 counties for income stability (BEA, 15 years)
  - ✓ Collected 802 counties for poverty rate (Census ACS)
  - ✓ Collected 774 counties for DIR income share (BEA)
  - ⏸ Life expectancy deferred (requires bulk download from County Health Rankings)

**Next Steps**:
1. Optional: Collect Measure 3.3 (Life Expectancy) via bulk download
2. Begin Component Index 4 data collection (Demographic Growth & Renewal Index)
   - 6 measures total (see API_MAPPING.md for details)
   - Data sources: Census Decennial, Census ACS, IRS Migration
3. Continue through Components 4-8 sequentially
4. Later: Validate and clean all component data
5. Later: Calculate growth rates and index scores

## Data Confidence Summary
See API_MAPPING.md for complete details on each measure's confidence level:
- HIGH confidence measures: 36 of 47 (76.6%)
- MEDIUM confidence measures: 7 of 47 (14.9%)
- LOW confidence measures: 4 of 47 (8.5%)

## Technical Dependencies
- Python 3.x
- API keys stored in .Renviron file:
  - BEA Regional API key
  - BLS API key
  - Census API key
  - Additional keys as needed for other sources
- Internet connection for API access
- Cross-platform compatibility (Linux/Windows)

## Notes
- API_MAPPING.md is the authoritative source for all variable definitions, data sources, and calculation methods
- Work component by component, completing each fully before proceeding
- Collect data for ALL counties in all 10 states
- Regional aggregation and peer matching will occur after data collection is complete
- Update this plan regularly as work progresses
- Focus on high-confidence measures first, address medium/low confidence measures as encountered
