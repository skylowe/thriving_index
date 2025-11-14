"""
Aggregate Micropolitan Data for Matching Variable 2

Calculates the percentage of each region's population living in micropolitan
statistical areas using Census CBSA codes and population data.

Variable 2: % in Micropolitan Area
- Micropolitan = urban cluster of 10,000-49,999 population
- Source: Census Bureau CBSA definitions + ACS population
"""

import sys
from pathlib import Path
import json
from typing import Dict
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.utils.fips_to_region import get_region_for_fips
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def get_cbsa_codes_and_populations(census: CensusAPI, logger):
    """
    Get CBSA codes and populations for all counties.

    Returns:
        Dict mapping FIPS to {population, cbsa_code, metro_micro}
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting CBSA Codes and County Populations")
    logger.info("=" * 70)

    state_fips_codes = {
        'VA': '51', 'MD': '24', 'WV': '54',
        'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'
    }

    county_data = {}

    for state_abbr, state_fips in state_fips_codes.items():
        logger.info(f"\nProcessing {state_abbr}...")

        try:
            # Get population using Census API method
            # Note: CBSA codes are not directly available from ACS API
            # We'll use our existing CBSA_CLASSIFICATIONS file
            response = census.get_population(year=2022, state=state_fips)

            if response and len(response) > 0:
                # Parse response - get_population() returns list of dicts
                for row in response:
                    name = row.get('NAME', '')
                    population = row.get('B01001_001E', 0)  # Fixed: was B01003_001E
                    state = row.get('state', '')
                    county = row.get('county', '')

                    if state and county:
                        fips = f"{state}{county}"

                        try:
                            pop = int(population)
                            county_data[fips] = {
                                'population': pop,
                                'name': name,
                                'cbsa': None,  # Will be filled from separate source
                                'metro_micro': 'rural'  # Default to rural
                            }
                        except (ValueError, TypeError):
                            logger.warning(f"  Could not parse population for {name}: {population}")

                logger.info(f"  Collected data for {len([k for k in county_data.keys() if k.startswith(state_fips)])} counties")

        except Exception as e:
            logger.error(f"  Failed for {state_abbr}: {e}")
            import traceback
            traceback.print_exc()

    logger.info(f"\n✓ Collected data for {len(county_data)} counties total")

    # Load CBSA classifications from our existing file
    # Note: This is incomplete, but we can use what we have and mark the rest as rural
    from data.cbsa_classifications import CBSA_CLASSIFICATIONS

    for fips, cbsa_data in CBSA_CLASSIFICATIONS.items():
        if fips in county_data:
            county_data[fips]['cbsa'] = cbsa_data.get('cbsa_name')
            county_data[fips]['metro_micro'] = cbsa_data.get('cbsa', 'rural')

    # Count classifications
    metro_count = sum(1 for d in county_data.values() if d['metro_micro'] == 'metro')
    micro_count = sum(1 for d in county_data.values() if d['metro_micro'] == 'micro')
    rural_count = sum(1 for d in county_data.values() if d['metro_micro'] == 'rural')

    logger.info(f"\nClassifications:")
    logger.info(f"  Metropolitan: {metro_count} counties")
    logger.info(f"  Micropolitan: {micro_count} counties")
    logger.info(f"  Rural: {rural_count} counties")
    logger.info(f"  Unknown (defaulted to rural): {rural_count}")

    return county_data


def calculate_regional_micropolitan_pct(county_data: Dict, logger):
    """
    Calculate population-weighted micropolitan percentage for each region.

    Args:
        county_data: Dict mapping FIPS to population and CBSA data

    Returns:
        Dict mapping region code to % micropolitan
    """
    logger.info("\n" + "=" * 70)
    logger.info("Calculating Regional Micropolitan Percentages")
    logger.info("=" * 70)

    regional_data = defaultdict(lambda: {'total_pop': 0, 'micro_pop': 0})

    for fips, data in county_data.items():
        region = get_region_for_fips(fips)

        if region:
            pop = data['population']
            regional_data[region]['total_pop'] += pop

            if data['metro_micro'] == 'micro':
                regional_data[region]['micro_pop'] += pop

    # Calculate percentages
    micropolitan_pct = {}

    for region, data in regional_data.items():
        if data['total_pop'] > 0:
            pct = (data['micro_pop'] / data['total_pop']) * 100
            micropolitan_pct[region] = round(pct, 2)

            logger.info(f"  {region}: {pct:.2f}% micropolitan ({data['micro_pop']:,} / {data['total_pop']:,})")

    logger.info(f"\n✓ Calculated micropolitan % for {len(micropolitan_pct)} regions")

    return micropolitan_pct


def main():
    """Main execution."""
    logger = setup_logger('aggregate_micropolitan_data')

    logger.info("=" * 70)
    logger.info("AGGREGATING MICROPOLITAN DATA (Variable 2)")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions across 7 states\n")

    # Initialize Census API client
    census = CensusAPI()

    # Get CBSA codes and populations
    county_data = get_cbsa_codes_and_populations(census, logger)

    # Calculate regional percentages
    micropolitan_pct = calculate_regional_micropolitan_pct(county_data, logger)

    # Load existing matching variables
    matching_vars_file = project_root / 'data' / 'processed' / 'matching_variables.json'

    if matching_vars_file.exists():
        with open(matching_vars_file) as f:
            matching_vars = json.load(f)
    else:
        matching_vars = {
            'metadata': {
                'collection_date': '2025-11-14',
                'regions': len(ALL_REGIONS),
                'description': 'Matching variables for peer region identification'
            },
            'variables': {}
        }

    # Update with micropolitan data
    matching_vars['variables']['pct_micropolitan'] = micropolitan_pct

    # Save results
    with open(matching_vars_file, 'w') as f:
        json.dump(matching_vars, f, indent=2)

    logger.info(f"\n✓ Saved updated matching variables to: {matching_vars_file}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("AGGREGATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Micropolitan data: {len(micropolitan_pct)}/{len(ALL_REGIONS)} regions ({len(micropolitan_pct)/len(ALL_REGIONS)*100:.1f}%)")

    if micropolitan_pct:
        values = list(micropolitan_pct.values())
        logger.info(f"\nMicropolitan % statistics:")
        logger.info(f"  Min: {min(values):.2f}%")
        logger.info(f"  Max: {max(values):.2f}%")
        logger.info(f"  Mean: {sum(values)/len(values):.2f}%")

        # Count regions with 0% (no micropolitan areas)
        zero_count = sum(1 for v in values if v == 0)
        logger.info(f"  Regions with 0% micropolitan: {zero_count}")

    logger.info("\nNOTE: Current CBSA classifications are incomplete.")
    logger.info("Counties without explicit CBSA data are classified as 'rural'.")
    logger.info("This means micropolitan percentages may be underestimated.")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
