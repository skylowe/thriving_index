#!/usr/bin/env python3
"""
Collect USDA NASS agricultural statistics data.

Collects:
- Farm proprietors income (total for region)
- Number of farms
- Agricultural land values
- Farm sales
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.usda_nass_api import USDANASSAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21'}

# Note: DC not included - no agricultural data for DC


def collect_nass_data_for_state(nass: USDANASSAPI, state_fips: str, state_abbr: str,
                                  year: int, data_type: str, logger) -> pd.DataFrame:
    """
    Collect NASS data for a state.

    Args:
        nass: NASS API client
        state_fips: State FIPS code
        state_abbr: State abbreviation
        year: Year to collect (use census years: 2017, 2022)
        data_type: Type of data (farm_income, farm_counts, land_value, sales)
        logger: Logger instance

    Returns:
        DataFrame with county-level agricultural data
    """
    logger.info(f"  {state_abbr}: Collecting {data_type}")

    try:
        if data_type == 'farm_income':
            data = nass.get_farm_income(year=year, state_fips=state_fips)
        elif data_type == 'farm_counts':
            data = nass.get_farm_counts(year=year, state_fips=state_fips)
        elif data_type == 'land_value':
            data = nass.get_agricultural_land_value(year=year, state_fips=state_fips)
        elif data_type == 'sales':
            data = nass.get_farm_sales(year=year, state_fips=state_fips)
        else:
            logger.error(f"Unknown data type: {data_type}")
            return pd.DataFrame()

        # Parse response
        records = USDANASSAPI.parse_response(data)

        if not records:
            logger.warning(f"  {state_abbr}: No data returned")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(records)
        df['state_abbr'] = state_abbr

        # Extract FIPS code
        if 'county_code' in df.columns and 'state_fips_code' in df.columns:
            df['fips'] = df['state_fips_code'].astype(str).str.zfill(2) + df['county_code'].astype(str).str.zfill(3)
        elif 'county_ansi' in df.columns and 'state_ansi' in df.columns:
            df['fips'] = df['state_ansi'].astype(str).str.zfill(2) + df['county_ansi'].astype(str).str.zfill(3)

        logger.info(f"  {state_abbr}: {len(df)} records")
        return df

    except Exception as e:
        logger.error(f"  {state_abbr}: Error - {str(e)}")
        return pd.DataFrame()


def main():
    """Main execution."""

    logger = setup_logger('nass_collection')
    nass = USDANASSAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("USDA NASS AGRICULTURAL DATA COLLECTION")
    logger.info("=" * 80)

    # NASS Census of Agriculture is conducted every 5 years
    # Most recent: 2017, next: 2022 (may not be available yet)
    # Use 2017 for now
    year = 2017
    logger.info(f"Using Census of Agriculture year: {year}")
    logger.info("Note: 2022 Census may not be fully available yet")

    measures = {}
    start_time = datetime.now()

    # 1. Farm counts
    logger.info("\n1/4: Farm Counts")
    all_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_nass_data_for_state(nass, state_fips, state_abbr, year, 'farm_counts', logger)
        if not df.empty:
            all_data.append(df)
        time.sleep(0.5)  # Be nice to the API

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Extract value
        if 'Value' in combined.columns:
            combined['farm_count'] = pd.to_numeric(combined['Value'].str.replace(',', ''), errors='coerce')

            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',  # Sum across counties in region
                value_column='farm_count',
                fips_column='fips',
                weight_column=None
            )
            measures['farm_count'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Aggregated to {len(regional)} regions")

    # 2. Farm Income
    logger.info("\n2/4: Farm Income")
    all_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_nass_data_for_state(nass, state_fips, state_abbr, year, 'farm_income', logger)
        if not df.empty:
            all_data.append(df)
        time.sleep(0.5)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Extract value
        if 'Value' in combined.columns:
            combined['farm_income'] = pd.to_numeric(combined['Value'].str.replace(',', ''), errors='coerce')

            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',  # Sum across counties in region
                value_column='farm_income',
                fips_column='fips',
                weight_column=None
            )
            measures['farm_income_total'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Aggregated to {len(regional)} regions")

    # 3. Agricultural Land Value
    logger.info("\n3/4: Agricultural Land Value")
    all_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_nass_data_for_state(nass, state_fips, state_abbr, year, 'land_value', logger)
        if not df.empty:
            all_data.append(df)
        time.sleep(0.5)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Extract value
        if 'Value' in combined.columns:
            combined['land_value'] = pd.to_numeric(combined['Value'].str.replace(',', ''), errors='coerce')

            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',  # Sum across counties in region
                value_column='land_value',
                fips_column='fips',
                weight_column=None
            )
            measures['ag_land_value_total'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Aggregated to {len(regional)} regions")

    # 4. Farm Sales
    logger.info("\n4/4: Farm Sales")
    all_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_nass_data_for_state(nass, state_fips, state_abbr, year, 'sales', logger)
        if not df.empty:
            all_data.append(df)
        time.sleep(0.5)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Extract value
        if 'Value' in combined.columns:
            combined['farm_sales'] = pd.to_numeric(combined['Value'].str.replace(',', ''), errors='coerce')

            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',  # Sum across counties in region
                value_column='farm_sales',
                fips_column='fips',
                weight_column=None
            )
            measures['farm_sales_total'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Aggregated to {len(regional)} regions")

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

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Year: {year}")
    print(f"States: {len(STATES)}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}/4")
    print(f"Time: {end_time - start_time}")
    print("=" * 80)
    print()
    print("NOTE: USDA NASS Census of Agriculture data is only available every 5 years.")
    print("      Most recent complete census: 2017")
    print("      Next census (2022) may have partial availability - check NASS QuickStats for updates.")
    print("=" * 80)


if __name__ == '__main__':
    main()
