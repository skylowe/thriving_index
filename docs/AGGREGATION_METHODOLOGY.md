# Data Aggregation Methodology

## Virginia Thriving Index - Regional Aggregation Documentation

**Date**: 2025-11-14
**Purpose**: Document the methodology for aggregating county-level data to multi-county regional groupings

---

## Overview

The Virginia Thriving Index uses **multi-county regional groupings** rather than individual counties as the unit of analysis. This approach:

1. **Aligns with Nebraska methodology**: Nebraska's original study used 8 multi-county regions
2. **Creates comparable units**: Regions of similar population size are more comparable than mixing large counties with tiny cities
3. **Improves data quality**: Reduces issues with small sample sizes in ACS estimates
4. **Enables meaningful peer matching**: Regions can be matched based on economic and demographic characteristics

---

## Regional Structure

### Total Regions: 54

- **Virginia**: 11 regions (133 localities → 11 regions)
- **Maryland**: 6 regions (24 jurisdictions → 6 regions)
- **West Virginia**: 7 regions (55 counties → 7 regions)
- **North Carolina**: 10 regions (100 counties → 10 regions)
- **Tennessee**: 9 regions (95 counties → 9 regions)
- **Kentucky**: 10 regions (120 counties → 10 regions)
- **District of Columbia**: 1 region (special case - single jurisdiction)

### Region Characteristics

Regions are grouped based on:
- **Geographic proximity**: Contiguous counties
- **Economic characteristics**: Similar industries, employment patterns
- **Population density**: Urban vs. rural vs. mixed
- **MSA/micropolitan status**: Metro areas, micropolitan areas, non-metro
- **Natural geographic divisions**: Mountain regions, coastal areas, valleys

---

## Aggregation Types

There are two fundamental types of measures that require different aggregation methods:

### 1. Extensive Measures (Totals)

**Definition**: Measures that represent absolute quantities that can be summed.

**Aggregation Method**: **Simple Sum**

**Formula**:
```
Regional_Value = Σ(County_Values)
```

**Examples**:
- Total population
- Number of employed persons
- Number of business establishments
- Total housing units
- Number of births/deaths

**Implementation**:
```python
regional_value = county_data.groupby('region_code')['measure'].sum()
```

**Rationale**: For totals, the regional value is simply the sum of all constituent county values. For example, if County A has 100,000 people and County B has 50,000 people, the region's total population is 150,000.

---

### 2. Intensive Measures (Rates, Averages, Percentages)

**Definition**: Measures that represent rates, ratios, percentages, or per-capita values that cannot be simply summed.

**Aggregation Method**: **Population-Weighted Average**

**Formula**:
```
Regional_Rate = Σ(County_Rate × County_Weight) / Σ(County_Weight)

Where:
  County_Weight = typically population or relevant denominator
```

**Detailed Calculation**:
```
1. For each county:
   weighted_value = county_rate × county_population

2. For the region:
   sum_weighted_values = Σ(weighted_values)
   sum_weights = Σ(county_population)

   regional_rate = sum_weighted_values / sum_weights
```

**Examples**:
- Median household income
- Poverty rate (%)
- Unemployment rate (%)
- Bachelor's degree attainment (%)
- Per capita income
- Crime rate (per 100,000)

**Implementation**:
```python
# Calculate weighted values
df['weighted_value'] = df['rate'] * df['population']

# Aggregate by region
regional = df.groupby('region_code').agg({
    'weighted_value': 'sum',
    'population': 'sum'
})

# Calculate weighted average
regional['rate'] = regional['weighted_value'] / regional['population']
```

**Rationale**: Rates and percentages must be weighted by the population (or relevant denominator) to avoid giving disproportionate influence to small counties.

**Example**:
```
County A: Population 100,000, Poverty Rate 10%
County B: Population 10,000, Poverty Rate 30%

INCORRECT (simple average):
  Regional Poverty Rate = (10% + 30%) / 2 = 20%

CORRECT (population-weighted):
  Regional Poverty Rate = (10% × 100,000 + 30% × 10,000) / (100,000 + 10,000)
                        = (10,000 + 3,000) / 110,000
                        = 11.8%
```

This is correct because County A has 10× the population of County B, so its rate should have more influence on the regional average.

---

## Specific Measure Aggregation Guidelines

### Demographics

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| Total Population | Extensive | Sum | N/A |
| Population by Age Group | Extensive | Sum | N/A |
| Median Age | Intensive | Population-weighted | Population |
| Population Density | Intensive | Recalculate (pop/area) | N/A |

### Income & Poverty

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| Median Household Income | Intensive | Population-weighted | Population |
| Per Capita Income | Intensive | Population-weighted | Population |
| Poverty Rate (%) | Intensive | Population-weighted | Poverty universe population |
| Gini Coefficient | Intensive | Population-weighted | Population |

### Education

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| High School Graduation Rate (%) | Intensive | Population-weighted | Population 25+ |
| Bachelor's Degree (%) | Intensive | Population-weighted | Population 25+ |
| Total Enrolled Students | Extensive | Sum | N/A |
| Student-Teacher Ratio | Intensive | Enrollment-weighted | Student enrollment |

### Employment

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| Total Employment | Extensive | Sum | N/A |
| Unemployment Rate (%) | Intensive | Labor-force-weighted | Labor force size |
| Labor Force Participation (%) | Intensive | Population-weighted | Population 16+ |
| Employment by Industry | Extensive | Sum | N/A |
| Median Wage | Intensive | Employment-weighted | Number of employees |

### Health

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| Life Expectancy | Intensive | Population-weighted | Population |
| Infant Mortality Rate | Intensive | Birth-weighted | Number of births |
| Uninsured Rate (%) | Intensive | Population-weighted | Population |
| Physicians per 100k | Intensive | Recalculate | N/A |

### Crime

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| Violent Crime Rate (per 100k) | Intensive | Population-weighted | Population |
| Property Crime Rate (per 100k) | Intensive | Population-weighted | Population |
| Total Crimes | Extensive | Sum | N/A |

### Business & Economy

| Measure | Type | Aggregation Method | Weight |
|---------|------|-------------------|--------|
| Number of Establishments | Extensive | Sum | N/A |
| Business Formation Rate | Intensive | Establishment-weighted | Number of establishments |
| GDP | Extensive | Sum | N/A |
| GDP per Capita | Intensive | Recalculate (GDP/pop) | N/A |

---

## Validation Procedures

### 1. Total Consistency Check (Extensive Measures)

For extensive measures, the sum of regional values should equal the sum of county values:

```
Σ(Regional_Values) = Σ(County_Values)
```

**Tolerance**: ±0.01% difference (accounting for rounding)

**Implementation**:
```python
county_total = county_data['value'].sum()
regional_total = regional_data['value'].sum()
diff_pct = abs(county_total - regional_total) / county_total * 100

assert diff_pct < 0.01, f"Total mismatch: {diff_pct:.4f}%"
```

### 2. Weighted Average Validation (Intensive Measures)

Verify that weighted averages are calculated correctly:

```python
# Manual calculation
manual_avg = (county_data['value'] * county_data['weight']).sum() / county_data['weight'].sum()

# Compare to regional value
assert abs(manual_avg - regional_value) < 0.01
```

### 3. Missing Data Check

Track and report unmapped FIPS codes:

```python
unmapped = county_data[county_data['region_code'].isna()]
print(f"Warning: {len(unmapped)} localities unmapped")
print(f"Unmapped population: {unmapped['population'].sum():,}")
```

### 4. Range Validation

Ensure regional values fall within reasonable ranges:

```python
assert regional_data['poverty_rate'].between(0, 100).all()
assert regional_data['population'] > 0
```

---

## Data Quality Considerations

### Small Sample Sizes

**Issue**: ACS 5-year estimates for small counties may have high margins of error.

**Solution**: Multi-county regions provide larger sample sizes, improving estimate reliability.

**Example**: A county with 5,000 people may have a median income estimate with ±$10,000 margin of error. A region with 500,000 people will have much smaller margins.

### Suppressed Data

**Issue**: Census suppresses some estimates for small geographies.

**Handling**:
- Regional aggregation reduces suppression
- If a county has suppressed data, exclude from that measure (not from region)
- Document suppression rates by measure

### Outliers

**Issue**: Very small or very large counties can skew averages.

**Handling**:
- Population weighting naturally reduces influence of outliers
- Consider robust alternatives (median instead of mean) if needed
- Document outliers in regional composition

### Missing FIPS Codes

**Issue**: Some localities may not be mapped to regions yet.

**Current Status**: 519 of 530 localities mapped (97.9%)

**Handling**:
- Investigate unmapped codes
- Add to appropriate regions or document exclusion rationale
- Report unmapped population in validation

---

## Implementation Details

### Module: `src/processing/regional_aggregator.py`

**Class**: `RegionalAggregator`

**Key Methods**:

1. **`aggregate_to_regions()`**
   - Inputs: county data DataFrame, measure type, value column, FIPS column, optional weight column
   - Process: Maps FIPS codes to regions, groups by region, applies appropriate aggregation
   - Outputs: Regional DataFrame with aggregated values

2. **`add_region_metadata()`**
   - Adds region names, state codes, county counts to aggregated data

3. **`validate_aggregation()`**
   - Performs validation checks on aggregated data
   - Returns validation report with warnings and errors

### Usage Example

```python
from src.processing.regional_aggregator import RegionalAggregator

aggregator = RegionalAggregator()

# Extensive measure (population)
regional_pop = aggregator.aggregate_to_regions(
    county_data=county_df,
    measure_type='extensive',
    value_column='population',
    fips_column='fips'
)

# Intensive measure (median income)
regional_income = aggregator.aggregate_to_regions(
    county_data=county_df,
    measure_type='intensive',
    value_column='median_household_income',
    fips_column='fips',
    weight_column='population'
)
```

---

## Data Collection Workflow

### Module: `src/data_collection/regional_data_collector.py`

**Class**: `RegionalDataCollector`

**Workflow**:

1. **Initialize API Clients**
   - Census API, BEA API, BLS API
   - Initialize Regional Aggregator

2. **Fetch County-Level Data**
   - Loop through all 7 states (VA, MD, WV, NC, TN, KY, DC)
   - Call appropriate API methods
   - Build FIPS codes for each record

3. **Combine State Data**
   - Concatenate all state DataFrames
   - Convert columns to appropriate numeric types
   - Handle DC special case

4. **Aggregate to Regions**
   - Call RegionalAggregator with appropriate method (extensive/intensive)
   - Add region metadata

5. **Save Results**
   - Export regional data to CSV files
   - Format: `{measure_name}_{year}_regional.csv`
   - Location: `data/regional_data/`

### Example Output Files

```
data/regional_data/
├── population_2022_regional.csv
├── median_household_income_2022_regional.csv
├── poverty_rate_2022_regional.csv
└── ... (additional measures)
```

### CSV Format

```csv
region_code,value,num_counties,total_weight,region_name,state
VA-8,2770137,11,,Northern Virginia,VA
VA-10,1746362,16,,Hampton Roads,VA
...
```

---

## Future Enhancements

### 1. Time-Series Data

**Current**: Single year (2022)
**Future**: Multiple years to track trends

**Consideration**: Ensure consistent regional definitions over time

### 2. Confidence Intervals

**Current**: Point estimates only
**Future**: Propagate ACS margins of error to regional estimates

**Formula** (for weighted averages):
```
Regional_MOE = sqrt(Σ(MOE_i² × weight_i²)) / Σ(weight_i)
```

### 3. Alternative Weighting Schemes

**Current**: Population weighting for most intensive measures
**Future**: Consider measure-specific weights

**Examples**:
- Crime rates: Weight by reporting population
- Education: Weight by school-age population
- Health: Weight by age-adjusted population

### 4. Spatial Statistics

**Current**: Simple aggregation only
**Future**: Account for spatial autocorrelation

**Methods**:
- Moran's I for spatial clustering
- Geographic weighting by contiguity

---

## References

### Methodology Sources

- **Nebraska Thriving Index 2022**: Original methodology document
- **Census Bureau ACS Documentation**: [https://www.census.gov/programs-surveys/acs/](https://www.census.gov/programs-surveys/acs/)
- **BEA Regional Accounts Methodology**: [https://www.bea.gov/regional](https://www.bea.gov/regional)
- **Population-Weighted Averages**: Standard statistical practice for aggregating rates

### Related Documentation

- `PROJECT_PLAN.md`: Overall project roadmap
- `API_MAPPING.md`: Detailed mapping of measures to API sources
- `CLAUDE.md`: Development notes and decisions
- `data/regional_groupings.py`: Authoritative regional definitions

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-11-14 | Initial documentation of aggregation methodology | Claude |
| 2025-11-14 | Implemented regional aggregator module | Claude |
| 2025-11-14 | Fixed Virginia regional mappings (added 15 missing counties) | Claude |
| 2025-11-14 | Completed data collection workflow for Census measures | Claude |

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-14
**Validation Status**: All Virginia localities mapped, validation passing (0.000% diff)
