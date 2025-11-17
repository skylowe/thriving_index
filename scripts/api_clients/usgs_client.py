"""
USGS National Map Transportation API Client

This client retrieves transportation data from USGS National Map ArcGIS REST API.
Primary use: Interstate highway presence data for county-level analysis.

Documentation: https://www.usgs.gov/national-geospatial-program/national-map
API Endpoint: https://carto.nationalmap.gov/arcgis/rest/services/transportation/mapserver
"""

import requests
import time
import pandas as pd
import geopandas as gpd
from pathlib import Path
import sys
from shapely.geometry import shape
import io

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT


class USGSTransportationClient:
    """Client for USGS National Map Transportation ArcGIS REST API"""

    def __init__(self):
        """Initialize USGS Transportation client."""
        self.base_url = 'https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer'
        self.controlled_access_layer = f'{self.base_url}/29/query'  # Controlled-access Highways layer
        self.session = requests.Session()

    def _make_request(self, url, params, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            url: API endpoint URL
            params: Query parameters
            retries: Number of retries remaining

        Returns:
            dict: JSON response
        """
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return response.json()

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"  Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1)
            else:
                raise Exception(f"USGS API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_interstate_highways_count(self):
        """
        Get total count of interstate highway features.

        Returns:
            int: Total number of interstate highway segments
        """
        params = {
            'where': "interstate IS NOT NULL AND interstate <> ''",
            'returnCountOnly': 'true',
            'f': 'json'
        }

        response = self._make_request(self.controlled_access_layer, params)
        return response.get('count', 0)

    def get_interstate_highways(self, batch_size=2000):
        """
        Retrieve all interstate highway geometries with pagination.

        Args:
            batch_size: Number of records to fetch per request (max 2000)

        Returns:
            GeoDataFrame: Interstate highway geometries with route information
        """
        # Get total count
        total_count = self.get_interstate_highways_count()
        print(f"Total interstate highway segments: {total_count:,}")

        if total_count == 0:
            print("Warning: No interstate highways found")
            return gpd.GeoDataFrame()

        # Fetch all records with pagination
        all_features = []
        offset = 0

        print(f"Fetching interstate highway data (batch size: {batch_size})...")

        while offset < total_count:
            params = {
                'where': "interstate IS NOT NULL AND interstate <> ''",
                'outFields': 'interstate,name',
                'returnGeometry': 'true',
                'f': 'geojson',
                'resultOffset': offset,
                'resultRecordCount': batch_size
            }

            try:
                data = self._make_request(self.controlled_access_layer, params)

                if 'features' in data:
                    features = data['features']
                    all_features.extend(features)
                    offset += len(features)
                    print(f"  Retrieved {offset:,} / {total_count:,} segments ({100*offset/total_count:.1f}%)")

                    if len(features) == 0:
                        break
                else:
                    print(f"  Warning: No features in response at offset {offset}")
                    break

            except Exception as e:
                print(f"  Error at offset {offset}: {e}")
                break

        print(f"✓ Retrieved {len(all_features):,} total interstate highway segments")

        # Convert to GeoDataFrame
        if all_features:
            gdf = gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
            return gdf
        else:
            return gpd.GeoDataFrame()

    def get_county_boundaries(self, year=2024):
        """
        Download Census TIGER county boundaries.

        Args:
            year: Year of TIGER boundaries (default 2024)

        Returns:
            GeoDataFrame: County boundaries with GEOID
        """
        print(f"Downloading Census TIGER {year} county boundaries...")

        # Census TIGER county boundaries URL
        url = f'https://www2.census.gov/geo/tiger/TIGER{year}/COUNTY/tl_{year}_us_county.zip'

        try:
            # Read directly from URL into GeoDataFrame
            counties = gpd.read_file(url)
            print(f"✓ Loaded {len(counties):,} county boundaries")

            # Ensure GEOID is string and 5 digits
            counties['GEOID'] = counties['GEOID'].astype(str).str.zfill(5)

            # Reproject to match highway data (EPSG:4326 / WGS84)
            if counties.crs != "EPSG:4326":
                counties = counties.to_crs("EPSG:4326")

            return counties

        except Exception as e:
            raise Exception(f"Failed to download county boundaries: {str(e)}")

    def identify_counties_with_interstates(self, state_fips_list=None):
        """
        Identify which counties have interstate highways using spatial intersection.

        Args:
            state_fips_list: Optional list of 2-digit state FIPS codes to filter counties

        Returns:
            DataFrame: County-level data with columns: area_fips, has_interstate, state_fips, county_name
        """
        # Get interstate highways
        interstates_gdf = self.get_interstate_highways()

        if interstates_gdf.empty:
            print("Error: No interstate data retrieved")
            return pd.DataFrame()

        # Get county boundaries
        counties_gdf = self.get_county_boundaries()

        if counties_gdf.empty:
            print("Error: No county boundaries retrieved")
            return pd.DataFrame()

        # Filter to specific states if requested
        if state_fips_list:
            # State FIPS is first 2 digits of GEOID
            counties_gdf = counties_gdf[counties_gdf['GEOID'].str[:2].isin(state_fips_list)].copy()
            print(f"Filtered to {len(counties_gdf):,} counties in {len(state_fips_list)} states")

        # Perform spatial intersection
        print("\nPerforming spatial analysis to identify counties with interstates...")
        print("(This may take a few minutes...)")

        # Use spatial join to find which counties intersect with interstates
        # Use 'inner' join to only keep counties that have interstates
        counties_with_interstates = gpd.sjoin(
            counties_gdf[['GEOID', 'NAME', 'geometry']],
            interstates_gdf[['geometry']],
            how='inner',
            predicate='intersects'
        )

        # Get unique county GEOIDs that have interstates
        counties_with_interstate_geoids = set(counties_with_interstates['GEOID'].unique())

        print(f"✓ Found {len(counties_with_interstate_geoids):,} counties with interstate highways")

        # Create result dataframe with all counties
        result = pd.DataFrame({
            'area_fips': counties_gdf['GEOID'].astype(int),
            'county_name': counties_gdf['NAME'],
            'has_interstate': counties_gdf['GEOID'].isin(counties_with_interstate_geoids).astype(int)
        })

        # Add state FIPS
        result['state_fips'] = result['area_fips'].astype(str).str.zfill(5).str[:2]

        # Summary statistics
        total_counties = len(result)
        counties_with = result['has_interstate'].sum()
        pct_with = 100 * counties_with / total_counties if total_counties > 0 else 0

        print(f"\n--- Summary ---")
        print(f"Total counties analyzed: {total_counties:,}")
        print(f"Counties with interstates: {counties_with:,} ({pct_with:.1f}%)")
        print(f"Counties without interstates: {total_counties - counties_with:,} ({100-pct_with:.1f}%)")

        return result


if __name__ == '__main__':
    # Test the USGS client
    print("Testing USGS Transportation API Client...")
    print("=" * 60)

    client = USGSTransportationClient()

    # Test 1: Get total count
    print("\nTest 1: Get Interstate Highway Count")
    print("-" * 60)
    try:
        count = client.get_interstate_highways_count()
        print(f"✓ Total interstate highway segments: {count:,}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get interstate highways for Delaware (small state for testing)
    print("\n\nTest 2: Identify Counties with Interstates - Delaware Only")
    print("-" * 60)
    try:
        df = client.identify_counties_with_interstates(state_fips_list=['10'])
        print(f"✓ Retrieved data for {len(df)} counties")
        if not df.empty:
            print(f"\nColumns: {df.columns.tolist()}")
            print(f"\nDelaware counties with interstates:")
            print(df[df['has_interstate'] == 1][['area_fips', 'county_name', 'has_interstate']])
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("USGS Client test complete")
