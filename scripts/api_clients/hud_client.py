"""
HUD (U.S. Department of Housing and Urban Development) API Client

This client retrieves data from HUD's ArcGIS REST API services.
Primary use: Qualified Opportunity Zones data.

Documentation: https://hudgis-hud.opendata.arcgis.com/
"""

import requests
import time
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT


class HUDClient:
    """Client for HUD ArcGIS REST API"""

    def __init__(self):
        """Initialize HUD client."""
        self.base_url = 'https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services'
        self.oz_endpoint = f'{self.base_url}/Opportunity_Zones/FeatureServer/13/query'
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
                raise Exception(f"HUD API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_opportunity_zones_count(self):
        """
        Get total count of Opportunity Zone tracts.

        Returns:
            int: Total number of OZ tracts nationwide
        """
        params = {
            'where': '1=1',
            'returnCountOnly': 'true',
            'f': 'json'
        }

        response = self._make_request(self.oz_endpoint, params)
        return response.get('count', 0)

    def get_opportunity_zones(self, state_fips_list=None, batch_size=1000):
        """
        Retrieve all Opportunity Zone tract data with pagination.

        Args:
            state_fips_list: Optional list of 2-digit state FIPS codes to filter
            batch_size: Number of records to fetch per request (default 1000)

        Returns:
            DataFrame: OZ tract data with columns: state_fips, county_fips, tract, geoid10, state_abbr, state_name
        """
        # Get total count
        total_count = self.get_opportunity_zones_count()
        print(f"Total OZ tracts nationwide: {total_count:,}")

        # Fetch all records with pagination
        all_features = []
        offset = 0

        print(f"Fetching OZ tract data (batch size: {batch_size})...")

        while offset < total_count:
            params = {
                'where': '1=1',
                'outFields': 'STATE,COUNTY,TRACT,GEOID10,STUSAB,STATE_NAME',
                'f': 'json',
                'resultOffset': offset,
                'resultRecordCount': batch_size
            }

            try:
                data = self._make_request(self.oz_endpoint, params)

                if 'features' in data:
                    features = data['features']
                    all_features.extend(features)
                    offset += len(features)
                    print(f"  Retrieved {offset:,} / {total_count:,} records ({100*offset/total_count:.1f}%)")

                    if len(features) == 0:
                        break
                else:
                    print(f"  Warning: No features in response at offset {offset}")
                    break

            except Exception as e:
                print(f"  Error at offset {offset}: {e}")
                break

        print(f"✓ Retrieved {len(all_features):,} total OZ tracts")

        # Convert to DataFrame
        oz_data = []
        for feature in all_features:
            attrs = feature['attributes']
            oz_data.append({
                'state_fips': attrs['STATE'],
                'county_fips': attrs['COUNTY'],
                'tract': attrs['TRACT'],
                'geoid10': attrs['GEOID10'],
                'state_abbr': attrs['STUSAB'],
                'state_name': attrs['STATE_NAME']
            })

        df = pd.DataFrame(oz_data)

        # Filter to specific states if requested
        if state_fips_list:
            df = df[df['state_fips'].isin(state_fips_list)].copy()
            print(f"Filtered to {len(df):,} OZ tracts in {len(state_fips_list)} states")

        return df

    def aggregate_oz_by_county(self, oz_df):
        """
        Aggregate OZ tract data to county level.

        Args:
            oz_df: DataFrame of OZ tracts from get_opportunity_zones()

        Returns:
            DataFrame: County-level OZ counts with columns: area_fips, oz_tract_count, state_fips, state_name, state_abbr
        """
        # Create full county FIPS (state + county)
        oz_df['county_fips_full'] = oz_df['state_fips'] + oz_df['county_fips']

        # Count OZ tracts per county
        county_oz_counts = oz_df.groupby('county_fips_full').agg({
            'tract': 'count',
            'state_fips': 'first',
            'state_name': 'first',
            'state_abbr': 'first'
        }).reset_index()

        county_oz_counts.rename(columns={
            'county_fips_full': 'area_fips',
            'tract': 'oz_tract_count'
        }, inplace=True)

        # Convert area_fips to integer for consistency
        county_oz_counts['area_fips'] = county_oz_counts['area_fips'].astype(int)

        return county_oz_counts


if __name__ == '__main__':
    # Test the HUD client
    print("Testing HUD API Client...")
    print("=" * 60)

    client = HUDClient()

    # Test 1: Get total count
    print("\nTest 1: Get Opportunity Zones Count")
    print("-" * 60)
    try:
        count = client.get_opportunity_zones_count()
        print(f"✓ Total OZ tracts nationwide: {count:,}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get OZ data for Delaware (small state for testing)
    print("\n\nTest 2: Get Opportunity Zones - Delaware Only")
    print("-" * 60)
    try:
        df = client.get_opportunity_zones(state_fips_list=['10'])
        print(f"✓ Retrieved {len(df)} OZ tracts for Delaware")
        if not df.empty:
            print(f"\nColumns: {df.columns.tolist()}")
            print(f"\nSample data:")
            print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Aggregate to county level
    print("\n\nTest 3: Aggregate to County Level")
    print("-" * 60)
    try:
        if not df.empty:
            county_df = client.aggregate_oz_by_county(df)
            print(f"✓ Aggregated to {len(county_df)} counties")
            print(f"\nCounty-level data:")
            print(county_df.to_string())
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("HUD Client test complete")
