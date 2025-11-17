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
**Status**: ✅ **FULLY COMPLETED** (All 5 measures collected in single script)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-17

Data collection tasks (ALL 5 measures - see API_MAPPING.md for details):
- [x] Set up CAINC1 support in BEA client for income stability
- [x] Collect Non-Farm Proprietor Income (BEA CAINC4) - **774 records**
- [x] Collect Personal Income Stability (BEA CAINC1, 15 years) - **774 records**
- [x] Collect Life Expectancy (County Health Rankings Zenodo) - **812 records** ✅
- [x] Collect Poverty Rate (Census ACS S1701) - **802 records**
- [x] Collect Share of DIR Income (BEA CAINC5N + CAINC1) - **774 records**

**Data Collected**:
- BEA Proprietor Income (2022): 774 counties ✓
- BEA Income Stability (2008-2022): 774 counties, 15 years of data ✓
- County Health Rankings Life Expectancy (2025): 812 counties ✓
- Census Poverty Rate (2022): 802 counties ✓
- BEA DIR Income Share (2022): 774 counties ✓

**Files Created**:
- `data/raw/bea/bea_proprietor_income_2022.json`
- `data/raw/bea/bea_personal_income_2008_2022.json`
- `data/raw/chr/chr_life_expectancy_2025_metadata.json`
- `data/raw/census/census_poverty_[STATE]_2022.json` (10 files)
- `data/raw/bea/bea_dir_income_share_2022.json`
- `data/raw/bea/bea_total_income_share_2022.json`
- `data/processed/bea_proprietor_income_2022.csv`
- `data/processed/bea_income_stability_2008_2022.csv`
- `data/processed/chr_life_expectancy_2025.csv`
- `data/processed/census_poverty_2022.csv`
- `data/processed/bea_dir_income_share_2022.csv`
- `data/processed/component3_collection_summary.json`

**Notes**:
- **100% COMPLETE**: Successfully collected all 5 measures in single script (3,936 total records)
- All measures collected via `collect_component3.py` including life expectancy integration
- Life expectancy data downloaded from Zenodo (DOI: 10.5281/zenodo.17584421)
- All 774 counties have complete 15-year data for income stability calculation
- Average coefficient of variation (CV) for income stability: 0.1734
- Average poverty rate: 15.92%
- Average DIR income share: 14.93%
- Average life expectancy: 73.75 years (range: 64.32-88.91)
- BEA data returns 774 counties (Virginia independent cities aggregated)
- Life expectancy data includes 812 counties (includes state summaries and independent cities)

### Phase 4: Component Index 4 - Demographic Growth & Renewal Index
**Status**: ✅ **FULLY COMPLETED** (All 6 measures collected)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-16

Data collection tasks (ALL 6 measures - see API_MAPPING.md for details):
- [x] Extend Census client for Component 4 data collection
- [x] Collect Long-Run Population Growth (2000 Census + 2022 ACS) - **1,606 records**
- [x] Collect Dependency Ratio (2022 ACS age distribution) - **802 records**
- [x] Collect Median Age (2022 ACS) - **802 records**
- [x] Collect Millennial/Gen Z Balance Change (2017-2022 ACS) - **1,604 records**
- [x] Collect Percent Hispanic (2022 ACS) - **802 records**
- [x] Collect Percent Non-White (2022 ACS) - **802 records**

**Total Records Collected**: 5,616 records for 802 counties across all 10 states

**Data Collected**:
- Census 2000 Population: 804 counties ✓
- Census ACS 2022 Population: 802 counties ✓
- Census ACS 2022 Age Distribution: 802 counties ✓
- Census ACS 2017 Age Distribution: 802 counties ✓
- Census ACS 2022 Median Age: 802 counties ✓
- Census ACS 2022 Hispanic Data: 802 counties ✓
- Census ACS 2022 Race Data: 802 counties ✓

**Files Created**:
- `data/raw/census/census_population_2000_[STATE].json` (10 files)
- `data/raw/census/census_population_2022_[STATE].json` (10 files)
- `data/raw/census/census_age_distribution_2022_[STATE].json` (10 files)
- `data/raw/census/census_age_distribution_2017_[STATE].json` (10 files)
- `data/raw/census/census_median_age_2022_[STATE].json` (10 files)
- `data/raw/census/census_hispanic_2022_[STATE].json` (10 files)
- `data/raw/census/census_race_2022_[STATE].json` (10 files)
- `data/processed/census_population_growth_2000_2022.csv`
- `data/processed/census_dependency_ratio_2022.csv`
- `data/processed/census_median_age_2022.csv`
- `data/processed/census_millennial_genz_change_2017_2022.csv`
- `data/processed/census_hispanic_2022.csv`
- `data/processed/census_race_2022.csv`
- `data/processed/component4_collection_summary.json`

**Notes**:
- **100% COMPLETE**: Successfully collected all 6 measures
- All 802 counties covered for ACS 2022 data
- 2000 Census data includes 804 counties (slight variation from 2022)
- Average population growth (2000-2022): 11.64%
- Average dependency ratio: 0.581
- Average median age: 42.0 years
- Average Millennial/Gen Z change: 5.27 percentage points
- Average % Hispanic: 5.35%
- Average % Non-White: 23.51%
- Extended Census client with 6 new methods for Component 4

### Phase 5: Component Index 5 - Education & Skill Index
**Status**: ✅ **FULLY COMPLETED** (All 5 measures collected)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-16

Data collection tasks (ALL 5 measures - see API_MAPPING.md for details):
- [x] Extend Census client for Component 5 data collection
- [x] Collect High School Attainment Rate (2022 ACS) - **802 records**
- [x] Collect Associate's Degree Attainment Rate (2022 ACS) - **802 records**
- [x] Collect Bachelor's Degree Attainment Rate (2022 ACS) - **802 records**
- [x] Collect Labor Force Participation Rate (2022 ACS) - **802 records**
- [x] Collect Percent of Knowledge Workers (2022 ACS) - **802 records**

**Total Records Collected**: 2,406 records for 802 counties across all 10 states

**Data Collected**:
- Census ACS 2022 Educational Attainment (B15003): 802 counties ✓
- Census ACS 2022 Labor Force Participation (B23025): 802 counties ✓
- Census ACS 2022 Knowledge Workers (S2401): 802 counties ✓

**Files Created**:
- `data/raw/census/census_education_detailed_2022_[STATE].json` (10 files)
- `data/raw/census/census_labor_force_2022_[STATE].json` (10 files)
- `data/raw/census/census_knowledge_workers_2022_[STATE].json` (10 files)
- `data/processed/census_education_attainment_2022.csv`
- `data/processed/census_labor_force_2022.csv`
- `data/processed/census_knowledge_workers_2022.csv`
- `data/processed/component5_collection_summary.json`

**Notes**:
- **100% COMPLETE**: Successfully collected all 5 measures
- All 802 counties covered for ACS 2022 data
- Average HS only attainment: 35.89%
- Average Associate's only attainment: 8.67%
- Average Bachelor's only attainment: 13.79%
- Average labor force participation rate: 56.03%
- Average knowledge workers: 33.33%
- Extended Census client with 3 new methods for Component 5
- Knowledge workers uses occupation data (S2401) as proxy instead of industry data due to API compatibility

### Phase 6: Component Index 6 - Infrastructure & Cost of Doing Business Index
**Status**: ⏳ **In Progress** (83% complete - 5 of 6 measures collected)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-17

Data collection tasks (6 measures - see API_MAPPING.md for details):
- [ ] Collect Broadband Internet Access (FCC Broadband Map)
- [x] Collect Interstate Highway Presence (USGS National Map Transportation API) - **391 counties with interstates**
- [x] Collect Count of 4-Year Colleges (Urban Institute IPEDS) - **345 counties, 902 colleges**
- [x] Collect Weekly Wage Rate (BLS QCEW) - **802 records**
- [x] Collect Top Marginal Income Tax Rate (Tax Foundation) - **10 records**
- [x] Collect Qualified Opportunity Zones (HUD ArcGIS) - **580 records**

**Total Records Collected**: 2,539 records across 5 measures

**Data Collected**:
- USGS Interstate Highways (2024): 802 counties analyzed, 391 counties with interstates (48.8%) ✓
- Urban Institute IPEDS 4-Year Colleges (2022): 345 counties with colleges, 902 total colleges ✓
- BLS QCEW Weekly Wage (2022): 802 counties ✓
- Tax Foundation State Tax Rates (2024): 10 states ✓
- HUD Opportunity Zones (2018): 580 counties with OZs, 1,709 total OZ tracts ✓

**Files Created**:
- `data/raw/usgs/county_interstate_presence.csv`
- `data/raw/usgs/interstate_highways.pkl` (cached GeoDataFrame)
- `data/raw/usgs/county_boundaries.pkl` (cached GeoDataFrame)
- `data/processed/usgs_county_interstate_presence.csv`
- `data/raw/urban_institute/ipeds_four_year_colleges_2022.csv`
- `data/processed/ipeds_four_year_colleges_by_county_2022.csv`
- `data/raw/qcew/qcew_weekly_wage_2022.csv`
- `data/processed/qcew_weekly_wage_2022.csv`
- `data/raw/tax_foundation/state_income_tax_rates_2024.json`
- `data/processed/state_income_tax_rates_2024.csv`
- `data/raw/hud/opportunity_zones_tracts.csv`
- `data/processed/hud_opportunity_zones_by_county.csv`
- `data/processed/component6_collection_summary.json`

**API Clients Created**:
- `scripts/api_clients/usgs_client.py` - USGS National Map Transportation API
- `scripts/api_clients/urban_institute_client.py` - Urban Institute Education Data Portal (IPEDS)
- `scripts/api_clients/hud_client.py` - HUD ArcGIS REST API

**Notes**:
- Interstate highway data collected via USGS National Map Transportation API
  - Downloaded 194,210 highway segments via ArcGIS REST API with pagination
  - Used Census TIGER 2024 county boundaries for spatial intersection
  - Implemented caching with pickled GeoDataFrames for performance
  - Runtime: ~10-15 minutes for initial download, <1 minute when cached
  - 391 of 802 counties (48.8%) have interstate highway presence
- 4-year college data collected via Urban Institute Education Data Portal API
- Urban Institute provides clean API access to IPEDS directory data with county FIPS codes
- API uses state-by-state queries (fips + inst_level) with local filtering for degree_granting
- Pennsylvania has most colleges (222), followed by North Carolina (139) and Georgia (112)
- Weekly wage data uses existing QCEW client from Component 1
- Tax rates are static state-level data (Tennessee: 0%, Delaware: 6.6%)
- OZ data collected via HUD ArcGIS REST API with pagination (8,765 tracts nationwide)
- 580 of 802 counties (72%) have at least one Opportunity Zone

### Phase 7: Component Index 7 - Quality of Life Index
**Status**: ⏳ In Progress - 100% Implemented, Pending Full Data Collection
**Last Updated**: 2025-11-17

Data collection tasks (8 measures - see API_MAPPING.md for details):
- [x] 7.1: Commute Time (Census ACS S0801) - **802 records**
- [x] 7.2: Housing Built Pre-1960 (Census ACS DP04) - **802 records**
- [x] 7.3: Relative Weekly Wage (BLS QCEW) - **802 records**
- [x] 7.4: Violent Crime Rate (FBI UCR) - **Implemented, test run: 1,207 crimes across 10 VA counties**
- [x] 7.5: Property Crime Rate (FBI UCR) - **Implemented, test run: 8,963 crimes across 10 VA counties**
- [x] 7.6: Climate Amenities (USDA ERS Natural Amenities Scale) - **805 records**
- [x] 7.7: Healthcare Access (Census CBP NAICS 621+622) - **771 records**
- [x] 7.8: Count of National Parks (NPS API with boundaries) - **802 records, 146 counties with parks**

**Files Created**:
- Extended `scripts/api_clients/census_client.py` with `get_commute_time()` and `get_housing_age()`
- Extended `scripts/api_clients/cbp_client.py` with `get_healthcare_employment()`
- Created `scripts/api_clients/nps_client.py` - NPS API client with boundary support
- Created `scripts/api_clients/fbi_cde_client.py` - **NEW** FBI Crime Data Explorer API client
- Created `scripts/data_collection/collect_component7.py` - Integrated collection script for measures 7.1-7.3, 7.6-7.8
- Created `scripts/data_collection/collect_measure_7_4_7_5_crime.py` - **NEW** FBI crime data collection script
- NPS park boundaries using spatial polygon intersection (255 park-county assignments across 146 counties)
- USDA ERS Natural Amenities Scale downloaded and processed (805 counties, includes VA independent cities)

**FBI Crime Data Implementation (Measures 7.4 & 7.5)**:
- API client with caching to minimize API calls (respects 1,000/day limit)
- Uses ORI9 codes to map 5,749 law enforcement agencies to counties
- Aggregates agency-level data to county level
- Test run successful: 30 VA agencies, 58 API calls, 10 counties
- **Full collection pending**: Requires ~11,498 API calls (2 per agency × 5,749 agencies)
- **Timeline estimate**: ~12 days with 1,000 call/day limit (with caching for re-runs)
- **Alternative explored**: Bulk download options from FBI CDE website (not yet pursued)
- See `FBI_CRIME_DATA_IMPLEMENTATION.md` for full details

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
**Phase**: Phase 7 - Component Index 7 (In Progress - 75% Complete)
**Date**: 2025-11-17

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
- ✅ Phase 3: Component Index 3 - Other Economic Prosperity Index (**ALL 5 measures complete, 3,936 records**)
  - ✓ Extended BEA client for CAINC1 table (total personal income)
  - ✓ All 5 measures collected via single `collect_component3.py` script
  - ✓ Integrated life expectancy collection from Zenodo into main component script
  - ✓ Collected 774 counties for proprietor income (BEA)
  - ✓ Collected 774 counties for income stability (BEA, 15 years)
  - ✓ Collected 812 counties for life expectancy (County Health Rankings via Zenodo)
  - ✓ Collected 802 counties for poverty rate (Census ACS)
  - ✓ Collected 774 counties for DIR income share (BEA)
- ✅ Phase 4: Component Index 4 - Demographic Growth & Renewal Index (**ALL 6 measures complete, 5,616 records**)
  - ✓ Extended Census client with 6 new methods for demographic data
  - ✓ Collected 804/802 counties for long-run population growth (2000-2022)
  - ✓ Collected 802 counties for dependency ratio (age distribution)
  - ✓ Collected 802 counties for median age
  - ✓ Collected 802 counties for Millennial/Gen Z balance change (2017-2022)
  - ✓ Collected 802 counties for percent Hispanic
  - ✓ Collected 802 counties for percent non-white
- ✅ Phase 5: Component Index 5 - Education & Skill Index (**ALL 5 measures complete, 2,406 records**)
  - ✓ Extended Census client with 3 new methods for education and labor data
  - ✓ Collected 802 counties for high school attainment rate (exclusive)
  - ✓ Collected 802 counties for associate's degree attainment rate (exclusive)
  - ✓ Collected 802 counties for bachelor's degree attainment rate (exclusive)
  - ✓ Collected 802 counties for labor force participation rate
  - ✓ Collected 802 counties for knowledge workers (occupation-based proxy)
- ✅ Phase 6: Component Index 6 - Infrastructure & Cost of Doing Business Index (**5 of 6 measures complete, 2,539 records**)
  - ✓ Collected 391 counties with interstate highways via USGS Transportation API (194,210 segments)
  - ✓ Collected 345 counties with 4-year colleges via Urban Institute IPEDS API (902 colleges)
  - ✓ Collected 802 counties for weekly wage rate (BLS QCEW 2022)
  - ✓ Collected 10 states for top marginal income tax rates (Tax Foundation 2024)
  - ✓ Collected 580 counties with Opportunity Zones via HUD ArcGIS API (1,709 OZ tracts)
  - ✓ Created `scripts/api_clients/usgs_client.py` - new USGS Transportation API client
  - ✓ Created `scripts/api_clients/urban_institute_client.py` - new Urban Institute API client
  - ✓ Created `scripts/api_clients/hud_client.py` - new HUD API client for Opportunity Zones
  - Created `collect_component6.py` script for measures 6.2-6.6
- ⏳ Phase 7: Component Index 7 - Quality of Life Index (**ALL 8 measures implemented, 6 fully collected, 2 pending full collection**)
  - ✓ Extended Census client with `get_commute_time()` and `get_housing_age()` methods
  - ✓ Extended CBP client with `get_healthcare_employment()` method
  - ✓ Created `scripts/api_clients/nps_client.py` - NPS API client with park boundary support
  - ✓ Created `scripts/api_clients/fbi_cde_client.py` - **NEW** FBI Crime Data Explorer API client
  - ✓ Collected 802 counties for commute time (Census ACS 2022)
  - ✓ Collected 802 counties for housing built pre-1960 (Census ACS 2022)
  - ✓ Collected 802 counties for relative weekly wage (BLS QCEW 2022)
  - ✓ Collected 805 counties for climate amenities (USDA ERS Natural Amenities Scale, 1941-1970 data)
  - ✓ Collected 771 counties for healthcare access (Census CBP 2021, NAICS 621+622)
  - ✓ Collected 802 counties for national parks (NPS API with boundary-based spatial intersection)
  - ✓ NPS boundaries mapped to 146 counties with parks (255 park-county assignments)
  - ✓ Created integrated `collect_component7.py` script for measures 7.1-7.3, 7.6-7.8
  - ✓ Implemented FBI crime data collection (measures 7.4 & 7.5) - test run successful
  - ⏳ FBI crime full collection pending: ~11,498 API calls needed (5,749 agencies × 2 crime types)

**Next Steps**:
1. **FBI Crime Data Collection Decision** (Measures 7.4 & 7.5)
   - Option A: Run full API collection (~12 days with 1,000/day limit)
   - Option B: Investigate bulk download from FBI CDE website
   - Option C: Collect incrementally (state-by-state or limited daily runs)
2. Continue through Component 8 - Social Capital Index (5 measures)
3. Return to complete Component 6 Measure 6.1 (Broadband)
4. Later: Validate and clean all component data
5. Later: Calculate growth rates and index scores

**Overall Progress**: 39 of 47 measures fully collected (83% complete), 41 of 47 implemented (87% complete)

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
