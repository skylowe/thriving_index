# FCC Broadband Data Implementation (Measure 6.1)

**Date**: 2025-11-18
**Status**: Implementation complete, authentication issue needs resolution
**Measure**: Component 6, Measure 6.1 - Broadband Internet Access

---

## Summary

I have successfully implemented the infrastructure for collecting FCC Broadband data for Measure 6.1 (Broadband Internet Access). The implementation includes:

1. ✅ FCC API client (`scripts/api_clients/fcc_client.py`)
2. ✅ Configuration updated to include `FCC_BB_KEY`
3. ✅ Data collection function in `collect_component6.py`
4. ✅ Integration with Component 6 summary and workflow

## What Was Implemented

### 1. FCC API Client
**File**: `scripts/api_clients/fcc_client.py`

Features:
- Authentication using `hash_value` and `username` headers
- Methods for fetching available data dates
- County-level broadband availability queries
- Batch processing for multiple counties
- Caching support to minimize API calls
- Filtering by download/upload speeds (default: 100/10 Mbps)

### 2. Configuration Updates
**File**: `scripts/config.py`

- Added `FCC_BB_KEY` to read API key from `.Renviron` or environment variables
- Follows same pattern as other API keys (CENSUS_KEY, BEA_API_KEY, etc.)

### 3. Data Collection Integration
**File**: `scripts/data_collection/collect_component6.py`

- New `collect_broadband_data()` function
- Integrated into main Component 6 workflow
- Error handling with graceful fallback
- Summary statistics and reporting
- County FIPS code collection from Census API

## Current Issue: API Authentication (401 Error)

When testing the FCC API client, we encountered a **401 Unauthorized** error:

```
HTTPError: 401 Client Error: Unauthorized for url:
https://broadbandmap.fcc.gov/api/public/map/listAsOfDates
```

### Possible Causes:

1. **API Key Not Set**: The `FCC_BB_KEY` environment variable may not be set in your `.Renviron` file
2. **Invalid API Key**: The API key format or value might be incorrect
3. **Registration Required**: The FCC API may require specific registration/credentials
4. **API Changes**: The FCC BDC Public Data API authentication method may have changed

### How to Verify Your API Key:

```bash
# Check if FCC_BB_KEY is set in your .Renviron file
grep FCC_BB_KEY .Renviron

# Or check environment variable
echo $FCC_BB_KEY
```

## Alternative Solution: FCC Bulk Data Download

Based on research, the FCC provides **bulk data downloads** as an alternative to the API:

### Data Source
- **URL**: https://broadbandmap.fcc.gov/data-download
- **Format**: CSV files
- **Geographic Level**: County
- **Speed Tier**: Includes "Served" tier (≥100/20 Mbps)
- **Update Frequency**: Twice per year (latest: November 2024)

### Advantages of Bulk Download:
- ✅ More reliable than API
- ✅ No authentication required
- ✅ County-level aggregations already computed
- ✅ Includes 100/20 Mbps service tier
- ✅ Official FCC data matching Nebraska methodology

### Implementation Approach:

If the API continues to have authentication issues, I recommend implementing a bulk download approach similar to how the project handles:
- QCEW data (BLS downloadable files)
- County Health Rankings (Zenodo download)
- USDA Natural Amenities Scale (XLS download)

The implementation would:
1. Download county-level CSV from FCC data portal
2. Filter to our 10 states
3. Extract percentage of locations served at ≥100/10 Mbps
4. Store as processed CSV file

## Next Steps

### Option A: Fix API Authentication (if you have valid API credentials)

1. **Verify API Key**: Ensure `FCC_BB_KEY` is set correctly in `.Renviron`
2. **Check API Documentation**: Review https://www.fcc.gov/sites/default/files/bdc-public-data-api-spec.pdf
3. **Test Authentication**: Run `python scripts/api_clients/fcc_client.py`
4. **Update Client**: Modify authentication if FCC API format has changed

### Option B: Implement Bulk Download (recommended)

1. **Download FCC Data**: Visit https://broadbandmap.fcc.gov/data-download
2. **Select County-Level Data**: Download "County Summary" CSV file
3. **Modify Collection Script**: Update `collect_broadband_data()` to process downloaded file
4. **Filter Speed Tier**: Extract data for ≥100/10 Mbps service tier
5. **Process Data**: Filter to our 10 states and save results

## File Locations

**API Client**:
- `scripts/api_clients/fcc_client.py`

**Collection Script**:
- `scripts/data_collection/collect_component6.py`
- Function: `collect_broadband_data()`

**Configuration**:
- `scripts/config.py` (FCC_BB_KEY variable)
- `.Renviron` (where API key should be stored)

**Data Output** (when working):
- Raw: `data/raw/fcc/fcc_broadband_100_10.csv`
- Processed: `data/processed/fcc_broadband_availability_100_10.csv`

## Testing the Implementation

### Test API Client:
```bash
python scripts/api_clients/fcc_client.py
```

### Run Full Component 6 Collection:
```bash
python scripts/data_collection/collect_component6.py
```

The script will attempt to collect broadband data but will gracefully continue with other measures (6.2-6.6) if broadband collection fails.

## Technical Details

### API Endpoints (Current Implementation):
- **Base URL**: `https://broadbandmap.fcc.gov/api/public/map`
- **List Dates**: `/listAsOfDates`
- **County Data**: `/county?fips={county_fips}&minDownloadSpeed=100&minUploadSpeed=10`

### Authentication Headers:
```python
headers = {
    'hash_value': '<your FCC_BB_KEY>',
    'username': 'api_user',
    'user-agent': 'VATrivingIndex/1.0'
}
```

### Speed Requirements:
- **Minimum Download**: 100 Mbps
- **Minimum Upload**: 10 Mbps
- Matches Nebraska Thriving Index methodology

## References

- **FCC Broadband Data Collection**: https://www.fcc.gov/BroadbandData
- **FCC National Broadband Map**: https://broadbandmap.fcc.gov/
- **Data Download Portal**: https://broadbandmap.fcc.gov/data-download
- **BDC Public Data API Spec**: https://www.fcc.gov/sites/default/files/bdc-public-data-api-spec.pdf
- **Form 477 County Data**: https://www.fcc.gov/form-477-county-data-internet-access-services

---

## Questions or Issues?

If you need help with:
1. **API Authentication**: Check your `FCC_BB_KEY` in `.Renviron`
2. **Bulk Download Implementation**: I can modify the script to use bulk CSV download
3. **Alternative Data Sources**: Let me know if you want to explore other broadband data sources

Let me know which approach you'd like to pursue!
