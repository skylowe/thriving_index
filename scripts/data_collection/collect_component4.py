"""
Component Index 4: Demographic Growth & Renewal - Data Collection Script

Collects ALL 6 measures for Component Index 4 for all counties in 10 states:
4.1 Long-Run Population Growth (Census 2000 + ACS 2022)
4.2 Dependency Ratio (Census ACS - age distribution)
4.3 Median Age (Census ACS)
4.4 Millennial and Gen Z Balance Change (Census ACS - two periods)
4.5 Percent Hispanic (Census ACS)
4.6 Percent Non-White (Census ACS)

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


def collect_population_2000(census_client, state_fips_list):
    """
    Collect 2000 Decennial Census population data (Measure 4.1 - baseline).

    Args:
        census_client: CensusClient instance
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with 2000 population data
    """
    print("\nCollecting Census 2000 Population Data (Measure 4.1 - baseline)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_decennial_population_2000(state_fips=state_fips)

            # Save raw response
            filename = f"census_population_2000_{state_name}.json"
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


def collect_population_current(census_client, year, state_fips_list):
    """
    Collect current ACS population data (Measure 4.1 - current).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with current population data
    """
    print(f"\nCollecting Census ACS {year} Population Data (Measure 4.1 - current)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_population_total(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_population_{year}_{state_name}.json"
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


def collect_age_distribution(census_client, year, state_fips_list):
    """
    Collect detailed age distribution data for dependency ratio (Measure 4.2).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with age distribution data
    """
    print(f"\nCollecting Census ACS {year} Age Distribution (Measure 4.2)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_age_distribution(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_age_distribution_{year}_{state_name}.json"
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


def collect_median_age(census_client, year, state_fips_list):
    """
    Collect median age data (Measure 4.3).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with median age data
    """
    print(f"\nCollecting Census ACS {year} Median Age (Measure 4.3)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_median_age(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_median_age_{year}_{state_name}.json"
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


def collect_hispanic_data(census_client, year, state_fips_list):
    """
    Collect Hispanic/Latino population data (Measure 4.5).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with Hispanic data
    """
    print(f"\nCollecting Census ACS {year} Hispanic Data (Measure 4.5)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_hispanic_data(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_hispanic_{year}_{state_name}.json"
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


def collect_race_data(census_client, year, state_fips_list):
    """
    Collect race distribution data for non-white percentage (Measure 4.6).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with race data
    """
    print(f"\nCollecting Census ACS {year} Race Data (Measure 4.6)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_race_data(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_race_{year}_{state_name}.json"
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


def process_and_save_data(df_2000, df_2022, df_age_2022, df_age_2017, df_median_2022,
                          df_hispanic_2022, df_race_2022):
    """
    Process and save all Component 4 data.

    Args:
        df_2000: 2000 population DataFrame
        df_2022: 2022 population DataFrame
        df_age_2022: 2022 age distribution DataFrame
        df_age_2017: 2017 age distribution DataFrame (for Millennial/Gen Z change)
        df_median_2022: 2022 median age DataFrame
        df_hispanic_2022: 2022 Hispanic data DataFrame
        df_race_2022: 2022 race data DataFrame
    """
    print("\nProcessing and Saving Data...")
    print("=" * 60)

    processed_dir = PROCESSED_DATA_DIR
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Measure 4.1: Long-run population growth
    if not df_2000.empty and not df_2022.empty:
        # Rename columns for clarity
        df_2000_clean = df_2000.rename(columns={'P001001': 'population_2000'})
        df_2022_clean = df_2022.rename(columns={'B01001_001E': 'population_2022'})

        # Create FIPS code for merging
        df_2000_clean['fips'] = df_2000_clean['state'] + df_2000_clean['county']
        df_2022_clean['fips'] = df_2022_clean['state'] + df_2022_clean['county']

        # Merge and calculate growth
        df_growth = pd.merge(
            df_2000_clean[['fips', 'NAME', 'population_2000']],
            df_2022_clean[['fips', 'population_2022']],
            on='fips',
            how='outer'
        )

        # Convert to numeric
        df_growth['population_2000'] = pd.to_numeric(df_growth['population_2000'], errors='coerce')
        df_growth['population_2022'] = pd.to_numeric(df_growth['population_2022'], errors='coerce')

        # Calculate percent change
        df_growth['population_growth_pct'] = (
            (df_growth['population_2022'] - df_growth['population_2000']) /
            df_growth['population_2000'] * 100
        )

        output_file = processed_dir / 'census_population_growth_2000_2022.csv'
        df_growth.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_growth)}")
        print(f"  Average growth: {df_growth['population_growth_pct'].mean():.2f}%")

    # Measure 4.2: Dependency ratio (from age distribution)
    if not df_age_2022.empty:
        # Calculate dependency ratio: (under 15 + 65+) / (15-64)
        df_dep = df_age_2022.copy()

        # Create FIPS code
        df_dep['fips'] = df_dep['state'] + df_dep['county']

        # Convert age columns to numeric
        age_cols = [col for col in df_dep.columns if col.startswith('B01001_') and col != 'B01001_001E']
        for col in age_cols:
            df_dep[col] = pd.to_numeric(df_dep[col], errors='coerce')

        # Calculate age groups
        # Under 15: Male (003-005) + Female (027-029)
        df_dep['under_15'] = (
            df_dep['B01001_003E'] + df_dep['B01001_004E'] + df_dep['B01001_005E'] +  # Male
            df_dep['B01001_027E'] + df_dep['B01001_028E'] + df_dep['B01001_029E']    # Female
        )

        # 65 and over: Male (020-025) + Female (044-049)
        df_dep['age_65_plus'] = (
            df_dep['B01001_020E'] + df_dep['B01001_021E'] + df_dep['B01001_022E'] +
            df_dep['B01001_023E'] + df_dep['B01001_024E'] + df_dep['B01001_025E'] +  # Male
            df_dep['B01001_044E'] + df_dep['B01001_045E'] + df_dep['B01001_046E'] +
            df_dep['B01001_047E'] + df_dep['B01001_048E'] + df_dep['B01001_049E']    # Female
        )

        # Total population
        df_dep['total_population'] = pd.to_numeric(df_dep['B01001_001E'], errors='coerce')

        # Working age (15-64) = Total - Under 15 - 65+
        df_dep['age_15_64'] = df_dep['total_population'] - df_dep['under_15'] - df_dep['age_65_plus']

        # Dependency ratio
        df_dep['dependency_ratio'] = (
            (df_dep['under_15'] + df_dep['age_65_plus']) / df_dep['age_15_64']
        )

        # Select relevant columns
        df_dep_final = df_dep[['fips', 'NAME', 'total_population', 'under_15', 'age_15_64',
                                'age_65_plus', 'dependency_ratio']]

        output_file = processed_dir / 'census_dependency_ratio_2022.csv'
        df_dep_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_dep_final)}")
        print(f"  Average dependency ratio: {df_dep_final['dependency_ratio'].mean():.3f}")

    # Measure 4.3: Median age
    if not df_median_2022.empty:
        df_median = df_median_2022.copy()
        df_median['fips'] = df_median['state'] + df_median['county']
        df_median['median_age'] = pd.to_numeric(df_median['B01002_001E'], errors='coerce')

        df_median_final = df_median[['fips', 'NAME', 'median_age']]

        output_file = processed_dir / 'census_median_age_2022.csv'
        df_median_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_median_final)}")
        print(f"  Average median age: {df_median_final['median_age'].mean():.1f} years")

    # Measure 4.4: Millennial and Gen Z balance change
    if not df_age_2022.empty and not df_age_2017.empty:
        # For 2022 (2018-2022 ACS): Born 1985+ = age 0-37 in 2022
        # For 2017 (2013-2017 ACS): Born 1985+ = age 0-32 in 2017

        # 2022: Calculate percentage age 0-37
        df_millennial_2022 = df_age_2022.copy()
        df_millennial_2022['fips'] = df_millennial_2022['state'] + df_millennial_2022['county']

        # Age 0-37 includes: Under 5, 5-9, 10-14, 15-17, 18-19, 20, 21, 22-24, 25-29, 30-34, 35-39 (partial)
        # Approximate using available age groups (0-39 is close enough)
        age_cols_2022 = [col for col in df_millennial_2022.columns if col.startswith('B01001_') and col != 'B01001_001E']
        for col in age_cols_2022:
            df_millennial_2022[col] = pd.to_numeric(df_millennial_2022[col], errors='coerce')

        # Ages 0-39 (close approximation for ages 0-37)
        # Male: 003-013, Female: 027-037
        df_millennial_2022['millennial_genz_2022'] = (
            df_millennial_2022['B01001_003E'] + df_millennial_2022['B01001_004E'] +
            df_millennial_2022['B01001_005E'] + df_millennial_2022['B01001_006E'] +
            df_millennial_2022['B01001_007E'] + df_millennial_2022['B01001_008E'] +
            df_millennial_2022['B01001_009E'] + df_millennial_2022['B01001_010E'] +
            df_millennial_2022['B01001_011E'] + df_millennial_2022['B01001_012E'] +
            df_millennial_2022['B01001_013E'] +  # Male 0-39
            df_millennial_2022['B01001_027E'] + df_millennial_2022['B01001_028E'] +
            df_millennial_2022['B01001_029E'] + df_millennial_2022['B01001_030E'] +
            df_millennial_2022['B01001_031E'] + df_millennial_2022['B01001_032E'] +
            df_millennial_2022['B01001_033E'] + df_millennial_2022['B01001_034E'] +
            df_millennial_2022['B01001_035E'] + df_millennial_2022['B01001_036E'] +
            df_millennial_2022['B01001_037E']    # Female 0-39
        )

        df_millennial_2022['total_pop_2022'] = pd.to_numeric(df_millennial_2022['B01001_001E'], errors='coerce')
        df_millennial_2022['pct_millennial_genz_2022'] = (
            df_millennial_2022['millennial_genz_2022'] / df_millennial_2022['total_pop_2022'] * 100
        )

        # Similar for 2017
        df_millennial_2017 = df_age_2017.copy()
        df_millennial_2017['fips'] = df_millennial_2017['state'] + df_millennial_2017['county']

        age_cols_2017 = [col for col in df_millennial_2017.columns if col.startswith('B01001_') and col != 'B01001_001E']
        for col in age_cols_2017:
            df_millennial_2017[col] = pd.to_numeric(df_millennial_2017[col], errors='coerce')

        # For 2017: age 0-32, use 0-34 as approximation (includes 25-29, 30-34)
        df_millennial_2017['millennial_genz_2017'] = (
            df_millennial_2017['B01001_003E'] + df_millennial_2017['B01001_004E'] +
            df_millennial_2017['B01001_005E'] + df_millennial_2017['B01001_006E'] +
            df_millennial_2017['B01001_007E'] + df_millennial_2017['B01001_008E'] +
            df_millennial_2017['B01001_009E'] + df_millennial_2017['B01001_010E'] +
            df_millennial_2017['B01001_011E'] + df_millennial_2017['B01001_012E'] +  # Male 0-34
            df_millennial_2017['B01001_027E'] + df_millennial_2017['B01001_028E'] +
            df_millennial_2017['B01001_029E'] + df_millennial_2017['B01001_030E'] +
            df_millennial_2017['B01001_031E'] + df_millennial_2017['B01001_032E'] +
            df_millennial_2017['B01001_033E'] + df_millennial_2017['B01001_034E'] +
            df_millennial_2017['B01001_035E'] + df_millennial_2017['B01001_036E']    # Female 0-34
        )

        df_millennial_2017['total_pop_2017'] = pd.to_numeric(df_millennial_2017['B01001_001E'], errors='coerce')
        df_millennial_2017['pct_millennial_genz_2017'] = (
            df_millennial_2017['millennial_genz_2017'] / df_millennial_2017['total_pop_2017'] * 100
        )

        # Merge and calculate change
        df_millennial_change = pd.merge(
            df_millennial_2017[['fips', 'pct_millennial_genz_2017']],
            df_millennial_2022[['fips', 'NAME', 'pct_millennial_genz_2022']],
            on='fips',
            how='outer'
        )

        df_millennial_change['millennial_genz_balance_change'] = (
            df_millennial_change['pct_millennial_genz_2022'] -
            df_millennial_change['pct_millennial_genz_2017']
        )

        output_file = processed_dir / 'census_millennial_genz_change_2017_2022.csv'
        df_millennial_change.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_millennial_change)}")
        print(f"  Average change: {df_millennial_change['millennial_genz_balance_change'].mean():.2f} percentage points")

    # Measure 4.5: Percent Hispanic
    if not df_hispanic_2022.empty:
        df_hispanic = df_hispanic_2022.copy()
        df_hispanic['fips'] = df_hispanic['state'] + df_hispanic['county']
        df_hispanic['total_population'] = pd.to_numeric(df_hispanic['B03003_001E'], errors='coerce')
        df_hispanic['hispanic_population'] = pd.to_numeric(df_hispanic['B03003_003E'], errors='coerce')
        df_hispanic['pct_hispanic'] = (
            df_hispanic['hispanic_population'] / df_hispanic['total_population'] * 100
        )

        df_hispanic_final = df_hispanic[['fips', 'NAME', 'total_population', 'hispanic_population', 'pct_hispanic']]

        output_file = processed_dir / 'census_hispanic_2022.csv'
        df_hispanic_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_hispanic_final)}")
        print(f"  Average % Hispanic: {df_hispanic_final['pct_hispanic'].mean():.2f}%")

    # Measure 4.6: Percent Non-White
    if not df_race_2022.empty:
        df_race = df_race_2022.copy()
        df_race['fips'] = df_race['state'] + df_race['county']
        df_race['total_population'] = pd.to_numeric(df_race['B02001_001E'], errors='coerce')
        df_race['white_alone'] = pd.to_numeric(df_race['B02001_002E'], errors='coerce')
        df_race['non_white'] = df_race['total_population'] - df_race['white_alone']
        df_race['pct_non_white'] = (
            df_race['non_white'] / df_race['total_population'] * 100
        )

        df_race_final = df_race[['fips', 'NAME', 'total_population', 'white_alone', 'non_white', 'pct_non_white']]

        output_file = processed_dir / 'census_race_2022.csv'
        df_race_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_race_final)}")
        print(f"  Average % Non-White: {df_race_final['pct_non_white'].mean():.2f}%")


def create_summary(df_2000, df_2022, df_age_2022, df_age_2017, df_median_2022,
                   df_hispanic_2022, df_race_2022):
    """Create and save collection summary."""
    summary = {
        'component': 'Component 4: Demographic Growth & Renewal Index',
        'collection_date': datetime.now().isoformat(),
        'measures': {
            '4.1_population_growth': {
                'description': 'Long-run population growth (2000 to 2022)',
                'data_sources': '2000 Decennial Census + 2022 ACS 5-year',
                'records_2000': len(df_2000) if not df_2000.empty else 0,
                'records_2022': len(df_2022) if not df_2022.empty else 0
            },
            '4.2_dependency_ratio': {
                'description': 'Dependency ratio (under 15 + 65+) / (15-64)',
                'data_source': '2022 ACS 5-year (Table B01001)',
                'records': len(df_age_2022) if not df_age_2022.empty else 0
            },
            '4.3_median_age': {
                'description': 'Median age of population',
                'data_source': '2022 ACS 5-year (Table B01002)',
                'records': len(df_median_2022) if not df_median_2022.empty else 0
            },
            '4.4_millennial_genz_change': {
                'description': 'Change in share of Millennials and Gen Z (born 1985+)',
                'data_sources': '2017 and 2022 ACS 5-year (Table B01001)',
                'records_2017': len(df_age_2017) if not df_age_2017.empty else 0,
                'records_2022': len(df_age_2022) if not df_age_2022.empty else 0
            },
            '4.5_percent_hispanic': {
                'description': 'Percent of population that is Hispanic or Latino',
                'data_source': '2022 ACS 5-year (Table B03003)',
                'records': len(df_hispanic_2022) if not df_hispanic_2022.empty else 0
            },
            '4.6_percent_non_white': {
                'description': 'Percent of population that is non-white',
                'data_source': '2022 ACS 5-year (Table B02001)',
                'records': len(df_race_2022) if not df_race_2022.empty else 0
            }
        },
        'total_records': sum([
            len(df_2000) if not df_2000.empty else 0,
            len(df_2022) if not df_2022.empty else 0,
            len(df_age_2022) if not df_age_2022.empty else 0,
            len(df_age_2017) if not df_age_2017.empty else 0,
            len(df_median_2022) if not df_median_2022.empty else 0,
            len(df_hispanic_2022) if not df_hispanic_2022.empty else 0,
            len(df_race_2022) if not df_race_2022.empty else 0
        ])
    }

    output_file = PROCESSED_DATA_DIR / 'component4_collection_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Saved collection summary: {output_file}")
    return summary


def main():
    """Main execution function."""
    print("=" * 60)
    print("Component Index 4: Demographic Growth & Renewal")
    print("Data Collection Script")
    print("=" * 60)

    # Initialize client
    census_client = CensusClient()

    # Define state FIPS codes to collect
    state_fips_list = list(STATE_FIPS.values())

    # Years to collect
    year_current = 2022  # Most recent ACS 5-year (2018-2022)
    year_earlier = 2017  # Earlier ACS 5-year (2013-2017) for Millennial/Gen Z change

    try:
        # Measure 4.1: Long-run population growth (2000 baseline)
        df_2000 = collect_population_2000(census_client, state_fips_list)

        # Measure 4.1: Long-run population growth (2022 current)
        df_2022 = collect_population_current(census_client, year_current, state_fips_list)

        # Measure 4.2: Dependency ratio (2022 age distribution)
        df_age_2022 = collect_age_distribution(census_client, year_current, state_fips_list)

        # Measure 4.4: Millennial/Gen Z change (2017 age distribution for baseline)
        df_age_2017 = collect_age_distribution(census_client, year_earlier, state_fips_list)

        # Measure 4.3: Median age (2022)
        df_median_2022 = collect_median_age(census_client, year_current, state_fips_list)

        # Measure 4.5: Percent Hispanic (2022)
        df_hispanic_2022 = collect_hispanic_data(census_client, year_current, state_fips_list)

        # Measure 4.6: Percent Non-White (2022)
        df_race_2022 = collect_race_data(census_client, year_current, state_fips_list)

        # Process and save all data
        process_and_save_data(
            df_2000, df_2022, df_age_2022, df_age_2017, df_median_2022,
            df_hispanic_2022, df_race_2022
        )

        # Create summary
        summary = create_summary(
            df_2000, df_2022, df_age_2022, df_age_2017, df_median_2022,
            df_hispanic_2022, df_race_2022
        )

        print("\n" + "=" * 60)
        print("Component 4 Data Collection Complete!")
        print("=" * 60)
        print(f"Total records collected: {summary['total_records']}")
        print("\nNext steps:")
        print("1. Review processed CSV files in data/processed/")
        print("2. Validate data quality and completeness")
        print("3. Proceed to Component 5 data collection")

    except Exception as e:
        print(f"\n✗ Error during data collection: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
