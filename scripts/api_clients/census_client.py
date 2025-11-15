"""
Census ACS (American Community Survey) API Client

This client retrieves data from the Census ACS API.
Primary use: Demographic, household, education, and housing data

Documentation: https://www.census.gov/data/developers/data-sets/acs-5year.html
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CENSUS_API_KEY, CENSUS_API_BASE, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class CensusClient:
    """Client for Census ACS API"""

    def __init__(self, api_key=None):
        """
        Initialize Census API client.

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
            dict: JSON response from API
        """
        params['key'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # Census API returns errors as JSON with single element containing error message
            if len(data) == 1 and isinstance(data[0], str) and 'error' in data[0].lower():
                raise Exception(f"Census API Error: {data[0]}")

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1)
            else:
                raise Exception(f"Census API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_acs5_data(self, year, variables, geography, state_fips=None):
        """
        Get ACS 5-year estimates data.

        Args:
            year: Year of ACS 5-year period end (e.g., 2022 for 2018-2022)
            variables: List of variable codes or comma-separated string
            geography: Geographic level (e.g., 'county:*' for all counties)
            state_fips: State FIPS code (required for county-level data)

        Returns:
            list: API response as list of lists (first row is headers)
        """
        if isinstance(variables, list):
            variables = ','.join(variables)

        url = f"{self.base_url}/{year}/acs/acs5"

        params = {
            'get': variables,
            'for': geography
        }

        # Add state filter if provided
        if state_fips:
            params['in'] = f'state:{state_fips}'

        return self._make_request(url, params)

    def get_acs5_subject_table(self, year, variables, geography, state_fips=None):
        """
        Get ACS 5-year subject table data (S-tables).

        Args:
            year: Year of ACS 5-year period end
            variables: List of variable codes or comma-separated string
            geography: Geographic level
            state_fips: State FIPS code (required for county-level data)

        Returns:
            list: API response as list of lists
        """
        if isinstance(variables, list):
            variables = ','.join(variables)

        url = f"{self.base_url}/{year}/acs/acs5/subject"

        params = {
            'get': variables,
            'for': geography
        }

        if state_fips:
            params['in'] = f'state:{state_fips}'

        return self._make_request(url, params)

    def get_households_with_children(self, year, state_fips=None):
        """
        Get households with children data from Table S1101.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code (None for all states)

        Returns:
            list: API response with household data
        """
        # S1101_C01_002E = Households with one or more people under 18 years
        # S1101_C01_001E = Total households
        variables = ['NAME', 'S1101_C01_002E', 'S1101_C01_001E']

        if state_fips:
            geography = 'county:*'
            return self.get_acs5_subject_table(year, variables, geography, state_fips)
        else:
            # Get for all counties (need to specify state)
            raise ValueError("state_fips required for county-level data")

    def get_poverty_rate(self, year, state_fips=None):
        """
        Get poverty rate data from ACS.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with poverty data
        """
        # S1701_C03_001E = Percent below poverty level
        variables = ['NAME', 'S1701_C03_001E']

        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    def get_education_attainment(self, year, state_fips):
        """
        Get educational attainment data.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with education data
        """
        # S1501 - Educational Attainment
        # S1501_C02_015E = Percent bachelor's degree or higher (25+ population)
        # S1501_C02_014E = Percent associate's degree or higher
        # S1501_C02_009E = Percent high school graduate or higher
        variables = [
            'NAME',
            'S1501_C02_015E',  # Bachelor's or higher
            'S1501_C02_014E',  # Associate's or higher
            'S1501_C02_009E'   # HS diploma or higher
        ]

        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    def get_housing_values(self, year, state_fips):
        """
        Get median housing value and gross rent data.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with housing data
        """
        # B25077_001E = Median value (owner-occupied units)
        # B25064_001E = Median gross rent
        variables = ['NAME', 'B25077_001E', 'B25064_001E']

        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

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
            data: Response data (list)
            filename: Output filename (will be saved in data/raw/census/)
        """
        output_dir = RAW_DATA_DIR / 'census'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the Census client
    print("Testing Census ACS API Client...")
    print("=" * 60)

    client = CensusClient()

    # Test 1: Get households with children for Virginia (2022)
    print("\nTest 1: Households with Children - Virginia (2022)")
    print("-" * 60)
    try:
        data = client.get_households_with_children(2022, state_fips='51')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
        print(f"Headers: {data[0]}")
        if len(data) > 1:
            print(f"Sample row: {data[1]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get poverty rate for Delaware (2022)
    print("\nTest 2: Poverty Rate - Delaware (2022)")
    print("-" * 60)
    try:
        data = client.get_poverty_rate(2022, state_fips='10')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
        parsed = client.parse_response_to_dict(data)
        if parsed:
            print(f"Sample parsed record: {parsed[0]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Get housing values for Maryland (2022)
    print("\nTest 3: Housing Values - Maryland (2022)")
    print("-" * 60)
    try:
        data = client.get_housing_values(2022, state_fips='24')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Census ACS API Client test complete")
