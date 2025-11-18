"""
Component Index 6: Infrastructure & Cost of Doing Business

This script collects data for Component 6 measures:
- 6.2: Interstate Highway Presence (USGS National Map Transportation API)
- 6.3: Count of 4-Year Colleges (Urban Institute IPEDS)
- 6.4: Weekly Wage Rate (BLS QCEW)
- 6.5: Top Marginal Income Tax Rate (Tax Foundation - static data)
- 6.6: Qualified Opportunity Zones (HUD ArcGIS)

Note: Measure 6.1 (Broadband Internet Access) requires FCC data and will be implemented separately.
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import PROCESSED_DATA_DIR, RAW_DATA_DIR, STATE_FIPS
from api_clients.qcew_client import QCEWClient
from api_clients.hud_client import HUDClient
from api_clients.urban_institute_client import UrbanInstituteClient
from api_clients.usgs_client import USGSTransportationClient
from api_clients.fcc_bulk_client import FCCBroadbandBulkClient  # Using bulk download instead of API
from api_clients.census_client import CensusClient

# State income tax rates (2024 tax year)
# Source: Tax Foundation (https://taxfoundation.org/data/all/state/state-income-tax-rates/)
# Researched: 2025-11-17
STATE_INCOME_TAX_RATES = {
    '51': {'name': 'Virginia', 'rate': 5.75, 'note': 'Top marginal rate'},
    '42': {'name': 'Pennsylvania', 'rate': 3.07, 'note': 'Flat rate'},
    '24': {'name': 'Maryland', 'rate': 5.75, 'note': 'Top marginal rate (state-only, excludes local taxes)'},
    '10': {'name': 'Delaware', 'rate': 6.6, 'note': 'Top marginal rate'},
    '54': {'name': 'West Virginia', 'rate': 5.12, 'note': '2024 rate (reduces to 4.82% in 2025)'},
    '21': {'name': 'Kentucky', 'rate': 4.0, 'note': 'Flat rate (reduced from 4.5% in 2023)'},
    '47': {'name': 'Tennessee', 'rate': 0.0, 'note': 'No state income tax'},
    '37': {'name': 'North Carolina', 'rate': 4.5, 'note': 'Flat rate (reduced from 4.75%, will reduce to 3.99% by 2026)'},
    '45': {'name': 'South Carolina', 'rate': 6.4, 'note': 'Top marginal rate (reduced from 6.5%)'},
    '13': {'name': 'Georgia', 'rate': 5.39, 'note': 'Flat rate for 2024 (will reduce to 5.19% in 2025, target 4.99% by 2028)'}
}


def collect_weekly_wage_data(year=2022):
    """
    Collect weekly wage data from BLS QCEW (Measure 6.4).

    Args:
        year: Year to collect (default 2022)

    Returns:
        DataFrame with county-level weekly wage data
    """
    print("\n" + "="*80)
    print("MEASURE 6.4: Weekly Wage Rate")
    print("="*80)
    print(f"Source: BLS QCEW Annual Data")
    print(f"Year: {year}")
    print(f"Metric: Average weekly wage (all industries, total covered)")

    client = QCEWClient()

    # Get state FIPS codes (values from STATE_FIPS dict)
    state_fips_list = list(STATE_FIPS.values())

    print(f"\nCollecting data for {len(state_fips_list)} states...")

    # Collect data for the year
    df = client.get_private_employment_wages(year, state_fips_list)

    if df.empty:
        print("ERROR: No data collected")
        return pd.DataFrame()

    # For this measure, we need total covered employment (not just private)
    # But the QCEW client already gives us private sector data which is fine
    # The weekly wage is in the 'annual_avg_wkly_wage' column

    # Create clean dataframe for this measure
    result = pd.DataFrame({
        'area_fips': df['area_fips'],
        'year': df['year'],
        'avg_weekly_wage': df['annual_avg_wkly_wage']
    })

    # Save raw data
    raw_output = RAW_DATA_DIR / 'qcew' / f'qcew_weekly_wage_{year}.csv'
    result.to_csv(raw_output, index=False)
    print(f"\n✓ Saved raw data: {raw_output}")

    # Save processed data
    processed_output = PROCESSED_DATA_DIR / f'qcew_weekly_wage_{year}.csv'
    result.to_csv(processed_output, index=False)
    print(f"✓ Saved processed data: {processed_output}")

    # Print summary statistics
    print(f"\n--- Summary Statistics ---")
    print(f"Total records: {len(result)}")
    print(f"Counties with data: {result['area_fips'].nunique()}")
    print(f"Average weekly wage: ${result['avg_weekly_wage'].mean():.2f}")
    print(f"Median weekly wage: ${result['avg_weekly_wage'].median():.2f}")
    print(f"Min weekly wage: ${result['avg_weekly_wage'].min():.2f}")
    print(f"Max weekly wage: ${result['avg_weekly_wage'].max():.2f}")

    return result


def collect_tax_rate_data():
    """
    Collect state income tax rate data (Measure 6.5).

    This is static data from Tax Foundation.
    All counties in the same state have the same tax rate.

    Returns:
        DataFrame with state-level tax rates
    """
    print("\n" + "="*80)
    print("MEASURE 6.5: Top Marginal Income Tax Rate")
    print("="*80)
    print(f"Source: Tax Foundation (2024 tax year)")
    print(f"Metric: Top marginal state income tax rate")
    print(f"Note: State-level data; all counties in a state have the same rate")

    # Create DataFrame from the tax rate dictionary
    tax_data = []
    for state_fips, data in STATE_INCOME_TAX_RATES.items():
        tax_data.append({
            'state_fips': state_fips,
            'state_name': data['name'],
            'top_marginal_rate': data['rate'],
            'note': data['note'],
            'tax_year': 2024
        })

    result = pd.DataFrame(tax_data)

    # Save as JSON (raw data)
    raw_output = RAW_DATA_DIR / 'tax_foundation' / 'state_income_tax_rates_2024.json'
    raw_output.parent.mkdir(parents=True, exist_ok=True)

    tax_rates_json = {
        'source': 'Tax Foundation',
        'url': 'https://taxfoundation.org/data/all/state/state-income-tax-rates/',
        'collection_date': '2025-11-17',
        'tax_year': 2024,
        'notes': 'Top marginal state income tax rates for 2024 tax year',
        'rates': STATE_INCOME_TAX_RATES
    }

    with open(raw_output, 'w') as f:
        json.dump(tax_rates_json, f, indent=2)
    print(f"\n✓ Saved raw data: {raw_output}")

    # Save as CSV (processed data)
    processed_output = PROCESSED_DATA_DIR / 'state_income_tax_rates_2024.csv'
    result.to_csv(processed_output, index=False)
    print(f"✓ Saved processed data: {processed_output}")

    # Print summary
    print(f"\n--- Summary Statistics ---")
    print(f"Total states: {len(result)}")
    print(f"Average tax rate: {result['top_marginal_rate'].mean():.2f}%")
    print(f"Median tax rate: {result['top_marginal_rate'].median():.2f}%")
    print(f"Min tax rate: {result['top_marginal_rate'].min():.2f}% ({result[result['top_marginal_rate'] == result['top_marginal_rate'].min()]['state_name'].values[0]})")
    print(f"Max tax rate: {result['top_marginal_rate'].max():.2f}% ({result[result['top_marginal_rate'] == result['top_marginal_rate'].max()]['state_name'].values[0]})")

    print(f"\n--- All State Tax Rates ---")
    for _, row in result.sort_values('top_marginal_rate').iterrows():
        print(f"{row['state_name']:20s}: {row['top_marginal_rate']:5.2f}%  ({row['note']})")

    return result


def collect_opportunity_zones():
    """
    Collect Qualified Opportunity Zones data from HUD ArcGIS API (Measure 6.6).

    Source: HUD Opportunity Zones ArcGIS REST API
    Returns:
        DataFrame with county-level OZ counts
    """
    print("\n" + "="*80)
    print("MEASURE 6.6: Qualified Opportunity Zones")
    print("="*80)
    print(f"Source: HUD Opportunity Zones ArcGIS REST API")
    print(f"Metric: Count of Qualified Opportunity Zone census tracts per county")
    print(f"Note: QOZs designated in 2018 under Tax Cuts and Jobs Act")

    # Initialize HUD client
    client = HUDClient()

    # Get state FIPS codes
    our_states = list(STATE_FIPS.values())

    # Fetch OZ data for our 10 states
    print(f"\nFetching Opportunity Zones for {len(our_states)} states...")
    df_tracts = client.get_opportunity_zones(state_fips_list=our_states)

    # Aggregate to county level
    county_oz_counts = client.aggregate_oz_by_county(df_tracts)

    # Save raw data (tract-level)
    raw_output = RAW_DATA_DIR / 'hud' / 'opportunity_zones_tracts.csv'
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    df_tracts.to_csv(raw_output, index=False)
    print(f"\n✓ Saved raw tract-level data: {raw_output}")

    # Save processed data (county-level counts)
    processed_output = PROCESSED_DATA_DIR / 'hud_opportunity_zones_by_county.csv'
    county_oz_counts.to_csv(processed_output, index=False)
    print(f"✓ Saved processed county-level data: {processed_output}")

    # Print summary statistics
    print(f"\n--- Summary Statistics ---")
    print(f"Total counties with OZs in our 10 states: {len(county_oz_counts)}")
    print(f"Total OZ tracts in our 10 states: {county_oz_counts['oz_tract_count'].sum()}")
    print(f"Average OZ tracts per county: {county_oz_counts['oz_tract_count'].mean():.2f}")
    print(f"Median OZ tracts per county: {county_oz_counts['oz_tract_count'].median():.0f}")
    print(f"Min OZ tracts: {county_oz_counts['oz_tract_count'].min()}")
    print(f"Max OZ tracts: {county_oz_counts['oz_tract_count'].max()}")

    # Show breakdown by state
    print(f"\n--- OZ Tracts by State ---")
    state_summary = df_tracts.groupby(['state_fips', 'state_name']).size().reset_index(name='oz_tracts')
    state_summary = state_summary.sort_values('oz_tracts', ascending=False)
    for _, row in state_summary.iterrows():
        print(f"{row['state_name']:20s}: {row['oz_tracts']:4d} OZ tracts")

    return county_oz_counts


def collect_broadband_data(min_download_speed=100, min_upload_speed=10, as_of_date=None):
    """
    Collect broadband availability data from FCC Broadband Data Collection bulk downloads (Measure 6.1).

    Source: FCC Broadband Data Collection (BDC) - County Summary CSV
    Method: Download bulk county summary file and filter locally

    Args:
        min_download_speed: Minimum download speed in Mbps (default 100)
        min_upload_speed: Minimum upload speed in Mbps (default 10)
        as_of_date: Data collection date (YYYY-MM-DD) or None for latest (default '2024-06-30')

    Returns:
        DataFrame with county-level broadband availability data
    """
    print("\n" + "="*80)
    print("MEASURE 6.1: Broadband Internet Access")
    print("="*80)
    print(f"Source: FCC Broadband Data Collection (BDC) - Bulk Download")
    print(f"Method: Download county summary CSV and filter locally")
    print(f"Metric: Percent of locations with broadband ≥{min_download_speed}/{min_upload_speed} Mbps")

    # Initialize FCC Broadband bulk client
    client = FCCBroadbandBulkClient()

    # Default to June 2024 if not specified
    if not as_of_date:
        as_of_date = '2024-06-30'
        print(f"Using default data date: {as_of_date}")

    # Get state FIPS codes
    state_fips_list = list(STATE_FIPS.values())
    print(f"\nFetching broadband data for {len(state_fips_list)} states...")

    # Download and process broadband data using bulk download approach
    try:
        result = client.get_broadband_availability(
            state_fips_list=state_fips_list,
            min_download_mbps=min_download_speed,
            min_upload_mbps=min_upload_speed,
            as_of_date=as_of_date,
            use_cache=True
        )

    except FileNotFoundError as e:
        # This is expected if the file hasn't been downloaded yet
        print(f"\n{str(e)}")
        print("\nBroadband data collection requires manual download.")
        print("Returning empty DataFrame. Please download the file and re-run.")
        return pd.DataFrame()

    except Exception as e:
        print(f"\nError collecting broadband data: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

    if result.empty:
        print("ERROR: No broadband data collected")
        return pd.DataFrame()

    # Save raw data
    raw_output = RAW_DATA_DIR / 'fcc' / 'bulk' / f'fcc_broadband_{min_download_speed}_{min_upload_speed}.csv'
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(raw_output, index=False)
    print(f"\n✓ Saved raw data: {raw_output}")

    # Save processed data
    processed_output = PROCESSED_DATA_DIR / f'fcc_broadband_availability_{min_download_speed}_{min_upload_speed}.csv'
    result.to_csv(processed_output, index=False)
    print(f"✓ Saved processed data: {processed_output}")

    # Print summary statistics
    print(f"\n--- Summary Statistics ---")
    print(f"Total counties: {len(result)}")
    if 'percent_covered' in result.columns and result['percent_covered'].notna().any():
        print(f"Average broadband coverage: {result['percent_covered'].mean():.2f}%")
        print(f"Median broadband coverage: {result['percent_covered'].median():.2f}%")
        print(f"Min coverage: {result['percent_covered'].min():.2f}%")
        print(f"Max coverage: {result['percent_covered'].max():.2f}%")
    else:
        print("Coverage percentage data not available in API response")

    return result


def collect_interstate_highways():
    """
    Identify counties with interstate highways using USGS National Map Transportation API (Measure 6.2).

    Source: USGS National Map Transportation ArcGIS REST API + Census TIGER county boundaries
    Returns:
        DataFrame with county-level interstate presence (binary indicator)
    """
    print("\n" + "="*80)
    print("MEASURE 6.2: Interstate Highway Presence")
    print("="*80)
    print(f"Source: USGS National Map Transportation API + Census TIGER county boundaries")
    print(f"Metric: Binary indicator (1 = county has interstate, 0 = no interstate)")
    print(f"Note: Uses spatial intersection of interstate geometries with county boundaries")

    # Initialize USGS Transportation client
    client = USGSTransportationClient()

    # Get state FIPS codes
    our_states = list(STATE_FIPS.values())

    # Identify counties with interstates
    print(f"\nAnalyzing interstate highway presence for counties in {len(our_states)} states...")
    print("This will:")
    print("  1. Download all interstate highway geometries from USGS (~194k segments)")
    print("  2. Download Census TIGER 2024 county boundaries")
    print("  3. Perform spatial intersection to identify counties with interstates")
    print("\nThis may take 10-15 minutes...")

    county_interstate_df = client.identify_counties_with_interstates(state_fips_list=our_states)

    # Save raw data (same as processed for this binary indicator)
    raw_output = RAW_DATA_DIR / 'usgs' / 'county_interstate_presence.csv'
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    county_interstate_df.to_csv(raw_output, index=False)
    print(f"\n✓ Saved raw data: {raw_output}")

    # Save processed data
    processed_output = PROCESSED_DATA_DIR / 'usgs_county_interstate_presence.csv'
    county_interstate_df.to_csv(processed_output, index=False)
    print(f"✓ Saved processed data: {processed_output}")

    # Print detailed summary statistics
    total_counties = len(county_interstate_df)
    counties_with_interstate = county_interstate_df['has_interstate'].sum()
    counties_without = total_counties - counties_with_interstate
    pct_with = 100 * counties_with_interstate / total_counties if total_counties > 0 else 0

    print(f"\n--- Summary Statistics ---")
    print(f"Total counties analyzed: {total_counties}")
    print(f"Counties with interstates: {counties_with_interstate} ({pct_with:.1f}%)")
    print(f"Counties without interstates: {counties_without} ({100-pct_with:.1f}%)")

    # Show breakdown by state
    print(f"\n--- Counties with Interstates by State ---")
    state_summary = county_interstate_df.groupby('state_fips').agg({
        'has_interstate': ['sum', 'count']
    }).reset_index()
    state_summary.columns = ['state_fips', 'with_interstate', 'total_counties']
    state_summary['pct_with_interstate'] = 100 * state_summary['with_interstate'] / state_summary['total_counties']

    # Add state names
    state_name_map = {v: k for k, v in STATE_FIPS.items()}
    state_summary['state_name'] = state_summary['state_fips'].map(state_name_map)

    state_summary = state_summary.sort_values('with_interstate', ascending=False)
    for _, row in state_summary.iterrows():
        print(f"{row['state_name']:20s}: {row['with_interstate']:3.0f} / {row['total_counties']:3.0f} counties ({row['pct_with_interstate']:5.1f}%)")

    return county_interstate_df


def collect_four_year_colleges(year=2022):
    """
    Collect 4-year degree-granting college data from Urban Institute IPEDS API (Measure 6.3).

    Source: Urban Institute Education Data Portal (IPEDS directory)
    Args:
        year: Year to collect (default 2022)

    Returns:
        DataFrame with county-level college counts
    """
    print("\n" + "="*80)
    print("MEASURE 6.3: Count of 4-Year Colleges")
    print("="*80)
    print(f"Source: Urban Institute Education Data Portal (IPEDS directory)")
    print(f"Year: {year}")
    print(f"Metric: Count of 4-year degree-granting institutions per county")

    # Initialize Urban Institute client
    client = UrbanInstituteClient()

    # Get state FIPS codes
    our_states = list(STATE_FIPS.values())

    # Fetch college data for our 10 states
    print(f"\nFetching 4-year degree-granting colleges for {len(our_states)} states...")
    df_colleges = client.get_four_year_colleges(year=year, state_fips_list=our_states)

    # Aggregate to county level
    county_college_counts = client.aggregate_colleges_by_county(df_colleges)

    # Save raw data (institution-level)
    raw_output = RAW_DATA_DIR / 'urban_institute' / f'ipeds_four_year_colleges_{year}.csv'
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    df_colleges.to_csv(raw_output, index=False)
    print(f"\n✓ Saved raw institution-level data: {raw_output}")

    # Save processed data (county-level counts)
    processed_output = PROCESSED_DATA_DIR / f'ipeds_four_year_colleges_by_county_{year}.csv'
    county_college_counts.to_csv(processed_output, index=False)
    print(f"✓ Saved processed county-level data: {processed_output}")

    # Print summary statistics
    print(f"\n--- Summary Statistics ---")
    print(f"Total 4-year degree-granting colleges: {len(df_colleges)}")
    print(f"Counties with 4-year colleges: {len(county_college_counts)}")
    print(f"Average colleges per county (counties with colleges): {county_college_counts['college_count'].mean():.2f}")
    print(f"Median colleges per county: {county_college_counts['college_count'].median():.0f}")
    print(f"Min colleges: {county_college_counts['college_count'].min()}")
    print(f"Max colleges: {county_college_counts['college_count'].max()}")

    # Show breakdown by state
    print(f"\n--- Colleges by State ---")
    state_summary = df_colleges.groupby(['state_fips', 'state_abbr']).size().reset_index(name='college_count')
    state_summary = state_summary.sort_values('college_count', ascending=False)
    for _, row in state_summary.iterrows():
        # Get state name from STATE_FIPS
        state_name = [k for k, v in STATE_FIPS.items() if v == row['state_fips']]
        state_name_str = state_name[0] if state_name else row['state_abbr']
        print(f"{state_name_str:20s} ({row['state_abbr']}): {row['college_count']:4d} colleges")

    return county_college_counts


def create_collection_summary(broadband_df, interstate_df, college_df, weekly_wage_df, tax_rate_df, oz_df):
    """Create a summary of Component 6 data collection."""

    # Determine completion status
    measures_collected = 5  # Default (6.2-6.6)
    if not broadband_df.empty:
        measures_collected = 6  # All 6 measures

    completion_pct = (measures_collected / 6) * 100

    summary = {
        'component': 'Component 6: Infrastructure & Cost of Doing Business',
        'collection_date': pd.Timestamp.now().isoformat(),
        'measures_collected': measures_collected,
        'total_measures': 6,
        'completion_percentage': completion_pct,
        'notes': f'{measures_collected} of 6 measures collected.',
        'measures': {
            '6.1_broadband': {
                'name': 'Broadband Internet Access',
                'source': 'FCC Broadband Data Collection (BDC) Public Data API',
                'year': 2024,
                'records': len(broadband_df),
                'counties': len(broadband_df),
                'avg_coverage': float(broadband_df['percent_covered'].mean()) if not broadband_df.empty and 'percent_covered' in broadband_df.columns else None,
                'files': [
                    'data/raw/fcc/fcc_broadband_100_10.csv',
                    'data/processed/fcc_broadband_availability_100_10.csv'
                ]
            },
            '6.2_interstate_highways': {
                'name': 'Interstate Highway Presence',
                'source': 'USGS National Map Transportation API + Census TIGER',
                'year': 2024,
                'records': len(interstate_df),
                'counties': len(interstate_df),
                'counties_with_interstate': int(interstate_df['has_interstate'].sum()) if not interstate_df.empty else 0,
                'pct_with_interstate': float(100 * interstate_df['has_interstate'].mean()) if not interstate_df.empty else 0,
                'files': [
                    'data/raw/usgs/county_interstate_presence.csv',
                    'data/processed/usgs_county_interstate_presence.csv'
                ]
            },
            '6.3_four_year_colleges': {
                'name': 'Count of 4-Year Colleges',
                'source': 'Urban Institute Education Data Portal (IPEDS)',
                'year': 2022,
                'records': len(college_df),
                'counties': len(college_df),
                'total_colleges': int(college_df['college_count'].sum()) if not college_df.empty else 0,
                'avg_colleges_per_county': float(college_df['college_count'].mean()) if not college_df.empty else 0,
                'files': [
                    'data/raw/urban_institute/ipeds_four_year_colleges_2022.csv',
                    'data/processed/ipeds_four_year_colleges_by_county_2022.csv'
                ]
            },
            '6.4_weekly_wage': {
                'name': 'Weekly Wage Rate',
                'source': 'BLS QCEW',
                'year': 2022,
                'records': len(weekly_wage_df),
                'counties': weekly_wage_df['area_fips'].nunique() if not weekly_wage_df.empty else 0,
                'avg_value': float(weekly_wage_df['avg_weekly_wage'].mean()) if not weekly_wage_df.empty else 0,
                'files': [
                    'data/raw/qcew/qcew_weekly_wage_2022.csv',
                    'data/processed/qcew_weekly_wage_2022.csv'
                ]
            },
            '6.5_tax_rate': {
                'name': 'Top Marginal Income Tax Rate',
                'source': 'Tax Foundation',
                'tax_year': 2024,
                'records': len(tax_rate_df),
                'states': len(tax_rate_df),
                'avg_value': float(tax_rate_df['top_marginal_rate'].mean()),
                'files': [
                    'data/raw/tax_foundation/state_income_tax_rates_2024.json',
                    'data/processed/state_income_tax_rates_2024.csv'
                ]
            },
            '6.6_opportunity_zones': {
                'name': 'Qualified Opportunity Zones',
                'source': 'HUD ArcGIS REST API',
                'designation_year': 2018,
                'records': len(oz_df),
                'counties_with_oz': len(oz_df),
                'total_oz_tracts': int(oz_df['oz_tract_count'].sum()) if not oz_df.empty else 0,
                'avg_oz_per_county': float(oz_df['oz_tract_count'].mean()) if not oz_df.empty else 0,
                'files': [
                    'data/raw/hud/opportunity_zones_tracts.csv',
                    'data/processed/hud_opportunity_zones_by_county.csv'
                ]
            }
        }
    }

    # Save summary
    summary_file = PROCESSED_DATA_DIR / 'component6_collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Saved collection summary: {summary_file}")

    return summary


def main():
    """Main function to collect Component 6 data (all 6 measures)."""
    print("="*80)
    print("COMPONENT 6: INFRASTRUCTURE & COST OF DOING BUSINESS INDEX")
    print("Collection: All 6 measures (6.1-6.6)")
    print("="*80)

    # Collect Measure 6.1: Broadband Internet Access
    try:
        broadband_df = collect_broadband_data(min_download_speed=100, min_upload_speed=10)
    except Exception as e:
        print(f"\nWarning: Broadband data collection failed: {str(e)}")
        print("Continuing with remaining measures...")
        broadband_df = pd.DataFrame()  # Empty DataFrame if collection fails

    # Collect Measure 6.2: Interstate Highway Presence
    interstate_df = collect_interstate_highways()

    # Collect Measure 6.3: Count of 4-Year Colleges
    college_df = collect_four_year_colleges(year=2022)

    # Collect Measure 6.4: Weekly Wage Rate
    weekly_wage_df = collect_weekly_wage_data(year=2022)

    # Collect Measure 6.5: Top Marginal Income Tax Rate
    tax_rate_df = collect_tax_rate_data()

    # Collect Measure 6.6: Qualified Opportunity Zones
    oz_df = collect_opportunity_zones()

    # Create collection summary
    summary = create_collection_summary(broadband_df, interstate_df, college_df, weekly_wage_df, tax_rate_df, oz_df)

    print("\n" + "="*80)
    print("COMPONENT 6 DATA COLLECTION COMPLETE")
    print("="*80)
    print(f"Measures collected: {summary['measures_collected']} of 6 ({summary['completion_percentage']:.1f}%)")

    # Calculate total records
    total_records = (
        summary['measures']['6.1_broadband']['records'] +
        summary['measures']['6.2_interstate_highways']['records'] +
        summary['measures']['6.3_four_year_colleges']['records'] +
        summary['measures']['6.4_weekly_wage']['records'] +
        summary['measures']['6.5_tax_rate']['records'] +
        summary['measures']['6.6_opportunity_zones']['records']
    )
    print(f"Total records: {total_records}")

    # Print measure-by-measure summary
    if summary['measures']['6.1_broadband']['records'] > 0:
        avg_coverage = summary['measures']['6.1_broadband']['avg_coverage']
        if avg_coverage is not None:
            print(f"  - Broadband: {summary['measures']['6.1_broadband']['counties']} counties (avg coverage: {avg_coverage:.2f}%)")
        else:
            print(f"  - Broadband: {summary['measures']['6.1_broadband']['counties']} counties")
    else:
        print(f"  - Broadband: Not collected (FCC API key may be missing or invalid)")

    print(f"  - Interstate highways: {summary['measures']['6.2_interstate_highways']['counties']} counties ({summary['measures']['6.2_interstate_highways']['counties_with_interstate']} with interstates)")
    print(f"  - 4-Year Colleges: {summary['measures']['6.3_four_year_colleges']['counties']} counties, {summary['measures']['6.3_four_year_colleges']['total_colleges']} colleges total")
    print(f"  - Weekly wages: {summary['measures']['6.4_weekly_wage']['records']} counties")
    print(f"  - Tax rates: {summary['measures']['6.5_tax_rate']['records']} states")
    print(f"  - Opportunity Zones: {summary['measures']['6.6_opportunity_zones']['counties_with_oz']} counties, {summary['measures']['6.6_opportunity_zones']['total_oz_tracts']} OZ tracts")

    if summary['measures_collected'] < 6:
        print("\nNote: Some measures were not collected. Check error messages above.")

    print("="*80)


if __name__ == '__main__':
    main()
