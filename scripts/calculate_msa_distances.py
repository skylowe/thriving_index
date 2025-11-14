"""
Calculate MSA Distances

Calculates distances from each regional centroid to:
- Nearest small MSA (50k-250k population)
- Nearest large MSA (>250k population)

Uses Haversine distance formula for great circle distances.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from data.msa_database import get_nearest_msa
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def calculate_all_msa_distances(regional_centroids: dict, logger):
    """
    Calculate MSA distances for all regions.

    Args:
        regional_centroids: Dict mapping region codes to centroid data
        logger: Logger instance

    Returns:
        Dict mapping region codes to MSA distance data
    """
    msa_distances = {}

    for region_code, centroid in regional_centroids.items():
        logger.info(f"\nProcessing {region_code}: {ALL_REGIONS[region_code]['name']}")

        lat = centroid['lat']
        lon = centroid['lon']

        # Find nearest small MSA
        nearest_small = get_nearest_msa(lat, lon, size='small')
        if nearest_small:
            logger.info(f"  Nearest small MSA: {nearest_small['name']}")
            logger.info(f"    Distance: {nearest_small['distance']:.1f} miles")
        else:
            logger.warning(f"  No small MSA found")

        # Find nearest large MSA
        nearest_large = get_nearest_msa(lat, lon, size='large')
        if nearest_large:
            logger.info(f"  Nearest large MSA: {nearest_large['name']}")
            logger.info(f"    Distance: {nearest_large['distance']:.1f} miles")
        else:
            logger.warning(f"  No large MSA found")

        # Store results
        msa_distances[region_code] = {
            'small_msa_distance': nearest_small['distance'] if nearest_small else None,
            'small_msa_name': nearest_small['name'] if nearest_small else None,
            'large_msa_distance': nearest_large['distance'] if nearest_large else None,
            'large_msa_name': nearest_large['name'] if nearest_large else None
        }

    return msa_distances


def main():
    """Main execution."""
    logger = setup_logger('calculate_msa_distances')

    logger.info("=" * 70)
    logger.info("CALCULATING MSA DISTANCES")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions\n")

    # Load regional centroids
    centroids_file = project_root / 'data' / 'processed' / 'regional_centroids.json'

    if not centroids_file.exists():
        logger.error("Regional centroids file not found!")
        logger.error("Please run calculate_regional_centroids.py first")
        return

    with open(centroids_file) as f:
        regional_centroids = json.load(f)

    logger.info(f"Loaded centroids for {len(regional_centroids)} regions\n")

    # Calculate MSA distances
    msa_distances = calculate_all_msa_distances(regional_centroids, logger)

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

    # Update with MSA distance data
    matching_vars['variables']['msa_distances'] = msa_distances

    # Save results
    with open(matching_vars_file, 'w') as f:
        json.dump(matching_vars, f, indent=2)

    logger.info(f"\n✓ Saved MSA distances to: {matching_vars_file}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Regions with MSA distances: {len(msa_distances)}/{len(ALL_REGIONS)}")
    logger.info(f"Coverage: {len(msa_distances)/len(ALL_REGIONS)*100:.1f}%")

    # Statistics
    small_distances = [d['small_msa_distance'] for d in msa_distances.values() if d.get('small_msa_distance')]
    large_distances = [d['large_msa_distance'] for d in msa_distances.values() if d.get('large_msa_distance')]

    if small_distances:
        logger.info(f"\nSmall MSA distances:")
        logger.info(f"  Min: {min(small_distances):.1f} miles")
        logger.info(f"  Max: {max(small_distances):.1f} miles")
        logger.info(f"  Mean: {sum(small_distances)/len(small_distances):.1f} miles")

    if large_distances:
        logger.info(f"\nLarge MSA distances:")
        logger.info(f"  Min: {min(large_distances):.1f} miles")
        logger.info(f"  Max: {max(large_distances):.1f} miles")
        logger.info(f"  Mean: {sum(large_distances)/len(large_distances):.1f} miles")

    logger.info("=" * 70)


if __name__ == '__main__':
    main()
