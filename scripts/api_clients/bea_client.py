"""
BEA (Bureau of Economic Analysis) Regional API Client

This client retrieves data from the BEA Regional Economic Accounts API.
Primary use: CAINC5 table (Personal Income by Major Component)

Documentation: https://apps.bea.gov/api/
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import BEA_API_KEY, BEA_API_URL, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class BEAClient:
    """Client for BEA Regional Economic Accounts API"""

    def __init__(self, api_key=None):
        """
        Initialize BEA API client.

        Args:
            api_key: BEA API key. If None, uses key from config.
        """
        self.api_key = api_key or BEA_API_KEY
        if not self.api_key:
            raise ValueError("BEA API key is required")

        self.base_url = BEA_API_URL
        self.session = requests.Session()

    def _make_request(self, params, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            params: Dictionary of API parameters
            retries: Number of retries remaining

        Returns:
            dict: JSON response from API
        """
        params['UserID'] = self.api_key
        params['ResultFormat'] = 'JSON'

        try:
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            # Check for BEA API errors
            if 'BEAAPI' in data and 'Error' in data['BEAAPI']:
                error_msg = data['BEAAPI']['Error'].get('APIErrorDescription', 'Unknown error')
                raise Exception(f"BEA API Error: {error_msg}")

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(params, retries - 1)
            else:
                raise Exception(f"BEA API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_dataset_list(self):
        """
        Get list of available datasets.

        Returns:
            list: List of available datasets
        """
        params = {'method': 'GETDATASETLIST'}
        response = self._make_request(params)
        return response['BEAAPI']['Results']['Dataset']

    def get_parameter_list(self, dataset_name):
        """
        Get list of parameters for a dataset.

        Args:
            dataset_name: Name of dataset (e.g., 'Regional')

        Returns:
            list: List of parameters
        """
        params = {
            'method': 'GETPARAMETERLIST',
            'datasetname': dataset_name
        }
        response = self._make_request(params)
        return response['BEAAPI']['Results']['Parameter']

    def get_cainc5_data(self, year, line_code, state_fips_list=None):
        """
        Get CAINC5 table data (Personal Income by Major Component).

        Args:
            year: Year or comma-separated years (e.g., '2020' or '2019,2020,2021')
            line_code: BEA line code (e.g., '10' for total employment, '40' for DIR income)
            state_fips_list: Optional list of state FIPS codes to filter results

        Returns:
            dict: API response with data
        """
        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC5N',
            'LineCode': str(line_code),
            'GeoFips': 'COUNTY',  # Get all counties
            'Year': str(year)
        }

        response = self._make_request(params)

        # Filter by state if requested
        if state_fips_list and 'BEAAPI' in response and 'Results' in response['BEAAPI']:
            if 'Data' in response['BEAAPI']['Results']:
                data = response['BEAAPI']['Results']['Data']
                # Filter to only counties in specified states
                filtered_data = [
                    row for row in data
                    if row['GeoFips'][:2] in state_fips_list
                ]
                response['BEAAPI']['Results']['Data'] = filtered_data

        return response

    def get_employment_data(self, years, state_fips_list=None):
        """
        Get total employment data (Line Code 10) for calculating growth.

        Args:
            years: List of years or comma-separated string
            state_fips_list: Optional list of state FIPS codes to filter results

        Returns:
            dict: API response
        """
        if isinstance(years, list):
            years = ','.join(str(y) for y in years)

        return self.get_cainc5_data(years, line_code=10, state_fips_list=state_fips_list)

    def get_dir_income_data(self, years, state_fips_list=None):
        """
        Get Dividends, Interest, and Rent income data (Line Code 46).

        Args:
            years: List of years or comma-separated string
            state_fips_list: Optional list of state FIPS codes to filter results

        Returns:
            dict: API response
        """
        if isinstance(years, list):
            years = ','.join(str(y) for y in years)

        return self.get_cainc5_data(years, line_code=46, state_fips_list=state_fips_list)

    def get_cainc4_data(self, year, line_code, state_fips_list=None):
        """
        Get CAINC4 table data (Personal income and employment by major component).

        Args:
            year: Year or comma-separated years (e.g., '2020' or '2019,2020,2021')
            line_code: BEA line code (e.g., '72' for nonfarm proprietors income, '71' for farm proprietors income)
            state_fips_list: Optional list of state FIPS codes to filter results

        Returns:
            dict: API response with data
        """
        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC4',
            'LineCode': str(line_code),
            'GeoFips': 'COUNTY',  # Get all counties
            'Year': str(year)
        }

        response = self._make_request(params)

        # Filter by state if requested
        if state_fips_list and 'BEAAPI' in response and 'Results' in response['BEAAPI']:
            if 'Data' in response['BEAAPI']['Results']:
                data = response['BEAAPI']['Results']['Data']
                # Filter to only counties in specified states
                filtered_data = [
                    row for row in data
                    if row['GeoFips'][:2] in state_fips_list
                ]
                response['BEAAPI']['Results']['Data'] = filtered_data

        return response

    def get_proprietors_data(self, years, state_fips_list=None, include_farm=False):
        """
        Get proprietors income data (nonfarm and optionally farm).

        Note: County-level proprietors employment is not available via BEA API.
        This method returns proprietors INCOME as a proxy for proprietorship activity.

        Args:
            years: List of years or comma-separated string
            state_fips_list: Optional list of state FIPS codes to filter results
            include_farm: If True, also get farm proprietors data

        Returns:
            dict: API response with nonfarm proprietors income (and farm if requested)
        """
        if isinstance(years, list):
            years = ','.join(str(y) for y in years)

        # Get nonfarm proprietors income (Line Code 72)
        nonfarm_response = self.get_cainc4_data(years, line_code=72, state_fips_list=state_fips_list)

        if include_farm:
            # Also get farm proprietors income (Line Code 71)
            farm_response = self.get_cainc4_data(years, line_code=71, state_fips_list=state_fips_list)
            # Combine the responses
            return {
                'nonfarm': nonfarm_response,
                'farm': farm_response
            }

        return nonfarm_response

    def save_response(self, data, filename):
        """
        Save API response to file.

        Args:
            data: Response data (dict)
            filename: Output filename (will be saved in data/raw/bea/)
        """
        output_dir = RAW_DATA_DIR / 'bea'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the BEA client
    print("Testing BEA API Client...")
    print("=" * 60)

    client = BEAClient()

    # Test 1: Get datasets
    print("\nTest 1: Available Datasets")
    print("-" * 60)
    try:
        datasets = client.get_dataset_list()
        for ds in datasets[:3]:  # Show first 3
            print(f"- {ds['DatasetName']}: {ds['DatasetDescription']}")
        print("✓ Dataset list retrieved successfully")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get employment data for Virginia (2020-2022)
    print("\nTest 2: Employment Data for Virginia (2020-2022)")
    print("-" * 60)
    try:
        data = client.get_employment_data('2020,2021,2022', state_fips_list=['51'])
        results = data['BEAAPI']['Results']['Data']
        print(f"✓ Retrieved {len(results)} records")
        print(f"Sample record: {results[0] if results else 'No data'}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("BEA API Client test complete")
