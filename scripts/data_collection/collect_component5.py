"""
Component Index 5: Education & Skill - Data Collection Script

Collects ALL 5 measures for Component Index 5 for all counties in 10 states:
5.1 High School Attainment Rate (Census ACS B15003 - exclusive category)
5.2 Associate's Degree Attainment Rate (Census ACS B15003 - exclusive category)
5.3 College Attainment Rate - Bachelor's (Census ACS B15003 - exclusive category)
5.4 Labor Force Participation Rate (Census ACS B23025)
5.5 Percent of Knowledge Workers (Census ACS C24030)

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


def collect_education_attainment(census_client, year, state_fips_list):
    """
    Collect detailed educational attainment data (Measures 5.1, 5.2, 5.3).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with educational attainment data
    """
    print(f"\nCollecting Census ACS {year} Educational Attainment (Measures 5.1, 5.2, 5.3)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_education_detailed(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_education_detailed_{year}_{state_name}.json"
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


def collect_labor_force(census_client, year, state_fips_list):
    """
    Collect labor force participation data (Measure 5.4).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with labor force data
    """
    print(f"\nCollecting Census ACS {year} Labor Force Participation (Measure 5.4)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_labor_force_participation(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_labor_force_{year}_{state_name}.json"
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


def collect_knowledge_workers(census_client, year, state_fips_list):
    """
    Collect knowledge worker data (Measure 5.5).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with knowledge worker data
    """
    print(f"\nCollecting Census ACS {year} Knowledge Workers (Measure 5.5)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_knowledge_workers(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_knowledge_workers_{year}_{state_name}.json"
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


def process_and_save_data(df_education, df_labor_force, df_knowledge):
    """
    Process and save all Component 5 data.

    Args:
        df_education: Educational attainment DataFrame
        df_labor_force: Labor force participation DataFrame
        df_knowledge: Knowledge workers DataFrame
    """
    print("\nProcessing and Saving Data...")
    print("=" * 60)

    processed_dir = PROCESSED_DATA_DIR
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Measures 5.1, 5.2, 5.3: Educational Attainment (exclusive categories)
    if not df_education.empty:
        df_edu = df_education.copy()

        # Create FIPS code
        df_edu['fips'] = df_edu['state'] + df_edu['county']

        # Convert to numeric
        df_edu['total_25_plus'] = pd.to_numeric(df_edu['B15003_001E'], errors='coerce')
        df_edu['hs_diploma'] = pd.to_numeric(df_edu['B15003_017E'], errors='coerce')
        df_edu['ged'] = pd.to_numeric(df_edu['B15003_018E'], errors='coerce')
        df_edu['associates'] = pd.to_numeric(df_edu['B15003_021E'], errors='coerce')
        df_edu['bachelors'] = pd.to_numeric(df_edu['B15003_022E'], errors='coerce')

        # Calculate percentages (exclusive categories - highest level only)
        df_edu['pct_hs_only'] = ((df_edu['hs_diploma'] + df_edu['ged']) / df_edu['total_25_plus'] * 100)
        df_edu['pct_associates_only'] = (df_edu['associates'] / df_edu['total_25_plus'] * 100)
        df_edu['pct_bachelors_only'] = (df_edu['bachelors'] / df_edu['total_25_plus'] * 100)

        # Select relevant columns
        df_edu_final = df_edu[[
            'fips', 'NAME', 'total_25_plus',
            'hs_diploma', 'ged', 'associates', 'bachelors',
            'pct_hs_only', 'pct_associates_only', 'pct_bachelors_only'
        ]]

        output_file = processed_dir / 'census_education_attainment_2022.csv'
        df_edu_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_edu_final)}")
        print(f"  Average % HS only: {df_edu_final['pct_hs_only'].mean():.2f}%")
        print(f"  Average % Associates only: {df_edu_final['pct_associates_only'].mean():.2f}%")
        print(f"  Average % Bachelors only: {df_edu_final['pct_bachelors_only'].mean():.2f}%")

    # Measure 5.4: Labor Force Participation Rate
    if not df_labor_force.empty:
        df_lf = df_labor_force.copy()

        # Create FIPS code
        df_lf['fips'] = df_lf['state'] + df_lf['county']

        # Convert to numeric
        df_lf['total_16_plus'] = pd.to_numeric(df_lf['B23025_001E'], errors='coerce')
        df_lf['in_labor_force'] = pd.to_numeric(df_lf['B23025_002E'], errors='coerce')

        # Calculate labor force participation rate
        df_lf['labor_force_participation_rate'] = (
            df_lf['in_labor_force'] / df_lf['total_16_plus'] * 100
        )

        # Select relevant columns
        df_lf_final = df_lf[['fips', 'NAME', 'total_16_plus', 'in_labor_force', 'labor_force_participation_rate']]

        output_file = processed_dir / 'census_labor_force_2022.csv'
        df_lf_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_lf_final)}")
        print(f"  Average labor force participation rate: {df_lf_final['labor_force_participation_rate'].mean():.2f}%")

    # Measure 5.5: Percent of Knowledge Workers
    if not df_knowledge.empty:
        df_kw = df_knowledge.copy()

        # Create FIPS code
        df_kw['fips'] = df_kw['state'] + df_kw['county']

        # Convert to numeric
        df_kw['total_employed'] = pd.to_numeric(df_kw['S2401_C01_001E'], errors='coerce')
        df_kw['mgmt_prof_sci_arts'] = pd.to_numeric(df_kw['S2401_C01_002E'], errors='coerce')

        # Calculate percentage
        # Using management/professional/science/arts occupations as proxy for knowledge workers
        df_kw['pct_knowledge_workers'] = (
            df_kw['mgmt_prof_sci_arts'] / df_kw['total_employed'] * 100
        )

        # Select relevant columns
        df_kw_final = df_kw[[
            'fips', 'NAME', 'total_employed',
            'mgmt_prof_sci_arts', 'pct_knowledge_workers'
        ]]

        output_file = processed_dir / 'census_knowledge_workers_2022.csv'
        df_kw_final.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        print(f"  Records: {len(df_kw_final)}")
        print(f"  Average % knowledge workers: {df_kw_final['pct_knowledge_workers'].mean():.2f}%")


def create_summary(df_education, df_labor_force, df_knowledge):
    """Create and save collection summary."""
    summary = {
        'component': 'Component 5: Education & Skill Index',
        'collection_date': datetime.now().isoformat(),
        'measures': {
            '5.1_hs_attainment': {
                'description': 'High school attainment rate (exclusive - HS/GED as highest level)',
                'data_source': '2022 ACS 5-year (Table B15003)',
                'records': len(df_education) if not df_education.empty else 0
            },
            '5.2_associates_attainment': {
                'description': "Associate's degree attainment rate (exclusive - Associate's as highest level)",
                'data_source': '2022 ACS 5-year (Table B15003)',
                'records': len(df_education) if not df_education.empty else 0
            },
            '5.3_bachelors_attainment': {
                'description': "Bachelor's degree attainment rate (exclusive - Bachelor's as highest level)",
                'data_source': '2022 ACS 5-year (Table B15003)',
                'records': len(df_education) if not df_education.empty else 0
            },
            '5.4_labor_force_participation': {
                'description': 'Labor force participation rate (% of 16+ population)',
                'data_source': '2022 ACS 5-year (Table B23025)',
                'records': len(df_labor_force) if not df_labor_force.empty else 0
            },
            '5.5_knowledge_workers': {
                'description': 'Percent of knowledge workers (info, finance, professional, education/health)',
                'data_source': '2022 ACS 5-year (Table C24030)',
                'records': len(df_knowledge) if not df_knowledge.empty else 0
            }
        },
        'total_records': sum([
            len(df_education) if not df_education.empty else 0,
            len(df_labor_force) if not df_labor_force.empty else 0,
            len(df_knowledge) if not df_knowledge.empty else 0
        ])
    }

    output_file = PROCESSED_DATA_DIR / 'component5_collection_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Saved collection summary: {output_file}")
    return summary


def main():
    """Main execution function."""
    print("=" * 60)
    print("Component Index 5: Education & Skill")
    print("Data Collection Script")
    print("=" * 60)

    # Initialize client
    census_client = CensusClient()

    # Define state FIPS codes to collect
    state_fips_list = list(STATE_FIPS.values())

    # Year to collect
    year = 2022  # Most recent ACS 5-year (2018-2022)

    try:
        # Measures 5.1, 5.2, 5.3: Educational Attainment
        df_education = collect_education_attainment(census_client, year, state_fips_list)

        # Measure 5.4: Labor Force Participation
        df_labor_force = collect_labor_force(census_client, year, state_fips_list)

        # Measure 5.5: Knowledge Workers
        df_knowledge = collect_knowledge_workers(census_client, year, state_fips_list)

        # Process and save all data
        process_and_save_data(df_education, df_labor_force, df_knowledge)

        # Create summary
        summary = create_summary(df_education, df_labor_force, df_knowledge)

        print("\n" + "=" * 60)
        print("Component 5 Data Collection Complete!")
        print("=" * 60)
        print(f"Total records collected: {summary['total_records']}")
        print("\nNext steps:")
        print("1. Review processed CSV files in data/processed/")
        print("2. Validate data quality and completeness")
        print("3. Proceed to Component 6 data collection")

    except Exception as e:
        print(f"\n✗ Error during data collection: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
