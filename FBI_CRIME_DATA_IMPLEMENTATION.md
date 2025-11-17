# FBI Crime Data Collection - Implementation Summary

## Status: ✅ Working and Ready for Review

Successfully implemented Measures 7.4 (Violent Crime Rate) and 7.5 (Property Crime Rate) for Component 7.

## Files Created

### 1. API Client
**`scripts/api_clients/fbi_cde_client.py`**
- FBI Crime Data Explorer API client
- Follows project's API client pattern
- **Includes caching** to minimize API calls
- Handles both violent ('V') and property ('P') crime data
- Tracks API calls made (important for 1000/day limit)

### 2. Collection Script
**`scripts/data_collection/collect_measure_7_4_7_5_crime.py`**
- Loads ORI crosswalk (maps law enforcement agencies to counties)
- Collects crime data for all agencies in 10 states
- Aggregates agency-level data to county level
- **Test mode enabled** by default (currently set to 30 VA agencies)
- Full collection disabled pending your review

## Test Results

### Test Run Details
- **Agencies tested**: 30 Virginia agencies
- **API calls made**: 58 (2 were cached)
- **Counties covered**: 10 Virginia counties
- **Data collected**:
  - Violent crimes: 1,207
  - Property crimes: 8,963

### Sample Output (first 10 counties)
```
County              Violent  Property  Agencies
ACCOMACK               116      322        7
ALBEMARLE              132    1,814        2
ALLEGHANY               44      300        5
AMELIA                  17      131        2
AMHERST                 70      364        3
APPOMATTOX              34      101        3
ARLINGTON              611    4,620        3
AUGUSTA                 97      758        2
BATH                     8       11        2
BEDFORD                 78      542        1
```

## Key Implementation Details

### 1. ORI Codes
- FBI API requires **ORI9** (9-character codes), not ORI7
- Example: `VA0010100` (ORI9) vs `VA00101` (ORI7)
- Crosswalk file contains both formats

### 2. Data Structure
- FBI API returns JSON with structure:
  ```json
  {
    "offenses": {
      "actuals": {
        "Agency Name": {
          "01-2022": 5,
          "02-2022": 3,
          ...
        }
      }
    }
  }
  ```
- Script sums monthly counts across full year
- Handles agencies with no data (`actuals: null`)

### 3. Caching System
- **Critical for API limit**: Each response cached locally
- Cached files stored in: `data/raw/fbi_cde/`
- Format: `{ORI}_{offense}_{from}_{to}.json`
- Subsequent runs use cache (no API calls)
- Currently **62 files cached** from testing

### 4. State Breakdown (Full Collection Scope)

| State          | Agencies | API Calls Needed |
|----------------|----------|------------------|
| Delaware       | 66       | 132              |
| Georgia        | 759      | 1,518            |
| Kentucky       | 608      | 1,216            |
| Maryland       | 175      | 350              |
| North Carolina | 563      | 1,126            |
| Pennsylvania   | 1,616    | 3,232            |
| South Carolina | 521      | 1,042            |
| Tennessee      | 488      | 976              |
| Virginia       | 437      | 874              |
| West Virginia  | 510      | 1,020            |
| **TOTAL**      | **5,749**| **11,498**       |

## Full Collection Plan

### Current Configuration (TEST MODE)
```python
TEST_LIMIT = 30          # Only process 30 agencies
TEST_STATE = 'VIRGINIA'  # Only Virginia agencies
```

### For Full Collection
```python
TEST_LIMIT = None        # Process all agencies
TEST_STATE = None        # All 10 states
```

### Timeline Estimate
- **Total API calls**: ~11,498 (5,749 agencies × 2 crime types)
- **Daily limit**: 1,000 calls
- **Estimated time**: ~12 days for complete collection
- **With caching**: Subsequent runs take 0 days (all cached)

### Recommended Approach
1. **Day 1-2**: Collect Virginia + smaller states (DE, MD) - ~1,400 calls
2. **Day 3-5**: Collect Pennsylvania (largest) - ~3,200 calls
3. **Day 6-12**: Collect remaining states incrementally
4. **Alternative**: Run with no limit, let it collect ~1,000/day automatically

## Next Steps (Pending Your Approval)

### Option 1: State-by-State Collection
Modify script to collect one state at a time:
```python
# Collect state by state
for state in ['VIRGINIA', 'DELAWARE', 'MARYLAND', ...]:
    TEST_STATE = state
    TEST_LIMIT = None
    # Run collection
```

### Option 2: Incremental Collection
Run script multiple times, letting it respect the 1000/day limit:
```python
TEST_LIMIT = 500  # Stay under limit
TEST_STATE = None  # All states
# Run daily until complete
```

### Option 3: Full Collection
```python
TEST_LIMIT = None
TEST_STATE = None
# Let it run, monitoring daily call count
```

## Additional Enhancements Needed

Before full collection, we should:

1. **Add population data** for crime rate calculation
   - Need to join with Census population data
   - Calculate: `(crimes / population) * 100,000`

2. **Create final processed output**
   - Violent crime rate per 100,000
   - Property crime rate per 100,000
   - Integrated with other Component 7 measures

3. **Handle missing data**
   - Some agencies don't report (actuals: null)
   - Document coverage gaps by county

4. **Add progress tracking**
   - Save incremental results
   - Resume capability if interrupted

## Files Generated (Current Test)

### Raw Data
- `data/raw/fbi_cde/*.json` - 62 cached API responses

### Processed Data
- `data/processed/fbi_crime_agencies_2022.json` - Agency-level data
- `data/processed/fbi_crime_counties_2022.csv` - County-level aggregates
- `data/processed/fbi_crime_summary_2022.json` - Collection summary

## Questions for Review

1. **Should we proceed with full collection now or wait?**
2. **Which collection approach do you prefer?** (state-by-state, incremental, or full)
3. **Should we add population data integration before full collection?**
4. **Do you want crime rates calculated, or just raw counts?**

---

**Status**: Ready for your review and direction on next steps.
