"""
Component Index 1: Growth Index - Data Collection Script

Collects all 5 measures for Component Index 1 for all counties in 10 states:
1. Growth in Total Employment (BEA CAINC5)
2. Private Employment (BLS QCEW)
3. Growth in Private Wages Per Job (BLS QCEW)
4. Growth in Households with Children (Census ACS)
5. Growth in Dividends, Interest and Rent Income (BEA CAINC5)

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
from api_clients.bea_client import BEAClient
from api_clients.qcew_client import QCEWClient
from api_clients.census_client import CensusClient


def collect_bea_employment(client, years, state_fips_list):
    """
    Collect total employment data from BEA (Measure 1.1).

    Args:
        client: BEAClient instance
        years: List of years (e.g., [2020, 2021, 2022])
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with employment data
    """
    print("\nCollecting BEA Total Employment Data (Measure 1.1)...")
    print("-" * 60)

    response = client.get_employment_data(years, state_fips_list=state_fips_list)

    # Save raw response
    filename = f"bea_employment_{min(years)}_{max(years)}.json"
    client.save_response(response, filename)

    # Extract data
    data = response['BEAAPI']['Results']['Data']
    df = pd.DataFrame(data)

    print(f"✓ Retrieved {len(df)} records")
    print(f"  Years: {sorted(df['TimePeriod'].unique())}")
    print(f"  States: {sorted(df['GeoFips'].str[:2].unique())}")

    return df


def collect_bea_dir_income(client, years, state_fips_list):
    """
    Collect dividends, interest, and rent income data from BEA (Measure 1.5).

    Args:
        client: BEAClient instance
        years: List of years
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with DIR income data
    """
    print("\nCollecting BEA DIR Income Data (Measure 1.5)...")
    print("-" * 60)

    response = client.get_dir_income_data(years, state_fips_list=state_fips_list)

    # Save raw response
    filename = f"bea_dir_income_{min(years)}_{max(years)}.json"
    client.save_response(response, filename)

    # Extract data
    data = response['BEAAPI']['Results']['Data']
    df = pd.DataFrame(data)

    print(f"✓ Retrieved {len(df)} records")
    print(f"  Years: {sorted(df['TimePeriod'].unique())}")

    return df


def collect_census_households_with_children(client, years, state_fips_list):
    """
    Collect households with children data from Census ACS (Measure 1.4).

    Args:
        client: CensusClient instance
        years: List of ACS 5-year period end years (e.g., [2017, 2022])
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with household data
    """
    print("\nCollecting Census Households with Children Data (Measure 1.4)...")
    print("-" * 60)

    all_data = []

    for year in years:
        print(f"  Collecting ACS {year} 5-year estimates...")
        for state_fips in state_fips_list:
            try:
                response = client.get_households_with_children(year, state_fips=state_fips)

                # Save raw response
                filename = f"census_households_children_{state_fips}_{year}.json"
                client.save_response(response, filename)

                # Parse response
                parsed = client.parse_response_to_dict(response)
                for row in parsed:
                    row['year'] = year
                    all_data.append(row)

            except Exception as e:
                print(f"  ✗ Error for state {state_fips}, year {year}: {e}")

    df = pd.DataFrame(all_data)
    print(f"✓ Retrieved {len(df)} records")
    print(f"  Years: {sorted(df['year'].unique()) if not df.empty else 'No data'}")
    print(f"  States: {sorted(df['state'].unique()) if not df.empty else 'No data'}")

    return df


def get_county_list_for_state(state_fips):
    """
    Get list of county FIPS codes for a state.
    Uses Census API to get current county list.

    Args:
        state_fips: State FIPS code

    Returns:
        list: List of 3-digit county FIPS codes
    """
    try:
        client = CensusClient()
        # Use a simple variable to get county list
        response = client.get_acs5_data(2022, ['NAME'], 'county:*', state_fips=state_fips)
        counties = [row[response[0].index('county')] for row in response[1:]]
        return counties
    except Exception as e:
        print(f"Warning: Could not retrieve county list for state {state_fips}: {e}")
        return []


def collect_qcew_data(client, state_fips_list, years):
    """
    Collect QCEW employment and wages data for multiple states and years.

    Args:
        client: QCEWClient instance
        state_fips_list: List of state FIPS codes
        years: List of years

    Returns:
        DataFrame with QCEW data (employment and wages combined)
    """
    print("\nCollecting QCEW Employment and Wages Data...")
    print("-" * 60)
    print("Note: This will download large ZIP files (~500MB per year)")
    print("Files will be cached for future use.")
    print()

    # Collect data for all years
    df = client.collect_multi_year_data(years, state_fips_list)

    if not df.empty:
        # Save the combined data
        client.save_data(df, f"qcew_private_employment_wages_{min(years)}_{max(years)}.csv")

    print(f"✓ Total records: {len(df)}")

    return df


def main(skip_bls=False):
    """
    Main data collection function for Component Index 1

    Args:
        skip_bls: If True, skip BLS QCEW data collection
    """

    print("=" * 80)
    print("COMPONENT INDEX 1: GROWTH INDEX - DATA COLLECTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # State list
    state_fips_list = list(STATE_FIPS.values())
    print(f"Collecting data for {len(state_fips_list)} states: {', '.join(STATE_FIPS.keys())}")
    print()

    # Define time periods (matching Nebraska methodology)
    # Nebraska used 2017-2020 (3-year period)
    # We'll use most recent 3-year period available: 2020-2022
    bea_years = [2020, 2021, 2022]
    acs_years = [2017, 2022]  # Two non-overlapping 5-year periods (2013-2017 and 2018-2022)

    # Initialize API clients
    bea_client = BEAClient()
    qcew_client = QCEWClient()
    census_client = CensusClient()

    # Collection results
    results = {}

    # ======================
    # 1. BEA Total Employment
    # ======================
    try:
        df = collect_bea_employment(bea_client, bea_years, state_fips_list)
        results['bea_employment'] = {
            'success': True,
            'records': len(df),
            'file': 'bea_employment_processed.csv'
        }
        # Save processed data
        output_file = PROCESSED_DATA_DIR / 'bea_employment_processed.csv'
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
    except Exception as e:
        print(f"✗ Failed to collect BEA employment data: {e}")
        results['bea_employment'] = {'success': False, 'error': str(e)}

    # ======================
    # 2. BEA DIR Income
    # ======================
    try:
        df = collect_bea_dir_income(bea_client, bea_years, state_fips_list)
        results['bea_dir_income'] = {
            'success': True,
            'records': len(df),
            'file': 'bea_dir_income_processed.csv'
        }
        # Save processed data
        output_file = PROCESSED_DATA_DIR / 'bea_dir_income_processed.csv'
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
    except Exception as e:
        print(f"✗ Failed to collect BEA DIR income data: {e}")
        results['bea_dir_income'] = {'success': False, 'error': str(e)}

    # ======================
    # 3. Census Households with Children
    # ======================
    try:
        df = collect_census_households_with_children(census_client, acs_years, state_fips_list)
        results['census_households'] = {
            'success': True,
            'records': len(df),
            'file': 'census_households_children_processed.csv'
        }
        # Save processed data
        output_file = PROCESSED_DATA_DIR / 'census_households_children_processed.csv'
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
    except Exception as e:
        print(f"✗ Failed to collect Census household data: {e}")
        results['census_households'] = {'success': False, 'error': str(e)}

    # ======================
    # 4. QCEW Private Employment and Wages (Measures 1.2 & 1.3)
    # ======================
    print("\n" + "=" * 80)
    print("NOTE: QCEW data collection will download large files (~500MB per year)")
    print("Files will be cached for future use")
    print("=" * 80)

    collect_qcew = not skip_bls

    if collect_qcew:
        try:
            # Collect employment and wages data (combined in one dataset)
            df_qcew = collect_qcew_data(qcew_client, state_fips_list, bea_years)
            results['qcew'] = {
                'success': True,
                'records': len(df_qcew),
                'file': f'qcew_private_employment_wages_{min(bea_years)}_{max(bea_years)}.csv'
            }
            # Also save to processed directory
            output_file = PROCESSED_DATA_DIR / f'qcew_private_employment_wages_{min(bea_years)}_{max(bea_years)}.csv'
            df_qcew.to_csv(output_file, index=False)
            print(f"  Saved to: {output_file}")

        except Exception as e:
            print(f"✗ Failed to collect QCEW data: {e}")
            results['qcew'] = {'success': False, 'error': str(e)}
    else:
        print("Skipping QCEW data collection")
        results['qcew'] = {'success': False, 'error': 'Skipped by user'}

    # ======================
    # Summary
    # ======================
    print("\n" + "=" * 80)
    print("DATA COLLECTION SUMMARY")
    print("=" * 80)

    for measure, result in results.items():
        status = "✓" if result['success'] else "✗"
        print(f"{status} {measure}: ", end="")
        if result['success']:
            print(f"{result['records']} records -> {result['file']}")
        else:
            print(f"Failed - {result.get('error', 'Unknown error')}")

    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Save summary
    summary_file = PROCESSED_DATA_DIR / 'component1_collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'states': list(STATE_FIPS.keys()),
            'bea_years': bea_years,
            'acs_years': acs_years,
            'results': results
        }, f, indent=2)

    print(f"\nSummary saved to: {summary_file}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Collect Component Index 1 data')
    parser.add_argument('--skip-bls', action='store_true',
                       help='Skip BLS QCEW data collection (faster)')
    args = parser.parse_args()

    main(skip_bls=args.skip_bls)
