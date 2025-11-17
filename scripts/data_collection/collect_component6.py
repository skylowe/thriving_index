"""
Component Index 6: Infrastructure & Cost of Doing Business

This script collects data for Component 6 measures:
- 6.4: Weekly Wage Rate (BLS QCEW)
- 6.5: Top Marginal Income Tax Rate (Tax Foundation - static data)
- 6.6: Qualified Opportunity Zones (HUD ArcGIS)

Note: Other measures (6.1-6.3) require different collection methods and will be implemented separately.
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


def create_collection_summary(weekly_wage_df, tax_rate_df, oz_df):
    """Create a summary of Component 6 data collection (partial)."""
    summary = {
        'component': 'Component 6: Infrastructure & Cost of Doing Business',
        'collection_date': pd.Timestamp.now().isoformat(),
        'measures_collected': 3,
        'total_measures': 6,
        'completion_percentage': 50.0,
        'notes': 'Measures 6.4, 6.5, and 6.6 collected. Measures 6.1-6.3 require different collection methods (FCC, manual GIS, NCES).',
        'measures': {
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
    summary_file = PROCESSED_DATA_DIR / 'component6_partial_collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Saved collection summary: {summary_file}")

    return summary


def main():
    """Main function to collect Component 6 data (partial - measures 6.4, 6.5, and 6.6)."""
    print("="*80)
    print("COMPONENT 6: INFRASTRUCTURE & COST OF DOING BUSINESS INDEX")
    print("Partial Collection: Measures 6.4, 6.5, and 6.6")
    print("="*80)

    # Collect Measure 6.4: Weekly Wage Rate
    weekly_wage_df = collect_weekly_wage_data(year=2022)

    # Collect Measure 6.5: Top Marginal Income Tax Rate
    tax_rate_df = collect_tax_rate_data()

    # Collect Measure 6.6: Qualified Opportunity Zones
    oz_df = collect_opportunity_zones()

    # Create collection summary
    summary = create_collection_summary(weekly_wage_df, tax_rate_df, oz_df)

    print("\n" + "="*80)
    print("COMPONENT 6 PARTIAL DATA COLLECTION COMPLETE")
    print("="*80)
    print(f"Measures collected: 3 of 6 ({summary['completion_percentage']:.1f}%)")
    total_records = (summary['measures']['6.4_weekly_wage']['records'] +
                     summary['measures']['6.5_tax_rate']['records'] +
                     summary['measures']['6.6_opportunity_zones']['records'])
    print(f"Total records: {total_records}")
    print(f"  - Weekly wages: {summary['measures']['6.4_weekly_wage']['records']} counties")
    print(f"  - Tax rates: {summary['measures']['6.5_tax_rate']['records']} states")
    print(f"  - Opportunity Zones: {summary['measures']['6.6_opportunity_zones']['counties_with_oz']} counties, {summary['measures']['6.6_opportunity_zones']['total_oz_tracts']} OZ tracts")
    print("\nRemaining measures:")
    print("  - Measure 6.1: Broadband Internet Access (FCC data)")
    print("  - Measure 6.2: Interstate Highway Presence (manual mapping)")
    print("  - Measure 6.3: Count of 4-Year Colleges (NCES IPEDS)")
    print("="*80)


if __name__ == '__main__':
    main()
