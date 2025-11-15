#!/usr/bin/env python3
"""
Collect Census data for Demographic Growth & Renewal Index measures.

Demographic Growth & Renewal Index Measures (Nebraska Methodology):
1. Long-Run Population Growth (2000 to 2018-2022)
2. Dependency Ratio (dependent pop / working age pop)
3. Median Age
4. Millennial and Gen Z Balance Change (5-year change in % born 1985+)
5. Percent Hispanic
6. Percent Non-White

Nebraska used 2016-2020 ACS 5-year estimates. We'll use the most
recent available period (2018-2022) for Virginia analysis.
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


def collect_decennial_2000_population(census: CensusAPI, logger) -> pd.DataFrame:
    """
    Collect 2000 Decennial Census population data.

    Returns:
        DataFrame with 2000 population by county
    """
    logger.info("Collecting 2000 Decennial Census population...")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            # 2000 Decennial Census SF1 dataset
            data = census.get_data(
                dataset='dec/sf1',
                year=2000,
                variables=['P001001'],  # Total population
                geography={'for': 'county:*', 'in': f'state:{state_fips}'}
            )

            if not data or len(data) < 2:
                logger.warning(f"  No 2000 data for {state_abbr}")
                continue

            df = pd.DataFrame(data[1:], columns=data[0])

            # Build FIPS
            if 'county' in df.columns:
                df['fips'] = df['state'] + df['county']
            else:  # DC
                df['fips'] = '11001'

            # Convert to numeric
            df['pop_2000'] = pd.to_numeric(df['P001001'], errors='coerce')

            all_data.append(df[['fips', 'pop_2000']])
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting 2000 data for {state_abbr}: {str(e)}")

    if not all_data:
        logger.error("No 2000 population data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def collect_acs_population(census: CensusAPI, year: int, logger) -> pd.DataFrame:
    """
    Collect ACS 5-year population estimates.

    Returns:
        DataFrame with population by county
    """
    logger.info(f"Collecting ACS {year-4}-{year} population...")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            data = census.get_acs5_data(
                year=year,
                variables=['B01003_001E'],  # Total population
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

            df['population'] = pd.to_numeric(df['B01003_001E'], errors='coerce')

            all_data.append(df[['fips', 'population']])
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        logger.error(f"No {year} population data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def collect_age_distribution(census: CensusAPI, year: int, logger) -> pd.DataFrame:
    """
    Collect detailed age distribution from ACS B01001.

    Returns:
        DataFrame with age group populations by county
    """
    logger.info(f"Collecting ACS {year-4}-{year} age distribution...")

    # Build list of all age variables from B01001 (Sex by Age)
    # Male: 003-025, Female: 027-049
    age_vars = ['B01001_001E']  # Total population
    age_vars += [f'B01001_{str(i).zfill(3)}E' for i in range(3, 26)]  # Male age groups
    age_vars += [f'B01001_{str(i).zfill(3)}E' for i in range(27, 50)]  # Female age groups

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            data = census.get_acs5_data(
                year=year,
                variables=age_vars,
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

            # Convert all to numeric
            for var in age_vars:
                if var in df.columns:
                    df[var] = pd.to_numeric(df[var], errors='coerce')

            all_data.append(df)
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        logger.error(f"No {year} age distribution data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def calculate_dependency_ratio(df: pd.DataFrame, logger) -> pd.DataFrame:
    """
    Calculate dependency ratio from age distribution.

    Dependency Ratio = (Pop < 15 + Pop >= 65) / Pop 15-64

    B01001 age groups:
    - Under 5: Male 003, Female 027
    - 5-9: Male 004, Female 028
    - 10-14: Male 005, Female 029
    - 15-17: Male 006, Female 030
    - 18-19: Male 007, Female 031
    - 20: Male 008, Female 032
    - 21: Male 009, Female 033
    - 22-24: Male 010, Female 034
    - 25-29: Male 011, Female 035
    - 30-34: Male 012, Female 036
    - 35-39: Male 013, Female 037
    - 40-44: Male 014, Female 038
    - 45-49: Male 015, Female 039
    - 50-54: Male 016, Female 040
    - 55-59: Male 017, Female 041
    - 60-61: Male 018, Female 042
    - 62-64: Male 019, Female 043
    - 65-66: Male 020, Female 044
    - 67-69: Male 021, Female 045
    - 70-74: Male 022, Female 046
    - 75-79: Male 023, Female 047
    - 80-84: Male 024, Female 048
    - 85+: Male 025, Female 049
    """
    logger.info("  Calculating dependency ratio...")

    # Under 15 (male + female)
    under_15_male = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(3, 6))
    under_15_female = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(27, 30))
    under_15 = under_15_male + under_15_female

    # 65 and over (male + female)
    over_64_male = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(20, 26))
    over_64_female = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(44, 50))
    over_64 = over_64_male + over_64_female

    # 15-64 (male + female)
    age_15_64_male = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(6, 20))
    age_15_64_female = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(30, 44))
    age_15_64 = age_15_64_male + age_15_64_female

    # Calculate ratio
    dependent = under_15 + over_64
    df['dependency_ratio'] = (dependent / age_15_64).round(4)
    df['total_pop'] = df['B01001_001E']

    return df[['fips', 'dependency_ratio', 'total_pop']]


def calculate_millennial_genz_share(df: pd.DataFrame, year: int, logger) -> pd.DataFrame:
    """
    Calculate share of population born 1985 or after.

    For ACS 2018-2022 (year=2022): Born 1985+ means age 0-37 in 2022
    For ACS 2013-2017 (year=2017): Born 1985+ means age 0-32 in 2017

    We need to sum the appropriate age groups from B01001.
    """
    logger.info(f"  Calculating Millennial/Gen Z share for {year-4}-{year}...")

    # Determine max age for "born 1985 or after"
    max_age = year - 1985  # e.g., 2022 - 1985 = 37

    # Map age to B01001 codes
    # This is complex - we need to identify which B01001 codes cover ages 0 to max_age
    # Simplification: We'll use specific age groups

    if year == 2022:
        # Born 1985+ in 2022 = age 0-37
        # Male: 003 (under 5), 004 (5-9), 005 (10-14), 006 (15-17), 007 (18-19),
        #       008 (20), 009 (21), 010 (22-24), 011 (25-29), 012 (30-34), 013 (35-39 - partial)
        # Female: 027-037 (same pattern)

        # Age 0-34: covers all, Age 35-39: covers 35-37 only (partial)
        # For simplicity, include all of 35-39 (slight overestimate)
        male_millennial = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(3, 14))
        female_millennial = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(27, 38))

    elif year == 2017:
        # Born 1985+ in 2017 = age 0-32
        # Covers age groups 0-34 (30-34 is partial, but we include all)
        male_millennial = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(3, 13))
        female_millennial = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(27, 37))
    else:
        logger.warning(f"  Unexpected year {year} for Millennial/Gen Z calculation")
        male_millennial = 0
        female_millennial = 0

    millennial_genz = male_millennial + female_millennial
    total_pop = df['B01001_001E']

    df['pct_millennial_genz'] = (millennial_genz / total_pop * 100).round(2)
    df['total_pop'] = total_pop

    return df[['fips', 'pct_millennial_genz', 'total_pop']]


def collect_hispanic_data(census: CensusAPI, year: int, logger) -> pd.DataFrame:
    """
    Collect Hispanic/Latino ethnicity data from ACS B03003.

    Returns:
        DataFrame with percent Hispanic by county
    """
    logger.info(f"Collecting ACS {year-4}-{year} Hispanic data...")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            data = census.get_acs5_data(
                year=year,
                variables=['B03003_001E', 'B03003_003E'],  # Total, Hispanic
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

            df['total'] = pd.to_numeric(df['B03003_001E'], errors='coerce')
            df['hispanic'] = pd.to_numeric(df['B03003_003E'], errors='coerce')
            df['pct_hispanic'] = (df['hispanic'] / df['total'] * 100).round(2)

            all_data.append(df[['fips', 'pct_hispanic', 'total']])
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        logger.error(f"No {year} Hispanic data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def collect_race_data(census: CensusAPI, year: int, logger) -> pd.DataFrame:
    """
    Collect race data from ACS B02001.

    Returns:
        DataFrame with percent non-white by county
    """
    logger.info(f"Collecting ACS {year-4}-{year} race data...")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            data = census.get_acs5_data(
                year=year,
                variables=['B02001_001E', 'B02001_002E'],  # Total, White alone
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

            df['total'] = pd.to_numeric(df['B02001_001E'], errors='coerce')
            df['white_alone'] = pd.to_numeric(df['B02001_002E'], errors='coerce')
            df['non_white'] = df['total'] - df['white_alone']
            df['pct_non_white'] = (df['non_white'] / df['total'] * 100).round(2)

            all_data.append(df[['fips', 'pct_non_white', 'total']])
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        logger.error(f"No {year} race data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def collect_median_age(census: CensusAPI, year: int, logger) -> pd.DataFrame:
    """
    Collect median age from ACS B01002.

    Returns:
        DataFrame with median age by county
    """
    logger.info(f"Collecting ACS {year-4}-{year} median age...")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            data = census.get_acs5_data(
                year=year,
                variables=['B01002_001E'],  # Median age
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

            df['median_age'] = pd.to_numeric(df['B01002_001E'], errors='coerce')

            all_data.append(df[['fips', 'median_age']])
            logger.debug(f"  {state_abbr}: {len(df)} counties")

        except Exception as e:
            logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        logger.error(f"No {year} median age data collected")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"  Collected {len(combined)} county records")

    return combined


def main():
    """Main execution."""

    logger = setup_logger('demographic_renewal_collection')
    census = CensusAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("DEMOGRAPHIC GROWTH & RENEWAL INDEX - DATA COLLECTION")
    logger.info("=" * 80)

    start_time = datetime.now()
    year_recent = 2022  # 2018-2022 ACS
    year_earlier = 2017  # 2013-2017 ACS

    measures = {}

    # ===========================================================================
    # MEASURE 4.1: LONG-RUN POPULATION GROWTH (2000 to 2018-2022)
    # ===========================================================================

    logger.info("\n1/6: Long-Run Population Growth (2000 to 2018-2022)")

    pop_2000 = collect_decennial_2000_population(census, logger)
    pop_2022 = collect_acs_population(census, year_recent, logger)

    if not pop_2000.empty and not pop_2022.empty:
        # Merge and calculate growth
        growth = pop_2000.merge(pop_2022, on='fips', how='inner')
        growth['long_run_pop_growth'] = (
            ((growth['population'] - growth['pop_2000']) / growth['pop_2000']) * 100
        ).round(2)

        logger.info(f"  Calculated growth for {len(growth)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=growth,
            measure_type='intensive',
            value_column='long_run_pop_growth',
            fips_column='fips',
            weight_column='population'
        )
        measures['long_run_pop_growth'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate long-run population growth")

    # ===========================================================================
    # MEASURE 4.2: DEPENDENCY RATIO
    # ===========================================================================

    logger.info("\n2/6: Dependency Ratio (2018-2022)")

    age_dist_2022 = collect_age_distribution(census, year_recent, logger)

    if not age_dist_2022.empty:
        dependency = calculate_dependency_ratio(age_dist_2022, logger)

        logger.info(f"  Calculated dependency ratio for {len(dependency)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=dependency,
            measure_type='intensive',
            value_column='dependency_ratio',
            fips_column='fips',
            weight_column='total_pop'
        )
        measures['dependency_ratio'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate dependency ratio")

    # ===========================================================================
    # MEASURE 4.3: MEDIAN AGE
    # ===========================================================================

    logger.info("\n3/6: Median Age (2018-2022)")

    median_age_data = collect_median_age(census, year_recent, logger)

    if not median_age_data.empty:
        # Aggregate to regions
        # Median age is tricky to aggregate - we'll use population-weighted average as proxy
        # First need to add population
        pop_2022_for_weight = collect_acs_population(census, year_recent, logger)
        median_age_data = median_age_data.merge(pop_2022_for_weight, on='fips', how='left')

        regional = aggregator.aggregate_to_regions(
            county_data=median_age_data,
            measure_type='intensive',
            value_column='median_age',
            fips_column='fips',
            weight_column='population'
        )
        measures['median_age'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not collect median age")

    # ===========================================================================
    # MEASURE 4.4: MILLENNIAL AND GEN Z BALANCE CHANGE
    # ===========================================================================

    logger.info("\n4/6: Millennial and Gen Z Balance Change (2013-2017 to 2018-2022)")

    # Collect age distribution for both periods
    age_dist_2017 = collect_age_distribution(census, year_earlier, logger)
    # Already have age_dist_2022 from above

    if not age_dist_2017.empty and not age_dist_2022.empty:
        millennial_2017 = calculate_millennial_genz_share(age_dist_2017, year_earlier, logger)
        millennial_2022 = calculate_millennial_genz_share(age_dist_2022, year_recent, logger)

        # Merge and calculate change
        millennial_change = millennial_2017.merge(
            millennial_2022,
            on='fips',
            how='inner',
            suffixes=('_2017', '_2022')
        )
        millennial_change['millennial_genz_balance_change'] = (
            millennial_change['pct_millennial_genz_2022'] -
            millennial_change['pct_millennial_genz_2017']
        ).round(2)

        logger.info(f"  Calculated change for {len(millennial_change)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=millennial_change,
            measure_type='intensive',
            value_column='millennial_genz_balance_change',
            fips_column='fips',
            weight_column='total_pop_2022'
        )
        measures['millennial_genz_balance_change'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate Millennial/Gen Z balance change")

    # ===========================================================================
    # MEASURE 4.5: PERCENT HISPANIC
    # ===========================================================================

    logger.info("\n5/6: Percent Hispanic (2018-2022)")

    hispanic_data = collect_hispanic_data(census, year_recent, logger)

    if not hispanic_data.empty:
        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=hispanic_data,
            measure_type='intensive',
            value_column='pct_hispanic',
            fips_column='fips',
            weight_column='total'
        )
        measures['pct_hispanic'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not collect Hispanic data")

    # ===========================================================================
    # MEASURE 4.6: PERCENT NON-WHITE
    # ===========================================================================

    logger.info("\n6/6: Percent Non-White (2018-2022)")

    race_data = collect_race_data(census, year_recent, logger)

    if not race_data.empty:
        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=race_data,
            measure_type='intensive',
            value_column='pct_non_white',
            fips_column='fips',
            weight_column='total'
        )
        measures['pct_non_white'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not collect race data")

    end_time = datetime.now()

    # Save all measures
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year_recent}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Recent period: {year_recent-4}-{year_recent} (ACS 5-year estimates)")
    print(f"Earlier period: {year_earlier-4}-{year_earlier} (ACS 5-year estimates)")
    print(f"Long-run period: 2000 to {year_recent-4}-{year_recent}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}/6")
    print()
    print("Demographic Growth & Renewal Measures:")
    print(f"  4.1 Long-Run Population Growth: {'✓' if 'long_run_pop_growth' in measures else '✗'}")
    print(f"  4.2 Dependency Ratio: {'✓' if 'dependency_ratio' in measures else '✗'}")
    print(f"  4.3 Median Age: {'✓' if 'median_age' in measures else '✗'}")
    print(f"  4.4 Millennial and Gen Z Balance Change: {'✓' if 'millennial_genz_balance_change' in measures else '✗'}")
    print(f"  4.5 Percent Hispanic: {'✓' if 'pct_hispanic' in measures else '✗'}")
    print(f"  4.6 Percent Non-White: {'✓' if 'pct_non_white' in measures else '✗'}")
    print("=" * 80)


if __name__ == '__main__':
    main()
