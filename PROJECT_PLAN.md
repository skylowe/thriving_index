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
**Status**: In Progress
- [x] Review Nebraska Thriving Index documentation
- [x] Review comparison regions methodology
- [x] Review API mapping documentation
- [x] Create project structure (scripts/ and data/ folders)
- [x] Create PROJECT_PLAN.md
- [x] Create CLAUDE.md
- [ ] User review and approval to proceed

### Phase 1: Component Index 1 - Growth Index
**Status**: Not Started
**Target**: Collect county-level data for all 10 states

Data collection tasks (5 measures - see API_MAPPING.md for details):
- [ ] Set up API clients (BEA, BLS, Census) with keys from .Renviron
- [ ] Collect Growth in Total Employment (BEA CAINC5)
- [ ] Collect Private Employment (BLS QCEW)
- [ ] Collect Growth in Private Wages Per Job (BLS QCEW)
- [ ] Collect Growth in Households with Children (Census ACS)
- [ ] Collect Growth in Dividends, Interest and Rent Income (BEA CAINC5)
- [ ] Validate and clean all Component 1 data
- [ ] Document any data gaps or issues

### Phase 2: Component Index 2 - Economic Opportunity & Diversity Index
**Status**: Not Started
- [ ] Collect data for 7 measures (BLS QCEW, USDA NASS, BEA, Census ACS)
- [ ] Validate and clean data

### Phase 3: Component Index 3 - Other Prosperity Index
**Status**: Not Started
- [ ] Collect data for 5 measures (BLS QCEW, BEA, Census ACS)
- [ ] Validate and clean data

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
**Phase**: Phase 0 - Project Setup (awaiting user review)

**Next Steps**:
1. User review of PROJECT_PLAN.md and CLAUDE.md
2. Upon approval, begin Phase 1: Component Index 1 data collection
3. Set up API clients reading keys from .Renviron file
4. Collect county-level data for all 5 Growth Index measures across all 10 states

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
