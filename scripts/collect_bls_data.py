#!/usr/bin/env python3
"""
Collect BLS (Bureau of Labor Statistics) data for labor market measures.

Collects from LAUS (Local Area Unemployment Statistics):
- Unemployment rate (annual average)
- Employment level
- Labor force size
- Labor force participation rate (calculated)
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bls_api import BLSAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger
from src.utils.fips_to_region import get_region_for_fips

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


def collect_laus_data_for_state(bls: BLSAPI, state_fips: str, state_abbr: str,
                                year: int, logger) -> pd.DataFrame:
    """
    Collect LAUS data for all counties in a state.

    Args:
        bls: BLS API client
        state_fips: State FIPS code
        state_abbr: State abbreviation
        year: Year to collect
        logger: Logger instance

    Returns:
        DataFrame with unemployment rate, employment, labor force by county
    """
    logger.info(f"Collecting LAUS data for {state_abbr} ({year})")

    # Get all county FIPS for this state - generate from state FIPS pattern
    # Virginia: 001-199, Maryland: 001-047, etc.
    state_counties = []
    for county_code in range(1, 1000, 2):  # Counties use odd numbers in some states
        fips = f"{state_fips}{str(county_code).zfill(3)}"
        if get_region_for_fips(fips):
            state_counties.append(fips)

    all_data = []
    batch_size = 50  # BLS API limit

    # Extract just the county codes (last 3 digits)
    county_codes = [fips[2:] for fips in state_counties]

    # Process in batches
    for i in range(0, len(county_codes), batch_size):
        batch_county_codes = county_codes[i:i + batch_size]

        logger.debug(f"  Batch {i // batch_size + 1}: {len(batch_county_codes)} county codes")

        try:
            # Build series IDs for this batch
            series_ids = []
            for county_fips in batch_county_codes:
                # Request all 4 LAUS measures
                series_ids.extend([
                    bls.build_laus_series_id(state_fips, county_fips, '03'),  # Unemployment rate
                    bls.build_laus_series_id(state_fips, county_fips, '04'),  # Unemployment
                    bls.build_laus_series_id(state_fips, county_fips, '05'),  # Employment
                    bls.build_laus_series_id(state_fips, county_fips, '06'),  # Labor force
                ])

            # Fetch data
            response = bls.get_multiple_series(
                series_ids=series_ids,
                start_year=year,
                end_year=year,
                annual_average=True
            )

            if response.get('status') == 'REQUEST_SUCCEEDED':
                parsed = bls.parse_series_data(response)

                # Organize by county
                for county_fips in batch_county_codes:
                    fips = state_fips + county_fips
                    county_data = {'fips': fips, 'state_abbr': state_abbr}
                    has_data = False

                    # Extract measures
                    for measure_code, measure_name in [('03', 'unemployment_rate'),
                                                       ('04', 'unemployment'),
                                                       ('05', 'employment'),
                                                       ('06', 'labor_force')]:
                        series_id = bls.build_laus_series_id(state_fips, county_fips, measure_code)

                        if series_id in parsed and parsed[series_id]:
                            # Get annual average from data
                            annual_avg = bls.get_annual_average(parsed[series_id])
                            if year in annual_avg:
                                county_data[measure_name] = annual_avg[year]
                                has_data = True

                    # Only add if we got at least some data
                    if has_data:
                        all_data.append(county_data)

            else:
                logger.warning(f"  Batch failed: {response.get('message', 'Unknown error')}")

            # Rate limiting: small delay between batches
            if i + batch_size < len(county_codes):
                time.sleep(0.5)

        except Exception as e:
            logger.error(f"  Error in batch {i // batch_size + 1}: {str(e)}")

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    logger.info(f"  Collected data for {len(df)} counties")

    return df


def main():
    """Main execution."""

    logger = setup_logger('bls_collection')
    bls = BLSAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("BLS LAUS DATA COLLECTION")
    logger.info("=" * 80)

    start_time = datetime.now()
    year = 2022

    # Collect data for all states
    all_states_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            state_data = collect_laus_data_for_state(bls, state_fips, state_abbr, year, logger)
            if not state_data.empty:
                all_states_data.append(state_data)
        except Exception as e:
            logger.error(f"Error collecting {state_abbr}: {str(e)}")

    if not all_states_data:
        logger.error("No data collected from any state")
        return

    # Combine all states
    combined = pd.concat(all_states_data, ignore_index=True)
    logger.info(f"\nTotal counties collected: {len(combined)}")

    # Convert to numeric
    for col in ['unemployment_rate', 'unemployment', 'employment', 'labor_force']:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors='coerce')

    # Save measures
    measures = {}

    # 1. Unemployment Rate
    logger.info("\nAggregating: Unemployment Rate")
    regional = aggregator.aggregate_to_regions(
        county_data=combined,
        measure_type='intensive',
        value_column='unemployment_rate',
        fips_column='fips',
        weight_column='labor_force'  # Weight by labor force size
    )
    measures['unemployment_rate'] = aggregator.add_region_metadata(regional)
    logger.info(f"  {len(regional)} regions")

    # 2. Employment
    logger.info("\nAggregating: Employment")
    regional = aggregator.aggregate_to_regions(
        county_data=combined,
        measure_type='extensive',
        value_column='employment',
        fips_column='fips',
        weight_column=None
    )
    measures['employment'] = aggregator.add_region_metadata(regional)
    logger.info(f"  {len(regional)} regions")

    # 3. Labor Force
    logger.info("\nAggregating: Labor Force")
    regional = aggregator.aggregate_to_regions(
        county_data=combined,
        measure_type='extensive',
        value_column='labor_force',
        fips_column='fips',
        weight_column=None
    )
    measures['labor_force'] = aggregator.add_region_metadata(regional)
    logger.info(f"  {len(regional)} regions")

    # 4. Labor Force Participation Rate (calculated from employment + unemployment / population)
    # Note: This would require population data, so we'll skip for now
    # Can be calculated later when combining all measures

    end_time = datetime.now()

    # Save all measures
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")

    # Save combined county-level data
    county_filepath = output_dir / f"bls_laus_{year}_county.csv"
    combined.to_csv(county_filepath, index=False)
    logger.info(f"  Saved: {county_filepath.name} ({len(combined)} counties)")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Year: {year}")
    print(f"Counties: {len(combined)}")
    print(f"Regions: {len(measures['unemployment_rate'])}")
    print(f"Measures: {len(measures)}")
    print(f"Time: {end_time - start_time}")
    print()
    print("Unemployment Rate Statistics:")
    if 'unemployment_rate' in combined.columns:
        valid_rates = combined['unemployment_rate'].dropna()
        if len(valid_rates) > 0:
            print(f"  Min: {valid_rates.min():.1f}%")
            print(f"  Max: {valid_rates.max():.1f}%")
            print(f"  Mean: {valid_rates.mean():.1f}%")
            print(f"  Median: {valid_rates.median():.1f}%")
    print("=" * 80)


if __name__ == '__main__':
    main()
