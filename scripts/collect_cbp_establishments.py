#!/usr/bin/env python3
"""
Collect Census County Business Patterns (CBP) data for establishment counts.

Collects establishments by NAICS industry code for:
- Recreation (NAICS 71)
- Restaurants/Food Services (NAICS 722)
- Arts & Entertainment (NAICS 711, 712)
- Social Associations (NAICS 813)
- All industries (for HHI economic diversity calculation)
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import requests

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.processing.regional_aggregator import RegionalAggregator
from src.utils.config import APIConfig
from src.utils.logging_setup import setup_logger

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


def main():
    """Collect CBP establishment data."""
    
    logger = setup_logger('cbp_collection')
    aggregator = RegionalAggregator()
    
    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    api_key = APIConfig.CENSUS_API_KEY
    base_url = "https://api.census.gov/data"
    
    # Use most recent available CBP year (2021 is latest as of 2024)
    year = 2021
    
    logger.info("=" * 80)
    logger.info("CENSUS COUNTY BUSINESS PATTERNS COLLECTION")
    logger.info(f"Year: {year}")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    measures = {}
    
    # Industry codes to collect
    industries = {
        'recreation': '71',  # Arts, Entertainment, Recreation
        'restaurants': '722',  # Food Services & Drinking Places
        'arts_performing': '711',  # Performing Arts
        'arts_museums': '712',  # Museums, Historical Sites
        'social_assoc': '813',  # Religious, Grantmaking, Civic, Professional Orgs
    }
    
    # Collect each industry
    for measure_name, naics in industries.items():
        logger.info(f"\nCollecting: {measure_name} (NAICS {naics})")
        
        all_data = []
        
        for state_abbr, state_fips in STATES.items():
            try:
                url = f"{base_url}/{year}/cbp"
                params = {
                    'get': 'NAME,NAICS2017,ESTAB,EMP',
                    'for': 'county:*',
                    'in': f'state:{state_fips}',
                    'NAICS2017': naics,
                    'key': api_key
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if len(data) > 1:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    
                    # Build FIPS
                    if 'county' in df.columns and 'state' in df.columns:
                        df['fips'] = df['state'] + df['county']
                    elif state_fips == '11':
                        df['fips'] = '11001'
                    
                    # Convert establishments to numeric
                    df[f'{measure_name}_establishments'] = pd.to_numeric(df['ESTAB'], errors='coerce')
                    
                    all_data.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} counties")
                    
            except Exception as e:
                logger.error(f"  Error {state_abbr}: {str(e)}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            
            # Aggregate to regions
            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',
                value_column=f'{measure_name}_establishments',
                fips_column='fips',
                weight_column=None
            )
            
            regional = aggregator.add_region_metadata(regional)
            
            # Get population to calculate per capita
            try:
                pop_file = output_dir / 'population_2022_regional.csv'
                if pop_file.exists():
                    pop_df = pd.read_csv(pop_file)
                    regional = regional.merge(
                        pop_df[['region_code', 'population']],
                        on='region_code',
                        how='left'
                    )
                    # Calculate per 10,000 population
                    regional[f'{measure_name}_per_10k'] = (
                        regional[f'{measure_name}_establishments'] / regional['population'] * 10000
                    ).round(2)
                    regional = regional.drop(columns=['population'])
            except Exception as e:
                logger.warning(f"Could not calculate per capita: {str(e)}")
            
            measures[measure_name] = regional
            logger.info(f"  Collected {len(regional)} regions")
    
    end_time = datetime.now()
    
    # Save all
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)
    
    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_establishments_{year}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Year: {year}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures: {len([m for m in measures.values() if m is not None and not m.empty])}/{len(industries)}")
    print("=" * 80)


if __name__ == '__main__':
    main()
