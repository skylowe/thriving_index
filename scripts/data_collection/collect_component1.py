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
from api_clients.bls_client import BLSClient
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


def collect_bls_qcew_data(client, state_fips_list, years, data_type='employment'):
    """
    Collect BLS QCEW data for multiple states and years.

    Args:
        client: BLSClient instance
        state_fips_list: List of state FIPS codes
        years: List of years
        data_type: 'employment' or 'wages'

    Returns:
        DataFrame with QCEW data
    """
    print(f"\nCollecting BLS QCEW {data_type.title()} Data...")
    print("-" * 60)

    all_data = []
    start_year = min(years)
    end_year = max(years)

    for state_fips in state_fips_list:
        print(f"  Processing state {state_fips}...")

        # Get county list
        counties = get_county_list_for_state(state_fips)
        if not counties:
            print(f"    Skipping state {state_fips} - no counties found")
            continue

        try:
            # Collect data in batches (API limit is 50 series)
            responses = client.get_state_counties_data(
                state_fips,
                counties,
                start_year,
                end_year,
                data_type=data_type
            )

            # Save raw responses
            for i, response in enumerate(responses):
                filename = f"bls_qcew_{data_type}_{state_fips}_batch{i+1}_{start_year}_{end_year}.json"
                client.save_response(response, filename)

                # Extract data from response
                if response.get('status') == 'REQUEST_SUCCEEDED':
                    for series in response['Results']['series']:
                        series_id = series['seriesID']
                        for datapoint in series['data']:
                            all_data.append({
                                'series_id': series_id,
                                'state_fips': state_fips,
                                'year': datapoint['year'],
                                'period': datapoint['period'],
                                'value': datapoint['value'],
                                'footnotes': str(datapoint.get('footnotes', ''))
                            })

            print(f"    ✓ Collected {len(responses)} batch(es)")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    df = pd.DataFrame(all_data)
    print(f"✓ Total records: {len(df)}")

    return df


def main():
    """Main data collection function for Component Index 1"""

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
    bls_client = BLSClient()
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
    # 4. BLS QCEW Private Employment (Measure 1.2)
    # ======================
    print("\n" + "=" * 80)
    print("NOTE: BLS QCEW data collection may take significant time due to API rate limits")
    print("Consider collecting BLS data separately or implementing caching")
    print("=" * 80)

    collect_bls = input("\nCollect BLS QCEW data now? (y/n): ").lower().strip() == 'y'

    if collect_bls:
        try:
            # Private employment (annual average)
            df_emp = collect_bls_qcew_data(bls_client, state_fips_list, bea_years, data_type='employment')
            results['bls_employment'] = {
                'success': True,
                'records': len(df_emp),
                'file': 'bls_qcew_employment_processed.csv'
            }
            output_file = PROCESSED_DATA_DIR / 'bls_qcew_employment_processed.csv'
            df_emp.to_csv(output_file, index=False)
            print(f"  Saved to: {output_file}")

            # Private wages (for wages per job calculation)
            df_wages = collect_bls_qcew_data(bls_client, state_fips_list, bea_years, data_type='wages')
            results['bls_wages'] = {
                'success': True,
                'records': len(df_wages),
                'file': 'bls_qcew_wages_processed.csv'
            }
            output_file = PROCESSED_DATA_DIR / 'bls_qcew_wages_processed.csv'
            df_wages.to_csv(output_file, index=False)
            print(f"  Saved to: {output_file}")

        except Exception as e:
            print(f"✗ Failed to collect BLS QCEW data: {e}")
            results['bls_qcew'] = {'success': False, 'error': str(e)}
    else:
        print("Skipping BLS QCEW data collection")
        results['bls_qcew'] = {'success': False, 'error': 'Skipped by user'}

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
    main()
