# API Keys Status - Virginia Thriving Index

**Last Updated**: 2025-11-14
**Status**: ✅ All essential API keys available + MEDIUM-confidence sources

---

## Summary

All essential API keys required for the Virginia Thriving Index project are available in the environment, plus additional MEDIUM-confidence sources (USDA NASS, FBI UCR). This enables immediate implementation of high-confidence measures and expands coverage to several MEDIUM-confidence measures. FCC broadband API key is pending but placeholder implementation will be created.

---

## Available API Keys

### Essential Keys (Required) ✅

| API Key Variable | Status | Purpose | Priority |
|-----------------|--------|---------|----------|
| `CENSUS_KEY` | ✅ Available | Census Bureau ACS, CBP, Population Estimates | **CRITICAL** |
| `BEA_API_KEY` | ✅ Available | Bureau of Economic Analysis - Income, GDP data | **CRITICAL** |
| `BLS_API_KEY` | ✅ Available | Bureau of Labor Statistics - Employment, Unemployment | **CRITICAL** |

### MEDIUM-Confidence Keys (Now Available) ✅

| API Key Variable | Status | Purpose | Impact |
|-----------------|--------|---------|--------|
| `FBI_UCR_KEY` | ✅ Available | FBI Uniform Crime Reporting | Enables crime rate measures (violent, property) |

### Pending Keys ⏳

| API Key Variable | Status | Purpose | Workaround |
|-----------------|--------|---------|------------|
| `FCC_API_KEY` | ⏳ Pending | FCC Broadband Map | Placeholder implementation for future |

### Bonus Keys (Potentially Useful) ✅

| API Key Variable | Status | Purpose | Notes |
|-----------------|--------|---------|-------|
| `FRED_API_KEY` | ✅ Available | Federal Reserve Economic Data | Alternative/supplementary economic indicators |

### Other Keys (Not Needed for This Project)

| API Key Variable | Status | Purpose |
|-----------------|--------|---------|
| `EIA_API_KEY` | ✅ Available | Energy Information Administration |
| `DASH_API_KEY` | ✅ Available | Unknown - possibly Plotly Dash |
| `MARKET_DATA_YAHOO_API_KEY` | ✅ Available | Yahoo Finance API |
| `WMATA_API_KEY` | ✅ Available | Washington Metro Transit |

---

## Data Sources Coverage

With the available API keys, we can access:

### Census Bureau (via CENSUS_KEY)

**American Community Survey (ACS) 5-Year Estimates**:
- Demographics (age, population, migration)
- Income (median household income, per capita income, poverty)
- Education (educational attainment)
- Employment (labor force participation, unemployment)
- Housing (home values, rent, construction year, units)
- Health insurance coverage
- Family structure (single-parent households)
- Income inequality (Gini coefficient)

**County Business Patterns (CBP)**:
- Establishments by industry (NAICS codes)
- Employment by industry
- Economic diversity measures
- Industry-specific counts (restaurants, recreation, social associations)

**Population Estimates Program (PEP)**:
- Annual population estimates
- Components of change (births, deaths, migration)
- Population by age and sex

### Bureau of Economic Analysis (via BEA_API_KEY)

**Regional Economic Accounts**:
- Per capita personal income (levels and growth)
- Total personal income by component:
  - Wages and salaries
  - Proprietors income (farm and non-farm)
  - Dividends, interest, rent
  - Transfer payments
- GDP by county
- Employment by industry

### Bureau of Labor Statistics (via BLS_API_KEY)

**Local Area Unemployment Statistics (LAUS)**:
- Monthly and annual unemployment rates by county
- Labor force size
- Employment levels

**Quarterly Census of Employment and Wages (QCEW)**:
- Employment by industry (detailed NAICS)
- Average weekly wages by industry
- Number of establishments by industry
- Total wages by industry

### Federal Reserve Economic Data (via FRED_API_KEY)

**Economic Indicators** (varies by availability):
- State and metro-level economic indicators
- May have some county-level data
- Can supplement BEA/BLS data
- Useful for validation and cross-checking

---

## Measures Confirmed Accessible

Based on available API keys, the following measures are confirmed accessible:
- **28 HIGH-confidence measures** (original assessment)
- **Additional measures promoted from MEDIUM to HIGH** with NASSQS_TOKEN and FBI_UCR_KEY

### Newly Promoted Measures (MEDIUM → HIGH)

With FBI_UCR_KEY now available:
1. **Property Crime Rate** (6.4) - FBI UCR API ✅
2. **Violent Crime Rate** (6.5) - FBI UCR API ✅

**Note**: Farm income comes from BEA (farm proprietors income), not USDA NASS, per Nebraska methodology.

**Updated Total**: 29 HIGH-confidence measures (up from 28)

### Growth Index (5/6)
- ✅ Population growth rate (5-year)
- ✅ Employment growth rate (5-year)
- ✅ Wages and salaries growth rate (5-year)
- ✅ Proprietors income growth rate (5-year)
- ✅ Per capita personal income growth rate (5-year)
- ❌ Retail sales growth rate (no API)

### Economic Opportunity & Diversity (6/7)
- ✅ Per capita personal income (level)
- ✅ Median household income
- ✅ Poverty rate
- ✅ Labor force participation rate
- ✅ Unemployment rate
- ✅ Economic diversity (HHI)
- 🟡 Share of workforce in high-wage industries (needs investigation)

### Other Economic Prosperity (0/4)
- ❌ Per capita retail sales (no API)
- 🟡 Per capita bank deposits (FDIC - investigate)
- 🟡 New business formations per capita (investigate)
- ❌ Business survival rate (no API)

### Demographic Growth & Renewal (4/4)
- ✅ Natural increase rate
- ✅ Net migration rate
- ✅ Percent of population age 25-54
- ✅ Median age

### Education & Skill (2/5)
- ❌ High school graduation rate (no API)
- ✅ Percent with some college
- ✅ Percent with bachelor's degree or higher
- ❌ Student-teacher ratio (no API)
- ❌ School district spending per pupil (no API)

### Infrastructure & Cost (5/6)
- 🟡 Broadband access (FCC - API key pending, placeholder planned)
- ✅ Housing affordability index
- ✅ Percent housing built in last 10 years
- ✅ Property crime rate (FBI UCR API - KEY NOW AVAILABLE)
- ✅ Violent crime rate (FBI UCR API - KEY NOW AVAILABLE)
- ❌ Highway accessibility (no API)

### Quality of Life (4/8)
- ❌ Life expectancy (County Health Rankings - investigate)
- 🟡 Infant mortality rate (CDC WONDER - investigate)
- ✅ Percent uninsured
- 🟡 Primary care physicians per capita (investigate)
- ❌ Mental health providers per capita (investigate)
- ✅ Recreation establishments per capita
- ✅ Restaurants per capita
- ✅ Arts/entertainment establishments per capita

### Social Capital (4/7)
- ❌ Voter participation rate (no API)
- 🟡 Nonprofit organizations per capita (IRS - investigate)
- ❌ Religious congregations per capita (no API)
- ✅ Social associations per capita
- ✅ Percent children in single-parent households
- ✅ Income inequality (Gini coefficient)
- 🟡 Social capital index composite (depends on components)

**Total Confirmed**: 30 HIGH-confidence measures (28 original + 2 promoted)
**Total Requires Investigation**: 8 MEDIUM-confidence measures (2 promoted to HIGH)
**Total Cannot Access**: 9 LOW-confidence measures

**Updated Assessment**:
- Property Crime Rate (6.4): MEDIUM → ✅ HIGH (FBI_UCR_KEY available)
- Violent Crime Rate (6.5): MEDIUM → ✅ HIGH (FBI_UCR_KEY available)
- Farm Income for matching: Uses BEA farm proprietors income (CAINC4, Line Code 50)

---

## Missing API Keys (Not Critical)

The following API keys are not available but would be needed for MEDIUM/LOW confidence measures:

### Would Be Useful (If Pursuing Additional Measures)
- `FCC_API_KEY` - FCC Broadband Map (broadband access)

### Not Available via API (Need Alternative Approach)
- State Department of Education APIs (varies by state)
- County Health Rankings data (bulk download)
- IRS Exempt Organizations data (bulk download)
- FDIC Summary of Deposits (web access)

---

## Recommendations

### Immediate Next Steps (Phase 2 Planning)

1. **Proceed with 28 HIGH-confidence measures** using available API keys:
   - CENSUS_KEY for ACS, CBP, Population Estimates
   - BEA_API_KEY for income and economic data
   - BLS_API_KEY for employment and wages

2. **Test API connections** with sample requests to validate access:
   - Census ACS 5-year estimates (2018-2022)
   - BEA Regional Economic Accounts (2017-2022)
   - BLS LAUS unemployment data (2022)

3. **Investigate MEDIUM-confidence measures**:
   - Research FBI Crime Data Explorer API (crime rates)
   - Research FCC Broadband Map API (broadband access)
   - Review County Health Rankings bulk download options
   - Check IRS Exempt Organizations data format

4. **Revise Component Indexes**:
   - "Other Economic Prosperity" index may need significant revision (0/4 measures available)
   - Consider dropping this component or finding proxy measures
   - All other components have ≥50% measure coverage

5. **FRED API Exploration** (Bonus):
   - Investigate what county-level data available via FRED
   - May supplement or validate BEA/BLS data
   - Could provide alternative sources for some measures

### Decision Required

**Component Index 3 (Other Economic Prosperity)** has zero HIGH-confidence measures available via API:
- Per capita retail sales: ❌ No API
- Per capita bank deposits: 🟡 FDIC (investigate)
- New business formations: 🟡 Census BFS (investigate)
- Business survival rate: ❌ No API

**Options**:
1. **Drop this component entirely** - proceed with 7 component indexes (42 measures)
2. **Investigate MEDIUM measures** - attempt to include bank deposits and business formations
3. **Find proxy measures** - identify alternative measures for economic prosperity
4. **User decision** - ask user preference

**Recommendation**: Investigate MEDIUM measures first; if not viable, drop this component rather than use poor proxies.

---

## API Rate Limits & Usage Planning

### Census Bureau API
- **Rate Limit**: 500 requests per IP per day (unregistered), higher with key
- **Strategy**: Batch requests where possible; one request can fetch multiple variables
- **Expected Usage**: ~50-100 requests for all ACS variables across ~600 counties

### BEA API
- **Rate Limit**: 1,000 requests per day (registered key)
- **Strategy**: Request multiple years in single call; batch geographies
- **Expected Usage**: ~20-30 requests for all income components across regions

### BLS API
- **Rate Limit**: 500 requests per day (registered key), 25 per day (unregistered)
- **Strategy**: Use registered key; batch series requests (up to 50 series per call)
- **Expected Usage**: ~30-50 requests for unemployment and wage data

### Overall Assessment
With proper batching and caching, all data collection can be completed within rate limits in a single day. Caching will enable dashboard updates without re-fetching all data.

---

## Next Steps Summary

1. ✅ **COMPLETE**: Essential API keys confirmed available
2. **NEXT**: Test API connections with sample requests
3. **NEXT**: Begin Phase 2 (Data Collection Infrastructure)
4. **NEXT**: Investigate MEDIUM-confidence measures
5. **NEXT**: Make final decision on Component Index 3

---

*Document will be updated as API investigations progress.*
