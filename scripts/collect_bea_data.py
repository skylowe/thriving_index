#!/usr/bin/env python3
"""
Collect BEA (Bureau of Economic Analysis) data for multiple component indexes.

Growth Index Measures (Nebraska Methodology):
- Growth in Total Employment (CAINC5N Line Code 10, 3-year growth)
- Growth in Dividends, Interest, and Rent Income (CAINC5N Line Code 40, 3-year growth)

Component Index 3: Other Economic Prosperity (Nebraska Methodology):
- Non-Farm Proprietor Personal Income (CAINC4 Line Code 60, level)
- Personal Income Stability (CAINC1 Line Code 1, coefficient of variation over 15 years)
- Share of Income from DIR (CAINC5N Line Code 40 / CAINC1 Line Code 1, percentage)

Other BEA Measures (for other component indexes):
- Per capita personal income (level) - for Economic Opportunity Index
- Farm proprietors income as % of total - for peer matching variables
- Nonfarm proprietors income as % of total - for peer matching variables
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
from src.api_clients.census_api import CensusAPI

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


def get_population_data(year: int, states: dict, logger) -> pd.DataFrame:
    """
    Fetch population data for weighting intensive measures.

    Args:
        year: Year to fetch
        states: Dictionary of state abbreviations to FIPS codes
        logger: Logger instance

    Returns:
        DataFrame with fips and population columns
    """
    census = CensusAPI()
    all_pop_data = []

    for state_abbr, state_fips in states.items():
        try:
            data = census.get_population(year, state_fips)
            if data:
                df = pd.DataFrame(data)
                # Extract FIPS and population
                if 'state' in df.columns and 'county' in df.columns:
                    df['fips'] = df['state'] + df['county']
                    df['population'] = pd.to_numeric(df.get('B01003_001E', df.get('POP', 0)), errors='coerce')
                    all_pop_data.append(df[['fips', 'population']])
        except Exception as e:
            logger.warning(f"Could not fetch population for {state_abbr}: {e}")

    if all_pop_data:
        return pd.concat(all_pop_data, ignore_index=True)
    return pd.DataFrame()


def main():
    """Main execution."""

    logger = setup_logger('bea_collection')
    bea = BEAAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get population data for weighting
    logger.info("Fetching population data for weighting...")
    population_df = get_population_data(2022, STATES, logger)
    if population_df.empty:
        logger.warning("No population data available for weighting")

    logger.info("=" * 80)
    logger.info("BEA ECONOMIC DATA COLLECTION")
    logger.info("=" * 80)

    measures = {}
    start_time = datetime.now()
    year_current = 2022
    year_start = 2019  # For 3-year growth rate (2019-2022)
    year_stability_start = 2008  # For 15-year personal income stability (2008-2022)

    # ===========================================================================
    # GROWTH INDEX MEASURES
    # ===========================================================================

    # 1. Growth in Total Employment (Growth Index 1.1)
    logger.info("\n1/5: Growth in Total Employment (2019-2022)")

    # Collect total employment 2022
    df_emp_2022 = collect_bea_measure(bea, 'get_total_employment', year_current, logger)

    # Collect total employment 2019
    df_emp_2019 = collect_bea_measure(bea, 'get_total_employment', year_start, logger)

    if not df_emp_2022.empty and not df_emp_2019.empty:
        df_emp_2022_temp = df_emp_2022.copy()
        df_emp_2022_temp['employment_2022'] = pd.to_numeric(df_emp_2022_temp['DataValue'], errors='coerce')

        df_emp_2019['employment_2019'] = pd.to_numeric(df_emp_2019['DataValue'], errors='coerce')

        growth_df = calculate_growth_rate(
            df_emp_2019[['fips', 'employment_2019']],
            df_emp_2022_temp[['fips', 'employment_2022']],
            'employment_2019',
            'employment_2022',
            'total_employment_growth_rate',
            years_between=3
        )

        regional = aggregator.aggregate_to_regions(
            county_data=growth_df,
            measure_type='intensive',
            value_column='total_employment_growth_rate',
            fips_column='fips',
            weight_column='employment_2022'  # Weight by current employment
        )
        measures['total_employment_growth_rate'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Calculated employment growth rates for {len(regional)} regions")

    # 2. Growth in DIR Income (Growth Index 1.5)
    logger.info("\n2/5: Growth in Dividends, Interest, and Rent Income (2019-2022)")

    # Collect DIR income 2022
    df_dir_2022 = collect_bea_measure(bea, 'get_dir_income', year_current, logger)

    # Collect DIR income 2019
    df_dir_2019 = collect_bea_measure(bea, 'get_dir_income', year_start, logger)

    if not df_dir_2022.empty and not df_dir_2019.empty:
        df_dir_2022_temp = df_dir_2022.copy()
        df_dir_2022_temp['dir_income_2022'] = pd.to_numeric(df_dir_2022_temp['DataValue'], errors='coerce')

        df_dir_2019['dir_income_2019'] = pd.to_numeric(df_dir_2019['DataValue'], errors='coerce')

        growth_df = calculate_growth_rate(
            df_dir_2019[['fips', 'dir_income_2019']],
            df_dir_2022_temp[['fips', 'dir_income_2022']],
            'dir_income_2019',
            'dir_income_2022',
            'dir_income_growth_rate',
            years_between=3
        )

        regional = aggregator.aggregate_to_regions(
            county_data=growth_df,
            measure_type='intensive',
            value_column='dir_income_growth_rate',
            fips_column='fips',
            weight_column='dir_income_2022'  # Weight by current DIR income
        )
        measures['dir_income_growth_rate'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Calculated DIR income growth rates for {len(regional)} regions")

    # ===========================================================================
    # OTHER ECONOMIC MEASURES
    # ===========================================================================

    # 3. Per capita personal income (current year) - for Economic Opportunity Index
    logger.info("\n3/5: Per Capita Personal Income (2022)")
    df_pcpi_2022 = collect_bea_measure(bea, 'get_personal_income_per_capita', year_current, logger)

    if not df_pcpi_2022.empty:
        df_pcpi_2022['per_capita_personal_income'] = pd.to_numeric(df_pcpi_2022['DataValue'], errors='coerce')

        # Merge with population for weighting
        if not population_df.empty:
            df_pcpi_2022 = df_pcpi_2022.merge(population_df, on='fips', how='left')

        regional = aggregator.aggregate_to_regions(
            county_data=df_pcpi_2022,
            measure_type='intensive',
            value_column='per_capita_personal_income',
            fips_column='fips',
            weight_column='population' if not population_df.empty else None
        )
        measures['per_capita_personal_income'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Collected {len(regional)} regions")

    # 4. Total personal income for Farm/Nonfarm proprietors income percentages
    # Note: We use personal income (LineCode=1) directly from each state call
    logger.info("\n4/5: Total Personal Income (for calculating proprietors percentages)")
    all_total_income = []
    for state_abbr, state_fips in STATES.items():
        try:
            # Call with single line code (1 = total personal income)
            data = bea.get_regional_income(year=year_current, state=state_fips, line_codes=[1])
            if data and 'BEAAPI' in data and 'Results' in data['BEAAPI']:
                results = data['BEAAPI']['Results']
                if 'Data' in results:
                    df = pd.DataFrame(results['Data'])
                    df['state_abbr'] = state_abbr
                    if 'GeoFips' in df.columns:
                        df['fips'] = df['GeoFips'].astype(str).str.zfill(5)
                    all_total_income.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} records")
        except Exception as e:
            logger.error(f"  Error {state_abbr}: {str(e)}")

    df_total_income = pd.concat(all_total_income, ignore_index=True) if all_total_income else pd.DataFrame()

    # Process total personal income
    if not df_total_income.empty:
        logger.debug(f"  Total income raw data: {len(df_total_income)} rows")
        # BEA API returns 'Code' column with values like 'CAINC1-1'
        if 'Code' in df_total_income.columns:
            # Filter for line code 1 (CAINC1-1 = total personal income)
            df_total_income = df_total_income[df_total_income['Code'].str.contains('-1$', na=False)].copy()
            logger.debug(f"  After filtering for line code 1: {len(df_total_income)} rows")
        df_total_income['total_personal_income'] = pd.to_numeric(df_total_income['DataValue'], errors='coerce')
        logger.info(f"  Collected total income for {len(df_total_income)} jurisdictions")
    else:
        logger.warning("  Total income DataFrame is empty!")

    # 5. Farm and Nonfarm proprietors income percentages (for peer matching)
    logger.info("\n5/5: Farm and Nonfarm Proprietors Income Percentages")
    df_farm = collect_bea_measure(bea, 'get_farm_proprietors_income', year_current, logger)

    if not df_farm.empty:
        logger.debug(f"  Farm income raw data: {len(df_farm)} rows")
        df_farm['farm_proprietors_income'] = pd.to_numeric(df_farm['DataValue'], errors='coerce')

        # Calculate as percentage of total income
        if not df_total_income.empty and 'total_personal_income' in df_total_income.columns:
            df_farm = df_farm.merge(
                df_total_income[['fips', 'total_personal_income']],
                on='fips',
                how='left'
            )
            # Both values are in thousands of dollars, so ratio is correct
            df_farm['pct_farm_income'] = (
                df_farm['farm_proprietors_income'] / df_farm['total_personal_income'] * 100
            ).round(2)
            logger.debug(f"  After merge with total income: {len(df_farm)} rows")

            regional = aggregator.aggregate_to_regions(
                county_data=df_farm,
                measure_type='intensive',
                value_column='pct_farm_income',
                fips_column='fips',
                weight_column='total_personal_income'
            )
            measures['pct_farm_income'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Calculated farm income % for {len(regional)} regions")

    # Nonfarm proprietors income
    logger.info("  Nonfarm Proprietors Income")
    df_nonfarm = collect_bea_measure(bea, 'get_nonfarm_proprietors_income', year_current, logger)

    if not df_nonfarm.empty:
        logger.debug(f"  Nonfarm income raw data: {len(df_nonfarm)} rows")
        df_nonfarm['nonfarm_proprietors_income'] = pd.to_numeric(df_nonfarm['DataValue'], errors='coerce')

        # Calculate as percentage of total income
        if not df_total_income.empty and 'total_personal_income' in df_total_income.columns:
            df_nonfarm = df_nonfarm.merge(
                df_total_income[['fips', 'total_personal_income']],
                on='fips',
                how='left'
            )
            # Both values are in thousands of dollars, so ratio is correct
            df_nonfarm['pct_nonfarm_income'] = (
                df_nonfarm['nonfarm_proprietors_income'] / df_nonfarm['total_personal_income'] * 100
            ).round(2)
            logger.debug(f"  After merge with total income: {len(df_nonfarm)} rows")

            regional = aggregator.aggregate_to_regions(
                county_data=df_nonfarm,
                measure_type='intensive',
                value_column='pct_nonfarm_income',
                fips_column='fips',
                weight_column='total_personal_income'
            )
            measures['pct_nonfarm_income'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Calculated nonfarm income % for {len(regional)} regions")

    # ===========================================================================
    # COMPONENT INDEX 3: OTHER ECONOMIC PROSPERITY
    # ===========================================================================

    # 6. Non-Farm Proprietor Personal Income (level, not percentage)
    logger.info("\n6/11: Non-Farm Proprietor Personal Income (2022)")
    # Already collected in df_nonfarm above
    if not df_nonfarm.empty:
        regional = aggregator.aggregate_to_regions(
            county_data=df_nonfarm,
            measure_type='extensive',  # This is a total income measure
            value_column='nonfarm_proprietors_income',
            fips_column='fips'
        )
        measures['nonfarm_proprietors_income_level'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Collected nonfarm proprietor income for {len(regional)} regions")

    # 7. Personal Income Stability (coefficient of variation, 2008-2022)
    logger.info("\n7/11: Personal Income Stability (2008-2022)")
    # Fetch personal income for 15 years
    year_range = ','.join(str(y) for y in range(year_stability_start, year_current + 1))

    all_income_stability = []
    for state_abbr, state_fips in STATES.items():
        try:
            data = bea.get_regional_income(year=year_range, state=state_fips, line_codes=[1])
            if data and 'BEAAPI' in data and 'Results' in data['BEAAPI']:
                results = data['BEAAPI']['Results']
                if 'Data' in results:
                    df = pd.DataFrame(results['Data'])
                    df['state_abbr'] = state_abbr
                    if 'GeoFips' in df.columns:
                        df['fips'] = df['GeoFips'].astype(str).str.zfill(5)
                    all_income_stability.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} records")
        except Exception as e:
            logger.error(f"  Error {state_abbr}: {str(e)}")

    if all_income_stability:
        df_income_ts = pd.concat(all_income_stability, ignore_index=True)
        df_income_ts['income'] = pd.to_numeric(df_income_ts['DataValue'], errors='coerce')
        df_income_ts['year'] = pd.to_numeric(df_income_ts['TimePeriod'], errors='coerce')

        # Calculate coefficient of variation for each FIPS
        stability_data = []
        for fips in df_income_ts['fips'].unique():
            fips_data = df_income_ts[df_income_ts['fips'] == fips].copy()
            if len(fips_data) >= 10:  # Require at least 10 years of data
                mean_income = fips_data['income'].mean()
                std_income = fips_data['income'].std()
                if mean_income > 0:
                    # Coefficient of variation (lower is more stable)
                    cv = (std_income / mean_income) * 100
                    stability_data.append({
                        'fips': fips,
                        'income_stability_cv': cv,
                        'mean_income': mean_income,
                        'years_data': len(fips_data)
                    })

        if stability_data:
            df_stability = pd.DataFrame(stability_data)

            # Merge with population for weighting
            if not population_df.empty:
                df_stability = df_stability.merge(population_df, on='fips', how='left')

            regional = aggregator.aggregate_to_regions(
                county_data=df_stability,
                measure_type='intensive',
                value_column='income_stability_cv',
                fips_column='fips',
                weight_column='mean_income'  # Weight by mean income
            )
            measures['income_stability_cv'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Calculated income stability for {len(regional)} regions")

    # 8. Share of Income from Dividends, Interest, and Rent (DIR percentage)
    logger.info("\n8/11: Share of Income from DIR (2022)")
    # DIR income already collected in df_dir_2022
    # Total income already collected in df_total_income

    if not df_dir_2022.empty and not df_total_income.empty:
        df_dir_pct = df_dir_2022.copy()
        df_dir_pct['dir_income'] = pd.to_numeric(df_dir_pct['DataValue'], errors='coerce')

        # Merge with total income
        df_dir_pct = df_dir_pct.merge(
            df_total_income[['fips', 'total_personal_income']],
            on='fips',
            how='left'
        )

        # Calculate percentage
        df_dir_pct['pct_dir_income'] = (
            df_dir_pct['dir_income'] / df_dir_pct['total_personal_income'] * 100
        ).round(2)

        regional = aggregator.aggregate_to_regions(
            county_data=df_dir_pct,
            measure_type='intensive',
            value_column='pct_dir_income',
            fips_column='fips',
            weight_column='total_personal_income'
        )
        measures['pct_dir_income'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Calculated DIR income % for {len(regional)} regions")

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
    print(f"Years: Growth ({year_start}-{year_current}), Stability ({year_stability_start}-{year_current})")
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}/11")
    print()
    print("Growth Index Measures (BEA):")
    print(f"  1. Total Employment Growth Rate ({year_start}-{year_current}): {'✓' if 'total_employment_growth_rate' in measures else '✗'}")
    print(f"  2. DIR Income Growth Rate ({year_start}-{year_current}): {'✓' if 'dir_income_growth_rate' in measures else '✗'}")
    print()
    print("Component Index 3: Other Economic Prosperity (BEA):")
    print(f"  3. Nonfarm Proprietors Income (level): {'✓' if 'nonfarm_proprietors_income_level' in measures else '✗'}")
    print(f"  4. Personal Income Stability (CV {year_stability_start}-{year_current}): {'✓' if 'income_stability_cv' in measures else '✗'}")
    print(f"  5. Share of Income from DIR (%): {'✓' if 'pct_dir_income' in measures else '✗'}")
    print()
    print("Other Economic Measures:")
    print(f"  6. Per Capita Personal Income: {'✓' if 'per_capita_personal_income' in measures else '✗'}")
    print(f"  7. Farm Proprietors Income %: {'✓' if 'pct_farm_income' in measures else '✗'}")
    print(f"  8. Nonfarm Proprietors Income %: {'✓' if 'pct_nonfarm_income' in measures else '✗'}")
    print("=" * 80)


if __name__ == '__main__':
    main()
