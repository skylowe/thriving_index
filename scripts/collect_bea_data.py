#!/usr/bin/env python3
"""
Collect BEA (Bureau of Economic Analysis) data for economic measures.

Collects:
- Per capita personal income (level)
- Per capita personal income growth rate (5-year)
- Farm proprietors income as % of total personal income
- Nonfarm proprietors income as % of total personal income
- GDP per capita (level)
- GDP per capita growth rate (5-year)
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bea_api import BEAAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


def collect_bea_measure(bea: BEAAPI, method_name: str, year, logger) -> pd.DataFrame:
    """
    Generic function to collect BEA data across all states.

    Args:
        bea: BEA API client
        method_name: Name of BEAAPI method to call
        year: Year or year range
        logger: Logger instance

    Returns:
        Combined DataFrame with all states
    """
    all_data = []
    method = getattr(bea, method_name)

    for state_abbr, state_fips in STATES.items():
        try:
            data = method(year=year, state=state_fips)

            if data and 'BEAAPI' in data and 'Results' in data['BEAAPI']:
                results = data['BEAAPI']['Results']
                if 'Data' in results:
                    df = pd.DataFrame(results['Data'])
                    df['state_abbr'] = state_abbr

                    # Extract FIPS from GeoFips
                    if 'GeoFips' in df.columns:
                        df['fips'] = df['GeoFips'].astype(str).str.zfill(5)

                    all_data.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} records")
        except Exception as e:
            logger.error(f"  Error {state_abbr}: {str(e)}")

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)


def calculate_growth_rate(df_start: pd.DataFrame, df_end: pd.DataFrame,
                         value_col_start: str, value_col_end: str,
                         growth_col_name: str, years_between: int) -> pd.DataFrame:
    """
    Calculate annualized growth rate between two periods.

    Args:
        df_start: DataFrame with start period data
        df_end: DataFrame with end period data
        value_col_start: Name of value column in start data
        value_col_end: Name of value column in end data
        growth_col_name: Name for growth rate column
        years_between: Number of years between periods

    Returns:
        DataFrame with growth rates
    """
    merged = df_start.merge(
        df_end,
        on='fips',
        how='inner',
        suffixes=('_start', '_end')
    )

    # Calculate annualized growth rate
    merged[growth_col_name] = (
        ((merged[value_col_end] / merged[value_col_start]) ** (1/years_between) - 1) * 100
    ).round(2)

    return merged


def main():
    """Main execution."""

    logger = setup_logger('bea_collection')
    bea = BEAAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("BEA ECONOMIC DATA COLLECTION")
    logger.info("=" * 80)

    measures = {}
    start_time = datetime.now()
    year_current = 2022
    year_start = 2017  # For 5-year growth rate

    # 1. Per capita personal income (current year)
    logger.info("\n1/6: Per Capita Personal Income (2022)")
    df_pcpi_2022 = collect_bea_measure(bea, 'get_personal_income_per_capita', year_current, logger)

    if not df_pcpi_2022.empty:
        df_pcpi_2022['per_capita_personal_income'] = pd.to_numeric(df_pcpi_2022['DataValue'], errors='coerce')
        regional = aggregator.aggregate_to_regions(
            county_data=df_pcpi_2022,
            measure_type='intensive',
            value_column='per_capita_personal_income',
            fips_column='fips',
            weight_column=None
        )
        measures['per_capita_personal_income'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Collected {len(regional)} regions")

    # 2. Per capita personal income (2017 for growth)
    logger.info("\n2/6: Per Capita Personal Income (2017 for growth)")
    df_pcpi_2017 = collect_bea_measure(bea, 'get_personal_income_per_capita', year_start, logger)

    if not df_pcpi_2017.empty and not df_pcpi_2022.empty:
        df_pcpi_2017['pcpi_2017'] = pd.to_numeric(df_pcpi_2017['DataValue'], errors='coerce')
        df_pcpi_2022_temp = df_pcpi_2022.copy()
        df_pcpi_2022_temp['pcpi_2022'] = pd.to_numeric(df_pcpi_2022_temp['DataValue'], errors='coerce')

        growth_df = calculate_growth_rate(
            df_pcpi_2017[['fips', 'pcpi_2017']],
            df_pcpi_2022_temp[['fips', 'pcpi_2022']],
            'pcpi_2017',
            'pcpi_2022',
            'per_capita_income_growth_rate',
            years_between=5
        )

        regional = aggregator.aggregate_to_regions(
            county_data=growth_df,
            measure_type='intensive',
            value_column='per_capita_income_growth_rate',
            fips_column='fips',
            weight_column='pcpi_2022'  # Weight by current income
        )
        measures['per_capita_income_growth_rate'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Calculated growth rates for {len(regional)} regions")

    # 3. Total personal income + Farm/Nonfarm proprietors income for percentages
    logger.info("\n3/6: Total Personal Income (for calculating percentages)")
    df_total_income = collect_bea_measure(bea, 'get_regional_income', year_current, logger)

    # Filter for line code 1 (total personal income)
    if not df_total_income.empty and 'LineCode' in df_total_income.columns:
        df_total_income = df_total_income[df_total_income['LineCode'] == '1'].copy()
        df_total_income['total_personal_income'] = pd.to_numeric(df_total_income['DataValue'], errors='coerce')

    # 4. Farm proprietors income
    logger.info("\n4/6: Farm Proprietors Income")
    df_farm = collect_bea_measure(bea, 'get_farm_proprietors_income', year_current, logger)

    if not df_farm.empty:
        df_farm['farm_proprietors_income'] = pd.to_numeric(df_farm['DataValue'], errors='coerce')

        # Calculate as percentage of total income
        if not df_total_income.empty:
            df_farm = df_farm.merge(
                df_total_income[['fips', 'total_personal_income']],
                on='fips',
                how='left'
            )
            df_farm['pct_farm_income'] = (
                (df_farm['farm_proprietors_income'] / df_farm['total_personal_income'] * 1000) * 100
            ).round(2)

            regional = aggregator.aggregate_to_regions(
                county_data=df_farm,
                measure_type='intensive',
                value_column='pct_farm_income',
                fips_column='fips',
                weight_column='total_personal_income'
            )
            measures['pct_farm_income'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Calculated farm income % for {len(regional)} regions")

    # 5. Nonfarm proprietors income
    logger.info("\n5/6: Nonfarm Proprietors Income")
    df_nonfarm = collect_bea_measure(bea, 'get_nonfarm_proprietors_income', year_current, logger)

    if not df_nonfarm.empty:
        df_nonfarm['nonfarm_proprietors_income'] = pd.to_numeric(df_nonfarm['DataValue'], errors='coerce')

        # Calculate as percentage of total income
        if not df_total_income.empty:
            df_nonfarm = df_nonfarm.merge(
                df_total_income[['fips', 'total_personal_income']],
                on='fips',
                how='left'
            )
            df_nonfarm['pct_nonfarm_income'] = (
                (df_nonfarm['nonfarm_proprietors_income'] / df_nonfarm['total_personal_income'] * 1000) * 100
            ).round(2)

            regional = aggregator.aggregate_to_regions(
                county_data=df_nonfarm,
                measure_type='intensive',
                value_column='pct_nonfarm_income',
                fips_column='fips',
                weight_column='total_personal_income'
            )
            measures['pct_nonfarm_income'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Calculated nonfarm income % for {len(regional)} regions")

    # 6. GDP per capita (if available)
    logger.info("\n6/6: GDP Per Capita")
    try:
        df_gdp = collect_bea_measure(bea, 'get_gdp_by_county', year_current, logger)

        if not df_gdp.empty:
            df_gdp['gdp'] = pd.to_numeric(df_gdp['DataValue'], errors='coerce')

            # Need population to calculate per capita
            # We'll save absolute GDP and calculate per capita during aggregation
            regional = aggregator.aggregate_to_regions(
                county_data=df_gdp,
                measure_type='extensive',
                value_column='gdp',
                fips_column='fips',
                weight_column=None
            )
            measures['gdp_total'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Collected GDP for {len(regional)} regions")
    except Exception as e:
        logger.warning(f"  GDP data not available: {str(e)}")

    end_time = datetime.now()

    # Save all
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year_current}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Years: {year_start}-{year_current}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures: {len([m for m in measures.values() if m is not None and not m.empty])}/6")
    print("=" * 80)


if __name__ == '__main__':
    main()
