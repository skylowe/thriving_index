#!/usr/bin/env python3
"""
Collect data for Economic Opportunity & Diversity Index measures.

Economic Opportunity & Diversity Index Measures (Nebraska Methodology):
1. Entrepreneurial Activity (BDS) - DEFERRED (requires bulk download)
2. Non-Farm Proprietors Per 1,000 Persons (BEA CAEMP25)
3. Employer Establishments Per 1,000 Residents (Census CBP)
4. Share of Workers in Non-Employer Establishment (Census CBP + NES)
5. Industry Diversity (Census CBP)
6. Occupation Diversity (Census ACS) - separate script
7. Share of Telecommuters (Census ACS) - separate script

This script collects measures 2, 3, 4, and 5 (BEA and CBP data).
ACS measures (6, 7) are collected in a separate script.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import requests
import numpy as np

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bea_api import BEAAPI
from src.api_clients.census_api import CensusAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger
from src.utils.config import get_api_key

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


def collect_bea_measure(bea: BEAAPI, method_name: str, year, logger) -> pd.DataFrame:
    """Generic function to collect BEA data across all states."""
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


def collect_cbp_data(year: int, state_fips: str, api_key: str, logger,
                     naics_code: str = '00', variables: str = 'EMP,ESTAB') -> pd.DataFrame:
    """Collect Census County Business Patterns data."""
    logger.debug(f"  Fetching CBP data for state {state_fips}, year {year}")

    base_url = f"https://api.census.gov/data/{year}/cbp"

    params = {
        'get': variables,
        'for': 'county:*',
        'in': f'state:{state_fips}',
        'NAICS2017': naics_code,
        'key': api_key
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) < 2:
            logger.warning(f"  No data returned for state {state_fips}")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
        df['fips'] = df['state'] + df['county']

        # Convert to numeric
        for col in df.columns:
            if col not in ['fips', 'state', 'county', 'NAICS2017', 'NAICS2017_LABEL']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df[df['EMP'].notna() & (df['EMP'] > 0)].copy() if 'EMP' in df.columns else df

        logger.debug(f"  Collected {len(df)} counties")
        return df

    except Exception as e:
        logger.error(f"  Error collecting CBP data: {str(e)}")
        return pd.DataFrame()


def collect_nonemp_data(year: int, state_fips: str, api_key: str, logger) -> pd.DataFrame:
    """Collect Census Nonemployer Statistics data."""
    logger.debug(f"  Fetching NES data for state {state_fips}, year {year}")

    # Note: NES API endpoint and variables may vary by year
    # 2020 is typically the most recent available
    base_url = f"https://api.census.gov/data/{year}/nonemp"

    params = {
        'get': 'NONEMP,RCPDEMP',  # Number of firms, receipts
        'for': 'county:*',
        'in': f'state:{state_fips}',
        'NAICS2017': '00',  # Total for all sectors
        'key': api_key
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) < 2:
            logger.warning(f"  No NES data returned for state {state_fips}")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
        df['fips'] = df['state'] + df['county']

        df['NONEMP'] = pd.to_numeric(df['NONEMP'], errors='coerce')
        df = df[df['NONEMP'].notna()].copy()

        logger.debug(f"  Collected {len(df)} counties")
        return df

    except Exception as e:
        logger.error(f"  Error collecting NES data: {str(e)}")
        return pd.DataFrame()


def calculate_industry_diversity_index(df: pd.DataFrame, logger) -> pd.DataFrame:
    """
    Calculate industry diversity index for each county.

    Nebraska methodology: Index matching US allocation of employment by industry.
    Higher value = more similar to US = more diverse.

    Formula: Diversity_Index = 1 - Σ|county_share_i - US_share_i| / 2
    """
    logger.info("  Calculating industry diversity index...")

    # Calculate US total employment by industry for reference
    us_totals = df.groupby('NAICS2017')['EMP'].sum()
    us_total_emp = us_totals.sum()
    us_shares = (us_totals / us_total_emp).to_dict()

    diversity_results = []

    for fips in df['fips'].unique():
        county_data = df[df['fips'] == fips]

        # Calculate county employment shares by industry
        county_totals = county_data.groupby('NAICS2017')['EMP'].sum()
        county_total_emp = county_totals.sum()

        if county_total_emp == 0:
            continue

        county_shares = county_totals / county_total_emp

        # Calculate dissimilarity index
        dissimilarity = 0
        for industry in us_shares.keys():
            us_share = us_shares.get(industry, 0)
            county_share = county_shares.get(industry, 0)
            dissimilarity += abs(county_share - us_share)

        # Diversity index = 1 - dissimilarity/2
        diversity_index = 1 - (dissimilarity / 2)

        diversity_results.append({
            'fips': fips,
            'industry_diversity_index': round(diversity_index, 4),
            'total_employment': county_total_emp
        })

    return pd.DataFrame(diversity_results)


def main():
    """Main execution."""

    logger = setup_logger('economic_opportunity_collection')
    bea = BEAAPI()
    census = CensusAPI()
    aggregator = RegionalAggregator()

    api_key = get_api_key('CENSUS_KEY')
    if not api_key:
        logger.error("Census API key not found. Set CENSUS_KEY environment variable.")
        return

    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("ECONOMIC OPPORTUNITY & DIVERSITY INDEX DATA COLLECTION")
    logger.info("=" * 80)

    start_time = datetime.now()
    year_current = 2022  # For BEA data
    year_cbp = 2021  # CBP 2022 may not be available yet
    year_nes = 2020  # NES typically has more lag

    measures = {}

    # Get population data for per-capita calculations
    logger.info("\nFetching population data...")
    population_data = []
    for state_abbr, state_fips in STATES.items():
        try:
            pop_data = census.get_population(year_current, state_fips)
            if pop_data:
                df = pd.DataFrame(pop_data)
                if 'state' in df.columns and 'county' in df.columns:
                    df['fips'] = df['state'] + df['county']
                    df['population'] = pd.to_numeric(df.get('B01003_001E', df.get('POP', 0)), errors='coerce')
                    population_data.append(df[['fips', 'population']])
        except Exception as e:
            logger.warning(f"  Could not fetch population for {state_abbr}: {e}")

    population_df = pd.concat(population_data, ignore_index=True) if population_data else pd.DataFrame()
    logger.info(f"  Population data for {len(population_df)} jurisdictions")

    # ===========================================================================
    # MEASURE 2.2: NON-FARM PROPRIETORS PER 1,000 PERSONS
    # ===========================================================================

    logger.info("\n1/4: Non-Farm Proprietors Per 1,000 Persons (2022)")

    df_proprietors = collect_bea_measure(bea, 'get_nonfarm_proprietor_employment', year_current, logger)

    if not df_proprietors.empty and not population_df.empty:
        df_proprietors['proprietors'] = pd.to_numeric(df_proprietors['DataValue'], errors='coerce')

        # Merge with population
        df_proprietors = df_proprietors.merge(population_df, on='fips', how='left')

        # Calculate per 1,000
        df_proprietors['proprietors_per_1000'] = (
            df_proprietors['proprietors'] / df_proprietors['population'] * 1000
        ).round(2)

        logger.info(f"  Collected data for {len(df_proprietors)} jurisdictions")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=df_proprietors,
            measure_type='intensive',
            value_column='proprietors_per_1000',
            fips_column='fips',
            weight_column='population'
        )
        measures['proprietors_per_1000'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate proprietors per 1,000")

    # ===========================================================================
    # MEASURE 2.3: EMPLOYER ESTABLISHMENTS PER 1,000 RESIDENTS
    # ===========================================================================

    logger.info(f"\n2/4: Employer Establishments Per 1,000 Residents ({year_cbp})")

    all_cbp_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_cbp_data(year_cbp, state_fips, api_key, logger)
        if not df.empty:
            df['state_abbr'] = state_abbr
            all_cbp_data.append(df)

    if all_cbp_data and not population_df.empty:
        combined_cbp = pd.concat(all_cbp_data, ignore_index=True)
        logger.info(f"  Total counties: {len(combined_cbp)}")

        # Merge with population
        combined_cbp = combined_cbp.merge(population_df, on='fips', how='left')

        # Calculate per 1,000
        combined_cbp['establishments_per_1000'] = (
            combined_cbp['ESTAB'] / combined_cbp['population'] * 1000
        ).round(2)

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=combined_cbp,
            measure_type='intensive',
            value_column='establishments_per_1000',
            fips_column='fips',
            weight_column='population'
        )
        measures['establishments_per_1000'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate establishments per 1,000")

    # ===========================================================================
    # MEASURE 2.4: SHARE OF WORKERS IN NON-EMPLOYER ESTABLISHMENT
    # ===========================================================================

    logger.info(f"\n3/4: Share of Workers in Non-Employer Establishment ({year_nes})")

    # Collect nonemployer statistics
    all_nes_data = []
    for state_abbr, state_fips in STATES.items():
        df = collect_nonemp_data(year_nes, state_fips, api_key, logger)
        if not df.empty:
            df['state_abbr'] = state_abbr
            all_nes_data.append(df)

    if all_nes_data and all_cbp_data:
        combined_nes = pd.concat(all_nes_data, ignore_index=True)
        logger.info(f"  NES data for {len(combined_nes)} counties")

        # Merge NES with CBP (need employment from CBP)
        merged = combined_nes[['fips', 'NONEMP']].merge(
            combined_cbp[['fips', 'EMP']],
            on='fips',
            how='inner'
        )

        # Calculate share
        merged['share_nonemployer'] = (
            merged['NONEMP'] / (merged['NONEMP'] + merged['EMP']) * 100
        ).round(2)

        logger.info(f"  Calculated share for {len(merged)} counties")

        # Aggregate to regions
        regional = aggregator.aggregate_to_regions(
            county_data=merged,
            measure_type='intensive',
            value_column='share_nonemployer',
            fips_column='fips',
            weight_column='EMP'  # Weight by employment
        )
        measures['share_nonemployer'] = aggregator.add_region_metadata(regional)
        logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate share of nonemployer workers")

    # ===========================================================================
    # MEASURE 2.5: INDUSTRY DIVERSITY
    # ===========================================================================

    logger.info(f"\n4/4: Industry Diversity Index ({year_cbp})")

    # Collect CBP data by 2-digit NAICS
    logger.info("  Collecting employment by industry (2-digit NAICS)...")
    all_industry_data = []

    for state_abbr, state_fips in STATES.items():
        # Get data for each 2-digit NAICS sector
        naics_2digit = ['11', '21', '22', '23', '31-33', '42', '44-45', '48-49',
                        '51', '52', '53', '54', '55', '56', '61', '62', '71', '72', '81', '99']

        for naics in naics_2digit:
            df = collect_cbp_data(year_cbp, state_fips, api_key, logger,
                                naics_code=naics, variables='EMP,NAICS2017')
            if not df.empty:
                df['state_abbr'] = state_abbr
                all_industry_data.append(df)

    if all_industry_data:
        combined_industry = pd.concat(all_industry_data, ignore_index=True)
        logger.info(f"  Collected industry data: {len(combined_industry)} rows")

        # Calculate diversity index
        diversity_df = calculate_industry_diversity_index(combined_industry, logger)

        if not diversity_df.empty:
            # Aggregate to regions
            regional = aggregator.aggregate_to_regions(
                county_data=diversity_df,
                measure_type='intensive',
                value_column='industry_diversity_index',
                fips_column='fips',
                weight_column='total_employment'
            )
            measures['industry_diversity_index'] = aggregator.add_region_metadata(regional)
            logger.info(f"  Aggregated to {len(regional)} regions")
    else:
        logger.warning("  Could not calculate industry diversity")

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
    print(f"Years: BEA {year_current}, CBP {year_cbp}, NES {year_nes}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if m is not None and not m.empty])}/4")
    print()
    print("Economic Opportunity & Diversity Measures (BEA/CBP/NES):")
    print(f"  2.2 Non-Farm Proprietors Per 1,000: {'✓' if 'proprietors_per_1000' in measures else '✗'}")
    print(f"  2.3 Employer Establishments Per 1,000: {'✓' if 'establishments_per_1000' in measures else '✗'}")
    print(f"  2.4 Share of Workers in Non-Employer: {'✓' if 'share_nonemployer' in measures else '✗'}")
    print(f"  2.5 Industry Diversity Index: {'✓' if 'industry_diversity_index' in measures else '✗'}")
    print()
    print("Note: Measures 2.6 (Occupation Diversity) and 2.7 (Share of Telecommuters)")
    print("      are collected separately from ACS data.")
    print("      Measure 2.1 (Entrepreneurial Activity) requires BDS bulk download.")
    print("=" * 80)


if __name__ == '__main__':
    main()
