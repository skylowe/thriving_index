# Virginia Rural Thriving Index - Project Knowledge Base

## Project Summary
This project creates a Thriving Index for rural regions in Virginia, modeled after the Nebraska Thriving Index. The project collects county-level data for ALL counties in 10 states (Virginia, Pennsylvania, Maryland, Delaware, West Virginia, Kentucky, Tennessee, North Carolina, South Carolina, and Georgia) across 47 individual measures in 8 component indexes. Regional aggregation and peer region matching will occur after county-level data collection is complete.

## Methodology Overview

### Index Structure
The Thriving Index consists of 8 component indexes:
1. **Growth Index** - Measures economic and demographic growth trends
2. **Economic Opportunity & Diversity Index** - Evaluates economic diversity and opportunities
3. **Other Prosperity Index** - Assesses income equality and business dynamics
4. **Demographic Growth & Renewal Index** - Tracks population changes and migration
5. **Education & Skill Index** - Measures educational attainment and achievement
6. **Infrastructure & Cost of Doing Business Index** - Evaluates infrastructure and business costs
7. **Quality of Life Index** - Assesses housing, health, and safety
8. **Social Capital Index** - Measures civic engagement and community organizations

Each component index contains 5-8 individual measures for a total of 47 measures.

### Scoring Methodology
- Each measure is scored where:
  - **100** = Average of peer regions
  - **0** = One standard deviation below peer average
  - **200** = One standard deviation above peer average
- Measures are combined within each component index
- Component indexes can be analyzed individually or combined for an overall thriving score

### Peer Region Selection (Future Phase)
**Note**: Peer region selection will occur AFTER county-level data collection is complete.

Will use **Mahalanobis distance matching** to identify comparable rural regions based on 6 variables:
1. Population
2. Percentage in micropolitan area
3. Farm income percentage
4. Ranch income percentage
5. Manufacturing employment percentage
6. Distance to small and large MSAs (Metropolitan Statistical Areas)

Process:
1. First, collect county-level data for all 10 states
2. Then, aggregate counties into Virginia regions and comparison regions
3. Finally, use Mahalanobis distance to select 5-8 peer regions for each Virginia region

## Data Sources

### Primary APIs (HIGH Confidence)
- **BEA Regional API**: Bureau of Economic Analysis - employment, wages, income data
  - Uses CAINC5N table for income components (Component 1)
  - Uses CAINC4 table for proprietors income (Component 2)
  - Provides county-level economic data
  - Note: Returns 774 counties (Virginia independent cities aggregated)
- **BLS QCEW Downloadable Files**: Bureau of Labor Statistics Quarterly Census of Employment and Wages
  - Employment and wage data by industry
  - Uses downloadable ZIP files (~500MB), NOT Time Series API
  - Annual county-level data for all ownership types
- **Census ACS API**: American Community Survey
  - Demographic and household data (Component 1)
  - Occupation and telecommuter data (Component 2)
  - Education, poverty, housing data (future components)
- **Census BDS API**: Business Dynamics Statistics
  - Establishment births and deaths by county
  - Uses `YEAR` parameter (not `time`)
  - Endpoint: `https://api.census.gov/data/timeseries/bds`
- **Census CBP API**: County Business Patterns
  - Establishment counts and employment by industry
  - Industry diversity calculations (19 NAICS sectors)
  - Available at county level for all 802 counties
- **Census Nonemployer Statistics API**: Non-employer firm data
  - Self-employed without employees
  - Variables: NESTAB, NRCPTOT (changed in 2021+ from NONEMP, RCPTOT)

### Secondary APIs (MEDIUM Confidence)
- **USDA NASS**: Agricultural statistics
- **FCC**: Broadband availability data
- **HUD Building Permits**: Construction data
- **CDC WONDER**: Health statistics
- **FBI Crime Data Explorer**: Crime statistics
- **IRS Migration Data**: County-to-county migration flows
- **Census State & Local Government Finance**: Tax data

### Manual/Static Sources (LOW Confidence)
- State Department of Education data (ACT scores, reading proficiency)
- State election data (voter participation)

## Key Technical Details

### Geographic Scope
**Current Focus**: County-level data collection

- Collect data for **ALL counties** in 10 states:
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
- Regional aggregation will occur in a later phase after county data is collected
- Final analysis will compare multi-county rural regions in Virginia to peer regions in the other 9 states

### Time Periods
- Most measures use 5-year growth rates or changes
- Some measures are point-in-time (current year)
- Need to align time periods across different data sources

### Data Collection Strategy
1. Work component by component, starting with Component 1
2. Implement Python scripts for each API source
3. Store raw data in data/ folder
4. Validate and clean data before calculations
5. Move to next component only when current component is complete

## Component Index 1: Growth Index (✅ COMPLETE)

**Status**: Completed 2025-11-15
**Records**: 8,654 total records across 802 counties

Component Index 1 contains 5 measures, all with HIGH confidence levels:
- **1.1**: Growth in Total Employment (BEA CAINC5N, Line 10)
- **1.2**: Private Employment (BLS QCEW downloadable files)
- **1.3**: Growth in Private Wages Per Job (BLS QCEW)
- **1.4**: Growth in Households with Children (Census ACS Table S1101)
- **1.5**: Growth in Dividends, Interest and Rent Income (BEA CAINC5N, Line 46)

**Key Implementation Details**:
- BEA returns 774 counties (Virginia independent cities combined)
- QCEW uses downloadable ZIP files, not Time Series API
- QCEW files cached locally (~500MB per year)
- Census ACS collected by state (10 states × 2 time periods = 20 API calls)

See **API_MAPPING.md** for complete details on each measure.

## Component Index 2: Economic Opportunity & Diversity (✅ COMPLETE)

**Status**: Completed 2025-11-16
**Records**: 802 counties for most measures, 774 for BEA, 19 NAICS sectors for industry diversity

Component Index 2 contains 7 measures with HIGH confidence levels:
- **2.1**: Entrepreneurial Activity - Business Births/Deaths (Census BDS)
- **2.2**: Non-Farm Proprietors Per 1,000 (BEA CAINC4, Line 72)
- **2.3**: Employer Establishments Per 1,000 (Census CBP)
- **2.4**: Share of Non-Employer Workers (Census Nonemployer Stats)
- **2.5**: Industry Diversity (Census CBP, 19 NAICS sectors)
- **2.6**: Occupation Diversity (Census ACS Table S2401)
- **2.7**: Share of Telecommuters (Census ACS Table B08128)

**Key Implementation Details**:
- **BDS API Discovery**: Uses `YEAR` parameter instead of `time`
- **BEA Table Workaround**: CAEMP25 doesn't exist; used CAINC4 Line 72 (proprietors income) as proxy
- **Nonemployer API Changes**: Variable names changed in 2021+ (NESTAB not NONEMP, NRCPTOT not RCPTOT)
- **Industry Diversity**: Not all industries exist in all counties (346-801 records per sector is normal)

**New API Clients Created**:
- `scripts/api_clients/bds_client.py` - Business Dynamics Statistics
- `scripts/api_clients/cbp_client.py` - County Business Patterns
- `scripts/api_clients/nonemp_client.py` - Nonemployer Statistics
- Extended `bea_client.py` to support CAINC4 table
- Extended `census_client.py` for occupation and telecommuter data

See **API_MAPPING.md** for complete details on each measure.

## Component Index 3: Other Economic Prosperity (✅ 100% COMPLETE)

**Status**: Fully Completed 2025-11-17 (all 5 measures in single script)
**Records**: 3,936 total records across ALL 5 measures (774-812 counties)

Component Index 3 contains 5 measures, ALL with HIGH/MEDIUM confidence collected:
- **3.1**: Non-Farm Proprietor Personal Income (BEA CAINC4, Line 72)
- **3.2**: Personal Income Stability (BEA CAINC1, 15-year CV)
- **3.3**: Life Expectancy (County Health Rankings via Zenodo) ✅
- **3.4**: Poverty Rate (Census ACS Table S1701)
- **3.5**: Share of DIR Income (BEA CAINC5N/CAINC1 ratio)

**Key Implementation Details**:
- **BEA CAINC1 Extension**: Added support for CAINC1 table (total personal income)
- **Income Stability**: Collected 15 years (2008-2022) for coefficient of variation calculation
- **Life Expectancy**: Downloaded from Zenodo (DOI: 10.5281/zenodo.17584421) using API
- **Complete Coverage**: All 774 BEA counties have 15 years of income data
- **Poverty Data**: All 802 Census counties with no null values (avg: 15.92%)
- **DIR Share**: Average 14.93%, range 6.09% to 45.52%

**New Functionality Added**:
- Extended `bea_client.py` with `get_cainc1_data()` method
- Extended `bea_client.py` with `get_total_personal_income()` method
- Created `scripts/data_collection/collect_component3.py` with integrated life expectancy collection
- Life expectancy collection integrated directly into Component 3 script (downloads from Zenodo)

**Key Statistics**:
- Income Stability CV: Average 0.1734, Range 0.0566 to 0.3685
- Poverty Rate: Average 15.92%, all 802 counties covered
- Proprietor Income: 774 counties (BEA aggregates VA independent cities)
- DIR Income Share: Average 14.93% of total personal income
- Life Expectancy: Average 73.75 years, Range 64.32-88.91, 812 counties (99.9% complete)

See **API_MAPPING.md** for complete details on each measure.

## Python Implementation Requirements

### Cross-Platform Compatibility
- Must run on both Linux and Windows
- Use pathlib for path handling
- Use platform-independent file operations
- Test on both operating systems

### API Integration
- API keys stored in .Renviron file OR environment variables
- Python config.py reads from .Renviron if available, falls back to environment variables
- Implemented in `scripts/config.py` with `get_api_key()` helper function
- Implement retry logic for API calls
- Handle rate limiting appropriately
- Cache API responses to minimize redundant calls (especially QCEW files)

### Data Storage
- Use consistent file naming conventions
- Store raw API responses
- Store processed/cleaned data separately
- Use CSV or JSON for data files
- Document data file structures

### Code Organization
```
scripts/
├── config.py              # Configuration and API key management
├── api_clients/           # API wrapper classes
│   ├── bea_client.py      # BEA Regional API (CAINC5N, CAINC4)
│   ├── qcew_client.py     # BLS QCEW downloadable files
│   ├── census_client.py   # Census ACS API
│   ├── bds_client.py      # Census Business Dynamics Statistics
│   ├── cbp_client.py      # Census County Business Patterns
│   └── nonemp_client.py   # Census Nonemployer Statistics
├── data_collection/       # Data collection scripts
│   ├── collect_component1.py  # Growth Index (5 measures)
│   ├── collect_component2.py  # Economic Opportunity & Diversity (7 measures)
│   └── ...
├── processing/            # Data processing and cleaning
│   └── clean_data.py
└── analysis/              # Index calculation and analysis
    └── calculate_index.py

data/
├── raw/                   # Raw API responses
│   ├── bea/               # BEA employment, income, proprietors
│   ├── qcew/              # QCEW employment and wages (+ cache/)
│   ├── census/            # ACS households, occupation, telecommuter
│   ├── bds/               # Business dynamics births/deaths
│   ├── cbp/               # Establishments and industry employment
│   └── nonemp/            # Nonemployer firms
├── processed/             # Cleaned and processed data (CSV files)
└── results/               # Calculated indexes and scores
```

## API Documentation References

### BEA Regional API
- Base URL: https://apps.bea.gov/api/data
- Parameters: UserID, method, datasetname, TableName, LineCode, GeoFIPS, Year
- **CAINC5N** (Personal Income by Major Component):
  - Line 10: Total employment
  - Line 46: Dividends, interest, and rent
- **CAINC4** (Personal Income and Employment by Major Component):
  - Line 72: Nonfarm proprietors' income
- **Note**: CAEMP25 table does not exist in API (documented in Nebraska methodology but unavailable)

### BLS QCEW Downloadable Files
- **NOT using Time Series API** - county data not available that way
- Download URL: `https://data.bls.gov/cew/data/files/{year}/csv/{year}_annual_singlefile.zip`
- Files are ~500MB each, cached locally in `data/raw/qcew/cache/`
- Filters: `own_code == 5` (private), `industry_code == '10'` (all industries)
- Fields: `annual_avg_emplvl`, `total_annual_wages`, `avg_annual_pay`

### Census ACS API
- Base URL: https://api.census.gov/data/{year}/acs/acs5
- Subject Tables (S prefix): S1101 (households), S2401 (occupation)
- Detailed Tables (B prefix): B08128 (telecommuters)
- 5-year estimates for stability
- Geographic level: county (050)
- Collected by state: `for=county:*&in=state:{fips}`

### Census BDS API (Business Dynamics Statistics)
- Base URL: https://api.census.gov/data/timeseries/bds
- **IMPORTANT**: Uses `YEAR` parameter, NOT `time`
- Variables: ESTABS_ENTRY (births), ESTABS_EXIT (deaths), ESTAB (total)
- Geographic level: county
- Example query: `?get=ESTABS_ENTRY,ESTABS_EXIT,ESTAB&for=county:*&in=state:51&YEAR=2021&NAICS=00`

### Census CBP API (County Business Patterns)
- Base URL: https://api.census.gov/data/{year}/cbp
- Variables: ESTAB (establishments), EMP (employment), NAICS2017 (industry code)
- Industry diversity: 19 major NAICS sectors (11, 21, 22, 23, 31-33, 42, 44-45, 48-49, 51, 52, 53, 54, 55, 56, 61, 62, 71, 72, 81)
- NAICS 00 = total all industries
- Not all industries exist in all counties (expected variation)

### Census Nonemployer Statistics API
- Base URL: https://api.census.gov/data/{year}/nonemp
- **IMPORTANT**: Variable names changed in 2021+
  - Old: NONEMP, RCPTOT
  - New: NESTAB (establishments), NRCPTOT (receipts in $1,000)
- Variables: NAME, NESTAB, NRCPTOT, NAICS2017
- NAICS 00 = total all industries

## Important Formulas and Calculations

### Index Scoring Formula
```
score = 100 + ((value - peer_mean) / peer_std_dev) * 100
```
Where:
- value = region's value for the measure
- peer_mean = average value across peer regions
- peer_std_dev = standard deviation across peer regions

### Mahalanobis Distance
```
D = sqrt((x - μ)^T * Σ^-1 * (x - μ))
```
Where:
- x = vector of characteristics for candidate region
- μ = vector of characteristics for target region
- Σ = covariance matrix
- Σ^-1 = inverse of covariance matrix

### Growth Rate Calculation
```
growth_rate = ((value_current - value_base) / value_base) * 100
```
Typically using 5-year period (current year vs. 5 years prior)

## Data Quality Notes

### Confidence Levels
- **HIGH (36 measures)**: Well-documented APIs with reliable county-level data
- **MEDIUM (7 measures)**: APIs available but may have coverage or timeliness issues
- **LOW (4 measures)**: Requires manual data collection or state-specific sources

### Known Challenges
1. **State education data**: Not standardized across states, may need different approaches per state
2. **Broadband data**: FCC data has known accuracy issues
3. **Crime data**: FBI UCR transitioning to NIBRS, data availability varies
4. **IRS migration**: Annual release delay, limited to county-to-county flows
5. **Agricultural data**: USDA NASS has suppression for privacy in small counties
6. **BEA County Coverage**: Returns 774 counties (not 802) due to Virginia independent cities being aggregated
7. **API Parameter Discovery**: Census APIs not always well-documented (e.g., BDS uses YEAR not time)
8. **Variable Name Changes**: Census variable names changed between API versions (e.g., Nonemployer 2021+)

### Data Validation Strategies
- Cross-check totals against published reports
- Verify geographic codes match counties
- Check for outliers and anomalies
- Ensure time period alignment across sources
- Document any data gaps or substitutions

## Project File Descriptions

### API_MAPPING.md
Comprehensive mapping of all 47 measures to data sources. Each measure includes:
- Description
- Data source and API endpoint
- Confidence level
- Specific variable codes and table references
- Calculation formulas
- Time period specifications

### PROJECT_PLAN.md
Living document tracking project progress:
- Implementation phases (0-10)
- Current status and next steps
- Task checklists for each component
- Data collection targets (all counties in 10 states)
- Technical dependencies and requirements
- References API_MAPPING.md for variable details

### CLAUDE.md (this file)
Project knowledge base containing:
- Methodology overview
- Technical implementation details
- API documentation
- Formulas and calculations
- Data quality notes
- Design decisions and rationale

## Design Decisions and Rationale

### Why Component-by-Component Approach?
1. Reduces complexity by focusing on 5-8 measures at a time
2. Allows validation of methodology before scaling
3. Provides early deliverables (can analyze Component 1 while working on others)
4. Easier debugging and error correction
5. Better alignment with iterative development

### Why Python?
1. Excellent API libraries (requests, pandas)
2. Strong data analysis ecosystem (numpy, scipy, pandas)
3. Cross-platform compatibility
4. Easy to read and maintain
5. Good for both data collection and analysis

### Why Store Raw API Responses?
1. Enables re-processing without re-fetching
2. Provides audit trail
3. Reduces API calls during development
4. Allows validation against original source
5. Helpful for debugging

## Lessons Learned from Implementation

### Component 1 & 2 Implementation (Completed)

**API Discovery and Documentation**:
- Census BDS API documentation incomplete - discovered `YEAR` parameter through testing
- BEA table CAEMP25 doesn't exist despite being referenced in Nebraska methodology
- Census Nonemployer API variable names changed in 2021+ without clear documentation
- QCEW Time Series API doesn't support county-level data - must use downloadable files

**Data Availability Insights**:
- BEA consistently returns 774 counties (Virginia independent cities aggregated) - expected behavior
- Industry diversity naturally varies by county (not all industries exist everywhere)
- County-level suppression is minimal for most measures (802 counties usually available)

**Technical Approaches That Worked**:
- Environment variable fallback for API keys provides flexibility across environments
- Caching large downloads (QCEW files) saves significant time during development
- State-by-state API calls for Census data provides better error handling
- Storing both raw JSON and processed CSV enables reproducibility

**Code Quality Practices**:
- Separate API clients for each data source improves maintainability
- Consistent file naming patterns (e.g., `{source}_{measure}_{STATE}_{year}.json`) helps organization
- Summary JSON files document collection completeness and aid validation

## Component Index 4: Demographic Growth & Renewal (✅ 100% COMPLETE)

**Status**: Fully Completed 2025-11-16
**Records**: 5,616 total records across ALL 6 measures (802-804 counties)

Component Index 4 contains 6 measures, ALL with HIGH confidence collected:
- **4.1**: Long-Run Population Growth (Census 2000 + ACS 2022)
- **4.2**: Dependency Ratio (Census ACS age distribution)
- **4.3**: Median Age (Census ACS)
- **4.4**: Millennial and Gen Z Balance Change (Census ACS 2017-2022)
- **4.5**: Percent Hispanic (Census ACS)
- **4.6**: Percent Non-White (Census ACS)

**Key Implementation Details**:
- Extended Census client with 6 new methods for demographic data
- 2000 Decennial Census + 2022 ACS 5-year for population growth
- Detailed age distribution (B01001) for dependency ratio and generational change
- Separate Hispanic (B03003) and Race (B02001) data for diversity measures
- Complete coverage: 802-804 counties across all 10 states

**New Functionality Added**:
- Extended `census_client.py` with `get_decennial_population_2000()` method
- Extended `census_client.py` with `get_population_total()` method
- Extended `census_client.py` with `get_age_distribution()` method
- Extended `census_client.py` with `get_median_age()` method
- Extended `census_client.py` with `get_hispanic_data()` method
- Extended `census_client.py` with `get_race_data()` method
- Created `scripts/data_collection/collect_component4.py`

**Key Statistics**:
- Population Growth 2000-2022: Average 11.64% across all counties
- Dependency Ratio: Average 0.581 (dependents per working-age person)
- Median Age: Average 42.0 years
- Millennial/Gen Z Change: Average +5.27 percentage points (2017-2022)
- Percent Hispanic: Average 5.35% across all counties
- Percent Non-White: Average 23.51% across all counties

See **API_MAPPING.md** for complete details on each measure.

## Component Index 5: Education & Skill (✅ 100% COMPLETE)

**Status**: Fully Completed 2025-11-16
**Records**: 2,406 total records across ALL 5 measures (802 counties)

Component Index 5 contains 5 measures, ALL with HIGH confidence collected:
- **5.1**: High School Attainment Rate (exclusive - HS/GED only)
- **5.2**: Associate's Degree Attainment Rate (exclusive - Associate's only)
- **5.3**: Bachelor's Degree Attainment Rate (exclusive - Bachelor's only)
- **5.4**: Labor Force Participation Rate
- **5.5**: Percent of Knowledge Workers

**Key Implementation Details**:
- Extended Census client with 3 new methods for education and workforce data
- Educational attainment uses B15003 table for exclusive categories (highest level only)
- Labor force participation from B23025 table
- Knowledge workers uses S2401 occupation table as proxy
- Complete coverage: 802 counties across all 10 states

**New Functionality Added**:
- Extended `census_client.py` with `get_education_detailed()` method (B15003)
- Extended `census_client.py` with `get_labor_force_participation()` method (B23025)
- Extended `census_client.py` with `get_knowledge_workers()` method (S2401)
- Created `scripts/data_collection/collect_component5.py`

**Key Statistics**:
- High School Only Attainment: Average 35.89%
- Associate's Degree Only Attainment: Average 8.67%
- Bachelor's Degree Only Attainment: Average 13.79%
- Labor Force Participation Rate: Average 56.03%
- Knowledge Workers: Average 33.33%

**Technical Notes**:
- Knowledge workers (5.5) uses occupation-based proxy (management/professional/science/arts from S2401) instead of industry-based approach (C24030) due to API variable compatibility issues
- Educational attainment measures use EXCLUSIVE categories matching Nebraska methodology exactly

See **API_MAPPING.md** for complete details on each measure.

## Next Steps

### Current Status: Component 7 In Progress (62.5% Complete)

**Completed**:
- ✅ Component 1: Growth Index (5/5 measures, 8,654 records) - **100% COMPLETE**
- ✅ Component 2: Economic Opportunity & Diversity (7/7 measures, 802+ counties) - **100% COMPLETE**
- ✅ Component 3: Other Prosperity Index (5/5 measures, 3,936 records) - **100% COMPLETE**
- ✅ Component 4: Demographic Growth & Renewal (6/6 measures, 5,616 records) - **100% COMPLETE**
- ✅ Component 5: Education & Skill (5/5 measures, 2,406 records) - **100% COMPLETE**
- ✅ Component 6: Infrastructure & Cost of Doing Business (5/6 measures, 2,539 records) - **83% COMPLETE**
- ⏳ Component 7: Quality of Life (5/8 measures, ~4,000 records) - **62.5% COMPLETE**

**Progress Summary**: 38 of 47 measures collected (81% complete)

**Next Implementation**:
1. **Complete Component 7: Quality of Life Index** (3 remaining measures)
   - 7.4: Crime Rate (FBI Crime Data Explorer - HIGH confidence)
   - 7.5: Air Quality Index (EPA Air Quality System - MEDIUM confidence)
   - 7.6: Recreational Amenities (Census CBP + USGS GNIS - MEDIUM confidence)

2. **Continue Through Component 8**
   - Component 8: Social Capital Index (5 measures - state election data, Census CBP)
   - Maintain component-by-component approach
   - Document API discoveries and workarounds
   - Validate data quality at each step

3. **Return to Component 6 Measure 6.1** (Broadband Internet Access)
   - Complete final measure for Component 6

4. **Later Phases** (After all data collected):
   - Regional aggregation and definition
   - Mahalanobis distance peer matching
   - Index calculation and scoring
   - Visualization and reporting

## Resources and References

- Nebraska Thriving Index Report (Thriving_Index.pdf)
- Comparison Regions Methodology (Comparison_Regions.pdf)
- API Mapping Documentation (API_MAPPING.md)
- BEA Regional API: https://apps.bea.gov/api/
- BLS API: https://www.bls.gov/developers/
- Census API: https://www.census.gov/data/developers.html

## Key Project Decisions

### County-Level Data Collection First
- Collect data for ALL counties in all 10 states before any regional aggregation
- This provides maximum flexibility for later defining regions
- Avoids having to re-collect data if region definitions change
- Allows validation of data quality at granular level

### API Keys in .Renviron or Environment Variables
- API keys stored in .Renviron file in project root (preferred)
- Python `config.py` falls back to environment variables if .Renviron unavailable
- Implemented via `get_api_key()` helper function
- Keeps sensitive keys out of version control
- Provides flexibility across different deployment environments

### Component-by-Component Approach
- Complete Component 1 (all 5 measures, all counties, all states) before moving to Component 2
- Validates methodology and data pipeline early
- Easier debugging and quality control
- Provides working subset for testing regional aggregation

## Updates Log

**2025-11-15**: Initial project setup
- Created PROJECT_PLAN.md and CLAUDE.md
- Clarified county-level data collection strategy (all 10 states)
- Documented API key management (.Renviron and environment variables)

**2025-11-15**: Component 1 Implementation
- Created BEA, QCEW, and Census API clients
- Implemented `collect_component1.py` script
- Successfully collected all 5 Growth Index measures
- Total: 8,654 records across 802 counties
- Key discovery: QCEW requires downloadable files, not Time Series API

**2025-11-16**: Component 2 Implementation
- Created BDS, CBP, and Nonemployer API clients
- Extended BEA client for CAINC4 table support
- Extended Census client for occupation and telecommuter data
- Implemented `collect_component2.py` script
- Successfully collected all 7 Economic Opportunity & Diversity measures
- Key discoveries:
  - BDS API uses `YEAR` parameter (not `time`)
  - BEA CAEMP25 table doesn't exist; used CAINC4 Line 72 as workaround
  - Nonemployer API variable names changed in 2021+ (NESTAB/NRCPTOT)
- Total: 802 counties for most measures, 19 NAICS sectors for industry diversity

**2025-11-16**: Documentation Updates (after Component 2)
- Updated PROJECT_PLAN.md with Component 2 completion status
- Updated API_MAPPING.md with data file locations and implementation notes
- Updated CLAUDE.md with lessons learned and current project state
- Ready to begin Component 3: Other Prosperity Index

**2025-11-16**: Component 3 Implementation
- Extended BEA client with CAINC1 table support (total personal income)
- Added `get_cainc1_data()` and `get_total_personal_income()` methods to BEA client
- Implemented `collect_component3.py` script
- Successfully collected 4 of 5 Other Prosperity measures
- Key achievements:
  - Income Stability: 15 years of data (2008-2022) for all 774 BEA counties
  - Poverty Rate: Complete coverage of all 802 counties, no null values
  - DIR Income Share: Calculated ratio from two BEA tables (CAINC5N + CAINC1)
  - Proprietor Income: 774 counties with complete data
- Total: 3,124 records across 4 measures
- Measure 3.3 (Life Expectancy) deferred - requires bulk download from County Health Rankings

**2025-11-16**: Documentation Updates (after Component 3, part 1)
- Updated PROJECT_PLAN.md with Component 3 completion status (4 of 5 measures)
- Updated API_MAPPING.md with Component 3 data collection details
- Updated CLAUDE.md with Component 3 section and updated next steps
- Ready to begin Component 4: Demographic Growth & Renewal Index

**2025-11-16**: Life Expectancy Data Collection (Component 3.3)
- Created `collect_life_expectancy.py` script for Zenodo API download
- Successfully downloaded County Health Rankings 2025 data (50.1 MB ZIP file)
- Extracted and processed life expectancy data from analytic_data2025_v2.csv
- Collected 812 counties with 99.9% data completeness
- Key achievements:
  - Automated download from Zenodo (DOI: 10.5281/zenodo.17584421)
  - Handled ZIP extraction and file parsing
  - Filtered to 10 target states (VA, PA, MD, DE, WV, KY, TN, NC, SC, GA)
  - Mean life expectancy: 73.75 years, range: 64.32-88.91 years
- Total Component 3 records: 3,936 (increased from 3,124)
- **Component 3 is now 100% COMPLETE** with all 5 measures collected

**2025-11-16**: Documentation Updates (after Component 3 completion)
- Updated PROJECT_PLAN.md to reflect 100% completion of Component 3
- Updated API_MAPPING.md with life expectancy data collection details
- Updated CLAUDE.md with Component 3 full completion status
- All three components (1, 2, 3) are now fully complete: 17 measures, ~16,500 total records

**2025-11-16**: Component 4 Implementation
- Extended Census client with 6 new methods for demographic data
- Added `get_decennial_population_2000()` method for 2000 Census data
- Added `get_population_total()` method for current ACS population
- Added `get_age_distribution()` method for detailed age breakdowns
- Added `get_median_age()` method for median age data
- Added `get_hispanic_data()` and `get_race_data()` methods for diversity measures
- Implemented `collect_component4.py` script
- Successfully collected all 6 Demographic Growth & Renewal measures
- Key achievements:
  - Population Growth: 22-year period (2000-2022) for 804/802 counties
  - Dependency Ratio: Complete age distribution for 802 counties
  - Median Age: All 802 counties with average 42.0 years
  - Millennial/Gen Z Change: 2017-2022 comparison for generational shift analysis
  - Diversity Measures: Hispanic (5.35% avg) and Non-White (23.51% avg) for all 802 counties
- Total: 5,616 records across 6 measures
- **Component 4 is now 100% COMPLETE** with all 6 measures collected

**2025-11-16**: Documentation Updates (after Component 4 completion)
- Updated PROJECT_PLAN.md with Component 4 completion status (all 6 measures)
- Updated API_MAPPING.md with Component 4 data collection details
- Updated CLAUDE.md with Component 4 section and updated next steps
- All four components (1, 2, 3, 4) are now fully complete: 23 measures, ~22,100 total records

**2025-11-16**: Component 5 Implementation
- Extended Census client with 3 new methods for education and workforce data
- Added `get_education_detailed()` method for exclusive educational categories (B15003)
- Added `get_labor_force_participation()` method for labor force data (B23025)
- Added `get_knowledge_workers()` method using occupation proxy (S2401)
- Implemented `collect_component5.py` script
- Successfully collected all 5 Education & Skill measures
- Key achievements:
  - Educational Attainment: Exclusive categories (HS only, Associate's only, Bachelor's only) for 802 counties
  - Labor Force Participation: Average 56.03% for all 802 counties
  - Knowledge Workers: Average 33.33% using occupation-based proxy for all 802 counties
  - All measures use HIGH confidence Census ACS data sources
- Total: 2,406 records across 5 measures
- **Component 5 is now 100% COMPLETE** with all 5 measures collected
- Technical note: Knowledge workers uses S2401 occupation table instead of C24030 industry table due to API compatibility

**2025-11-16**: Documentation Updates (after Component 5 completion)
- Updated PROJECT_PLAN.md with Component 5 completion status (all 5 measures)
- Updated API_MAPPING.md with Component 5 data collection details and collection status section
- Updated CLAUDE.md with Component 5 section and updated next steps
- All five components (1, 2, 3, 4, 5) are now fully complete: 28 measures, ~24,500 total records (60% of project)

## Component Index 6: Infrastructure & Cost of Doing Business (⏳ NEAR COMPLETE - 83% COMPLETE)

**Status**: Near Complete 2025-11-17
**Records**: 2,539 total records across 5 of 6 measures

Component Index 6 contains 6 measures. Currently collected 5 measures (6.2, 6.3, 6.4, 6.5, and 6.6):
- **6.1**: Broadband Internet Access (FCC - NOT YET COLLECTED)
- **6.2**: Interstate Highway Presence (USGS + Census TIGER) ✅
- **6.3**: Count of 4-Year Colleges (Urban Institute IPEDS) ✅
- **6.4**: Weekly Wage Rate (BLS QCEW) ✅
- **6.5**: Top Marginal Income Tax Rate (Tax Foundation) ✅
- **6.6**: Qualified Opportunity Zones (HUD ArcGIS) ✅

**Key Implementation Details**:
- Interstate highway data from USGS National Map Transportation API + Census TIGER county boundaries
- Downloaded 194,210 interstate highway segments nationwide via USGS API
- Performed spatial intersection analysis to identify counties with interstates
- 4-year college data from Urban Institute Education Data Portal API (IPEDS directory)
- BLS QCEW weekly wage data uses same downloadable files as Component 1
- State income tax rates are static, state-level data from Tax Foundation
- Opportunity Zones collected via HUD ArcGIS REST API (8,765 tracts nationwide)
- 391 of 802 counties have interstate highways (48.8%)
- 345 counties have 4-year colleges (902 total colleges, avg: 2.61 per county with colleges)
- All 802 counties have weekly wage data (avg: $931.61, range: $0-$2,241)
- All 10 states have tax rate data (avg: 4.66%, range: 0% TN to 6.6% DE)
- 580 counties have Opportunity Zones (1,709 OZ tracts total, avg: 2.95 per county)

**New Functionality Added**:
- Created `scripts/api_clients/usgs_client.py` - new USGS Transportation API client
  - USGSTransportationClient class for National Map Transportation data
  - get_interstate_highways() - fetch all 194,210 interstate highway segments with pagination
  - download_county_boundaries() - fetch Census TIGER 2024 county shapefiles
  - identify_counties_with_interstates() - perform spatial intersection analysis
  - Includes caching (pickled GeoDataFrames) for faster subsequent runs
- Created `scripts/api_clients/urban_institute_client.py` - new Urban Institute API client
  - UrbanInstituteClient class for Education Data Portal (IPEDS)
  - get_four_year_colleges() - fetch 4-year degree-granting institutions with pagination
  - aggregate_colleges_by_county() - aggregate institution data to county level
  - State-by-state queries with local filtering (avoids API 503 errors)
  - Pagination support (up to 10,000 records per page)
- Created `scripts/api_clients/hud_client.py` - new HUD API client
  - HUDClient class with methods for Opportunity Zones data
  - get_opportunity_zones_count() - get total OZ tract count
  - get_opportunity_zones() - fetch all OZ tracts with pagination and state filtering
  - aggregate_oz_by_county() - aggregate tract data to county level
  - Includes retry logic, error handling, and testable main block
- Created `scripts/data_collection/collect_component6.py` for measures 6.2-6.6
- Utilized existing QCEW client (already had weekly wage field)
- Created static tax rate data structure with 2024 rates
- Installed geopandas, shapely, and related geospatial libraries for spatial analysis

**Key Statistics**:
- Interstate Highways: 391 of 802 counties (48.8%) have interstates
  - Downloaded and processed 194,210 highway segments nationwide
  - Runtime: ~10-15 minutes for full spatial analysis
- 4-Year Colleges: 902 colleges across 345 counties (43% of counties have colleges)
  - College Distribution: Pennsylvania (222), North Carolina (139), Georgia (112)
- Weekly Wage Rate: Average $931.61, 802 counties covered
- Tax Rates: 10 states, range 0% (Tennessee - no income tax) to 6.6% (Delaware)
- Opportunity Zones: 580 counties with OZs, 1,709 total OZ tracts across 10 states
  - OZ Distribution: Pennsylvania (300), Georgia (260), North Carolina (252), Virginia (213)

**Remaining Measures**:
- 6.1: Broadband (FCC bulk download or API)

See **API_MAPPING.md** for complete details on each measure.

## Component Index 7: Quality of Life (⏳ 62.5% COMPLETE)

**Status**: In Progress 2025-11-17
**Records**: ~4,000 total records across 5 of 8 measures

Component Index 7 contains 8 measures. Currently collected 5 measures (7.1, 7.2, 7.3, 7.7, and 7.8):
- **7.1**: Commute Time (Census ACS S0801) ✅
- **7.2**: Housing Built Pre-1960 (Census ACS DP04) ✅
- **7.3**: Relative Weekly Wage (BLS QCEW) ✅
- **7.4**: Crime Rate (FBI Crime Data Explorer - NOT YET COLLECTED)
- **7.5**: Air Quality Index (EPA Air Quality System - NOT YET COLLECTED)
- **7.6**: Recreational Amenities (Census CBP + USGS GNIS - NOT YET COLLECTED)
- **7.7**: Healthcare Access (Census CBP NAICS 621+622) ✅
- **7.8**: Count of National Parks (NPS API with boundaries) ✅

**Key Implementation Details**:
- Extended Census client with `get_commute_time()` and `get_housing_age()` methods
- Extended CBP client with `get_healthcare_employment()` method
- Created NPS API client with park boundary support (spatial polygon intersection)
- Commute time: Average travel time to work in minutes (Census ACS 2022)
- Housing Pre-1960: Percentage of housing units built before 1960 (Census ACS 2022)
- Relative Weekly Wage: County wage / state average wage ratio (BLS QCEW 2022)
- Healthcare Access: Employment in NAICS 621 (ambulatory) + 622 (hospitals) per capita
- National Parks: NPS API with boundary-based spatial intersection to assign parks to ALL counties they touch
- All 802 counties covered for commute time, housing age, and weekly wage
- 771 counties have healthcare employment data
- 146 counties (18.2%) have national parks using boundary-based approach

**New Functionality Added**:
- Extended `scripts/api_clients/census_client.py` with Component 7 methods
  - `get_commute_time()` - Census ACS Table S0801 (mean travel time to work)
  - `get_housing_age()` - Census ACS Table DP04 (housing units by year built)
- Extended `scripts/api_clients/cbp_client.py` with Component 7 methods
  - `get_healthcare_employment()` - Census CBP for NAICS 621 and 622
- Created `scripts/api_clients/nps_client.py` - **NEW** NPS API client
  - NPSClient class for National Park Service data
  - `get_all_parks()` - fetch parks with pagination (state filtering)
  - `get_park_boundary()` - fetch park boundary GeoJSON from `/mapdata/parkboundaries/{parkCode}` endpoint
  - `parse_park_location()` - extract park location metadata
  - Full support for GeoJSON FeatureCollection boundary geometries
- Created `scripts/data_collection/collect_component7.py` - **INTEGRATED collection script**
  - Collects all 5 completed measures in single script run
  - Includes NPS collection with spatial analysis (previously in separate script)
  - `collect_commute_time()` - Census ACS commute data
  - `collect_housing_age()` - Census ACS housing age data
  - `collect_relative_weekly_wage()` - BLS QCEW wage data with state-level aggregation
  - `collect_healthcare_employment()` - Census CBP healthcare establishments
  - `collect_nps_parks()` - NPS parks with boundary-based spatial intersection
  - `load_county_boundaries()` - Load/cache Census TIGER county boundaries for spatial analysis
  - Integrated workflow similar to Component 3 (all measures in one script)
- Installed geopandas and shapely for spatial analysis (used for Component 6 as well)

**Key Statistics**:
- Commute Time: Average 27.1 minutes across all counties
- Housing Pre-1960: Average 28.5% of housing stock
- Relative Weekly Wage: Average 1.0 (ratio to state), range 0.4 to 1.8
- Healthcare Employment: 771 counties with healthcare establishments
- National Parks:
  - 33 parks across 10 states
  - 146 counties with parks (18.2% of 802 counties)
  - 255 park-county assignments using boundary-based approach (8x increase vs point-based)
  - Top parks by coverage: Captain John Smith Chesapeake Trail (90 counties), Blue Ridge Parkway (30 counties)
  - Boundary-based spatial intersection assigns parks to ALL counties they touch
  - Previous point-based approach only assigned to 27 counties; boundary approach identifies 146 counties

**Remaining Measures**:
- 7.4: Crime Rate (FBI Crime Data Explorer)
- 7.5: Air Quality Index (EPA)
- 7.6: Recreational Amenities (CBP + GNIS)

See **API_MAPPING.md** for complete details on each measure.

## Updates Log (continued)

**2025-11-17**: Component 6 Partial Implementation
- Implemented measures 6.4 (Weekly Wage Rate) and 6.5 (Top Marginal Income Tax Rate)
- Created `collect_component6.py` script
- Collected 802 counties for weekly wage data (BLS QCEW 2022)
- Collected 10 states for income tax rates (Tax Foundation 2024)
- Total: 812 records across 2 measures
- Component 6 is 33% complete (2 of 6 measures)
- Remaining measures require different collection methods (FCC, NCES, IRS, manual GIS)

**2025-11-17**: Component 6 Measure 6.6 Implementation
- Added measure 6.6 (Qualified Opportunity Zones) using HUD ArcGIS REST API
- Created new `scripts/api_clients/hud_client.py` following project API client pattern
- Successfully collected all 8,765 OZ tracts nationwide via API pagination
- Filtered to 1,709 OZ tracts across our 10 states
- Aggregated to county-level: 580 counties with OZs (average 2.95 tracts per county)
- Key findings:
  - Pennsylvania has the most OZ tracts (300), followed by Georgia (260)
  - 580 of 802 counties (72%) have at least one Opportunity Zone
  - Range: 1 to 82 OZ tracts per county
- Updated `collect_component6.py` to use HUD API client
- Refactored to follow separation of concerns (API logic in client, collection logic in script)
- Total Component 6: 1,392 records across 3 measures
- Component 6 is now 50% complete (3 of 6 measures)

**2025-11-17**: Component 6 Measure 6.3 Implementation
- Added measure 6.3 (Count of 4-Year Colleges) using Urban Institute Education Data Portal API
- Created new `scripts/api_clients/urban_institute_client.py` following project API client pattern
- Successfully collected 902 4-year degree-granting colleges across 10 states
- Aggregated to county-level: 345 counties with colleges (average 2.61 colleges per county)
- Key findings:
  - Pennsylvania has the most colleges (222), followed by North Carolina (139) and Georgia (112)
  - 345 of 802 counties (43%) have at least one 4-year degree-granting college
  - Range: 1 to 23 colleges per county
- API implementation notes:
  - Urban Institute provides clean API access to IPEDS institutional characteristics
  - Combining all filters causes 503 errors; workaround uses fips + inst_level then local filtering
  - State-by-state queries ensure reliable data collection
  - Pagination support handles large result sets
- Updated `collect_component6.py` to include measure 6.3
- Total Component 6: 1,737 records across 4 measures
- **Component 6 is now 67% complete (4 of 6 measures)**

**2025-11-17**: Component 6 Measure 6.2 Implementation (Final Update)
- Added measure 6.2 (Interstate Highway Presence) using USGS National Map Transportation API + Census TIGER
- Created new `scripts/api_clients/usgs_client.py` following project API client pattern
- Successfully downloaded all 194,210 interstate highway segments nationwide from USGS API
- Downloaded Census TIGER 2024 county boundaries for spatial analysis
- Performed spatial intersection to identify counties with interstate highways
- Installed geopandas and shapely libraries for geospatial analysis
- Key findings:
  - 391 of 802 counties (48.8%) have interstate highways
  - Spatial analysis completed successfully across all 10 states
  - Runtime: ~10-15 minutes for full download and spatial processing
- API implementation notes:
  - USGS provides comprehensive transportation data via ArcGIS REST API
  - Downloaded in batches of 2,000 segments with progress tracking
  - Cached highway and boundary data as pickled GeoDataFrames for faster subsequent runs
  - Spatial intersection performed using geopandas geometric operations
- Updated `collect_component6.py` to include all 5 measures (6.2-6.6)
- Total Component 6: 2,539 records across 5 measures
- **Component 6 is now 83% complete (5 of 6 measures)**
- Only measure 6.1 (Broadband Internet Access) remains for Component 6

**2025-11-17**: Component 3 Script Consolidation
- Integrated life expectancy collection (Measure 3.3) directly into `collect_component3.py`
- Removed separate `collect_life_expectancy.py` script (redundant after integration)
- Component 3 now collects all 5 measures in a single script run:
  - 3.1: Proprietor Income (BEA)
  - 3.2: Income Stability (BEA, 15 years)
  - 3.3: Life Expectancy (Zenodo download, integrated)
  - 3.4: Poverty Rate (Census ACS)
  - 3.5: DIR Income Share (BEA)
- Benefits of integration:
  - Simplified workflow - one script collects everything
  - Consistent error handling and logging across all measures
  - Single summary file includes all 5 measures
  - Eliminated need for separate script execution
- Testing confirmed all 5 measures collect successfully in 2-3 minutes
- Total records: 3,936 across all 5 measures