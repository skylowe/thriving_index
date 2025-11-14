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


def load_county_data(logger):
    """
    Load county centroids and population data.

    Returns:
        Dict mapping FIPS to {lat, lon, population}
    """
    # Load county centroids from gazetteer file
    centroids_file = project_root / 'data' / 'processed' / 'county_centroids.json'

    if not centroids_file.exists():
        logger.error(f"County centroids file not found: {centroids_file}")
        logger.info("Run: python scripts/get_county_centroids.py")
        return {}

    with open(centroids_file) as f:
        centroids = json.load(f)

    logger.info(f"Loaded {len(centroids)} county centroids")

    # Load population data from Census API
    from src.api_clients.census_api import CensusAPI

    census = CensusAPI()
    state_fips_codes = {
        'VA': '51', 'MD': '24', 'WV': '54',
        'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'
    }

    county_populations = {}

    for state_abbr, state_fips in state_fips_codes.items():
        try:
            response = census.get_population(year=2022, state=state_fips)

            if response and len(response) > 0:
                for row in response:
                    state = row.get('state', '')
                    county = row.get('county', '')
                    # get_population() uses B01001_001E (total pop by sex)
                    population = row.get('B01001_001E', row.get('B01003_001E', 0))

                    if state and county:
                        fips = f"{state}{county}"
                        try:
                            county_populations[fips] = int(population)
                        except (ValueError, TypeError):
                            pass

        except Exception as e:
            logger.warning(f"Failed to get population for {state_abbr}: {e}")

    logger.info(f"Loaded population data for {len(county_populations)} counties")

    # Combine centroids and population
    county_data = {}
    for fips, centroid in centroids.items():
        if fips in county_populations:
            county_data[fips] = {
                'lat': centroid['lat'],
                'lon': centroid['lon'],
                'population': county_populations[fips]
            }
        else:
            # Use default population of 1 if not found
            county_data[fips] = {
                'lat': centroid['lat'],
                'lon': centroid['lon'],
                'population': 1
            }

    logger.info(f"✓ Combined data for {len(county_data)} counties")

    return county_data


def calculate_weighted_centroid(fips_list: list, county_data: dict, logger) -> dict:
    """
    Calculate population-weighted centroid for a region.

    Args:
        fips_list: List of FIPS codes in the region
        county_data: Dict mapping FIPS to {lat, lon, population}
        logger: Logger instance

    Returns:
        Dictionary with lat, lon, total_population
    """
    total_pop = 0
    weighted_lat = 0
    weighted_lon = 0
    counties_found = 0

    for fips in fips_list:
        if fips in county_data:
            county = county_data[fips]
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

    # Load county data (centroids + population)
    county_data = load_county_data(logger)

    if not county_data:
        logger.error("Failed to load county data")
        return

    regional_centroids = {}

    for region_code, region_info in ALL_REGIONS.items():
        logger.info(f"\nProcessing {region_code}: {region_info['name']}")

        # Get all FIPS codes for this region
        fips_list = get_all_fips_in_region(region_code)

        if not fips_list:
            logger.warning(f"  No FIPS codes found for {region_code}")
            continue

        # Calculate weighted centroid
        centroid = calculate_weighted_centroid(fips_list, county_data, logger)

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
