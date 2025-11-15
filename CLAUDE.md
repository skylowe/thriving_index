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
  - Uses CAINC5 table for income components
  - Provides county-level economic data
- **BLS QCEW API**: Bureau of Labor Statistics Quarterly Census of Employment and Wages
  - Employment and wage data by industry
  - Used for economic diversity calculations
- **Census ACS API**: American Community Survey
  - Demographic and household data
  - Education, poverty, housing data
- **Census Population Estimates**: Annual county population data
- **Census County Business Patterns**: Business establishment data

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

## Component Index 1: Growth Index (First Implementation Target)

Component Index 1 contains 5 measures, all with HIGH confidence levels and well-documented APIs:
- BEA CAINC5 (employment and investment income)
- BLS QCEW (private employment and wages)
- Census ACS (households with children)

See **API_MAPPING.md** for complete details on each measure, including specific line codes, table references, and calculation formulas.

## Python Implementation Requirements

### Cross-Platform Compatibility
- Must run on both Linux and Windows
- Use pathlib for path handling
- Use platform-independent file operations
- Test on both operating systems

### API Integration
- API keys are stored in the .Renviron file in the project root
- Read API keys from .Renviron at runtime using R or Python environment loading
- Implement retry logic for API calls
- Handle rate limiting appropriately
- Cache API responses to minimize redundant calls

### Data Storage
- Use consistent file naming conventions
- Store raw API responses
- Store processed/cleaned data separately
- Use CSV or JSON for data files
- Document data file structures

### Code Organization
```
scripts/
├── api_clients/          # API wrapper classes
│   ├── bea_client.py
│   ├── bls_client.py
│   └── census_client.py
├── data_collection/      # Data collection scripts
│   ├── collect_component1.py
│   └── ...
├── processing/           # Data processing and cleaning
│   └── clean_data.py
└── analysis/            # Index calculation and analysis
    └── calculate_index.py

data/
├── raw/                 # Raw API responses
│   ├── bea/
│   ├── bls/
│   └── census/
├── processed/           # Cleaned and processed data
└── results/            # Calculated indexes and scores
```

## API Documentation References

### BEA Regional API
- Base URL: https://apps.bea.gov/api/data
- Parameters: UserID, method, datasetname, TableName, LineCode, GeoFIPS, Year
- Table: CAINC5 (Personal Income by Major Component)
- Relevant Line Codes:
  - 10: Total employment
  - 31: Dividends, interest, and rent

### BLS QCEW API
- Base URL: https://api.bls.gov/publicAPI/v2/timeseries/data/
- Series ID format: ENUCS + FIPS + industry_code
- Annual averages for employment and wages
- Industry codes for economic diversity calculations

### Census ACS API
- Base URL: https://api.census.gov/data/{year}/acs/acs5
- Subject Tables (S prefix) and Detailed Tables (B prefix)
- 5-year estimates for stability
- Geographic level: county (050)

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

## Next Steps (After User Review)

1. **Set Up API Clients**: Create Python clients for BEA, BLS, Census APIs that read keys from .Renviron
2. **Collect Component 1 Data**: Implement data collection for all 5 Growth Index measures for ALL counties in all 10 states
3. **Validate Component 1 Data**: Process and clean the collected data, document any gaps
4. **Proceed Component by Component**: Move to Component 2-8 only after Component 1 is complete
5. **Regional Aggregation** (Later Phase): After all data is collected, define and aggregate counties into regions
6. **Peer Selection** (Later Phase): Implement Mahalanobis distance matching to identify peer regions

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

### API Keys in .Renviron
- All API keys stored in .Renviron file in project root
- Python scripts will read from this file at runtime
- Keeps sensitive keys out of version control

### Component-by-Component Approach
- Complete Component 1 (all 5 measures, all counties, all states) before moving to Component 2
- Validates methodology and data pipeline early
- Easier debugging and quality control
- Provides working subset for testing regional aggregation

## Updates Log
- 2025-11-15: Initial project setup, documentation review, created PROJECT_PLAN.md and CLAUDE.md
- 2025-11-15: Revised to clarify county-level data collection for all 10 states, .Renviron for API keys, regional aggregation as later phase
