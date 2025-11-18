"""
Component Index 8: Social Capital - Data Collection Script

Collects measures for Component Index 8 for all counties in 10 states:
8.1 Number of 501(c)(3) Organizations Per 1,000 Persons (IRS EO BMF)
8.3 Social Associations (County Health Rankings - membership associations per 10,000 pop)
8.4 Voter Turnout (County Health Rankings - 2020 Presidential Election)

States: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
"""

import sys
from pathlib import Path
import json
import pandas as pd
import requests
import zipfile
import io
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


def collect_voter_turnout(chr_year, state_fips_dict):
    """
    Collect voter turnout data from County Health Rankings via Zenodo (Measure 8.4).

    Args:
        chr_year: Year of CHR data release (e.g., 2025)
        state_fips_dict: Dictionary of state abbreviations to FIPS codes

    Returns:
        DataFrame with voter turnout data (2020 presidential election)
    """
    print("\nCollecting Voter Turnout Data (Measure 8.4)...")
    print(f"Source: County Health Rankings & Roadmaps {chr_year} (Zenodo)")
    print("Election: 2020 U.S. Presidential Election")
    print("-" * 60)

    # Download from Zenodo
    print(f"Downloading data from Zenodo... (this may take a minute, ~50 MB)")
    url = f"https://zenodo.org/api/records/17584421/files/{chr_year}.zip/content"

    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        file_size_mb = len(response.content) / (1024 * 1024)
        print(f"✓ Downloaded {file_size_mb:.1f} MB")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download CHR data: {str(e)}")

    # Extract ZIP and find voter turnout data
    print("Extracting and locating voter turnout data...")
    zip_data = io.BytesIO(response.content)

    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        # Look for analytic data file
        analytic_files = [
            f for f in file_list
            if ('analytic' in f.lower() or 'data' in f.lower())
            and f.endswith('.csv')
            and not f.startswith('__MACOSX')
        ]

        if not analytic_files:
            analytic_files = [f for f in file_list if f.endswith('.csv') and not f.startswith('__MACOSX')]

        if not analytic_files:
            raise Exception("No CSV data files found in ZIP")

        # Read the first analytic file
        filename = analytic_files[0]
        print(f"Reading: {filename}")

        with zip_ref.open(filename) as f:
            df = pd.read_csv(f, encoding='utf-8', low_memory=False)

        # Save metadata
        raw_dir = RAW_DATA_DIR / 'chr'
        raw_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            'source': 'County Health Rankings & Roadmaps',
            'zenodo_doi': '10.5281/zenodo.17584421',
            'year': chr_year,
            'download_date': datetime.now().isoformat(),
            'source_file': filename,
            'records_downloaded': len(df),
            'measure': 'Voter Turnout (2020 Presidential Election)'
        }

        metadata_file = raw_dir / f'chr_voter_turnout_{chr_year}_metadata.json'
        with open(metadata_file, 'w') as f_out:
            json.dump(metadata, f_out, indent=2)
        print(f"Saved metadata: {metadata_file}")

    # Process the data
    # Look for voter turnout columns (v177_rawvalue)
    voter_cols = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in [
            'voter turnout raw', 'v177_rawvalue', 'voter_turnout'
        ])
    ]

    if not voter_cols:
        raise Exception("Could not find voter turnout column")

    voter_col = voter_cols[0]
    print(f"Using column: {voter_col}")

    # Find FIPS columns
    fips_5digit_cols = [c for c in df.columns if '5-digit' in c.lower() and 'fips' in c.lower()]
    if fips_5digit_cols:
        df['full_fips'] = df[fips_5digit_cols[0]].astype(str).str.zfill(5)
    elif any('fipscode' in c.lower() for c in df.columns):
        fips_col = next((c for c in df.columns if 'fipscode' in c.lower()), None)
        df['full_fips'] = df[fips_col].astype(str).str.zfill(5)
    else:
        # Look for state and county FIPS columns
        state_cols = [c for c in df.columns if 'state' in c.lower() and 'fips' in c.lower()]
        county_cols = [c for c in df.columns if 'county' in c.lower() and 'fips' in c.lower()]

        if state_cols and county_cols:
            df['full_fips'] = (
                df[state_cols[0]].astype(str).str.zfill(2) +
                df[county_cols[0]].astype(str).str.zfill(3)
            )
        else:
            raise Exception("Cannot determine FIPS code structure")

    # Extract state FIPS and filter
    df['state_fips'] = df['full_fips'].str[:2]
    target_state_fips = list(state_fips_dict.values())
    filtered_df = df[df['state_fips'].isin(target_state_fips)].copy()

    print(f"✓ Retrieved {len(filtered_df)} records for target states")

    # Select and rename columns
    name_columns = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in ['name', 'county_name', 'county name'])
    ]

    result_df = filtered_df[['full_fips', 'state_fips', voter_col]].copy()
    if name_columns:
        result_df['county_name'] = filtered_df[name_columns[0]]

    result_df = result_df.rename(columns={voter_col: 'voter_turnout_pct'})

    # Convert to numeric and multiply by 100 to get percentage (CHR stores as proportion 0-1)
    result_df['voter_turnout_pct'] = pd.to_numeric(result_df['voter_turnout_pct'], errors='coerce') * 100

    print(f"  Mean: {result_df['voter_turnout_pct'].mean():.2f}%")
    print(f"  Median: {result_df['voter_turnout_pct'].median():.2f}%")
    print(f"  Range: {result_df['voter_turnout_pct'].min():.2f}% - {result_df['voter_turnout_pct'].max():.2f}%")
    print(f"  Missing values: {result_df['voter_turnout_pct'].isna().sum()}")

    return result_df


def collect_social_associations(chr_year, state_fips_dict):
    """
    Collect social associations data from County Health Rankings via Zenodo (Measure 8.3).

    Args:
        chr_year: Year of CHR data release (e.g., 2025)
        state_fips_dict: Dictionary of state abbreviations to FIPS codes

    Returns:
        DataFrame with social associations data (membership associations per 10,000 pop)
    """
    print("\nCollecting Social Associations Data (Measure 8.3)...")
    print(f"Source: County Health Rankings & Roadmaps {chr_year} (Zenodo)")
    print("Measure: Number of membership associations per 10,000 population")
    print("-" * 60)

    # Download from Zenodo (same data source as voter turnout)
    print(f"Downloading data from Zenodo... (this may take a minute, ~50 MB)")
    url = f"https://zenodo.org/api/records/17584421/files/{chr_year}.zip/content"

    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        file_size_mb = len(response.content) / (1024 * 1024)
        print(f"✓ Downloaded {file_size_mb:.1f} MB")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download CHR data: {str(e)}")

    # Extract ZIP and find social associations data
    print("Extracting and locating social associations data...")
    zip_data = io.BytesIO(response.content)

    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        # Look for analytic data file
        analytic_files = [
            f for f in file_list
            if ('analytic' in f.lower() or 'data' in f.lower())
            and f.endswith('.csv')
            and not f.startswith('__MACOSX')
        ]

        if not analytic_files:
            analytic_files = [f for f in file_list if f.endswith('.csv') and not f.startswith('__MACOSX')]

        if not analytic_files:
            raise Exception("No CSV data files found in ZIP")

        # Read the first analytic file
        filename = analytic_files[0]
        print(f"Reading: {filename}")

        with zip_ref.open(filename) as f:
            df = pd.read_csv(f, encoding='utf-8', low_memory=False)

        # Save metadata
        raw_dir = RAW_DATA_DIR / 'chr'
        raw_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            'source': 'County Health Rankings & Roadmaps',
            'zenodo_doi': '10.5281/zenodo.17584421',
            'year': chr_year,
            'download_date': datetime.now().isoformat(),
            'source_file': filename,
            'records_downloaded': len(df),
            'measure': 'Social Associations (v140_rawvalue)',
            'description': 'Number of membership associations per 10,000 population'
        }

        metadata_file = raw_dir / f'chr_social_associations_{chr_year}_metadata.json'
        with open(metadata_file, 'w') as f_out:
            json.dump(metadata, f_out, indent=2)
        print(f"Saved metadata: {metadata_file}")

    # Process the data
    # Look for social associations columns (v140_rawvalue or "Social Associations raw value")
    social_cols = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in [
            'social associations raw', 'v140_rawvalue'
        ])
    ]

    if not social_cols:
        raise Exception("Could not find social associations column")

    social_col = social_cols[0]
    print(f"Using column: {social_col}")

    # Find FIPS columns
    fips_5digit_cols = [c for c in df.columns if '5-digit' in c.lower() and 'fips' in c.lower()]
    if fips_5digit_cols:
        df['full_fips'] = df[fips_5digit_cols[0]].astype(str).str.zfill(5)
    elif any('fipscode' in c.lower() for c in df.columns):
        fips_col = next((c for c in df.columns if 'fipscode' in c.lower()), None)
        df['full_fips'] = df[fips_col].astype(str).str.zfill(5)
    else:
        # Look for state and county FIPS columns
        state_cols = [c for c in df.columns if 'state' in c.lower() and 'fips' in c.lower()]
        county_cols = [c for c in df.columns if 'county' in c.lower() and 'fips' in c.lower()]

        if state_cols and county_cols:
            df['full_fips'] = (
                df[state_cols[0]].astype(str).str.zfill(2) +
                df[county_cols[0]].astype(str).str.zfill(3)
            )
        else:
            raise Exception("Cannot determine FIPS code structure")

    # Extract state FIPS and filter
    df['state_fips'] = df['full_fips'].str[:2]
    target_state_fips = list(state_fips_dict.values())
    filtered_df = df[df['state_fips'].isin(target_state_fips)].copy()

    print(f"✓ Retrieved {len(filtered_df)} records for target states")

    # Select and rename columns
    name_columns = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in ['name', 'county_name', 'county name'])
    ]

    result_df = filtered_df[['full_fips', 'state_fips', social_col]].copy()
    if name_columns:
        result_df['county_name'] = filtered_df[name_columns[0]]

    result_df = result_df.rename(columns={social_col: 'social_associations_per_10k'})

    # Convert to numeric
    result_df['social_associations_per_10k'] = pd.to_numeric(
        result_df['social_associations_per_10k'],
        errors='coerce'
    )

    print(f"  Mean: {result_df['social_associations_per_10k'].mean():.2f} per 10,000 pop")
    print(f"  Median: {result_df['social_associations_per_10k'].median():.2f} per 10,000 pop")
    print(f"  Range: {result_df['social_associations_per_10k'].min():.2f} - {result_df['social_associations_per_10k'].max():.2f}")
    print(f"  Missing values: {result_df['social_associations_per_10k'].isna().sum()}")

    return result_df


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


def process_and_save_data(county_counts, population_df, year, social_associations_df=None, voter_turnout_df=None):
    """
    Process all data and save to CSV files.

    Args:
        county_counts: Dictionary mapping county FIPS to organization count
        population_df: DataFrame with population data
        year: Year of data collection
        social_associations_df: Optional DataFrame with social associations data
        voter_turnout_df: Optional DataFrame with voter turnout data

    Returns:
        DataFrame with all processed data
    """
    print("\nProcessing and saving data...")
    print("-" * 60)

    # Calculate per capita metrics for 501(c)(3) organizations
    final_df = calculate_orgs_per_capita(county_counts, population_df)

    # Merge with social associations data if provided
    if social_associations_df is not None:
        print("\nMerging social associations data...")
        # Ensure both have consistent FIPS codes
        social_associations_df = social_associations_df.rename(columns={'full_fips': 'fips'})
        social_merge = social_associations_df[['fips', 'social_associations_per_10k']].copy()

        final_df = final_df.merge(
            social_merge,
            on='fips',
            how='left'  # Left join to keep all counties from 501(c)(3) data
        )
        print(f"✓ Merged social associations data for {final_df['social_associations_per_10k'].notna().sum()} counties")

    # Merge with voter turnout data if provided
    if voter_turnout_df is not None:
        print("\nMerging voter turnout data...")
        # Ensure both have consistent FIPS codes
        voter_turnout_df = voter_turnout_df.rename(columns={'full_fips': 'fips'})
        voter_turnout_merge = voter_turnout_df[['fips', 'voter_turnout_pct']].copy()

        final_df = final_df.merge(
            voter_turnout_merge,
            on='fips',
            how='left'  # Left join to keep all counties from 501(c)(3) data
        )
        print(f"✓ Merged voter turnout data for {final_df['voter_turnout_pct'].notna().sum()} counties")

    # Save to CSV
    processed_dir = Path(PROCESSED_DATA_DIR)
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_file = processed_dir / f"component8_social_capital_{year}.csv"
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

    # Add social associations summary if data was collected
    if social_associations_df is not None and 'social_associations_per_10k' in final_df.columns:
        summary['measures']['8.3'] = {
            'name': 'Social Associations (membership associations per 10,000 pop)',
            'source': 'County Health Rankings & Roadmaps (Zenodo)',
            'data_source': 'County Business Patterns (NAICS 813)',
            'records': int(final_df['social_associations_per_10k'].notna().sum()),
            'mean_per_10k': float(final_df['social_associations_per_10k'].mean()),
            'median_per_10k': float(final_df['social_associations_per_10k'].median()),
            'min_per_10k': float(final_df['social_associations_per_10k'].min()),
            'max_per_10k': float(final_df['social_associations_per_10k'].max())
        }

    # Add voter turnout summary if data was collected
    if voter_turnout_df is not None and 'voter_turnout_pct' in final_df.columns:
        summary['measures']['8.4'] = {
            'name': 'Voter Turnout (2020 Presidential Election)',
            'source': 'County Health Rankings & Roadmaps (Zenodo)',
            'election_year': 2020,
            'records': int(final_df['voter_turnout_pct'].notna().sum()),
            'mean_turnout_pct': float(final_df['voter_turnout_pct'].mean()),
            'median_turnout_pct': float(final_df['voter_turnout_pct'].median()),
            'min_turnout_pct': float(final_df['voter_turnout_pct'].min()),
            'max_turnout_pct': float(final_df['voter_turnout_pct'].max())
        }

    summary_file = processed_dir / f"component8_collection_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved collection summary to: {summary_file}")

    return final_df


def main():
    """Main collection workflow for Component 8 measures"""
    print("=" * 80)
    print("Component Index 8: Social Capital - Data Collection")
    print("Measure 8.1: 501(c)(3) Organizations Per 1,000 Persons")
    print("Measure 8.3: Social Associations (per 10,000 population)")
    print("Measure 8.4: Voter Turnout (2020 Presidential Election)")
    print("=" * 80)

    # Initialize clients
    irs_client = IRSExemptOrgClient()
    census_client = CensusClient()

    # Define target states (all 10 states)
    state_fips_list = list(STATE_FIPS.values())

    # Define data year (use most recent available)
    year = 2022  # Most recent Census ACS population data
    chr_year = 2025  # County Health Rankings 2025 release

    # Step 1: Collect 501(c)(3) organization counts by county
    county_counts = collect_501c3_organizations(irs_client, state_fips_list)

    # Step 2: Get population data for per capita calculation
    population_df = get_population_data(census_client, year, state_fips_list)

    # Step 3: Collect social associations data
    social_associations_df = None
    try:
        social_associations_df = collect_social_associations(chr_year, STATE_FIPS)
    except Exception as e:
        print(f"\n✗ Error collecting social associations data: {e}")
        print("  Continuing without social associations data...")

    # Step 4: Collect voter turnout data
    voter_turnout_df = None
    try:
        voter_turnout_df = collect_voter_turnout(chr_year, STATE_FIPS)
    except Exception as e:
        print(f"\n✗ Error collecting voter turnout data: {e}")
        print("  Continuing without voter turnout data...")

    # Step 5: Calculate per capita metrics and save
    final_df = process_and_save_data(
        county_counts,
        population_df,
        year,
        social_associations_df,
        voter_turnout_df
    )

    # Print final summary
    print("\n" + "=" * 80)
    print("COLLECTION COMPLETE")
    print("=" * 80)
    print(f"Total counties: {len(final_df)}")
    print()
    print("Measure 8.1: 501(c)(3) Organizations")
    print(f"  Counties with organizations: {(final_df['org_count_501c3'] > 0).sum()}")
    print(f"  Total organizations: {final_df['org_count_501c3'].sum():,}")
    print(f"  Mean per 1,000 persons: {final_df['orgs_per_1000'].mean():.2f}")

    if 'social_associations_per_10k' in final_df.columns:
        print()
        print("Measure 8.3: Social Associations")
        print(f"  Counties with data: {final_df['social_associations_per_10k'].notna().sum()}")
        print(f"  Mean per 10,000 pop: {final_df['social_associations_per_10k'].mean():.2f}")
        print(f"  Median per 10,000 pop: {final_df['social_associations_per_10k'].median():.2f}")

    if 'voter_turnout_pct' in final_df.columns:
        print()
        print("Measure 8.4: Voter Turnout (2020 Presidential Election)")
        print(f"  Counties with data: {final_df['voter_turnout_pct'].notna().sum()}")
        print(f"  Mean turnout: {final_df['voter_turnout_pct'].mean():.2f}%")
        print(f"  Median turnout: {final_df['voter_turnout_pct'].median():.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
