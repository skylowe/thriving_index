"""
Test Regional Aggregation with Real API Data

This script demonstrates the full workflow:
1. Fetch county-level data from Census API
2. Aggregate to multi-county regions
3. Validate aggregation results
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pandas as pd
from src.api_clients.census_api import CensusAPI
from src.processing.regional_aggregator import RegionalAggregator, validate_aggregation
from src.utils.logging_setup import setup_logger

logger = setup_logger('test_regional_aggregation')

print("=" * 80)
print("REGIONAL AGGREGATION TEST - Real Census Data")
print("=" * 80)

# Initialize clients
census = CensusAPI()
aggregator = RegionalAggregator()

# Test 1: Fetch Virginia county-level data
print("\nStep 1: Fetching Virginia county data from Census API...")
print("-" * 80)

try:
    # Get population and median household income for all Virginia localities
    county_data = census.get_median_household_income(year=2022, state='51')

    if county_data:
        # Convert to DataFrame
        df = pd.DataFrame(county_data)

        # Build FIPS codes (state + county code)
        df['fips'] = '51' + df['county'].astype(str).str.zfill(3)

        # Rename variable codes to friendly names
        df = df.rename(columns={'B19013_001E': 'median_household_income'})

        # Show sample
        print(f"✓ Retrieved data for {len(df)} Virginia localities")
        print("\nSample county data:")
        print(df[['fips', 'NAME', 'median_household_income']].head(10))

        # Step 2: Aggregate to regions
        print("\n" + "=" * 80)
        print("Step 2: Aggregating to multi-county regions...")
        print("-" * 80)

        # For median income, we need population weights
        # First get population data
        pop_data = census.get_population(year=2022, state='51')

        if pop_data:
            pop_df = pd.DataFrame(pop_data)
            pop_df['fips'] = '51' + pop_df['county'].astype(str).str.zfill(3)

            # Rename variable codes to friendly names
            pop_df = pop_df.rename(columns={'B01001_001E': 'population'})

            # Merge population with income data
            merged = df.merge(
                pop_df[['fips', 'population']],
                on='fips',
                how='left'
            )

            # Clean up - convert to numeric
            merged['median_household_income'] = pd.to_numeric(
                merged['median_household_income'],
                errors='coerce'
            )
            merged['population'] = pd.to_numeric(
                merged['population'],
                errors='coerce'
            )

            # Aggregate median income (intensive - population-weighted)
            print("\nAggregating median household income (population-weighted)...")
            regional_income = aggregator.aggregate_to_regions(
                county_data=merged,
                measure_type='intensive',
                value_column='median_household_income',
                fips_column='fips',
                weight_column='population'
            )

            # Add metadata
            regional_income = aggregator.add_region_metadata(regional_income)

            # Sort for display
            regional_income = regional_income.sort_values(
                'median_household_income',
                ascending=False
            ).reset_index(drop=True)

            print(f"\n✓ Aggregated to {len(regional_income)} Virginia regions")
            print("\nVirginia Regional Median Household Income (2022):")
            print(regional_income[[
                'region_code', 'region_name', 'median_household_income',
                'num_counties', 'total_weight'
            ]])

            # Aggregate population (extensive - sum)
            print("\n" + "-" * 80)
            print("Aggregating population (sum)...")
            regional_pop = aggregator.aggregate_to_regions(
                county_data=merged,
                measure_type='extensive',
                value_column='population',
                fips_column='fips'
            )

            regional_pop = aggregator.add_region_metadata(regional_pop)

            # Sort for display
            regional_pop = regional_pop.sort_values(
                'population',
                ascending=False
            ).reset_index(drop=True)

            print(f"\n✓ Aggregated to {len(regional_pop)} Virginia regions")
            print("\nVirginia Regional Population (2022):")
            print(regional_pop[[
                'region_code', 'region_name', 'population', 'num_counties'
            ]])

            # Step 3: Validate
            print("\n" + "=" * 80)
            print("Step 3: Validation")
            print("-" * 80)

            validation = validate_aggregation(
                county_data=merged[merged['population'].notna()],
                regional_data=regional_pop,
                measure_column='population',
                measure_type='extensive'
            )

            if validation['valid']:
                print("✓ Population aggregation validated successfully")
            else:
                print("✗ Validation failed")

            for warning in validation['warnings']:
                print(f"  ⚠ {warning}")
            for error in validation['errors']:
                print(f"  ✗ {error}")

            # Summary statistics
            print("\n" + "=" * 80)
            print("Summary Statistics")
            print("-" * 80)

            total_pop = regional_pop['population'].sum()
            avg_income = (
                (regional_pop['population'] * regional_income['median_household_income']).sum() /
                total_pop
            )

            print(f"\nTotal Virginia Population: {total_pop:,.0f}")
            print(f"Population-Weighted Avg Median Income: ${avg_income:,.0f}")
            print(f"\nHighest Income Region: {regional_income.iloc[0]['region_name']}")
            print(f"  ${regional_income.iloc[0]['median_household_income']:,.0f}")
            print(f"\nLowest Income Region: {regional_income.iloc[-1]['region_name']}")
            print(f"  ${regional_income.iloc[-1]['median_household_income']:,.0f}")

            print(f"\nLargest Region: {regional_pop.iloc[0]['region_name']}")
            print(f"  {regional_pop.iloc[0]['population']:,.0f} people")

        else:
            print("✗ Failed to fetch population data")

    else:
        print("✗ Failed to fetch income data")

except Exception as e:
    logger.error(f"Test failed: {str(e)}", exc_info=True)
    print(f"✗ Error: {str(e)}")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
