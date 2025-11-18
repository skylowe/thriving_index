# Virginia Thriving Index - API Source Mapping

**Last Updated**: 2025-11-17
**Status**: Components 1-5 complete (100%); Component 6 near complete (83%, 5 of 6 measures); Component 7 complete (100%); Component 8 not started

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

**✅ COLLECTION STATUS: COMPLETE** (as of 2025-11-15)
- **Total Records**: 8,654 records
- **Counties Covered**: 802 unique counties across 10 states (VA, PA, MD, DE, WV, KY, TN, NC, SC, GA)
- **Summary File**: `data/processed/component1_collection_summary.json`
- **Collection Script**: `scripts/data_collection/collect_component1.py`

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
- **✅ DATA COLLECTED** (2025-11-15):
  - **Years**: 2020, 2021, 2022
  - **Records**: 2,322 (774 counties × 3 years)
  - **Raw Data**: `data/raw/bea/bea_employment_2020_2022.json`
  - **Processed Data**: `data/processed/bea_employment_processed.csv`
  - **Script**: `scripts/data_collection/collect_component1.py`
  - **API Client**: `scripts/api_clients/bea_client.py` (method: `get_employment_data()`)

### 1.2 Private Employment

- **Nebraska Source**: BLS Quarterly Census of Employment and Wages (QCEW)
- **Nebraska Year**: 2020 (level measure, not growth)
- **Virginia Data Source**: BLS QCEW Open Data Files (downloadable CSV)
- **Data URL**: `https://data.bls.gov/cew/data/files/[YEAR]/csv/[YEAR]_annual_singlefile.zip`
- **Filters**:
  - `own_code == 5` (Private ownership)
  - `industry_code == '10'` (Total, all industries)
  - Exclude area_fips ending in '000' (state-level) or '999' (special codes)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - QCEW provides private sector wage and salary employment (excludes government)
  - This is a LEVEL measure, not a growth rate
  - Use annual average employment (`annual_avg_emplvl` field)
  - **IMPORTANT**: Uses downloadable ZIP files (~500MB each), NOT the BLS Time Series API
  - Time Series API does not support QCEW county-level data
  - Files are cached locally to avoid re-downloading
- **Data Year for Virginia**: Use most recent year available (likely 2022 or 2023)
- **✅ DATA COLLECTED** (2025-11-15):
  - **Years**: 2020, 2021, 2022
  - **Records**: 2,406 (802 counties × 3 years)
  - **Raw Data**: `data/raw/qcew/qcew_private_employment_wages_2020_2022.csv`
  - **Processed Data**: `data/processed/qcew_private_employment_wages_2020_2022.csv`
  - **Cache Files**: `data/raw/qcew/cache/[YEAR]_annual_singlefile.csv` (one per year)
  - **Script**: `scripts/data_collection/collect_component1.py`
  - **API Client**: `scripts/api_clients/qcew_client.py` (method: `get_private_employment_wages()`)

### 1.3 Growth in Private Wages Per Job

- **Nebraska Source**: BLS QCEW (Private Wages and Private Employment)
- **Nebraska Years**: 2017 and 2020
- **Virginia Data Source**: BLS QCEW Open Data Files (same as 1.2)
- **Data URL**: `https://data.bls.gov/cew/data/files/[YEAR]/csv/[YEAR]_annual_singlefile.zip`
- **Fields Used**:
  - `annual_avg_emplvl` (Average annual employment)
  - `total_annual_wages` (Total annual wages)
  - `avg_annual_pay` (Average annual pay per worker)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Calculate wages per job: `total_annual_wages / annual_avg_emplvl`
  - Or use pre-calculated `avg_annual_pay` field
  - Calculate percent change in wages per job between start and end year
  - Formula: `((WagesPerJob_2020 - WagesPerJob_2017) / WagesPerJob_2017) * 100`
  - Annual data includes all wages already totaled (no quarterly summing needed)
  - **IMPORTANT**: Uses downloadable ZIP files, NOT the BLS Time Series API
- **Data Years for Virginia**: Use most recent 3-year period available
- **✅ DATA COLLECTED** (2025-11-15):
  - **Years**: 2020, 2021, 2022
  - **Records**: Same 2,406 records as measure 1.2 (wages and employment in same dataset)
  - **Raw Data**: `data/raw/qcew/qcew_private_employment_wages_2020_2022.csv`
  - **Processed Data**: `data/processed/qcew_private_employment_wages_2020_2022.csv`
  - **Cache Files**: `data/raw/qcew/cache/[YEAR]_annual_singlefile.csv` (one per year)
  - **Script**: `scripts/data_collection/collect_component1.py`
  - **API Client**: `scripts/api_clients/qcew_client.py` (method: `get_private_employment_wages()`)

### 1.4 Growth in Households with Children

- **Nebraska Source**: Census ACS Table S1101 (Households and Families)
- **Nebraska Periods**: 2011-2015 ACS 5-year estimates and 2016-2020 ACS 5-year estimates
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5/subject`
- **Table**: S1101 (Households and Families)
- **Variables**:
  - S1101_C01_002E (Households with one or more people under 18 years)
  - S1101_C01_001E (Total households) - for verification
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Compare 2011-2015 ACS estimates to 2016-2020 ACS estimates
  - Calculate percent change in number of households with children
  - Formula: `((HH_with_children_2016_2020 - HH_with_children_2011_2015) / HH_with_children_2011_2015) * 100`
  - Available at county level for all counties
  - Data collected by state (all counties in each state)
- **Data Periods for Virginia**: Use two most recent non-overlapping 5-year ACS periods
  - Earlier period: 2013-2017 or 2014-2018
  - Later period: 2018-2022 or 2019-2023
- **✅ DATA COLLECTED** (2025-11-15):
  - **Periods**: 2017 (2013-2017 5-year estimates), 2022 (2018-2022 5-year estimates)
  - **Records**: 1,604 (802 counties × 2 periods)
  - **Raw Data**: `data/raw/census/census_households_children_[STATE]_[YEAR].json` (20 files: 10 states × 2 years)
  - **Processed Data**: `data/processed/census_households_children_processed.csv`
  - **Script**: `scripts/data_collection/collect_component1.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_households_with_children()`)

### 1.5 Growth in Dividends, Interest and Rent (DIR) Income

- **Nebraska Source**: BEA Regional Economic Accounts, Table CAINC5
- **Nebraska Years**: 2017 and 2020
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC5N (Personal Income by Major Component)
- **Line Code**: Line Code 46 - Dividends, interest, and rent
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BEA provides total DIR income by county
  - This captures investment income and rental income
  - Calculate percent change from 2017 to 2020
  - Formula: `((DIR_2020 - DIR_2017) / DIR_2017) * 100`
  - Available at county level for all states
  - **IMPORTANT**: Use Line Code 46, not 40 (40 is not available in CAINC5N)
- **Data Years for Virginia**: Use most recent 3-year period available (likely 2019-2022 or 2020-2023)
- **✅ DATA COLLECTED** (2025-11-15):
  - **Years**: 2020, 2021, 2022
  - **Records**: 2,322 (774 counties × 3 years)
  - **Raw Data**: `data/raw/bea/bea_dir_income_2020_2022.json`
  - **Processed Data**: `data/processed/bea_dir_income_processed.csv`
  - **Script**: `scripts/data_collection/collect_component1.py`
  - **API Client**: `scripts/api_clients/bea_client.py` (method: `get_dir_income_data()`)

---

## Component Index 2: Economic Opportunity & Diversity (7 measures)

**Note**: This index measures entrepreneurial activity, business formation, and economic diversity, following Nebraska Thriving Index methodology exactly.

**✅ COLLECTION STATUS: COMPLETE** (as of 2025-11-16)
- **Total Measures**: 7 of 7 collected (100%)
- **Counties Covered**: 802 counties (BEA: 774 due to Virginia independent city aggregation)
- **Summary File**: `data/processed/component2_collection_summary.json`
- **Collection Script**: `scripts/data_collection/collect_component2.py`

### 2.1 Entrepreneurial Activity (Business Births and Deaths Per Person)

- **Nebraska Source**: Census Bureau, Business Dynamics Statistics (BDS), 2019
- **Nebraska Metric**: Business births and deaths per person
- **Virginia API Source**: Census Bureau Business Dynamics Statistics
- **API Endpoint**: `https://api.census.gov/data/timeseries/bds`
- **Variables**: ESTABS_ENTRY (births), ESTABS_EXIT (deaths), ESTAB (total establishments)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - BDS provides establishment births and deaths by county
  - Calculate: (Births + Deaths) / Population
  - County-level data may be suppressed for small counties
  - BDS has ~2 year lag
  - **IMPORTANT**: BDS API uses `YEAR` parameter (not `time`)
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2021
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/bds/bds_business_dynamics_[STATE]_2021.json` (10 files)
  - **Processed Data**: `data/processed/bds_business_dynamics_2021.csv`
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/bds_client.py` (method: `get_business_dynamics()`)

### 2.2 Non-Farm Proprietors Per 1,000 Persons

- **Nebraska Source**: BEA Table CAEMP25, Census Population, 2020
- **Nebraska Metric**: Number of proprietor businesses per 1,000 persons
- **Virginia API Source**: BEA Regional API
- **API Endpoint**: `https://apps.bea.gov/api/data/`
- **Dataset**: CAINC4 (Personal Income and Employment by Major Component)
- **Line Code**: Line Code 72 (Nonfarm proprietors' income)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - **IMPORTANT**: BEA Table CAEMP25 does not exist in the BEA Regional API
  - Using CAINC4 Line Code 72 (Nonfarm proprietors' INCOME) as proxy for proprietorship activity
  - This measures proprietor income rather than employment count, but serves as indicator of self-employment activity
  - Divide by population and multiply by 1,000
  - Available at county level for all states
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022
  - **Records**: 774 counties (Virginia independent cities aggregated by BEA)
  - **Raw Data**: `data/raw/bea/bea_proprietors_2022.json`
  - **Processed Data**: `data/processed/bea_proprietors_2022.csv`
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/bea_client.py` (method: `get_cainc4_data()`)

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2021
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/cbp/cbp_establishments_[STATE]_2021.json` (10 files)
  - **Processed Data**: `data/processed/cbp_establishments_2021.csv`
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/cbp_client.py` (method: `get_establishments()`)

### 2.4 Share of Workers in Non-Employer Establishment

- **Nebraska Source**: Census County Business Patterns and Nonemployer Statistics Combined Report, 2018
- **Nebraska Metric**: Self-employed individuals / total employed
- **Virginia API Source**: Census Nonemployer Statistics (NES) API + CBP API
- **API Endpoints**:
  - Nonemployer: `https://api.census.gov/data/[year]/nonemp`
  - CBP: `https://api.census.gov/data/[year]/cbp`
- **Variables**: NESTAB (Number of establishments), NRCPTOT (Total receipts)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Nonemployer Statistics (NES) provides count of non-employer firms
  - CBP provides employment in employer establishments
  - Calculate: NONEMP / (NONEMP + EMP_CBP)
  - Available at county level for all counties
  - **IMPORTANT**: Variable names changed in 2021+ API - use NESTAB (not NONEMP) and NRCPTOT (not RCPTOT)
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2021
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/nonemp/nonemp_firms_[STATE]_2021.json` (10 files)
  - **Processed Data**: `data/processed/nonemp_firms_2021.csv`
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/nonemp_client.py` (method: `get_nonemployer_firms()`)

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
  - Not all industries exist in all counties (legitimate variation)
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2021
  - **NAICS Sectors**: 19 major sectors (11, 21, 22, 23, 31-33, 42, 44-45, 48-49, 51, 52, 53, 54, 55, 56, 61, 62, 71, 72, 81)
  - **Records per sector**: 346 to 801 counties (variation is normal - not all industries exist everywhere)
  - **Raw Data**: `data/raw/cbp/cbp_industry_employment_[STATE]_2021.json` (10 files)
  - **Processed Data**: `data/processed/cbp_industry_naics[XX]_2021.csv` (19 files, one per sector)
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/cbp_client.py` (method: `get_industry_employment()`)

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Period**: 2022 (2018-2022 5-year estimates)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_occupation_[STATE]_2022.json` (10 files)
  - **Processed Data**: `data/processed/census_occupation_2022.csv`
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_occupation_data()`)

### 2.7 Share of Telecommuters

- **Nebraska Source**: Census ACS Table B08128, 2016-2020 period
- **Nebraska Metric**: Share working at home but not self-employed
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5`
- **Variables**:
  - B08128_001E (Total workers)
  - B08128_002E (Total worked at home)
  - B08128_003E (Worked at home: Private wage/salary)
  - B08128_009E (Worked at home: Self-employed not incorporated)
  - B08128_013E (Worked at home: Self-employed incorporated)
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Table B08128: Means of Transportation to Work by Class of Worker
  - Filter for worked at home AND not self-employed
  - Calculate: Telecommuters / Total workers
  - Available at county level
  - NOTE: Post-COVID data may show significant increase
- **✅ DATA COLLECTED** (2025-11-16):
  - **Period**: 2022 (2018-2022 5-year estimates)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_telecommuter_[STATE]_2022.json` (10 files)
  - **Processed Data**: `data/processed/census_telecommuter_2022.csv`
  - **Script**: `scripts/data_collection/collect_component2.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_telecommuter_data()`)

---

## Component Index 3: Other Economic Prosperity (5 measures)

**✅ COLLECTION STATUS: 100% COMPLETE** (as of 2025-11-17)
- **Total Records**: 3,936 records across all 5 measures
- **Counties Covered**: 774-812 counties across 10 states (VA, PA, MD, DE, WV, KY, TN, NC, SC, GA)
- **Summary File**: `data/processed/component3_collection_summary.json`
- **Collection Script**: `scripts/data_collection/collect_component3.py` (all 5 measures in single script)
- **All measures collected including life expectancy via integrated Zenodo download**

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022
  - **Records**: 774 counties (Virginia independent cities aggregated by BEA)
  - **Raw Data**: `data/raw/bea/bea_proprietor_income_2022.json`
  - **Processed Data**: `data/processed/bea_proprietor_income_2022.csv`
  - **Script**: `scripts/data_collection/collect_component3.py`
  - **API Client**: `scripts/api_clients/bea_client.py` (method: `get_proprietors_data()`)
  - **Note**: Uses CAINC4 Line 72 (actual implementation differs from Line 60 noted above)

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Years**: 2008-2022 (15 years)
  - **Records**: 774 counties with complete 15-year data
  - **Raw Data**: `data/raw/bea/bea_personal_income_2008_2022.json`
  - **Processed Data**: `data/processed/bea_income_stability_2008_2022.csv`
  - **Script**: `scripts/data_collection/collect_component3.py`
  - **API Client**: `scripts/api_clients/bea_client.py` (method: `get_total_personal_income()`)
  - **Statistics**: Average CV = 0.1734, Range: 0.0566 to 0.3685

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2025 release (data from 2021-2023)
  - **Records**: 812 counties (includes state summaries and independent cities)
  - **Source**: County Health Rankings & Roadmaps via Zenodo (DOI: 10.5281/zenodo.17584421)
  - **Download Method**: Zenodo API programmatic download of 2025.zip file
  - **Raw Data**: `data/raw/chr/chr_life_expectancy_2025_metadata.json`
  - **Processed Data**: `data/processed/chr_life_expectancy_2025.csv`
  - **Script**: `scripts/data_collection/collect_component3.py` (integrated with other Component 3 measures)
  - **Statistics**: Mean = 73.75 years, Range: 64.32-88.91 years, Missing: 1 (99.9% complete)
  - **File Format**: CSV extracted from 50.1MB ZIP archive containing Excel and CSV files

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (5-year estimates: 2018-2022)
  - **Records**: 802 counties across all 10 states
  - **Raw Data**: `data/raw/census/census_poverty_[STATE]_2022.json` (10 files)
  - **Processed Data**: `data/processed/census_poverty_2022.csv`
  - **Script**: `scripts/data_collection/collect_component3.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_poverty_rate()`)
  - **Statistics**: Average poverty rate = 15.92%, No null values

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022
  - **Records**: 774 counties (Virginia independent cities aggregated by BEA)
  - **Raw Data**: `data/raw/bea/bea_dir_income_share_2022.json`, `data/raw/bea/bea_total_income_share_2022.json`
  - **Processed Data**: `data/processed/bea_dir_income_share_2022.csv`
  - **Script**: `scripts/data_collection/collect_component3.py`
  - **API Client**: `scripts/api_clients/bea_client.py` (methods: `get_dir_income_data()`, `get_total_personal_income()`)
  - **Statistics**: Average DIR share = 14.93%, Range: 6.09% to 45.52%

---

## Component Index 4: Demographic Growth & Renewal (6 measures)

**✅ COLLECTION STATUS: COMPLETE** (as of 2025-11-16)
- **Total Records**: 5,616 records across all 6 measures
- **Counties Covered**: 802-804 counties across 10 states (VA, PA, MD, DE, WV, KY, TN, NC, SC, GA)
- **Summary File**: `data/processed/component4_collection_summary.json`
- **Collection Script**: `scripts/data_collection/collect_component4.py`

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Years**: 2000 (Decennial Census), 2022 (2018-2022 ACS 5-year)
  - **Records 2000**: 804 counties
  - **Records 2022**: 802 counties
  - **Raw Data**: `data/raw/census/census_population_2000_[STATE].json` (10 files), `data/raw/census/census_population_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_population_growth_2000_2022.csv`
  - **Script**: `scripts/data_collection/collect_component4.py`
  - **API Client**: `scripts/api_clients/census_client.py` (methods: `get_decennial_population_2000()`, `get_population_total()`)
  - **Statistics**: Average population growth = 11.64%

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (2018-2022 ACS 5-year)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_age_distribution_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_dependency_ratio_2022.csv`
  - **Script**: `scripts/data_collection/collect_component4.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_age_distribution()`)
  - **Statistics**: Average dependency ratio = 0.581

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (2018-2022 ACS 5-year)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_median_age_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_median_age_2022.csv`
  - **Script**: `scripts/data_collection/collect_component4.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_median_age()`)
  - **Statistics**: Average median age = 42.0 years

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Years**: 2017 (2013-2017 ACS 5-year), 2022 (2018-2022 ACS 5-year)
  - **Records 2017**: 802 counties
  - **Records 2022**: 802 counties
  - **Raw Data**: `data/raw/census/census_age_distribution_2017_[STATE].json` (10 files), `data/raw/census/census_age_distribution_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_millennial_genz_change_2017_2022.csv`
  - **Script**: `scripts/data_collection/collect_component4.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_age_distribution()`)
  - **Statistics**: Average change = 5.27 percentage points

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (2018-2022 ACS 5-year)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_hispanic_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_hispanic_2022.csv`
  - **Script**: `scripts/data_collection/collect_component4.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_hispanic_data()`)
  - **Statistics**: Average % Hispanic = 5.35%

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (2018-2022 ACS 5-year)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_race_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_race_2022.csv`
  - **Script**: `scripts/data_collection/collect_component4.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_race_data()`)
  - **Statistics**: Average % Non-White = 23.51%

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (2018-2022 ACS 5-year)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_education_detailed_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_education_attainment_2022.csv`
  - **Script**: `scripts/data_collection/collect_component5.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_education_detailed()`)
  - **Statistics**: Average % HS only = 35.89%

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
- **✅ DATA COLLECTED** (2025-11-16):
  - **Year**: 2022 (2018-2022 ACS 5-year)
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/census/census_knowledge_workers_2022_[STATE].json` (10 files)
  - **Processed Data**: `data/processed/census_knowledge_workers_2022.csv`
  - **Script**: `scripts/data_collection/collect_component5.py`
  - **API Client**: `scripts/api_clients/census_client.py` (method: `get_knowledge_workers()`)
  - **Statistics**: Average % knowledge workers = 33.33%
  - **Implementation Note**: Uses S2401 occupation table (management/professional/science/arts) as proxy for knowledge workers instead of industry table C24030 due to API variable compatibility issues

---

## Component Index 5: Education & Skill (5 measures) - COLLECTION STATUS

**✅ COLLECTION STATUS: COMPLETE** (as of 2025-11-16)
- **Total Records**: 2,406 records across all 5 measures (802 counties per measure)
- **Counties Covered**: 802 counties across 10 states (VA, PA, MD, DE, WV, KY, TN, NC, SC, GA)
- **Summary File**: `data/processed/component5_collection_summary.json`
- **Collection Script**: `scripts/data_collection/collect_component5.py`

**Key Statistics**:
- Average High School Only attainment: 35.89%
- Average Associate's Degree Only attainment: 8.67%
- Average Bachelor's Degree Only attainment: 13.79%
- Average Labor Force Participation Rate: 56.03%
- Average Knowledge Workers: 33.33%

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

### 6.2 Presence of Interstate Highway ✅ DATA COLLECTED

- **Nebraska Source**: Google Maps Interstate Map, 2018
- **Nebraska Metric**: Share of population in county that contains an interstate highway
- **Virginia API Source**: USGS National Map Transportation API + Census TIGER county boundaries
- **API Endpoint**: `https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/29/query`
- **API Client**: `scripts/api_clients/usgs_client.py`
- **Confidence**: ✅ **HIGH** (API implemented successfully with spatial analysis)
- **Collection Date**: 2025-11-17
- **Notes**:
  - USGS National Map provides comprehensive transportation data via ArcGIS REST API
  - Downloaded all 194,210 interstate highway segments nationwide (layer 29: Controlled-access Highways)
  - Used Census TIGER 2024 county boundaries for spatial intersection
  - Binary variable: 1 if county contains interstate, 0 if not
  - For multi-county regions: Calculate weighted share of population in counties with interstates
  - Spatial analysis performed using geopandas and shapely libraries
  - Highway and boundary data cached as pickled GeoDataFrames for faster subsequent runs
  - Enhances access to regional economy and manufacturing facility locations
- **Implementation**: USGS API with pagination (batches of 2,000 segments) + Census TIGER boundaries + spatial intersection
- **Data Year for Virginia**: 2024 (USGS transportation data + Census TIGER 2024 boundaries)
- **Data Files**:
  - **Raw**: `data/raw/usgs/county_interstate_presence.csv` (county-level, 802 counties)
  - **Processed**: `data/processed/usgs_county_interstate_presence.csv` (county-level, 802 counties)
  - **Cache**: `data/raw/usgs/cache/interstate_highways_nationwide.pkl` (194,210 segments)
  - **Cache**: `data/raw/usgs/cache/county_boundaries_2024.pkl` (Census TIGER boundaries)
- **Collection Results**:
  - Total counties analyzed: 802 counties
  - Counties with interstates: 391 counties (48.8%)
  - Counties without interstates: 411 counties (51.2%)
  - Binary indicator (has_interstate): 1 or 0 for each county
  - Runtime: ~10-15 minutes for full download and spatial processing
- **Technical Notes**:
  - API query filters for interstate highways: `interstate IS NOT NULL AND interstate <> ''`
  - Pagination handled automatically (2,000 records per batch with progress tracking)
  - Spatial intersection uses geopandas `sjoin` (spatial join) operation
  - Caching reduces subsequent runtime to <1 minute

### 6.3 Count of 4-Year Colleges ✅ DATA COLLECTED

- **Nebraska Source**: National Center for Education Statistics (NCES) College Navigator, 2020-2021
- **Nebraska Metric**: Average number of 4-year colleges in the counties where regional residents live
- **Virginia API Source**: Urban Institute Education Data Portal (IPEDS directory)
- **API Endpoint**: `https://educationdata.urban.org/api/v1/college-university/ipeds/directory/2022/`
- **API Client**: `scripts/api_clients/urban_institute_client.py`
- **Confidence**: ✅ **HIGH** (API implemented successfully)
- **Collection Date**: 2025-11-17
- **Notes**:
  - Urban Institute provides clean API access to IPEDS institutional characteristics data
  - Filter for `inst_level=4` (4-year institutions)
  - Filter for `degree_granting=1` (degree-granting institutions only)
  - Data includes county FIPS codes for direct county-level aggregation
  - API query uses state-by-state approach for reliability (fips + inst_level filters)
  - Local filtering applied for degree_granting status (avoids API 503 errors)
  - For multi-county regions: Average count across counties (weighted by population)
  - Influences probability of attracting/retaining young people post-graduation
- **Implementation**: Urban Institute Education Data Portal API with state-by-state queries and local filtering
- **Data Year for Virginia**: 2022 (most recent available via API)
- **Data Files**:
  - **Raw**: `data/raw/urban_institute/ipeds_four_year_colleges_2022.csv` (institution-level, 902 colleges)
  - **Processed**: `data/processed/ipeds_four_year_colleges_by_county_2022.csv` (county-level counts, 345 counties)
- **Collection Results**:
  - Total 4-year degree-granting colleges: 902 institutions
  - Counties with colleges: 345 of 802 counties (43%)
  - Average colleges per county (for counties with colleges): 2.61
  - Range: 1-23 colleges per county
  - Top states: Pennsylvania (222), North Carolina (139), Georgia (112)
- **Technical Notes**:
  - API requires `state_fips_list` parameter for reliable access
  - Combining all three filters (fips + inst_level + degree_granting) causes 503 errors
  - Workaround: Query with fips + inst_level, then filter locally for degree_granting==1
  - Pagination handled automatically (up to 10,000 records per page)

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
- **✅ DATA COLLECTED** (2025-11-17):
  - **Year**: 2022
  - **Records**: 802 counties
  - **Raw Data**: `data/raw/qcew/qcew_weekly_wage_2022.csv`
  - **Processed Data**: `data/processed/qcew_weekly_wage_2022.csv`
  - **Script**: `scripts/data_collection/collect_component6.py`
  - **API Client**: `scripts/api_clients/qcew_client.py` (reused from Component 1)
  - **Statistics**: Average weekly wage: $931.61, Range: $0-$2,241

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
  - Inverse scoring: Lower tax rate = better for business
  - Can hardcode by state; update annually from Tax Foundation
- **Implementation**: Manual data collection from Tax Foundation; hardcode by state
- **Data Source**: https://taxfoundation.org/state-income-tax-rates/
- **Data Year for Virginia**: Use most recent tax rates (2024 or 2025)
- **✅ DATA COLLECTED** (2025-11-17):
  - **Tax Year**: 2024
  - **Records**: 10 states
  - **Raw Data**: `data/raw/tax_foundation/state_income_tax_rates_2024.json`
  - **Processed Data**: `data/processed/state_income_tax_rates_2024.csv`
  - **Script**: `scripts/data_collection/collect_component6.py`
  - **Statistics**: Average rate: 4.66%, Range: 0% (TN) to 6.6% (DE)
  - **Updated Rates**: Kentucky 4.0% (reduced from 4.5%), NC 4.5% (reduced from 4.75%), GA 5.39% (will reduce to 5.19% in 2025)

### 6.6 Count of Qualified Opportunity Zones

- **Nebraska Source**: U.S. Department of the Treasury, Community Development Financial Institutions Fund, 2018
- **Nebraska Metric**: Average number of qualified opportunity zones in the counties where regional residents live
- **Virginia API Source**: HUD Opportunity Zones ArcGIS REST API
- **API Endpoint**: `https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/Opportunity_Zones/FeatureServer/13/query`
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - Qualified Opportunity Zones (QOZs) designated in 2018 under Tax Cuts and Jobs Act
  - Static list: QOZs do not change frequently
  - HUD provides ArcGIS REST API with all 8,765 OZ tracts nationwide
  - For each county: Count number of QOZ census tracts
  - For multi-county regions: Average count across counties (weighted by population)
  - QOZs help attract capital investment to economically distressed areas
  - API supports pagination for large datasets
- **Implementation**: Use HUD ArcGIS REST API with pagination; filter to our 10 states; aggregate to county level
- **Data Source**: HUD ArcGIS REST API (https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/Opportunity_Zones/)
- **Data Year for Virginia**: 2018 designations (static)
- **✅ DATA COLLECTED** (2025-11-17):
  - **Designation Year**: 2018
  - **Records**: 580 counties with OZs (72% of all 802 counties)
  - **Total OZ Tracts**: 1,709 tracts across our 10 states (8,765 nationwide)
  - **Raw Data**: `data/raw/hud/opportunity_zones_tracts.csv` (tract-level data)
  - **Processed Data**: `data/processed/hud_opportunity_zones_by_county.csv` (county-level counts)
  - **Script**: `scripts/data_collection/collect_component6.py`
  - **API Client**: `scripts/api_clients/hud_client.py` (new HUD API client created)
  - **API Method**: HUD ArcGIS REST API with pagination (1,000 records per batch)
  - **Statistics**: Average 2.95 OZ tracts per county, Range: 1-82 tracts
  - **Top States**: Pennsylvania (300), Georgia (260), North Carolina (252), Virginia (213)

---

## Component Index 7: Quality of Life (8 measures)

**Note**: This index measures quality of life factors including commute times, housing quality, wages, safety, climate, healthcare access, and recreation, following Nebraska Thriving Index methodology exactly.

### 7.1 Commute Time

- **Nebraska Source**: Census Bureau American Community Survey, Table S0801, 2016-2020 period
- **Nebraska Metric**: Average commuting time to work (in minutes)
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5/subject`
- **Table**: S0801 (Commuting Characteristics by Sex)
- **Variables**:
  - S0801_C01_046E (Mean travel time to work in minutes)
- **Confidence**: ✅ **HIGH**
- **Collection Status**: ✅ **COLLECTED** (2025-11-17)
- **Notes**:
  - Represents the cost of living in terms of time
  - Provides insight into travel times to important destinations within a region
  - Inverse scoring: Shorter commute time = better quality of life
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)
- **Data Files**:
  - Raw: `data/raw/census/census_commute_time_2022_[STATE].json` (10 states)
  - Processed: `data/processed/census_commute_time_2022.csv` (802 counties)

### 7.2 Percent of Housing Built Pre-1960

- **Nebraska Source**: Census Bureau American Community Survey, Table DP04, 2016-2020 period
- **Nebraska Metric**: Share of housing units built before 1960
- **Virginia API Source**: Census ACS API
- **API Endpoint**: `https://api.census.gov/data/[year]/acs/acs5/profile`
- **Table**: DP04 (Selected Housing Characteristics)
- **Variables**:
  - DP04_0035E (Built 1939 or earlier)
  - DP04_0036E (Built 1940 to 1949)
  - DP04_0037E (Built 1950 to 1959)
  - DP04_0033E (Total housing units)
- **Confidence**: ✅ **HIGH**
- **Collection Status**: ✅ **COLLECTED** (2025-11-17)
- **Notes**:
  - Older housing units may lack contemporary design and are subject to depreciation
  - Calculate: (Built_1939_or_earlier + Built_1940_1949 + Built_1950_1959) / Total_units * 100
  - Inverse scoring: Lower percentage of old housing = better
  - Available at county level for all states
- **Data Period for Virginia**: Use most recent 5-year ACS period (2018-2022)
- **Data Files**:
  - Raw: `data/raw/census/census_housing_age_2022_[STATE].json` (10 states)
  - Processed: `data/processed/census_housing_pre1960_2022.csv` (802 counties)

### 7.3 Relative Weekly Wage

- **Nebraska Source**: Bureau of Labor Statistics Quarterly Census of Employment and Wages, Average Weekly Wage (all industries, total covered, all establishment sizes), Quarter 2 2021
- **Nebraska Metric**: The ratio of regional quarterly wages per job to statewide quarterly wages per job
- **Virginia API Source**: BLS QCEW Downloadable Files
- **API Endpoint**: `https://data.bls.gov/cew/data/files/[year]/csv/[year]_annual_singlefile.zip`
- **Series ID Format**: `ENU` + state FIPS + county FIPS + ownership + industry + data type
- **Confidence**: ✅ **HIGH**
- **Collection Status**: ✅ **COLLECTED** (2025-11-17)
- **Notes**:
  - Calculate regional average weekly wage (all industries, total covered)
  - Calculate statewide average weekly wage
  - Compute ratio: Regional_Wage / State_Wage
  - Reflects the relative earnings opportunities in the region
  - Higher ratio = better earnings relative to state
  - Uses BLS QCEW downloadable files (not Time Series API)
  - Already implemented in QCEW client with caching
- **Data Year for Virginia**: Use most recent year available (2022)
- **Data Files**:
  - Processed: `data/processed/qcew_relative_weekly_wage_2022.csv` (802 counties)

### 7.4 Violent Crime Rate

- **Nebraska Source**: FBI Uniform Crime Reporting, Crime in the United States, 2018
- **Nebraska Metric**: Annual violent crimes per 100,000 population
- **Virginia API Source**: FBI Crime Data Explorer API
- **API Endpoint**: `https://api.usa.gov/crime/fbi/cde/`
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - FBI UCR provides violent crime counts by agency
  - Violent crimes include: murder, rape, robbery, aggravated assault
  - Aggregate agency-level data to county level
  - Calculate: (Violent_crimes / Population) * 100,000
  - Inverse scoring: Lower crime rate = better quality of life
  - Personal safety is a critical factor in enjoying life
  - FBI_UCR_KEY available in environment
- **Data Year for Virginia**: Use most recent year available (likely 2021 or 2022)
- **✅ DATA COLLECTED** (2025-11-17):
  - **API Endpoint**: `/summarized/agency/{ORI9}/{offense}` where offense = 'V' for violent
  - **Year**: 2023 (01-2023 to 12-2023)
  - **Agency Mapping**: Uses `ori_crosswalk.tsv` to map 5,749 agencies (ORI9 codes) to counties
  - **API Investigation**: No batch endpoints available; requires 1 call per agency per offense type
  - **Total API Calls Made**: 10,624 (2 per agency × 5,312 non-cached agencies)
  - **No API Limit Encountered**: Full collection completed in single run (~2.5 hours)
  - **Caching**: Implemented in `fbi_cde_client.py` - 89 MB cache prevents redundant API calls
  - **Full Collection**: 5,749 agencies processed (100% success rate, 0 errors)
  - **Counties Covered**: 804 counties
  - **Total Violent Crimes**: 248,963
  - **Raw Data**: `data/raw/fbi_cde/{ORI}_{offense}_{from}_{to}.json` (cached)
  - **Processed Data**: `data/processed/fbi_crime_counties_2023.csv` (804 counties)
  - **Agency Data**: `data/processed/fbi_crime_agencies_2023.json` (5,749 agencies, 80 MB)
  - **Summary**: `data/processed/fbi_crime_summary_2023.json`
  - **Script**: `scripts/data_collection/collect_measure_7_4_7_5_crime.py`
  - **API Client**: `scripts/api_clients/fbi_cde_client.py`

### 7.5 Property Crime Rate

- **Nebraska Source**: FBI Uniform Crime Reporting, Crime in the United States, 2018
- **Nebraska Metric**: Annual property crimes per 100,000 population
- **Virginia API Source**: FBI Crime Data Explorer API
- **API Endpoint**: `https://api.usa.gov/crime/fbi/cde/`
- **Confidence**: ✅ **HIGH**
- **Notes**:
  - FBI UCR provides property crime counts by agency
  - Property crimes include: burglary, larceny-theft, motor vehicle theft, arson
  - Aggregate agency-level data to county level
  - Calculate: (Property_crimes / Population) * 100,000
  - Inverse scoring: Lower crime rate = better quality of life
  - The safety of personal property is a critical component of enjoying life
  - FBI_UCR_KEY available in environment
- **Data Year for Virginia**: Use most recent year available (likely 2021 or 2022)
- **✅ DATA COLLECTED** (2025-11-17):
  - **API Endpoint**: `/summarized/agency/{ORI9}/{offense}` where offense = 'P' for property
  - **Year**: 2023 (01-2023 to 12-2023)
  - **Agency Mapping**: Uses `ori_crosswalk.tsv` to map 5,749 agencies (ORI9 codes) to counties
  - **Same implementation as Measure 7.4** - collected simultaneously
  - **Full Collection**: 5,749 agencies processed (same collection as 7.4)
  - **Total Property Crimes**: 1,278,315
  - **Counties Covered**: 804 counties
  - **Raw Data**: `data/raw/fbi_cde/{ORI}_{offense}_{from}_{to}.json` (shared cache with 7.4)
  - **Processed Data**: `data/processed/fbi_crime_counties_2023.csv` (shared with 7.4)
  - **Agency Data**: `data/processed/fbi_crime_agencies_2023.json` (shared with 7.4)
  - **Summary**: `data/processed/fbi_crime_summary_2023.json` (shared with 7.4)
  - **Script**: `scripts/data_collection/collect_measure_7_4_7_5_crime.py` (shared with 7.4)
  - **API Client**: `scripts/api_clients/fbi_cde_client.py` (shared with 7.4)

### 7.6 Climate Amenities

- **Nebraska Source**: United States Department of Agriculture Economic Research Service, Natural Amenities Scale, 1941-1970, last updated 1999
- **Nebraska Metric**: An index capturing average temperatures in January and July, sunny days in January, and humidity in July
- **Virginia Data Source**: USDA ERS Natural Amenities Scale (bulk download)
- **Confidence**: 🟡 **MEDIUM** (static data)
- **Notes**:
  - USDA ERS Natural Amenities Scale is a county-level index based on 30-year climate data
  - Available as bulk download: https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/52201/natamenf_1_.xls?v=83168
  - Static data (based on 1941-1970 climate normals)
  - Index components (6 measures combined into composite scale):
    - Mean January temperature (warm winter)
    - Mean July temperature (temperate summer)
    - Mean January days with sun (winter sun)
    - Mean July relative humidity (low summer humidity)
    - Topographic variation
    - Water area
  - A more comfortable climate can reduce utility costs and increase the enjoyment of outdoor activities
  - One-time data collection acceptable for static historical data
  - XLS file contains 104 rows of documentation before data table begins
  - Uses 'FIPS Code' column and 'Scale' column for composite amenity index
- **Implementation**: Download USDA ERS Natural Amenities Scale XLS file and filter to our 10 states
- **Data Source**: https://www.ers.usda.gov/data-products/natural-amenities-scale/
- **Data Year**: Based on 1941-1970 climate normals (static)
- **✅ DATA COLLECTED** (2025-11-17):
  - **Records**: 805 counties across 10 states
  - **Raw Data**: `data/raw/usda_ers/natural_amenities_scale.xls`
  - **Filtered Data**: `data/raw/usda_ers/natural_amenities_scale_filtered.json`
  - **Processed Data**: `data/processed/usda_ers_natural_amenities_scale.csv`
  - **Script**: `scripts/data_collection/collect_component7.py` (integrated with other measures)
  - **Mean Scale**: -0.01 (range: -3.98 to 3.55)

### 7.7 Healthcare Access

- **Nebraska Source**: Census Bureau County Business Patterns and Annual Estimates of the Resident Population for Counties, 2019
- **Nebraska Metric**: Number of healthcare practitioners per person (or per 1,000/10,000 population)
- **Virginia API Source**: Census CBP API
- **API Endpoint**: `https://api.census.gov/data/[year]/cbp`
- **NAICS Code**: 621 (Ambulatory Health Care Services) + 622 (Hospitals)
- **Variables**: EMP (Employment in healthcare establishments)
- **Confidence**: ✅ **HIGH**
- **Collection Status**: ✅ **COLLECTED** (2025-11-17)
- **Notes**:
  - CBP provides employment counts for healthcare establishments
  - NAICS 621: Ambulatory Health Care Services (physician offices, dentist offices, etc.)
  - NAICS 622: Hospitals
  - Calculate: (Healthcare_employment / Population) * 10,000
  - Measures access to medical care or key institutions like hospitals where physicians work in large numbers
  - Available at county level for all states
- **Data Year for Virginia**: Use most recent CBP year available (2021)
- **Data Files**:
  - Raw: `data/raw/cbp/cbp_healthcare_621_2021_[STATE].json` (10 states, NAICS 621)
  - Raw: `data/raw/cbp/cbp_healthcare_622_2021_[STATE].json` (10 states, NAICS 622)
  - Processed: `data/processed/cbp_healthcare_employment_2021.csv` (771 counties with healthcare establishments)

### 7.8 Count of National Parks

- **Nebraska Source**: National Park Service, Find a Park, 2018
- **Nebraska Metric**: Share of regional counties with one or more national parks, monuments, trails or other protected areas
- **Virginia API Source**: National Park Service API
- **API Endpoint**:
  - Parks: `https://developer.nps.gov/api/v1/parks`
  - Boundaries: `https://developer.nps.gov/api/v1/mapdata/parkboundaries/{parkCode}`
- **Confidence**: ✅ **HIGH**
- **Collection Status**: ✅ **COLLECTED** (2025-11-17)
- **Notes**:
  - NPS API provides both park location data and boundary geometries (GeoJSON MultiPolygon)
  - **Implementation uses boundary-based spatial intersection** (not just headquarters location)
  - Parks are assigned to ALL counties they touch using polygon intersection analysis
  - Filter for parks in Virginia and surrounding 9 states
  - Types include: National Parks, National Monuments, National Historic Sites, National Trails, National Seashores, etc.
  - A measure of local recreation options
  - Spatial analysis performed with geopandas and shapely
- **Results**:
  - 33 parks collected across 10 states
  - 146 counties with parks (18.2% of 802 counties)
  - 255 park-county assignments (parks mapped to all counties they intersect)
  - Examples: Captain John Smith Chesapeake Trail (90 counties), Blue Ridge Parkway (30 counties)
- **Data Files**:
  - Raw: `data/raw/nps/nps_parks_raw_data.json` (33 parks)
  - Processed: `data/processed/nps_park_counts_by_county.csv` (802 counties with park counts)
  - Processed: `data/processed/nps_parks_county_mapping.csv` (255 park-county assignments)
  - Alternative: Use NPS bulk data download if API insufficient
- **Implementation**: Use NPS API to get park locations; map to counties using GIS
- **Data Year for Virginia**: Use current NPS data (updates infrequently)

---

## Component Index 8: Social Capital (5 measures)

**Note**: This index measures community engagement, volunteering, and civic participation, following Nebraska Thriving Index methodology exactly.

### 8.1 Number of 501c3 Organizations Per 1,000 Persons

- **Nebraska Source**: Tax Exempt World, 2022
- **Nebraska Metric**: Count of non-profit 501(c)(3) organizations per 1,000 persons
- **Virginia API Source**: IRS Exempt Organizations Business Master File (EO BMF)
- **Data Source**: IRS bulk download
- **Confidence**: 🟡 **MEDIUM** (bulk download, no direct API)
- **Notes**:
  - IRS publishes Exempt Organizations Business Master File monthly
  - Available as CSV/JSON bulk download from IRS.gov
  - Filter by subsection code "03" for 501(c)(3) organizations
  - County FIPS codes included in download
  - For multi-county regions: Sum organizations, divide by total population
  - Formula: `(Count_501c3 / Population) * 1000`
  - Measures opportunities for volunteering and building social capital networks
- **Data Period for Virginia**: Use most recent IRS EO BMF extract (monthly updates)
- **Download URL**: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf

### 8.2 Volunteer Rate (State Level)

- **Nebraska Source**: Corporation for National & Community Service, 2017
- **Nebraska Metric**: Share of state population volunteering time to non-profit organizations
- **Virginia API Source**: AmeriCorps (formerly CNCS) Volunteering and Civic Life in America
- **Data Source**: AmeriCorps annual reports and data downloads
- **Confidence**: 🟡 **MEDIUM** (bulk data, state-level only, not county-level)
- **Notes**:
  - AmeriCorps publishes annual Volunteering in America reports
  - Data collected via Current Population Survey (CPS) September Volunteer Supplement
  - STATE-LEVEL DATA ONLY (not available at county/regional level)
  - All regions within same state receive same volunteer rate
  - Use most recent available year (check for updates beyond 2017)
  - Measures participation in networking opportunities related to volunteering
- **Data Period for Virginia**: Use most recent AmeriCorps Volunteering in America data
- **Download URL**: https://americorps.gov/about/our-impact/volunteering-civic-engagement-research

### 8.3 Volunteer Hours Per Person (State Level)

- **Nebraska Source**: Corporation for National & Community Service, 2017
- **Nebraska Metric**: Number of volunteer hours per person in the state
- **Virginia API Source**: AmeriCorps Volunteering and Civic Life in America
- **Data Source**: AmeriCorps annual reports and data downloads
- **Confidence**: 🟡 **MEDIUM** (bulk data, state-level only, not county-level)
- **Notes**:
  - Same source as measure 8.2
  - STATE-LEVEL DATA ONLY (not available at county/regional level)
  - All regions within same state receive same volunteer hours per person
  - Represents intensity of participation in volunteering (beyond just % who volunteer)
  - Use most recent available year
- **Data Period for Virginia**: Use most recent AmeriCorps Volunteering in America data
- **Download URL**: https://americorps.gov/about/our-impact/volunteering-civic-engagement-research

### 8.4 Voter Turnout

- **Nebraska Source**: State by State Voter Turnout, 2018
- **Nebraska Metric**: Percentage of registered voters who participated in fall 2018 general election
- **Virginia API Source**: State election offices and MIT Election Lab
- **Data Source**: State-level election results (bulk data collection)
- **Confidence**: 🟡 **MEDIUM** (bulk data, requires state-by-state collection)
- **Notes**:
  - No unified API across states
  - Each state publishes election results on Secretary of State websites
  - MIT Election Data and Science Lab aggregates county-level results
  - Use most recent general election (2022 or 2020) for consistency
  - For multi-county regions: Calculate weighted average turnout by county
  - Formula: `(Total_Votes_Cast / Registered_Voters) * 100`
  - Measures civic involvement short of formally volunteering
  - County-level data generally available from state election offices
- **Data Period for Virginia**: Use most recent general election (2022 recommended)
- **Alternative Source**: MIT Election Data + Science Lab (https://electionlab.mit.edu/)

### 8.5 Share of Tree City USA Counties

- **Nebraska Source**: Arbor Day Foundation, Tree City USA Communities, 2022
- **Nebraska Metric**: Share of regional population living in a county with at least one Tree City USA community
- **Virginia API Source**: Arbor Day Foundation Tree City USA directory
- **Data Source**: Static list from Arbor Day Foundation website
- **Confidence**: 🟡 **MEDIUM** (static data, requires manual mapping)
- **Notes**:
  - Arbor Day Foundation publishes list of Tree City USA communities annually
  - Need to map communities to counties (some communities are cities within counties)
  - Binary variable at county level: 1 if county has Tree City USA, 0 if not
  - For multi-county regions: Calculate as `(Population_in_Tree_City_counties / Total_regional_population)`
  - Measures social involvement related to built environment and environmental stewardship
  - Tree City USA designation requires: tree board/department, tree ordinance, $2/capita forestry spending, Arbor Day proclamation
  - One-time manual mapping acceptable for this static data
- **Data Period for Virginia**: Use most recent Tree City USA list (updated annually)
- **Directory URL**: https://www.arborday.org/programs/treecityusa/

---