# Virginia Thriving Index - Project Plan

## Project Overview

The Virginia Thriving Index is an adaptation of the Nebraska Thriving Index methodology, designed to measure and compare economic prosperity and conditions across Virginia localities and similar regions in surrounding states (Maryland, West Virginia, North Carolina, Tennessee, Kentucky, and Washington DC).

## Objectives

1. **Replicate Nebraska Methodology**: Apply the same 8 component indexes and 47 individual measures used in the Nebraska Thriving Index
2. **Regional Comparison**: Compare Virginia locality regions with peer regions in surrounding states
3. **Peer Region Matching**: Use Mahalanobis distance matching to identify statistically similar regions
4. **API-First Approach**: Utilize only metrics accessible via APIs (no placeholders in production)
5. **Interactive Visualization**: Create a web-based dashboard with maps and interactive charts
6. **Data Efficiency**: Minimize API calls while respecting rate limits

## Methodology Framework

### 8 Component Indexes

#### Economic Prosperity Indexes (3)
1. **Growth Index**
2. **Economic Opportunity & Diversity Index**
3. **Other Economic Prosperity Index**

#### Economic Conditions Indexes (5)
4. **Demographic Growth & Renewal Index**
5. **Education & Skill Index**
6. **Infrastructure & Cost of Doing Business Index**
7. **Quality of Life Index**
8. **Social Capital Index**

### 47 Individual Measures (from Nebraska Study)

#### Growth Index Measures
1. Population growth rate (5-year)
2. Employment growth rate (5-year)
3. Wages and salaries growth rate (5-year)
4. Proprietors income growth rate (5-year)
5. Per capita personal income growth rate (5-year)
6. Retail sales growth rate (5-year)

#### Economic Opportunity & Diversity Index Measures
7. Per capita personal income (level)
8. Median household income
9. Poverty rate (inverse)
10. Labor force participation rate
11. Unemployment rate (inverse)
12. Share of workforce in high-wage industries
13. Economic diversity (Hachman index)

#### Other Economic Prosperity Index Measures
14. Per capita retail sales
15. Per capita bank deposits
16. New business formations per capita
17. Business survival rate

#### Demographic Growth & Renewal Index Measures
18. Natural increase rate (births minus deaths)
19. Net migration rate
20. Percent of population age 25-54
21. Median age (inverse for younger population)

#### Education & Skill Index Measures
22. High school graduation rate
23. Percent of adults with some college
24. Percent of adults with bachelor's degree or higher
25. Student-teacher ratio (inverse)
26. School district spending per pupil

#### Infrastructure & Cost of Doing Business Index Measures
27. Broadband access (percent with access)
28. Housing affordability index
29. Percent of housing units built in last 10 years
30. Property crime rate (inverse)
31. Violent crime rate (inverse)
32. Highway accessibility index

#### Quality of Life Index Measures
33. Life expectancy at birth
34. Infant mortality rate (inverse)
35. Percent uninsured (inverse)
36. Primary care physicians per capita
37. Mental health providers per capita
38. Recreation establishments per capita
39. Restaurants per capita
40. Arts and entertainment establishments per capita

#### Social Capital Index Measures
41. Voter participation rate
42. Nonprofit organizations per capita
43. Religious congregations per capita
44. Social associations per capita
45. Percent of children in single-parent households (inverse)
46. Income inequality (Gini coefficient, inverse)
47. Social capital index (composite measure)

## Data Requirements & API Availability

### Phase 1: API Source Identification (PENDING)

For each of the 47 measures, identify:
- Primary data source
- API availability
- API endpoint and authentication requirements
- Update frequency
- Geographic granularity available

### Prioritized API Sources

#### Federal APIs (Likely Available)
- **Census Bureau API**: Demographics, income, poverty, education
  - American Community Survey (ACS)
  - County Business Patterns (CBP)
  - Population Estimates Program
- **Bureau of Economic Analysis (BEA) API**: Income, employment, GDP
- **Bureau of Labor Statistics (BLS) API**: Employment, unemployment, wages
- **USDA NASS API**: Farm income data
- **FCC Broadband API**: Internet access data

#### Additional API Sources to Investigate
- **FBI Crime Data API**: Uniform Crime Reporting (UCR) data
- **CMS Data API**: Healthcare providers
- **IRS Statistics of Income**: Tax-related economic data
- **Federal Reserve Economic Data (FRED) API**: Various economic indicators
- **OpenStreetMap/Google Maps API**: Distance calculations to MSAs
- **State-specific APIs**: Virginia, Maryland, West Virginia, North Carolina, Tennessee, Kentucky, DC

### Metrics Excluded from Current Analysis

Any measures that cannot be accessed via API will be excluded from the initial implementation. These will be documented but not calculated until API access is established.

## Virginia Region Definitions

### Approach Options

**Option 1: County-Level Analysis**
- Treat each Virginia county and independent city as a separate region
- Pro: Maximum granularity, data availability
- Con: Large number of regions (95 counties + 38 cities = 133 regions)

**Option 2: Multi-County Regional Groupings**
- Group Virginia localities into 8-12 larger regions based on:
  - Economic characteristics
  - Urban/rural classification
  - Geographic proximity
  - Existing planning district commissions
- Pro: More comparable to Nebraska's 8-region approach
- Con: Requires aggregation methodology

**Option 3: MSA/Micropolitan Statistical Areas**
- Use existing Census-defined statistical areas
- Pro: Standardized definitions, comparable across states
- Con: Not all counties included in statistical areas

**Decision**: To be finalized in CLAUDE.md after data exploration

## Peer Region Selection: Mahalanobis Distance Matching

### Matching Variables (from Nebraska Study)
1. Total population
2. Percent of population in micropolitan statistical area
3. Percent farm and ranch income of total personal income
4. Percent manufacturing employment
5. Distance to small MSA (population < 250,000)
6. Distance to large MSA (population > 250,000)

### Process
1. Calculate matching variables for all Virginia regions
2. Calculate matching variables for all regions in surrounding states
3. Compute Mahalanobis distance between each Virginia region and all potential peer regions
4. Select top 5-10 closest peer regions for each Virginia region
5. Use peer regions for comparative ranking in index calculations

## Scoring Methodology

### Standardization Approach
- Index value of 100 = average across all regions (Virginia + peers)
- Index value of 0 = one standard deviation below average
- Index value of 200 = one standard deviation above average
- Formula: `Index = 100 + 100 * (value - mean) / std_dev`

### Component Index Calculation
- Each component index is the average of its constituent measures
- All measures standardized before averaging
- Measures with inverse relationship (e.g., poverty rate, unemployment) are inverted during standardization

### Overall Thriving Index
- Weighted or unweighted average of all 8 component indexes
- Decision on weighting to be documented in CLAUDE.md

## Technical Architecture

### Technology Stack
- **Language**: Python 3.9+
- **Data Collection**:
  - `requests` for API calls
  - Custom API wrapper functions
  - Rate limiting and retry logic
- **Data Processing**:
  - `pandas` for data manipulation
  - `numpy` for calculations
  - `scipy` for Mahalanobis distance
- **Visualization**:
  - `plotly` or `dash` for interactive dashboard
  - `folium` or `plotly` for maps
  - Web framework: Flask or Dash
- **Data Storage**:
  - SQLite or PostgreSQL for processed data
  - CSV/JSON for intermediate results
  - Caching layer for API responses

### Project Structure
```
thriving_index/
├── data/
│   ├── raw/                 # Raw API responses
│   ├── processed/           # Cleaned and processed data
│   └── cache/              # API response cache
├── src/
│   ├── api_clients/        # API wrapper functions
│   ├── data_collection/    # Data fetching scripts
│   ├── processing/         # Data cleaning and calculation
│   ├── matching/           # Peer region matching
│   ├── scoring/            # Index calculation
│   └── visualization/      # Dashboard and charts
├── dashboard/              # Web dashboard application
├── notebooks/              # Jupyter notebooks for exploration
├── tests/                  # Unit and integration tests
├── config/                 # Configuration files
├── docs/                   # Documentation
├── PROJECT_PLAN.md         # This file
├── CLAUDE.md              # Development notes
└── requirements.txt       # Python dependencies
```

## Implementation Phases

### Phase 1: Planning & Data Source Identification ⏳ IN PROGRESS
- [x] Create PROJECT_PLAN.md
- [ ] Create CLAUDE.md
- [ ] Map all 47 measures to potential API sources
- [ ] Identify available API keys in environment
- [ ] Document API requirements and access methods
- [ ] Determine which measures can be included in initial analysis
- [ ] Finalize Virginia region definition approach
- [ ] Define regions in surrounding states

**Estimated Duration**: 2-3 days

### Phase 2: Data Collection Infrastructure 📋 PENDING
- [ ] Set up project structure
- [ ] Create API client modules for each data source
- [ ] Implement rate limiting and caching
- [ ] Build data validation functions
- [ ] Create error handling and retry logic
- [ ] Test API connections with sample requests
- [ ] Document API usage patterns

**Estimated Duration**: 3-4 days

### Phase 3: Region Definition & Geographic Data 📋 PENDING
- [ ] Define Virginia regions (counties or groupings)
- [ ] Define regions in surrounding states
- [ ] Collect geographic boundary data
- [ ] Calculate distances to MSAs
- [ ] Build region metadata database
- [ ] Create region lookup functions

**Estimated Duration**: 2 days

### Phase 4: Peer Region Matching 📋 PENDING
- [ ] Collect matching variables for all regions
- [ ] Implement Mahalanobis distance calculation
- [ ] Generate peer region assignments
- [ ] Validate peer region selections
- [ ] Document peer region rationale
- [ ] Create peer region visualization

**Estimated Duration**: 2-3 days

### Phase 5: Data Collection & Processing 📋 PENDING
- [ ] Fetch all available data via APIs
- [ ] Clean and standardize data
- [ ] Handle missing values
- [ ] Calculate derived measures
- [ ] Validate data quality
- [ ] Store processed data
- [ ] Document data collection issues

**Estimated Duration**: 5-7 days

### Phase 6: Index Calculation 📋 PENDING
- [ ] Implement standardization formulas
- [ ] Calculate all 47 individual measures
- [ ] Calculate 8 component indexes
- [ ] Calculate overall Thriving Index
- [ ] Validate calculations against test cases
- [ ] Generate summary statistics
- [ ] Create ranking tables

**Estimated Duration**: 3-4 days

### Phase 7: Visualization & Dashboard 📋 PENDING
- [ ] Design dashboard layout
- [ ] Create interactive maps
- [ ] Build component index charts
- [ ] Create peer region comparison views
- [ ] Implement filtering and selection
- [ ] Add data export functionality
- [ ] Test dashboard performance
- [ ] Deploy dashboard locally

**Estimated Duration**: 5-7 days

### Phase 8: Testing & Validation 📋 PENDING
- [ ] Validate against Nebraska methodology
- [ ] Test edge cases
- [ ] Verify ranking consistency
- [ ] Review data accuracy
- [ ] Conduct user acceptance testing
- [ ] Document known limitations
- [ ] Create user guide

**Estimated Duration**: 2-3 days

### Phase 9: Documentation & Deployment 📋 PENDING
- [ ] Finalize technical documentation
- [ ] Create user documentation
- [ ] Document deployment procedures
- [ ] Package application
- [ ] Create README with setup instructions
- [ ] Archive source data references
- [ ] Plan for data updates

**Estimated Duration**: 2-3 days

## Success Criteria

1. **Methodology Fidelity**: Accurately replicate Nebraska's approach for Virginia context
2. **Data Completeness**: Include at least 35 of 47 measures (75% coverage)
3. **API-Only Data**: All included measures sourced exclusively from APIs
4. **Peer Region Quality**: Statistically valid peer region matches using Mahalanobis distance
5. **Dashboard Functionality**: Fully interactive web dashboard with maps and charts
6. **Performance**: Dashboard loads within 3 seconds, API calls respect rate limits
7. **Documentation**: Complete documentation allowing replication and updates

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| API access limitations | High | Identify alternatives, prioritize most important measures |
| Rate limiting issues | Medium | Implement caching, batch requests, exponential backoff |
| Data quality problems | High | Robust validation, handle missing values systematically |
| Geographic granularity mismatches | Medium | Document assumptions, provide aggregation methodology |
| Calculation complexity | Medium | Unit tests, validate against Nebraska results where possible |
| Dashboard performance | Low | Optimize queries, implement lazy loading, cache results |

## Open Questions

1. Should Virginia regions be individual counties or multi-county groupings?
2. What weighting (if any) should be applied to the 8 component indexes?
3. How should we handle temporal data - most recent year only or multi-year averages?
4. Should we include independent cities as separate regions or merge with adjacent counties?
5. What is the update frequency for the dashboard - quarterly, annually?

## Timeline

- **Phase 1**: Days 1-3
- **Phase 2**: Days 4-7
- **Phase 3**: Days 8-9
- **Phase 4**: Days 10-12
- **Phase 5**: Days 13-19
- **Phase 6**: Days 20-23
- **Phase 7**: Days 24-30
- **Phase 8**: Days 31-33
- **Phase 9**: Days 34-36

**Total Estimated Duration**: 5-6 weeks

## Progress Tracking

### Current Status: Phase 1 - Planning & Data Source Identification ⏳

**Last Updated**: 2025-11-14

**Completed Tasks**:
- Created PROJECT_PLAN.md

**In Progress**:
- Creating CLAUDE.md
- Mapping measures to API sources

**Next Steps**:
1. Complete CLAUDE.md
2. Analyze all 47 measures for API availability
3. Check environment variables for existing API keys
4. Begin Phase 2 planning

## Notes

- This is a living document that will be updated as the project progresses
- Major decisions and changes should be logged in CLAUDE.md
- Phase completion should be marked with dates and any deviations from plan
