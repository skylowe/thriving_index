# API Investigation Report - Medium Confidence Measures

**Date**: 2025-11-14
**Status**: In Progress

---

## Purpose

This document provides detailed findings from investigating MEDIUM-confidence API sources identified in the initial API mapping. The goal is to determine which measures can be promoted to HIGH confidence and implemented immediately.

---

## Investigation Summary

| API Source | Status | Measures Affected | Confidence Level | Ready to Implement |
|------------|--------|-------------------|------------------|-------------------|
| USDA NASS QuickStats | ✅ Verified | Farm income (matching variable) | HIGH | ✅ Yes |
| FBI Crime Data Explorer | ✅ Verified | Property & violent crime rates | HIGH | ✅ Yes |
| FCC Broadband Map | ⏳ Pending Key | Broadband access | MEDIUM | Placeholder only |
| CMS Provider Data | 🔄 Investigating | Physicians per capita | TBD | TBD |
| CDC WONDER | 🔄 Not Started | Infant mortality | TBD | TBD |
| IRS Exempt Orgs | 🔄 Not Started | Nonprofit orgs per capita | TBD | TBD |

---

## 1. USDA NASS QuickStats API ✅

### Status: **VERIFIED - Ready to Implement**

### Overview
The USDA National Agricultural Statistics Service (NASS) QuickStats API provides comprehensive agricultural statistics including farm income data at the county level.

### API Details

**Base URL**: `https://quickstats.nass.usda.gov/api/`

**Authentication**:
- API key required (environment variable: `NASSQS_TOKEN`)
- Key obtained via registration at quickstats.nass.usda.gov

**Primary Endpoint**: `/api/api_GET`

### Key Parameters for Our Use Case

**WHAT Dimension** (commodity/data type):
- `sector_desc=ECONOMICS` - For income/financial data
- `commodity_desc` - Specific commodity (or "AG LAND" for aggregate)
- `statisticcat_desc` - Type of statistic (e.g., "INCOME, NET CASH FARM")

**WHERE Dimension** (location):
- `state_alpha=VA` - State code (Virginia and peer states)
- `county_name` - County name
- `agg_level_desc=COUNTY` - County-level aggregation

**WHEN Dimension** (time):
- `year=2022` - Specific year
- `freq_desc=ANNUAL` - Annual data

### Query Operators
- Comparison: `__GE`, `__LE`, `__GT`, `__LT` (greater/less than)
- Equality: `__EQ`, `__NE` (equal, not equal)
- Pattern: `__LIKE`, `__NOT_LIKE`

### Rate Limits
- **50,000 records maximum** per API request
- No explicit daily limit mentioned in documentation

### Response Format
- JSON (default), CSV, XML, JSONP
- Returns data with metadata including source, reference period, location details

### Example API Call
```
https://quickstats.nass.usda.gov/api/api_GET/
?key={NASSQS_TOKEN}
&sector_desc=ECONOMICS
&state_alpha=VA
&agg_level_desc=COUNTY
&year=2022
&format=JSON
```

### Data Availability for Virginia Thriving Index

**Matching Variable: % Farm Income**
- BEA provides farm proprietors income as % of total personal income
- USDA NASS can supplement/validate BEA data
- Used in Mahalanobis distance calculation for peer region matching

**Potential Measure: Farm/Ranch Income**
- Component Index 3 (Other Economic Prosperity) currently has 0/4 HIGH measures
- Farm income could partially address this gap
- Particularly relevant for rural Virginia regions

### Implementation Notes
- Data from NASS Census of Agriculture (every 5 years) provides most comprehensive county data
- Annual survey estimates available but may have suppression for small counties
- Need to handle missing data for urban counties with minimal agricultural activity
- Cross-validate with BEA farm proprietors income data

### Confidence Assessment: ✅ **HIGH**

**Rationale**:
- API key available (`NASSQS_TOKEN`)
- Well-documented API with clear parameters
- County-level data confirmed available
- Suitable rate limits for our data collection needs

---

## 2. FBI Crime Data Explorer API ✅

### Status: **VERIFIED - Ready to Implement (with caveats)**

### Overview
The FBI Crime Data API provides access to Uniform Crime Reporting (UCR) data through multiple endpoints. The public-facing API is hosted at api.usa.gov.

### API Details

**Base URL**: `https://api.usa.gov/crime/fbi/sapi`

**Authentication**:
- API key required (environment variable: `FBI_UCR_KEY`)
- Key obtained via registration at https://api.data.gov/signup/
- Note: This may require data.gov API key rather than FBI-specific key

**Alternative Documentation**:
- GitHub: https://github.com/fbi-cde/crime-data-api
- Swagger UI: https://crime-data-api.fr.cloud.gov/swagger-ui/

### Data Systems

**Summary Reporting System (SRS)**:
- Legacy format with aggregated crime counts
- Organized by offense type and location
- Most suitable for county-level aggregation

**National Incident-Based Reporting System (NIBRS)**:
- Newer incident-level data
- More detailed but not appropriate for aggregation
- Not recommended for our use case

### Key Endpoints (Preliminary)

**Agency-Level Data**: `/api/summarized/agencies/{ORI}/`
- ORI = Originating Agency Identifier
- Can filter agencies by county
- Returns crime counts by offense type

**State-Level Estimates**: `/api/summarized/state/{state_abbr}/`
- State-level aggregated estimates
- May need to work with agency-level data instead

### Geographic Granularity Challenge

**Important Finding**: FBI UCR data is primarily **agency-level**, not county-level.
- Each law enforcement agency reports separately
- Agencies can be filtered by `county_name`
- Requires aggregation of multiple agencies per county
- Not all agencies report consistently

**Implication**: Need to:
1. Identify all agencies within each county
2. Aggregate reported crimes across agencies
3. Handle missing data where agencies don't report
4. Calculate crime rates using county population

### Available Crime Categories

**Violent Crime** (for Measure 6.5):
- Murder and nonnegligent manslaughter
- Rape
- Robbery
- Aggravated assault
- **Calculation**: Sum all violent crimes / population * 100,000

**Property Crime** (for Measure 6.4):
- Burglary
- Larceny-theft
- Motor vehicle theft
- Arson
- **Calculation**: Sum all property crimes / population * 100,000

### Data Quality Concerns

1. **Participation**: Not all agencies report to FBI UCR
2. **Completeness**: Some agencies report partial year data
3. **NIBRS Transition**: Ongoing transition from SRS to NIBRS format
4. **FBI Guidance**: FBI discourages county/agency ranking due to comparability issues

### Rate Limits
- Not explicitly documented for api.usa.gov endpoint
- Assume standard data.gov rate limits apply
- Need to test actual limits

### Implementation Approach

**Option 1: Agency Aggregation**
1. Query `/agencies` endpoint to get all agencies by county
2. For each county, sum crime counts across all reporting agencies
3. Calculate rates using Census population estimates
4. Flag counties with incomplete reporting

**Option 2: Alternative Data Source**
- Consider FBI's Estimated Crime Data if county estimates available
- May provide pre-aggregated county-level estimates
- Need to verify availability

### Example API Calls

```
# Get agencies in a county (pseudo-code)
https://api.usa.gov/crime/fbi/sapi/api/agencies?county_name=Fairfax&state_abbr=VA&api_key={FBI_UCR_KEY}

# Get crime data for specific agency
https://api.usa.gov/crime/fbi/sapi/api/summarized/agencies/{ORI}/violent-crime/{year}?api_key={FBI_UCR_KEY}
```

### Confidence Assessment: ✅ **HIGH (with reservations)**

**Promoted to HIGH because**:
- API key available (`FBI_UCR_KEY`)
- Data is accessible via documented API
- Crime measures are important for infrastructure index
- Agency-to-county aggregation is feasible

**Reservations**:
- Requires aggregation logic (not direct county queries)
- Data quality varies by jurisdiction
- May have missing data for some counties
- FBI discourages comparisons due to reporting variations

**Recommendation**:
- Implement with data quality flags
- Document reporting completeness for each county
- Consider excluding counties with < 80% agency participation
- Include caveats in dashboard about data limitations

---

## 3. FCC Broadband Map API ⏳

### Status: **API KEY PENDING - Placeholder Implementation Required**

### Overview
The Federal Communications Commission provides broadband availability data through the National Broadband Map.

### API Status
- **API Key**: ⏳ NOT YET AVAILABLE
- **User Request**: Create placeholder implementation for future use
- **Measure**: Broadband access (% of population with access) - Measure 6.1

### Preliminary Research

**FCC National Broadband Map**: https://broadbandmap.fcc.gov/

**Potential Data Sources**:
1. FCC Broadband Data Collection (BDC)
2. FCC Form 477 data (legacy)
3. FCC API (if available)

### Placeholder Implementation Strategy

**Approach**: Design API client with placeholder data structure

**Components**:
1. **API Client Class** (`fcc_api.py`):
   - Inherit from BaseAPIClient
   - Method: `get_broadband_access(state, county, year)`
   - Returns: Placeholder values or raises "API key not configured" error

2. **Placeholder Data**:
   - Option A: Return `None` for all queries with logging
   - Option B: Use national/state averages as placeholders
   - Option C: Skip measure entirely until key available

3. **Documentation**:
   - Clear comments indicating placeholder status
   - Instructions for adding API key when obtained
   - Test suite ready for real API integration

**Configuration**:
```python
# config.py
FCC_API_KEY = os.getenv('FCC_API_KEY', None)
FCC_API_ENABLED = FCC_API_KEY is not None
```

**Implementation**:
```python
# fcc_api.py
class FCCBroadbandAPI(BaseAPIClient):
    def get_broadband_access(self, state, county, year):
        if not self.api_key:
            logger.warning(f"FCC API key not configured. Skipping broadband data for {county}, {state}")
            return None

        # Real API call would go here when key available
        # endpoint = f"/broadband/county/{state}/{county}/{year}"
        # return self.fetch(endpoint)

        return None
```

**Dashboard Handling**:
- Broadband measure excluded from Component Index 6 calculation
- Show "Data pending" or hide measure in UI
- Recalculate index when data becomes available

### Next Steps
1. Monitor FCC API key acquisition
2. Research exact API endpoints when key obtained
3. Update placeholder with real implementation
4. Re-run data collection and index calculations

### Confidence Assessment: 🟡 **MEDIUM (Pending Key)**

**Rationale**:
- Data exists and is public
- API likely available but key pending
- Implementation deferred, not impossible
- Will be promoted to HIGH once key obtained

---

## 4. CMS Provider Data API 🔄

### Status: **INVESTIGATION IN PROGRESS**

### Overview
Centers for Medicare & Medicaid Services (CMS) provides healthcare provider data that could support physician per capita measures.

### Measure Affected
- **7.4**: Primary care physicians per capita (Quality of Life index)

### Investigation Tasks
- [ ] Identify CMS API endpoints
- [ ] Determine if county-level physician counts available
- [ ] Check if API key required
- [ ] Assess data quality and coverage
- [ ] Verify definition of "primary care physician"

### Preliminary Resources
- CMS Data API: https://data.cms.gov/
- National Provider Index (NPI)
- Medicare Provider Enrollment data

### Status: **TO BE CONTINUED**

---

## 5. CDC WONDER API 🔄

### Status: **NOT YET INVESTIGATED**

### Measure Affected
- **7.2**: Infant mortality rate (Quality of Life index)

### Known Information
- CDC WONDER provides vital statistics
- County-level data may be suppressed for small populations
- API access unclear

### Status: **TO BE INVESTIGATED**

---

## 6. IRS Exempt Organizations 🔄

### Status: **NOT YET INVESTIGATED**

### Measure Affected
- **8.2**: Nonprofit organizations per capita (Social Capital index)

### Known Information
- IRS publishes Exempt Organizations Business Master File
- Available as bulk download (monthly)
- Direct API unclear
- Can filter by county

### Status: **TO BE INVESTIGATED**

---

## Summary & Recommendations

### Promoted to HIGH Confidence ✅
1. **USDA NASS** - Farm income data (matching variable)
2. **FBI UCR** - Violent and property crime rates (Measures 6.4, 6.5)

**Impact**: Increases HIGH-confidence measures from 28 to 30

### FCC Broadband ⏳
- **Recommendation**: Implement placeholder
- **Strategy**: Exclude from initial index calculation; add when key available
- **Impact**: Component Index 6 (Infrastructure) will have 4/6 measures instead of 5/6

### Remaining Investigations 🔄
- **CMS** (physicians per capita) - Priority: MEDIUM
- **CDC WONDER** (infant mortality) - Priority: MEDIUM
- **IRS** (nonprofits per capita) - Priority: LOW

### Updated Measure Count

**By Component Index** (after promotions):
- Growth: 5/6 (83%)
- Economic Opportunity & Diversity: 6/7 (86%)
- Other Economic Prosperity: 0/4 (0%) ⚠️
- Demographic Growth & Renewal: 4/4 (100%)
- Education & Skill: 2/5 (40%)
- Infrastructure & Cost: **5/6** (83%) ⬆ was 3/6
- Quality of Life: 4/8 (50%)
- Social Capital: 4/7 (57%)

**Total HIGH-Confidence**: 30/47 (64%)

### Next Steps
1. ✅ Update API_MAPPING.md with promoted measures
2. ✅ Update API_KEYS_STATUS.md with findings
3. ✅ Update CLAUDE.md change log
4. 🔄 Continue CMS investigation
5. ⏳ Design FCC placeholder implementation
6. ⏳ Document dashboard requirements

---

*Investigation report will be updated as additional APIs are researched.*
