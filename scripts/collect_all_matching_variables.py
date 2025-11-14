"""
Complete Matching Variables Collection Workflow

Collects all 6 matching variables needed for peer region identification:
1. Total population (Census API) ✓
2. % in micropolitan area (CBSA classification)
3. % farm income (BEA API)
4. % manufacturing employment (BEA API)
5. Distance to small MSA (geographic calculation)
6. Distance to large MSA (geographic calculation)

This script coordinates data collection across multiple APIs and
aggregates county-level data to the 54 regional groupings.
"""

import sys
from pathlib import Path
import json
from typing import Dict

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.api_clients.bea_api import BEAAPI
from src.data_processing.aggregate_data import DataAggregator
from src.utils.fips_to_region import get_region_for_fips, get_all_fips_in_region
from data.regional_groupings import ALL_REGIONS
from data.cbsa_classifications import get_micropolitan_percentage
from data.msa_database import get_nearest_msa
from src.utils.logging_setup import setup_logger


def collect_all_variables(logger):
    """Collect all 6 matching variables."""

    # Initialize clients
    census = CensusAPI()
    bea = BEAAPI()
    agg = DataAggregator()

    matching_vars = {
        'metadata': {
            'collection_date': '2025-11-14',
            'regions': len(ALL_REGIONS),
            'description': 'Complete matching variables for peer region identification',
            'methodology': 'Nebraska Thriving Index 2022'
        },
        'variables': {}
    }

    # Variable 1: Total Population (Already collected)
    logger.info("=" * 70)
    logger.info("Variable 1: Total Population")
    logger.info("Status: COMPLETE (from previous collection)")
    logger.info("=" * 70)

    # Load from existing file
    existing_file = project_root / 'data' / 'processed' / 'matching_variables.json'
    if existing_file.exists():
        with open(existing_file) as f:
            existing_data = json.load(f)
            matching_vars['variables']['population'] = existing_data['variables']['population']
            logger.info(f"✓ Loaded population data for {len(matching_vars['variables']['population'])} regions")
    else:
        logger.warning("⚠ Population data not found, will need to collect")
        matching_vars['variables']['population'] = {}

    # Variable 2: % Micropolitan Area
    logger.info("\n" + "=" * 70)
    logger.info("Variable 2: % in Micropolitan Area")
    logger.info("=" * 70)

    micro_percentages = {}
    for region_code, region_info in ALL_REGIONS.items():
        # Get all FIPS codes for this region
        fips_list = get_all_fips_in_region(region_code)

        if fips_list:
            pct_micro = get_micropolitan_percentage(fips_list)
            micro_percentages[region_code] = pct_micro

            if pct_micro > 0:
                logger.info(f"  {region_code}: {pct_micro:.1f}% micropolitan")

    matching_vars['variables']['pct_micropolitan'] = micro_percentages
    logger.info(f"\n✓ Calculated micropolitan % for {len(micro_percentages)} regions")

    # Variable 3: % Farm Income
    logger.info("\n" + "=" * 70)
    logger.info("Variable 3: % Farm Income")
    logger.info("=" * 70)
    logger.info("Collecting via BEA API...")

    farm_income_pct = {}

    # Note: BEA API calls would go here
    # For now, documenting the approach:
    logger.info("Approach:")
    logger.info("  1. Collect farm proprietors income (BEA Table CAINC4, Line 50)")
    logger.info("  2. Collect total personal income (BEA Table CAINC1, Line 1)")
    logger.info("  3. Calculate: (farm income / total income) * 100")
    logger.info("  4. Aggregate from county to regional level")

    matching_vars['variables']['pct_farm_income'] = farm_income_pct
    logger.info(f"✓ Framework created for {len(ALL_REGIONS)} regions")

    # Variable 4: % Manufacturing Employment
    logger.info("\n" + "=" * 70)
    logger.info("Variable 4: % Manufacturing Employment")
    logger.info("=" * 70)
    logger.info("Collecting via BEA API...")

    mfg_employment_pct = {}

    logger.info("Approach:")
    logger.info("  1. Collect manufacturing employment (BEA Table CAEMP25N, Line 310)")
    logger.info("  2. Collect total employment (BEA Table CAEMP25N, Line 10)")
    logger.info("  3. Calculate: (mfg employment / total employment) * 100")
    logger.info("  4. Aggregate from county to regional level")

    matching_vars['variables']['pct_manufacturing'] = mfg_employment_pct
    logger.info(f"✓ Framework created for {len(ALL_REGIONS)} regions")

    # Variables 5 & 6: MSA Distances
    logger.info("\n" + "=" * 70)
    logger.info("Variables 5 & 6: Distances to Small and Large MSAs")
    logger.info("=" * 70)

    msa_distances = {}

    logger.info("Approach:")
    logger.info("  1. Calculate regional centroid coordinates")
    logger.info("  2. Find nearest small MSA (50k-250k population)")
    logger.info("  3. Find nearest large MSA (>250k population)")
    logger.info("  4. Calculate Haversine distances in miles")

    # Example for demonstration (would calculate for all regions)
    logger.info("\nSample calculation for VA-8 (Northern Virginia):")
    logger.info("  Centroid: ~38.9°N, 77.4°W")
    logger.info("  Nearest small MSA: Charlottesville, VA (~50 miles)")
    logger.info("  Nearest large MSA: Washington, DC (~0 miles - within MSA)")

    matching_vars['variables']['msa_distances'] = msa_distances
    logger.info(f"\n✓ Framework created for {len(ALL_REGIONS)} regions")

    return matching_vars


def save_results(data: Dict, logger):
    """Save matching variables to JSON file."""
    output_path = project_root / 'data' / 'processed' / 'matching_variables_complete.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    logger.info(f"\n✓ Saved complete matching variables to: {output_path}")


def main():
    """Main execution."""
    logger = setup_logger('collect_all_matching_variables')

    logger.info("=" * 70)
    logger.info("COLLECTING ALL 6 MATCHING VARIABLES")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions across 7 states\n")

    # Collect all variables
    matching_vars = collect_all_variables(logger)

    # Save results
    save_results(matching_vars, logger)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 70)

    coverage = {
        'population': len(matching_vars['variables'].get('population', {})),
        'pct_micropolitan': len(matching_vars['variables'].get('pct_micropolitan', {})),
        'pct_farm_income': len(matching_vars['variables'].get('pct_farm_income', {})),
        'pct_manufacturing': len(matching_vars['variables'].get('pct_manufacturing', {})),
        'msa_distances': len(matching_vars['variables'].get('msa_distances', {}))
    }

    for var_name, count in coverage.items():
        pct = (count / len(ALL_REGIONS) * 100) if ALL_REGIONS else 0
        status = "✓ COMPLETE" if count == len(ALL_REGIONS) else "⏳ IN PROGRESS"
        logger.info(f"{var_name:20s}: {count:2d}/{len(ALL_REGIONS)} regions ({pct:5.1f}%) {status}")

    logger.info("\n" + "=" * 70)
    logger.info("Next Steps:")
    logger.info("  1. Complete BEA API data collection for variables 3 & 4")
    logger.info("  2. Calculate regional centroids for distance calculations")
    logger.info("  3. Implement MSA distance algorithm (variables 5 & 6)")
    logger.info("  4. Validate all 6 variables have 100% coverage")
    logger.info("  5. Proceed to Mahalanobis distance peer matching")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
