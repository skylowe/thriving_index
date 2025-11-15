#!/usr/bin/env python3
"""
Collect all Census ACS measures using the existing working infrastructure.

This script systematically collects all HIGH-confidence measures from Census ACS
for all 54 regions.
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


def collect_and_aggregate_measure(
    census: CensusAPI,
    aggregator: RegionalAggregator,
    year: int,
    variables: list,
    measure_name: str,
    calc_func=None,
    measure_type='intensive',
    logger=None
) -> pd.DataFrame:
    """
    Generic function to collect a Census measure and aggregate to regions.

    Args:
        census: Census API client
        aggregator: Regional aggregator
        year: Year of ACS estimates
        variables: List of ACS variable codes
        measure_name: Name of the measure (will be the column name)
        calc_func: Optional function to calculate derived measure
        measure_type: 'extensive' or 'intensive'
        logger: Logger instance

    Returns:
        DataFrame with regional data
    """
    if logger:
        logger.info(f"Collecting: {measure_name}")

    all_data = []

    for state_abbr, state_fips in STATES.items():
        try:
            data = census.get_acs5_data(
                year=year,
                variables=variables,
                geography='county:*',
                state=state_fips
            )

            if not data:
                continue

            df = pd.DataFrame(data)

            # Build FIPS
            if 'county' in df.columns:
                df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
            else:  # DC
                df['fips'] = '11001'

            # Convert to numeric
            for var in variables:
                if var in df.columns:
                    df[var] = pd.to_numeric(df[var], errors='coerce')

            # Apply calculation function
            if calc_func:
                df = calc_func(df, measure_name)
            else:
                # If no calculation function, rename the first variable to the measure name
                if len(variables) == 1 and variables[0] in df.columns:
                    df[measure_name] = df[variables[0]]

            all_data.append(df)

        except Exception as e:
            if logger:
                logger.error(f"  Error collecting {state_abbr}: {str(e)}")

    if not all_data:
        if logger:
            logger.error(f"No data collected for {measure_name}")
        return pd.DataFrame()

    # Combine all states
    combined = pd.concat(all_data, ignore_index=True)

    # Determine weight column for intensive measures
    weight_col = None
    if measure_type == 'intensive':
        # Look for population or universe column
        potential_weights = [c for c in combined.columns if 'total' in c.lower() or 'universe' in c.lower() or 'pop' in c.lower()]
        if potential_weights:
            weight_col = potential_weights[0]
        else:
            # Add population for weighting
            pop_data = []
            for state_abbr, state_fips in STATES.items():
                try:
                    pop = census.get_population(year=year, state=state_fips)
                    pop_df = pd.DataFrame(pop)
                    if 'county' in pop_df.columns:
                        pop_df['fips'] = state_fips + pop_df['county'].astype(str).str.zfill(3)
                    else:
                        pop_df['fips'] = '11001'
                    pop_df = pop_df.rename(columns={'B01001_001E': 'population'})
                    pop_data.append(pop_df[['fips', 'population']])
                except:
                    pass
            if pop_data:
                pop_combined = pd.concat(pop_data, ignore_index=True)
                pop_combined['population'] = pd.to_numeric(pop_combined['population'], errors='coerce')
                combined = combined.merge(pop_combined, on='fips', how='left')
                weight_col = 'population'

    # Aggregate to regions
    regional = aggregator.aggregate_to_regions(
        county_data=combined,
        measure_type=measure_type,
        value_column=measure_name,
        fips_column='fips',
        weight_column=weight_col
    )

    # Add metadata
    regional = aggregator.add_region_metadata(regional)

    if logger:
        logger.info(f"  Aggregated to {len(regional)} regions")

    return regional


def main():
    """Collect all Census ACS measures."""

    logger = setup_logger('acs_collection')
    census = CensusAPI()
    aggregator = RegionalAggregator()
    year = 2022

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("CENSUS ACS COMPREHENSIVE DATA COLLECTION")
    logger.info(f"Year: {year}")
    logger.info("=" * 80)

    start_time = datetime.now()
    measures = {}

    # 1. Median Age
    logger.info("\n1/13: Median Age")
    measures['median_age'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B01002_001E'],
        measure_name='median_age',
        logger=logger
    )

    # 2. Percent Age 25-54
    logger.info("\n2/13: Percent Age 25-54")
    def calc_age_25_54(df, measure_name):
        total = df['B01001_001E']
        male_25_54 = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(11, 17))
        female_25_54 = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(35, 41))
        df[measure_name] = ((male_25_54 + female_25_54) / total * 100).round(2)
        df['total_pop'] = total
        return df

    age_vars = ['B01001_001E'] + [f'B01001_{str(i).zfill(3)}E' for i in list(range(11, 17)) + list(range(35, 41))]
    measures['pct_age_25_54'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=age_vars,
        measure_name='pct_age_25_54',
        calc_func=calc_age_25_54,
        logger=logger
    )

    # 3-5. Educational Attainment (3 measures)
    logger.info("\n3-5/13: Educational Attainment (3 measures)")
    ed_vars = ['B15003_001E'] + [f'B15003_{str(i).zfill(3)}E' for i in range(17, 26)]

    def calc_hs_or_higher(df, measure_name):
        total = df['B15003_001E']
        hs_plus = sum(df[f'B15003_{str(i).zfill(3)}E'] for i in range(17, 26))
        df[measure_name] = (hs_plus / total * 100).round(2)
        df['total_25plus'] = total
        return df

    measures['pct_hs_or_higher'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=ed_vars,
        measure_name='pct_hs_or_higher',
        calc_func=calc_hs_or_higher,
        logger=logger
    )

    def calc_some_college(df, measure_name):
        total = df['B15003_001E']
        some_college = df['B15003_019E'] + df['B15003_020E'] + df['B15003_021E']
        df[measure_name] = (some_college / total * 100).round(2)
        df['total_25plus'] = total
        return df

    measures['pct_some_college'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=ed_vars,
        measure_name='pct_some_college',
        calc_func=calc_some_college,
        logger=logger
    )

    def calc_bachelors_plus(df, measure_name):
        total = df['B15003_001E']
        bachelors_plus = df['B15003_022E'] + df['B15003_023E'] + df['B15003_024E'] + df['B15003_025E']
        df[measure_name] = (bachelors_plus / total * 100).round(2)
        df['total_25plus'] = total
        return df

    measures['pct_bachelors_or_higher'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=ed_vars,
        measure_name='pct_bachelors_or_higher',
        calc_func=calc_bachelors_plus,
        logger=logger
    )

    # 6-8. Housing Measures
    logger.info("\n6/13: Median Home Value")
    measures['median_home_value'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B25077_001E'],
        measure_name='median_home_value',
        logger=logger
    )

    logger.info("\n7/13: Median Gross Rent")
    measures['median_gross_rent'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B25064_001E'],
        measure_name='median_gross_rent',
        logger=logger
    )

    logger.info("\n8/13: Housing Built Last 10 Years")
    def calc_recent_housing(df, measure_name):
        total = df['B25034_001E']
        recent = df['B25034_002E'] + df['B25034_003E']
        df[measure_name] = (recent / total * 100).round(2)
        df['total_housing_units'] = total
        return df

    measures['pct_housing_built_last_10_years'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B25034_001E', 'B25034_002E', 'B25034_003E'],
        measure_name='pct_housing_built_last_10_years',
        calc_func=calc_recent_housing,
        logger=logger
    )

    # 9. Percent Uninsured
    logger.info("\n9/13: Percent Uninsured")
    def calc_uninsured(df, measure_name):
        total = df['B27001_001E']
        # Sum all "no health insurance coverage" columns
        uninsured_cols = ['B27001_005E', 'B27001_008E', 'B27001_011E', 'B27001_014E',
                         'B27001_017E', 'B27001_020E', 'B27001_023E', 'B27001_026E',
                         'B27001_029E', 'B27001_033E', 'B27001_036E', 'B27001_039E',
                         'B27001_042E', 'B27001_045E', 'B27001_048E', 'B27001_051E',
                         'B27001_054E', 'B27001_057E']
        no_insurance = sum(df[col] for col in uninsured_cols if col in df.columns)
        df[measure_name] = (no_insurance / total * 100).round(2)
        df['health_insurance_universe'] = total
        return df

    uninsured_vars = ['B27001_001E'] + ['B27001_005E', 'B27001_008E', 'B27001_011E', 'B27001_014E',
                                       'B27001_017E', 'B27001_020E', 'B27001_023E', 'B27001_026E',
                                       'B27001_029E', 'B27001_033E', 'B27001_036E', 'B27001_039E',
                                       'B27001_042E', 'B27001_045E', 'B27001_048E', 'B27001_051E',
                                       'B27001_054E', 'B27001_057E']
    measures['pct_uninsured'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=uninsured_vars,
        measure_name='pct_uninsured',
        calc_func=calc_uninsured,
        logger=logger
    )

    # 10. Single Parent Households
    logger.info("\n10/13: Single Parent Households")
    def calc_single_parent(df, measure_name):
        total = df['B09002_001E']
        single_parent = df['B09002_009E'] + df['B09002_015E']
        df[measure_name] = (single_parent / total * 100).round(2)
        df['children_universe'] = total
        return df

    measures['pct_single_parent_households'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B09002_001E', 'B09002_009E', 'B09002_015E'],
        measure_name='pct_single_parent_households',
        calc_func=calc_single_parent,
        logger=logger
    )

    # 11. Gini Coefficient
    logger.info("\n11/13: Gini Coefficient")
    measures['gini_coefficient'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B19083_001E'],
        measure_name='gini_coefficient',
        logger=logger
    )

    # 12. Labor Force Participation (using detailed table B23025)
    logger.info("\n12/13: Labor Force Participation Rate")
    def calc_lfpr(df, measure_name):
        total_16plus = df['B23025_003E']  # Civilian labor force + not in labor force
        in_labor_force = df['B23025_002E']  # In labor force
        df[measure_name] = (in_labor_force / total_16plus * 100).round(2)
        df['labor_force_universe'] = total_16plus
        return df

    measures['labor_force_participation_rate'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B23025_002E', 'B23025_003E'],
        measure_name='labor_force_participation_rate',
        calc_func=calc_lfpr,
        logger=logger
    )

    # 13. Unemployment Rate (from same table B23025)
    logger.info("\n13/13: Unemployment Rate")
    def calc_unemployment(df, measure_name):
        labor_force = df['B23025_003E']  # In civilian labor force
        unemployed = df['B23025_005E']  # Unemployed
        df[measure_name] = (unemployed / labor_force * 100).round(2)
        df['labor_force_employed_unemployed'] = labor_force
        return df

    measures['unemployment_rate'] = collect_and_aggregate_measure(
        census, aggregator, year,
        variables=['B23025_003E', 'B23025_005E'],
        measure_name='unemployment_rate',
        calc_func=calc_unemployment,
        logger=logger
    )

    end_time = datetime.now()

    # Save all measures
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    saved_count = 0
    for measure_name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{measure_name}_{year}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")
            saved_count += 1
        else:
            logger.warning(f"  Skipped {measure_name}: No data")

    # Print summary
    print()
    print("=" * 80)
    print("COLLECTION SUMMARY")
    print("=" * 80)
    print(f"Year: {year}")
    print(f"Measures collected: {saved_count}/{len(measures)}")
    print(f"Output directory: {output_dir}")
    print(f"Time elapsed: {end_time - start_time}")
    print("=" * 80)
    print()
    print("COMPLETE!")
    print("=" * 80)


if __name__ == '__main__':
    main()
