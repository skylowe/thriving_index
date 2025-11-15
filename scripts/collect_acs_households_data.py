#!/usr/bin/env python3
"""
Collect Census ACS data for Growth Index household measure.

Growth Index Measure (Nebraska Methodology):
- Growth in Households with Children (2013-2017 vs 2018-2022) - Growth Index 1.4

Census ACS Table S1101 (Households and Families) provides:
- S1101_C01_002E: Households with one or more people under 18 years
- S1101_C01_001E: Total households

Note: Nebraska used 2011-2015 and 2016-2020 periods. We'll use more recent
2013-2017 and 2018-2022 periods for Virginia analysis.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


def collect_acs_households(census: CensusAPI, year: int, state_fips: str,
                           state_abbr: str, logger) -> pd.DataFrame:
    """
    Collect ACS data on households with children for a state.

    Args:
        census: Census API client
        year: Year (for 5-year estimates, this is the end year, e.g., 2022 for 2018-2022)
        state_fips: State FIPS code (2 digits)
        state_abbr: State abbreviation
        logger: Logger instance

    Returns:
        DataFrame with households with children by county
    """
    logger.debug(f"  Fetching ACS households data for {state_abbr} ({year-4}-{year} 5-year)")

    # Variables from ACS Table S1101
    variables = [
        'S1101_C01_002E',  # Households with one or more people under 18 years
        'S1101_C01_001E',  # Total households (for verification)
    ]

    try:
        # Use acs5 endpoint for 5-year estimates
        data = census.get_data(
            dataset=f'acs/acs5/subject',
            year=year,
            variables=variables,
            geography={'for': 'county:*', 'in': f'state:{state_fips}'}
        )

        if not data or len(data) < 2:
            logger.warning(f"  No data returned for {state_abbr}")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        # Create FIPS code
        df['fips'] = df['state'] + df['county']
        df['state_abbr'] = state_abbr

        # Rename variables to friendly names
        df['households_with_children'] = pd.to_numeric(df['S1101_C01_002E'], errors='coerce')
        df['total_households'] = pd.to_numeric(df['S1101_C01_001E'], errors='coerce')

        # Filter out null values
        df = df[df['households_with_children'].notna()].copy()

        logger.debug(f"  Collected {len(df)} counties")
        return df

    except Exception as e:
        logger.error(f"  Error collecting ACS data for {state_abbr}: {str(e)}")
        return pd.DataFrame()


def calculate_growth_rate(df_start: pd.DataFrame, df_end: pd.DataFrame,
                         value_col: str, growth_col_name: str,
                         years_between: int) -> pd.DataFrame:
    """
    Calculate growth rate between two 5-year ACS periods.

    Args:
        df_start: DataFrame with earlier period data
        df_end: DataFrame with later period data
        value_col: Name of value column
        growth_col_name: Name for growth rate column
        years_between: Number of years between period midpoints

    Returns:
        DataFrame with growth rates
    """
    merged = df_start[['fips', value_col]].merge(
        df_end[['fips', value_col]],
        on='fips',
        how='inner',
        suffixes=('_start', '_end')
    )

    # Calculate percent change (not annualized, since we're comparing two 5-year periods)
    merged[growth_col_name] = (
        ((merged[f'{value_col}_end'] - merged[f'{value_col}_start']) / merged[f'{value_col}_start']) * 100
    ).round(2)

    return merged


def main():
    """Main execution."""

    logger = setup_logger('acs_households_collection')
    census = CensusAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("CENSUS ACS HOUSEHOLDS WITH CHILDREN DATA COLLECTION")
    logger.info("=" * 80)

    start_time = datetime.now()
    # Use most recent available 5-year periods
    year_end_late = 2022  # 2018-2022 ACS 5-year estimates
    year_end_early = 2017  # 2013-2017 ACS 5-year estimates

    measures = {}

    # ===========================================================================
    # GROWTH INDEX MEASURE - HOUSEHOLDS WITH CHILDREN
    # ===========================================================================

    logger.info(f"\nGrowth in Households with Children ({year_end_early-4}-{year_end_early} vs {year_end_late-4}-{year_end_late})")

    # Collect earlier period data (2013-2017)
    logger.info(f"\n  Collecting earlier period ({year_end_early-4}-{year_end_early})...")
    all_states_early = []
    for state_abbr, state_fips in STATES.items():
        df = collect_acs_households(census, year_end_early, state_fips, state_abbr, logger)
        if not df.empty:
            all_states_early.append(df)

    # Collect later period data (2018-2022)
    logger.info(f"\n  Collecting later period ({year_end_late-4}-{year_end_late})...")
    all_states_late = []
    for state_abbr, state_fips in STATES.items():
        df = collect_acs_households(census, year_end_late, state_fips, state_abbr, logger)
        if not df.empty:
            all_states_late.append(df)

    if all_states_early and all_states_late:
        combined_early = pd.concat(all_states_early, ignore_index=True)
        combined_late = pd.concat(all_states_late, ignore_index=True)

        logger.info(f"\n  Earlier period: {len(combined_early)} counties")
        logger.info(f"  Later period: {len(combined_late)} counties")

        # Calculate growth rate
        # Number of years between period midpoints: (2017-2013)/2 to (2022-2018)/2 = 5 years
        growth_df = calculate_growth_rate(
            combined_early,
            combined_late,
            'households_with_children',
            'households_with_children_growth',
            years_between=5  # Between period midpoints
        )

        # Merge with later period total households for weighting
        growth_df = growth_df.merge(
            combined_late[['fips', 'total_households']],
            on='fips',
            how='left'
        )

        logger.info(f"  Calculated growth rates for {len(growth_df)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=growth_df,
            measure_type='intensive',
            value_column='households_with_children_growth',
            fips_column='fips',
            weight_column='total_households'  # Weight by total households
        )
        measures['households_with_children_growth'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")

        # Also save the latest period level data for reference
        regional_level = aggregator.aggregate_to_regions(
            county_data=combined_late,
            measure_type='extensive',
            value_column='households_with_children',
            fips_column='fips',
            weight_column=None
        )
        measures['households_with_children_level'] = aggregator.add_region_metadata(regional_level)

    else:
        logger.warning("  Could not collect data for both periods")

    end_time = datetime.now()

    # Save all measures
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year_end_late}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Periods compared: {year_end_early-4}-{year_end_early} vs {year_end_late-4}-{year_end_late}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}")
    print()
    print("Growth Index Measure (ACS):")
    print(f"  Households with Children Growth: {'✓' if 'households_with_children_growth' in measures else '✗'}")
    print()
    print("Note: Growth is calculated as percent change between two 5-year")
    print("      ACS period estimates, not annualized.")
    print("=" * 80)


if __name__ == '__main__':
    main()
