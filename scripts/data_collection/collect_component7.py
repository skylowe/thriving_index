"""
Component Index 7: Quality of Life - Data Collection Script

Collects 4 of 8 measures for Component Index 7 for all counties in 10 states:
7.1 Commute Time (Census ACS S0801)
7.2 Percent of Housing Built Pre-1960 (Census ACS DP04)
7.3 Relative Weekly Wage (BLS QCEW)
7.7 Healthcare Access (Census CBP NAICS 621+622)

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
from api_clients.census_client import CensusClient
from api_clients.cbp_client import CBPClient
from api_clients.qcew_client import QCEWClient


def collect_commute_time(census_client, year, state_fips_list):
    """
    Collect average commute time data (Measure 7.1).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with commute time data
    """
    print(f"\nCollecting Census ACS {year} Commute Time (Measure 7.1)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_commute_time(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_commute_time_{year}_{state_name}.json"
            census_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrame
    df = pd.DataFrame(all_data)
    print(f"\n✓ Total records: {len(df)}")

    return df


def collect_housing_age(census_client, year, state_fips_list):
    """
    Collect housing age data for pre-1960 calculation (Measure 7.2).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with housing age data
    """
    print(f"\nCollecting Census ACS {year} Housing Age (Measure 7.2)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_housing_age(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_housing_age_{year}_{state_name}.json"
            census_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrame
    df = pd.DataFrame(all_data)
    print(f"\n✓ Total records: {len(df)}")

    return df


def collect_relative_weekly_wage(qcew_client, year, state_fips_list):
    """
    Collect weekly wage data for relative wage calculation (Measure 7.3).

    Args:
        qcew_client: QCEWClient instance
        year: Year of data
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with weekly wage data (county and state level)
    """
    print(f"\nCollecting BLS QCEW {year} Weekly Wage Data (Measure 7.3)...")
    print("-" * 60)

    # Get private employment and wages for all states at once
    print("  Fetching QCEW data for all states...")
    try:
        # QCEW client method takes a list of state FIPS codes
        response = qcew_client.get_private_employment_wages(
            year=year,
            state_fips_list=state_fips_list
        )

        print(f"    ✓ Retrieved {len(response)} counties")

    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        response = []

    # Create DataFrame
    df = pd.DataFrame(response)

    # Calculate weekly wage from annual data
    if not df.empty and 'avg_annual_pay' in df.columns:
        df['weekly_wage'] = df['avg_annual_pay'] / 52

    print(f"\n✓ Total records: {len(df)}")

    return df


def collect_healthcare_employment(cbp_client, year, state_fips_list):
    """
    Collect healthcare employment data (Measure 7.7).

    Args:
        cbp_client: CBPClient instance
        year: Year of CBP data
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with healthcare employment data
    """
    print(f"\nCollecting Census CBP {year} Healthcare Employment (Measure 7.7)...")
    print("-" * 60)

    all_ambulatory = []
    all_hospitals = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            results = cbp_client.get_healthcare_employment(year, state_fips=state_fips)

            # Process ambulatory data (NAICS 621)
            if results['ambulatory']:
                filename = f"cbp_healthcare_621_{year}_{state_name}.json"
                cbp_client.save_response(results['ambulatory'], filename)
                parsed = cbp_client.parse_response_to_dict(results['ambulatory'])
                all_ambulatory.extend(parsed)

            # Process hospitals data (NAICS 622)
            if results['hospitals']:
                filename = f"cbp_healthcare_622_{year}_{state_name}.json"
                cbp_client.save_response(results['hospitals'], filename)
                parsed = cbp_client.parse_response_to_dict(results['hospitals'])
                all_hospitals.extend(parsed)

            print(f"    ✓ Retrieved ambulatory: {len(parsed) if results['ambulatory'] else 0}, hospitals: {len(parsed) if results['hospitals'] else 0}")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrames
    df_ambulatory = pd.DataFrame(all_ambulatory)
    df_hospitals = pd.DataFrame(all_hospitals)

    # Merge the two dataframes by county
    # Both should have state, county, NAME columns
    if not df_ambulatory.empty and not df_hospitals.empty:
        # Rename EMP columns to be specific
        df_ambulatory['EMP_ambulatory'] = pd.to_numeric(df_ambulatory['EMP'], errors='coerce')
        df_hospitals['EMP_hospitals'] = pd.to_numeric(df_hospitals['EMP'], errors='coerce')

        # Merge on state and county
        df = pd.merge(
            df_ambulatory[['state', 'county', 'NAME', 'EMP_ambulatory']],
            df_hospitals[['state', 'county', 'EMP_hospitals']],
            on=['state', 'county'],
            how='outer'
        )

        # Fill NaN with 0 (counties that don't have hospitals or ambulatory facilities)
        df['EMP_ambulatory'] = df['EMP_ambulatory'].fillna(0)
        df['EMP_hospitals'] = df['EMP_hospitals'].fillna(0)

        # Calculate total healthcare employment
        df['total_healthcare_employment'] = df['EMP_ambulatory'] + df['EMP_hospitals']

        print(f"\n✓ Total records: {len(df)}")
        return df
    else:
        print("\n✗ Error: Missing data for ambulatory or hospitals")
        return pd.DataFrame()


def process_and_save_data(
    commute_df, housing_df, wage_df, healthcare_df,
    acs_year, cbp_year, qcew_year
):
    """
    Process collected data and save to CSV files.

    Args:
        commute_df: DataFrame with commute time data
        housing_df: DataFrame with housing age data
        wage_df: DataFrame with weekly wage data
        healthcare_df: DataFrame with healthcare employment data
        acs_year: Year of ACS data
        cbp_year: Year of CBP data
        qcew_year: Year of QCEW data

    Returns:
        dict: Summary statistics
    """
    print("\nProcessing and saving Component 7 data...")
    print("=" * 60)

    processed_dir = PROCESSED_DATA_DIR
    processed_dir.mkdir(parents=True, exist_ok=True)

    summary = {}

    # Process 7.1: Commute Time
    if not commute_df.empty:
        commute_df['mean_commute_time'] = pd.to_numeric(
            commute_df['S0801_C01_046E'], errors='coerce'
        )

        output_file = processed_dir / f"census_commute_time_{acs_year}.csv"
        commute_df[['state', 'county', 'NAME', 'mean_commute_time']].to_csv(
            output_file, index=False
        )
        print(f"✓ Saved: {output_file}")

        summary['7.1_commute_time'] = {
            'records': len(commute_df),
            'mean': float(commute_df['mean_commute_time'].mean()),
            'min': float(commute_df['mean_commute_time'].min()),
            'max': float(commute_df['mean_commute_time'].max())
        }

    # Process 7.2: Housing Age (Pre-1960)
    if not housing_df.empty:
        housing_df['total_units'] = pd.to_numeric(housing_df['DP04_0033E'], errors='coerce')
        housing_df['built_1939_earlier'] = pd.to_numeric(housing_df['DP04_0035E'], errors='coerce')
        housing_df['built_1940_1949'] = pd.to_numeric(housing_df['DP04_0036E'], errors='coerce')
        housing_df['built_1950_1959'] = pd.to_numeric(housing_df['DP04_0037E'], errors='coerce')

        housing_df['units_pre_1960'] = (
            housing_df['built_1939_earlier'] +
            housing_df['built_1940_1949'] +
            housing_df['built_1950_1959']
        )
        housing_df['pct_pre_1960'] = (
            housing_df['units_pre_1960'] / housing_df['total_units'] * 100
        )

        output_file = processed_dir / f"census_housing_pre1960_{acs_year}.csv"
        housing_df[['state', 'county', 'NAME', 'pct_pre_1960', 'total_units', 'units_pre_1960']].to_csv(
            output_file, index=False
        )
        print(f"✓ Saved: {output_file}")

        summary['7.2_housing_pre1960'] = {
            'records': len(housing_df),
            'mean': float(housing_df['pct_pre_1960'].mean()),
            'min': float(housing_df['pct_pre_1960'].min()),
            'max': float(housing_df['pct_pre_1960'].max())
        }

    # Process 7.3: Relative Weekly Wage
    if not wage_df.empty:
        # Extract state FIPS from area_fips (first 2 digits)
        wage_df['area_fips_str'] = wage_df['area_fips'].astype(str).str.zfill(5)
        wage_df['state_fips'] = wage_df['area_fips_str'].str[:2]
        wage_df['county_fips'] = wage_df['area_fips_str'].str[2:]

        # Calculate state-level average wages
        state_wages = wage_df.groupby('state_fips')['weekly_wage'].mean().reset_index()
        state_wages.columns = ['state_fips', 'state_avg_weekly_wage']

        # Merge state average back to county data
        wage_df = wage_df.merge(state_wages, on='state_fips', how='left')

        # Calculate relative wage
        wage_df['relative_weekly_wage'] = (
            wage_df['weekly_wage'] / wage_df['state_avg_weekly_wage']
        )

        output_file = processed_dir / f"qcew_relative_weekly_wage_{qcew_year}.csv"
        wage_df[[
            'area_fips', 'state_fips', 'county_fips',
            'weekly_wage', 'state_avg_weekly_wage', 'relative_weekly_wage'
        ]].to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        summary['7.3_relative_wage'] = {
            'records': len(wage_df),
            'mean': float(wage_df['relative_weekly_wage'].mean()),
            'min': float(wage_df['relative_weekly_wage'].min()),
            'max': float(wage_df['relative_weekly_wage'].max())
        }

    # Process 7.7: Healthcare Access
    if not healthcare_df.empty:
        output_file = processed_dir / f"cbp_healthcare_employment_{cbp_year}.csv"
        healthcare_df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        summary['7.7_healthcare_employment'] = {
            'records': len(healthcare_df),
            'mean': float(healthcare_df['total_healthcare_employment'].mean()),
            'min': float(healthcare_df['total_healthcare_employment'].min()),
            'max': float(healthcare_df['total_healthcare_employment'].max())
        }

    # Save summary
    summary['collection_date'] = datetime.now().isoformat()
    summary['acs_year'] = acs_year
    summary['cbp_year'] = cbp_year
    summary['qcew_year'] = qcew_year
    summary['states'] = list(STATE_FIPS.keys())

    summary_file = processed_dir / 'component7_collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved: {summary_file}")

    return summary


def main():
    """Main execution function"""
    print("=" * 60)
    print("Component 7: Quality of Life - Data Collection")
    print("Measures: 7.1, 7.2, 7.3, 7.7")
    print("=" * 60)

    # Configuration
    ACS_YEAR = 2022  # 2018-2022 5-year estimates
    CBP_YEAR = 2021  # Most recent CBP year
    QCEW_YEAR = 2022  # Most recent QCEW year

    # All 10 states
    state_fips_list = list(STATE_FIPS.values())

    # Initialize clients
    print("\nInitializing API clients...")
    census_client = CensusClient()
    cbp_client = CBPClient()
    qcew_client = QCEWClient()
    print("✓ Clients initialized")

    # Collect data for each measure
    try:
        # 7.1: Commute Time
        commute_df = collect_commute_time(census_client, ACS_YEAR, state_fips_list)

        # 7.2: Housing Age (Pre-1960)
        housing_df = collect_housing_age(census_client, ACS_YEAR, state_fips_list)

        # 7.3: Relative Weekly Wage
        wage_df = collect_relative_weekly_wage(qcew_client, QCEW_YEAR, state_fips_list)

        # 7.7: Healthcare Employment
        healthcare_df = collect_healthcare_employment(cbp_client, CBP_YEAR, state_fips_list)

        # Process and save all data
        summary = process_and_save_data(
            commute_df, housing_df, wage_df, healthcare_df,
            ACS_YEAR, CBP_YEAR, QCEW_YEAR
        )

        # Print summary
        print("\n" + "=" * 60)
        print("COLLECTION COMPLETE")
        print("=" * 60)
        print(f"Total measures collected: 4 of 4")
        print(f"\nSummary:")
        for measure, stats in summary.items():
            if measure.startswith('7.'):
                print(f"  {measure}: {stats['records']} records")

    except Exception as e:
        print(f"\n✗ Error during collection: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
