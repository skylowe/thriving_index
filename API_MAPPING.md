# Virginia Thriving Index - API Source Mapping

**Last Updated**: 2025-11-14
**Status**: Initial analysis based on Nebraska Thriving Index methodology

---

## Overview

This document maps each of the 47 individual measures from the Nebraska Thriving Index to potential API data sources for the Virginia implementation. Each measure is evaluated for:
- API availability
- Data source reliability
- Geographic granularity (county-level)
- Update frequency
- Implementation confidence (HIGH/MEDIUM/LOW)

---

## Component Index 1: Growth Index (6 measures)

### 1.1 Population Growth Rate (5-year)

- **Nebraska Source**: Census Bureau Population Estimates
- **Virginia API Source**: Census Bureau Population Estimates API
- **API Endpoint**: `https://api.census.gov/data/[year]/pep/population`
- **Required Parameters**: County FIPS codes, time series
- **Confidence**: ✅ **HIGH**
- **Notes**: Need to fetch population for current year and 5 years prior; calculate growth rate
- **Calculation**: `((Pop_current - Pop_5yr_ago) / Pop_5yr_ago) * 100 / 5` (annualized)

### 1.2 Employment Growth Rate (5-year)

- **Nebraska Source**: Bureau of Labor Statistics, Quarterly Census of Employment and Wages (QCEW)
- **Virginia API Source**: BLS QCEW API
- **API Endpoint**: `https://api.bls.gov/publicAPI/v2/timeseries/data/`
- **Series ID Format**: `ENU` + state code + county code + `05` + `510` + industry
- **Confidence**: ✅ **HIGH**
- **Notes**: QCEW provides total employment by county; calculate 5-year change
- **Alternative**: BLS Local Area Unemployment Statistics (LAUS) for total employment

### 1.3 Wages and Salaries Growth Rate (5-year)

- **Nebraska Source**: Bureau of Economic Analysis, Regional Economic Accounts
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC5N (Personal Income by Major Component)
- **Line Code**: 30 (Wages and salaries)
- **Confidence**: ✅ **HIGH**
- **Notes**: County-level wages and salaries available from BEA

### 1.4 Proprietors Income Growth Rate (5-year)

- **Nebraska Source**: Bureau of Economic Analysis, Regional Economic Accounts
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC5N
- **Line Code**: 45 (Proprietors' income)
- **Confidence**: ✅ **HIGH**
- **Notes**: Includes farm and non-farm proprietors income

### 1.5 Per Capita Personal Income Growth Rate (5-year)

- **Nebraska Source**: Bureau of Economic Analysis
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC1 (Personal Income Summary)
- **Line Code**: 3 (Per capita personal income)
- **Confidence**: ✅ **HIGH**
- **Notes**: Directly available from BEA; already calculated per capita

### 1.6 Retail Sales Growth Rate (5-year)

- **Nebraska Source**: State revenue departments, Census Bureau
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: ❌ **LOW**
- **Notes**:
  - Census Bureau Economic Census (every 5 years, not annual)
  - State-level retail sales tax data (may not be public API)
  - County Business Patterns has retail establishments but not sales
- **Decision**: **MAY NEED TO EXCLUDE** - Investigate Virginia Department of Taxation API

---

## Component Index 2: Economic Opportunity & Diversity (7 measures)

### 2.1 Per Capita Personal Income (Level)

- **Nebraska Source**: Bureau of Economic Analysis
- **Virginia API Source**: BEA Regional API
- **Dataset**: CAINC1, Line Code 3
- **Confidence**: ✅ **HIGH**
- **Notes**: Same as 1.5 but level, not growth rate

### 2.2 Median Household Income

- **Nebraska Source**: American Community Survey (ACS) 5-year estimates
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Variable**: B19013_001E (Median household income in the past 12 months)
- **Confidence**: ✅ **HIGH**
- **Notes**: Most recent ACS 5-year estimates (2018-2022)

### 2.3 Poverty Rate (Inverse)

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variables**:
  - S1701_C03_001E (Percent below poverty level)
  - Or B17001 table for detailed poverty
- **Confidence**: ✅ **HIGH**
- **Notes**: Inverse scoring (lower poverty = higher index)

### 2.4 Labor Force Participation Rate

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variables**:
  - S2301_C02_001E (Labor force participation rate)
  - Or calculate from B23025 table
- **Confidence**: ✅ **HIGH**
- **Notes**: Percent of population 16+ in labor force

### 2.5 Unemployment Rate (Inverse)

- **Nebraska Source**: Bureau of Labor Statistics, LAUS
- **Virginia API Source**: BLS LAUS API
- **Series ID Format**: `LAU` + ST + county code + `03` (unemployment rate)
- **Confidence**: ✅ **HIGH**
- **Notes**: Annual average; inverse scoring
- **Alternative**: ACS also has unemployment estimates

### 2.6 Share of Workforce in High-Wage Industries

- **Nebraska Source**: BLS QCEW or County Business Patterns
- **Virginia API Source**: Census County Business Patterns API or BLS QCEW
- **API**: `https://api.census.gov/data/[year]/cbp`
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - Need to define "high-wage industries" (e.g., Information, Finance, Professional Services, Management)
  - Calculate employment share in these NAICS codes
  - CBP provides employment by industry; QCEW provides wages
- **Decision**: Use QCEW if available; define high-wage as industries with wages > 120% of county average

### 2.7 Economic Diversity (Herfindahl-Hirschman Index)

- **Nebraska Source**: Calculated from CBP or QCEW employment by industry
- **Virginia API Source**: Census CBP API
- **API**: `https://api.census.gov/data/[year]/cbp`
- **Variables**: Employment by 2-digit NAICS code
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - HHI = sum of squared employment shares by industry
  - More diverse economy = lower HHI = higher index score
  - Inverse scoring needed
- **Calculation**: `HHI = Σ(employment_share_i)²` where i = industry

---

## Component Index 3: Other Economic Prosperity (4 measures)

### 3.1 Per Capita Retail Sales

- **Nebraska Source**: State revenue data, Economic Census
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: ❌ **LOW**
- **Notes**: Same issue as measure 1.6
- **Decision**: **MAY NEED TO EXCLUDE** or use proxy (retail establishments per capita)

### 3.2 Per Capita Bank Deposits

- **Nebraska Source**: FDIC Summary of Deposits
- **Virginia API Source**: FDIC API or bulk download
- **API**: FDIC provides data, but API access unclear
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - FDIC Summary of Deposits is public data
  - May need to use bulk download rather than API
  - Annual data by county
- **Decision**: Investigate FDIC data access; may need web scraping or bulk file

### 3.3 New Business Formations Per Capita

- **Nebraska Source**: Census Bureau Business Formation Statistics
- **Virginia API Source**: Census Business Formation Statistics (BFS)
- **API**: May be available through Census API
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - Census BFS launched 2020, provides quarterly business applications
  - County-level data availability unclear
  - May only be available at state or metro level
- **Decision**: **INVESTIGATE** - If not available at county level, may need to exclude

### 3.4 Business Survival Rate

- **Nebraska Source**: Census Bureau Business Dynamics Statistics (BDS)
- **Virginia API Source**: Census BDS
- **Confidence**: ❌ **LOW**
- **Notes**:
  - BDS provides establishment entry/exit rates
  - County-level detail may be suppressed for small counties
  - No clear API access
- **Decision**: **LIKELY EXCLUDE** - Investigate if county-level data available

---

## Component Index 4: Demographic Growth & Renewal (4 measures)

### 4.1 Natural Increase Rate (Births minus Deaths)

- **Nebraska Source**: Census Bureau Population Estimates, Vital Statistics
- **Virginia API Source**: Census Population Estimates API
- **API**: `https://api.census.gov/data/[year]/pep/components`
- **Variables**: BIRTHS, DEATHS
- **Confidence**: ✅ **HIGH**
- **Notes**: Calculate (births - deaths) / population * 1000

### 4.2 Net Migration Rate

- **Nebraska Source**: Census Bureau Population Estimates
- **Virginia API Source**: Census Population Estimates API
- **API**: Same as 4.1 - components of population change
- **Variables**: NETMIG (Net migration)
- **Confidence**: ✅ **HIGH**
- **Notes**: Net migration / population * 1000

### 4.3 Percent of Population Age 25-54

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variables**: B01001 table (Sex by Age)
- **Confidence**: ✅ **HIGH**
- **Notes**: Sum age groups 25-54, divide by total population

### 4.4 Median Age (Inverse for Younger Population)

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variable**: B01002_001E (Median age)
- **Confidence**: ✅ **HIGH**
- **Notes**: Inverse scoring if younger is considered better

---

## Component Index 5: Education & Skill (5 measures)

### 5.1 High School Graduation Rate

- **Nebraska Source**: State Department of Education, NCES (4-year cohort graduation rate)
- **Virginia API Source**: Census ACS API (Educational Attainment - Proxy Measure)
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Variables**:
  - S1501_C02_014E (Percent high school graduate or higher, age 25+)
  - Or B15003 table for detailed educational attainment
- **Confidence**: ✅ **HIGH** (Updated from LOW)
- **Notes**:
  - Traditional graduation rates (NCES 4-year cohort) not available via API at county level
  - Using educational attainment as proxy: percent of adults 25+ with HS diploma or higher
  - This is actually superior for regional analysis:
    - Consistently available across all states via Census API
    - Reflects actual educational outcomes of adult population
    - County-level data for all counties
    - Updated annually with ACS 5-year estimates
  - Captures workforce educational quality better than current student graduation rates
- **Decision**: **USE EDUCATIONAL ATTAINMENT** - Percent of adults 25+ with high school diploma or higher

### 5.2 Percent of Adults with Some College

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variables**: B15003 table (Educational Attainment)
- **Confidence**: ✅ **HIGH**
- **Notes**: Sum "some college, no degree" + "Associate's degree"

### 5.3 Percent of Adults with Bachelor's Degree or Higher

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variable**: S1501_C02_015E (Percent bachelor's degree or higher)
- **Confidence**: ✅ **HIGH**
- **Notes**: Readily available from ACS

### 5.4 Student-Teacher Ratio (Inverse)

- **Nebraska Source**: NCES, State Department of Education
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: ❌ **LOW**
- **Notes**: Same issues as 5.1
- **Decision**: **INVESTIGATE** - May need to exclude

### 5.5 School District Spending Per Pupil

- **Nebraska Source**: NCES, State Department of Education
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: ❌ **LOW**
- **Notes**: Same issues as 5.1
- **Decision**: **INVESTIGATE** - May need to exclude

---

## Component Index 6: Infrastructure & Cost of Doing Business (6 measures)

### 6.1 Broadband Access (Percent with Access)

- **Nebraska Source**: FCC Broadband Data
- **Virginia API Source**: FCC Broadband Map API
- **API**: `https://broadbandmap.fcc.gov/api`
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - FCC National Broadband Map provides coverage data
  - API documentation unclear
  - May need to use bulk download
- **Decision**: **INVESTIGATE** FCC API access

### 6.2 Housing Affordability Index

- **Nebraska Source**: Calculated from ACS (median income vs median housing costs)
- **Virginia API Source**: Census ACS API
- **Variables**:
  - B19013_001E (Median household income)
  - B25077_001E (Median home value)
  - B25064_001E (Median gross rent)
- **Confidence**: ✅ **HIGH**
- **Notes**: Calculate affordability index (various formulas possible)

### 6.3 Percent of Housing Units Built in Last 10 Years

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variables**: B25034 table (Year Structure Built)
- **Confidence**: ✅ **HIGH**
- **Notes**: Sum recent construction categories

### 6.4 Property Crime Rate (Inverse)

- **Nebraska Source**: FBI Uniform Crime Reporting (UCR)
- **Virginia API Source**: FBI Crime Data Explorer API
- **API**: `https://api.usa.gov/crime/fbi/cde/` (check current API)
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - Not all jurisdictions report to FBI
  - Virginia State Police also maintains crime data
  - May have missing data for some localities
- **Decision**: **INVESTIGATE** - Use FBI API if available; may have gaps

### 6.5 Violent Crime Rate (Inverse)

- **Nebraska Source**: FBI UCR
- **Virginia API Source**: FBI Crime Data Explorer API
- **Confidence**: 🟡 **MEDIUM**
- **Notes**: Same as 6.4

### 6.6 Highway Accessibility Index

- **Nebraska Source**: Calculated based on distance to interstate highways
- **Virginia API Source**: ⚠️ **NO STANDARD API**
- **Confidence**: ❌ **LOW**
- **Notes**:
  - Would need GIS data for highway locations
  - Calculate distance from county centroid to nearest interstate
  - Could use OpenStreetMap or Census TIGER/Line files
  - No direct API
- **Decision**: **LIKELY EXCLUDE** - Would require significant GIS processing

---

## Component Index 7: Quality of Life (8 measures)

### 7.1 Life Expectancy at Birth

- **Nebraska Source**: National Vital Statistics, CDC
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: ❌ **LOW**
- **Notes**:
  - County-level life expectancy requires special calculation
  - Institute for Health Metrics and Evaluation (IHME) publishes estimates
  - Robert Wood Johnson Foundation County Health Rankings has this data
  - No standard public API
- **Decision**: **INVESTIGATE** - May need to use County Health Rankings bulk download

### 7.2 Infant Mortality Rate (Inverse)

- **Nebraska Source**: CDC WONDER, Vital Statistics
- **Virginia API Source**: CDC WONDER API (limited)
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - CDC WONDER has county data but small counties may be suppressed
  - May need to use state vital statistics offices
- **Decision**: **INVESTIGATE** CDC WONDER API capabilities

### 7.3 Percent Uninsured (Inverse)

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variable**: S2701_C05_001E (Percent uninsured)
- **Confidence**: ✅ **HIGH**
- **Notes**: Readily available from ACS

### 7.4 Primary Care Physicians Per Capita

- **Nebraska Source**: Area Health Resources Files (AHRF), CMS
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - CMS National Provider Index (NPI) has provider data
  - HRSA Area Health Resources Files (AHRF) compiles this
  - County Health Rankings includes this metric
  - No clear public API
- **Decision**: **INVESTIGATE** - May need County Health Rankings data

### 7.5 Mental Health Providers Per Capita

- **Nebraska Source**: AHRF, HRSA
- **Virginia API Source**: ⚠️ **PROBLEMATIC**
- **Confidence**: ❌ **LOW**
- **Notes**: Same issues as 7.4
- **Decision**: **INVESTIGATE** - Likely need bulk data source

### 7.6 Recreation Establishments Per Capita

- **Nebraska Source**: County Business Patterns
- **Virginia API Source**: Census CBP API
- **NAICS Code**: 71 (Arts, Entertainment, and Recreation)
- **Confidence**: ✅ **HIGH**
- **Notes**: Count establishments in NAICS 71, divide by population

### 7.7 Restaurants Per Capita

- **Nebraska Source**: County Business Patterns
- **Virginia API Source**: Census CBP API
- **NAICS Code**: 722 (Food Services and Drinking Places)
- **Confidence**: ✅ **HIGH**
- **Notes**: Count establishments in NAICS 722, divide by population

### 7.8 Arts and Entertainment Establishments Per Capita

- **Nebraska Source**: County Business Patterns
- **Virginia API Source**: Census CBP API
- **NAICS Codes**: 711 (Performing Arts) + 712 (Museums, Historical Sites)
- **Confidence**: ✅ **HIGH**
- **Notes**: Count establishments, divide by population

---

## Component Index 8: Social Capital (7 measures)

### 8.1 Voter Participation Rate

- **Nebraska Source**: State election data
- **Virginia API Source**: ⚠️ **NO STANDARD API**
- **Confidence**: ❌ **LOW**
- **Notes**:
  - Each state maintains own election data
  - Virginia Department of Elections publishes data
  - Peer states (MD, WV, NC, TN, KY) would need separate sources
  - No standardized API across states
- **Decision**: **LIKELY EXCLUDE** - No consistent API across states

### 8.2 Nonprofit Organizations Per Capita

- **Nebraska Source**: IRS Exempt Organizations Business Master File
- **Virginia API Source**: IRS API or bulk download
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - IRS publishes Exempt Organizations Business Master File (monthly)
  - Available as bulk download
  - May not have direct API
  - Can filter by county
- **Decision**: **INVESTIGATE** - Use bulk download if API not available

### 8.3 Religious Congregations Per Capita

- **Nebraska Source**: Association of Statisticians of American Religious Bodies (ASARB)
- **Virginia API Source**: ⚠️ **NO API**
- **Confidence**: ❌ **LOW**
- **Notes**:
  - U.S. Religion Census conducted periodically
  - No public API
  - Data may be outdated
- **Decision**: **LIKELY EXCLUDE**

### 8.4 Social Associations Per Capita

- **Nebraska Source**: County Business Patterns
- **Virginia API Source**: Census CBP API
- **NAICS Code**: 813 (Religious, Grantmaking, Civic, Professional Organizations)
- **Confidence**: ✅ **HIGH**
- **Notes**: Count establishments in NAICS 813, divide by population

### 8.5 Percent of Children in Single-Parent Households (Inverse)

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variables**: B09002 table (Own Children by Family Type)
- **Confidence**: ✅ **HIGH**
- **Notes**: Calculate percent in single-parent households; inverse scoring

### 8.6 Income Inequality (Gini Coefficient, Inverse)

- **Nebraska Source**: ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **Variable**: B19083_001E (Gini Index of Income Inequality)
- **Confidence**: ✅ **HIGH**
- **Notes**: Directly available; inverse scoring (lower inequality = better)

### 8.7 Social Capital Index (Composite)

- **Nebraska Source**: Various sources combined into composite
- **Virginia API Source**: ⚠️ **DEPENDS ON COMPONENTS**
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - This is typically a calculated composite of other social capital measures
  - May be subset of measures 8.1-8.6
  - Penn State Social Capital Index project provides methodology
- **Decision**: Calculate from available component measures

---

## Summary Statistics

### By Confidence Level

| Confidence | Count | Percentage |
|------------|-------|------------|
| ✅ HIGH | 29 | 61.7% |
| 🟡 MEDIUM | 10 | 21.3% |
| ❌ LOW | 8 | 17.0% |
| **TOTAL** | **47** | **100%** |

### By Component Index

| Component Index | HIGH | MEDIUM | LOW | Total |
|----------------|------|--------|-----|-------|
| 1. Growth | 5 | 0 | 1 | 6 |
| 2. Economic Opportunity & Diversity | 6 | 1 | 0 | 7 |
| 3. Other Economic Prosperity | 0 | 2 | 2 | 4 |
| 4. Demographic Growth & Renewal | 4 | 0 | 0 | 4 |
| 5. Education & Skill | 3 | 0 | 2 | 5 |
| 6. Infrastructure & Cost | 3 | 2 | 1 | 6 |
| 7. Quality of Life | 4 | 2 | 2 | 8 |
| 8. Social Capital | 4 | 1 | 2 | 7 |

### Measures to Likely Exclude (LOW Confidence)

1. Retail Sales Growth Rate (1.6)
2. Per Capita Retail Sales (3.1)
3. Business Survival Rate (3.4)
4. Student-Teacher Ratio (5.4) - *May be possible with effort*
5. School District Spending Per Pupil (5.5) - *May be possible with effort*
6. Highway Accessibility Index (6.6)
7. Life Expectancy at Birth (7.1) - *Available from County Health Rankings*
8. Mental Health Providers Per Capita (7.5) - *Available from County Health Rankings*
9. Voter Participation Rate (8.1)
10. Religious Congregations Per Capita (8.3)

**Note**: High School Graduation Rate (5.1) has been PROMOTED to HIGH confidence using Census ACS educational attainment data.

### Measures Requiring Further Investigation (MEDIUM Confidence)

1. Share of Workforce in High-Wage Industries (2.6)
2. Per Capita Bank Deposits (3.2)
3. New Business Formations Per Capita (3.3)
4. Broadband Access (6.1)
5. Property Crime Rate (6.4)
6. Violent Crime Rate (6.5)
7. Infant Mortality Rate (7.2)
8. Primary Care Physicians Per Capita (7.4)
9. Nonprofit Organizations Per Capita (8.2)
10. Social Capital Index composite (8.7)

---

## Required API Keys

Based on HIGH and MEDIUM confidence measures:

### Essential (HIGH Priority)
1. **CENSUS_API_KEY** - Census Bureau (ACS, CBP, Population Estimates)
2. **BEA_API_KEY** - Bureau of Economic Analysis (income, GDP data)
3. **BLS_API_KEY** - Bureau of Labor Statistics (employment, unemployment, wages)

### Important (MEDIUM Priority)
4. **FCC_API_KEY** - FCC Broadband data (if API available)
5. **FBI_API_KEY** - FBI Crime Data Explorer (if API available)

### Optional (for investigation)
6. **USDA_NASS_API_KEY** - USDA agricultural data (farm income)
7. IRS API credentials (nonprofit data)
8. State-specific API keys (crime, education data)

---

## Recommended Initial Implementation

### Phase 1: Core Measures (29 HIGH confidence measures)

Include only measures with HIGH confidence API availability. This ensures:
- Complete data coverage across all regions
- Minimal data gaps
- Reliable API access
- Consistent cross-state comparisons

**Coverage by Component**:
- Growth: 5/6 measures (83%)
- Economic Opportunity: 6/7 measures (86%)
- Other Prosperity: 0/4 measures (0%) ⚠️
- Demographics: 4/4 measures (100%)
- Education: 3/5 measures (60%)
- Infrastructure: 3/6 measures (50%)
- Quality of Life: 4/8 measures (50%)
- Social Capital: 4/7 measures (57%)

**Note**: "Other Economic Prosperity" index may need to be excluded or significantly revised due to lack of API-accessible measures.

### Phase 2: Add MEDIUM Confidence Measures (After Investigation)

Once API access verified for MEDIUM confidence measures, add them to enhance coverage.

### Phase 3: Explore Alternatives for LOW Confidence Measures

For excluded measures, explore:
- Alternative proxy measures
- Manual data collection (one-time)
- Partnerships with state agencies for data access
- Accepting incomplete coverage

---

## Next Steps

1. **Check environment variables** for existing API keys (CENSUS_API_KEY, BEA_API_KEY, BLS_API_KEY, etc.)
2. **Test API access** with sample requests for each HIGH confidence data source
3. **Investigate MEDIUM confidence measures** to determine if they can be promoted to HIGH
4. **Make final decision** on which measures to include in initial implementation
5. **Update PROJECT_PLAN.md** with finalized measure list
6. **Begin Phase 2** (Data Collection Infrastructure) with confirmed measures

---

*This document will be updated as API investigations progress and decisions are finalized.*
