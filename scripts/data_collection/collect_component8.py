"""
Component Index 8: Social Capital - Data Collection Script

Collects Measure 8.1 for Component Index 8 for all counties in 10 states:
8.1 Number of 501(c)(3) Organizations Per 1,000 Persons (IRS EO BMF)

States: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
"""

import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import STATE_FIPS, RAW_DATA_DIR, PROCESSED_DATA_DIR
from api_clients.irs_client import IRSExemptOrgClient
from api_clients.census_client import CensusClient


# State names from STATE_FIPS mapping (imported from config)
# STATE_FIPS keys are already the 2-letter abbreviations we need for IRS downloads


def collect_501c3_organizations(irs_client, state_fips_list):
    """
    Collect 501(c)(3) organizations for all states (Measure 8.1).

    Args:
        irs_client: IRSExemptOrgClient instance
        state_fips_list: List of state FIPS codes to collect

    Returns:
        dict: Dictionary mapping county FIPS to organization count
    """
    print("\nCollecting IRS 501(c)(3) Organizations (Measure 8.1)...")
    print("-" * 60)

    # Download ZIP-to-FIPS crosswalk once
    print("Loading ZIP-to-FIPS crosswalk...")
    irs_client.get_zip_to_fips_crosswalk()

    all_county_counts = {}
    total_orgs = 0
    total_mapped = 0
    total_unmapped = 0

    for state_abbr, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"\n  Fetching {state_abbr} (FIPS {state_fips})...")
        try:
            # Get 501(c)(3) organizations for this state
            orgs = irs_client.get_501c3_organizations(state_abbr, cache=True)
            total_orgs += len(orgs)

            # Save raw JSON
            irs_client.save_organizations_json(orgs, state_abbr)

            # Map to counties
            county_orgs = irs_client.map_organizations_to_counties(orgs)

            # Count organizations by county
            for fips, org_list in county_orgs.items():
                if fips not in all_county_counts:
                    all_county_counts[fips] = 0
                all_county_counts[fips] += len(org_list)

            # Track mapping statistics
            mapped = sum(len(org_list) for org_list in county_orgs.values())
            unmapped = len(orgs) - mapped
            total_mapped += mapped
            total_unmapped += unmapped

            print(f"    ✓ Retrieved {len(orgs)} organizations")
            print(f"    ✓ Mapped to {len(county_orgs)} counties ({mapped} orgs)")
            print(f"    ⚠ Unmapped: {unmapped} orgs")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print(f"Total 501(c)(3) organizations collected: {total_orgs:,}")
    if total_orgs > 0:
        print(f"Total organizations mapped: {total_mapped:,} ({total_mapped/total_orgs*100:.1f}%)")
        print(f"Total organizations unmapped: {total_unmapped:,} ({total_unmapped/total_orgs*100:.1f}%)")
    else:
        print(f"Total organizations mapped: {total_mapped:,}")
        print(f"Total organizations unmapped: {total_unmapped:,}")
    print(f"Total counties with organizations: {len(all_county_counts)}")
    print(f"{'='*60}\n")

    return all_county_counts


def get_population_data(census_client, year, state_fips_list):
    """
    Get population data from Census ACS for calculating per capita metrics.

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with population data by county FIPS
    """
    print(f"\nCollecting Census ACS {year} Population Data...")
    print("-" * 60)

    all_data = []

    for state_abbr, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_abbr} (FIPS {state_fips})...")
        try:
            response = census_client.get_population_total(year, state_fips=state_fips)

            # Parse response
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Create county FIPS code (state + county)
    if 'state' in df.columns and 'county' in df.columns:
        df['fips'] = df['state'].astype(str).str.zfill(2) + df['county'].astype(str).str.zfill(3)

    # Rename B01001_001E to total_population for clarity
    if 'B01001_001E' in df.columns:
        df['total_population'] = pd.to_numeric(df['B01001_001E'], errors='coerce')

    print(f"\n✓ Total population records: {len(df)}")

    return df


def calculate_orgs_per_capita(county_counts, population_df):
    """
    Calculate 501(c)(3) organizations per 1,000 persons.

    Args:
        county_counts: Dictionary mapping county FIPS to organization count
        population_df: DataFrame with population data (must have 'fips' and 'total_population' columns)

    Returns:
        DataFrame with organization counts and per capita metrics
    """
    print("\nCalculating organizations per 1,000 persons...")
    print("-" * 60)

    # Convert county counts to DataFrame
    orgs_df = pd.DataFrame([
        {'fips': fips, 'org_count_501c3': count}
        for fips, count in county_counts.items()
    ])

    # Merge with population data
    merged = population_df[['fips', 'NAME', 'total_population']].merge(
        orgs_df,
        on='fips',
        how='outer'  # Outer join to keep all counties
    )

    # Fill missing organization counts with 0
    merged['org_count_501c3'] = merged['org_count_501c3'].fillna(0).astype(int)

    # Calculate per capita metric
    merged['orgs_per_1000'] = (merged['org_count_501c3'] / merged['total_population']) * 1000

    # Sort by FIPS
    merged = merged.sort_values('fips')

    print(f"✓ Calculated per capita metrics for {len(merged)} counties")
    print(f"  Mean: {merged['orgs_per_1000'].mean():.2f} orgs per 1,000 persons")
    print(f"  Median: {merged['orgs_per_1000'].median():.2f} orgs per 1,000 persons")
    print(f"  Range: {merged['orgs_per_1000'].min():.2f} to {merged['orgs_per_1000'].max():.2f}")

    return merged


def process_and_save_data(county_counts, population_df, year):
    """
    Process all data and save to CSV files.

    Args:
        county_counts: Dictionary mapping county FIPS to organization count
        population_df: DataFrame with population data
        year: Year of data collection

    Returns:
        DataFrame with all processed data
    """
    print("\nProcessing and saving data...")
    print("-" * 60)

    # Calculate per capita metrics
    final_df = calculate_orgs_per_capita(county_counts, population_df)

    # Save to CSV
    processed_dir = Path(PROCESSED_DATA_DIR)
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_file = processed_dir / f"irs_501c3_by_county_{year}.csv"
    final_df.to_csv(output_file, index=False)
    print(f"\n✓ Saved processed data to: {output_file}")

    # Create summary JSON
    summary = {
        'collection_date': datetime.now().isoformat(),
        'data_year': year,
        'component': 'Component 8: Social Capital',
        'measures': {
            '8.1': {
                'name': 'Number of 501(c)(3) Organizations Per 1,000 Persons',
                'source': 'IRS Exempt Organizations Business Master File',
                'records': len(final_df),
                'counties_with_orgs': int((final_df['org_count_501c3'] > 0).sum()),
                'total_organizations': int(final_df['org_count_501c3'].sum()),
                'mean_per_1000': float(final_df['orgs_per_1000'].mean()),
                'median_per_1000': float(final_df['orgs_per_1000'].median()),
                'min_per_1000': float(final_df['orgs_per_1000'].min()),
                'max_per_1000': float(final_df['orgs_per_1000'].max())
            }
        },
        'data_files': {
            'processed': str(output_file.name)
        }
    }

    summary_file = processed_dir / f"component8_collection_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved collection summary to: {summary_file}")

    return final_df


def main():
    """Main collection workflow for Component 8 Measure 8.1"""
    print("=" * 80)
    print("Component Index 8: Social Capital - Data Collection")
    print("Measure 8.1: 501(c)(3) Organizations Per 1,000 Persons")
    print("=" * 80)

    # Initialize clients
    irs_client = IRSExemptOrgClient()
    census_client = CensusClient()

    # Define target states (all 10 states)
    state_fips_list = list(STATE_FIPS.values())

    # Define data year (use most recent available)
    year = 2022  # Most recent Census ACS population data

    # Step 1: Collect 501(c)(3) organization counts by county
    county_counts = collect_501c3_organizations(irs_client, state_fips_list)

    # Step 2: Get population data for per capita calculation
    population_df = get_population_data(census_client, year, state_fips_list)

    # Step 3: Calculate per capita metrics and save
    final_df = process_and_save_data(county_counts, population_df, year)

    # Print final summary
    print("\n" + "=" * 80)
    print("COLLECTION COMPLETE")
    print("=" * 80)
    print(f"Total counties: {len(final_df)}")
    print(f"Counties with 501(c)(3) orgs: {(final_df['org_count_501c3'] > 0).sum()}")
    print(f"Total 501(c)(3) organizations: {final_df['org_count_501c3'].sum():,}")
    print(f"Mean per 1,000 persons: {final_df['orgs_per_1000'].mean():.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
