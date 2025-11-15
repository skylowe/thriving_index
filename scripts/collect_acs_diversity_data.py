#!/usr/bin/env python3
"""
Collect Census ACS data for Economic Opportunity & Diversity Index measures.

Economic Opportunity & Diversity Index Measures (Nebraska Methodology):
- Occupation Diversity (ACS Table S2401, 2016-2020)
- Share of Telecommuters (ACS Table B08128, 2016-2020)

Note: Nebraska used 2016-2020 ACS 5-year estimates. We'll use the most
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


def collect_acs_occupation_data(census: CensusAPI, year: int, state_fips: str,
                                state_abbr: str, logger) -> pd.DataFrame:
    """
    Collect ACS occupation data for diversity calculation.

    Args:
        census: Census API client
        year: Year (end year of 5-year period, e.g., 2022 for 2018-2022)
        state_fips: State FIPS code
        state_abbr: State abbreviation
        logger: Logger instance

    Returns:
        DataFrame with occupation employment by county
    """
    logger.debug(f"  Fetching ACS occupation data for {state_abbr} ({year-4}-{year})")

    # ACS Table S2401 - Occupation by Sex and Median Earnings
    # Major occupation categories
    variables = [
        'S2401_C01_001E',  # Total employed
        'S2401_C01_002E',  # Management, business, science, and arts
        'S2401_C01_003E',  # Service occupations
        'S2401_C01_004E',  # Sales and office occupations
        'S2401_C01_005E',  # Natural resources, construction, and maintenance
        'S2401_C01_006E',  # Production, transportation, and material moving
    ]

    try:
        data = census.get_data(
            dataset='acs/acs5/subject',
            year=year,
            variables=variables,
            geography={'for': 'county:*', 'in': f'state:{state_fips}'}
        )

        if not data or len(data) < 2:
            logger.warning(f"  No occupation data returned for {state_abbr}")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
        df['fips'] = df['state'] + df['county']
        df['state_abbr'] = state_abbr

        # Convert to numeric
        for var in variables:
            df[var] = pd.to_numeric(df[var], errors='coerce')

        # Rename to friendly names
        df = df.rename(columns={
            'S2401_C01_001E': 'total_employed',
            'S2401_C01_002E': 'mgmt_business_science_arts',
            'S2401_C01_003E': 'service',
            'S2401_C01_004E': 'sales_office',
            'S2401_C01_005E': 'natural_resources_construction',
            'S2401_C01_006E': 'production_transportation'
        })

        df = df[df['total_employed'].notna() & (df['total_employed'] > 0)].copy()

        logger.debug(f"  Collected {len(df)} counties")
        return df

    except Exception as e:
        logger.error(f"  Error collecting occupation data for {state_abbr}: {str(e)}")
        return pd.DataFrame()


def collect_acs_telecommuter_data(census: CensusAPI, year: int, state_fips: str,
                                  state_abbr: str, logger) -> pd.DataFrame:
    """
    Collect ACS telecommuter data.

    Args:
        census: Census API client
        year: Year (end year of 5-year period)
        state_fips: State FIPS code
        state_abbr: State abbreviation
        logger: Logger instance

    Returns:
        DataFrame with telecommuter counts by county
    """
    logger.debug(f"  Fetching ACS telecommuter data for {state_abbr} ({year-4}-{year})")

    # ACS Table B08128 - Means of Transportation to Work by Class of Worker
    # We need workers who work at home but are NOT self-employed
    variables = [
        'B08128_001E',  # Total workers
        'B08128_002E',  # Worked at home (total)
        'B08128_003E',  # Worked at home: Private wage and salary workers
        'B08128_008E',  # Worked at home: Government workers
        'B08128_013E',  # Worked at home: Self-employed (to exclude)
    ]

    try:
        data = census.get_data(
            dataset='acs/acs5',
            year=year,
            variables=variables,
            geography={'for': 'county:*', 'in': f'state:{state_fips}'}
        )

        if not data or len(data) < 2:
            logger.warning(f"  No telecommuter data returned for {state_abbr}")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
        df['fips'] = df['state'] + df['county']
        df['state_abbr'] = state_abbr

        # Convert to numeric
        for var in variables:
            df[var] = pd.to_numeric(df[var], errors='coerce')

        # Calculate telecommuters (work at home but not self-employed)
        # Telecommuters = Private wage workers at home + Government workers at home
        df['telecommuters'] = df['B08128_003E'].fillna(0) + df['B08128_008E'].fillna(0)
        df['total_workers'] = df['B08128_001E']

        # Calculate share
        df['share_telecommuters'] = (
            df['telecommuters'] / df['total_workers'] * 100
        ).round(2)

        df = df[df['total_workers'].notna() & (df['total_workers'] > 0)].copy()

        logger.debug(f"  Collected {len(df)} counties")
        return df

    except Exception as e:
        logger.error(f"  Error collecting telecommuter data for {state_abbr}: {str(e)}")
        return pd.DataFrame()


def calculate_occupation_diversity_index(df: pd.DataFrame, logger) -> pd.DataFrame:
    """
    Calculate occupation diversity index for each county.

    Nebraska methodology: Index matching US allocation of employment by occupation.
    Formula: Diversity_Index = 1 - Σ|county_share_i - US_share_i| / 2

    Higher value = more similar to US = more diverse.
    """
    logger.info("  Calculating occupation diversity index...")

    occupation_cols = [
        'mgmt_business_science_arts',
        'service',
        'sales_office',
        'natural_resources_construction',
        'production_transportation'
    ]

    # Calculate US occupation shares
    us_totals = df[occupation_cols].sum()
    us_total = us_totals.sum()
    us_shares = (us_totals / us_total).to_dict()

    diversity_results = []

    for _, row in df.iterrows():
        fips = row['fips']
        total_employed = row['total_employed']

        if total_employed == 0 or pd.isna(total_employed):
            continue

        # Calculate county occupation shares
        dissimilarity = 0
        for occupation in occupation_cols:
            us_share = us_shares.get(occupation, 0)
            county_value = row.get(occupation, 0)
            if pd.isna(county_value):
                county_value = 0
            county_share = county_value / total_employed
            dissimilarity += abs(county_share - us_share)

        # Diversity index = 1 - dissimilarity/2
        diversity_index = 1 - (dissimilarity / 2)

        diversity_results.append({
            'fips': fips,
            'occupation_diversity_index': round(diversity_index, 4),
            'total_employed': total_employed
        })

    return pd.DataFrame(diversity_results)


def main():
    """Main execution."""

    logger = setup_logger('acs_diversity_collection')
    census = CensusAPI()
    aggregator = RegionalAggregator()

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("ECONOMIC OPPORTUNITY & DIVERSITY - ACS MEASURES")
    logger.info("=" * 80)

    start_time = datetime.now()
    # Use most recent 5-year period
    year_end = 2022  # 2018-2022 ACS 5-year estimates

    measures = {}

    # ===========================================================================
    # MEASURE 2.6: OCCUPATION DIVERSITY
    # ===========================================================================

    logger.info(f"\n1/2: Occupation Diversity Index ({year_end-4}-{year_end})")

    all_occupation_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_acs_occupation_data(census, year_end, state_fips, state_abbr, logger)
        if not df.empty:
            all_occupation_data.append(df)

    if all_occupation_data:
        combined_occupation = pd.concat(all_occupation_data, ignore_index=True)
        logger.info(f"  Collected occupation data for {len(combined_occupation)} counties")

        # Calculate diversity index
        diversity_df = calculate_occupation_diversity_index(combined_occupation, logger)

        if not diversity_df.empty:
            logger.info(f"  Calculated diversity for {len(diversity_df)} counties")

            # Aggregate to regions
            regional = aggregator.aggregate_to_regions(
                county_data=diversity_df,
                measure_type='intensive',
                value_column='occupation_diversity_index',
                fips_column='fips',
                weight_column='total_employed'
            )
            measures['occupation_diversity_index'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate occupation diversity")

    # ===========================================================================
    # MEASURE 2.7: SHARE OF TELECOMMUTERS
    # ===========================================================================

    logger.info(f"\n2/2: Share of Telecommuters ({year_end-4}-{year_end})")

    all_telecommuter_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_acs_telecommuter_data(census, year_end, state_fips, state_abbr, logger)
        if not df.empty:
            all_telecommuter_data.append(df)

    if all_telecommuter_data:
        combined_telecommuter = pd.concat(all_telecommuter_data, ignore_index=True)
        logger.info(f"  Collected telecommuter data for {len(combined_telecommuter)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=combined_telecommuter,
            measure_type='intensive',
            value_column='share_telecommuters',
            fips_column='fips',
            weight_column='total_workers'
        )
        measures['share_telecommuters'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate share of telecommuters")

    end_time = datetime.now()

    # Save all measures
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)

    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year_end}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Period: {year_end-4}-{year_end} (ACS 5-year estimates)")
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}/2")
    print()
    print("Economic Opportunity & Diversity Measures (ACS):")
    print(f"  2.6 Occupation Diversity Index: {'✓' if 'occupation_diversity_index' in measures else '✗'}")
    print(f"  2.7 Share of Telecommuters: {'✓' if 'share_telecommuters' in measures else '✗'}")
    print()
    print("Note: Post-COVID data (2020+) may show significantly higher")
    print("      telecommuting rates than pre-pandemic baseline.")
    print("=" * 80)


if __name__ == '__main__':
    main()
