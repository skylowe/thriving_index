"""
Census County Business Patterns (CBP) API Client

This client retrieves data from the Census County Business Patterns API.
Primary use: Business establishments and employment data by industry

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


class CBPClient:
    """Client for Census County Business Patterns API"""

    def __init__(self, api_key=None):
        """
        Initialize Census CBP API client.

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
                raise Exception(f"Census CBP API Error: {data[0]}")

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1)
            else:
                raise Exception(f"Census CBP API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_cbp_data(self, year, variables, naics='00', state_fips=None):
        """
        Get County Business Patterns data.

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

        url = f"{self.base_url}/{year}/cbp"

        params = {
            'get': variables,
            'for': 'county:*',
            'NAICS2017': naics
        }

        # Add state filter if provided
        if state_fips:
            params['in'] = f'state:{state_fips}'

        return self._make_request(url, params)

    def get_establishments(self, year, state_fips=None, naics='00'):
        """
        Get establishment counts from CBP.

        Args:
            year: Year of data
            state_fips: State FIPS code (None for all states)
            naics: NAICS code (default '00' for total)

        Returns:
            list: API response with establishment data
        """
        # ESTAB = Number of establishments
        # EMP = Total mid-March employment
        variables = ['NAME', 'ESTAB', 'EMP', 'NAICS2017']

        return self.get_cbp_data(year, variables, naics, state_fips)

    def get_industry_employment(self, year, state_fips, naics_codes=None):
        """
        Get employment by industry (for diversity calculations).

        Args:
            year: Year of data
            state_fips: State FIPS code
            naics_codes: List of 2-digit NAICS codes (None for all 2-digit industries)

        Returns:
            dict: Dictionary mapping NAICS code to data
        """
        if naics_codes is None:
            # Major 2-digit NAICS industry sectors
            naics_codes = [
                '11',  # Agriculture, Forestry, Fishing and Hunting
                '21',  # Mining, Quarrying, and Oil and Gas Extraction
                '22',  # Utilities
                '23',  # Construction
                '31-33',  # Manufacturing
                '42',  # Wholesale Trade
                '44-45',  # Retail Trade
                '48-49',  # Transportation and Warehousing
                '51',  # Information
                '52',  # Finance and Insurance
                '53',  # Real Estate and Rental and Leasing
                '54',  # Professional, Scientific, and Technical Services
                '55',  # Management of Companies and Enterprises
                '56',  # Administrative and Support and Waste Management
                '61',  # Educational Services
                '62',  # Health Care and Social Assistance
                '71',  # Arts, Entertainment, and Recreation
                '72',  # Accommodation and Food Services
                '81',  # Other Services (except Public Administration)
            ]

        results = {}
        variables = ['NAME', 'EMP', 'ESTAB', 'NAICS2017']

        for naics in naics_codes:
            try:
                data = self.get_cbp_data(year, variables, naics, state_fips)
                results[naics] = data
                print(f"  Retrieved data for NAICS {naics}: {len(data) - 1} counties")
            except Exception as e:
                print(f"  Warning: Could not retrieve NAICS {naics}: {e}")
                results[naics] = None

        return results

    def get_healthcare_employment(self, year, state_fips):
        """
        Get healthcare employment data from CBP for healthcare access calculation.

        Collects employment data for:
        - NAICS 621: Ambulatory Health Care Services (physician offices, dentist offices, etc.)
        - NAICS 622: Hospitals

        Args:
            year: Year of data
            state_fips: State FIPS code

        Returns:
            dict: Dictionary with 'ambulatory' and 'hospitals' data
        """
        variables = ['NAME', 'EMP', 'ESTAB', 'NAICS2017']

        results = {}

        # Get ambulatory healthcare services (NAICS 621)
        try:
            data_621 = self.get_cbp_data(year, variables, '621', state_fips)
            results['ambulatory'] = data_621
            print(f"  Retrieved NAICS 621 (Ambulatory): {len(data_621) - 1} counties")
        except Exception as e:
            print(f"  Warning: Could not retrieve NAICS 621: {e}")
            results['ambulatory'] = None

        # Get hospitals (NAICS 622)
        try:
            data_622 = self.get_cbp_data(year, variables, '622', state_fips)
            results['hospitals'] = data_622
            print(f"  Retrieved NAICS 622 (Hospitals): {len(data_622) - 1} counties")
        except Exception as e:
            print(f"  Warning: Could not retrieve NAICS 622: {e}")
            results['hospitals'] = None

        return results

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
            filename: Output filename (will be saved in data/raw/cbp/)
        """
        output_dir = RAW_DATA_DIR / 'cbp'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the CBP client
    print("Testing Census County Business Patterns API Client...")
    print("=" * 60)

    client = CBPClient()

    # Test 1: Get establishments for Virginia (2021)
    print("\nTest 1: Establishments - Virginia (2021)")
    print("-" * 60)
    try:
        data = client.get_establishments(2021, state_fips='51')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
        print(f"Headers: {data[0]}")
        if len(data) > 1:
            print(f"Sample row: {data[1]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get total establishments for Delaware (2021)
    print("\nTest 2: Total Establishments - Delaware (2021)")
    print("-" * 60)
    try:
        data = client.get_establishments(2021, state_fips='10', naics='00')
        parsed = client.parse_response_to_dict(data)
        if parsed:
            print(f"✓ Retrieved {len(parsed)} records")
            print(f"Sample parsed record: {parsed[0]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Get industry employment for Maryland (2021) - just a few sectors
    print("\nTest 3: Industry Employment - Maryland (2021, sample sectors)")
    print("-" * 60)
    try:
        test_naics = ['23', '42', '62']  # Construction, Wholesale, Healthcare
        results = client.get_industry_employment(2021, state_fips='24', naics_codes=test_naics)
        print(f"✓ Retrieved industry data for {len(results)} NAICS codes")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Census CBP API Client test complete")
