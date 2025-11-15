"""
BLS (Bureau of Labor Statistics) QCEW API Client

This client retrieves data from the BLS Quarterly Census of Employment and Wages API.
Primary use: Private sector employment and wage data

Documentation: https://www.bls.gov/developers/
QCEW Series ID Format: ENUCS + state FIPS + county FIPS + ownership + aggregate level + industry
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import BLS_API_KEY, BLS_API_URL, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class BLSClient:
    """Client for BLS QCEW API"""

    def __init__(self, api_key=None):
        """
        Initialize BLS API client.

        Args:
            api_key: BLS API key. If None, uses key from config.
        """
        self.api_key = api_key or BLS_API_KEY
        if not self.api_key:
            raise ValueError("BLS API key is required")

        self.base_url = BLS_API_URL
        self.session = requests.Session()

    def _make_request(self, series_ids, start_year, end_year, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            series_ids: List of BLS series IDs
            start_year: Start year
            end_year: End year
            retries: Number of retries remaining

        Returns:
            dict: JSON response from API
        """
        # BLS API v2 limits to 50 series per request with registered key
        if len(series_ids) > 50:
            raise ValueError("BLS API limited to 50 series per request")

        payload = {
            'seriesid': series_ids,
            'startyear': str(start_year),
            'endyear': str(end_year),
            'registrationkey': self.api_key
        }

        try:
            response = self.session.post(
                self.base_url,
                json=payload,
                headers={'Content-type': 'application/json'},
                timeout=TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            # Check for BLS API errors
            if data.get('status') != 'REQUEST_SUCCEEDED':
                error_msg = data.get('message', ['Unknown error'])[0]
                raise Exception(f"BLS API Error: {error_msg}")

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(series_ids, start_year, end_year, retries - 1)
            else:
                raise Exception(f"BLS API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def build_qcew_series_id(self, state_fips, county_fips, data_type='employment',
                             ownership='5', industry='10'):
        """
        Build QCEW series ID.

        Args:
            state_fips: State FIPS code (2 digits)
            county_fips: County FIPS code (3 digits)
            data_type: 'employment' or 'wages'
            ownership: '5' for private, '1' for federal govt, etc.
            industry: '10' for total all industries

        Returns:
            str: BLS series ID

        Series ID format: ENU + ST + CNTY + ownership + data_type_code + industry
        - ENU: QCEW program prefix
        - ownership: 5 = private
        - data_type_code: 5 = employment (annual avg), 6 = total wages
        - aggregate level: 10 = total
        - industry: Industry code (10 = all industries)
        """
        # Ensure FIPS codes are properly formatted
        state_fips = str(state_fips).zfill(2)
        county_fips = str(county_fips).zfill(3)

        # Data type code
        if data_type == 'employment':
            dt_code = '5'  # Annual average employment
        elif data_type == 'wages':
            dt_code = '6'  # Total quarterly wages
        else:
            raise ValueError(f"Invalid data_type: {data_type}")

        # Build series ID: ENU + state + county + ownership + dt_code + aggregate + industry
        series_id = f"ENU{state_fips}{county_fips}{ownership}{dt_code}{industry}"

        return series_id

    def get_county_data(self, state_fips, county_fips, start_year, end_year,
                       data_types=['employment', 'wages']):
        """
        Get QCEW data for a specific county.

        Args:
            state_fips: State FIPS code
            county_fips: County FIPS code
            start_year: Start year
            end_year: End year
            data_types: List of data types to retrieve

        Returns:
            dict: API response
        """
        series_ids = []
        for dt in data_types:
            series_id = self.build_qcew_series_id(state_fips, county_fips, data_type=dt)
            series_ids.append(series_id)

        return self._make_request(series_ids, start_year, end_year)

    def get_state_counties_data(self, state_fips, county_fips_list, start_year, end_year,
                                data_type='employment'):
        """
        Get QCEW data for multiple counties in batches.

        Args:
            state_fips: State FIPS code
            county_fips_list: List of county FIPS codes
            start_year: Start year
            end_year: End year
            data_type: 'employment' or 'wages'

        Returns:
            list: List of API responses (one per batch of 50 counties)
        """
        all_responses = []

        # Process in batches of 50 (API limit)
        for i in range(0, len(county_fips_list), 50):
            batch = county_fips_list[i:i + 50]
            series_ids = [
                self.build_qcew_series_id(state_fips, county_fips, data_type=data_type)
                for county_fips in batch
            ]

            print(f"Fetching batch {i // 50 + 1} ({len(series_ids)} series)...")
            response = self._make_request(series_ids, start_year, end_year)
            all_responses.append(response)

        return all_responses

    def save_response(self, data, filename):
        """
        Save API response to file.

        Args:
            data: Response data (dict)
            filename: Output filename (will be saved in data/raw/bls/)
        """
        output_dir = RAW_DATA_DIR / 'bls'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the BLS client
    print("Testing BLS QCEW API Client...")
    print("=" * 60)

    client = BLSClient()

    # Test 1: Build series ID
    print("\nTest 1: Build QCEW Series ID")
    print("-" * 60)
    series_id_emp = client.build_qcew_series_id('51', '001', data_type='employment')
    series_id_wage = client.build_qcew_series_id('51', '001', data_type='wages')
    print(f"Employment series: {series_id_emp}")
    print(f"Wages series: {series_id_wage}")
    print("✓ Series IDs built successfully")

    # Test 2: Get data for one county (Accomack County, VA - FIPS 001)
    print("\nTest 2: Get Employment Data for Accomack County, VA (2020-2022)")
    print("-" * 60)
    try:
        data = client.get_county_data('51', '001', 2020, 2022, data_types=['employment'])
        if data['status'] == 'REQUEST_SUCCEEDED':
            series_count = len(data['Results']['series'])
            print(f"✓ Retrieved data for {series_count} series")
            if series_count > 0:
                first_series = data['Results']['series'][0]
                print(f"Series ID: {first_series['seriesID']}")
                print(f"Data points: {len(first_series['data'])}")
        else:
            print(f"✗ Request failed: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("BLS QCEW API Client test complete")
