"""
FCC (Federal Communications Commission) Broadband Data Collection API Client

This client retrieves data from FCC's Broadband Data Collection (BDC) Public Data API.
Primary use: Broadband availability and coverage data at county level.

Documentation: https://www.fcc.gov/sites/default/files/bdc-public-data-api-spec.pdf
API Base: https://broadbandmap.fcc.gov/api/public/map
"""

import requests
import time
import pandas as pd
from pathlib import Path
import sys
import json

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR, FCC_BB_KEY


class FCCBroadbandClient:
    """Client for FCC Broadband Data Collection Public Data API"""

    def __init__(self, api_key=None, username=None):
        """
        Initialize FCC Broadband client.

        Args:
            api_key: FCC API hash_value (defaults to FCC_BB_KEY from config)
            username: FCC API username/email (optional, defaults to generic email)
        """
        self.api_key = api_key or FCC_BB_KEY
        # Username should be an email address for FCC API
        self.username = username or "thriving_index@example.com"
        self.base_url = 'https://broadbandmap.fcc.gov/api/public/map'
        self.session = requests.Session()

        # Set up authentication headers (following FCC API spec)
        if self.api_key:
            self.session.headers.clear()  # Clear default headers first
            self.session.headers.update({
                'username': self.username,
                'hash_value': self.api_key,
                'user-agent': 'VATrivingIndex/1.0'
            })

        # Set up cache directory
        self.cache_dir = RAW_DATA_DIR / 'fcc' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_request(self, endpoint, params=None, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            endpoint: API endpoint (e.g., 'listAsOfDates')
            params: Query parameters (optional)
            retries: Number of retries remaining

        Returns:
            dict or DataFrame: JSON response or parsed data
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY)

            # Try to parse as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                # Some endpoints might return other formats
                return response.text

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"  Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(endpoint, params, retries - 1)
            else:
                raise Exception(f"FCC API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_available_dates(self):
        """
        Get list of available data collection dates.

        Returns:
            list: Available as-of dates for broadband data
        """
        print("Fetching available data collection dates...")
        response = self._make_request('listAsOfDates')

        if isinstance(response, dict) and 'data' in response:
            dates = response['data']
        elif isinstance(response, list):
            dates = response
        else:
            dates = []

        print(f"  Found {len(dates)} available date(s)")
        return dates

    def get_county_summary(self, county_fips, as_of_date=None, min_download_speed=100, min_upload_speed=10):
        """
        Get broadband availability summary for a specific county.

        Args:
            county_fips: 5-digit county FIPS code (state + county)
            as_of_date: Data collection date (YYYY-MM-DD format) or None for latest
            min_download_speed: Minimum download speed in Mbps (default 100)
            min_upload_speed: Minimum upload speed in Mbps (default 10)

        Returns:
            dict: County broadband availability data
        """
        params = {
            'fips': county_fips,
            'minDownloadSpeed': min_download_speed,
            'minUploadSpeed': min_upload_speed
        }

        if as_of_date:
            params['asOfDate'] = as_of_date

        try:
            response = self._make_request('county', params=params)
            return response
        except Exception as e:
            print(f"  Error fetching data for county {county_fips}: {str(e)}")
            return None

    def get_broadband_availability_batch(self, county_fips_list, as_of_date=None,
                                         min_download_speed=100, min_upload_speed=10,
                                         use_cache=True):
        """
        Get broadband availability data for multiple counties.

        Args:
            county_fips_list: List of 5-digit county FIPS codes
            as_of_date: Data collection date or None for latest
            min_download_speed: Minimum download speed in Mbps (default 100)
            min_upload_speed: Minimum upload speed in Mbps (default 10)
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame: County-level broadband availability data
        """
        # Create cache filename
        cache_key = f"broadband_{min_download_speed}_{min_upload_speed}"
        if as_of_date:
            cache_key += f"_{as_of_date}"
        cache_file = self.cache_dir / f'{cache_key}.pkl'

        # Check cache
        if use_cache and cache_file.exists():
            print(f"Loading broadband data from cache: {cache_file}")
            try:
                df = pd.read_pickle(cache_file)
                print(f"✓ Loaded {len(df):,} counties from cache")
                return df
            except Exception as e:
                print(f"  Cache load failed: {str(e)}, fetching fresh data...")

        # Fetch data for each county
        print(f"Fetching broadband data for {len(county_fips_list):,} counties...")
        print(f"  Download speed: ≥{min_download_speed} Mbps")
        print(f"  Upload speed: ≥{min_upload_speed} Mbps")

        results = []
        for i, county_fips in enumerate(county_fips_list):
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1:,} / {len(county_fips_list):,} counties")

            data = self.get_county_summary(
                county_fips,
                as_of_date=as_of_date,
                min_download_speed=min_download_speed,
                min_upload_speed=min_upload_speed
            )

            if data:
                # Extract relevant fields from API response
                # Note: Actual field names will depend on API response structure
                result = {
                    'county_fips': county_fips,
                    'as_of_date': as_of_date,
                    'min_download_speed': min_download_speed,
                    'min_upload_speed': min_upload_speed,
                    'raw_data': data  # Store full response for now
                }
                results.append(result)

        # Create DataFrame
        df = pd.DataFrame(results)

        # Cache the results
        if len(df) > 0:
            df.to_pickle(cache_file)
            print(f"✓ Cached broadband data: {cache_file}")

        print(f"✓ Retrieved broadband data for {len(df):,} counties")
        return df

    def parse_broadband_coverage(self, raw_data):
        """
        Parse broadband coverage data from API response.

        Args:
            raw_data: Raw API response data

        Returns:
            dict: Parsed coverage metrics (percent_covered, provider_count, etc.)
        """
        # This function will need to be customized based on actual API response structure
        # Placeholder implementation
        if not raw_data:
            return {
                'percent_covered': None,
                'provider_count': None,
                'total_locations': None,
                'covered_locations': None
            }

        # Parse based on API response structure
        # Actual implementation will depend on API response format
        return {
            'percent_covered': raw_data.get('percent_covered'),
            'provider_count': raw_data.get('provider_count'),
            'total_locations': raw_data.get('total_locations'),
            'covered_locations': raw_data.get('covered_locations'),
            'raw_data': raw_data
        }


def main():
    """Test the FCC Broadband API client."""
    print("="*80)
    print("FCC BROADBAND DATA COLLECTION API CLIENT TEST")
    print("="*80)

    # Initialize client
    client = FCCBroadbandClient()

    # Test 1: Get available dates
    print("\nTest 1: Get available data collection dates")
    print("-"*80)
    dates = client.get_available_dates()
    if dates:
        print(f"Available dates: {dates}")
        latest_date = dates[-1] if isinstance(dates, list) else None
        print(f"Latest date: {latest_date}")
    else:
        print("No dates available or API key not configured")

    # Test 2: Get data for a single county (Fairfax County, VA: 51059)
    print("\nTest 2: Get broadband data for Fairfax County, VA (FIPS: 51059)")
    print("-"*80)
    test_county = '51059'
    county_data = client.get_county_summary(test_county, min_download_speed=100, min_upload_speed=10)
    if county_data:
        print(f"County data retrieved:")
        print(json.dumps(county_data, indent=2)[:500])  # Print first 500 chars
    else:
        print("No data retrieved for test county")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
