#!/usr/bin/env python3
"""
Collect population growth using ACS 5-year estimates.

Compares most recent 5-year estimate (2018-2022) to previous 5-year estimate (2013-2017)
to calculate annualized population growth rate.
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


def collect_acs_population(census: CensusAPI, year: int, logger) -> pd.DataFrame:
    """
    Collect ACS 5-year population estimates for all counties.

    Args:
        census: Census API client
        year: Year of ACS 5-year estimate (e.g., 2022 for 2018-2022 estimates)
        logger: Logger instance

    Returns:
        DataFrame with population by county
    """
    logger.info(f"Collecting ACS 5-year population estimates for {year}")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            # Use B01003_001E for total population
            data = census.get_acs5_data(
                year=year,
                variables=['B01003_001E'],
                geography='county:*',
                state=state_fips
            )

            if not data:
                logger.warning(f"  No data for {state_abbr}")
                continue

            df = pd.DataFrame(data)

            # Build FIPS
            if 'county' in df.columns:
                df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
            else:  # DC
                df['fips'] = '11001'

            # Convert population to numeric
            df['population'] = pd.to_numeric(df['B01003_001E'], errors='coerce')

            all_data.append(df[['fips', 'population', 'NAME']])
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        logger.error("No population data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def calculate_growth_rate(pop_start: pd.DataFrame, pop_end: pd.DataFrame,
                         years_between: int, logger) -> pd.DataFrame:
    """
    Calculate annualized population growth rate.

    Args:
        pop_start: Population at start period
        pop_end: Population at end period
        years_between: Number of years between periods (5 for 2013-2017 to 2018-2022)
        logger: Logger instance

    Returns:
        DataFrame with growth rates by county
    """
    logger.info(f"Calculating {years_between}-year annualized growth rate")

    # Merge start and end populations
    merged = pop_start.merge(
        pop_end,
        on='fips',
        how='outer',
        suffixes=('_start', '_end')
    )

    # Calculate annualized growth rate: ((P_end / P_start)^(1/years) - 1) * 100
    merged['population_growth_rate'] = (
        ((merged['population_end'] / merged['population_start']) ** (1/years_between) - 1) * 100
    ).round(2)

    # Keep only valid growth rates
    valid = merged.dropna(subset=['population_growth_rate'])

    logger.info(f"  Calculated growth rates for {len(valid)} counties")

    return valid[['fips', 'population_start', 'population_end', 'population_growth_rate']]


def main():
    """Main execution."""

    logger = setup_logger('acs_pop_growth')
    census = CensusAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("ACS POPULATION GROWTH COLLECTION")
    logger.info("Comparing 2013-2017 to 2018-2022 ACS 5-year estimates")
    logger.info("=" * 80)

    start_time = datetime.now()

    # Collect population for both periods
    # 2013-2017 ACS 5-year estimates
    pop_2017 = collect_acs_population(census, year=2017, logger=logger)

    # 2018-2022 ACS 5-year estimates
    pop_2022 = collect_acs_population(census, year=2022, logger=logger)

    if pop_2017.empty or pop_2022.empty:
        logger.error("Failed to collect population data for both periods")
        return

    # Calculate growth rate (5 years between midpoints: 2015 to 2020)
    growth = calculate_growth_rate(pop_2017, pop_2022, years_between=5, logger=logger)

    if growth.empty:
        logger.error("Failed to calculate growth rates")
        return

    # Aggregate to regions using population-weighted average
    # Use end-period population as weight
    logger.info("\nAggregating to regions...")
    regional = aggregator.aggregate_to_regions(
        county_data=growth,
        measure_type='intensive',
        value_column='population_growth_rate',
        fips_column='fips',
        weight_column='population_end'
    )

    regional = aggregator.add_region_metadata(regional)

    logger.info(f"  Aggregated to {len(regional)} regions")

    # Save regional data
    end_time = datetime.now()

    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    filepath = output_dir / "population_growth_rate_acs_regional.csv"
    regional.to_csv(filepath, index=False)
    logger.info(f"  Saved: {filepath.name} ({len(regional)} regions)")

    # Save county-level data as well for reference
    county_filepath = output_dir / "population_growth_rate_acs_county.csv"
    growth.to_csv(county_filepath, index=False)
    logger.info(f"  Saved: {county_filepath.name} ({len(growth)} counties)")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Period: 2013-2017 to 2018-2022 (5-year ACS estimates)")
    print(f"Counties: {len(growth)}")
    print(f"Regions: {len(regional)}")
    print(f"Time: {end_time - start_time}")
    print()
    print("Growth Rate Statistics:")
    print(f"  Min: {growth['population_growth_rate'].min():.2f}%")
    print(f"  Max: {growth['population_growth_rate'].max():.2f}%")
    print(f"  Mean: {growth['population_growth_rate'].mean():.2f}%")
    print(f"  Median: {growth['population_growth_rate'].median():.2f}%")
    print("=" * 80)


if __name__ == '__main__':
    main()
