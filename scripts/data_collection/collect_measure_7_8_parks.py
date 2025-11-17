"""
Measure 7.8: Count of National Parks - Data Collection Script

Collects national park data from NPS API and maps parks to counties using
spatial analysis (point-in-polygon).

Note: NPS API provides point coordinates (headquarters/visitor center), not full
park boundaries. For large parks spanning multiple counties, this assigns the park
to the county containing the coordinate point.

States: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
"""

import sys
from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import STATE_FIPS, RAW_DATA_DIR, PROCESSED_DATA_DIR
from api_clients.nps_client import NPSClient


def load_county_boundaries(cache_file=None):
    """
    Load county boundary data from cache (Component 6).

    Args:
        cache_file: Path to cached county boundaries pickle file

    Returns:
        GeoDataFrame: County boundaries with FIPS codes
    """
    if cache_file is None:
        cache_file = RAW_DATA_DIR / 'usgs' / 'cache' / 'county_boundaries_2024.pkl'

    if not cache_file.exists():
        print(f"  County boundaries cache not found at {cache_file}")
        print(f"  Downloading from Census TIGER...")

        # Download county boundaries - download locally first
        import requests
        import zipfile
        import io

        url = "https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip"

        # Download ZIP file
        print(f"    Downloading {url}...")
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        # Save ZIP temporarily
        zip_path = cache_file.parent / 'temp_counties.zip'
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print(f"    ✓ Downloaded {len(response.content) / (1024*1024):.1f} MB")

        # Load with geopandas
        counties_gdf = gpd.read_file(f"zip://{zip_path}")

        # Cache for future use
        counties_gdf.to_pickle(cache_file)
        print(f"    ✓ Cached county boundaries to {cache_file}")

        # Clean up temp file
        zip_path.unlink()
        print(f"    ✓ Cleaned up temporary file")
    else:
        print(f"  Using cached county boundaries from {cache_file}")
        counties_gdf = pd.read_pickle(cache_file)

    return counties_gdf


def collect_nps_parks(nps_client, state_codes):
    """
    Collect all parks from NPS API for specified states.

    Args:
        nps_client: NPSClient instance
        state_codes: List of 2-letter state codes (e.g., ['VA', 'MD'])

    Returns:
        list: List of park records with locations
    """
    print(f"\nCollecting NPS Parks...")
    print("-" * 60)

    # Fetch all parks for our states
    all_parks = nps_client.get_all_parks(state_codes=state_codes)

    # Parse locations
    park_locations = []
    for park in all_parks:
        location = nps_client.parse_park_location(park)

        # Only include parks with valid coordinates
        if location['latitude'] and location['longitude']:
            park_locations.append(location)
        else:
            print(f"    Warning: No coordinates for {park.get('fullName', 'Unknown')}")

    print(f"\n✓ Total parks with coordinates: {len(park_locations)}")

    return park_locations


def map_parks_to_counties(park_locations, counties_gdf, state_fips_list):
    """
    Map parks to counties using spatial point-in-polygon analysis.

    Args:
        park_locations: List of park location dictionaries
        counties_gdf: GeoDataFrame with county boundaries
        state_fips_list: List of state FIPS codes to filter

    Returns:
        DataFrame: Parks mapped to counties with counts
    """
    print(f"\nMapping parks to counties...")
    print("-" * 60)

    # Filter counties to our 10 states
    counties_gdf = counties_gdf[counties_gdf['STATEFP'].isin(state_fips_list)].copy()
    print(f"  Counties in scope: {len(counties_gdf)}")

    # Ensure CRS is WGS84 for lat/lon coordinates
    if counties_gdf.crs != "EPSG:4326":
        counties_gdf = counties_gdf.to_crs("EPSG:4326")

    # Create GeoDataFrame from park locations
    park_points = []
    park_data = []

    for park in park_locations:
        if park['latitude'] and park['longitude']:
            point = Point(park['longitude'], park['latitude'])
            park_points.append(point)
            park_data.append(park)

    parks_gdf = gpd.GeoDataFrame(
        park_data,
        geometry=park_points,
        crs="EPSG:4326"
    )

    print(f"  Parks to map: {len(parks_gdf)}")

    # Spatial join: assign parks to counties
    parks_with_counties = gpd.sjoin(
        parks_gdf,
        counties_gdf[['STATEFP', 'COUNTYFP', 'NAME', 'geometry']],
        how='left',
        predicate='within'
    )

    # Check for unmapped parks
    unmapped = parks_with_counties[parks_with_counties['STATEFP'].isna()]
    if len(unmapped) > 0:
        print(f"  Warning: {len(unmapped)} parks could not be mapped to counties:")
        for idx, park in unmapped.iterrows():
            print(f"    - {park['park_name']} ({park['park_code']})")

    # Remove unmapped parks
    mapped_parks = parks_with_counties[parks_with_counties['STATEFP'].notna()].copy()
    print(f"  ✓ Successfully mapped {len(mapped_parks)} parks to counties")

    # Count parks per county
    county_park_counts = mapped_parks.groupby(['STATEFP', 'COUNTYFP']).size().reset_index(name='park_count')

    # Add county names
    county_names = counties_gdf[['STATEFP', 'COUNTYFP', 'NAME']].drop_duplicates()
    county_park_counts = county_park_counts.merge(
        county_names,
        on=['STATEFP', 'COUNTYFP'],
        how='left'
    )

    # Create full county list (all 802 counties) with 0 counts for counties without parks
    all_counties = counties_gdf[['STATEFP', 'COUNTYFP', 'NAME']].copy()
    all_counties = all_counties.merge(
        county_park_counts[['STATEFP', 'COUNTYFP', 'park_count']],
        on=['STATEFP', 'COUNTYFP'],
        how='left'
    )
    all_counties['park_count'] = all_counties['park_count'].fillna(0).astype(int)

    print(f"\n  Counties with parks: {len(county_park_counts)}")
    print(f"  Counties without parks: {len(all_counties[all_counties['park_count'] == 0])}")
    print(f"  Max parks in a county: {all_counties['park_count'].max()}")

    return all_counties, mapped_parks


def save_results(county_counts, park_details, nps_raw_data):
    """
    Save results to processed data directory.

    Args:
        county_counts: DataFrame with park counts by county
        park_details: GeoDataFrame with parks mapped to counties
        nps_raw_data: Raw park data from NPS API
    """
    print(f"\nSaving results...")
    print("=" * 60)

    processed_dir = PROCESSED_DATA_DIR
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = RAW_DATA_DIR / 'nps'
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Save county-level counts (main output)
    output_file = processed_dir / 'nps_park_counts_by_county.csv'
    county_counts.to_csv(output_file, index=False)
    print(f"✓ Saved: {output_file}")

    # Save detailed park-to-county mapping
    park_details_df = pd.DataFrame(park_details.drop(columns=['geometry']))
    output_file = processed_dir / 'nps_parks_county_mapping.csv'
    park_details_df.to_csv(output_file, index=False)
    print(f"✓ Saved: {output_file}")

    # Save raw NPS API data
    output_file = raw_dir / 'nps_parks_raw_data.json'
    with open(output_file, 'w') as f:
        json.dump(nps_raw_data, f, indent=2)
    print(f"✓ Saved: {output_file}")

    # Create summary
    summary = {
        'collection_date': datetime.now().isoformat(),
        'total_parks': len(park_details),
        'counties_with_parks': len(county_counts[county_counts['park_count'] > 0]),
        'total_counties': len(county_counts),
        'mean_parks_per_county': float(county_counts['park_count'].mean()),
        'max_parks_in_county': int(county_counts['park_count'].max()),
        'states': list(STATE_FIPS.keys())
    }

    output_file = processed_dir / 'measure_7_8_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved: {output_file}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total parks collected: {summary['total_parks']}")
    print(f"Counties with parks: {summary['counties_with_parks']} ({summary['counties_with_parks']/summary['total_counties']*100:.1f}%)")
    print(f"Counties without parks: {summary['total_counties'] - summary['counties_with_parks']}")
    print(f"Average parks per county: {summary['mean_parks_per_county']:.2f}")
    print(f"Maximum parks in one county: {summary['max_parks_in_county']}")

    return summary


def main():
    """Main execution function"""
    print("=" * 60)
    print("Measure 7.8: Count of National Parks")
    print("=" * 60)

    # State codes for our 10 states
    state_codes = list(STATE_FIPS.keys())
    state_fips_list = list(STATE_FIPS.values())

    try:
        # Initialize NPS client
        print("\nInitializing NPS API client...")
        nps_client = NPSClient()
        print("✓ Client initialized")

        # Collect parks from NPS API
        park_locations = collect_nps_parks(nps_client, state_codes)

        # Save raw data for reference
        nps_raw_data = park_locations

        # Load county boundaries
        print("\nLoading county boundaries...")
        counties_gdf = load_county_boundaries()
        print(f"✓ Loaded {len(counties_gdf)} county boundaries")

        # Map parks to counties
        county_counts, park_details = map_parks_to_counties(
            park_locations,
            counties_gdf,
            state_fips_list
        )

        # Save results
        summary = save_results(county_counts, park_details, nps_raw_data)

        print("\n✓ Collection complete!")
        return 0

    except Exception as e:
        print(f"\n✗ Error during collection: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
