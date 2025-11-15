#!/usr/bin/env python3
"""
Collect BEA (Bureau of Economic Analysis) data for economic measures.

Collects:
- Per capita personal income (level)
- Farm proprietors income
- Nonfarm proprietors income  
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


def main():
    """Main execution."""
    
    logger = setup_logger('bea_collection')
    bea = BEAAPI()
    aggregator = RegionalAggregator()
    
    output_dir = project_root / 'data' / 'regional_data'
    output_dir.mkdir(parents=True, exist_ok=True)
    year = 2022
    
    logger.info("=" * 80)
    logger.info("BEA ECONOMIC DATA COLLECTION")
    logger.info(f"Year: {year}")
    logger.info("=" * 80)
    
    measures = {}
    start_time = datetime.now()
    
    # 1. Per capita personal income
    logger.info("\n1/3: Per Capita Personal Income")
    try:
        all_data = []
        for state_abbr, state_fips in STATES.items():
            try:
                data = bea.get_personal_income_per_capita(year=year, state=state_fips)
                if data:
                    df = pd.DataFrame(data)
                    if 'GeoFips' in df.columns:
                        df['fips'] = df['GeoFips']
                    value_col = [c for c in df.columns if c not in ['GeoFips', 'GeoName', 'fips', 'TimePeriod', 'Year']][0]
                    df['per_capita_personal_income'] = pd.to_numeric(df[value_col], errors='coerce')
                    all_data.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} records")
            except Exception as e:
                logger.error(f"  Error {state_abbr}: {str(e)}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='intensive',
                value_column='per_capita_personal_income',
                fips_column='fips',
                weight_column=None
            )
            regional = aggregator.add_region_metadata(regional)
            measures['per_capita_personal_income'] = regional
            logger.info(f"  Collected {len(regional)} regions")
    except Exception as e:
        logger.error(f"Per capita income error: {str(e)}")
    
    # 2. Farm proprietors income
    logger.info("\n2/3: Farm Proprietors Income")
    try:
        all_data = []
        for state_abbr, state_fips in STATES.items():
            try:
                data = bea.get_farm_proprietors_income(year=year, state=state_fips)
                if data:
                    df = pd.DataFrame(data)
                    if 'GeoFips' in df.columns:
                        df['fips'] = df['GeoFips']
                    value_col = [c for c in df.columns if c not in ['GeoFips', 'GeoName', 'fips', 'TimePeriod', 'Year']][0]
                    df['farm_proprietors_income'] = pd.to_numeric(df[value_col], errors='coerce')
                    all_data.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} records")
            except Exception as e:
                logger.error(f"  Error {state_abbr}: {str(e)}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',
                value_column='farm_proprietors_income',
                fips_column='fips',
                weight_column=None
            )
            regional = aggregator.add_region_metadata(regional)
            measures['farm_proprietors_income'] = regional
            logger.info(f"  Collected {len(regional)} regions")
    except Exception as e:
        logger.error(f"Farm income error: {str(e)}")
    
    # 3. Nonfarm proprietors income
    logger.info("\n3/3: Nonfarm Proprietors Income")
    try:
        all_data = []
        for state_abbr, state_fips in STATES.items():
            try:
                data = bea.get_nonfarm_proprietors_income(year=year, state=state_fips)
                if data:
                    df = pd.DataFrame(data)
                    if 'GeoFips' in df.columns:
                        df['fips'] = df['GeoFips']
                    value_col = [c for c in df.columns if c not in ['GeoFips', 'GeoName', 'fips', 'TimePeriod', 'Year']][0]
                    df['nonfarm_proprietors_income'] = pd.to_numeric(df[value_col], errors='coerce')
                    all_data.append(df)
                    logger.debug(f"  {state_abbr}: {len(df)} records")
            except Exception as e:
                logger.error(f"  Error {state_abbr}: {str(e)}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            regional = aggregator.aggregate_to_regions(
                county_data=combined,
                measure_type='extensive',
                value_column='nonfarm_proprietors_income',
                fips_column='fips',
                weight_column=None
            )
            regional = aggregator.add_region_metadata(regional)
            measures['nonfarm_proprietors_income'] = regional
            logger.info(f"  Collected {len(regional)} regions")
    except Exception as e:
        logger.error(f"Nonfarm income error: {str(e)}")
    
    end_time = datetime.now()
    
    # Save all
    logger.info("\n" + "=" * 80)
    logger.info("SAVING DATA")
    logger.info("=" * 80)
    
    for name, df in measures.items():
        if df is not None and not df.empty:
            filepath = output_dir / f"{name}_{year}_regional.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Year: {year}")
    print(f"Time: {end_time - start_time}")
    print(f"Measures: {len([m for m in measures.values() if m is not None and not m.empty])}/3")
    print("=" * 80)


if __name__ == '__main__':
    main()
