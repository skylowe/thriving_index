"""
Create region boundary GeoJSON files from county boundaries.

Downloads Census TIGER county shapefiles and aggregates them into regional boundaries
for all 94 regions across 10 states.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import requests
import zipfile
import io


# State FIPS codes for our 10 states
STATE_FIPS = {
    'Virginia': '51',
    'Pennsylvania': '42',
    'Maryland': '24',
    'Delaware': '10',
    'West Virginia': '54',
    'Kentucky': '21',
    'Tennessee': '47',
    'North Carolina': '37',
    'South Carolina': '45',
    'Georgia': '13'
}

STATE_FILES = {
    'Virginia': 'virginia_go_regions.csv',
    'Pennsylvania': 'pennsylvania_edd_regions.csv',
    'Maryland': 'maryland_edd_regions.csv',
    'Delaware': None,  # No regional divisions
    'West Virginia': 'westvirginia_edd_regions.csv',
    'Kentucky': 'kentucky_add_regions.csv',
    'Tennessee': 'tennessee_dd_regions.csv',
    'North Carolina': 'northcarolina_cog_regions.csv',
    'South Carolina': 'southcarolina_cog_regions.csv',
    'Georgia': 'georgia_rc_regions.csv'
}


def download_county_boundaries(year=2022):
    """
    Download county boundaries from Census TIGER.

    Returns national county shapefile as GeoDataFrame.
    """
    print("Downloading county boundaries from Census TIGER...")

    # Census TIGER counties URL
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COUNTY/tl_{year}_us_county.zip"

    print(f"  Fetching: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Extract zip file in memory
    print("  Extracting shapefile...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Create temp directory
        temp_dir = Path('data/temp')
        temp_dir.mkdir(parents=True, exist_ok=True)

        z.extractall(temp_dir)

        # Read shapefile
        shp_file = temp_dir / f"tl_{year}_us_county.shp"
        gdf = gpd.read_file(shp_file)

        print(f"  ✓ Loaded {len(gdf)} counties")

    return gdf


def filter_counties_to_10_states(gdf):
    """Filter counties to only our 10 states."""
    state_fips_list = list(STATE_FIPS.values())
    gdf_filtered = gdf[gdf['STATEFP'].isin(state_fips_list)].copy()

    print(f"\nFiltered to 10 states: {len(gdf_filtered)} counties")
    return gdf_filtered


def load_region_mappings():
    """Load all region-to-county mappings."""
    regions_dir = Path('data/regions')
    all_regions = []

    for state_name, filename in STATE_FILES.items():
        if filename is None:
            continue

        file_path = regions_dir / filename
        df = pd.read_csv(file_path)

        # The county_fips column is actually the full FIPS code (5 digits)
        df['fips'] = df['county_fips'].astype(str).str.zfill(5)

        # Create region_key from state_fips + region_id
        df['region_key'] = (
            df['state_fips'].astype(str).str.zfill(2) + '_' +
            df['region_id'].astype(str)
        )

        # Add state_name column
        df['state_name'] = state_name

        all_regions.append(df)
        print(f"  Loaded {len(df)} counties from {state_name}")

    # Combine all
    regions_df = pd.concat(all_regions, ignore_index=True)
    print(f"\n✓ Total: {len(regions_df)} county-region mappings")

    return regions_df


def create_region_boundaries(counties_gdf, regions_df):
    """
    Create region boundaries by dissolving county boundaries.

    Args:
        counties_gdf: GeoDataFrame of county boundaries
        regions_df: DataFrame with county-to-region mappings

    Returns:
        GeoDataFrame of region boundaries
    """
    print("\nCreating region boundaries...")

    # Use GEOID as FIPS (already 5-digit format)
    counties_gdf['fips'] = counties_gdf['GEOID']

    # Merge counties with region assignments
    counties_with_regions = counties_gdf.merge(
        regions_df[['fips', 'region_key', 'region_name', 'state_name']],
        on='fips',
        how='inner'
    )

    print(f"  Matched {len(counties_with_regions)} counties to regions")

    # Dissolve counties into regions
    print("  Dissolving county boundaries into regions...")
    regions_gdf = counties_with_regions.dissolve(
        by='region_key',
        aggfunc='first'  # Keep first occurrence of region metadata
    ).reset_index()

    # Keep only necessary columns
    regions_gdf = regions_gdf[[
        'region_key', 'region_name', 'state_name', 'geometry'
    ]]

    print(f"  ✓ Created {len(regions_gdf)} region boundaries")

    return regions_gdf, counties_with_regions


def save_geojson_files(regions_gdf, counties_gdf, output_dir):
    """Save region and county boundaries as GeoJSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save region boundaries
    regions_file = output_dir / 'region_boundaries.geojson'
    regions_gdf.to_file(regions_file, driver='GeoJSON')
    print(f"\n✓ Saved region boundaries: {regions_file}")
    print(f"  Regions: {len(regions_gdf)}")

    # Save county boundaries (for showing within regions)
    counties_file = output_dir / 'county_boundaries.geojson'
    counties_gdf.to_file(counties_file, driver='GeoJSON')
    print(f"✓ Saved county boundaries: {counties_file}")
    print(f"  Counties: {len(counties_gdf)}")

    return regions_file, counties_file


def main():
    """Create region and county boundary GeoJSON files."""
    print("="*80)
    print("CREATE REGION BOUNDARY FILES")
    print("="*80)

    # 1. Download county boundaries
    counties_gdf = download_county_boundaries(year=2022)

    # 2. Filter to our 10 states
    counties_gdf = filter_counties_to_10_states(counties_gdf)

    # 3. Load region mappings
    print("\nLoading region-to-county mappings...")
    regions_df = load_region_mappings()

    # 4. Create region boundaries
    regions_gdf, counties_with_regions = create_region_boundaries(
        counties_gdf, regions_df
    )

    # 5. Save as GeoJSON
    print("\nSaving GeoJSON files...")
    regions_file, counties_file = save_geojson_files(
        regions_gdf,
        counties_with_regions,
        output_dir='data/geojson'
    )

    # Summary
    print("\n" + "="*80)
    print("REGION BOUNDARIES CREATED SUCCESSFULLY!")
    print("="*80)
    print(f"\nFiles created:")
    print(f"  1. {regions_file} ({len(regions_gdf)} regions)")
    print(f"  2. {counties_file} ({len(counties_with_regions)} counties)")
    print(f"\nCoverage:")
    print(f"  States: {regions_gdf['state_name'].nunique()}")
    print(f"  Regions: {len(regions_gdf)}")
    print(f"  Counties: {len(counties_with_regions)}")

    # Show region counts by state
    print("\nRegions by state:")
    state_counts = regions_gdf.groupby('state_name').size().sort_values(ascending=False)
    for state, count in state_counts.items():
        print(f"  {state}: {count} regions")


if __name__ == '__main__':
    main()
