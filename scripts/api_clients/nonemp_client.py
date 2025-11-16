"""
Census Nonemployer Statistics (NES) API Client

This client retrieves data from the Census Nonemployer Statistics API.
Primary use: Data on self-employed individuals and businesses without employees

Documentation: https://www.census.gov/data/developers/data-sets/cbp-nonemp-zbp.html
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CENSUS_API_KEY, CENSUS_API_BASE, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class NonempClient:
    """Client for Census Nonemployer Statistics API"""

    def __init__(self, api_key=None):
        """
        Initialize Census Nonemployer Statistics API client.

        Args:
            api_key: Census API key. If None, uses key from config.
        """
        self.api_key = api_key or CENSUS_API_KEY
        if not self.api_key:
            raise ValueError("Census API key is required")

        self.base_url = CENSUS_API_BASE
        self.session = requests.Session()

    def _make_request(self, url, params, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            url: Full API URL
            params: Dictionary of query parameters
            retries: Number of retries remaining

        Returns:
            list: JSON response from API (list of lists)
        """
        params['key'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # Census API returns errors as JSON with single element containing error message
            if len(data) == 1 and isinstance(data[0], str) and 'error' in data[0].lower():
                raise Exception(f"Census Nonemployer API Error: {data[0]}")

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1)
            else:
                raise Exception(f"Census Nonemployer API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_nonemp_data(self, year, variables, naics='00', state_fips=None):
        """
        Get Nonemployer Statistics data.

        Args:
            year: Year of data (e.g., 2021)
            variables: List of variable codes or comma-separated string
            naics: NAICS code (default '00' for total all industries)
            state_fips: State FIPS code (None for all states)

        Returns:
            list: API response as list of lists (first row is headers)
        """
        if isinstance(variables, list):
            variables = ','.join(variables)

        url = f"{self.base_url}/{year}/nonemp"

        params = {
            'get': variables,
            'for': 'county:*',
            'NAICS2017': naics
        }

        # Add state filter if provided
        if state_fips:
            params['in'] = f'state:{state_fips}'

        return self._make_request(url, params)

    def get_nonemployer_firms(self, year, state_fips=None, naics='00'):
        """
        Get nonemployer firm counts.

        Args:
            year: Year of data
            state_fips: State FIPS code (None for all states)
            naics: NAICS code (default '00' for total)

        Returns:
            list: API response with nonemployer data
        """
        # NONEMP = Number of nonemployer establishments
        # RCPTOT = Total receipts ($1,000)
        variables = ['NAME', 'NONEMP', 'RCPTOT', 'NAICS2017']

        return self.get_nonemp_data(year, variables, naics, state_fips)

    def parse_response_to_dict(self, response):
        """
        Convert Census API response to list of dictionaries.

        Args:
            response: Census API response (list of lists)

        Returns:
            list: List of dictionaries with column names as keys
        """
        if not response or len(response) < 2:
            return []

        headers = response[0]
        data_rows = response[1:]

        return [dict(zip(headers, row)) for row in data_rows]

    def save_response(self, data, filename):
        """
        Save API response to file.

        Args:
            data: Response data (list or dict)
            filename: Output filename (will be saved in data/raw/nonemp/)
        """
        output_dir = RAW_DATA_DIR / 'nonemp'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the Nonemployer client
    print("Testing Census Nonemployer Statistics API Client...")
    print("=" * 60)

    client = NonempClient()

    # Test 1: Get nonemployer firms for Virginia (2021)
    print("\nTest 1: Nonemployer Firms - Virginia (2021)")
    print("-" * 60)
    try:
        data = client.get_nonemployer_firms(2021, state_fips='51')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
        print(f"Headers: {data[0]}")
        if len(data) > 1:
            print(f"Sample row: {data[1]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get nonemployer firms for Delaware (2021)
    print("\nTest 2: Nonemployer Firms - Delaware (2021)")
    print("-" * 60)
    try:
        data = client.get_nonemployer_firms(2021, state_fips='10', naics='00')
        parsed = client.parse_response_to_dict(data)
        if parsed:
            print(f"✓ Retrieved {len(parsed)} records")
            print(f"Sample parsed record: {parsed[0]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Census Nonemployer Statistics API Client test complete")
