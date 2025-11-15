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

## Component Index 1: Growth Index (5 measures)

**Note**: This index measures regional economic growth from 2017-2020, following Nebraska Thriving Index methodology exactly.

### 1.1 Growth in Total Employment

- **Nebraska Source**: BEA Regional Economic Accounts, Table CAINC5 (Personal Income by Major Component and Earnings by NAICS Industry)
- **Nebraska Years**: 2017 and 2020
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC5N (Personal Income by Major Component)
- **Line Code**: Line Code 10 - Total employment (wage and salary + proprietors)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BEA provides total employment including wage/salary workers and proprietors (self-employed)
  - Calculate percent change from 2017 to 2020 (3-year growth rate)
  - Formula: `((Employment_2020 - Employment_2017) / Employment_2017) * 100`
  - Available at county level for all states
- **Data Years for Virginia**: Use most recent 3-year period available (likely 2019-2022 or 2020-2023)

### 1.2 Private Employment

- **Nebraska Source**: BLS Quarterly Census of Employment and Wages (QCEW)
- **Nebraska Year**: 2020 (level measure, not growth)
- **Virginia API Source**: BLS QCEW API
- **API Endpoint**: `https://api.bls.gov/publicAPI/v2/timeseries/data/`
- **Series ID Format**: `ENU` + state FIPS + county FIPS + `05` + `510` + `10` (private sector, all industries)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - QCEW provides private sector wage and salary employment (excludes government)
  - This is a LEVEL measure, not a growth rate
  - Use annual average for most recent year available
  - Series ID components: ENU (QCEW program), ownership code 5 (private), aggregate level 10 (total)
- **Data Year for Virginia**: Use most recent year available (likely 2022 or 2023)

### 1.3 Growth in Private Wages Per Job

- **Nebraska Source**: BLS QCEW (Private Wages and Private Employment)
- **Nebraska Years**: 2017 and 2020
- **Virginia API Source**: BLS QCEW API
- **API Endpoint**: `https://api.bls.gov/publicAPI/v2/timeseries/data/`
- **Series ID for Employment**: `ENU` + ST + CNTY + `05` + `510` + `10`
- **Series ID for Wages**: `ENU` + ST + CNTY + `05` + `610` + `10` (total wages, quarterly, needs annualization)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Calculate wages per job: Total annual wages / Average employment
  - Do this for both start year and end year
  - Calculate percent change in wages per job
  - Formula: `((WagesPerJob_2020 - WagesPerJob_2017) / WagesPerJob_2017) * 100`
  - QCEW wages are reported quarterly; need to sum 4 quarters for annual total
- **Data Years for Virginia**: Use most recent 3-year period available

### 1.4 Growth in Households with Children

- **Nebraska Source**: Census ACS Table S1101 (Households and Families)
- **Nebraska Periods**: 2011-2015 ACS 5-year estimates and 2016-2020 ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Variables**:
  - S1101_C01_002E (Households with one or more people under 18 years)
  - S1101_C01_001E (Total households) - for verification
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Compare 2011-2015 ACS estimates to 2016-2020 ACS estimates
  - Calculate percent change in number of households with children
  - Formula: `((HH_with_children_2016_2020 - HH_with_children_2011_2015) / HH_with_children_2011_2015) * 100`
  - Available at county level for all counties
- **Data Periods for Virginia**: Use two most recent non-overlapping 5-year ACS periods
  - Earlier period: 2013-2017 or 2014-2018
  - Later period: 2018-2022 or 2019-2023

### 1.5 Growth in Dividends, Interest and Rent (DIR) Income

- **Nebraska Source**: BEA Regional Economic Accounts, Table CAINC5
- **Nebraska Years**: 2017 and 2020
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC5N (Personal Income by Major Component)
- **Line Code**: Line Code 40 - Dividends, interest, and rent
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BEA provides total DIR income by county
  - This captures investment income and rental income
  - Calculate percent change from 2017 to 2020
  - Formula: `((DIR_2020 - DIR_2017) / DIR_2017) * 100`
  - Available at county level for all states
- **Data Years for Virginia**: Use most recent 3-year period available (likely 2019-2022 or 2020-2023)

---

## Component Index 2: Economic Opportunity & Diversity (7 measures)

**Note**: This index measures entrepreneurial activity, business formation, and economic diversity, following Nebraska Thriving Index methodology exactly.

### 2.1 Entrepreneurial Activity (Business Births and Deaths Per Person)

- **Nebraska Source**: Census Bureau, Business Dynamics Statistics (BDS), 2019
- **Nebraska Metric**: Business births and deaths per person
- **Virginia API Source**: Census Bureau Business Dynamics Statistics
- **API**: May require bulk data download; API access unclear
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - BDS provides establishment births and deaths by county
  - Calculate: (Births + Deaths) / Population
  - County-level data may be suppressed for small counties
  - BDS has ~2 year lag
- **Alternative**: Use Census County Business Patterns year-over-year change as proxy
- **Data Year for Virginia**: Use most recent available (likely 2020 or 2021)

### 2.2 Non-Farm Proprietors Per 1,000 Persons

- **Nebraska Source**: BEA Table CAEMP25, Census Population, 2020
- **Nebraska Metric**: Number of proprietor businesses per 1,000 persons
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAEMP25 (Full-time and part-time employment by industry)
- **Line Code**: Line Code 200 (Nonfarm proprietors) or 300 (Farm proprietors) - sum for total
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BEA Table CAEMP25 provides proprietor employment counts
  - Line Code 200 = Nonfarm proprietors
  - Line Code 300 = Farm proprietors (if including farm)
  - Divide by population and multiply by 1,000
  - Available at county level for all states
- **Data Year for Virginia**: Use most recent available (likely 2022)

### 2.3 Employer Establishments Per 1,000 Residents

- **Nebraska Source**: BLS QCEW Private Annual Average Establishments, Census Population, 2020
- **Nebraska Metric**: Number of establishments with employees per 1,000 persons
- **Virginia API Source**: Census County Business Patterns API (easier than BLS QCEW)
- **API Endpoint**: `https://api.census.gov/data/[year]/cbp`
- **Variable**: ESTAB (Number of establishments)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Census CBP provides establishment counts (ESTAB variable)
  - Filter for NAICS 00 (total, all industries)
  - Excludes government, agricultural production, self-employed without employees
  - Divide by population and multiply by 1,000
  - Available at county level
- **Data Year for Virginia**: Use most recent available (likely 2021)

### 2.4 Share of Workers in Non-Employer Establishment

- **Nebraska Source**: Census County Business Patterns and Nonemployer Statistics Combined Report, 2018
- **Nebraska Metric**: Self-employed individuals / total employed
- **Virginia API Source**: Census Nonemployer Statistics (NES) API + CBP API
- **API Endpoints**:
  - Nonemployer: `https://api.census.gov/data/[year]/nonemp`
  - CBP: `https://api.census.gov/data/[year]/cbp`
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Nonemployer Statistics (NES) provides count of non-employer firms
  - CBP provides employment in employer establishments
  - Calculate: NONEMP / (NONEMP + EMP_CBP)
  - Available at county level for all counties
  - NES variable: NONEMP (Number of nonemployer establishments)
- **Data Year for Virginia**: Use most recent available (likely 2020 or 2021)

### 2.5 Industry Diversity

- **Nebraska Source**: Census County Business Patterns, 2019
- **Nebraska Metric**: Index matching US allocation of employment by industry
- **Virginia API Source**: Census CBP API
- **API Endpoint**: `https://api.census.gov/data/[year]/cbp`
- **Variables**: EMP (Employment) by 2-digit NAICS code
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Calculate dissimilarity index or correlation with US employment shares
  - For each county: `Diversity_Index = 1 - Σ|county_share_i - US_share_i| / 2`
  - Higher value = more similar to US = more diverse
  - Alternative: Herfindahl-Hirschman Index (HHI) where lower = more diverse
  - Nebraska likely uses dissimilarity index
- **Calculation**: Compare county industry shares to national shares
- **Data Year for Virginia**: Use most recent available (likely 2021)

### 2.6 Occupation Diversity

- **Nebraska Source**: Census ACS Table S2401, 2016-2020 period
- **Nebraska Metric**: Index matching US allocation of employment by occupation
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5/subject`
- **Table**: S2401 (Occupation by Sex and Median Earnings)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Table S2401 provides employment by occupation categories
  - Major occupation groups (6 categories): Management/Business, Service, Sales, Natural Resources, Production, Transportation
  - Calculate dissimilarity index with US occupation shares
  - Formula: `Diversity_Index = 1 - Σ|county_share_i - US_share_i| / 2`
  - Available at county level
- **Data Period for Virginia**: Use most recent 5-year period (2018-2022)

### 2.7 Share of Telecommuters

- **Nebraska Source**: Census ACS Table B08128, 2016-2020 period
- **Nebraska Metric**: Share working at home but not self-employed
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Variables**:
  - B08128_001E (Total workers)
  - B08128_002E (Workers who worked at home)
  - Need to subtract self-employed: use B08126 table
  - Alternative: Use pre-calculated variable if available
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Table B08128: Means of Transportation to Work by Class of Worker
  - Filter for worked at home AND not self-employed
  - Calculate: Telecommuters / Total workers
  - Available at county level
  - NOTE: Post-COVID data may show significant increase
- **Data Period for Virginia**: Use most recent 5-year period (2018-2022)

---

## Component Index 3: Other Economic Prosperity (5 measures)

**Note**: This index measures economic well-being beyond traditional growth metrics, following Nebraska Thriving Index methodology exactly.

### 3.1 Non-Farm Proprietor Personal Income

- **Nebraska Source**: BEA Regional Economic Accounts, Table CAINC5, 2020
- **Nebraska Metric**: Total amount of non-farm proprietor income (in thousands of dollars)
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC4 (Personal Income and Employment by Major Component)
- **Line Code**: Line Code 60 - Nonfarm proprietors' income
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BEA provides nonfarm proprietors' income at county level
  - This is the LEVEL of nonfarm proprietor income, not a percentage
  - Reflects self-employment income outside agriculture
  - Available for all states at county level
  - Already implemented in BEA API client
- **Data Year for Virginia**: Use most recent year available (likely 2022)

### 3.2 Personal Income Stability

- **Nebraska Source**: BEA Regional Economic Accounts, Table CAINC5, 2006-2020
- **Nebraska Metric**: Measure of stability in total personal income over 15-year period
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC1 (County and MSA personal income summary)
- **Line Code**: Line Code 1 - Total personal income
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Calculate coefficient of variation (CV) or standard deviation of income over 15 years
  - Lower CV = more stable income (better score)
  - Nebraska used 2006-2020 period; Virginia will use most recent 15-year period available
  - Formula: `Stability = StdDev(Income_t) / Mean(Income_t)` where t = years
  - Inverse scoring: Lower volatility = higher index score
  - BEA provides annual data from 2001-present
- **Data Years for Virginia**: Use 2008-2022 (15 years, most recent available)

### 3.3 Life Span (Life Expectancy at Birth)

- **Nebraska Source**: University of Washington Institute for Health Metrics and Evaluation (IHME), 1980-2014
- **Nebraska Metric**: Life expectancy at birth (in years)
- **Virginia API Source**: ⚠️ **NO PUBLIC API**
- **Alternative Source**: County Health Rankings & Roadmaps (annual report)
- **Confidence**: 🟡 **MEDIUM** (bulk download available)
- **Notes**:
  - IHME provides county-level life expectancy estimates but no public API
  - County Health Rankings publishes annual life expectancy data
  - Robert Wood Johnson Foundation provides bulk download
  - Data available at: https://www.countyhealthrankings.org/
  - May need manual download or web scraping
  - Alternative: CDC Life Expectancy data (limited API via CDC WONDER)
- **Decision**: **USE BULK DOWNLOAD** from County Health Rankings for 2022-2023 data
- **Data Year for Virginia**: Use most recent County Health Rankings year available

### 3.4 Poverty Rate

- **Nebraska Source**: Census Bureau American Community Survey, Table S1701, 2016-2020 5-year estimates
- **Nebraska Metric**: Percentage of population in poverty
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5/subject`
- **Table**: S1701 (Poverty Status in the Past 12 Months)
- **Variables**:
  - S1701_C03_001E (Percent below poverty level, all people)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Directly available from ACS 5-year estimates
  - Inverse scoring: Higher poverty rate = lower index score
  - Available at county level for all counties
  - Already used in Component Index 2 as well
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 3.5 Share of Income from Dividends, Interest and Rent (DIR)

- **Nebraska Source**: BEA Regional Economic Accounts, Table CAINC5, 2020
- **Nebraska Metric**: DIR income divided by total personal income (percentage)
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC5N (Personal Income by Major Component)
- **Line Code**: Line Code 40 - Dividends, interest, and rent
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Need both DIR income (Line Code 40) and total personal income (Line Code 1 from CAINC1)
  - Calculate: DIR / Total Personal Income * 100
  - Reflects income from wealth and investments
  - Supplements income from current work
  - Available for all states at county level
  - Already implemented in BEA API client
- **Data Year for Virginia**: Use most recent year available (likely 2022)

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
| ✅ HIGH | 33 | 70.2% |
| 🟡 MEDIUM | 9 | 19.1% |
| ❌ LOW | 5 | 10.6% |
| **TOTAL** | **47** | **100%** |

### By Component Index

| Component Index | HIGH | MEDIUM | LOW | Total |
|----------------|------|--------|-----|-------|
| 1. Growth | 5 | 0 | 0 | 5 |
| 2. Economic Opportunity & Diversity | 6 | 1 | 0 | 7 |
| 3. Other Economic Prosperity | 4 | 1 | 0 | 5 |
| 4. Demographic Growth & Renewal | 4 | 0 | 0 | 4 |
| 5. Education & Skill | 3 | 0 | 2 | 5 |
| 6. Infrastructure & Cost | 3 | 2 | 1 | 6 |
| 7. Quality of Life | 4 | 2 | 2 | 8 |
| 8. Social Capital | 4 | 1 | 2 | 7 |

**Note**: Component Index 3 (Other Economic Prosperity) updated to match Nebraska methodology exactly (5 measures, 4 HIGH confidence).

### Measures to Likely Exclude (LOW Confidence)

1. Student-Teacher Ratio (5.4) - *May be possible with effort*
2. School District Spending Per Pupil (5.5) - *May be possible with effort*
3. Highway Accessibility Index (6.6)
4. Mental Health Providers Per Capita (7.5) - *Available from County Health Rankings*
5. Voter Participation Rate (8.1)
6. Religious Congregations Per Capita (8.3)

**Note**: High School Graduation Rate (5.1) has been PROMOTED to HIGH confidence using Census ACS educational attainment data.

### Measures Requiring Further Investigation (MEDIUM Confidence)

1. Share of Workforce in High-Wage Industries (2.6)
2. Life Span / Life Expectancy at Birth (3.3) - *Bulk download from County Health Rankings*
3. Broadband Access (6.1)
4. Property Crime Rate (6.4)
5. Violent Crime Rate (6.5)
6. Infant Mortality Rate (7.2)
7. Primary Care Physicians Per Capita (7.4)
8. Nonprofit Organizations Per Capita (8.2)
9. Social Capital Index composite (8.7)

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
6. IRS API credentials (nonprofit data)
7. State-specific API keys (crime, education data)

**Note**: Farm income data comes from BEA (farm proprietors income, CAINC4 Line Code 50), not USDA NASS, per Nebraska methodology.

---

## Recommended Initial Implementation

### Phase 1: Core Measures (33 HIGH confidence measures)

Include only measures with HIGH confidence API availability. This ensures:
- Complete data coverage across all regions
- Minimal data gaps
- Reliable API access
- Consistent cross-state comparisons

**Coverage by Component**:
- Growth: 5/5 measures (100%) ✅
- Economic Opportunity & Diversity: 6/7 measures (86%)
- Other Prosperity: 4/5 measures (80%) ✅ - **Updated to match Nebraska methodology**
- Demographics: 4/4 measures (100%) ✅
- Education: 3/5 measures (60%)
- Infrastructure: 3/6 measures (50%)
- Quality of Life: 4/8 measures (50%)
- Social Capital: 4/7 measures (57%)

**Note**: Component Index 3 (Other Economic Prosperity) has been corrected to use Nebraska methodology with 4/5 measures available via API (80% coverage). Only Life Span (3.3) requires bulk download from County Health Rankings.

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
