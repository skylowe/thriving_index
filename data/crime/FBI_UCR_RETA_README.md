# FBI UCR Return A (RETA) Data

## Overview

The FBI Uniform Crime Reporting (UCR) Return A (RETA) data contains monthly crime statistics reported by participating law enforcement agencies across the United States.

## Data Files

### Current Data
- **File**: `reta-2024.zip` (5.9 MB compressed, 193 MB uncompressed)
- **Format**: Fixed-width text file (7,385 bytes per record)
- **Coverage**: 2024 data (most agencies report 12 months)
- **Documentation**: `reta-help.zip` contains field definitions and record layouts

### Data Structure

Each record represents one law enforcement agency's annual crime data:

**Header Information:**
- ORI Code (Originating Agency Identifier) - unique 7-character agency ID
- State code, county code, agency type
- Population served
- Number of months reported

**Monthly Crime Data (12 months):**
Each month contains counts for:
- **Violent crimes**: Murder, manslaughter, rape, robbery, assault
- **Property crimes**: Burglary, larceny, motor vehicle theft
- Detailed breakdowns (e.g., robbery with gun, burglary forcible entry, etc.)
- Offenses unfounded, actual offenses, and clearances

## Data Quality

Based on analysis of 2024 data for target states (VA, MD, WV, NC, TN, KY, DC):

- **Total agencies**: 3,502
- **Full year data (12 months)**: 1,852 agencies (52.9%)
- **Population data available**: 1,853 agencies (52.9%)
- **Agencies reporting crime data**: 1,865 agencies (53.3%)

### State Coverage

| State | Agencies | Population Covered | Violent Crime Rate* | Property Crime Rate* |
|-------|----------|-------------------|---------------------|----------------------|
| DC | 8 | 702,250 | 3,499.6 | 3,693.4 |
| KY | 761 | 4,587,273 | 995.3 | 1,350.2 |
| MD | 228 | 6,325,943 | 1,382.1 | 2,029.8 |
| NC | 843 | 11,022,249 | 1,300.7 | 1,868.5 |
| TN | 614 | 7,198,775 | 1,977.9 | 2,041.6 |
| VA | 499 | 8,824,093 | 1,204.3 | 1,566.8 |
| WV | 549 | 1,771,420 | 841.4 | 1,028.7 |

*Rate per 100,000 population

## Data Processing

### Parser Implementation

The `FBIUCRReturnAParser` class (`src/parsers/fbi_ucr_parser.py`) handles:

1. **Extraction**: Reads fixed-width format records
2. **Parsing**: Extracts crime counts, population, and metadata
3. **Aggregation**: Sums monthly data to annual totals
4. **Filtering**: Selects only target states

### Key Features

- **Handles negative values**: RETA uses alphabetic codes for negative numbers (rare but documented)
- **Flexible aggregation**: Can aggregate by agency, county, or region
- **Data validation**: Checks record length and field formats

### Crime Metrics

**Violent Crime** = Murder + Manslaughter + Rape + Robbery + Assault

**Property Crime** = Burglary + Larceny + Motor Vehicle Theft

These align with the Nebraska Thriving Index methodology (measures 6.4 and 6.5).

## Next Steps for Thriving Index

1. **ORI-to-FIPS Mapping**: Create mapping from ORI codes to county FIPS codes
   - ORI codes identify individual agencies (city police, county sheriffs, etc.)
   - Need to aggregate all agencies in a county to get county-level crime data
   - Multiple agencies per county is common (city PDs + county sheriff)

2. **County-Level Aggregation**:
   - Sum all agency crime counts within each county
   - Use Census population data (more complete than RETA population field)
   - Calculate crime rates per 100,000 population

3. **Regional Aggregation**:
   - Aggregate county-level data to 54 regional groupings
   - Population-weighted averaging for rates

4. **Standardization**:
   - Calculate z-scores for violent and property crime rates
   - Invert scores (lower crime = higher index value)
   - Apply Nebraska's standardization formula: `100 + 100 * (μ - X) / σ`

## Data Limitations

### Coverage Gaps

- **Not all jurisdictions report**: UCR participation is voluntary
- **Partial year data**: ~47% of agencies report < 12 months
- **Population gaps**: Many agencies don't report population served

### Agency Complexity

- **Multiple agencies per area**: Cities may have police department + county sheriff + university police + transit police
- **Overlapping jurisdictions**: Some crimes may be reported by multiple agencies
- **State police**: Report statewide but serve specific areas (highways, rural areas)

### Solutions

1. **Use Census population data** instead of RETA population fields
2. **Aggregate all agencies by county** using ORI-to-FIPS mapping
3. **Document coverage**: Track which counties have complete vs partial data
4. **Compare to state statistics**: Validate against published state crime reports

## References

- **FBI Crime Data Explorer**: https://cde.ucr.cde.fbi.gov/
- **UCR Documentation**: https://www.fbi.gov/how-we-can-help-you/more-fbi-services-and-information/ucr
- **NACJD Data Archive**: https://www.icpsr.umich.edu/web/pages/NACJD/index.html

## Testing

Test the parser:

```bash
python scripts/test_ucr_parser.py
```

This will:
- Extract and parse the 2024 RETA data
- Show sample Virginia agencies
- Display data quality metrics
- Calculate state-level crime rates

## File Format Details

See `reta-help/help/Ret A Rec Descrip.pdf` for complete field definitions and positions.

Key field positions (1-indexed):
- Positions 1-3: Identifier and state code
- Positions 4-10: ORI code
- Positions 11-12: Agency group/type
- Positions 42-43: Number of months reported
- Positions 45-53: Population
- Positions 306-895: Monthly crime data (12 months × 590 bytes)

Within each month block:
- Card 0 (offset 17): Unfounded offenses
- Card 1 (offset 157): Actual offenses (used for crime rates)
- Card 2: Clearances
- Card 3: Clearances under age 18
