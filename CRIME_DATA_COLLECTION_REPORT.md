# Crime Data Collection Report

**Date**: 2025-11-14
**Data Source**: FBI Crime Data Explorer API
**Year**: 2024
**Status**: ✅ Complete for Virginia

---

## Collection Summary

### Virginia Crime Data (2024)

**Coverage**:
- **454 law enforcement agencies** queried via FBI API
- **134 counties** with aggregated data (100.0% coverage)
- **54 regions** (all states) with aggregated data

**Crime Totals**:
- **Violent crimes**: 19,508
- **Property crimes**: 139,811
- **Total crimes**: 159,319

**Top 5 Counties by Violent Crime**:
1. Newport News (City) - 1,378 violent, 4,557 property
2. Prince William - 1,268 violent, 7,267 property
3. Fairfax - 1,207 violent, 17,227 property
4. Norfolk (City) - 1,160 violent, 9,120 property
5. Chesapeake (City) - 895 violent, 4,527 property

---

## Technical Implementation

### ORI Code Format Discovery

**Critical Finding**: The FBI Crime Data Explorer API requires **9-character ORI codes** (ORI9 format), not the 7-character ORI7 codes commonly referenced.

**Example**:
- ❌ ORI7: `VA11700` → Returns `null` actuals
- ✅ ORI9: `VA1170000` → Returns actual crime counts

This was discovered through testing with Norfolk PD:
- Using ORI7 (`VA11700`): Only national-level rates returned, agency actuals were `null`
- Using ORI9 (`VA1170000`): Full agency-level monthly crime counts returned

### Data Sources

**Crosswalk**: Law Enforcement Agency Identifiers Crosswalk, United States, 2012 (ICPSR 35158)
- Maps ORI codes to FIPS county codes
- Includes both ORI7 and ORI9 formats
- Filtered for target states: VA, MD, WV, NC, TN, KY, DC

**FBI API Endpoint**: `https://api.usa.gov/crime/fbi/cde/summarized/agency/{ori}/{offense}`
- Parameters:
  - `{ori}`: 9-character ORI code (ORI9 format)
  - `{offense}`: 'V' for violent crime, 'P' for property crime
  - `from`: Start date (MM-YYYY format)
  - `to`: End date (MM-YYYY format)
  - `API_KEY`: FBI API key

### Aggregation Pipeline

1. **Agency Level**: Raw API responses for each ORI
   - File: `data/processed/crime_agency_data_2024.json`
   - Contains monthly counts by agency

2. **County Level**: Aggregation by FIPS code
   - File: `data/processed/crime_county_data_2024.json`
   - Sums all agencies within each county
   - Includes monthly breakdowns

3. **Regional Level**: Aggregation by region code
   - File: `data/processed/crime_regional_data_2024.json`
   - Aggregates counties to 54 defined regions
   - Totals only (no monthly breakdown at this level)

---

## Data Quality

### Completeness
- ✅ 100% of Virginia counties have crime data
- ✅ All 454 Virginia agencies successfully queried
- ✅ Monthly breakdowns available for all data

### API Response Structure

Successful API responses include:
```json
{
  "offenses": {
    "actuals": {
      "{Agency Name}": {
        "01-2024": 81,
        "02-2024": 59,
        ...
      },
      "{Agency Name} Clearances": { ... }
    },
    "rates": {
      "Virginia": { ... },
      "United States": { ... }
    }
  }
}
```

### Known Limitations

1. **Non-reporting Agencies**: Some small agencies may not report to FBI UCR
   - These return `null` for actuals field
   - County totals only include reporting agencies

2. **Clearance Data**: Clearance rates are included in API response but not currently aggregated

3. **Partial Year Data**: 2024 data may be provisional for recent months

---

## Next Steps

### Immediate
- [x] Collect Virginia crime data
- [ ] Collect data for remaining states (MD, WV, NC, TN, KY, DC)
- [ ] Validate cross-state data consistency

### Future Enhancements
- [ ] Incorporate clearance rates
- [ ] Add crime rate calculations (crimes per 100,000 population)
- [ ] Add temporal analysis (year-over-year changes)
- [ ] Add crime type breakdowns (murder, robbery, burglary, etc.)

---

## Files Generated

### Code
- `src/utils/ori_crosswalk.py` - ORI-to-FIPS mapping (uses ORI9)
- `src/api_clients/fbi_cde_api.py` - FBI API client
- `src/data_collection/collect_crime_data.py` - Collection pipeline

### Data (gitignored - regenerated via API)
- `data/processed/crime_agency_data_2024.json` - Agency-level data
- `data/processed/crime_county_data_2024.json` - County aggregations
- `data/processed/crime_regional_data_2024.json` - Regional aggregations
- `cache/fbi_cde/*.json` - API response cache

### Logs
- `crime_collection_va.log` - Collection run log

---

## Performance

**Collection Time**: ~3-4 minutes for 454 agencies
**API Calls**: 908 total (454 agencies × 2 crime types)
**Rate Limiting**: 100ms delay between requests
**Cache Hit Rate**: N/A (first run)

---

## Validation

**Data Validation Checks**:
- ✅ All counties have non-negative crime counts
- ✅ Monthly totals sum to annual totals
- ✅ Regional totals match sum of member counties
- ✅ Top crime counties match expected urban areas

**Known Good Data Points**:
- Norfolk PD: 1,095 violent crimes in 2024 (81 in Jan, 59 in Feb, 77 in Mar)
- All major VA cities (Norfolk, Virginia Beach, Richmond, etc.) have data
- Urban counties have higher crime counts than rural counties (as expected)

---

*Report generated: 2025-11-14*
*Collection script: `src/data_collection/collect_crime_data.py`*
*API: FBI Crime Data Explorer (https://cde.ucr.cde.fbi.gov/)*
