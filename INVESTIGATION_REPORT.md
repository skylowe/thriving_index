# Investigation Report: FBI UCR API and Micropolitan Data Issues

**Date**: 2025-11-14
**Session**: claude/thriving-index-analysis-01BYbBkdyC1xUoLqqV4x7XCD

---

## Issue 1: FBI UCR API - 403 Forbidden Errors

### Problem
All FBI UCR API endpoints return `403 Forbidden` errors when accessed with the current API key.

### Root Cause
The FBI Crime Data API requires a **data.gov API key**, not a general FBI API key. The current `FBI_UCR_KEY` environment variable may not be properly configured for the Crime Data Explorer API.

### Technical Details
- **Base URL**: `https://api.usa.gov/crime/fbi/sapi/`
- **Authentication**: Requires `api_key` parameter from data.gov
- **Current Status**: All test endpoints failing with 403 errors
- **Key Format**: Should be from https://api.data.gov/signup/

### Test Results
```
Test 1: State Crime Summary - ✗ FAILED (403 Forbidden)
Test 2: Agency List - ✗ FAILED (403 Forbidden)
Test 3: Agency Crime Data - ✗ FAILED (403 Forbidden)
Test 4: Raw Endpoint Variations - ✗ FAILED (all 403 Forbidden)
```

### Endpoint Patterns Tested
1. `/api/summarized/state/{state}/offense/{year}` - 403
2. `/summarized/state/{state}/offense/{year}` - 403
3. `/states/{state}/offense/{year}` - 403
4. `/v1/state/{state}/{year}` - 403
5. `/api/agencies/byStateAbbr/{state}` - 403

### Findings from Research
- The API is **active and not deprecated** (as of November 2025)
- The GitHub repository (https://github.com/fbi-cde/crime-data-api) confirms API structure
- API requires data.gov API network key
- Alternative direct endpoint: `https://crime-data-api.fr.cloud.gov/` (also returns 404 for test endpoints)

### Resolution Required
**Option 1: Obtain Valid data.gov API Key**
- Sign up at: https://api.data.gov/signup/
- This key can be used across multiple federal APIs
- Update environment variable `FBI_UCR_KEY` with data.gov key

**Option 2: Alternative Data Sources for Crime Rates**
- Use FBI UCR bulk download files (https://ucr.fbi.gov/crime-in-the-u.s/)
- State-level crime statistics from individual state agencies
- Bureau of Justice Statistics data

**Option 3: Placeholder Implementation (Short-term)**
- Similar to FCC broadband approach
- Use state-level estimates and distribute to counties
- Mark data as "estimated" in dashboard
- Replace with real data once API access is secured

### Recommendations
1. **Immediate**: Verify if `FBI_UCR_KEY` is a valid data.gov API key
2. **Short-term**: Implement FBI UCR bulk data download parser if API unavailable
3. **Long-term**: Obtain proper data.gov API key for programmatic access
4. **Note**: Crime rates are Matching Variables 6.4 and 6.5 (classified as HIGH confidence)

---

## Issue 2: Micropolitan Data - All Values 0%

### Problem
All regional micropolitan percentages show 0%, indicating no counties are classified as micropolitan areas.

### Root Cause
The `data/cbsa_classifications.py` file contains classifications for only **35 counties** out of ~530 total counties in the study. All unclassified counties default to 'rural', and none of the 35 classified counties are micropolitan - they're all metropolitan.

### Technical Details
**Current Classification Coverage**:
- Total counties in study: ~530
- Classified in cbsa_classifications.py: 35 (6.6%)
- Classifications:
  - Metropolitan: 35 (100% of classified)
  - Micropolitan: 0 (0% of classified)
  - Rural: 495 (93.4% defaulted)

**Classified Regions**:
- Virginia: Northern Virginia, Richmond Metro, Hampton Roads (major metros only)
- Maryland: Baltimore Metro, DC suburbs (major metros only)
- District of Columbia: Full district (metro)
- Missing: All of WV, NC, TN, KY + most of VA and MD

### Impact on Matching Variable 2
```python
# From aggregate_micropolitan_data.py:
for fips, data in county_data.items():
    if data['metro_micro'] == 'micro':  # None match this condition!
        regional_data[region]['micro_pop'] += pop
```

Result: All regions calculate to 0% micropolitan because no counties are marked as 'micro'.

### Resolution Steps

**Step 1: Downloaded Complete CBSA Delineation File** ✓
- Source: Census Bureau (https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xls)
- File: `data/raw/cbsa_delineation_2023.xls`
- Size: 19 KB
- Contains: Complete metropolitan and micropolitan area delineations for all US counties

**Step 2: Parse and Convert to Python Dictionary**
- Read Excel file
- Extract columns: FIPS code, county name, CBSA code, CBSA title, metropolitan/micropolitan designation
- Map all ~530 study counties to their proper classification

**Step 3: Update cbsa_classifications.py**
- Replace incomplete dictionary with complete 530-county classification
- Ensure all FIPS codes in study regions are covered
- Maintain existing data structure for compatibility

**Step 4: Re-run Micropolitan Aggregation**
- Execute `scripts/aggregate_micropolitan_data.py`
- Verify non-zero micropolitan percentages
- Validate population-weighted calculations

### Expected Results After Fix
Based on Census Bureau data:
- **Metropolitan areas**: ~70-80% of study counties
- **Micropolitan areas**: ~15-20% of study counties
- **Rural areas**: ~5-10% of study counties

Example micropolitan areas in study region:
- Blacksburg, VA (Montgomery County)
- Harrisonburg, VA (Harrisonburg city/Rockingham County)
- Staunton, VA (Staunton city)
- Winchester, VA-WV
- Beckley, WV
- Pikeville, KY
- Morristown, TN

### Validation Checks
After implementing fix:
1. Verify total counties classified: 530/530 (100%)
2. Verify micropolitan count > 0
3. Check specific known micropolitan areas are correctly classified
4. Validate regional percentages make sense (not all 0%, not all 100%)
5. Compare to Nebraska study - they had ~20-30% micropolitan across regions

---

## Priority and Next Steps

### High Priority (Immediate)
1. ✓ Download CBSA delineation file (COMPLETED)
2. **Parse CBSA file and update cbsa_classifications.py** (IN PROGRESS)
3. **Re-run micropolitan aggregation**
4. **Verify matching variables now complete**

### Medium Priority (This Session)
1. **Investigate FBI_UCR_KEY validity** - check if it's a data.gov key
2. **Test FBI API with proper authentication format** - try api_key query parameter
3. **Implement fallback for crime data** - bulk download parser if API fails

### Low Priority (Future Session)
1. Obtain new data.gov API key if current key invalid
2. Implement comprehensive FBI UCR data collection
3. Document any API endpoint changes in CLAUDE.md

---

## Files Modified/Created
- `scripts/test_fbi_api_endpoints.py` - FBI API diagnostic script
- `data/raw/cbsa_delineation_2023.xls` - Census CBSA delineation data
- `INVESTIGATION_REPORT.md` - This document

## Files Requiring Updates
- `data/cbsa_classifications.py` - Needs complete 530-county classification
- `API_KEYS_STATUS.md` - Update FBI UCR key status and requirements
- `CLAUDE.md` - Document FBI API issues and resolution

---

## Conclusion

**Issue 1 (FBI API)**: Requires proper data.gov API key or alternative data source. Not blocking for matching variables collection - can use bulk downloads temporarily.

**Issue 2 (Micropolitan)**: **Solvable immediately**. CBSA file downloaded, just needs parsing and integration. This will unblock Matching Variable 2 collection.

**Recommendation**: Fix micropolitan issue first (30 minutes), then investigate FBI API authentication separately.
