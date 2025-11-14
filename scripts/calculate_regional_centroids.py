"""
Calculate Regional Centroids

Calculates population-weighted geographic centroids for all 54 regions.
Uses county centroids from Census Gazetteer files.

Outputs:
- Regional centroid coordinates (latitude, longitude)
- Used for calculating distances to MSAs (matching variables 5 & 6)
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.fips_to_region import get_all_fips_in_region
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


# County centroid data (subset - would normally load from Census Gazetteer file)
# Format: {FIPS: {'lat': float, 'lon': float, 'population': int}}
COUNTY_CENTROIDS = {
    # Virginia - Major counties/cities (examples)
    '51013': {'lat': 38.8816, 'lon': -77.0910, 'population': 238643},  # Arlington
    '51059': {'lat': 38.8462, 'lon': -77.3064, 'population': 1150309},  # Fairfax
    '51107': {'lat': 39.0738, 'lon': -77.6469, 'population': 456599},  # Loudoun
    '51153': {'lat': 38.7235, 'lon': -77.4610, 'population': 470335},  # Prince William
    '51510': {'lat': 38.8048, 'lon': -77.0469, 'population': 159467},  # Alexandria City
    '51087': {'lat': 37.5538, 'lon': -77.4428, 'population': 334389},  # Henrico
    '51041': {'lat': 37.3771, 'lon': -77.6050, 'population': 364548},  # Chesterfield
    '51760': {'lat': 37.5407, 'lon': -77.4360, 'population': 226610},  # Richmond City
    '51810': {'lat': 36.8529, 'lon': -76.0859, 'population': 459470},  # Virginia Beach
    '51710': {'lat': 36.8468, 'lon': -76.2852, 'population': 238005},  # Norfolk
    '51650': {'lat': 37.0299, 'lon': -76.3452, 'population': 137148},  # Hampton

    # Maryland - Major counties
    '24031': {'lat': 39.1434, 'lon': -77.2014, 'population': 1062061},  # Montgomery
    '24033': {'lat': 38.8277, 'lon': -76.8730, 'population': 967201},  # Prince George's
    '24005': {'lat': 39.4145, 'lon': -76.6093, 'population': 854535},  # Baltimore County
    '24510': {'lat': 39.2904, 'lon': -76.6122, 'population': 585708},  # Baltimore City

    # DC
    '11001': {'lat': 38.9072, 'lon': -77.0369, 'population': 670587},  # District of Columbia

    # TODO: Add remaining 515 counties
    # This should be loaded from Census Gazetteer file:
    # https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
}


def calculate_weighted_centroid(fips_list: list, logger) -> dict:
    """
    Calculate population-weighted centroid for a region.

    Args:
        fips_list: List of FIPS codes in the region
        logger: Logger instance

    Returns:
        Dictionary with lat, lon, total_population
    """
    total_pop = 0
    weighted_lat = 0
    weighted_lon = 0
    counties_found = 0

    for fips in fips_list:
        if fips in COUNTY_CENTROIDS:
            county = COUNTY_CENTROIDS[fips]
            pop = county['population']

            weighted_lat += county['lat'] * pop
            weighted_lon += county['lon'] * pop
            total_pop += pop
            counties_found += 1

    if total_pop > 0:
        centroid = {
            'lat': weighted_lat / total_pop,
            'lon': weighted_lon / total_pop,
            'population': total_pop,
            'counties_included': counties_found,
            'counties_total': len(fips_list)
        }
        return centroid
    else:
        logger.warning(f"No centroids found for region with {len(fips_list)} counties")
        return None


def main():
    """Main execution."""
    logger = setup_logger('calculate_regional_centroids')

    logger.info("=" * 70)
    logger.info("CALCULATING REGIONAL CENTROIDS")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions\n")

    regional_centroids = {}

    for region_code, region_info in ALL_REGIONS.items():
        logger.info(f"Processing {region_code}: {region_info['name']}")

        # Get all FIPS codes for this region
        fips_list = get_all_fips_in_region(region_code)

        if not fips_list:
            logger.warning(f"  No FIPS codes found for {region_code}")
            continue

        # Calculate weighted centroid
        centroid = calculate_weighted_centroid(fips_list, logger)

        if centroid:
            regional_centroids[region_code] = centroid
            logger.info(f"  ✓ Centroid: {centroid['lat']:.4f}°N, {centroid['lon']:.4f}°W")
            logger.info(f"    Population: {centroid['population']:,}")
            logger.info(f"    Coverage: {centroid['counties_included']}/{centroid['counties_total']} counties")
        else:
            logger.warning(f"  ✗ Could not calculate centroid")

    # Save results
    output_path = project_root / 'data' / 'processed' / 'regional_centroids.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(regional_centroids, f, indent=2)

    logger.info(f"\n✓ Saved regional centroids to: {output_path}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Regions with centroids: {len(regional_centroids)}/{len(ALL_REGIONS)}")
    logger.info(f"Coverage: {len(regional_centroids)/len(ALL_REGIONS)*100:.1f}%")

    logger.info("\n⚠️  NOTE: This uses a subset of county centroids.")
    logger.info("For complete coverage, download Census Gazetteer file:")
    logger.info("https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
