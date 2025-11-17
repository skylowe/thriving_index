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


def collect_nps_parks_with_boundaries(nps_client, state_codes):
    """
    Collect all parks from NPS API with boundary geometries.

    Args:
        nps_client: NPSClient instance
        state_codes: List of 2-letter state codes (e.g., ['VA', 'MD'])

    Returns:
        tuple: (parks_with_boundaries, parks_with_points_only, park_raw_data)
    """
    print(f"\nCollecting NPS Parks and Boundaries...")
    print("-" * 60)

    # Fetch all parks for our states
    all_parks = nps_client.get_all_parks(state_codes=state_codes)

    parks_with_boundaries = []
    parks_with_points_only = []
    park_raw_data = []

    print(f"\n  Fetching boundaries for {len(all_parks)} parks...")

    for i, park in enumerate(all_parks, 1):
        park_code = park.get('parkCode', '')
        park_name = park.get('fullName', 'Unknown')

        # Parse basic location info
        location = nps_client.parse_park_location(park)
        park_raw_data.append(location)

        # Try to fetch boundary geometry
        boundary = nps_client.get_park_boundary(park_code)

        if boundary and 'geometry' in boundary:
            # Park has boundary data
            location['has_boundary'] = True
            location['geometry'] = boundary['geometry']
            parks_with_boundaries.append(location)
            if i % 5 == 0:
                print(f"    Progress: {i}/{len(all_parks)} parks (boundaries: {len(parks_with_boundaries)}, points: {len(parks_with_points_only)})")
        elif location['latitude'] and location['longitude']:
            # Fall back to point location
            location['has_boundary'] = False
            parks_with_points_only.append(location)
            if i % 5 == 0:
                print(f"    Progress: {i}/{len(all_parks)} parks (boundaries: {len(parks_with_boundaries)}, points: {len(parks_with_points_only)})")
        else:
            print(f"    Warning: No boundary or coordinates for {park_name} ({park_code})")

    print(f"\n  ✓ Parks with boundaries: {len(parks_with_boundaries)}")
    print(f"  ✓ Parks with points only: {len(parks_with_points_only)}")
    print(f"  Total parks: {len(parks_with_boundaries) + len(parks_with_points_only)}")

    return parks_with_boundaries, parks_with_points_only, park_raw_data


def map_parks_to_counties(parks_with_boundaries, parks_with_points, counties_gdf, state_fips_list):
    """
    Map parks to counties using spatial intersection for boundaries and point-in-polygon for points.

    Args:
        parks_with_boundaries: List of parks with boundary geometries
        parks_with_points: List of parks with point coordinates only
        counties_gdf: GeoDataFrame with county boundaries
        state_fips_list: List of state FIPS codes to filter

    Returns:
        tuple: (county_counts DataFrame, park_county_assignments DataFrame)
    """
    print(f"\nMapping parks to counties...")
    print("-" * 60)

    # Filter counties to our 10 states
    counties_gdf = counties_gdf[counties_gdf['STATEFP'].isin(state_fips_list)].copy()
    print(f"  Counties in scope: {len(counties_gdf)}")

    # Ensure CRS is WGS84
    if counties_gdf.crs != "EPSG:4326":
        counties_gdf = counties_gdf.to_crs("EPSG:4326")

    all_park_county_assignments = []

    # Process parks with boundaries (polygon intersection)
    if parks_with_boundaries:
        print(f"\n  Processing {len(parks_with_boundaries)} parks with boundaries...")

        for park in parks_with_boundaries:
            try:
                from shapely.geometry import shape
                # Convert GeoJSON geometry to Shapely geometry
                park_geom = shape(park['geometry'])

                # Find all counties that intersect with this park
                intersecting = counties_gdf[counties_gdf.intersects(park_geom)].copy()

                for _, county in intersecting.iterrows():
                    all_park_county_assignments.append({
                        'park_code': park['park_code'],
                        'park_name': park['park_name'],
                        'designation': park['designation'],
                        'states': park['states'],
                        'has_boundary': True,
                        'STATEFP': county['STATEFP'],
                        'COUNTYFP': county['COUNTYFP'],
                        'county_name': county['NAME']
                    })

                if len(intersecting) == 0:
                    print(f"    Warning: No counties found for {park['park_name']}")

            except Exception as e:
                print(f"    Error processing boundary for {park['park_name']}: {e}")

        print(f"    ✓ Mapped to {len(all_park_county_assignments)} park-county assignments")

    # Process parks with points only (point-in-polygon)
    if parks_with_points:
        print(f"\n  Processing {len(parks_with_points)} parks with points only...")

        park_points = []
        park_data = []

        for park in parks_with_points:
            if park['latitude'] and park['longitude']:
                point = Point(park['longitude'], park['latitude'])
                park_points.append(point)
                park_data.append(park)

        if park_points:
            parks_gdf = gpd.GeoDataFrame(
                park_data,
                geometry=park_points,
                crs="EPSG:4326"
            )

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
                print(f"    Warning: {len(unmapped)} parks could not be mapped:")
                for idx, park in unmapped.iterrows():
                    print(f"      - {park['park_name']} ({park['park_code']})")

            # Add mapped parks to assignments
            for idx, row in parks_with_counties.iterrows():
                if pd.notna(row['STATEFP']):
                    all_park_county_assignments.append({
                        'park_code': row['park_code'],
                        'park_name': row['park_name'],
                        'designation': row['designation'],
                        'states': row['states'],
                        'has_boundary': False,
                        'STATEFP': row['STATEFP'],
                        'COUNTYFP': row['COUNTYFP'],
                        'county_name': row['NAME']
                    })

            print(f"    ✓ Mapped {len(parks_with_counties[parks_with_counties['STATEFP'].notna()])} parks")

    # Create DataFrame of all park-county assignments
    park_assignments_df = pd.DataFrame(all_park_county_assignments)
    print(f"\n  Total park-county assignments: {len(park_assignments_df)}")

    # Count unique parks per county
    county_park_counts = park_assignments_df.groupby(['STATEFP', 'COUNTYFP']).agg({
        'park_code': 'count'  # Count parks per county
    }).reset_index()
    county_park_counts.columns = ['STATEFP', 'COUNTYFP', 'park_count']

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

    return all_counties, park_assignments_df


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
    output_file = processed_dir / 'nps_parks_county_mapping.csv'
    park_details.to_csv(output_file, index=False)
    print(f"✓ Saved: {output_file}")

    # Save raw NPS API data
    output_file = raw_dir / 'nps_parks_raw_data.json'
    with open(output_file, 'w') as f:
        json.dump(nps_raw_data, f, indent=2)
    print(f"✓ Saved: {output_file}")

    # Create summary
    unique_parks = park_details['park_code'].nunique() if not park_details.empty else 0
    summary = {
        'collection_date': datetime.now().isoformat(),
        'total_parks': unique_parks,
        'total_park_county_assignments': len(park_details),
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

        # Collect parks from NPS API with boundaries
        parks_with_boundaries, parks_with_points, nps_raw_data = collect_nps_parks_with_boundaries(
            nps_client, state_codes
        )

        # Load county boundaries
        print("\nLoading county boundaries...")
        counties_gdf = load_county_boundaries()
        print(f"✓ Loaded {len(counties_gdf)} county boundaries")

        # Map parks to counties (using boundaries for spatial intersection)
        county_counts, park_details = map_parks_to_counties(
            parks_with_boundaries,
            parks_with_points,
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
