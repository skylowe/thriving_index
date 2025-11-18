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

## Current Project Status

**See PROJECT_PLAN.md for detailed progress tracking and component status.**

**Quick Summary**:
- **Progress**: 45 of 47 measures collected (96% complete)
- **Completed**: Components 1-7 (100% complete)
- **In Progress**: Component 8 - Social Capital (3 of 5 measures complete, 60%)
- **Total Records**: ~34,500+ data points across all measures

**Component Status** (see PROJECT_PLAN.md for details):
- ✅ Component 1: Growth Index (5/5 measures)
- ✅ Component 2: Economic Opportunity & Diversity (7/7 measures)
- ✅ Component 3: Other Prosperity Index (5/5 measures)
- ✅ Component 4: Demographic Growth & Renewal (6/6 measures)
- ✅ Component 5: Education & Skill (5/5 measures)
- ✅ Component 6: Infrastructure & Cost of Doing Business (6/6 measures)
- ✅ Component 7: Quality of Life (8/8 measures)
- 🔄 Component 8: Social Capital (3/5 measures) - measures 8.1, 8.3, and 8.4 complete

**Remaining Work**:
- Component 8: Measures 8.2 (Volunteer Rate - not implementing), 8.5 (Tree City USA)
- Later: Regional aggregation, peer matching, index calculation

**For measure-specific details**, see **API_MAPPING.md**.

## Data Sources Overview

**See API_MAPPING.md for complete data source details for all 47 measures.**

### Key Data Sources
- **BEA Regional API**: Employment, wages, income data (774 counties - VA independent cities aggregated)
- **BLS QCEW**: Employment and wage data (downloadable files, ~500MB)
- **Census APIs**: ACS (demographics), BDS (business dynamics), CBP (establishments), Nonemployer Stats
- **County Health Rankings**: Life expectancy, voter turnout (via Zenodo)
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
│   └── ... (15+ clients total)
├── data_collection/       # Data collection scripts (one per component)
│   ├── collect_component1.py
│   ├── collect_component2.py
│   └── ... (8 component scripts)
└── processing/            # Data processing and cleaning (future)

data/
├── raw/                   # Raw API responses (by source)
│   ├── bea/
│   ├── qcew/
│   ├── census/
│   ├── chr/               # County Health Rankings
│   ├── fbi/
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

### Data Availability Insights
- **BEA**: Consistently returns 774 counties (Virginia independent cities aggregated) - expected behavior
- **Industry Diversity**: Not all industries exist in all counties (346-801 records per sector is normal)
- **County Suppression**: Minimal for most measures (802 counties usually available)
- **Spatial Data**: Boundary-based approach yields much better coverage than point-based (e.g., 146 counties with national parks vs 27 with point-based)

### Technical Approaches That Worked
- **Environment Variable Fallback**: Provides flexibility across environments
- **Caching Large Downloads**: Saves significant time during development (QCEW files, CHR data, FBI crime)
- **State-by-State API Calls**: Better error handling for Census data
- **Storing Raw + Processed**: Enables reproducibility and debugging
- **Spatial Libraries**: Geopandas essential for interstate highways, national parks analysis
- **Integrated Collection Scripts**: Collecting multiple related measures in single script (e.g., Component 8 measures 8.1 and 8.4)

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

**2025-11-18**: Component 8 In Progress (Social Capital - 60% complete)
- Measure 8.1: Created IRS Exempt Organizations client, ZIP-to-FIPS crosswalk (343,917 orgs, 86.9% mapping success)
- Measure 8.3: **Replaced "Volunteer Hours" with "Social Associations"** from CHR dataset (804 counties, mean: 10.63 per 10k pop)
  - Changed from state-level AmeriCorps data to county-level CBP data (NAICS 813)
  - Upgraded from MEDIUM to HIGH confidence
  - 100% coverage with no missing data
  - Measures civic infrastructure availability (membership associations) vs volunteer intensity
- Measure 8.4: Discovered voter turnout in CHR dataset - upgraded from MEDIUM to HIGH confidence (804 counties, 2020 Presidential Election)
- 2 measures remaining: 8.2 (Volunteer Rate - not implementing), 8.5 (Tree City USA)

**Overall Progress**: 45 of 47 measures collected (96% complete)

## Resources and References

- Nebraska Thriving Index Report (Thriving_Index.pdf)
- Comparison Regions Methodology (Comparison_Regions.pdf)
- **API Mapping Documentation**: API_MAPPING.md (all 47 measures with data sources and confidence levels)
- **Project Progress Tracking**: PROJECT_PLAN.md (detailed component status and file lists)
- BEA Regional API: https://apps.bea.gov/api/
- BLS API: https://www.bls.gov/developers/
- Census API: https://www.census.gov/data/developers.html
- County Health Rankings: https://zenodo.org/records/17584421
- FBI Crime Data Explorer: https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi
