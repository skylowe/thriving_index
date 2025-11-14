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
| USDA NASS QuickStats | ✅ Verified | Farm income (matching variable) | HIGH | ✅ Yes (API) |
| FBI Crime Data Explorer | ✅ Verified | Property & violent crime rates | HIGH | ✅ Yes (API) |
| CMS NPPES NPI | ✅ Verified | Physicians per capita | HIGH | ✅ Yes (Bulk Download) |
| IRS EO BMF | ✅ Verified | Nonprofit orgs per capita | HIGH | ✅ Yes (Bulk Download) |
| CDC WONDER | ❌ Excluded | Infant mortality | EXCLUDED | ❌ No (API Limitation) |
| FCC Broadband Map | ⏳ Pending Key | Broadband access | MEDIUM | ⏳ Placeholder only |

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

## 4. CMS NPPES NPI API ✅

### Status: **VERIFIED - Bulk Download Approach Recommended**

### Overview
The Centers for Medicare & Medicaid Services (CMS) maintains the National Plan and Provider Enumeration System (NPPES), which contains information about healthcare providers including the National Provider Identifier (NPI) registry.

### Measure Affected
- **7.4**: Primary care physicians per capita (Quality of Life index)

### API Details

**Base URL**: `https://npiregistry.cms.hhs.gov/api/`

**Authentication**: No API key required for public NPI Registry API

**Alternative APIs**:
1. **CMS NPPES API**: Official registry at npiregistry.cms.hhs.gov
2. **NLM Clinical Tables API**: `https://clinicaltables.nlm.nih.gov/apidoc/npi_org/v3/doc.html`
   - Uses NPI data from CMS
   - Includes Healthcare Provider Taxonomy from NUCC
   - Provides crosswalk data

### Data Format & Availability

**Geographic Granularity**:
- Provider-level records with **ZIP codes** (not direct county assignment)
- Requires ZIP-to-county crosswalk for aggregation
- Address fields: street, city, state, ZIP code

**Data Volume**:
- As of November 2025: 9.3 GB raw CSV file when extracted
- 947.84 MB compressed download
- Updated **weekly** by CMS
- Contains all active provider NPIs

**Download Source**: https://download.cms.gov/nppes/NPI_Files.html

### Implementation Approach

**Recommended Strategy**: **Bulk Download + Local Processing**

**Rationale**:
- API designed for individual provider lookups, not bulk county aggregation
- Large dataset (~10GB) better handled as bulk download
- Weekly updates available - download once, use repeatedly
- No rate limiting concerns with bulk data

**Processing Pipeline**:
1. Download NPPES bulk data file (weekly or monthly refresh)
2. Filter to relevant states (VA, MD, WV, NC, TN, KY, DC)
3. Use ZIP-to-county crosswalk to assign counties
4. Filter by provider taxonomy codes for "primary care physicians":
   - Family Medicine
   - General Practice
   - Internal Medicine
   - Pediatrics
5. Count unique NPIs per county
6. Calculate per capita rates using Census population

**ZIP-to-County Crosswalk**:
- HUD USPS ZIP Code Crosswalk Files: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
- Maps ZIP codes to counties with residential/business allocation ratios
- Updated quarterly

### Provider Taxonomy Codes

**Primary Care Physician Codes** (from NUCC taxonomy):
- `207Q00000X` - Family Medicine
- `208D00000X` - General Practice
- `207R00000X` - Internal Medicine
- `2080P0216X` - Pediatrics

**Data Fields Available**:
- Provider name, credentials
- Business address (street, city, state, ZIP)
- Primary taxonomy code
- License information
- Active status

### Data Quality Considerations

**Strengths**:
- Comprehensive coverage of Medicare/Medicaid providers
- Regularly updated (weekly)
- Authoritative government source
- Includes taxonomy classification

**Limitations**:
- May not capture all physicians (only those billing Medicare/Medicaid)
- ZIP-to-county assignment adds complexity
- Urban ZIP codes may span multiple counties
- Rural providers may serve multiple counties

**Data Suppression**: No population-based suppression like Census; all providers included

### Alternative: API-Based Approach

**If Bulk Download Not Feasible**:
- Query NPPES API by state and taxonomy code
- Paginate through results (API supports pagination)
- Filter and aggregate locally
- Much slower but avoids large file downloads

**API Query Example**:
```
https://npiregistry.cms.hhs.gov/api/?version=2.1&state=VA&taxonomy_description=Family%20Medicine&limit=200
```

### Implementation Complexity

**Estimated Effort**: Medium-High
- Bulk download: Simple (wget or API download)
- Data parsing: Medium (9GB CSV)
- ZIP-to-county mapping: Medium (requires crosswalk file)
- Taxonomy filtering: Low (simple field match)
- Aggregation: Low (group by county and count)

### Rate Limits
- **Bulk Download**: No limits (public data)
- **API**: Not explicitly documented; assume reasonable use

### Confidence Assessment: ✅ **HIGH - Bulk Download Method**

**Promoted to HIGH because**:
- Data is publicly accessible and comprehensive
- No API key required
- Weekly updates ensure freshness
- Clear methodology for county aggregation
- Provider taxonomy allows precise physician definition

**Implementation Notes**:
- Use bulk download approach for efficiency
- Implement as initial data pipeline step (not real-time API)
- Cache processed county-level aggregations
- Refresh monthly or quarterly (weekly updates likely unnecessary)
- Document ZIP-to-county methodology clearly

### Status: ✅ **INVESTIGATION COMPLETE - READY TO IMPLEMENT**

---

## 5. CDC WONDER API ⚠️

### Status: **CRITICAL LIMITATION IDENTIFIED - API RESTRICTED TO NATIONAL DATA ONLY**

### Measure Affected
- **7.2**: Infant mortality rate (Quality of Life index)

### Overview
CDC WONDER (Wide-ranging OnLine Data for Epidemiologic Research) provides access to vital statistics including the Linked Birth/Infant Death Records dataset.

### API Details

**Base URL**: `https://wonder.cdc.gov/controller/datarequest/`

**Data Available**:
- Linked Birth/Infant Death Records
- Infant mortality counts and rates
- Available since 1995
- County-level data available in web interface

### CRITICAL LIMITATION ⚠️

**Geographic Restriction in API**:
> "Only national data are available for query by the API, and queries for mortality and births statistics from the National Vital Statistics System cannot limit or group results by any location field, such as Region, Division, State or County."

**Translation**:
- Web interface at wonder.cdc.gov allows county-level queries
- **API is restricted to national-level data only**
- This is a policy decision by CDC for vital statistics data
- No workaround via API parameters

### Additional Restrictions

**Population Threshold**:
- Only counties with total population ≥ 250,000 are listed in infant death queries
- This excludes most Virginia counties (only ~10-15 counties meet threshold)
- Small-population suppression for privacy

**Web Interface Access**:
- Interactive queries: https://wonder.cdc.gov/lbd.html
- Can download county-level data manually
- No automation possible via API

### Alternative Approaches

**Option 1: Manual Web Interface Queries** ❌
- Download data manually from CDC WONDER web interface
- Not scalable or automatable
- Violates project requirement for API-accessible data
- **Not recommended**

**Option 2: Alternative Data Source - State Health Departments** 🤔
- Virginia Department of Health may provide county-level infant mortality
- Would need to collect from each state separately
- Non-standardized formats
- Likely no APIs available
- **Complex, not recommended**

**Option 3: Use State-Level Data Only** ⚠️
- Query API for state-level infant mortality rates
- Apply same rate to all counties within state
- Loss of geographic variation
- Poor methodology for county comparisons
- **Not ideal but possible fallback**

**Option 4: Exclude Measure from Index** ✅
- Drop infant mortality from Component Index 7 (Quality of Life)
- Component would have 7 measures instead of 8
- Cleanest approach given API limitation
- **Recommended approach**

### Implementation Recommendation

**Decision**: **EXCLUDE MEASURE 7.2 (Infant Mortality) from Index**

**Rationale**:
1. API limitation is policy-based, not technical - unlikely to change
2. Manual data collection violates project principles
3. State-level rates don't provide county variation needed
4. Component Index 7 still has 7 other measures (4 currently HIGH confidence)
5. Maintains data quality and automation standards

**Impact on Quality of Life Index**:
- Before: 4/8 HIGH-confidence measures (50%)
- After excluding 7.2: 4/7 HIGH-confidence measures (57%)
- Improves percentage while maintaining quality

### CDC WONDER API Capabilities (What It Can Do)

Despite geographic limitations, the API can provide:
- National-level vital statistics
- Trend analysis over time
- Demographic breakdowns (age, race, sex)
- Useful for research but not for our county comparison needs

### Example API Structure

```python
# Pseudo-code - what the API CAN do
import requests
url = "https://wonder.cdc.gov/controller/datarequest/D76"
# Can only get national data:
params = {
    "year": "2022",
    "measure": "infant_deaths",
    # Cannot include: "county": "Fairfax"  <- Not allowed
}
```

### GitHub Resources

**Community API Wrappers**:
- https://github.com/alipphardt/cdc-wonder-api
- Provides Python examples for API usage
- Confirms geographic limitation

### Confidence Assessment: ❌ **EXCLUDED - API Limitation**

**Status Change**: MEDIUM → **EXCLUDED**

**Rationale for Exclusion**:
- API restriction is intentional CDC policy, not technical limitation
- County-level data not accessible via automated means
- Alternative approaches violate project requirements or compromise quality
- Component index remains robust with remaining measures

**Documentation Note**:
- Clearly document why infant mortality excluded in methodology notes
- Explain CDC API limitation in dashboard
- Consider adding in future if CDC policy changes

### Status: ✅ **INVESTIGATION COMPLETE - MEASURE EXCLUDED**

---

## 6. IRS Exempt Organizations ✅

### Status: **VERIFIED - Bulk Download Approach Recommended**

### Measure Affected
- **8.2**: Nonprofit organizations per capita (Social Capital index)

### Overview
The Internal Revenue Service (IRS) maintains the Exempt Organizations Business Master File (EO BMF), which contains information on all active tax-exempt organizations recognized under Section 501(c) of the tax code.

### Data Details

**Official IRS Source**:
- **Tax Exempt Organization Search**: https://www.irs.gov/charities-non-profits/tax-exempt-organization-search
- **Bulk Data Downloads**: https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads
- **Update Frequency**: Monthly

**Authentication**: No API key required for bulk downloads

### Data Format & Availability

**Geographic Granularity**:
- Organization-level records with full address
- Fields: EIN, NAME, STREET, CITY, STATE, ZIP
- Requires aggregation to county level using:
  - City name matching (less reliable)
  - ZIP-to-county crosswalk (more reliable)

**File Structure**:
- Available as regional CSV files or by state
- Regional files cover 4 areas:
  - Region 1: Northeast (CT, ME, MA, NH, NJ, NY, RI, VT)
  - Region 2: Mid-Atlantic and Great Lakes
  - Region 3: Gulf Coast and Pacific Coast
  - Includes all states needed: VA, MD, WV, NC, TN, KY, DC

**Data Size**: Moderate (millions of organizations nationally, manageable when filtered by region)

### Implementation Approach

**Recommended Strategy**: **Bulk Download + Local Processing**

**Rationale**:
- No real-time API provided by IRS for bulk queries
- Monthly updates sufficient for index calculation
- Bulk download more efficient than individual queries
- Avoids potential rate limiting issues

**Processing Pipeline**:
1. Download EO BMF regional files (monthly refresh)
2. Filter to relevant states (VA, MD, WV, NC, TN, KY, DC)
3. Use ZIP-to-county crosswalk to assign counties
4. Filter to relevant exempt organization types:
   - 501(c)(3) public charities (most common nonprofits)
   - Potentially exclude private foundations, churches
5. Count unique EINs per county
6. Calculate per capita rates using Census population

**ZIP-to-County Crosswalk**:
- Same HUD USPS crosswalk as used for CMS physician data
- https://www.huduser.gov/portal/datasets/usps_crosswalk.html

### Organization Type Filtering

**501(c) Categories** (from IRS):
- **501(c)(3)**: Charitable organizations (recommended focus)
  - Public charities
  - Private foundations
  - Religious organizations
- **501(c)(4)**: Social welfare organizations
- **501(c)(5)**: Labor unions
- **501(c)(6)**: Business leagues, chambers of commerce
- Many others (up to 501(c)(29))

**Recommendation**: Focus on **501(c)(3) public charities** as primary "nonprofits"
- Most closely aligns with community-serving organizations
- Excludes private foundations (often family foundations)
- May include or exclude religious organizations based on preference

### Alternative API: ProPublica Nonprofit Explorer

**ProPublica API**: https://projects.propublica.org/nonprofits/api

**Features**:
- Programmatic access to nonprofit data
- Includes organization profiles with addresses
- Merges with IRS filing data (Form 990)
- Free for non-commercial use

**Advantages**:
- RESTful API interface (easier than bulk downloads)
- Enhanced data with Form 990 information
- Search by geography and organization name
- JSON responses

**Limitations**:
- Rate limiting (need to verify limits)
- May not include all organizations in IRS database
- Third-party service (not official IRS)

**Recommendation**: Use as **alternative** if IRS bulk download proves challenging

### Example ProPublica API Query
```
# Search by state
GET https://projects.propublica.org/nonprofits/api/v2/search.json?state[id]=VA

# Get organization details
GET https://projects.propublica.org/nonprofits/api/v2/organizations/{EIN}.json
```

### Data Quality Considerations

**Strengths**:
- Comprehensive registry of all tax-exempt organizations
- Official government source
- Monthly updates
- Includes active status

**Limitations**:
- ZIP-to-county assignment adds complexity
- Definition of "nonprofit" varies (need to filter organization types)
- Some organizations may be inactive but still in database
- Address may be headquarters, not service location

**Filtering Recommendations**:
- Use only organizations with NTEE codes (National Taxonomy of Exempt Entities)
- Exclude organizations with revoked tax-exempt status
- Consider revenue thresholds to focus on active organizations

### Implementation Complexity

**Estimated Effort**: Medium
- Bulk download: Simple (direct HTTP download)
- Data parsing: Low (CSV format)
- ZIP-to-county mapping: Medium (requires crosswalk file, same as CMS)
- Organization type filtering: Medium (need to understand taxonomy)
- Aggregation: Low (group by county and count)

### Alternative: Third-Party APIs

**GuideStar (Candid)**: https://www.guidestar.org/
- Commercial API with more features
- Requires subscription/API key
- Enhanced nonprofit profiles
- Not recommended for free project

### Confidence Assessment: ✅ **HIGH - Bulk Download Method**

**Promoted to HIGH because**:
- Data is publicly accessible and comprehensive
- No API key required for IRS bulk downloads
- Monthly updates sufficient for project needs
- Clear methodology for county aggregation
- ProPublica API available as alternative

**Implementation Notes**:
- Use IRS bulk download as primary source
- ProPublica API as backup option
- Implement as initial data pipeline step (not real-time)
- Cache processed county-level aggregations
- Refresh quarterly (monthly updates likely unnecessary)
- Document organization type filtering clearly
- Same ZIP-to-county crosswalk as CMS physician data

**Organization Type Decision Needed**:
- Recommend focusing on 501(c)(3) public charities
- User may prefer broader definition (all 501(c) types)
- Should document choice in methodology

### Status: ✅ **INVESTIGATION COMPLETE - READY TO IMPLEMENT**

---

## Summary & Recommendations

### Promoted to HIGH Confidence ✅
1. **USDA NASS** - Farm income data (matching variable)
2. **FBI UCR** - Violent and property crime rates (Measures 6.4, 6.5)
3. **CMS NPPES** - Primary care physicians per capita (Measure 7.4) - Bulk download method
4. **IRS EO BMF** - Nonprofit organizations per capita (Measure 8.2) - Bulk download method

**Impact**: Increases HIGH-confidence measures from 28 to **32**

### Excluded Due to API Limitations ❌
1. **CDC WONDER** - Infant mortality (Measure 7.2) - API restricted to national data only

**Rationale**:
- CDC policy restricts API to national-level queries only
- County-level data only available via manual web interface
- Violates project requirement for API-accessible data
- Maintaining data quality standards over measure quantity

### FCC Broadband ⏳
- **Recommendation**: Implement placeholder
- **Strategy**: Exclude from initial index calculation; add when key available
- **Impact**: Component Index 6 (Infrastructure) will have 4/6 measures instead of 5/6

### Updated Measure Count

**By Component Index** (after all investigations):
- Growth: 5/6 (83%)
- Economic Opportunity & Diversity: 6/7 (86%)
- Other Economic Prosperity: 0/4 (0%) ⚠️ *Still needs attention*
- Demographic Growth & Renewal: 4/4 (100%)
- Education & Skill: 2/5 (40%)
- Infrastructure & Cost: **5/6** (83%) ⬆ was 3/6
- Quality of Life: **4/7** (57%) ⬆ was 4/8 (measure 7.2 excluded)
- Social Capital: **5/7** (71%) ⬆ was 4/7

**Total HIGH-Confidence**: **32/46** (69.6%)
- Note: Total measures reduced from 47 to 46 due to exclusion of 7.2

### Implementation Approach Summary

**Traditional API Clients** (real-time queries):
- Census Bureau (ACS, CBP)
- Bureau of Economic Analysis (BEA)
- Bureau of Labor Statistics (BLS)
- USDA NASS QuickStats
- FBI Crime Data Explorer
- Federal Reserve (FRED) - bonus data source

**Bulk Download Pipeline** (batch processing):
- CMS NPPES NPI Registry (~9GB CSV, weekly updates)
- IRS Exempt Organizations (~regional CSV, monthly updates)
- Both require ZIP-to-county crosswalk

**Placeholder Implementations**:
- FCC Broadband (pending API key)

**Excluded**:
- CDC WONDER (API limitation, not data availability)

### Key Implementation Dependencies

**ZIP-to-County Crosswalk File**:
- Required for: CMS physician data, IRS nonprofit data
- Source: HUD USPS ZIP Code Crosswalk Files
- URL: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
- Update frequency: Quarterly
- **Action Item**: Download and integrate into data pipeline

**Taxonomy/Classification Files**:
- NUCC Healthcare Provider Taxonomy (for CMS physician filtering)
- IRS NTEE Codes (for nonprofit organization filtering)
- **Action Item**: Document filtering criteria for both

### Data Quality Flags Needed

Implement data quality indicators for:
1. **FBI Crime Data**: Flag counties with < 80% agency reporting
2. **CMS Physician Data**: Note that only Medicare/Medicaid providers included
3. **IRS Nonprofit Data**: Document organization type filtering (501(c)(3) vs all)
4. **Census Data**: Flag suppressed values for small populations
5. **FCC Broadband**: Mark as "Data Pending" until API key obtained

### Next Steps - Phase 2 Implementation

**Immediate (This Session)**:
1. ✅ Update API_INVESTIGATION_REPORT.md (COMPLETE)
2. ⏳ Update API_MAPPING.md with promoted/excluded measures
3. ⏳ Create base API client architecture
4. ⏳ Implement BaseAPIClient class
5. ⏳ Create project directory structure

**Short Term (Next Session)**:
1. Implement Census API client (highest priority - most measures)
2. Implement BEA API client
3. Implement BLS API client
4. Download and process ZIP-to-county crosswalk
5. Test all API connections

**Medium Term**:
1. Implement USDA NASS client
2. Implement FBI UCR client with aggregation logic
3. Create bulk download pipeline for CMS NPPES
4. Create bulk download pipeline for IRS EO BMF
5. Implement FCC placeholder

### Critical Decision Points

**Decision Needed: Component Index 3 (Other Economic Prosperity)**
- Currently 0/4 HIGH-confidence measures (0%)
- All 4 measures (self-employment, business formations, etc.) are LOW confidence
- **Options**:
  1. Investigate additional APIs for these measures
  2. Exclude Component Index 3 entirely from Overall Index
  3. Proceed with incomplete component using available measures
- **Recommendation**: Investigate before proceeding to Phase 3

**Decision Needed: IRS Nonprofit Filtering**
- Should we include all 501(c) organizations or only 501(c)(3) public charities?
- **Recommendation**: 501(c)(3) public charities only (most closely matches "nonprofits" concept)

### Investigation Status Summary

| API Source | Status | Measures | Implementation Method | Priority |
|------------|--------|----------|----------------------|----------|
| Census ACS | ✅ Verified | 15+ measures | API Client | **HIGH** |
| BEA | ✅ Verified | 6 measures | API Client | **HIGH** |
| BLS | ✅ Verified | 4 measures | API Client | **HIGH** |
| USDA NASS | ✅ Verified | 1 measure | API Client | MEDIUM |
| FBI UCR | ✅ Verified | 2 measures | API Client (w/ aggregation) | MEDIUM |
| FCC | ⏳ Pending Key | 1 measure | Placeholder | LOW |
| CMS NPPES | ✅ Verified | 1 measure | Bulk Download | MEDIUM |
| IRS EO BMF | ✅ Verified | 1 measure | Bulk Download | MEDIUM |
| CDC WONDER | ❌ Excluded | 0 measures | Not Applicable | N/A |

---

**Phase 1 Complete**: All API investigations finished
**Next Phase**: Phase 2 - Data Collection Infrastructure

---

*Investigation report updated: 2025-11-14 (evening session)*
