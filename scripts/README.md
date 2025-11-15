# Virginia Thriving Index - Data Collection Scripts

## Overview

This directory contains Python scripts for collecting data from various APIs to build the Virginia Thriving Index. All scripts are designed to work cross-platform (Linux/Windows) and use API keys stored in the `.Renviron` file in the project root.

## Structure

```
scripts/
├── config.py                    # Configuration and API key management
├── api_clients/                 # API client modules
│   ├── bea_client.py           # BEA Regional API client
│   ├── bls_client.py           # BLS QCEW API client
│   └── census_client.py        # Census ACS API client
├── data_collection/             # Data collection scripts by component
│   └── collect_component1.py   # Component Index 1 data collection
├── processing/                  # Data processing scripts (future)
└── analysis/                    # Analysis scripts (future)
```

## Prerequisites

1. **Python 3.x** installed
2. **Required Python packages:**
   ```bash
   pip install requests pandas
   ```
3. **API keys** configured in `.Renviron` file at project root:
   - `CENSUS_KEY` - Census API key
   - `BEA_API_KEY` - BEA API key
   - `BLS_API_KEY` - BLS API key

## Configuration

The `config.py` module handles:
- Loading API keys from `.Renviron`
- Project paths and directory structure
- State FIPS codes for all 10 states
- API endpoints and request settings

### State Coverage

Data is collected for all counties in these 10 states:
- Virginia (VA)
- Pennsylvania (PA)
- Maryland (MD)
- Delaware (DE)
- West Virginia (WV)
- Kentucky (KY)
- Tennessee (TN)
- North Carolina (NC)
- South Carolina (SC)
- Georgia (GA)

## API Clients

### BEA Client (`api_clients/bea_client.py`)

Bureau of Economic Analysis Regional API client for:
- CAINC5 table (Personal Income by Major Component)
- Employment data (Line Code 10)
- Dividends, Interest, and Rent income (Line Code 40)

**Example usage:**
```python
from api_clients.bea_client import BEAClient

client = BEAClient()
data = client.get_employment_data('2020,2021,2022', state_fips_list=['51', '42'])
```

### BLS Client (`api_clients/bls_client.py`)

Bureau of Labor Statistics QCEW API client for:
- Private sector employment
- Private sector wages
- County-level data by industry

**Example usage:**
```python
from api_clients.bls_client import BLSClient

client = BLSClient()
data = client.get_county_data('51', '001', 2020, 2022, data_types=['employment', 'wages'])
```

### Census Client (`api_clients/census_client.py`)

Census American Community Survey API client for:
- Household demographics
- Education attainment
- Poverty rates
- Housing values

**Example usage:**
```python
from api_clients.census_client import CensusClient

client = CensusClient()
data = client.get_households_with_children(2022, state_fips='51')
```

## Component Index 1 Data Collection

The `collect_component1.py` script collects all 5 measures for the Growth Index:

### Measures Collected

1. **Growth in Total Employment** (BEA CAINC5, Line 10)
   - Time period: 2020-2022
   - All counties in 10 states

2. **Private Employment** (BLS QCEW)
   - Time period: 2020-2022 annual average
   - All counties in 10 states

3. **Growth in Private Wages Per Job** (BLS QCEW)
   - Time period: 2020-2022
   - Requires both employment and wages data

4. **Growth in Households with Children** (Census ACS Table S1101)
   - Time periods: 2013-2017 and 2018-2022 (5-year estimates)
   - All counties in 10 states

5. **Growth in Dividends, Interest, and Rent Income** (BEA CAINC5, Line 40)
   - Time period: 2020-2022
   - All counties in 10 states

### Running the Collection Script

```bash
# From project root
python3 scripts/data_collection/collect_component1.py
```

The script will:
1. Collect BEA employment data (~315 records per year for all states)
2. Collect BEA DIR income data
3. Collect Census household data for 2 time periods
4. **Ask permission** before collecting BLS QCEW data (takes longer due to rate limits)

### Output Files

**Raw Data** (saved to `data/raw/[source]/`):
- `bea_employment_2020_2022.json` - BEA employment raw response
- `bea_dir_income_2020_2022.json` - BEA DIR income raw response
- `census_households_children_[STATE]_[YEAR].json` - Census household data per state/year
- `bls_qcew_employment_[STATE]_batch[N]_2020_2022.json` - BLS employment data by state
- `bls_qcew_wages_[STATE]_batch[N]_2020_2022.json` - BLS wages data by state

**Processed Data** (saved to `data/processed/`):
- `bea_employment_processed.csv` - Cleaned BEA employment data
- `bea_dir_income_processed.csv` - Cleaned BEA DIR income data
- `census_households_children_processed.csv` - Cleaned Census household data
- `bls_qcew_employment_processed.csv` - Cleaned BLS employment data
- `bls_qcew_wages_processed.csv` - Cleaned BLS wages data
- `component1_collection_summary.json` - Collection summary and metadata

## Testing API Clients

Each API client has built-in tests. Run them individually:

```bash
# Test BEA client
python3 scripts/api_clients/bea_client.py

# Test BLS client
python3 scripts/api_clients/bls_client.py

# Test Census client
python3 scripts/api_clients/census_client.py

# Test configuration
python3 scripts/config.py
```

## Data Collection Best Practices

1. **Raw Data Preservation**: All raw API responses are saved for audit trail and re-processing
2. **Rate Limiting**: Clients implement delays between requests to respect API rate limits
3. **Error Handling**: Retry logic with exponential backoff for failed requests
4. **Batch Processing**: BLS data is collected in batches of 50 series (API limit)
5. **Progress Reporting**: Real-time progress output during collection

## Troubleshooting

### API Key Issues
```bash
# Test if API keys are loaded correctly
python3 scripts/config.py
```

### API Connection Issues
- Check internet connection
- Verify API keys are valid
- Check API status pages:
  - BEA: https://apps.bea.gov/api/
  - BLS: https://www.bls.gov/developers/
  - Census: https://www.census.gov/data/developers.html

### BLS QCEW Data Taking Too Long
- The BLS API has rate limits
- Consider running BLS collection separately or overnight
- Data is saved in batches, so partial progress is preserved

## Next Steps

After Component 1 data is collected:
1. Validate data quality and coverage
2. Calculate growth rates for each measure
3. Proceed to Component Index 2 data collection
4. Eventually: Aggregate counties into regions and calculate index scores

## References

- API_MAPPING.md - Complete variable mapping for all 47 measures
- PROJECT_PLAN.md - Project plan and status tracking
- CLAUDE.md - Project knowledge base and methodology
