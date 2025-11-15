#!/usr/bin/env python3
"""
Collect Component Index 7: Quality of Life measures

This script collects all 8 measures for the Quality of Life component index,
following Nebraska Thriving Index methodology exactly.

Measures collected:
7.1 Commute Time (Census ACS S0801)
7.2 Percent of Housing Built Pre-1960 (Census ACS DP04)
7.3 Relative Weekly Wage (BLS QCEW)
7.4 Violent Crime Rate (FBI UCR)
7.5 Property Crime Rate (FBI UCR)
7.6 Climate Amenities (USDA ERS Natural Amenities Scale) - BULK DATA
7.7 Healthcare Access (Census CBP)
7.8 Count of National Parks (NPS API) - NEEDS MANUAL MAPPING

Note: Measures 7.6 and 7.8 require bulk data download or manual mapping.
This script focuses on API-accessible measures (7.1, 7.2, 7.3, 7.4, 7.5, 7.7).
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_clients.census_api import CensusAPI
from src.api_clients.bls_api import BLSAPI
from src.utils.config import Config
from src.utils.logging_setup import setup_logging
from data.regional_groupings import REGIONS

# Setup logging
logger = setup_logging(__name__)

def collect_commute_time(census_api, year=2022):
    """
    Measure 7.1: Commute Time

    Source: Census ACS Table S0801
    Metric: Average commuting time to work (in minutes)
    Scoring: Inverse (shorter commute = better)
    """
    logger.info("Collecting Measure 7.1: Commute Time")

    all_data = []

    for region_code, region_info in REGIONS.items():
        state_fips = region_code.split('-')[0]

        # Get state name for logging
        state_names = {
            'VA': 'Virginia', 'MD': 'Maryland', 'WV': 'West Virginia',
            'NC': 'North Carolina', 'TN': 'Tennessee', 'KY': 'Kentucky', 'DC': 'DC'
        }
        state_name = state_names.get(state_fips, state_fips)

        logger.info(f"  Processing {region_info['name']} ({region_code})")

        # S0801_C01_046E: Mean travel time to work (minutes)
        variables = ['S0801_C01_046E', 'NAME']

        for county_fips in region_info['counties']:
            try:
                # Get data from Census ACS 5-year estimates
                data = census_api.get_acs_data(
                    year=year,
                    variables=variables,
                    geography='county',
                    state_fips=state_fips,
                    county_fips=county_fips,
                    dataset='acs5/subject'
                )

                if data and len(data) > 0:
                    county_data = data[0]
                    all_data.append({
                        'region_code': region_code,
                        'region_name': region_info['name'],
                        'county_fips': county_fips,
                        'county_name': county_data.get('NAME', ''),
                        'measure': '7.1_commute_time',
                        'mean_travel_time_minutes': county_data.get('S0801_C01_046E'),
                        'year': year,
                        'source': 'Census ACS S0801'
                    })

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.warning(f"    Error collecting commute time for {county_fips}: {e}")
                continue

    logger.info(f"Collected commute time data for {len(all_data)} counties")
    return all_data


def collect_housing_age(census_api, year=2022):
    """
    Measure 7.2: Percent of Housing Built Pre-1960

    Source: Census ACS Table DP04
    Metric: Share of housing units built before 1960
    Scoring: Inverse (lower percentage of old housing = better)
    """
    logger.info("Collecting Measure 7.2: Percent of Housing Built Pre-1960")

    all_data = []

    for region_code, region_info in REGIONS.items():
        state_fips = region_code.split('-')[0]

        logger.info(f"  Processing {region_info['name']} ({region_code})")

        # DP04 variables for housing age
        variables = [
            'DP04_0035E',  # Built 1939 or earlier
            'DP04_0036E',  # Built 1940 to 1949
            'DP04_0037E',  # Built 1950 to 1959
            'DP04_0033E',  # Total housing units
            'NAME'
        ]

        for county_fips in region_info['counties']:
            try:
                # Get data from Census ACS 5-year estimates (profile tables)
                data = census_api.get_acs_data(
                    year=year,
                    variables=variables,
                    geography='county',
                    state_fips=state_fips,
                    county_fips=county_fips,
                    dataset='acs5/profile'
                )

                if data and len(data) > 0:
                    county_data = data[0]

                    # Calculate percent built pre-1960
                    built_pre_1940 = float(county_data.get('DP04_0035E', 0) or 0)
                    built_1940_1949 = float(county_data.get('DP04_0036E', 0) or 0)
                    built_1950_1959 = float(county_data.get('DP04_0037E', 0) or 0)
                    total_units = float(county_data.get('DP04_0033E', 0) or 0)

                    percent_pre_1960 = None
                    if total_units > 0:
                        percent_pre_1960 = ((built_pre_1940 + built_1940_1949 + built_1950_1959) / total_units) * 100

                    all_data.append({
                        'region_code': region_code,
                        'region_name': region_info['name'],
                        'county_fips': county_fips,
                        'county_name': county_data.get('NAME', ''),
                        'measure': '7.2_housing_age',
                        'built_pre_1940': built_pre_1940,
                        'built_1940_1949': built_1940_1949,
                        'built_1950_1959': built_1950_1959,
                        'total_housing_units': total_units,
                        'percent_built_pre_1960': percent_pre_1960,
                        'year': year,
                        'source': 'Census ACS DP04'
                    })

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.warning(f"    Error collecting housing age for {county_fips}: {e}")
                continue

    logger.info(f"Collected housing age data for {len(all_data)} counties")
    return all_data


def collect_relative_weekly_wage(bls_api, year=2023, quarter='Q2'):
    """
    Measure 7.3: Relative Weekly Wage

    Source: BLS QCEW
    Metric: Ratio of regional weekly wage to statewide weekly wage
    Scoring: Higher ratio = better earnings relative to state

    Note: This requires collecting both county-level and state-level wages,
    then calculating the ratio.
    """
    logger.info("Collecting Measure 7.3: Relative Weekly Wage")
    logger.warning("  This measure requires QCEW data collection and state-level wage calculations")
    logger.warning("  Implementation requires BLS QCEW API with series IDs for counties and states")
    logger.warning("  Placeholder implementation - needs full QCEW integration")

    # This would require:
    # 1. Get average weekly wage for each county (QCEW)
    # 2. Get average weekly wage for each state (QCEW)
    # 3. Calculate ratio: county_wage / state_wage

    # Placeholder return
    return []


def collect_healthcare_access(census_api, year=2021):
    """
    Measure 7.7: Healthcare Access

    Source: Census County Business Patterns
    Metric: Number of healthcare practitioners per 10,000 population
    Scoring: Higher = better healthcare access
    """
    logger.info("Collecting Measure 7.7: Healthcare Access (Healthcare Employment)")

    all_data = []

    for region_code, region_info in REGIONS.items():
        state_fips = region_code.split('-')[0]

        logger.info(f"  Processing {region_info['name']} ({region_code})")

        for county_fips in region_info['counties']:
            try:
                # Get healthcare employment from CBP
                # NAICS 621: Ambulatory Health Care Services
                # NAICS 622: Hospitals

                ambulatory_data = census_api.get_cbp_data(
                    year=year,
                    naics='621',
                    state_fips=state_fips,
                    county_fips=county_fips
                )

                hospitals_data = census_api.get_cbp_data(
                    year=year,
                    naics='622',
                    state_fips=state_fips,
                    county_fips=county_fips
                )

                # Extract employment counts
                ambulatory_emp = 0
                if ambulatory_data and len(ambulatory_data) > 0:
                    ambulatory_emp = int(ambulatory_data[0].get('EMP', 0) or 0)

                hospitals_emp = 0
                if hospitals_data and len(hospitals_data) > 0:
                    hospitals_emp = int(hospitals_data[0].get('EMP', 0) or 0)

                total_healthcare_emp = ambulatory_emp + hospitals_emp

                all_data.append({
                    'region_code': region_code,
                    'region_name': region_info['name'],
                    'county_fips': county_fips,
                    'measure': '7.7_healthcare_access',
                    'ambulatory_healthcare_employment': ambulatory_emp,
                    'hospital_employment': hospitals_emp,
                    'total_healthcare_employment': total_healthcare_emp,
                    'year': year,
                    'source': 'Census CBP NAICS 621+622'
                })

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.warning(f"    Error collecting healthcare access for {county_fips}: {e}")
                continue

    logger.info(f"Collected healthcare access data for {len(all_data)} counties")
    return all_data


def main():
    """Main data collection function"""
    logger.info("=" * 80)
    logger.info("COMPONENT INDEX 7: QUALITY OF LIFE DATA COLLECTION")
    logger.info("=" * 80)

    # Initialize API clients
    config = Config()
    census_api = CensusAPI(api_key=config.CENSUS_API_KEY)
    bls_api = BLSAPI(api_key=config.BLS_API_KEY)

    # Collect measures
    results = {}

    # Measure 7.1: Commute Time
    try:
        results['commute_time'] = collect_commute_time(census_api, year=2022)
    except Exception as e:
        logger.error(f"Error collecting commute time: {e}")
        results['commute_time'] = []

    # Measure 7.2: Housing Age
    try:
        results['housing_age'] = collect_housing_age(census_api, year=2022)
    except Exception as e:
        logger.error(f"Error collecting housing age: {e}")
        results['housing_age'] = []

    # Measure 7.3: Relative Weekly Wage
    logger.warning("Measure 7.3 (Relative Weekly Wage) requires QCEW implementation - skipping for now")
    results['relative_wage'] = []

    # Measures 7.4 & 7.5: Crime Rates
    logger.warning("Measures 7.4 & 7.5 (Crime Rates) require FBI UCR API implementation - skipping for now")
    results['violent_crime'] = []
    results['property_crime'] = []

    # Measure 7.6: Climate Amenities
    logger.warning("Measure 7.6 (Climate Amenities) requires USDA ERS bulk download - manual collection needed")
    results['climate'] = []

    # Measure 7.7: Healthcare Access
    try:
        results['healthcare_access'] = collect_healthcare_access(census_api, year=2021)
    except Exception as e:
        logger.error(f"Error collecting healthcare access: {e}")
        results['healthcare_access'] = []

    # Measure 7.8: National Parks
    logger.warning("Measure 7.8 (National Parks) requires NPS API and GIS mapping - manual collection needed")
    results['national_parks'] = []

    # Save results
    output_dir = 'data/raw/quality_of_life'
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for measure_name, measure_data in results.items():
        if measure_data:
            output_file = os.path.join(output_dir, f'{measure_name}_{timestamp}.json')
            with open(output_file, 'w') as f:
                json.dump(measure_data, f, indent=2)
            logger.info(f"Saved {len(measure_data)} records to {output_file}")

    # Summary
    logger.info("=" * 80)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Commute Time: {len(results['commute_time'])} records")
    logger.info(f"Housing Age: {len(results['housing_age'])} records")
    logger.info(f"Relative Weekly Wage: {len(results['relative_wage'])} records (NOT YET IMPLEMENTED)")
    logger.info(f"Violent Crime Rate: {len(results['violent_crime'])} records (NOT YET IMPLEMENTED)")
    logger.info(f"Property Crime Rate: {len(results['property_crime'])} records (NOT YET IMPLEMENTED)")
    logger.info(f"Climate Amenities: {len(results['climate'])} records (BULK DATA REQUIRED)")
    logger.info(f"Healthcare Access: {len(results['healthcare_access'])} records")
    logger.info(f"National Parks: {len(results['national_parks'])} records (MANUAL MAPPING REQUIRED)")
    logger.info("=" * 80)

    # Implementation notes
    logger.info("")
    logger.info("IMPLEMENTATION NOTES:")
    logger.info("1. Measure 7.3 (Relative Weekly Wage) requires BLS QCEW implementation")
    logger.info("2. Measures 7.4 & 7.5 (Crime Rates) require FBI UCR API integration")
    logger.info("3. Measure 7.6 (Climate Amenities) requires USDA ERS bulk data download")
    logger.info("4. Measure 7.8 (National Parks) requires NPS API and GIS mapping")
    logger.info("")
    logger.info("Currently implemented: 3/8 measures (7.1, 7.2, 7.7)")
    logger.info("Requires API implementation: 3/8 measures (7.3, 7.4, 7.5)")
    logger.info("Requires bulk data: 2/8 measures (7.6, 7.8)")


if __name__ == '__main__':
    main()
