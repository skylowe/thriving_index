"""
Component Index 2: Economic Opportunity & Diversity - Data Collection Script

Collects 6 of 7 measures for Component Index 2 for all counties in 10 states:
2.2 Non-Farm Proprietors Per 1,000 Persons (BEA CAEMP25)
2.3 Employer Establishments Per 1,000 Residents (Census CBP)
2.4 Share of Workers in Non-Employer Establishment (Census NES + CBP)
2.5 Industry Diversity (Census CBP)
2.6 Occupation Diversity (Census ACS)
2.7 Share of Telecommuters (Census ACS)

Note: Measure 2.1 (Entrepreneurial Activity via BDS) is skipped for now (MEDIUM confidence).

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
from api_clients.cbp_client import CBPClient
from api_clients.nonemp_client import NonempClient
from api_clients.census_client import CensusClient


def collect_proprietors_data(bea_client, year, state_fips_list):
    """
    Collect non-farm proprietors data from BEA CAEMP25 (Measure 2.2).

    Args:
        bea_client: BEAClient instance
        year: Year of data (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with proprietors data
    """
    print("\nCollecting BEA Non-Farm Proprietors Data (Measure 2.2)...")
    print("-" * 60)

    response = bea_client.get_proprietors_data(year, state_fips_list=state_fips_list, include_farm=False)

    # Save raw response
    filename = f"bea_proprietors_{year}.json"
    bea_client.save_response(response, filename)

    # Extract data
    data = response['BEAAPI']['Results']['Data']
    df = pd.DataFrame(data)

    print(f"✓ Retrieved {len(df)} records")
    print(f"  Year: {year}")
    print(f"  States: {sorted(df['GeoFips'].str[:2].unique())}")

    return df


def collect_cbp_establishments(cbp_client, year, state_fips_list):
    """
    Collect establishment counts from Census CBP (Measure 2.3).

    Args:
        cbp_client: CBPClient instance
        year: Year of data
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with establishment data
    """
    print("\nCollecting Census CBP Establishments Data (Measure 2.3)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = cbp_client.get_establishments(year, state_fips=state_fips, naics='00')

            # Save raw response
            filename = f"cbp_establishments_{state_name}_{year}.json"
            cbp_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = cbp_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    df = pd.DataFrame(all_data)
    print(f"\n✓ Total: {len(df)} records across all states")

    return df


def collect_nonemployer_data(nonemp_client, year, state_fips_list):
    """
    Collect nonemployer statistics from Census (Measure 2.4 part 1).

    Args:
        nonemp_client: NonempClient instance
        year: Year of data
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with nonemployer data
    """
    print("\nCollecting Census Nonemployer Statistics Data (Measure 2.4)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = nonemp_client.get_nonemployer_firms(year, state_fips=state_fips, naics='00')

            # Save raw response
            filename = f"nonemp_firms_{state_name}_{year}.json"
            nonemp_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = nonemp_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    df = pd.DataFrame(all_data)
    print(f"\n✓ Total: {len(df)} records across all states")

    return df


def collect_industry_diversity_data(cbp_client, year, state_fips_list):
    """
    Collect employment by industry from Census CBP for diversity calculation (Measure 2.5).

    Args:
        cbp_client: CBPClient instance
        year: Year of data
        state_fips_list: List of state FIPS codes

    Returns:
        dict: Dictionary mapping NAICS code to DataFrame
    """
    print("\nCollecting Census CBP Industry Employment Data (Measure 2.5)...")
    print("-" * 60)

    industry_data = {}

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"\n  Fetching {state_name} (FIPS {state_fips})...")
        results = cbp_client.get_industry_employment(year, state_fips=state_fips)

        # Save raw response
        filename = f"cbp_industry_employment_{state_name}_{year}.json"
        cbp_client.save_response(results, filename)

        # Store in industry_data dict
        for naics_code, response in results.items():
            if response is not None:
                if naics_code not in industry_data:
                    industry_data[naics_code] = []
                parsed = cbp_client.parse_response_to_dict(response)
                industry_data[naics_code].extend(parsed)

    # Convert to DataFrames
    industry_dfs = {}
    for naics_code, data_list in industry_data.items():
        if data_list:
            industry_dfs[naics_code] = pd.DataFrame(data_list)
            print(f"\n✓ NAICS {naics_code}: {len(data_list)} total records")

    return industry_dfs


def collect_occupation_diversity_data(census_client, year, state_fips_list):
    """
    Collect occupation data from Census ACS for diversity calculation (Measure 2.6).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with occupation data
    """
    print("\nCollecting Census ACS Occupation Data (Measure 2.6)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_occupation_data(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_occupation_{state_name}_{year}.json"
            census_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    df = pd.DataFrame(all_data)
    print(f"\n✓ Total: {len(df)} records across all states")

    return df


def collect_telecommuter_data(census_client, year, state_fips_list):
    """
    Collect telecommuter data from Census ACS (Measure 2.7).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with telecommuter data
    """
    print("\nCollecting Census ACS Telecommuter Data (Measure 2.7)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_telecommuter_data(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_telecommuter_{state_name}_{year}.json"
            census_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    df = pd.DataFrame(all_data)
    print(f"\n✓ Total: {len(df)} records across all states")

    return df


def main():
    """Main data collection function for Component 2."""
    print("=" * 80)
    print("COMPONENT INDEX 2 DATA COLLECTION")
    print("Economic Opportunity & Diversity Index")
    print("=" * 80)
    print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configuration
    cbp_year = 2021  # Most recent CBP data
    nonemp_year = 2021  # Most recent Nonemployer data
    bea_year = 2022  # Most recent BEA data
    acs_year = 2022  # ACS 5-year estimates ending 2022 (2018-2022)

    state_fips_list = list(STATE_FIPS.values())

    print(f"\nData Years:")
    print(f"  BEA Proprietors: {bea_year}")
    print(f"  CBP Establishments & Industry: {cbp_year}")
    print(f"  Nonemployer Statistics: {nonemp_year}")
    print(f"  ACS Occupation & Telecommuter: {acs_year} (5-year estimates)")
    print(f"\nStates: {', '.join(STATE_FIPS.keys())}")
    print()

    # Initialize API clients
    bea_client = BEAClient()
    cbp_client = CBPClient()
    nonemp_client = NonempClient()
    census_client = CensusClient()

    # Collect all measures
    try:
        # Measure 2.2: Non-Farm Proprietors
        proprietors_df = collect_proprietors_data(bea_client, bea_year, state_fips_list)

        # Measure 2.3: Employer Establishments
        establishments_df = collect_cbp_establishments(cbp_client, cbp_year, state_fips_list)

        # Measure 2.4: Nonemployer Statistics
        nonemployer_df = collect_nonemployer_data(nonemp_client, nonemp_year, state_fips_list)

        # Measure 2.5: Industry Diversity
        industry_dfs = collect_industry_diversity_data(cbp_client, cbp_year, state_fips_list)

        # Measure 2.6: Occupation Diversity
        occupation_df = collect_occupation_diversity_data(census_client, acs_year, state_fips_list)

        # Measure 2.7: Telecommuters
        telecommuter_df = collect_telecommuter_data(census_client, acs_year, state_fips_list)

        # Save processed data
        print("\n" + "=" * 80)
        print("SAVING PROCESSED DATA")
        print("=" * 80)

        processed_dir = PROCESSED_DATA_DIR
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Save each dataset
        proprietors_df.to_csv(processed_dir / f'bea_proprietors_{bea_year}.csv', index=False)
        print(f"✓ Saved: bea_proprietors_{bea_year}.csv ({len(proprietors_df)} records)")

        establishments_df.to_csv(processed_dir / f'cbp_establishments_{cbp_year}.csv', index=False)
        print(f"✓ Saved: cbp_establishments_{cbp_year}.csv ({len(establishments_df)} records)")

        nonemployer_df.to_csv(processed_dir / f'nonemp_firms_{nonemp_year}.csv', index=False)
        print(f"✓ Saved: nonemp_firms_{nonemp_year}.csv ({len(nonemployer_df)} records)")

        # Save industry diversity data (each NAICS as separate CSV)
        for naics_code, df in industry_dfs.items():
            filename = f'cbp_industry_naics{naics_code}_{cbp_year}.csv'
            df.to_csv(processed_dir / filename, index=False)
            print(f"✓ Saved: {filename} ({len(df)} records)")

        occupation_df.to_csv(processed_dir / f'census_occupation_{acs_year}.csv', index=False)
        print(f"✓ Saved: census_occupation_{acs_year}.csv ({len(occupation_df)} records)")

        telecommuter_df.to_csv(processed_dir / f'census_telecommuter_{acs_year}.csv', index=False)
        print(f"✓ Saved: census_telecommuter_{acs_year}.csv ({len(telecommuter_df)} records)")

        # Create summary
        summary = {
            'collection_date': datetime.now().isoformat(),
            'component': 'Component 2: Economic Opportunity & Diversity',
            'measures_collected': 6,
            'measures_skipped': ['2.1 Entrepreneurial Activity (BDS - MEDIUM confidence)'],
            'data_years': {
                'bea_proprietors': bea_year,
                'cbp_establishments': cbp_year,
                'cbp_industry': cbp_year,
                'nonemp_firms': nonemp_year,
                'acs_occupation': acs_year,
                'acs_telecommuter': acs_year
            },
            'states': list(STATE_FIPS.keys()),
            'record_counts': {
                'bea_proprietors': len(proprietors_df),
                'cbp_establishments': len(establishments_df),
                'nonemp_firms': len(nonemployer_df),
                'cbp_industry_sectors': len(industry_dfs),
                'census_occupation': len(occupation_df),
                'census_telecommuter': len(telecommuter_df)
            }
        }

        summary_file = processed_dir / 'component2_collection_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Saved: component2_collection_summary.json")

        print("\n" + "=" * 80)
        print("COLLECTION COMPLETE")
        print("=" * 80)
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal records collected:")
        for key, count in summary['record_counts'].items():
            print(f"  {key}: {count:,}")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
