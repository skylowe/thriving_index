"""
Fix housing pre-1960 data by using correct Census table.

Issue: DP04 profile table mixes counts and percentages.
Solution: Use B25034 (Year Structure Built) detailed table which has all counts.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api_clients.census_client import CensusClient
import pandas as pd
import json


# State FIPS codes for our 10 states
STATE_FIPS = {
    'Virginia': '51',
    'Pennsylvania': '42',
    'Maryland': '24',
    'Delaware': '10',
    'West Virginia': '54',
    'Kentucky': '21',
    'Tennessee': '47',
    'North Carolina': '37',
    'South Carolina': '45',
    'Georgia': '13'
}


def collect_housing_age_corrected(year=2022):
    """
    Collect housing age data using B25034 table (all counts).

    B25034 variables:
    - B25034_001E: Total housing units
    - B25034_010E: Built 1940 to 1949
    - B25034_011E: Built 1939 or earlier
    - B25034_009E: Built 1950 to 1959
    """
    print("="*80)
    print(f"FIXING HOUSING PRE-1960 DATA - Using B25034 Table")
    print("="*80)

    census_client = CensusClient()
    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        print(f"\n  Fetching {state_name} (FIPS {state_fips})...")

        # Use B25034 table - Year Structure Built
        url = f"{census_client.base_url}/{year}/acs/acs5"

        variables = [
            'NAME',
            'B25034_001E',  # Total housing units
            'B25034_011E',  # Built 1939 or earlier
            'B25034_010E',  # Built 1940 to 1949
            'B25034_009E',  # Built 1950 to 1959
        ]

        params = {
            'get': ','.join(variables),
            'for': 'county:*',
            'in': f'state:{state_fips}',
            'key': census_client.api_key
        }

        try:
            response = census_client._make_request(url, params)

            # Save raw response
            raw_dir = Path('data/raw/census')
            raw_dir.mkdir(parents=True, exist_ok=True)
            filename = f"census_housing_age_b25034_{year}_{state_name.replace(' ', '_')}.json"

            with open(raw_dir / filename, 'w') as f:
                json.dump(response, f, indent=2)

            # Parse response
            if response and len(response) > 1:
                headers = response[0]
                for row in response[1:]:
                    all_data.append(dict(zip(headers, row)))
                print(f"    ✓ Retrieved {len(response)-1} counties")
            else:
                print(f"    ⚠️  No data returned")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    print(f"\n  Total records collected: {len(all_data)}")

    # Process data
    df = pd.DataFrame(all_data)

    print("\n  Processing data...")
    df['total_units'] = pd.to_numeric(df['B25034_001E'], errors='coerce')
    df['built_1939_earlier'] = pd.to_numeric(df['B25034_011E'], errors='coerce')
    df['built_1940_1949'] = pd.to_numeric(df['B25034_010E'], errors='coerce')
    df['built_1950_1959'] = pd.to_numeric(df['B25034_009E'], errors='coerce')

    # Calculate units pre-1960
    df['units_pre_1960'] = (
        df['built_1939_earlier'] +
        df['built_1940_1949'] +
        df['built_1950_1959']
    )

    # Calculate percentage
    df['pct_pre_1960'] = (df['units_pre_1960'] / df['total_units'] * 100)

    # Check for data quality
    invalid = df[df['pct_pre_1960'] > 100]
    if len(invalid) > 0:
        print(f"\n  ⚠️  WARNING: {len(invalid)} counties still have >100%!")
        print(invalid[['NAME', 'total_units', 'units_pre_1960', 'pct_pre_1960']].head())
        return None

    print(f"\n  ✓ Data quality check passed: All percentages 0-100%")
    print(f"    Min: {df['pct_pre_1960'].min():.2f}%")
    print(f"    Mean: {df['pct_pre_1960'].mean():.2f}%")
    print(f"    Max: {df['pct_pre_1960'].max():.2f}%")

    # Save processed data
    output_file = Path('data/processed/census_housing_pre1960_2022.csv')
    df[['state', 'county', 'NAME', 'pct_pre_1960', 'total_units', 'units_pre_1960']].to_csv(
        output_file, index=False
    )

    print(f"\n✓ Saved corrected data: {output_file}")
    print(f"  Records: {len(df)}")

    return df


def main():
    """Run housing data correction."""
    # Backup old file
    old_file = Path('data/processed/census_housing_pre1960_2022.csv')
    if old_file.exists():
        backup_file = Path('data/processed/census_housing_pre1960_2022_BACKUP.csv')
        old_file.rename(backup_file)
        print(f"✓ Backed up old file to: {backup_file}\n")

    # Collect corrected data
    df = collect_housing_age_corrected(year=2022)

    if df is not None:
        print("\n" + "="*80)
        print("HOUSING DATA FIX COMPLETE")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("HOUSING DATA FIX FAILED - Check errors above")
        print("="*80)


if __name__ == '__main__':
    main()
