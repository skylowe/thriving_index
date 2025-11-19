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

### Regional Definitions
**Status**: Virginia regions defined; comparison state regions pending

#### Virginia Regions (GO Virginia)
Virginia uses **GO Virginia regions** - 9 economic development regions established for regional economic planning:

| Region ID | Region Name | Counties | Cities | Total Localities | Rural/Metro |
|-----------|-------------|----------|--------|------------------|-------------|
| 1 | Southwest Virginia | 13 | 3 | 16 | Rural |
| 2 | Central/Western Virginia | 13 | 5 | 18 | Rural |
| 3 | Southside Virginia | 13 | 2 | 15 | Rural |
| 4 | Greater Richmond | 12 | 5 | 17 | Metro |
| 5 | Hampton Roads | 6 | 10 | 16 | Metro |
| 6 | Mary Ball Washington Regional Council | 14 | 1 | 15 | Rural |
| 7 | Northern Virginia | 4 | 5 | 9 | Metro |
| 8 | Shenandoah Valley | 10 | 6 | 16 | Rural |
| 9 | Central Virginia | 10 | 1 | 11 | Rural |

**Coverage**: All 133 Virginia localities (95 counties + 38 independent cities)

**Rural Focus**: 6 of 9 regions classified as rural (excluding Northern Virginia, Hampton Roads, Greater Richmond)

**Data Files**:
- `data/regions/virginia_go_regions.csv` - County/city to region mapping
- `scripts/regions.py` - VirginiaRegions class for working with regional data

#### Comparison State Regions (Pending)
For the 9 comparison states (PA, MD, DE, WV, KY, TN, NC, SC, GA), the plan is to use **USDA Economic Development Administration (EDA) regions**:
- Pre-defined, stable boundaries used for economic development planning
- Same framework used by Nebraska Thriving Index for peer region selection
- Facilitates direct comparison with existing research

**Implementation approach**: Contact USDA EDA or state economic development offices for region definitions and shapefiles.

## Current Project Status

**See PROJECT_PLAN.md for detailed progress tracking and component status.**

**Quick Summary**:
- **Progress**: ✅ **47 of 47 measures collected (100% COMPLETE!)**
- **Completed**: All 8 Components (100% complete)
- **Total Records**: ~38,500+ data points across all measures
- **Data Confidence**: 95.7% HIGH confidence (45 of 47 measures)

**Component Status** (see PROJECT_PLAN.md for details):
- ✅ Component 1: Growth Index (5/5 measures)
- ✅ Component 2: Economic Opportunity & Diversity (7/7 measures)
- ✅ Component 3: Other Prosperity Index (5/5 measures)
- ✅ Component 4: Demographic Growth & Renewal (6/6 measures)
- ✅ Component 5: Education & Skill (5/5 measures)
- ✅ Component 6: Infrastructure & Cost of Doing Business (6/6 measures)
- ✅ Component 7: Quality of Life (8/8 measures)
- ✅ Component 8: Social Capital (5/5 measures) - ALL measures complete!

**Next Steps**:
- Data validation and quality checks
- ✅ Regional definitions for Virginia (GO Virginia regions - COMPLETE)
- Define comparison regions for other 9 states (PA, MD, DE, WV, KY, TN, NC, SC, GA)
- Regional data aggregation (county-level to region-level)
- Peer region matching using Mahalanobis distance
- Index calculation and scoring

**For measure-specific details**, see **API_MAPPING.md**.

## Data Sources Overview

**See API_MAPPING.md for complete data source details for all 47 measures.**

### Key Data Sources
- **BEA Regional API**: Employment, wages, income data (774 counties - VA independent cities aggregated)
- **BLS QCEW**: Employment and wage data (downloadable files, ~500MB)
- **Census APIs**: ACS (demographics), BDS (business dynamics), CBP (establishments), Nonemployer Stats
- **County Health Rankings**: Life expectancy, voter turnout, social associations (via Zenodo)
- **Social Capital Atlas**: Volunteering rates, civic organizations density (Meta/Facebook research)
- **FBI Crime Data Explorer**: Violent and property crime (5,749 agencies)
- **IRS Exempt Organizations**: 501(c)(3) nonprofits (bulk download)
- **FCC Broadband Data**: Internet access (BDC Public Data API)
- **National Park Service**: Park boundaries (spatial intersection)
- **USDA ERS**: Natural amenities scale (climate data)
- **HUD**: Opportunity Zones (ArcGIS REST API)
- **Urban Institute**: IPEDS college directory
- **USGS**: Interstate highway data

### Geographic Scope
**Current Focus**: County-level data collection

- Collect data for **ALL counties** in 10 states: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
- Total: 802 counties (some datasets include 807 due to VA independent cities)
- Regional aggregation will occur in a later phase after county data is collected
- Final analysis will compare multi-county rural regions in Virginia to peer regions in the other 9 states

### Time Periods
- Most measures use 5-year growth rates or changes
- Some measures are point-in-time (current year)
- Primary data years: 2017-2022 (varies by measure)
- Historical data collected for stability measures (e.g., 15 years for income stability)

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
- Cache API responses to minimize redundant calls (especially large files like QCEW, CHR)

### Data Storage
- Use consistent file naming conventions
- Store raw API responses in `data/raw/` by source
- Store processed/cleaned data in `data/processed/`
- Use CSV for processed data, JSON for raw API responses
- Document data file structures in collection summary JSON files

### Code Organization
```
scripts/
├── config.py              # Configuration and API key management
├── api_clients/           # API wrapper classes (one per data source)
│   ├── bea_client.py
│   ├── qcew_client.py
│   ├── census_client.py
│   ├── fbi_cde_client.py
│   ├── irs_client.py
│   ├── fcc_client.py
│   ├── social_capital_client.py  # NEW - Social Capital Atlas
│   └── ... (16 clients total)
├── data_collection/       # Data collection scripts (one per component)
│   ├── collect_component1.py
│   ├── collect_component2.py
│   └── ... (8 component scripts - all complete)
└── processing/            # Data processing and cleaning (future)

data/
├── raw/                   # Raw API responses (by source)
│   ├── bea/
│   ├── qcew/
│   ├── census/
│   ├── chr/               # County Health Rankings
│   ├── fbi/
│   ├── social_capital/    # Social Capital Atlas (NEW)
│   └── ...
├── processed/             # Cleaned and processed data (CSV files)
└── results/               # Calculated indexes and scores (future)
```

## Important Formulas and Calculations

### Index Scoring Formula
```
score = 100 + ((value - peer_mean) / peer_std_dev) * 100
```
Where:
- value = region's value for the measure
- peer_mean = average value across peer regions
- peer_std_dev = standard deviation across peer regions

### Mahalanobis Distance (Peer Matching)
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
- **HIGH (37 measures)**: Well-documented APIs with reliable county-level data
- **MEDIUM (7 measures)**: APIs available but may have coverage or timeliness issues
- **LOW (3 measures)**: Requires manual data collection or state-specific sources

See **API_MAPPING.md** for confidence level of each measure.

### Known Challenges and Solutions
1. **BEA County Coverage**: Returns 774 counties (not 802) due to Virginia independent cities being aggregated
2. **QCEW Data Size**: Large files (~500MB) require caching to avoid redundant downloads
3. **FBI Crime API**: No batch endpoints; requires 1 call per agency per offense type (solved with comprehensive caching)
4. **API Parameter Discovery**: Census APIs not always well-documented (e.g., BDS uses YEAR not time)
5. **Variable Name Changes**: Census variable names changed between API versions (e.g., Nonemployer 2021+)
6. **Spatial Analysis**: Interstate highways and national parks require GeoDataFrame spatial intersection
7. **ZIP-to-FIPS Mapping**: 13.1% of IRS organizations unmapped due to outdated ZIP codes or PO boxes

### Data Validation Strategies
- Cross-check totals against published reports
- Verify geographic codes match expected counties (802 or 774 for BEA)
- Check for outliers and anomalies
- Ensure time period alignment across sources
- Document any data gaps or substitutions in collection summary files

## Design Decisions and Rationale

### Why County-Level Data Collection First?
1. Reduces complexity by focusing on 5-8 measures at a time (component-by-component)
2. Provides maximum flexibility for later defining regions
3. Avoids having to re-collect data if region definitions change
4. Allows validation of data quality at granular level
5. Better alignment with iterative development

### Why Python?
1. Excellent API libraries (requests, pandas, geopandas)
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

### Why Component-by-Component Approach?
1. Complete Component 1 (all 5 measures, all counties, all states) before moving to Component 2
2. Validates methodology and data pipeline early
3. Easier debugging and quality control
4. Provides working subset for testing regional aggregation
5. Reduces cognitive load - focus on 5-8 measures at a time

### Why API Keys in .Renviron or Environment Variables?
- API keys stored in .Renviron file in project root (preferred)
- Python `config.py` falls back to environment variables if .Renviron unavailable
- Implemented via `get_api_key()` helper function
- Keeps sensitive keys out of version control
- Provides flexibility across different deployment environments

## Lessons Learned from Implementation

### API Discovery and Documentation
- **BDS API**: Uses `YEAR` parameter instead of `time` (not well documented)
- **BEA Tables**: CAEMP25 doesn't exist despite being referenced in Nebraska methodology; used CAINC4 Line 72 as proxy
- **Census Variables**: Nonemployer API variable names changed in 2021+ without clear documentation (NESTAB not NONEMP, NRCPTOT not RCPTOT)
- **QCEW Access**: Time Series API doesn't support county-level data - must use downloadable files
- **FBI Crime API**: No batch endpoints available; must call each agency individually
- **County Health Rankings**: Contains many useful measures beyond life expectancy (discovered voter turnout in v177_rawvalue column)
- **Social Capital Atlas**: Excellent county-level replacement for state-level AmeriCorps data; Humanitarian Data Exchange provides direct CSV download; no API key required

### Data Availability Insights
- **BEA**: Consistently returns 774 counties (Virginia independent cities aggregated) - expected behavior
- **Industry Diversity**: Not all industries exist in all counties (346-801 records per sector is normal)
- **County Suppression**: Minimal for most measures (802 counties usually available)
- **Spatial Data**: Boundary-based approach yields much better coverage than point-based (e.g., 146 counties with national parks vs 27 with point-based)
- **FIPS Code Standardization**: Many processed data files needed FIPS codes added post-collection; future collections should include FIPS from the start

### Technical Approaches That Worked
- **Environment Variable Fallback**: Provides flexibility across environments
- **Caching Large Downloads**: Saves significant time during development (QCEW files, CHR data, FBI crime, Social Capital Atlas)
- **State-by-State API Calls**: Better error handling for Census data
- **Storing Raw + Processed**: Enables reproducibility and debugging
- **Spatial Libraries**: Geopandas essential for interstate highways, national parks analysis
- **Integrated Collection Scripts**: Collecting multiple related measures in single script (Component 8 collects all 5 measures)
- **Data Source Replacement**: When better county-level data available, replace state-level or binary measures (Social Capital Atlas for measures 8.2 & 8.5)
- **Multi-State Regional Data Manager**: Single class handles all 10 states with consistent county↔region lookups
- **Configuration-Driven Aggregation**: Separate config file defines aggregation methods for all measures, making changes easy
- **Measure-Specific Aggregation Methods**: Different measures require different approaches (sum, weighted_mean, recalculate from components)

### Code Quality Practices
- **Separate API Clients**: One client per data source improves maintainability
- **Consistent File Naming**: `{source}_{measure}_{STATE}_{year}.json` helps organization
- **Summary JSON Files**: Document collection completeness and aid validation
- **Progress Tracking**: Collection summary files track records, coverage, statistics

## Documentation Update Policy

**IMPORTANT**: After every significant commit (new measures, components, or major changes), the following documentation files MUST be updated:
1. **PROJECT_PLAN.md** - Update component status, progress percentages, completion checkboxes
2. **API_MAPPING.md** - Add collection status, data file locations, and statistics for completed measures
3. **CLAUDE.md** - Add major milestone entry to Updates Log if significant (new component complete, major discovery, etc.)

This ensures documentation stays synchronized with code changes and provides accurate project status at all times.

## Key Project Milestones (Updates Log)

For detailed updates, see PROJECT_PLAN.md. Major milestones listed below:

**2025-11-15**: Initial project setup
- Created PROJECT_PLAN.md, API_MAPPING.md, and CLAUDE.md
- Established county-level data collection strategy (all 10 states)
- Documented API key management (.Renviron and environment variables)

**2025-11-15**: Component 1 Complete (Growth Index)
- 5 measures, 8,654 records across 802 counties
- Created BEA, QCEW, and Census API clients
- Key discovery: QCEW requires downloadable files, not Time Series API

**2025-11-16**: Component 2 Complete (Economic Opportunity & Diversity)
- 7 measures collected
- Created BDS, CBP, Nonemployer API clients
- Key discoveries: BDS uses YEAR parameter; BEA CAEMP25 doesn't exist; Nonemployer variable names changed in 2021+

**2025-11-16**: Component 3 Complete (Other Prosperity Index)
- 5 measures including life expectancy from County Health Rankings (Zenodo)
- Extended BEA client for CAINC1 (15-year income stability analysis)
- Integrated CHR download directly into component script

**2025-11-16**: Component 4 Complete (Demographic Growth & Renewal)
- 6 measures, 5,616 records
- Extended Census client for 2000 Decennial Census + detailed age distribution

**2025-11-16**: Component 5 Complete (Education & Skill)
- 5 measures, 2,406 records
- Used occupation-based proxy for knowledge workers (S2401) instead of industry-based (C24030)

**2025-11-17**: Component 6 Complete (Infrastructure & Cost of Doing Business)
- 6 measures, 3,341 records
- Created 5 new API clients: FCC (broadband), USGS (highways), Urban Institute (colleges), HUD (opportunity zones)
- Implemented spatial analysis for interstate highways using USGS + Census TIGER

**2025-11-17**: Component 7 Complete (Quality of Life)
- 8 measures, ~6,400 records
- Created NPS API client with boundary-based spatial intersection (146 counties vs 27 with point-based)
- Created FBI Crime client with comprehensive caching (89 MB cache, 5,749 agencies)
- Integrated crime data collection with optional `--crime` flag

**2025-11-18**: ✅ **Component 8 Complete - ALL DATA COLLECTION FINISHED!** (Social Capital - 100% complete)
- Measure 8.1: Created IRS Exempt Organizations client, ZIP-to-FIPS crosswalk (343,917 orgs, 86.9% mapping success)
- Measure 8.2: **Implemented Volunteer Rate from Social Capital Atlas** (782 counties, mean: 6.36% participation) ✅ NEW
  - **REPLACEMENT**: County-level Facebook data instead of state-level AmeriCorps
  - Upgraded from MEDIUM to HIGH confidence
  - Source: Meta/Facebook Social Capital Atlas research (Harvard/NYU/Stanford collaboration)
  - Measures participation in volunteering/activism groups via Facebook network data
- Measure 8.3: **Replaced "Volunteer Hours" with "Social Associations"** from CHR dataset (804 counties, mean: 10.63 per 10k pop)
  - Changed from state-level AmeriCorps data to county-level CBP data (NAICS 813)
  - Upgraded from MEDIUM to HIGH confidence
  - 100% coverage with no missing data
  - Measures civic infrastructure availability (membership associations) vs volunteer intensity
- Measure 8.4: Discovered voter turnout in CHR dataset - upgraded from MEDIUM to HIGH confidence (804 counties, 2020 Presidential Election)
- Measure 8.5: **Implemented Civic Organizations Density from Social Capital Atlas** (782 counties, mean: 0.0176 per 1k users) ✅ NEW
  - **REPLACEMENT**: Continuous density measure instead of binary Tree City USA designation
  - Upgraded from MEDIUM to HIGH confidence
  - Measures number of civic organizations with Facebook pages per 1,000 Facebook users
  - Source: Same Social Capital Atlas dataset as measure 8.2
- Created new Social Capital Atlas API client (`social_capital_client.py`)
- All Component 8 measures now integrated in single collection script

**Overall Progress**: ✅ **47 of 47 measures collected (100% COMPLETE!)**
**Data Confidence**: 95.7% HIGH confidence (45 of 47 measures)

**2025-11-18**: Virginia Regional Definitions Complete
- Defined Virginia regions using **GO Virginia regions** framework
  - 9 economic development regions covering all 133 Virginia localities (95 counties + 38 independent cities)
  - Pre-defined, stable boundaries designed for regional economic analysis
  - Aligns with Nebraska methodology (USDA EDA regions for comparison states)
- Created regional data infrastructure:
  - `data/regions/virginia_go_regions.csv` - Complete county/city-to-region mapping
  - `scripts/regions.py` - VirginiaRegions class with lookup, validation, and filtering functions
- Identified 6 rural regions (excluding Northern Virginia, Hampton Roads, Greater Richmond):
  - Region 1: Southwest Virginia (13 counties, 3 cities)
  - Region 2: Central/Western Virginia (13 counties, 5 cities)
  - Region 3: Southside Virginia (13 counties, 2 cities)
  - Region 6: Mary Ball Washington Regional Council (14 counties, 1 city)
  - Region 8: Shenandoah Valley (10 counties, 6 cities)
  - Region 9: Central Virginia (10 counties, 1 city)

**2025-11-19**: ✅ **Comparison State Regional Definitions Complete - ALL 10 STATES DEFINED!**
- Defined regions for all 9 comparison states using EDA/EDD framework
- **Total Coverage**: 94 regions covering 773 counties across 10 states
- State-by-state breakdown:
  - **Pennsylvania**: 7 EDDs covering 52 of 67 counties (15 metro counties not in EDDs)
  - **Maryland**: 5 regional councils covering 15 of 24 counties (9 Baltimore-Washington metro counties uncovered)
  - **Delaware**: No formal EDDs (3 counties total, will use county-level data only)
  - **West Virginia**: 11 regional planning councils covering all 55 counties (100% coverage)
  - **Kentucky**: 15 ADDs covering 119 of 120 counties (99% coverage)
  - **Tennessee**: 9 development districts covering 94 of 95 counties (99% coverage)
  - **North Carolina**: 16 COGs covering all 100 counties (100% coverage)
  - **South Carolina**: 10 COGs covering all 46 counties (100% coverage)
  - **Georgia**: 12 regional commissions covering all 159 counties (100% coverage)
- Created regional data files for each state (9 CSV files in `data/regions/`)
- **Next steps**: Regional data aggregation (county-level to region-level for all measures)

**2025-11-18**: ⚙️ **Regional Data Aggregation Infrastructure Complete**
- Built complete system for aggregating county-level data to regional level (94 regions)
- **Infrastructure created**:
  - `scripts/add_fips_to_regions.py` - Added county FIPS codes to all 9 regional CSV files (773 counties, 100% success)
  - `scripts/regional_data_manager.py` - Multi-state RegionalDataManager class with county↔region lookups and aggregation functions
  - `scripts/aggregation_config.py` - Defined aggregation methods for all 47 measures (24 recalculate, 16 weighted_mean, 4 sum, 3 other)
  - `scripts/aggregate_to_regional.py` - Main aggregation script with component-by-component processing
- **Aggregation testing**:
  - Component 2: Economic Opportunity & Diversity - 4 of 7 measures aggregated successfully
    - 2.1: Entrepreneurial Activity (per capita) ✓
    - 2.2: Proprietors per 1,000 ✓
    - 2.3: Establishments per 1,000 ✓
    - 2.7: Telecommuter Share ✓
    - Remaining 3 measures require special calculations (Herfindahl indexes, nonemployer share)
  - Component 8: Social Capital - All 5 measures aggregated successfully ✓
    - 8.1: Nonprofits per 1,000 ✓
    - 8.2: Volunteer Rate ✓
    - 8.3: Social Associations per 10k ✓
    - 8.4: Voter Turnout ✓
    - 8.5: Civic Organizations Density ✓
- **Regional output files created**:
  - `data/regional/component2_economic_opportunity_regional.csv` (94 regions)
  - `data/regional/component8_social_capital_regional.csv` (94 regions)
- **Progress**: 9 of 47 measures aggregated (19% complete)
- **Data quality issue identified**:
  - Component 1, Measure 1.4: Wrong Census variable used (S1101_C01_002E = average household size)
  - Should be S1101_C01_010E (households with one or more people under 18 years)
  - Requires re-collection
- **Next steps**:
  - Add aggregation functions for Components 3-7 (straightforward)
  - Implement special case calculations (industry/occupation diversity Herfindahl indexes, income stability CV)
  - Re-collect Component 1.4 with correct variable
  - Complete aggregation for all 47 measures

## Resources and References

- Nebraska Thriving Index Report (Thriving_Index.pdf)
- Comparison Regions Methodology (Comparison_Regions.pdf)
- **API Mapping Documentation**: API_MAPPING.md (all 47 measures with data sources and confidence levels)
- **Project Progress Tracking**: PROJECT_PLAN.md (detailed component status and file lists)
- BEA Regional API: https://apps.bea.gov/api/
- BLS API: https://www.bls.gov/developers/
- Census API: https://www.census.gov/data/developers.html
- County Health Rankings: https://zenodo.org/records/17584421
- Social Capital Atlas: https://socialcapital.org / https://data.humdata.org/dataset/social-capital-atlas
- FBI Crime Data Explorer: https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi
