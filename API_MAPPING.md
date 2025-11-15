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

## Component Index 4: Demographic Growth & Renewal (6 measures)

**Note**: This index measures demographic vitality, diversity, and generational renewal following Nebraska Thriving Index methodology exactly.

### 4.1 Long-Run Population Growth

- **Nebraska Source**: Census Bureau County Population Totals 2000, American Community Survey Table S0101, 2016-2020 period
- **Nebraska Metric**: Percent growth in population from 2000 to 2016-2020 period
- **Virginia API Source**: Census Decennial Census 2000 + Census ACS API
- **API Endpoints**:
  - Decennial 2000: `https://api.census.gov/data/2000/dec/sf1`
  - ACS 5-year: `https://api.census.gov/data/[year]/acs/acs5`
- **Variables**:
  - 2000 Decennial: P001001 (Total population)
  - ACS 2022: B01001_001E (Total population)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Calculate percent change from 2000 to most recent ACS 5-year period
  - Nebraska used 2000 to 2016-2020 (20-year period)
  - Virginia will use 2000 to 2018-2022 (22-year period)
  - Formula: `((Pop_2022 - Pop_2000) / Pop_2000) * 100`
  - Available at county level for all states
- **Data Years for Virginia**: 2000 Decennial Census to 2018-2022 ACS 5-year estimates

### 4.2 Dependency Ratio

- **Nebraska Source**: Census Bureau American Community Survey Table S0101, 2016-2020 period
- **Nebraska Metric**: Ratio of dependent population (age <15 and >64) to prime working age (15-64)
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5/subject`
- **Table**: S0101 (Age and Sex)
- **Variables**:
  - S0101_C01_001E (Total population)
  - Age breakdowns from S0101 or detailed B01001 table
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Dependent population: Under 15 + 65 and over
  - Working age population: 15 to 64
  - Formula: `(Pop_<15 + Pop_65+) / Pop_15_64`
  - Higher ratio = more dependents per working-age person
  - Inverse scoring: Lower dependency ratio = better (more working-age people)
  - Use B01001 table for precise age breakdowns
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 4.3 Median Age

- **Nebraska Source**: Census Bureau American Community Survey Table S0101, 2016-2020 period
- **Nebraska Metric**: Median age of the population
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Variable**: B01002_001E (Median age)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Directly available from ACS
  - Younger median age = faster natural population growth
  - Inverse scoring: Lower (younger) median age = better
  - Available at county level for all counties
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 4.4 Millennial and Gen Z Balance Change

- **Nebraska Source**: Census Bureau American Community Survey Tables S0101 and B01001, 2016-2020 and 2011-2015 periods
- **Nebraska Metric**: Five-year change in the share of population born in 1985 or after
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Tables**: B01001 (Sex by Age) or S0101 (Age and Sex)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Born 1985 or after = Millennials (1985-1996) + Gen Z (1997+)
  - Nebraska compared 2011-2015 to 2016-2020 ACS periods
  - For 2016-2020 data: Calculate % of population age 0-35 (born 1985-2020)
  - For 2011-2015 data: Calculate % of population age 0-30 (born 1985-2015)
  - Virginia will use 2013-2017 to 2018-2022 ACS periods
  - For 2018-2022 data: Born 1985+ means age 0-37 in 2022
  - For 2013-2017 data: Born 1985+ means age 0-32 in 2017
  - Formula: `(Pct_Millennial_GenZ_2022 - Pct_Millennial_GenZ_2017)`
  - Positive change = younger cohorts increasing concentration
- **Data Periods for Virginia**: 2013-2017 and 2018-2022 ACS 5-year estimates

### 4.5 Percent Hispanic

- **Nebraska Source**: Census Bureau American Community Survey Table B03003, 2016-2020 period
- **Nebraska Metric**: Percent of population that is Hispanic or Latino
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: B03003 (Hispanic or Latino Origin)
- **Variables**:
  - B03003_001E (Total population)
  - B03003_003E (Hispanic or Latino)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Directly available from ACS
  - Hispanic ethnicity is separate from race (can be any race)
  - Formula: `(Hispanic / Total) * 100`
  - Diversity measure: More diverse population brings broader perspectives
  - Available at county level for all counties
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 4.6 Percent Non-White

- **Nebraska Source**: Census Bureau American Community Survey Table B02001, 2016-2020 period
- **Nebraska Metric**: Percent of population that is non-white (all races except white alone)
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: B02001 (Race)
- **Variables**:
  - B02001_001E (Total population)
  - B02001_002E (White alone)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Calculate: `((Total - White_Alone) / Total) * 100`
  - Or sum all non-white categories
  - Diversity measure: More diverse population brings broader perspectives
  - Available at county level for all counties
  - Note: Hispanic ethnicity is counted separately in 4.5
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

---

## Component Index 5: Education & Skill (5 measures)

**Note**: This index measures educational attainment and workforce skill composition, following Nebraska Thriving Index methodology exactly.

### 5.1 High School Attainment Rate

- **Nebraska Source**: Census Bureau American Community Survey, Table S1501, 2016-2020 period
- **Nebraska Metric**: Share of population age 25+ with high school degree (or GED) as their HIGHEST level of education
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: B15003 (Detailed Tables - Educational Attainment for the Population 25 Years and Over)
- **Variables**:
  - B15003_001E (Total population 25 years and over)
  - B15003_017E (Regular high school diploma) + B15003_018E (GED or alternative credential)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - This is an EXCLUSIVE category: only those with HS/GED as highest level
  - Does NOT include those with any college education (Associate's, Bachelor's, etc.)
  - Formula: `(HS_diploma + GED) / Total_25plus * 100`
  - High school graduates are better able to adjust to a changing economy than non-graduates
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 5.2 Associate's Degree Attainment Rate

- **Nebraska Source**: Census Bureau American Community Survey, Table S1501, 2016-2020 period
- **Nebraska Metric**: Share of population age 25+ with Associate's degree as their HIGHEST level of education
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: B15003 (Detailed Tables - Educational Attainment)
- **Variables**:
  - B15003_001E (Total population 25 years and over)
  - B15003_021E (Associate's degree)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - This is an EXCLUSIVE category: only those with Associate's as highest level
  - Does NOT include "some college, no degree"
  - Does NOT include those with Bachelor's or higher degrees
  - Formula: `Associate_degree / Total_25plus * 100`
  - Associate's degree graduates meet critical workforce needs throughout the economy
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 5.3 College Attainment Rate (Bachelor's Degree)

- **Nebraska Source**: Census Bureau American Community Survey, Table S1501, 2016-2020 period
- **Nebraska Metric**: Share of population age 25+ with Bachelor's degree as their HIGHEST level of education
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: B15003 (Detailed Tables - Educational Attainment)
- **Variables**:
  - B15003_001E (Total population 25 years and over)
  - B15003_022E (Bachelor's degree)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - This is an EXCLUSIVE category: only those with Bachelor's as highest level
  - Does NOT include Master's, Professional, or Doctoral degrees
  - Formula: `Bachelor_degree / Total_25plus * 100`
  - College graduates have opportunities for careers in higher paying, knowledge-intensive occupations
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 5.4 Labor Force Participation Rate

- **Nebraska Source**: Census Bureau American Community Survey, Table DP03, 2016-2020 period
- **Nebraska Metric**: Share of the population age 16 and over who are in the labor force
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: B23025 (Employment Status for the Population 16 Years and Over)
- **Variables**:
  - B23025_001E (Total population 16 years and over)
  - B23025_002E (In labor force)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Labor force = employed + unemployed (actively seeking work)
  - Formula: `In_labor_force / Total_16plus * 100`
  - Workers gain job experience fastest in regions where a larger share participates in the workforce
  - Higher participation indicates economic vitality and opportunity
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

### 5.5 Percent of Knowledge Workers

- **Nebraska Source**: Census Bureau American Community Survey, Table DP03, 2016-2020 period
- **Nebraska Metric**: Share of labor force employed in information, financial services, professional/business services, or health care/education industries
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Table**: C24030 (Sex by Industry for the Civilian Employed Population 16 Years and Over)
- **Variables**:
  - C24030_001E (Total civilian employed population 16 years and over)
  - Information: C24030_029E (Male) + C24030_066E (Female)
  - Finance/insurance/real estate: C24030_030E (Male) + C24030_067E (Female)
  - Professional/scientific/management: C24030_031E (Male) + C24030_068E (Female)
  - Educational/health/social services: C24030_032E (Male) + C24030_069E (Female)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Knowledge industries are those requiring higher skill levels and offering career development
  - Formula: `(Information + Finance + Professional + Education_Health) / Total_employed * 100`
  - Workers in knowledge industries better maintain and grow their skills
  - Higher share indicates advanced economy with skill-building opportunities
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)

---

## Component Index 6: Infrastructure & Cost of Doing Business (6 measures)

**Note**: This index measures infrastructure quality and business environment conditions following Nebraska Thriving Index methodology exactly.

### 6.1 Broadband Internet Access

- **Nebraska Source**: FCC Broadband Availability, December 2020
- **Nebraska Metric**: Percent of population with one or more broadband providers with 100/10Mbps capacity
- **Virginia API Source**: FCC Broadband Map API
- **API Endpoint**: `https://broadbandmap.fcc.gov/api`
- **Technology**: ADSL, Cable, Fiber, Fixed Wireless, Satellite, Other at ≥100/10 Mbps
- **Confidence**: 🟡 **MEDIUM**
- **Notes**:
  - FCC API key pending (FCC_API_KEY environment variable not yet available)
  - Placeholder implementation strategy documented in FCC_PLACEHOLDER_DESIGN.md
  - Can use FCC National Broadband Map bulk data as alternative
  - Critical infrastructure measure for business operations and attraction
  - Available at county level
- **Data Year for Virginia**: Use most recent FCC Broadband Map data available (likely 2022-2023)

### 6.2 Presence of Interstate Highway

- **Nebraska Source**: Google Maps Interstate Map, 2018
- **Nebraska Metric**: Share of population in county that contains an interstate highway
- **Virginia API Source**: ⚠️ **NO STANDARD API**
- **Confidence**: ❌ **LOW** (API), ✅ **HIGH** (manual mapping)
- **Notes**:
  - No API for interstate highway presence
  - Can manually map which counties/regions contain interstate highways using:
    - U.S. Department of Transportation highway data
    - Census TIGER/Line shapefiles
    - Google Maps or OpenStreetMap
  - Binary variable: 1 if region contains interstate, 0 if not
  - For multi-county regions: Calculate weighted share of population in counties with interstates
  - One-time manual data collection is acceptable
  - Enhances access to regional economy and manufacturing facility locations
- **Implementation**: Manual mapping of interstate presence by county; one-time data collection
- **Data Source**: Census TIGER/Line roads shapefile + county population data

### 6.3 Count of 4-Year Colleges

- **Nebraska Source**: National Center for Education Statistics (NCES) College Navigator, 2020-2021
- **Nebraska Metric**: Average number of 4-year colleges in the counties where regional residents live
- **Virginia API Source**: NCES Integrated Postsecondary Education Data System (IPEDS) API
- **API Endpoint**: `https://nces.ed.gov/ipeds/datacenter/data/`
- **Confidence**: 🟡 **MEDIUM** (API unclear), ✅ **HIGH** (bulk data)
- **Notes**:
  - NCES College Navigator provides institution-level data with locations
  - IPEDS data available as bulk download or potentially via API
  - Filter for 4-year institutions (Level: 4-year)
  - Filter for degree-granting institutions
  - Geocode to county using institution addresses
  - For multi-county regions: Average count across counties (weighted by population)
  - Influences probability of attracting/retaining young people post-graduation
  - Can use IPEDS data download from https://nces.ed.gov/ipeds/datacenter/
- **Implementation**: Use IPEDS bulk download, filter for 4-year colleges, map to counties
- **Data Year for Virginia**: Use most recent IPEDS year available (likely 2022-2023)

### 6.4 Weekly Wage Rate

- **Nebraska Source**: Bureau of Labor Statistics, Quarterly Census of Employment and Wages (QCEW), Q2 2021
- **Nebraska Metric**: Average weekly wage rate in the region (all industries, total covered)
- **Virginia API Source**: BLS QCEW API
- **API Endpoint**: `https://api.bls.gov/publicAPI/v2/timeseries/data/`
- **Series ID Format**: `ENU` + state FIPS + county FIPS + `10` + `510` + `10`
- **Variables**:
  - Average weekly wage (all industries, private sector)
  - Alternative: All establishment ownership codes (not just private)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BLS QCEW provides average weekly wage directly
  - Reflects both hourly wage rate and hours worked per week
  - Use annual average or Q2 for consistency with Nebraska
  - Inverse scoring: Higher wages = worse for business cost competitiveness
  - But also reflects worker quality and purchasing power
  - Available at county level for all states
  - Already implemented in BLS API client (similar to QCEW employment data)
- **Data Year for Virginia**: Use most recent quarter available (likely Q2 2023 or Q2 2024)

### 6.5 Top Marginal Income Tax Rate

- **Nebraska Source**: Tax Foundation, 2022
- **Nebraska Metric**: Highest marginal income tax rate in the state where the region is located
- **Virginia API Source**: ⚠️ **NO API**
- **Confidence**: ✅ **HIGH** (static data)
- **Notes**:
  - Tax Foundation publishes state tax rates annually
  - No API, but data is publicly available and relatively static
  - State-level data: All regions in same state have same tax rate
  - One-time data collection with annual updates
  - State income tax rates for relevant states (2024):
    - Virginia: 5.75% (flat rate as of 2024)
    - Maryland: 5.75% (top marginal rate)
    - West Virginia: 6.5%
    - North Carolina: 4.75% (flat rate)
    - Tennessee: 0% (no income tax on wages)
    - Kentucky: 4.5% (flat rate as of 2024)
    - District of Columbia: 10.75%
  - Inverse scoring: Lower tax rate = better for business
  - Can hardcode by state; update annually from Tax Foundation
- **Implementation**: Manual data collection from Tax Foundation; hardcode by state
- **Data Source**: https://taxfoundation.org/state-income-tax-rates/
- **Data Year for Virginia**: Use most recent tax rates (2024 or 2025)

### 6.6 Count of Qualified Opportunity Zones

- **Nebraska Source**: U.S. Department of the Treasury, Community Development Financial Institutions Fund, 2018
- **Nebraska Metric**: Average number of qualified opportunity zones in the counties where regional residents live
- **Virginia API Source**: ⚠️ **NO API**
- **Confidence**: ✅ **HIGH** (static data)
- **Notes**:
  - Qualified Opportunity Zones (QOZs) designated in 2018 under Tax Cuts and Jobs Act
  - Static list: QOZs do not change frequently
  - Treasury publishes list of all designated QOZ census tracts
  - Can download and map to counties
  - Data available at: https://www.cdfifund.gov/opportunity-zones
  - For each county: Count number of QOZ census tracts
  - For multi-county regions: Average count across counties (weighted by population)
  - QOZs help attract capital investment to economically distressed areas
  - One-time data collection is acceptable
- **Implementation**: Download QOZ tract list from Treasury; map tracts to counties; count by county
- **Data Source**: https://www.cdfifund.gov/opportunity-zones (Excel/CSV download)
- **Data Year for Virginia**: 2018 designations (static)

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
| ✅ HIGH | 38 | 77.6% |
| 🟡 MEDIUM | 9 | 18.4% |
| ❌ LOW | 2 | 4.1% |
| **TOTAL** | **49** | **100%** |

### By Component Index

| Component Index | HIGH | MEDIUM | LOW | Total |
|----------------|------|--------|-----|-------|
| 1. Growth | 5 | 0 | 0 | 5 |
| 2. Economic Opportunity & Diversity | 6 | 1 | 0 | 7 |
| 3. Other Economic Prosperity | 4 | 1 | 0 | 5 |
| 4. Demographic Growth & Renewal | 6 | 0 | 0 | 6 |
| 5. Education & Skill | 5 | 0 | 0 | 5 |
| 6. Infrastructure & Cost | 4 | 2 | 0 | 6 |
| 7. Quality of Life | 4 | 2 | 2 | 8 |
| 8. Social Capital | 4 | 3 | 0 | 7 |

**Notes**:
- Component Index 3 (Other Economic Prosperity) updated to match Nebraska methodology exactly (5 measures, 4 HIGH confidence)
- Component Index 4 (Demographic Growth & Renewal) updated to match Nebraska methodology exactly (6 measures, 6 HIGH confidence)
- Component Index 5 (Education & Skill) updated to match Nebraska methodology exactly (5 measures, 5 HIGH confidence)
- Component Index 6 (Infrastructure & Cost) updated to match Nebraska methodology exactly (6 measures, 4 HIGH confidence)

### Measures to Likely Exclude (LOW Confidence)

1. Retail Sales Growth Rate (1.6) - No consistent API across states
2. Mental Health Providers Per Capita (7.5) - *May be available from County Health Rankings*

**Notes**:
- Component Index 5 now uses exclusive educational categories (HS as highest, Associate's as highest, Bachelor's as highest) plus labor force participation and knowledge workers, all via Census ACS API with HIGH confidence.
- Component Index 6 now matches Nebraska methodology exactly: Broadband, Interstate Presence, 4-Year Colleges, Weekly Wage, Tax Rate, QOZ Count
- Highway Accessibility Index removed (was not in Nebraska methodology)

### Measures Requiring Further Investigation (MEDIUM Confidence)

1. Share of Workforce in High-Wage Industries (2.6) - Need to define high-wage threshold
2. Life Span / Life Expectancy at Birth (3.3) - *Bulk download from County Health Rankings*
3. Broadband Internet Access (6.1) - FCC API key pending; can use bulk download
4. Presence of Interstate Highway (6.2) - Manual mapping using Census TIGER/Line
5. Infant Mortality Rate (7.2) - CDC WONDER API (may have suppression issues)
6. Primary Care Physicians Per Capita (7.4) - CMS NPPES or AHRF bulk data
7. Nonprofit Organizations Per Capita (8.2) - IRS bulk download
8. Religious Congregations Per Capita (8.3) - ASARB data (may be outdated)
9. Social Capital Index composite (8.7) - Calculate from available components

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

### Phase 1: Core Measures (38 HIGH confidence measures)

Include only measures with HIGH confidence for API availability, static data, or bulk downloads. This ensures:
- Complete data coverage across all regions
- Minimal data gaps
- Reliable API access
- Consistent cross-state comparisons

**Coverage by Component**:
- Growth: 5/5 measures (100%) ✅
- Economic Opportunity & Diversity: 6/7 measures (86%)
- Other Prosperity: 4/5 measures (80%) ✅ - **Updated to match Nebraska methodology**
- Demographics: 6/6 measures (100%) ✅ - **Updated to match Nebraska methodology**
- Education & Skill: 5/5 measures (100%) ✅ - **Updated to match Nebraska methodology**
- Infrastructure: 4/6 measures (67%) ✅ - **Updated to match Nebraska methodology**
- Quality of Life: 4/8 measures (50%)
- Social Capital: 4/7 measures (57%)

**Notes**:
- Component Index 3 (Other Economic Prosperity) has been corrected to use Nebraska methodology with 4/5 measures available via API (80% coverage). Only Life Span (3.3) requires bulk download from County Health Rankings.
- Component Index 4 (Demographic Growth & Renewal) has been corrected to use Nebraska methodology with 6/6 measures available via API (100% coverage).
- Component Index 5 (Education & Skill) has been corrected to use Nebraska methodology with 5/5 measures available via API (100% coverage). Uses exclusive educational categories plus labor force participation and knowledge workers.
- Component Index 6 (Infrastructure & Cost) has been corrected to use Nebraska methodology with 4/6 measures ready for implementation (67% coverage). Includes: 4-year colleges (bulk data), weekly wage (API), state tax rate (static), QOZ count (bulk data). Broadband and Interstate presence require additional data collection.

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
