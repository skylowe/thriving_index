"""
Get County Centroids from Census Gazetteer Files

Downloads and parses Census Bureau Gazetteer files to get latitude/longitude
centroids and populations for all counties in the study.

Source: https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/
"""

import sys
from pathlib import Path
import json
import requests
import csv
from io import StringIO
from typing import Dict

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.logging_setup import setup_logger


def download_census_gazetteer(logger):
    """
    Download Census Gazetteer file for counties.

    Returns:
        Dict mapping FIPS codes to centroid data
    """
    logger.info("\n" + "=" * 70)
    logger.info("Downloading Census Gazetteer File")
    logger.info("=" * 70)

    # Census Gazetteer URL
    url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_counties_national.zip"

    logger.info(f"\nDownloading from: {url}")

    try:
        # Download the file
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        logger.info(f"✓ Downloaded {len(response.content):,} bytes")

        # Save to temp file
        zip_path = project_root / 'data' / 'temp' / '2023_Gaz_counties_national.zip'
        zip_path.parent.mkdir(parents=True, exist_ok=True)

        with open(zip_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"✓ Saved to: {zip_path}")

        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(zip_path.parent)

        logger.info(f"✓ Extracted zip file")

        # Find the txt file
        txt_files = list(zip_path.parent.glob("*.txt"))
        if not txt_files:
            logger.error("No .txt file found in zip")
            return {}

        txt_file = txt_files[0]
        logger.info(f"✓ Found data file: {txt_file.name}")

        return txt_file

    except Exception as e:
        logger.error(f"Failed to download gazetteer: {e}")
        import traceback
        traceback.print_exc()
        return None


def parse_gazetteer_file(txt_file: Path, logger):
    """
    Parse Census Gazetteer file to extract county centroids.

    Format: Tab-delimited with columns:
    - USPS: State abbreviation
    - GEOID: 5-digit FIPS code
    - NAME: County name
    - INTPTLAT: Latitude (internal point)
    - INTPTLONG: Longitude (internal point)

    Returns:
        Dict mapping FIPS to {name, lat, lon}
    """
    logger.info("\n" + "=" * 70)
    logger.info("Parsing Gazetteer File")
    logger.info("=" * 70)

    county_centroids = {}

    try:
        with open(txt_file, 'r', encoding='latin-1') as f:
            # Read the file
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                try:
                    # Strip whitespace from keys and values
                    row = {k.strip(): v.strip() for k, v in row.items()}

                    geoid = row.get('GEOID', '')
                    name = row.get('NAME', '')
                    lat = row.get('INTPTLAT', '')
                    lon = row.get('INTPTLONG', '')

                    # Skip rows with empty lat/lon
                    if not lat or not lon:
                        continue

                    # Filter to our study states
                    state_fips = geoid[:2] if len(geoid) >= 5 else ''
                    study_states = ['51', '24', '54', '37', '47', '21', '11']

                    if state_fips in study_states and len(geoid) == 5:
                        county_centroids[geoid] = {
                            'name': name,
                            'lat': float(lat),
                            'lon': float(lon)
                        }

                except (ValueError, TypeError, KeyError) as e:
                    # Skip rows with parse errors silently
                    continue

        logger.info(f"\n✓ Parsed {len(county_centroids)} counties from study states")

        # Show sample
        if county_centroids:
            sample_fips = list(county_centroids.keys())[0]
            sample = county_centroids[sample_fips]
            logger.info(f"\nSample: {sample_fips} - {sample['name']}")
            logger.info(f"  Lat: {sample['lat']}, Lon: {sample['lon']}")

        return county_centroids

    except Exception as e:
        logger.error(f"Failed to parse gazetteer: {e}")
        import traceback
        traceback.print_exc()
        return {}


def save_county_centroids(county_centroids: Dict, logger):
    """
    Save county centroids to JSON file.

    Args:
        county_centroids: Dict mapping FIPS to centroid data
    """
    logger.info("\n" + "=" * 70)
    logger.info("Saving County Centroids")
    logger.info("=" * 70)

    output_file = project_root / 'data' / 'processed' / 'county_centroids.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(county_centroids, f, indent=2)

    logger.info(f"\n✓ Saved {len(county_centroids)} county centroids to:")
    logger.info(f"  {output_file}")

    # Show coverage by state
    by_state = {}
    for fips in county_centroids.keys():
        state_fips = fips[:2]
        by_state[state_fips] = by_state.get(state_fips, 0) + 1

    state_names = {
        '51': 'Virginia',
        '24': 'Maryland',
        '54': 'West Virginia',
        '37': 'North Carolina',
        '47': 'Tennessee',
        '21': 'Kentucky',
        '11': 'DC'
    }

    logger.info("\nCoverage by state:")
    for state_fips, count in sorted(by_state.items()):
        state_name = state_names.get(state_fips, state_fips)
        logger.info(f"  {state_name}: {count} counties")


def main():
    """Main execution."""
    logger = setup_logger('get_county_centroids')

    logger.info("=" * 70)
    logger.info("COLLECTING COUNTY CENTROIDS FROM CENSUS GAZETTEER")
    logger.info("=" * 70)
    logger.info("\nThis will download Census Bureau Gazetteer data with")
    logger.info("latitude/longitude centroids for all U.S. counties.\n")

    # Download gazetteer file
    txt_file = download_census_gazetteer(logger)

    if not txt_file:
        logger.error("\nFailed to download gazetteer file")
        return

    # Parse the file
    county_centroids = parse_gazetteer_file(txt_file, logger)

    if not county_centroids:
        logger.error("\nFailed to parse gazetteer file")
        return

    # Save results
    save_county_centroids(county_centroids, logger)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COLLECTION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"✓ Collected centroids for {len(county_centroids)} counties")
    logger.info("\nNext step: Run calculate_regional_centroids.py to aggregate")
    logger.info("county centroids to regional level (population-weighted).")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
