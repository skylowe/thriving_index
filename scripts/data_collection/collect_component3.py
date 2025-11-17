"""
Component Index 3: Other Economic Prosperity - Data Collection Script

Collects all 5 measures for Component Index 3 for all counties in 10 states:
3.1 Non-Farm Proprietor Personal Income (BEA CAINC4)
3.2 Personal Income Stability (BEA CAINC1 - 15 years)
3.3 Life Expectancy (County Health Rankings via Zenodo)
3.4 Poverty Rate (Census ACS S1701)
3.5 Share of Income from DIR (BEA CAINC5N + CAINC1)

States: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
"""

import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
import requests
import zipfile
import io
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import STATE_FIPS, RAW_DATA_DIR, PROCESSED_DATA_DIR
from api_clients.bea_client import BEAClient
from api_clients.census_client import CensusClient


def collect_proprietor_income(bea_client, year, state_fips_list):
    """
    Collect non-farm proprietor income data from BEA CAINC4 (Measure 3.1).

    Args:
        bea_client: BEAClient instance
        year: Year of data (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with proprietor income data
    """
    print("\nCollecting BEA Non-Farm Proprietor Income (Measure 3.1)...")
    print("-" * 60)

    response = bea_client.get_proprietors_data(year, state_fips_list=state_fips_list, include_farm=False)

    # Save raw response
    filename = f"bea_proprietor_income_{year}.json"
    bea_client.save_response(response, filename)

    # Extract data
    data = response['BEAAPI']['Results']['Data']
    df = pd.DataFrame(data)

    print(f"✓ Retrieved {len(df)} records for year {year}")
    print(f"  States: {sorted(df['GeoFips'].str[:2].unique())}")
    print(f"  Counties: {len(df['GeoFips'].unique())}")

    return df


def collect_income_stability(bea_client, years, state_fips_list):
    """
    Collect personal income data for stability calculation from BEA CAINC1 (Measure 3.2).

    Args:
        bea_client: BEAClient instance
        years: List of years (e.g., list(range(2008, 2023)) for 15 years)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with personal income data over time
    """
    print("\nCollecting BEA Personal Income for Stability Analysis (Measure 3.2)...")
    print(f"Years: {min(years)} to {max(years)} ({len(years)} years)")
    print("-" * 60)

    response = bea_client.get_total_personal_income(years, state_fips_list=state_fips_list)

    # Save raw response
    filename = f"bea_personal_income_{min(years)}_{max(years)}.json"
    bea_client.save_response(response, filename)

    # Extract data
    data = response['BEAAPI']['Results']['Data']
    df = pd.DataFrame(data)

    print(f"✓ Retrieved {len(df)} records")
    print(f"  Years: {sorted(df['TimePeriod'].unique())}")
    print(f"  Counties: {len(df['GeoFips'].unique())}")

    return df


def collect_poverty_rate(census_client, year, state_fips_dict):
    """
    Collect poverty rate data from Census ACS (Measure 3.4).

    Args:
        census_client: CensusClient instance
        year: ACS 5-year period end year (e.g., 2022 for 2018-2022)
        state_fips_dict: Dictionary mapping state abbreviations to FIPS codes

    Returns:
        DataFrame with poverty rate data
    """
    print("\nCollecting Census ACS Poverty Rate Data (Measure 3.4)...")
    print(f"ACS 5-year period ending: {year}")
    print("-" * 60)

    all_data = []

    # Collect data state by state
    for state_abbr, state_fips in state_fips_dict.items():
        print(f"  Collecting {state_abbr}...", end=" ")
        try:
            response = census_client.get_poverty_rate(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_poverty_{state_abbr}_{year}.json"
            census_client.save_response(response, filename)

            # Parse response (first row is headers)
            if len(response) > 1:
                headers = response[0]
                data_rows = response[1:]
                for row in data_rows:
                    record = dict(zip(headers, row))
                    record['state_abbr'] = state_abbr
                    all_data.append(record)
                print(f"✓ {len(data_rows)} counties")
            else:
                print("✗ No data")

        except Exception as e:
            print(f"✗ Error: {e}")

    df = pd.DataFrame(all_data)
    print(f"\n✓ Total records collected: {len(df)}")
    print(f"  States: {sorted(df['state_abbr'].unique())}")

    return df


def collect_dir_income_share(bea_client, year, state_fips_list):
    """
    Collect DIR income and total personal income for ratio calculation (Measure 3.5).

    Args:
        bea_client: BEAClient instance
        year: Year of data (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        Tuple of (dir_income_df, total_income_df)
    """
    print("\nCollecting BEA DIR Income Share Data (Measure 3.5)...")
    print("-" * 60)

    # Collect DIR income (Line 46 from CAINC5N)
    print("  Getting DIR income (CAINC5N Line 46)...", end=" ")
    dir_response = bea_client.get_dir_income_data(year, state_fips_list=state_fips_list)
    filename = f"bea_dir_income_share_{year}.json"
    bea_client.save_response(dir_response, filename)
    dir_data = dir_response['BEAAPI']['Results']['Data']
    dir_df = pd.DataFrame(dir_data)
    print(f"✓ {len(dir_df)} records")

    # Collect total personal income (Line 1 from CAINC1)
    print("  Getting total personal income (CAINC1 Line 1)...", end=" ")
    total_response = bea_client.get_total_personal_income(year, state_fips_list=state_fips_list)
    filename = f"bea_total_income_share_{year}.json"
    bea_client.save_response(total_response, filename)
    total_data = total_response['BEAAPI']['Results']['Data']
    total_df = pd.DataFrame(total_data)
    print(f"✓ {len(total_df)} records")

    print(f"\n✓ Retrieved data for DIR share calculation")
    print(f"  Counties with DIR data: {len(dir_df['GeoFips'].unique())}")
    print(f"  Counties with total income data: {len(total_df['GeoFips'].unique())}")

    return dir_df, total_df


def process_proprietor_income(df):
    """Process proprietor income data into clean CSV."""
    processed = df[['GeoFips', 'GeoName', 'TimePeriod', 'DataValue', 'CL_UNIT', 'UNIT_MULT']].copy()
    processed.columns = ['county_fips', 'county_name', 'year', 'proprietor_income', 'unit', 'unit_mult']
    processed['proprietor_income'] = pd.to_numeric(processed['proprietor_income'], errors='coerce')
    return processed


def process_income_stability(df):
    """
    Process income stability data and calculate coefficient of variation.

    Returns:
        DataFrame with CV (coefficient of variation) for each county
    """
    # Convert DataValue to numeric
    df = df.copy()
    df['income'] = pd.to_numeric(df['DataValue'], errors='coerce')
    df['year'] = pd.to_numeric(df['TimePeriod'], errors='coerce')

    # Calculate CV for each county
    stability_results = []
    for county_fips, county_data in df.groupby('GeoFips'):
        county_name = county_data['GeoName'].iloc[0]
        income_values = county_data['income'].dropna()

        if len(income_values) >= 10:  # Require at least 10 years of data
            mean_income = income_values.mean()
            std_income = income_values.std()
            cv = (std_income / mean_income) if mean_income != 0 else np.nan

            stability_results.append({
                'county_fips': county_fips,
                'county_name': county_name,
                'years_data': len(income_values),
                'mean_income': mean_income,
                'std_income': std_income,
                'coefficient_of_variation': cv
            })

    processed = pd.DataFrame(stability_results)
    print(f"\n  Calculated CV for {len(processed)} counties")
    print(f"  Average CV: {processed['coefficient_of_variation'].mean():.4f}")

    return processed


def process_poverty_rate(df):
    """Process poverty rate data into clean CSV."""
    processed = df[['state', 'county', 'NAME', 'S1701_C03_001E', 'state_abbr']].copy()
    processed.columns = ['state_fips', 'county_fips', 'county_name', 'poverty_rate', 'state_abbr']

    # Create full FIPS code
    processed['full_fips'] = processed['state_fips'] + processed['county_fips']
    processed['poverty_rate'] = pd.to_numeric(processed['poverty_rate'], errors='coerce')

    return processed[['full_fips', 'state_fips', 'county_fips', 'county_name', 'state_abbr', 'poverty_rate']]


def process_dir_income_share(dir_df, total_df):
    """
    Process DIR income share data and calculate ratio.

    Returns:
        DataFrame with DIR/Total income ratio for each county
    """
    # Process DIR income
    dir_processed = dir_df.copy()
    dir_processed['dir_income'] = pd.to_numeric(dir_processed['DataValue'], errors='coerce')
    dir_processed = dir_processed[['GeoFips', 'GeoName', 'dir_income']]

    # Process total income
    total_processed = total_df.copy()
    total_processed['total_income'] = pd.to_numeric(total_processed['DataValue'], errors='coerce')
    total_processed = total_processed[['GeoFips', 'total_income']]

    # Merge and calculate ratio
    merged = pd.merge(dir_processed, total_processed, on='GeoFips', how='inner')
    merged['dir_share_pct'] = (merged['dir_income'] / merged['total_income']) * 100

    processed = merged[['GeoFips', 'GeoName', 'dir_income', 'total_income', 'dir_share_pct']].copy()
    processed.columns = ['county_fips', 'county_name', 'dir_income', 'total_income', 'dir_share_pct']

    print(f"\n  Calculated DIR share for {len(processed)} counties")
    print(f"  Average DIR share: {processed['dir_share_pct'].mean():.2f}%")

    return processed


def collect_life_expectancy(year, state_fips_dict):
    """
    Collect life expectancy data from County Health Rankings via Zenodo (Measure 3.3).

    Args:
        year: Year of CHR data release (e.g., 2025)
        state_fips_dict: Dictionary of state abbreviations to FIPS codes

    Returns:
        DataFrame with life expectancy data
    """
    print("\nCollecting Life Expectancy Data (Measure 3.3)...")
    print(f"Source: County Health Rankings & Roadmaps {year} (Zenodo)")
    print("-" * 60)

    # Download from Zenodo
    print(f"Downloading data from Zenodo... (this may take a minute, ~52 MB)")
    url = f"https://zenodo.org/api/records/17584421/files/{year}.zip/content"

    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        file_size_mb = len(response.content) / (1024 * 1024)
        print(f"✓ Downloaded {file_size_mb:.1f} MB")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download CHR data: {str(e)}")

    # Extract ZIP and find life expectancy data
    print("Extracting and locating life expectancy data...")
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
            'year': year,
            'download_date': datetime.now().isoformat(),
            'source_file': filename,
            'records_downloaded': len(df)
        }

        metadata_file = raw_dir / f'chr_life_expectancy_{year}_metadata.json'
        with open(metadata_file, 'w') as f_out:
            json.dump(metadata, f_out, indent=2)
        print(f"Saved: {metadata_file}")

    # Process the data
    # Look for life expectancy columns
    le_columns = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in [
            'life expectancy', 'life_expectancy', 'lifespan', 'v147'
        ])
    ]

    if not le_columns:
        raise Exception("Could not find life expectancy column")

    le_col = le_columns[0]
    print(f"Using column: {le_col}")

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

    result_df = filtered_df[['full_fips', 'state_fips', le_col]].copy()
    if name_columns:
        result_df['county_name'] = filtered_df[name_columns[0]]

    result_df = result_df.rename(columns={le_col: 'life_expectancy'})
    result_df['life_expectancy'] = pd.to_numeric(result_df['life_expectancy'], errors='coerce')

    print(f"  Mean: {result_df['life_expectancy'].mean():.2f} years")
    print(f"  Range: {result_df['life_expectancy'].min():.2f} - {result_df['life_expectancy'].max():.2f} years")

    return result_df


def main():
    """Main execution function."""
    print("=" * 80)
    print("COMPONENT INDEX 3: OTHER ECONOMIC PROSPERITY - DATA COLLECTION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configuration
    CURRENT_YEAR = 2022
    INCOME_STABILITY_YEARS = list(range(2008, 2023))  # 2008-2022 = 15 years
    STATE_FIPS_LIST = list(STATE_FIPS.values())

    # Initialize API clients
    print("Initializing API clients...")
    bea_client = BEAClient()
    census_client = CensusClient()
    print("✓ API clients initialized\n")

    # Track collection summary
    summary = {
        'collection_date': datetime.now().isoformat(),
        'measures': {},
        'total_records': 0
    }

    # MEASURE 3.1: Non-Farm Proprietor Income
    try:
        proprietor_df = collect_proprietor_income(bea_client, CURRENT_YEAR, STATE_FIPS_LIST)
        proprietor_processed = process_proprietor_income(proprietor_df)

        # Save processed data
        output_file = PROCESSED_DATA_DIR / f'bea_proprietor_income_{CURRENT_YEAR}.csv'
        proprietor_processed.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}\n")

        summary['measures']['3.1_proprietor_income'] = {
            'status': 'complete',
            'records': len(proprietor_processed),
            'year': CURRENT_YEAR
        }
    except Exception as e:
        print(f"✗ Error collecting Measure 3.1: {e}\n")
        summary['measures']['3.1_proprietor_income'] = {'status': 'failed', 'error': str(e)}

    # MEASURE 3.2: Personal Income Stability
    try:
        income_stability_df = collect_income_stability(bea_client, INCOME_STABILITY_YEARS, STATE_FIPS_LIST)
        stability_processed = process_income_stability(income_stability_df)

        # Save processed data
        output_file = PROCESSED_DATA_DIR / f'bea_income_stability_{min(INCOME_STABILITY_YEARS)}_{max(INCOME_STABILITY_YEARS)}.csv'
        stability_processed.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}\n")

        summary['measures']['3.2_income_stability'] = {
            'status': 'complete',
            'records': len(stability_processed),
            'years': f"{min(INCOME_STABILITY_YEARS)}-{max(INCOME_STABILITY_YEARS)}"
        }
    except Exception as e:
        print(f"✗ Error collecting Measure 3.2: {e}\n")
        summary['measures']['3.2_income_stability'] = {'status': 'failed', 'error': str(e)}

    # MEASURE 3.3: Life Expectancy
    try:
        life_expectancy_df = collect_life_expectancy(2025, STATE_FIPS)

        # Save processed data
        output_file = PROCESSED_DATA_DIR / 'chr_life_expectancy_2025.csv'
        life_expectancy_df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}\n")

        summary['measures']['3.3_life_expectancy'] = {
            'status': 'complete',
            'records': len(life_expectancy_df),
            'year': 2025,
            'source': 'County Health Rankings (Zenodo)'
        }
    except Exception as e:
        print(f"✗ Error collecting Measure 3.3: {e}\n")
        summary['measures']['3.3_life_expectancy'] = {'status': 'failed', 'error': str(e)}

    # MEASURE 3.4: Poverty Rate
    try:
        poverty_df = collect_poverty_rate(census_client, CURRENT_YEAR, STATE_FIPS)
        poverty_processed = process_poverty_rate(poverty_df)

        # Save processed data
        output_file = PROCESSED_DATA_DIR / f'census_poverty_{CURRENT_YEAR}.csv'
        poverty_processed.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}\n")

        summary['measures']['3.4_poverty_rate'] = {
            'status': 'complete',
            'records': len(poverty_processed),
            'year': CURRENT_YEAR
        }
    except Exception as e:
        print(f"✗ Error collecting Measure 3.4: {e}\n")
        summary['measures']['3.4_poverty_rate'] = {'status': 'failed', 'error': str(e)}

    # MEASURE 3.5: Share of DIR Income
    try:
        dir_df, total_df = collect_dir_income_share(bea_client, CURRENT_YEAR, STATE_FIPS_LIST)
        dir_share_processed = process_dir_income_share(dir_df, total_df)

        # Save processed data
        output_file = PROCESSED_DATA_DIR / f'bea_dir_income_share_{CURRENT_YEAR}.csv'
        dir_share_processed.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}\n")

        summary['measures']['3.5_dir_share'] = {
            'status': 'complete',
            'records': len(dir_share_processed),
            'year': CURRENT_YEAR
        }
    except Exception as e:
        print(f"✗ Error collecting Measure 3.5: {e}\n")
        summary['measures']['3.5_dir_share'] = {'status': 'failed', 'error': str(e)}

    # Calculate total records
    summary['total_records'] = sum(
        m.get('records', 0) for m in summary['measures'].values() if 'records' in m
    )

    # Save collection summary
    summary_file = PROCESSED_DATA_DIR / 'component3_collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("=" * 80)
    print("COLLECTION SUMMARY")
    print("=" * 80)
    print(f"Total records collected: {summary['total_records']}")
    print(f"\nMeasures collected (5 of 5):")
    for measure, info in summary['measures'].items():
        status = info.get('status', 'unknown')
        records = info.get('records', 'N/A')
        print(f"  {measure}: {status} ({records} records)")

    print(f"\n✓ Summary saved: {summary_file}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    main()
