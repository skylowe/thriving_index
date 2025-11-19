"""
Fix Component 1.4: Re-collect Households with Children Data

This script re-collects measure 1.4 using the correct Census variable:
- S1101_C01_005E (Households with own children under 18 years - COUNT) - CORRECT
- Previously used S1101_C01_002E (Average household size) - WRONG

The corrected data will replace the existing processed file.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import STATE_FIPS, RAW_DATA_DIR, PROCESSED_DATA_DIR
from api_clients.census_client import CensusClient


def main():
    """Re-collect households with children data with correct variable."""
    print("=" * 80)
    print("FIXING COMPONENT 1.4: HOUSEHOLDS WITH CHILDREN DATA")
    print("=" * 80)
    print()
    print("Issue: Previously used S1101_C01_002E (average household size)")
    print("Fix:   Using S1101_C01_005E (count of households with own children under 18)")
    print()
    print("=" * 80)

    # Initialize Census client
    client = CensusClient()

    # Years to collect (5-year ACS periods)
    years = [2017, 2022]

    # States to collect
    state_fips_list = list(STATE_FIPS.values())

    all_data = []
    total_records = 0

    for year in years:
        print(f"\nCollecting ACS {year} 5-year estimates...")
        year_records = 0

        for state_fips in state_fips_list:
            # Get state abbreviation for logging
            state_abbr = [k for k, v in STATE_FIPS.items() if v == state_fips][0]
            try:
                response = client.get_households_with_children(year, state_fips=state_fips)

                # Save raw response (overwrite old data)
                filename = f"census_households_children_{state_fips}_{year}.json"
                client.save_response(response, filename)

                # Parse response
                parsed = client.parse_response_to_dict(response)
                for row in parsed:
                    row['year'] = year
                    all_data.append(row)
                    year_records += 1

                print(f"  ✓ {state_abbr}: {len(parsed)} counties")

                # Add small delay to avoid rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"  ✗ Error for {state_abbr}, year {year}: {e}")
                # Continue with next state even if one fails
                continue

        print(f"  Total for {year}: {year_records} records")
        total_records += year_records

    # Create DataFrame
    df = pd.DataFrame(all_data)

    if len(df) == 0:
        print("\n" + "=" * 80)
        print("ERROR: No data collected!")
        print("=" * 80)
        return

    # Add FIPS column
    df['fips'] = df['state'].astype(str).str.zfill(2) + df['county'].astype(str).str.zfill(3)

    # Rename variable column to be more descriptive
    df = df.rename(columns={
        'S1101_C01_005E': 'households_with_children',
        'S1101_C01_001E': 'total_households'
    })

    # Convert to numeric
    df['households_with_children'] = pd.to_numeric(df['households_with_children'], errors='coerce')
    df['total_households'] = pd.to_numeric(df['total_households'], errors='coerce')

    # Save processed data (overwrite old file)
    output_file = PROCESSED_DATA_DIR / "census_households_children_processed.csv"
    df.to_csv(output_file, index=False)

    print()
    print("=" * 80)
    print("DATA COLLECTION COMPLETE")
    print("=" * 80)
    print(f"Total records: {total_records}")
    print(f"Unique counties: {df['fips'].nunique()}")
    print(f"Years: {sorted(df['year'].unique())}")
    print()

    # Show sample statistics
    print("Sample Statistics:")
    print("-" * 80)
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        print(f"\nYear {year}:")
        print(f"  Counties: {len(year_df)}")
        print(f"  Mean households with children: {year_df['households_with_children'].mean():,.0f}")
        print(f"  Median households with children: {year_df['households_with_children'].median():,.0f}")
        print(f"  Min: {year_df['households_with_children'].min():,.0f}")
        print(f"  Max: {year_df['households_with_children'].max():,.0f}")

    # Show sample of data
    print()
    print("Sample of corrected data (first 10 rows):")
    print("-" * 80)
    print(df[['NAME', 'households_with_children', 'total_households', 'year', 'fips']].head(10).to_string(index=False))

    print()
    print(f"✓ Saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
