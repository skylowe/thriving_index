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
**Status**: ✅ **COMPLETE** (100% - All 6 measures collected)
**Target**: Collect county-level data for all 10 states
**Last Updated**: 2025-11-18

Data collection tasks (6 measures - see API_MAPPING.md for details):
- [x] Collect Broadband Internet Access (FCC BDC Public Data API) - **802 counties (avg: 99.96% coverage)**
- [x] Collect Interstate Highway Presence (USGS National Map Transportation API) - **391 counties with interstates**
- [x] Collect Count of 4-Year Colleges (Urban Institute IPEDS) - **345 counties, 902 colleges**
- [x] Collect Weekly Wage Rate (BLS QCEW) - **802 records**
- [x] Collect Top Marginal Income Tax Rate (Tax Foundation) - **10 records**
- [x] Collect Qualified Opportunity Zones (HUD ArcGIS) - **580 records**

**Total Records Collected**: 3,341 records across all 6 measures

**Data Collected**:
- FCC Broadband (Dec 2024): 802 counties, avg 99.96% coverage at ≥100/20 Mbps (FCC "served" tier) ✓
- USGS Interstate Highways (2024): 802 counties analyzed, 391 counties with interstates (48.8%) ✓
- Urban Institute IPEDS 4-Year Colleges (2022): 345 counties with colleges, 902 total colleges ✓
- BLS QCEW Weekly Wage (2022): 802 counties ✓
- Tax Foundation State Tax Rates (2024): 10 states ✓
- HUD Opportunity Zones (2018): 580 counties with OZs, 1,709 total OZ tracts ✓

**Files Created**:
- `data/raw/fcc/api_cache/county_summary_2024-12-31.csv` (processed county data, cached)
- `data/raw/fcc/api_cache/geo_summary_2024-12-31.zip` (raw ZIP download from API)
- `data/raw/fcc/api/fcc_broadband_100_20.csv`
- `data/processed/fcc_broadband_availability_100_20.csv`
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
- `scripts/api_clients/fcc_client.py` - **NEW** FCC BDC Public Data API (downloads geography summary ZIP)
- `scripts/api_clients/usgs_client.py` - USGS National Map Transportation API
- `scripts/api_clients/urban_institute_client.py` - Urban Institute Education Data Portal (IPEDS)
- `scripts/api_clients/hud_client.py` - HUD ArcGIS REST API

**Notes**:
- **FCC Broadband** data collected via FCC BDC Public Data API (implemented 2025-11-18)
  - Uses official FCC API with username/hash_value authentication
  - Downloads geography summary ZIP file (8.93 MB, 623K+ records across all geography types)
  - Automatically extracts and filters to county-level data (3,232 US counties)
  - Returns coverage at ≥100/20 Mbps (FCC official "served" tier)
  - Exceeds target of 100/10 Mbps, matches Nebraska methodology
  - Average coverage: 99.96% (range: 88.91% to 100%)
  - Requires FCC_BB_KEY and FCC_USERNAME in .Renviron
  - Caches processed results for reuse
  - Download time: ~10 seconds, Processing time: ~5 seconds
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
**Status**: ✅ **FULLY COMPLETED** (All 8 measures collected)
**Last Updated**: 2025-11-17

Data collection tasks (ALL 8 measures - see API_MAPPING.md for details):
- [x] 7.1: Commute Time (Census ACS S0801) - **802 records**
- [x] 7.2: Housing Built Pre-1960 (Census ACS DP04) - **802 records**
- [x] 7.3: Relative Weekly Wage (BLS QCEW) - **802 records**
- [x] 7.4: Violent Crime Rate (FBI UCR) - **804 counties, 5,749 agencies** ✅
- [x] 7.5: Property Crime Rate (FBI UCR) - **804 counties, 5,749 agencies** ✅
- [x] 7.6: Climate Amenities (USDA ERS Natural Amenities Scale) - **805 records**
- [x] 7.7: Healthcare Access (Census CBP NAICS 621+622) - **771 records**
- [x] 7.8: Count of National Parks (NPS API with boundaries) - **802 records, 146 counties with parks**

**Total Records Collected**: ~6,400 records across ALL 8 measures

**Files Created**:
- Extended `scripts/api_clients/census_client.py` with `get_commute_time()` and `get_housing_age()`
- Extended `scripts/api_clients/cbp_client.py` with `get_healthcare_employment()`
- Created `scripts/api_clients/nps_client.py` - NPS API client with boundary support
- Created `scripts/api_clients/fbi_cde_client.py` - FBI Crime Data Explorer API client with caching
- Created `scripts/data_collection/collect_component7.py` - Integrated collection script for ALL 8 measures (7.1-7.8)
  - Supports `--crime` flag to optionally include FBI crime data collection
  - Usage: `python collect_component7.py` (6 measures) or `python collect_component7.py --crime` (all 8 measures)
- `data/processed/fbi_crime_counties_2023.csv` - County-level crime data (804 counties)
- `data/processed/fbi_crime_agencies_2023.json` - Agency-level crime data (5,749 agencies)
- `data/processed/fbi_crime_summary_2023.json` - Collection summary and statistics

**FBI Crime Data Collection (Measures 7.4 & 7.5)** - ✅ **COMPLETE**:
- **Full collection completed**: 2025-11-17
- **Agencies processed**: 5,749 law enforcement agencies across all 10 states (100% success)
- **Counties covered**: 804 counties
- **API calls made**: 10,624 (no daily limit encountered)
- **Total violent crimes**: 248,963
- **Total property crimes**: 1,278,315
- **Cache size**: 89 MB of cached API responses for fast re-runs
- **Errors**: 0
- Uses ORI9 codes to map agencies to counties via ori_crosswalk.tsv
- Aggregates agency-level data to county level automatically
- 2023 full-year data (January - December)
- See `FBI_CRIME_DATA_IMPLEMENTATION.md` for implementation details

### Phase 8: Component Index 8 - Social Capital Index
**Status**: ✅ **FULLY COMPLETED** (All 5 measures collected - 100%)
**Last Updated**: 2025-11-18

Data collection tasks (5 measures - see API_MAPPING.md for details):
- [x] 8.1: Number of 501(c)(3) Organizations Per 1,000 Persons (IRS EO BMF) - **807 records**
- [x] 8.2: Volunteer Rate (Social Capital Atlas) - **782 records** ✅
- [x] 8.3: Social Associations Per 10,000 Population (County Health Rankings) - **804 records** ✅
- [x] 8.4: Voter Turnout (County Health Rankings - 2020 Presidential Election) - **804 records**
- [x] 8.5: Civic Organizations Density (Social Capital Atlas) - **782 records** ✅

**Total Records Collected**: 3,979 records across ALL 5 measures

**Data Collected**:
- IRS 501(c)(3) Organizations (2022): 807 counties ✓
  - Total organizations: 343,917 across all 10 states
  - Organizations mapped to counties: 298,734 (86.9% success rate)
  - Mean: 4.27 organizations per 1,000 persons
  - Median: 3.81 organizations per 1,000 persons
- Social Capital Atlas Volunteering Rate (2022): 782 counties ✓
  - Mean volunteering rate: 0.0636 (6.36%)
  - Median volunteering rate: 0.0602 (6.02%)
  - Range: 0.0152 (1.52%) to 0.2100 (21.00%)
  - **REPLACEMENT MEASURE**: County-level data from Social Capital Atlas instead of state-level AmeriCorps
- Social Associations (2025 CHR release): 804 counties ✓
  - Data source: County Business Patterns (NAICS 813 - membership associations)
  - Mean: 10.63 associations per 10,000 population
  - Median: 10.40 associations per 10,000 population
  - Range: 0.00 to 29.93
  - **REPLACEMENT MEASURE**: Replaced "Volunteer Hours Per Person" (state-level) with county-level data
- Voter Turnout (2020 Presidential Election): 804 counties ✓
  - Mean turnout: 63.67%
  - Median turnout: 63.07%
  - Range: 19.42% to 90.55%
- Social Capital Atlas Civic Organizations Density (2022): 782 counties ✓
  - Mean civic orgs density: 0.0176 per 1,000 Facebook users
  - Median civic orgs density: 0.0163 per 1,000 Facebook users
  - Range: 0.0046 to 0.0754 per 1,000 Facebook users
  - **REPLACEMENT MEASURE**: Continuous density measure instead of binary Tree City USA designation

**Files Created**:
- `scripts/api_clients/irs_client.py` - IRS Exempt Organizations API client
- `scripts/api_clients/social_capital_client.py` - Social Capital Atlas API client ✅ NEW
- `scripts/data_collection/collect_component8.py` - Component 8 collection script (ALL 5 measures: 8.1, 8.2, 8.3, 8.4, 8.5)
- `data/raw/irs/eo_[STATE]_raw.csv` - Raw IRS files (10 states, cached)
- `data/raw/irs/eo_[STATE]_501c3.json` - Filtered 501(c)(3) organizations (10 states)
- `data/raw/irs/zip_to_fips_crosswalk.json` - ZIP to county FIPS mapping (41,173 mappings)
- `data/raw/chr/chr_social_associations_2025_metadata.json` - County Health Rankings social associations metadata
- `data/raw/chr/chr_voter_turnout_2025_metadata.json` - County Health Rankings voter turnout metadata
- `data/raw/social_capital/social_capital_county.csv` - Social Capital Atlas county data (all US counties, cached) ✅ NEW
- `data/raw/social_capital/social_capital_atlas_metadata.json` - Social Capital Atlas metadata ✅ NEW
- `data/processed/component8_social_capital_2022.csv` - County-level data for ALL 5 measures (8.1, 8.2, 8.3, 8.4, 8.5)
- `data/processed/component8_collection_summary.json` - Collection summary for all 5 measures

**Notes**:
- **✅ 100% COMPLETE**: All 5 measures successfully collected
- **Measure 8.1**: 501(c)(3) organizations - 807 counties, 86.9% ZIP-FIPS mapping success
- **Measure 8.2 (NEW)**: Volunteering rate from Social Capital Atlas - 782 counties (97.5% coverage)
  - **REPLACEMENT**: County-level data from Meta/Facebook instead of state-level AmeriCorps data
  - Academic research published in Nature journal
  - Measures participation in volunteering/activism groups via Facebook data
- **Measure 8.3**: Social associations from County Health Rankings - 804 counties (100% coverage)
  - County-level membership associations data (NAICS 813)
  - Replaces original "Volunteer Hours Per Person" measure
- **Measure 8.4**: Voter turnout from County Health Rankings - 804 counties (99.6% coverage)
  - 2020 Presidential Election data
- **Measure 8.5 (NEW)**: Civic organizations density from Social Capital Atlas - 782 counties (97.5% coverage)
  - **REPLACEMENT**: Continuous density measure instead of binary Tree City USA designation
  - Measures number of civic organizations per 1,000 Facebook users
  - Academic research from Meta/Harvard/NYU/Stanford collaboration
- Used ZIP-to-FIPS crosswalk from GitHub (bgruber/zip2fips) for IRS organization geocoding
- Social Capital Atlas data provides comprehensive county-level social capital metrics
- All data integrated into single CSV file with consistent county FIPS codes

### Phase 10: Regional Data Aggregation
**Status**: ✅ **COMPLETE** (100% - All 47 measures aggregated across 94 regions)
**Last Updated**: 2025-11-18

**Objective**: Aggregate county-level data to regional level for all 47 measures across 94 regions.

Infrastructure Development:
- [x] Add county FIPS codes to all regional CSV files
- [x] Create multi-state RegionalDataManager class
- [x] Design aggregation configuration for all 47 measures
- [x] Build main regional aggregation script
- [x] Test aggregation system with sample components

**Files Created**:
- `scripts/add_fips_to_regions.py` - Adds FIPS codes to regional definitions
- `scripts/regional_data_manager.py` - Multi-state regional data management class
- `scripts/aggregation_config.py` - Aggregation methods for all 47 measures
- `scripts/aggregate_to_regional.py` - Main aggregation script (Components 1, 2, 8)
- `scripts/aggregate_components_3_7.py` - Component 3-7 aggregation script
- `scripts/fix_households_children_data.py` - Re-collected Component 1.4 with correct Census variable
- `scripts/complete_component2_aggregation.py` - Completed Component 2 (Herfindahl indexes)
- `data/regions/*.csv` - Updated with county_fips column (9 files)
- `data/regional/component1_growth_index_regional.csv` - Component 1 regional data (94 regions)
- `data/regional/component2_economic_opportunity_regional.csv` - Component 2 regional data (94 regions)
- `data/regional/component3_other_prosperity_regional.csv` - Component 3 regional data (94 regions)
- `data/regional/component4_demographic_growth_regional.csv` - Component 4 regional data (94 regions)
- `data/regional/component5_education_skill_regional.csv` - Component 5 regional data (94 regions)
- `data/regional/component6_infrastructure_cost_regional.csv` - Component 6 regional data (94 regions)
- `data/regional/component7_quality_of_life_regional.csv` - Component 7 regional data (94 regions)
- `data/regional/component8_social_capital_regional.csv` - Component 8 regional data (94 regions)

Component Aggregation Status:
- [x] Component 1: Growth Index (5 of 5 measures) ✅ **COMPLETE**
  - ✓ 1.1: Employment Growth
  - ✓ 1.2: Private Employment
  - ✓ 1.3: Wage Growth
  - ✓ 1.4: Households with Children Growth (data issue fixed - re-collected with S1101_C01_005E)
  - ✓ 1.5: DIR Income Growth
- [x] Component 2: Economic Opportunity & Diversity (7 of 7 measures) ✅ **COMPLETE**
  - ✓ 2.1: Entrepreneurial Activity
  - ✓ 2.2: Proprietors per 1,000
  - ✓ 2.3: Establishments per 1,000
  - ✓ 2.4: Nonemployer Share
  - ✓ 2.5: Industry Diversity (Herfindahl index)
  - ✓ 2.6: Occupation Diversity (Herfindahl index)
  - ✓ 2.7: Telecommuter Share
- [x] Component 3: Other Prosperity Index (5 of 5 measures) ✅ **COMPLETE**
  - ✓ 3.1: Proprietor Income Percentage
  - ✓ 3.2: Income Stability (CV)
  - ✓ 3.3: Life Expectancy
  - ✓ 3.4: Poverty Rate
  - ✓ 3.5: DIR Income Share
- [x] Component 4: Demographic Growth & Renewal (6 of 6 measures) ✅ **COMPLETE**
  - ✓ 4.1: Population Growth
  - ✓ 4.2: Dependency Ratio
  - ✓ 4.3: Median Age
  - ✓ 4.4: Millennial/Gen Z Balance Change
  - ✓ 4.5: Hispanic Percentage
  - ✓ 4.6: Non-White Percentage
- [x] Component 5: Education & Skill (5 of 5 measures) ✅ **COMPLETE**
  - ✓ 5.1: High School Attainment
  - ✓ 5.2: Associate's Degree Attainment
  - ✓ 5.3: Bachelor's Degree Attainment
  - ✓ 5.4: Labor Force Participation
  - ✓ 5.5: Knowledge Workers Percentage
- [x] Component 6: Infrastructure & Cost of Doing Business (6 of 6 measures) ✅ **COMPLETE**
  - ✓ 6.1: Broadband Access
  - ✓ 6.2: Interstate Highway Presence
  - ✓ 6.3: Four-Year Colleges Count
  - ✓ 6.4: Weekly Wage
  - ✓ 6.5: Income Tax Rate
  - ✓ 6.6: Opportunity Zones Count
- [x] Component 7: Quality of Life (8 of 8 measures) ✅ **COMPLETE**
  - ✓ 7.1: Mean Commute Time
  - ✓ 7.2: Housing Built Pre-1960
  - ✓ 7.3: Relative Weekly Wage
  - ✓ 7.4: Violent Crime Rate
  - ✓ 7.5: Property Crime Rate
  - ✓ 7.6: Climate Amenities Scale
  - ✓ 7.7: Healthcare Access
  - ✓ 7.8: National Parks Count
- [x] Component 8: Social Capital (5 of 5 measures) ✅ **COMPLETE**
  - ✓ 8.1: Nonprofits per 1,000
  - ✓ 8.2: Volunteer Rate
  - ✓ 8.3: Social Associations per 10k
  - ✓ 8.4: Voter Turnout
  - ✓ 8.5: Civic Organizations Density

**Regional Data Files Created** (All 8 components):
- `data/regional/component1_growth_index_regional.csv` (94 regions, 5 measures)
- `data/regional/component2_economic_opportunity_regional.csv` (94 regions, 7 measures)
- `data/regional/component3_other_prosperity_regional.csv` (94 regions, 5 measures)
- `data/regional/component4_demographic_growth_regional.csv` (94 regions, 6 measures)
- `data/regional/component5_education_skill_regional.csv` (94 regions, 5 measures)
- `data/regional/component6_infrastructure_cost_regional.csv` (94 regions, 6 measures)
- `data/regional/component7_quality_of_life_regional.csv` (94 regions, 8 measures)
- `data/regional/component8_social_capital_regional.csv` (94 regions, 5 measures)

**Aggregation Methods Summary** (47 measures):
- Recalculate from components: 24 measures (growth rates, ratios, per-capita)
- Weighted mean: 16 measures (rates, percentages)
- Sum: 4 measures (absolute counts)
- Max: 1 measure (binary indicators)
- State-level: 1 measure (income tax rate)
- Simple mean: 1 measure (amenity scale)

**Implementation Notes**:
- Component 1.4: Fixed data issue - re-collected with correct Census variable (S1101_C01_005E)
- Component 2: Implemented Herfindahl diversity indexes for industry and occupation diversity
- Component 3.2: Calculated income stability using coefficient of variation across 15-year time series
- Component 7.3: Calculated relative wage as region wage / state average wage using employment weights
- Component 7.6: Used " 1=Low  7=High" column from USDA ERS natural amenities file (1-7 scale)
- FIPS column detection: Fixed to check full FIPS codes (fips_str, FIPS Code) before state+county combinations

**Data Quality**:
- Coverage: 94/94 regions (100%) for all measures except college_count (93/94 - one region without colleges)
- All regional files validated with complete data
- Housing pre-1960 percentage shows >100% for some regions (data quality issue in source file)

**Completion Summary**:
✅ **ALL 47 MEASURES AGGREGATED SUCCESSFULLY**
- 8 regional component files created
- 94 regions covered (all 10 states)
- Ready for Phase 11: Peer Region Matching

### Phase 11: Peer Region Matching
**Status**: ✅ COMPLETE (100% - All 7 variables gathered)
**Last Updated**: 2025-11-18

**Objective**: Identify 5-8 comparable peer regions for each of the 6 rural Virginia regions using Mahalanobis distance matching.

**Methodology Update**: Modified from Nebraska's 6 variables to **7 variables** tailored for Appalachian region:
1. **Population** (regional size) ✅
2. **Percentage in micropolitan area** (urban proximity) ✅
3. **Farm income percentage** (agricultural economy) ✅
4. **Services employment percentage** (tourism, hospitality, service economy) ✅ *REPLACED ranch income*
5. **Manufacturing employment percentage** (industrial base) ✅
6. **Distance to MSAs** (geographic isolation) ✅
7. **Mining/extraction employment percentage** (coal/natural gas economy) ✅ *NEW - Appalachia-specific*

**Files Created**:
- `scripts/gather_peer_matching_variables.py` - Complete script gathering all 7 matching variables (603 lines)
- `data/peer_matching_variables.csv` - Complete dataset with 94 regions × 7 variables
- `data/raw/omb/metro_micro_delineation_2020.xls` - OMB metro/micro area definitions (cached)
- `data/raw/census/county_gazetteer_2022.txt` - County centroids for distance calculations (cached)
- `data/raw/bea/cainc4_farm_income_2022.json` - Farm proprietors income data (cached)
- `data/raw/bea/cainc1_total_income_2022.json` - Total personal income data (cached)

**Variables Summary** (All 7 Complete):
- [x] **Variable 1: Population** - Regional total population, 2022 (mean: 569,294; range: 81k - 4.96M)
- [x] **Variable 2: Micropolitan %** - % of population in micropolitan areas (mean: 19.64%; range: 0% - 91.44%)
- [x] **Variable 3: Farm income %** - Farm proprietors income as % of total personal income (mean: 0.70%; range: -0.34% - 4.44%)
- [x] **Variable 4: Services employment %** - Services sector employment share (mean: 82.99%)
- [x] **Variable 5: Manufacturing employment %** - Manufacturing sector employment share (mean: 16.30%)
- [x] **Variable 6: Distance to MSAs** - Haversine distance to nearest small MSA (mean: 34.0 mi) and large MSA (mean: 59.3 mi)
- [x] **Variable 7: Mining employment %** - Mining/extraction employment share (mean: 0.71%; 79 of 94 regions have mining)

**Data Sources**:
- OMB Metropolitan/Micropolitan Delineation File 2020 (665 micropolitan counties nationwide, 148 in our 10 states)
- BEA Regional API: CAINC4 Line 71 (farm income), CAINC1 Line 1 (total personal income)
- Census Gazetteer 2022: County centroids (lat/lon) for distance calculations
- Census CBP 2021: Employment by NAICS industry codes
- Census Population 2022: Regional aggregation and weighting

**Technical Implementation**:
- **Micropolitan calculation**: Matched counties to OMB delineations, calculated population-weighted % per region
- **Farm income**: BEA CAINC4 Line 71 / CAINC1 Line 1 ratio, aggregated to regional level
- **MSA distances**:
  - Calculated population-weighted regional centroids
  - Identified 365 small MSAs and 23 large MSAs using central county locations
  - Haversine formula for great-circle distances in miles
  - Small MSA: <1M population; Large MSA: >1M (Atlanta, Charlotte, Pittsburgh, Nashville, etc.)
- **Employment percentages**: Sum of three sectors (services + manufacturing + mining) as denominator

**Key Findings**:
- Wide variation in micropolitan exposure (0% for metro regions to 91% for Purchase Area, KY)
- Farm income minimal in most regions (<1%) but significant in rural KY/TN (up to 4.4%)
- Services dominate employment (83% average), manufacturing varies widely
- Mining concentrated in Appalachian regions (WV, eastern KY, southwest VA)
- Geographic isolation varies: some regions 6 miles from small MSA, others 75+ miles
- Distance to large MSAs ranges from 11 miles (Central Savannah River, GA near Augusta) to 193 miles (Southwest GA)

**Peer Region Selection Complete**:
- ✅ Implemented Mahalanobis distance algorithm using numpy
- ✅ Calculated covariance matrix and inverse for all 94 regions
- ✅ Selected 8 peer regions for each of 6 Virginia rural regions (48 total)
- ✅ Saved results to `data/peer_regions_selected.csv`

**Peer Selection Results**:
- **48 peer regions** selected across 6 Virginia rural regions
- **Mahalanobis distance range**: 0.689 to 2.349 (mean: 1.508)
- **State distribution**: Tennessee (10), South Carolina (9), Kentucky (8), Pennsylvania (5), Georgia (4), Maryland (4), Virginia (3), North Carolina (3), West Virginia (2)
- **Script**: `scripts/select_peer_regions.py` - Automated peer selection (280 lines)

**Sample Peer Matches**:
- **Southwest Virginia (51_1)**: Catawba SC, Northwest PA, Region VII WV, Northern Tier PA
- **Central/Western Virginia (51_2)**: First TN DD, Southeast TN DD, Southwest TN DD, Pee Dee SC
- **Southside Virginia (51_3)**: Lake Cumberland KY, Buffalo Trace KY, South Central TN, Northwest TN
- **Mary Ball Washington (51_6)**: MidSouth TN, Berkeley-Charleston SC, Tri-County Southern MD
- **Shenandoah Valley (51_8)**: Georgia Mountains, Eastern Carolina NC, Barren River KY, Santee Lynches SC
- **Central Virginia (51_9)**: Central Midlands SC, Greater Richmond VA, Berkeley-Charleston SC, Kentuckiana KY

**Next Steps**:
1. Review peer region selections for appropriateness and comparability
2. Calculate thriving index scores using peer region averages (Phase 12)
3. Generate regional comparison reports and visualizations

### Phase 12: Index Calculation and Analysis
**Status**: Not Started
- [ ] Implement index scoring methodology (100 = peer average, ±100 = ±1 SD)
- [ ] Calculate all 8 component indexes
- [ ] Calculate overall Thriving Index scores
- [ ] Generate comparison rankings
- [ ] Create visualizations and reports

## Current Status
**Phase**: **Phase 11: Peer Region Matching** ✅ COMPLETE
**Date**: 2025-11-18

**Completed**:
- ✓ Phase 0: Project setup and infrastructure
- ✓ Phase 1: Component Index 1 - Growth Index (8,654 records collected)
  - ✓ API clients created and tested (BEA, QCEW, Census)
  - ✓ All 5 measures collected for 802 counties across 10 states
  - ✓ QCEW client implemented using downloadable data files
  - ✓ Data cached for efficient reprocessing
  - ✓ **Data quality issue fixed**: Measure 1.4 re-collected with correct Census variable (S1101_C01_005E)
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
- ✅ Phase 6: Component Index 6 - Infrastructure & Cost of Doing Business Index (**ALL 6 measures complete, 3,341 records**) - **100% COMPLETE** ✨
  - ✓ Collected 802 counties for broadband internet access via FCC BDC Public Data API (avg 99.96% coverage)
  - ✓ Collected 391 counties with interstate highways via USGS Transportation API (194,210 segments)
  - ✓ Collected 345 counties with 4-year colleges via Urban Institute IPEDS API (902 colleges)
  - ✓ Collected 802 counties for weekly wage rate (BLS QCEW 2022)
  - ✓ Collected 10 states for top marginal income tax rates (Tax Foundation 2024)
  - ✓ Collected 580 counties with Opportunity Zones via HUD ArcGIS API (1,709 OZ tracts)
  - ✓ Created `scripts/api_clients/fcc_client.py` - new FCC Broadband Data Collection API client
  - ✓ Created `scripts/api_clients/usgs_client.py` - new USGS Transportation API client
  - ✓ Created `scripts/api_clients/urban_institute_client.py` - new Urban Institute API client
  - ✓ Created `scripts/api_clients/hud_client.py` - new HUD API client for Opportunity Zones
  - ✓ Created `collect_component6.py` script for all 6 measures (6.1-6.6)
- ✅ Phase 7: Component Index 7 - Quality of Life Index (**ALL 8 measures COMPLETE, 100%!**)
  - ✓ Extended Census client with `get_commute_time()` and `get_housing_age()` methods
  - ✓ Extended CBP client with `get_healthcare_employment()` method
  - ✓ Created `scripts/api_clients/nps_client.py` - NPS API client with park boundary support
  - ✓ Created `scripts/api_clients/fbi_cde_client.py` - FBI Crime Data Explorer API client
  - ✓ Collected 802 counties for commute time (Census ACS 2022)
  - ✓ Collected 802 counties for housing built pre-1960 (Census ACS 2022)
  - ✓ Collected 802 counties for relative weekly wage (BLS QCEW 2022)
  - ✓ Collected 805 counties for climate amenities (USDA ERS Natural Amenities Scale, 1941-1970 data)
  - ✓ Collected 771 counties for healthcare access (Census CBP 2021, NAICS 621+622)
  - ✓ Collected 802 counties for national parks (NPS API with boundary-based spatial intersection)
  - ✓ NPS boundaries mapped to 146 counties with parks (255 park-county assignments)
  - ✓ Created integrated `collect_component7.py` script for ALL 8 measures (7.1-7.8)
  - ✓ Script supports `--crime` flag to optionally include FBI crime data collection
  - ✓ **FBI Crime Data FULLY COLLECTED** (2025-11-17): 5,749 agencies, 804 counties, 10,624 API calls
  - ✓ Total violent crimes: 248,963 | Total property crimes: 1,278,315
  - ✓ No API rate limit encountered - full collection completed in single run
  - ✓ FBI crime data uses comprehensive caching (89 MB cache) for fast re-runs
- ✅ Phase 8: Component Index 8 - Social Capital Index (**ALL 5 measures complete, 3,979 records, 100%**)
  - ✓ Created `scripts/api_clients/irs_client.py` - IRS Exempt Organizations API client with ZIP-FIPS crosswalk
  - ✓ Created `scripts/api_clients/social_capital_client.py` - Social Capital Atlas API client ✅ NEW
  - ✓ Updated `scripts/data_collection/collect_component8.py` - Component 8 collection script (ALL 5 measures)
  - ✓ Measure 8.1: 501(c)(3) Organizations Per 1,000 Persons (807 counties, mean: 4.27 per 1,000)
  - ✓ Total organizations collected: 343,917 across all 10 states
  - ✓ Successfully mapped 298,734 organizations (86.9%) to counties using ZIP-FIPS crosswalk
  - ✓ Measure 8.2: Volunteer Rate from Social Capital Atlas (782 counties, mean: 6.36%) ✅ NEW
  - ✓ **REPLACEMENT**: County-level volunteering data instead of state-level AmeriCorps
  - ✓ Measure 8.3: Social Associations Per 10,000 Pop (804 counties, mean: 10.63 per 10k)
  - ✓ **REPLACEMENT**: County-level CBP data instead of "Volunteer Hours Per Person"
  - ✓ Measure 8.4: Voter Turnout - 2020 Presidential Election (804 counties, mean: 63.67%)
  - ✓ Measure 8.5: Civic Organizations Density from Social Capital Atlas (782 counties, mean: 0.0176 per 1k users) ✅ NEW
  - ✓ **REPLACEMENT**: Continuous density measure instead of binary Tree City USA
- ✅ Phase 9: Regional Definitions (**100% COMPLETE** - All 10 states defined)
  - ✓ Virginia: 9 GO Virginia regions (133 localities, 100% coverage)
  - ✓ Pennsylvania: 7 EDDs (52 counties, 78% coverage)
  - ✓ Maryland: 5 regional councils (15 counties, 63% coverage)
  - ✓ Delaware: No formal regions (3 counties, county-level only)
  - ✓ West Virginia: 11 regional planning councils (55 counties, 100% coverage)
  - ✓ Kentucky: 15 ADDs (119 counties, 99% coverage)
  - ✓ Tennessee: 9 development districts (94 counties, 99% coverage)
  - ✓ North Carolina: 16 COGs (100 counties, 100% coverage)
  - ✓ South Carolina: 10 COGs (46 counties, 100% coverage)
  - ✓ Georgia: 12 regional commissions (159 counties, 100% coverage)
  - ✓ Total: 94 regions covering 773 counties
- ✅ Phase 10: Regional Data Aggregation (**100% COMPLETE** - All 47 measures aggregated across 94 regions!)
  - ✓ Regional aggregation infrastructure complete
  - ✓ Added county FIPS codes to all regional CSV files
  - ✓ Created `scripts/regional_data_manager.py` - Multi-state regional data management
  - ✓ Created `scripts/aggregation_config.py` - Aggregation methods for all 47 measures
  - ✓ Created `scripts/aggregate_to_regional.py` - Main aggregation script
  - ✓ Created `scripts/aggregate_components_3_7.py` - Comprehensive aggregation for Components 3-7
  - ✓ Created `scripts/complete_component2_aggregation.py` - Herfindahl diversity indexes
  - ✓ Added `add_region_names()` and `ensure_fips_column()` helper methods
  - ✓ **Component 1 data issue fixed**: Re-collected measure 1.4 with correct Census variable
  - ✅ Component 1: 5/5 measures aggregated (growth index - COMPLETE)
  - ✅ Component 2: 7/7 measures aggregated (economic opportunity - COMPLETE)
  - ✅ Component 3: 5/5 measures aggregated (other prosperity - COMPLETE)
  - ✅ Component 4: 6/6 measures aggregated (demographic growth - COMPLETE)
  - ✅ Component 5: 5/5 measures aggregated (education & skill - COMPLETE)
  - ✅ Component 6: 6/6 measures aggregated (infrastructure - COMPLETE)
  - ✅ Component 7: 8/8 measures aggregated (quality of life - COMPLETE)
  - ✅ Component 8: 5/5 measures aggregated (social capital - COMPLETE)
  - ✓ Created 8 regional data files (94 regions each, all components complete)
- ⚙️ Phase 11: Peer Region Matching (**57% IN PROGRESS** - 4 of 7 variables gathered)
  - ✓ Methodology updated: 7 variables tailored for Appalachian region
  - ✓ Replaced "ranch income" with "services employment %"
  - ✓ Added "mining/extraction employment %" as 7th variable (Appalachia-specific)
  - ✓ Created `scripts/gather_peer_matching_variables.py` - variable gathering script
  - ✓ Variable 1: Population (mean: 569,294) - COMPLETE
  - ✓ Variable 4: Services employment % (mean: 82.99%) - COMPLETE
  - ✓ Variable 5: Manufacturing employment % (mean: 16.30%) - COMPLETE
  - ✓ Variable 7: Mining employment % (mean: 0.71%, 79/94 regions) - COMPLETE
  - ⏸ Variable 2: Micropolitan % - needs Census/OMB definitions
  - ⏸ Variable 3: Farm income % - needs BEA CAINC45 table
  - ⏸ Variable 6: Distance to MSAs - needs geospatial calculation

### Phase 9: Regional Definitions
**Status**: ✓ Complete for All 10 States
**Last Updated**: 2025-11-19

**Objective**: Define multi-county regions for Virginia and the 9 comparison states to enable regional aggregation and peer matching.

Virginia Regions (GO Virginia Framework):
- [x] Research regional frameworks for Virginia
- [x] Identify GO Virginia regions as optimal framework (9 economic development regions)
- [x] Extract complete county/city-to-region mappings from VEDP and DHCD sources
- [x] Create regional data file: `data/regions/virginia_go_regions.csv`
- [x] Create regional data management script: `scripts/regions.py`
- [x] Validate complete coverage: 133 localities (95 counties + 38 independent cities)
- [x] Identify 6 rural regions for analysis (excluding Northern VA, Hampton Roads, Greater Richmond)

**Virginia Regions Summary**:
- Region 1: Southwest Virginia (13 counties, 3 cities) - Rural
- Region 2: Central/Western Virginia (13 counties, 5 cities) - Rural
- Region 3: Southside Virginia (13 counties, 2 cities) - Rural
- Region 4: Greater Richmond (12 counties, 5 cities) - Metro
- Region 5: Hampton Roads (6 counties, 10 cities) - Metro
- Region 6: Mary Ball Washington Regional Council (14 counties, 1 city) - Rural
- Region 7: Northern Virginia (4 counties, 5 cities) - Metro
- Region 8: Shenandoah Valley (10 counties, 6 cities) - Rural
- Region 9: Central Virginia (10 counties, 1 city) - Rural

Comparison State Regions (EDA/EDD Framework):
- [x] Research EDA regions for Pennsylvania - 7 EDDs (52 of 67 counties)
- [x] Research EDA regions for Maryland - 5 regional councils (15 of 24 counties)
- [x] Research EDA regions for Delaware - No formal EDDs (3 counties, will use county-level only)
- [x] Research EDA regions for West Virginia - 11 regional planning councils (55 of 55 counties - 100%)
- [x] Research EDA regions for Kentucky - 15 ADDs (119 of 120 counties - 99%)
- [x] Research EDA regions for Tennessee - 9 development districts (94 of 95 counties - 99%)
- [x] Research EDA regions for North Carolina - 16 COGs (100 of 100 counties - 100%)
- [x] Research EDA regions for South Carolina - 10 COGs (46 of 46 counties - 100%)
- [x] Research EDA regions for Georgia - 12 regional commissions (159 of 159 counties - 100%)
- [x] Create regional data files for all comparison states (9 CSV files in data/regions/)
- [ ] Extend regional data management script for multi-state support (future enhancement)

**Total Regional Coverage**:
- **94 regions** covering **773 counties** across **10 states**
- States with 100% coverage: VA, WV, NC, SC, GA
- States with 99%+ coverage: KY, TN
- States with partial coverage (metro areas excluded): PA (78%), MD (63%)
- Delaware: No formal regions (county-level data only)

**Next Steps**:
1. ✅ **DATA COLLECTION COMPLETE**: All 47 measures collected!
2. ✅ **REGIONAL DEFINITIONS COMPLETE**: All 10 states defined (94 regions, 773 counties)
3. ✅ **REGIONAL AGGREGATION INFRASTRUCTURE COMPLETE**: Multi-state aggregation system built and tested
4. In Progress: Regional data aggregation for remaining components (9 of 47 measures aggregated)
5. Later: Validate and clean all component data
6. Later: Calculate growth rates and index scores
7. Later: Peer region matching using Mahalanobis distance

**Overall Progress**: ✅ **47 of 47 measures fully collected (100% COMPLETE!)**

## Data Confidence Summary
See API_MAPPING.md for complete details on each measure's confidence level:
- HIGH confidence measures: 45 of 47 (95.7%) ✅ (includes new Social Capital Atlas measures 8.2 & 8.5)
- MEDIUM confidence measures: 2 of 47 (4.3%)
- LOW confidence measures: 0 of 47 (0%)

**Note**: Two measures (8.2 and 8.5) upgraded from MEDIUM/LOW to HIGH by replacing original data sources with Social Capital Atlas county-level data.

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
