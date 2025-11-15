# Nebraska vs Virginia Thriving Index - Measure Comparison

**Date**: 2025-11-15
**Total Measures**: 47
**Virginia Ready**: 29 (61.7%)
**Virginia Needs Investigation**: 10 (21.3%)
**Virginia Cannot Implement**: 8 (17.0%)

---

## Legend

- ✅ **READY**: Data source identified, API available, implementation ready
- 🟡 **INVESTIGATE**: Potential data source exists, needs verification
- ❌ **NO API**: No viable API source identified
- ⚠️ **MODIFIED**: Virginia uses different data source/methodology than Nebraska

---

## Component Index 1: Growth Index (6 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 1.1 | Population Growth Rate (5-year) | Census Population Estimates | ✅ READY | Census PEP API | Identical to Nebraska |
| 1.2 | Employment Growth Rate (5-year) | BLS QCEW | ✅ READY | BLS QCEW API | Identical to Nebraska |
| 1.3 | Wages and Salaries Growth Rate (5-year) | BEA Regional | ✅ READY | BEA CAINC4 Line 30 | **Just implemented** |
| 1.4 | Proprietors Income Growth Rate (5-year) | BEA Regional | ✅ READY | BEA CAINC4 Lines 50+60 | **Just implemented** |
| 1.5 | Per Capita Personal Income Growth (5-year) | BEA Regional | ✅ READY | BEA CAINC1 Line 3 | Identical to Nebraska |
| 1.6 | Retail Sales Growth Rate (5-year) | State revenue, Census | ❌ NO API | N/A | No consistent API across states |

**Summary**: 5/6 measures ready (83.3%)

---

## Component Index 2: Economic Opportunity & Diversity (7 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 2.1 | Per Capita Personal Income (level) | BEA Regional | ✅ READY | BEA CAINC1 Line 3 | Identical to Nebraska |
| 2.2 | Median Household Income | Census ACS | ✅ READY | Census ACS B19013_001E | Identical to Nebraska |
| 2.3 | Poverty Rate (inverse) | Census ACS | ✅ READY | Census ACS S1701_C03_001E | Identical to Nebraska |
| 2.4 | Labor Force Participation Rate | Census ACS | ✅ READY | Census ACS S2301_C02_001E | Identical to Nebraska |
| 2.5 | Unemployment Rate (inverse) | BLS LAUS | ✅ READY | BLS LAUS API | Identical to Nebraska |
| 2.6 | Share of Workforce in High-Wage Industries | BLS QCEW / CBP | 🟡 INVESTIGATE | Census CBP or BLS QCEW | Need to define "high-wage" threshold |
| 2.7 | Economic Diversity (HHI) | CBP employment | ✅ READY | Census CBP API | Identical to Nebraska |

**Summary**: 6/7 measures ready (85.7%), 1 needs investigation

---

## Component Index 3: Other Economic Prosperity (4 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 3.1 | Per Capita Retail Sales | State revenue | ❌ NO API | N/A | State-level only, no county API |
| 3.2 | Per Capita Bank Deposits | FDIC Summary | 🟡 INVESTIGATE | FDIC bulk download | May require bulk download vs API |
| 3.3 | New Business Formations Per Capita | Census BFS | 🟡 INVESTIGATE | Census BFS | County-level availability unclear |
| 3.4 | Business Survival Rate | Census BDS | ❌ NO API | N/A | County detail often suppressed |

**Summary**: 0/4 measures ready (0%), 2 need investigation, 2 no API
**⚠️ WARNING**: This component may need to be excluded or significantly revised

---

## Component Index 4: Demographic Growth & Renewal (4 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 4.1 | Natural Increase Rate | Census PEP | ✅ READY | Census PEP components API | Identical to Nebraska |
| 4.2 | Net Migration Rate | Census PEP | ✅ READY | Census PEP components API | Identical to Nebraska |
| 4.3 | Percent Population Age 25-54 | Census ACS | ✅ READY | Census ACS B01001 | Identical to Nebraska |
| 4.4 | Median Age (inverse) | Census ACS | ✅ READY | Census ACS B01002_001E | Identical to Nebraska |

**Summary**: 4/4 measures ready (100%)

---

## Component Index 5: Education & Skill (5 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 5.1 | High School Graduation Rate | State Dept of Education | ✅ READY | Census ACS S1501_C02_014E | ⚠️ **MODIFIED**: Uses educational attainment instead of graduation rate |
| 5.2 | Percent with Some College | Census ACS | ✅ READY | Census ACS B15003 | Identical to Nebraska |
| 5.3 | Percent with Bachelor's or Higher | Census ACS | ✅ READY | Census ACS S1501_C02_015E | Identical to Nebraska |
| 5.4 | Student-Teacher Ratio (inverse) | NCES, State DoE | ❌ NO API | N/A | District-level, not county; no API |
| 5.5 | School District Spending Per Pupil | NCES, State DoE | ❌ NO API | N/A | District-level, not county; no API |

**Summary**: 3/5 measures ready (60%), 1 modified methodology

---

## Component Index 6: Infrastructure & Cost of Doing Business (6 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 6.1 | Broadband Access (% with access) | FCC Broadband Map | 🟡 INVESTIGATE | FCC API (pending key) | Placeholder implementation planned |
| 6.2 | Housing Affordability Index | Census ACS (calculated) | ✅ READY | Census ACS B19013, B25077, B25064 | Identical to Nebraska |
| 6.3 | Percent Housing Built in Last 10 Years | Census ACS | ✅ READY | Census ACS B25034 | Identical to Nebraska |
| 6.4 | Property Crime Rate (inverse) | FBI UCR | ✅ READY | FBI Crime Data Explorer API | FBI_UCR_KEY available |
| 6.5 | Violent Crime Rate (inverse) | FBI UCR | ✅ READY | FBI Crime Data Explorer API | FBI_UCR_KEY available |
| 6.6 | Highway Accessibility Index | Calculated from GIS | ❌ NO API | N/A | Would require GIS processing |

**Summary**: 3/6 measures ready (50%), 2 ready with keys, 1 needs investigation

---

## Component Index 7: Quality of Life (8 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 7.1 | Life Expectancy at Birth | CDC, IHME | ❌ NO API | County Health Rankings | Bulk download available, no API |
| 7.2 | Infant Mortality Rate (inverse) | CDC WONDER | 🟡 INVESTIGATE | CDC WONDER | API limited, small counties suppressed |
| 7.3 | Percent Uninsured (inverse) | Census ACS | ✅ READY | Census ACS S2701_C05_001E | Identical to Nebraska |
| 7.4 | Primary Care Physicians Per Capita | AHRF, CMS | 🟡 INVESTIGATE | CMS NPPES / AHRF | May require bulk download |
| 7.5 | Mental Health Providers Per Capita | AHRF, HRSA | ❌ NO API | County Health Rankings | Bulk download available, no API |
| 7.6 | Recreation Establishments Per Capita | Census CBP | ✅ READY | Census CBP NAICS 71 | Identical to Nebraska |
| 7.7 | Restaurants Per Capita | Census CBP | ✅ READY | Census CBP NAICS 722 | Identical to Nebraska |
| 7.8 | Arts/Entertainment Establishments Per Capita | Census CBP | ✅ READY | Census CBP NAICS 711, 712 | Identical to Nebraska |

**Summary**: 4/8 measures ready (50%), 2 need investigation

---

## Component Index 8: Social Capital (7 measures)

| # | Measure | Nebraska Source | Virginia Status | Virginia Source | Notes |
|---|---------|----------------|----------------|-----------------|-------|
| 8.1 | Voter Participation Rate | State election data | ❌ NO API | N/A | No standardized API across states |
| 8.2 | Nonprofit Organizations Per Capita | IRS Exempt Orgs | 🟡 INVESTIGATE | IRS bulk download | Bulk file available monthly |
| 8.3 | Religious Congregations Per Capita | ASARB | ❌ NO API | N/A | Periodic census, no API |
| 8.4 | Social Associations Per Capita | Census CBP | ✅ READY | Census CBP NAICS 813 | Identical to Nebraska |
| 8.5 | % Children in Single-Parent HH (inverse) | Census ACS | ✅ READY | Census ACS B09002 | Identical to Nebraska |
| 8.6 | Income Inequality - Gini (inverse) | Census ACS | ✅ READY | Census ACS B19083_001E | Identical to Nebraska |
| 8.7 | Social Capital Index (composite) | Various/calculated | 🟡 INVESTIGATE | Depends on components | Will calculate from available measures |

**Summary**: 4/7 measures ready (57.1%), 2 need investigation

---

## Overall Summary

### Measures by Status

| Status | Count | Percentage | Notes |
|--------|-------|------------|-------|
| ✅ **READY** (Identical to Nebraska) | 26 | 55.3% | Direct API access, same methodology |
| ✅ **READY** (Modified methodology) | 1 | 2.1% | Educational attainment vs graduation rate |
| 🟡 **FBI/FCC Keys Available** | 2 | 4.3% | Crime rates (FBI_UCR_KEY available) |
| 🟡 **INVESTIGATE** | 10 | 21.3% | Potential sources, need verification |
| ❌ **NO API** | 8 | 17.0% | No viable API source |
| **TOTAL** | **47** | **100%** | |

### Ready for Implementation: **29 measures (61.7%)**
- 26 identical to Nebraska methodology
- 1 modified methodology (educational attainment)
- 2 with available API keys (crime rates)

---

## Key Differences from Nebraska

### 1. **Educational Attainment vs Graduation Rates** (Measure 5.1)
- **Nebraska**: Uses 4-year cohort graduation rates from state departments of education
- **Virginia**: Uses percent of adults 25+ with high school diploma or higher (Census ACS)
- **Rationale**: Better regional metric, consistently available across all states via API

### 2. **Farm Income Source** (Used in matching variables)
- **Nebraska**: BEA farm proprietors income (CAINC4, Line Code 50)
- **Virginia**: BEA farm proprietors income (CAINC4, Line Code 50)
- **Note**: Originally incorrectly assumed USDA NASS; corrected to match Nebraska exactly

### 3. **Missing BEA Measures - NOW IMPLEMENTED** (Measures 1.3, 1.4)
- **Wages and salaries growth rate**: BEA CAINC4, Line Code 30 ✅
- **Total proprietors income growth rate**: BEA CAINC4, Line Codes 50+60 ✅
- **Status**: Implemented as of 2025-11-15

---

## Component Coverage Analysis

| Component Index | Ready | Investigate | No API | Total | % Ready |
|----------------|-------|-------------|--------|-------|---------|
| 1. Growth | 5 | 0 | 1 | 6 | 83.3% |
| 2. Economic Opportunity & Diversity | 6 | 1 | 0 | 7 | 85.7% |
| 3. Other Economic Prosperity | 0 | 2 | 2 | 4 | 0% ⚠️ |
| 4. Demographic Growth & Renewal | 4 | 0 | 0 | 4 | 100% |
| 5. Education & Skill | 3 | 0 | 2 | 5 | 60.0% |
| 6. Infrastructure & Cost | 5 | 1 | 0 | 6 | 83.3% |
| 7. Quality of Life | 4 | 2 | 2 | 8 | 50.0% |
| 8. Social Capital | 4 | 2 | 1 | 7 | 57.1% |
| **OVERALL** | **31** | **8** | **8** | **47** | **66.0%** |

**Note**: Totals include 2 measures with available keys (FBI crime rates) in "Ready" category.

---

## Critical Decision Required

### Component Index 3: "Other Economic Prosperity"

**Problem**: 0/4 measures have HIGH-confidence API access

**Options**:
1. **Exclude this component entirely** - Proceed with 7 component indexes (43 measures)
2. **Investigate MEDIUM measures** - Bank deposits and business formations may be accessible via bulk downloads
3. **Find proxy measures** - Identify alternative measures of economic prosperity
4. **Combine with Component 2** - Merge into "Economic Opportunity, Diversity & Prosperity"

**Recommendation**: Investigate bank deposits (FDIC) and business formations (Census BFS) first. If not viable at county level, **exclude this component** rather than use poor proxies.

---

## Next Steps for Full Nebraska Alignment

### Immediate (Already Completed) ✅
- [x] Implement wages and salaries growth rate (1.3)
- [x] Implement total proprietors income growth rate (1.4)
- [x] Remove USDA NASS (Nebraska doesn't use it)
- [x] Use BEA farm proprietors income for matching

### Short Term (Investigate MEDIUM measures)
- [ ] Test FCC API for broadband access (6.1) - API key pending
- [ ] Verify FBI Crime Data Explorer for crime rates (6.4, 6.5) - Key available
- [ ] Investigate FDIC Summary of Deposits for bank deposits (3.2)
- [ ] Check Census BFS for business formations at county level (3.3)
- [ ] Research CDC WONDER API for infant mortality (7.2)
- [ ] Explore CMS NPPES for physician counts (7.4)
- [ ] Review IRS Exempt Organizations bulk data (8.2)

### Medium Term (Methodology Decisions)
- [ ] Define "high-wage industries" threshold for measure 2.6
- [ ] Decide on Component Index 3 (exclude vs investigate vs modify)
- [ ] Finalize social capital composite calculation (8.7)

### Long Term (Data Collection)
- [ ] Collect all 29 ready measures for 54 regions
- [ ] Calculate peer matching variables (6 measures)
- [ ] Implement Mahalanobis distance peer selection
- [ ] Calculate standardized scores and component indexes

---

**Last Updated**: 2025-11-15
**Document Status**: Reflects implementation after USDA NASS removal and BEA measures addition
