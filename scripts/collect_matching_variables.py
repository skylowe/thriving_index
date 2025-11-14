"""
Collect Matching Variables for Peer Region Identification

This script collects the 6 matching variables used in the Nebraska Thriving Index
for identifying peer regions:

1. Total population
2. % in micropolitan area
3. % farm income
4. % manufacturing employment
5. Distance to small MSA (< 250k population)
6. Distance to large MSA (> 250k population)

These variables are used for Mahalanobis distance calculation to find
the 10 most similar peer regions for each Virginia region.
"""

import sys
from pathlib import Path
import json
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.api_clients.bea_api import BEAAPI
from src.data_processing.aggregate_data import DataAggregator
from src.utils.fips_to_region import get_region_for_fips, get_all_fips_in_region
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def collect_population_data(census: CensusAPI, agg: DataAggregator, logger) -> Dict[str, float]:
    """
    Collect total population for all regions.

    Returns:
        Dict mapping region code to total population
    """
    logger.info("=" * 70)
    logger.info("Collecting Variable 1: Total Population")
    logger.info("=" * 70)

    all_population = {}

    # Get state FIPS codes
    state_fips = census.get_state_fips_codes()

    for state_abbr, fips in state_fips.items():
        logger.info(f"Fetching population data for {state_abbr}...")

        try:
            # Get county-level population
            pop_data = census.get_population(year=2022, state=fips)

            # Convert to dict with FIPS as key
            county_pop = {}
            for record in pop_data:
                state_fips_code = record.get('state')
                county_fips_code = record.get('county')

                if state_fips_code and county_fips_code:
                    full_fips = state_fips_code + county_fips_code
                    pop = record.get('B01001_001E')

                    if pop and pop != 'N/A':
                        county_pop[full_fips] = int(pop)

            # Aggregate to regional level
            regional_pop = agg.aggregate_extensive_measure(county_pop)
            all_population.update(regional_pop)

            logger.info(f"  ✓ Collected data for {len(regional_pop)} {state_abbr} regions")

        except Exception as e:
            logger.error(f"  ✗ Failed to collect {state_abbr} population: {e}")

    logger.info(f"\nTotal regions with population data: {len(all_population)}")

    # Summary statistics
    summary = agg.get_regional_summary(all_population)
    logger.info(f"Population range: {summary['min']:,} to {summary['max']:,}")
    logger.info(f"Mean: {summary['mean']:,.0f}, Median: {summary['median']:,.0f}")

    return all_population


def collect_cbsa_classifications(census: CensusAPI, logger) -> Dict[str, str]:
    """
    Collect CBSA (Core-Based Statistical Area) classifications.

    Classifies each county as:
    - 'metropolitan' (urban area 50,000+)
    - 'micropolitan' (urban area 10,000-50,000)
    - 'rural' (neither)

    Returns:
        Dict mapping FIPS code to classification
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Variable 2: Micropolitan Area Classification")
    logger.info("=" * 70)

    # For now, use a simplified approach based on population
    # TODO: Implement proper CBSA classification using Census API or manual mapping

    logger.info("Note: CBSA classification requires additional data sources")
    logger.info("      Will implement using Census CBSA definitions or Tiger shapefiles")

    return {}


def collect_farm_income(bea: BEAAPI, agg: DataAggregator, logger) -> Dict[str, float]:
    """
    Collect % farm income (farm proprietors income / total personal income).

    Returns:
        Dict mapping region code to % farm income
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Variable 3: % Farm Income")
    logger.info("=" * 70)

    # TODO: Implement BEA farm income collection
    logger.info("Farm income data requires BEA Regional Income API")
    logger.info("  - Table: CA05N (Personal Income by Major Component)")
    logger.info("  - Line codes: Farm proprietors income, Total personal income")

    return {}


def collect_manufacturing_employment(bea: BEAAPI, agg: DataAggregator, logger) -> Dict[str, float]:
    """
    Collect % manufacturing employment.

    Returns:
        Dict mapping region code to % manufacturing employment
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Variable 4: % Manufacturing Employment")
    logger.info("=" * 70)

    # TODO: Implement BEA manufacturing employment collection
    logger.info("Manufacturing employment requires BEA Regional Income API")
    logger.info("  - Table: CA25N (Employment by Industry)")
    logger.info("  - Line codes: Manufacturing, Total employment")

    return {}


def calculate_msa_distances(logger) -> Dict[str, Dict[str, float]]:
    """
    Calculate distances from each region to nearest small and large MSAs.

    Returns:
        Dict mapping region code to {'small_msa_dist': float, 'large_msa_dist': float}
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Variables 5 & 6: Distances to MSAs")
    logger.info("=" * 70)

    # TODO: Implement geographic distance calculation
    logger.info("MSA distance calculation requires:")
    logger.info("  1. List of MSAs with population sizes and coordinates")
    logger.info("  2. Region centroid coordinates")
    logger.info("  3. Haversine distance calculation")

    return {}


def save_matching_variables(data: Dict, output_path: Path, logger):
    """Save matching variables to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    logger.info(f"\n✓ Saved matching variables to: {output_path}")


def main():
    """Main function to collect all matching variables."""
    logger = setup_logger('collect_matching_variables')

    logger.info("=" * 70)
    logger.info("COLLECTING MATCHING VARIABLES FOR PEER REGION IDENTIFICATION")
    logger.info("=" * 70)
    logger.info(f"\nTotal regions to process: {len(ALL_REGIONS)}")
    logger.info(f"States: VA, MD, WV, NC, TN, KY, DC\n")

    # Initialize API clients
    census = CensusAPI()
    bea = BEAAPI()
    agg = DataAggregator()

    # Collect all variables
    matching_vars = {
        'metadata': {
            'collection_date': '2025-11-14',
            'regions': len(ALL_REGIONS),
            'description': 'Matching variables for peer region identification'
        },
        'variables': {}
    }

    # Variable 1: Total population
    try:
        population = collect_population_data(census, agg, logger)
        matching_vars['variables']['population'] = population
    except Exception as e:
        logger.error(f"Failed to collect population: {e}")
        matching_vars['variables']['population'] = {}

    # Variable 2: Micropolitan classification
    try:
        cbsa = collect_cbsa_classifications(census, logger)
        matching_vars['variables']['cbsa_classification'] = cbsa
    except Exception as e:
        logger.error(f"Failed to collect CBSA classification: {e}")
        matching_vars['variables']['cbsa_classification'] = {}

    # Variable 3: Farm income
    try:
        farm_income = collect_farm_income(bea, agg, logger)
        matching_vars['variables']['pct_farm_income'] = farm_income
    except Exception as e:
        logger.error(f"Failed to collect farm income: {e}")
        matching_vars['variables']['pct_farm_income'] = {}

    # Variable 4: Manufacturing employment
    try:
        manufacturing = collect_manufacturing_employment(bea, agg, logger)
        matching_vars['variables']['pct_manufacturing'] = manufacturing
    except Exception as e:
        logger.error(f"Failed to collect manufacturing employment: {e}")
        matching_vars['variables']['pct_manufacturing'] = {}

    # Variables 5 & 6: MSA distances
    try:
        msa_distances = calculate_msa_distances(logger)
        matching_vars['variables']['msa_distances'] = msa_distances
    except Exception as e:
        logger.error(f"Failed to calculate MSA distances: {e}")
        matching_vars['variables']['msa_distances'] = {}

    # Save results
    output_path = project_root / 'data' / 'processed' / 'matching_variables.json'
    save_matching_variables(matching_vars, output_path, logger)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 70)

    for var_name, var_data in matching_vars['variables'].items():
        if isinstance(var_data, dict):
            count = len(var_data)
            coverage = (count / len(ALL_REGIONS) * 100) if ALL_REGIONS else 0
            logger.info(f"{var_name}: {count}/{len(ALL_REGIONS)} regions ({coverage:.1f}%)")

    logger.info("\n" + "=" * 70)
    logger.info("Matching variables collection complete")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
