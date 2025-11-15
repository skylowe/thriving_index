#!/usr/bin/env python3
"""
Collect Census County Business Patterns (CBP) data for Growth Index measures.

Growth Index Measures (Nebraska Methodology):
- Private Employment (level, 2022) - Growth Index 1.2
- Growth in Private Wages Per Job (2019-2022) - Growth Index 1.3

Census CBP provides:
- EMP: Total Mid-March Employees (excludes government, self-employed, farm)
- PAYANN: Annual Payroll ($1,000)
- ESTAB: Number of Establishments

Note: CBP excludes government, agricultural production, and most self-employed.
This aligns well with "private employment" definition.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import requests

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger
from src.utils.config import get_api_key

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


def collect_cbp_data(year: int, state_fips: str, api_key: str, logger) -> pd.DataFrame:
    """
    Collect County Business Patterns data for a state.

    Args:
        year: Year to collect
        state_fips: State FIPS code (2 digits)
        api_key: Census API key
        logger: Logger instance

    Returns:
        DataFrame with employment and payroll by county
    """
    logger.debug(f"  Fetching CBP data for state {state_fips}, year {year}")

    # CBP API endpoint
    base_url = f"https://api.census.gov/data/{year}/cbp"

    # Get total employment and payroll for all industries (exclude government)
    params = {
        'get': 'EMP,PAYANN,ESTAB,NAICS2017_LABEL',
        'for': 'county:*',
        'in': f'state:{state_fips}',
        'NAICS2017': '00',  # Total for all sectors (excludes government by design)
        'key': api_key
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) < 2:
            logger.warning(f"  No data returned for state {state_fips}")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        # Create FIPS code
        df['fips'] = df['state'] + df['county']

        # Convert to numeric
        df['EMP'] = pd.to_numeric(df['EMP'], errors='coerce')
        df['PAYANN'] = pd.to_numeric(df['PAYANN'], errors='coerce')
        df['ESTAB'] = pd.to_numeric(df['ESTAB'], errors='coerce')

        # Filter out null values
        df = df[df['EMP'].notna() & (df['EMP'] > 0)].copy()

        logger.debug(f"  Collected {len(df)} counties")
        return df

    except Exception as e:
        logger.error(f"  Error collecting CBP data: {str(e)}")
        return pd.DataFrame()


def calculate_growth_rate(df_start: pd.DataFrame, df_end: pd.DataFrame,
                         value_col: str, growth_col_name: str,
                         years_between: int) -> pd.DataFrame:
    """
    Calculate annualized growth rate between two periods.

    Args:
        df_start: DataFrame with start period data
        df_end: DataFrame with end period data
        value_col: Name of value column
        growth_col_name: Name for growth rate column
        years_between: Number of years between periods

    Returns:
        DataFrame with growth rates
    """
    merged = df_start[['fips', value_col]].merge(
        df_end[['fips', value_col]],
        on='fips',
        how='inner',
        suffixes=('_start', '_end')
    )

    # Calculate annualized growth rate
    merged[growth_col_name] = (
        ((merged[f'{value_col}_end'] / merged[f'{value_col}_start']) ** (1/years_between) - 1) * 100
    ).round(2)

    return merged


def main():
    """Main execution."""

    logger = setup_logger('cbp_collection')
    aggregator = RegionalAggregator()

    api_key = get_api_key('CENSUS_KEY')
    if not api_key:
        logger.error("Census API key not found. Set CENSUS_KEY environment variable.")
        return

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("CENSUS COUNTY BUSINESS PATTERNS DATA COLLECTION")
    logger.info("=" * 80)

    start_time = datetime.now()
    year_current = 2021  # CBP 2022 may not be available yet
    year_start = 2018  # For 3-year growth rate (2018-2021)

    measures = {}

    # ===========================================================================
    # GROWTH INDEX MEASURES - CBP
    # ===========================================================================

    # 1. Private Employment (level, current year)
    logger.info(f"\n1/2: Private Employment ({year_current})")

    all_states_current = []
    for state_abbr, state_fips in STATES.items():
        df = collect_cbp_data(year_current, state_fips, api_key, logger)
        if not df.empty:
            df['state_abbr'] = state_abbr
            all_states_current.append(df)

    if all_states_current:
        combined_current = pd.concat(all_states_current, ignore_index=True)
        logger.info(f"  Total counties: {len(combined_current)}")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=combined_current,
            measure_type='extensive',
            value_column='EMP',
            fips_column='fips',
            weight_column=None
        )
        measures['private_employment'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  No private employment data collected")

    # 2. Growth in Private Wages Per Job (2018-2021)
    logger.info(f"\n2/2: Growth in Private Wages Per Job ({year_start}-{year_current})")

    # Collect start year data
    all_states_start = []
    for state_abbr, state_fips in STATES.items():
        df = collect_cbp_data(year_start, state_fips, api_key, logger)
        if not df.empty:
            df['state_abbr'] = state_abbr
            all_states_start.append(df)

    if all_states_current and all_states_start:
        combined_start = pd.concat(all_states_start, ignore_index=True)
        logger.info(f"  Start year counties: {len(combined_start)}")

        # Calculate wages per job for both years
        combined_current['wages_per_job'] = (combined_current['PAYANN'] * 1000) / combined_current['EMP']
        combined_start['wages_per_job'] = (combined_start['PAYANN'] * 1000) / combined_start['EMP']

        # Calculate growth rate
        growth_df = calculate_growth_rate(
            combined_start,
            combined_current,
            'wages_per_job',
            'wages_per_job_growth_rate',
            years_between=(year_current - year_start)
        )

        # Merge with current year employment for weighting
        growth_df = growth_df.merge(
            combined_current[['fips', 'EMP']],
            on='fips',
            how='left'
        )

        logger.info(f"  Calculated growth rates for {len(growth_df)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=growth_df,
            measure_type='intensive',
            value_column='wages_per_job_growth_rate',
            fips_column='fips',
            weight_column='EMP'  # Weight by employment
        )
        measures['wages_per_job_growth_rate'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  No wages per job growth data collected")

    end_time = datetime.now()

    # Save all measures
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year_current}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Years: {year_start}-{year_current}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}/2")
    print()
    print("Growth Index Measures (CBP):")
    print(f"  1. Private Employment ({year_current}): {'✓' if 'private_employment' in measures else '✗'}")
    print(f"  2. Wages Per Job Growth Rate ({year_start}-{year_current}): {'✓' if 'wages_per_job_growth_rate' in measures else '✗'}")
    print("=" * 80)


if __name__ == '__main__':
    main()
