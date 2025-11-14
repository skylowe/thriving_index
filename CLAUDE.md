# Virginia Thriving Index - Development Notes

**Project**: Virginia Thriving Index
**Based on**: Nebraska Thriving Index 2022
**Started**: 2025-11-14
**Branch**: `claude/thriving-index-analysis-01BYbBkdyC1xUoLqqV4x7XCD`

---

## Document Purpose

This file serves as a development journal and decision log for the Virginia Thriving Index project. It documents:
- Technical decisions and their rationale
- Methodology adaptations from Nebraska to Virginia
- API integration details and challenges
- Data quality issues and resolutions
- Code architecture choices
- Implementation progress and blockers

---

## Development Log

### 2025-11-14: Project Initialization

#### Context
Starting a new project to replicate the Nebraska Thriving Index methodology for Virginia and surrounding states. User provided two PDF documents explaining the Nebraska approach and an Excel file with calculations.

#### Initial Requirements Clarification
- **Geographic Scope**: Virginia localities compared to regions in MD, WV, NC, TN, KY, DC
- **Methodology**: 8 component indexes, 47 individual measures, Mahalanobis distance peer matching
- **Data Constraint**: API-accessible data only; no placeholders in production
- **Output**: Interactive web dashboard with maps and charts
- **Technical**: Python-based implementation
- **Efficiency**: Minimize API calls, respect rate limits

#### Documents Created
1. **PROJECT_PLAN.md**: Comprehensive project roadmap with phases, timeline, and success criteria
2. **CLAUDE.md**: This file - development notes and decisions
3. **API_MAPPING.md**: Detailed mapping of all 47 measures to potential API sources
4. **API_KEYS_STATUS.md**: Documentation of available API keys and data source coverage

#### API Analysis Complete

**Status**: ✅ Phase 1 initial analysis complete

**API Source Mapping**:
- Analyzed all 47 measures from Nebraska study
- Categorized by confidence level: HIGH (28), MEDIUM (10), LOW (9)
- 28 measures (59.6%) have HIGH confidence API availability
- 10 measures (21.3%) require further investigation
- 9 measures (19.1%) likely cannot be accessed via API

**API Keys Verified**:
- ✅ `CENSUS_KEY` - Available (Census Bureau ACS, CBP, Population data)
- ✅ `BEA_API_KEY` - Available (Bureau of Economic Analysis income/GDP data)
- ✅ `BLS_API_KEY` - Available (Bureau of Labor Statistics employment/wages)
- ✅ `FRED_API_KEY` - Available (Bonus - Federal Reserve Economic Data)

**Key Finding**: All three essential API keys are available. This enables immediate implementation of 28 high-confidence measures covering all 8 component indexes (though "Other Economic Prosperity" index has limited coverage).

**Next Steps**:
1. Test API connections with sample requests
2. Investigate MEDIUM-confidence measures for potential inclusion
3. Make decision on Component Index 3 (Other Economic Prosperity) which has 0/4 HIGH-confidence measures
4. Begin Phase 2 (Data Collection Infrastructure)

#### Key Observations from Nebraska Study

**Regional Structure**:
- Nebraska divided into 8 regions
- Each region compared to 10 peer regions from surrounding states
- Peer selection based on 6 matching variables (population, urban/rural mix, economic structure, MSA proximity)

**Scoring System**:
- Standardized scoring: mean = 100, std dev = 100
- Higher values = better performance
- Inverse measures (e.g., poverty, crime) flipped so higher is still better
- Component indexes are averages of their constituent measures

**Data Sources** (from Nebraska study):
- Heavily reliant on Census Bureau (ACS 5-year estimates)
- Bureau of Economic Analysis (BEA) for income/employment data
- Bureau of Labor Statistics (BLS) for unemployment
- FBI UCR for crime data
- FCC for broadband access
- Various federal sources for healthcare, business formation, etc.

---

## Technical Decisions

### Decision 1: Region Definition Approach

**Status**: 🤔 PENDING
**Decision Date**: TBD

**Options Considered**:

1. **County-Level Analysis**
   - Each Virginia county and independent city as separate region
   - Pros: Maximum granularity, matches typical Census data geography
   - Cons: 133 regions is unwieldy; some cities/counties very small
   - Virginia has 95 counties + 38 independent cities = 133 localities

2. **Multi-County Regional Groupings**
   - Group localities into 8-12 economic regions
   - Could use Virginia's Planning District Commissions (PDCs) as template
   - Pros: More comparable to Nebraska's 8-region approach
   - Cons: Requires aggregation methodology; some arbitrariness in grouping

3. **MSA/Micropolitan Statistical Areas**
   - Use Census-defined Core-Based Statistical Areas (CBSAs)
   - Pros: Standardized definitions, functional economic areas
   - Cons: Not all counties included; some overlap with adjacent states

**Implications**:
- Affects peer region matching (need similar units across states)
- Impacts data aggregation requirements
- Determines dashboard granularity

**Preliminary Recommendation**: Start with county-level analysis for Virginia, then allow dashboard users to view aggregated regional views. This preserves maximum flexibility.

**Next Steps**:
- Examine data availability at county vs regional level
- Review Virginia Planning District Commission boundaries
- Consult with user on preferred granularity

---

### Decision 2: Handling Independent Cities

**Status**: 🤔 PENDING
**Decision Date**: TBD

**Context**: Virginia has 38 independent cities that are not part of any county. This is unique among US states.

**Options**:
1. Treat each independent city as a separate region
2. Merge cities with adjacent counties for analysis
3. Create city-county combined units where appropriate
4. Analyze cities separately from counties (two different region types)

**Implications**:
- Affects peer region matching (do other states have comparable city structures?)
- Impacts data availability and comparability
- Some cities very small (< 20,000 population) may not have reliable ACS estimates

**Preliminary Recommendation**: TBD after reviewing data availability

---

### Decision 3: Temporal Coverage

**Status**: 🤔 PENDING
**Decision Date**: TBD

**Question**: Should we use most recent year data only, or multi-year averages?

**Considerations**:
- Nebraska study primarily used 5-year ACS estimates (2016-2020)
- Growth measures used 5-year change calculations
- Some sources provide annual data, others multi-year
- COVID-19 pandemic may have introduced unusual volatility in 2020-2021

**Options**:
1. **Most Recent Available**: Use latest data regardless of year
   - Pro: Most current snapshot
   - Con: Different measures from different years; comparability issues

2. **Single Reference Year**: Use 2022 data where available
   - Pro: Temporal consistency
   - Con: Not all measures available for same year

3. **Multi-Year Averages**: Use 5-year ACS estimates and 5-year averages for other measures
   - Pro: Reduces volatility, matches Nebraska approach
   - Con: Less current, may smooth over recent trends

**Preliminary Recommendation**: Use ACS 5-year estimates (most recent: 2018-2022) as baseline, with growth calculations using 5-year changes. Match temporal coverage across measures where possible.

---

### Decision 4: Peer Region Pool Definition

**Status**: 🤔 PENDING
**Decision Date**: TBD

**Question**: How do we define regions in surrounding states for peer matching?

**Considerations**:
- Maryland: 23 counties + 1 independent city (Baltimore)
- West Virginia: 55 counties
- North Carolina: 100 counties
- Tennessee: 95 counties
- Kentucky: 120 counties
- Washington DC: Single entity (special case)
- **Total**: ~500 potential peer regions across 6 states/districts

**Options**:
1. County-level for all states (most consistent with Virginia)
2. MSA/micropolitan areas where defined
3. Mix of approaches based on state structures
4. Limit to border counties only (reduces pool, increases relevance)

**Implications**:
- Larger pool = better chance of finding true peers
- All peer regions need same 6 matching variables
- Data collection scales with number of regions
- API call volume increases with region count

**Preliminary Recommendation**: Use county-level for all states (excluding DC, which is single region). This provides ~500 potential peers for matching while maintaining geographic consistency.

---

### Decision 5: Dashboard Technology Stack

**Status**: 🤔 PENDING
**Decision Date**: TBD

**Options Considered**:

1. **Plotly Dash**
   - Pros: Python-native, excellent charts, good for data apps
   - Cons: Can be slower for large datasets, limited styling flexibility

2. **Streamlit**
   - Pros: Very fast development, simple API, great for prototypes
   - Cons: Limited customization, some performance issues

3. **Flask + Plotly.js**
   - Pros: Maximum flexibility, lightweight, standard web tech
   - Cons: More code needed, template management

4. **Django + Plotly**
   - Pros: Full-featured, good for scaling, admin interface
   - Cons: Overkill for this project, steeper learning curve

**Preliminary Recommendation**: Start with Plotly Dash for rapid development. Can migrate to Flask if customization needs exceed Dash capabilities.

**Map Visualization**: Use Plotly's choropleth maps or Folium for interactive geographic displays.

---

## API Integration Strategy

### API Sources Identified

Based on the 47 measures from Nebraska study, preliminary API source mapping:

#### High Confidence - API Available

**Census Bureau API** (https://api.census.gov/data.html)
- American Community Survey (ACS) 5-year estimates
- Key measures: demographics, income, poverty, education, housing, employment
- API Key: Required (check environment: `CENSUS_API_KEY`)
- Rate Limit: Typically generous for ACS
- Coverage: Virtually all demographic and socioeconomic measures

**Bureau of Economic Analysis (BEA) API** (https://apps.bea.gov/api/)
- Regional Economic Accounts
- Key measures: personal income, wages, proprietors income, GDP
- API Key: Required (check environment: `BEA_API_KEY`)
- Rate Limit: 1000 calls/day (need to confirm)
- Coverage: Income and economic growth measures

**Bureau of Labor Statistics (BLS) API** (https://www.bls.gov/developers/)
- Local Area Unemployment Statistics (LAUS)
- Quarterly Census of Employment and Wages (QCEW)
- Key measures: unemployment rate, employment by industry, wages
- API Key: Required (check environment: `BLS_API_KEY`)
- Rate Limit: 500 queries/day (daily), 25/day (no registration)
- Coverage: Employment and wage measures

**FCC Broadband API** (https://broadbandmap.fcc.gov/)
- Broadband availability data
- Key measure: percent with broadband access
- API Key: May not be required (check)
- Rate Limit: Unknown
- Coverage: Infrastructure measure

#### Medium Confidence - API May Be Available

**FBI Crime Data Explorer API** (https://cde.ucr.cde.fbi.gov/)
- Uniform Crime Reporting (UCR) data
- Key measures: violent crime rate, property crime rate
- API: New Crime Data Explorer API launched 2021
- Status: Need to investigate current API access
- Coverage: Crime measures

**USDA NASS API** (https://quickstats.nass.usda.gov/api)
- Agricultural statistics
- Key measure: farm/ranch income
- API Key: Required (check environment: `USDA_NASS_API_KEY`)
- Rate Limit: Unknown
- Coverage: Agricultural income measures

**CMS Data API** (https://data.cms.gov/)
- Medicare provider data
- Key measures: physicians per capita, healthcare access
- API: Available through data.cms.gov
- Status: Need to verify county-level granularity
- Coverage: Healthcare measures

**IRS Statistics of Income**
- Tax statistics including business formations, income distributions
- Key measures: new business formations, Gini coefficient
- API: Limited or no public API (may need to use bulk downloads)
- Status: LOW CONFIDENCE for API access

#### Low Confidence - May Not Have API

**State Department of Education Data**
- School district spending, student-teacher ratios, graduation rates
- API: Varies by state; may not have public APIs
- Alternative: Bulk downloads from National Center for Education Statistics (NCES)
- Status: Need to investigate NCES API options

**County Health Rankings**
- Life expectancy, infant mortality, health outcomes
- Source: County Health Rankings & Roadmaps program
- API: May not have API; provides bulk downloads
- Status: Need to investigate

**Social Capital Project Data**
- Comprehensive social capital measures
- Source: Research projects and academic institutions
- API: Unlikely
- Status: May need to exclude or find alternatives

### API Call Optimization Strategy

**Principles**:
1. **Cache Everything**: Store all API responses locally with timestamps
2. **Batch Requests**: Where APIs support it, request multiple geographies in single call
3. **Incremental Updates**: Only fetch new data when updating, not full refresh
4. **Parallel Processing**: Use async requests where possible, respecting rate limits
5. **Fallback Sources**: Have alternative data sources identified for critical measures

**Caching Approach**:
```python
# Pseudo-code structure
cache/
  census/
    acs_2022_county_demographics.json
    acs_2022_county_income.json
  bea/
    personal_income_2022.json
  bls/
    unemployment_2022.json
  [metadata with fetch timestamp, expiration]
```

**Rate Limiting Implementation**:
- Use `ratelimit` or `tenacity` library for automatic backoff
- Implement exponential backoff on failures
- Track API usage against known limits
- Log all API calls for monitoring

---

## Methodology Adaptations

### Mahalanobis Distance Matching

**Nebraska Approach**:
- 6 matching variables used to find peer regions
- Variables: total population, % in micropolitan area, % farm income, % manufacturing employment, distance to small MSA, distance to large MSA
- Selects 10 closest peer regions for each target region

**Virginia Adaptation Considerations**:

1. **Population**: Straightforward - use Census population estimates

2. **% in Micropolitan Area**: Need to classify each county/city as metropolitan, micropolitan, or neither based on Census CBSA definitions

3. **% Farm Income**: BEA provides farm proprietors income; calculate as % of total personal income

4. **% Manufacturing Employment**: BLS QCEW or Census CBP provides employment by industry; calculate manufacturing share

5. **Distance to Small MSA**: Need to:
   - Define "small MSA" (population < 250,000)
   - Calculate geographic distances (county centroid to MSA centroid)
   - Use geopy or similar for distance calculations

6. **Distance to Large MSA**: Same as above but for MSA > 250,000

**Implementation Notes**:
- Use `scipy.spatial.distance.mahalanobis` for calculation
- Covariance matrix computed across full region pool (Virginia + surrounding states)
- May need to standardize/normalize variables before distance calculation
- Should validate: Are distance calculations Euclidean or driving distance? (Assume Euclidean)

**Potential Challenges**:
- Independent cities may have unusual characteristics (very urban, small area)
- DC is unique - single city-state entity, very urban, federal employment
- Border regions may have different peer characteristics than interior regions

---

### Scoring and Standardization

**Formula** (from Nebraska):
```
Index_Value = 100 + 100 * (X - μ) / σ

Where:
- X = raw value for region
- μ = mean across all regions (Virginia + peer regions)
- σ = standard deviation across all regions
```

**Inverse Measures**:
For measures where lower is better (poverty, crime, unemployment), apply inversion:
```
Index_Value = 100 + 100 * (μ - X) / σ
```

**Component Index Calculation**:
- Average of all constituent measure indexes within that component
- All measures weighted equally (unless user requests otherwise)

**Overall Thriving Index**:
- Average of all 8 component indexes
- Could implement weighted average if desired

**Implementation Considerations**:
- Need to handle missing values before standardization
- Outliers may skew σ; consider robust alternatives (median, MAD)
- Should validate: Does Nebraska trim outliers? (Review methodology)
- Edge case: σ = 0 (all values identical) - set all indexes to 100

---

## Data Quality Considerations

### Missing Data Strategy

**Approach**:
1. **Prevention**: Select measures with high data availability across all regions
2. **Detection**: Flag missing values during data collection
3. **Handling Options**:
   - Exclude region from specific measure (include in others)
   - Exclude entire measure if > 20% of regions missing
   - Impute using peer region averages (use cautiously)
   - Document all missing data in dashboard

**Nebraska Precedent**:
- Nebraska study did not extensively document missing data handling
- Appears to have high data completeness for all measures

**Virginia Context**:
- Small independent cities may have suppressed ACS estimates due to small sample sizes
- Rural counties may have missing data for healthcare, business measures
- Need to investigate: What is actual missing data rate?

### Data Validation Checks

**Implement Validation Suite**:
1. Range checks: Values within reasonable bounds
2. Temporal consistency: Growth rates make sense
3. Geographic consistency: Similar regions have similar values
4. Source reconciliation: Cross-check against published state statistics
5. Peer validation: Compare to other published indexes (if available)

### Known Data Limitations

**From Nebraska Study**:
- Crime data: Not all jurisdictions report to FBI UCR
- Healthcare: Provider counts may not reflect access (rural providers serving large areas)
- Social capital: Difficult to measure quantitatively
- Business data: May lag by 1-2 years

**Additional Considerations for Virginia**:
- Independent cities complicate county-level data
- DC as peer region may skew comparisons (very different governance, federal employment)
- Appalachian regions may have unique economic characteristics

---

## Code Architecture

### Proposed Module Structure

```python
# Directory structure planning
src/
  api_clients/
    census_api.py       # Census Bureau API wrapper
    bea_api.py          # BEA API wrapper
    bls_api.py          # BLS API wrapper
    fcc_api.py          # FCC broadband data
    fbi_api.py          # FBI crime data
    base_api.py         # Base class with caching, rate limiting

  data_collection/
    fetch_demographics.py
    fetch_economic.py
    fetch_education.py
    fetch_health.py
    fetch_infrastructure.py
    orchestrator.py     # Main data collection orchestration

  processing/
    clean_data.py       # Data cleaning and validation
    aggregate_data.py   # Aggregation for multi-county regions
    derive_measures.py  # Calculate derived measures (growth rates, etc.)

  matching/
    mahalanobis.py      # Peer region matching implementation
    distance_calc.py    # Geographic distance calculations
    matching_vars.py    # Matching variable preparation

  scoring/
    standardize.py      # Standardization and index calculation
    component_index.py  # Component index calculation
    overall_index.py    # Overall Thriving Index

  visualization/
    dashboard_app.py    # Main dashboard application
    map_viz.py          # Map visualization components
    chart_viz.py        # Chart components
    data_export.py      # Export functionality

  utils/
    config.py           # Configuration management
    logging_setup.py    # Logging configuration
    validators.py       # Data validation functions
```

### Design Principles

1. **Modularity**: Each API client is independent; can be tested separately
2. **Caching**: All API clients inherit caching behavior from base class
3. **Error Handling**: Consistent error handling and logging across modules
4. **Testability**: Pure functions for calculations; mock API responses for testing
5. **Configuration**: Environment-based configuration (dev/prod)

### Key Classes

```python
class BaseAPIClient:
    """Base class for all API clients with caching and rate limiting"""
    def __init__(self, api_key, cache_dir, rate_limit)
    def fetch(self, endpoint, params, cache_expiry)
    def _load_cache(self, cache_key)
    def _save_cache(self, cache_key, data)
    def _check_rate_limit(self)

class RegionMatcher:
    """Handles peer region matching using Mahalanobis distance"""
    def __init__(self, regions_df, matching_variables)
    def calculate_distances(self, target_region)
    def find_peers(self, target_region, n_peers=10)
    def validate_matches(self)

class IndexCalculator:
    """Calculates component and overall indexes"""
    def __init__(self, measures_df, methodology="nebraska")
    def standardize_measure(self, measure_name, inverse=False)
    def calculate_component_index(self, component_name)
    def calculate_overall_index(self, weighting=None)
```

---

## Implementation Progress

### Phase 1: Planning & Data Source Identification ⏳

**Status**: IN PROGRESS
**Started**: 2025-11-14

- [x] Create PROJECT_PLAN.md
- [x] Create CLAUDE.md
- [ ] Map all 47 measures to API sources
- [ ] Identify available API keys in environment
- [ ] Document API requirements and access methods
- [ ] Determine measures to include in initial analysis
- [ ] Finalize Virginia region definition approach
- [ ] Define regions in surrounding states

**Next Session Goals**:
1. Complete comprehensive API source mapping for all 47 measures
2. Check environment variables for existing API keys
3. Test API connections with sample requests
4. Make initial decisions on region definitions

---

## Open Questions & Blockers

### Questions for User

1. **Region Granularity**: Preference for county-level vs multi-county regions for Virginia?
2. **Independent Cities**: Should Virginia's independent cities be separate regions or merged with adjacent counties?
3. **DC Inclusion**: Should Washington DC be included as a peer region candidate? (Very different characteristics)
4. **Weighting**: Should the 8 component indexes be weighted equally or should some be prioritized?
5. **Update Frequency**: How often should the dashboard data be refreshed?
6. **Public vs Private**: Will this dashboard be public-facing or internal use only?

### Current Blockers

None at this time.

---

## Resources & References

### Primary Sources
- **Nebraska Thriving Index 2022 Report**: `/home/user/thriving_index/Thriving_Index.pdf`
- **Comparison Regions Methodology**: `/home/user/thriving_index/Comparison_Regions.pdf`
- **Nebraska Calculations**: `/home/user/thriving_index/Thriving_Index_Calculations.xlsx`

### External Documentation
- Census API Documentation: https://www.census.gov/data/developers/data-sets.html
- BEA API Documentation: https://apps.bea.gov/api/
- BLS API Documentation: https://www.bls.gov/developers/
- Mahalanobis Distance: https://en.wikipedia.org/wiki/Mahalanobis_distance
- Plotly Dash: https://dash.plotly.com/
- Virginia Planning District Commissions: https://www.vapdc.org/

### Related Research
- County Health Rankings: https://www.countyhealthrankings.org/
- Economic Innovation Group Distressed Communities Index: https://eig.org/dci/
- USDA Rural-Urban Continuum Codes: https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/

---

## Lessons Learned

*This section will be updated as the project progresses*

---

## Next Steps

1. **Immediate (Current Session)**:
   - ✅ Complete API source mapping for all 47 measures
   - ✅ Check environment for API keys
   - 🔄 Test sample API requests to verify access (NEXT)
   - ⏳ Make region definition decision

2. **Short Term (This Week)**:
   - Set up project structure
   - Implement base API client class
   - Create Census API client
   - Begin data collection for matching variables

3. **Medium Term (Next 2 Weeks)**:
   - Complete all API clients
   - Collect data for all regions
   - Implement peer region matching
   - Begin index calculations

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2025-11-14 | Created CLAUDE.md | Initial project setup and documentation |
| 2025-11-14 | Created PROJECT_PLAN.md | Comprehensive project roadmap |
| 2025-11-14 | Created API_MAPPING.md | Detailed analysis of all 47 measures and API availability |
| 2025-11-14 | Created API_KEYS_STATUS.md | Documentation of available API keys and coverage |
| 2025-11-14 | Verified API keys in environment | Confirmed CENSUS_KEY, BEA_API_KEY, BLS_API_KEY, FRED_API_KEY available |
| 2025-11-14 | Completed Phase 1 initial analysis | 28 HIGH-confidence measures identified; ready for Phase 2 |

---

*This document is continuously updated throughout development.*
