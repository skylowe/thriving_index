"""
National Park Service (NPS) API Client

This client retrieves data from the NPS API for national parks and protected areas.
Primary use: Counting national parks and recreation areas by county

Documentation: https://www.nps.gov/subjects/developer/api-documentation.htm
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import NPS_API_KEY, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class NPSClient:
    """Client for National Park Service API"""

    def __init__(self, api_key=None):
        """
        Initialize NPS API client.

        Args:
            api_key: NPS API key. If None, uses key from config.
        """
        self.api_key = api_key or NPS_API_KEY
        if not self.api_key:
            raise ValueError("NPS API key is required. Register at https://www.nps.gov/subjects/developer/get-started.htm")

        self.base_url = 'https://developer.nps.gov/api/v1'
        self.session = requests.Session()

    def _make_request(self, endpoint, params=None, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            endpoint: API endpoint path (e.g., '/parks')
            params: Dictionary of query parameters
            retries: Number of retries remaining

        Returns:
            dict: JSON response from API
        """
        if params is None:
            params = {}

        # Add API key to params
        params['api_key'] = self.api_key

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(endpoint, params, retries - 1)
            else:
                raise Exception(f"NPS API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_parks(self, state_code=None, limit=50, start=0):
        """
        Get parks data from NPS API.

        Args:
            state_code: Two-letter state code (e.g., 'VA') or comma-separated list (e.g., 'VA,MD')
            limit: Number of results per page (max 50)
            start: Starting index for pagination

        Returns:
            dict: API response with parks data
        """
        params = {
            'limit': min(limit, 50),  # NPS API max is 50
            'start': start
        }

        if state_code:
            params['stateCode'] = state_code

        return self._make_request('/parks', params)

    def get_all_parks(self, state_codes=None):
        """
        Get all parks for specified states with pagination.

        Args:
            state_codes: List of two-letter state codes (e.g., ['VA', 'MD'])
                        If None, gets all parks nationwide

        Returns:
            list: List of all park records
        """
        all_parks = []

        if state_codes:
            # Join state codes with comma for API
            state_param = ','.join(state_codes)
        else:
            state_param = None

        # Get first page to determine total
        print(f"  Fetching parks for states: {state_param if state_param else 'ALL'}...")
        first_page = self.get_parks(state_code=state_param, limit=50, start=0)

        if 'data' not in first_page:
            print(f"  Warning: No data in response")
            return []

        all_parks.extend(first_page['data'])
        total = int(first_page.get('total', 0))

        print(f"    Total parks to fetch: {total}")
        print(f"    Retrieved first page: {len(first_page['data'])} parks")

        # Fetch remaining pages
        start = 50
        while len(all_parks) < total:
            page = self.get_parks(state_code=state_param, limit=50, start=start)
            if 'data' in page and page['data']:
                all_parks.extend(page['data'])
                print(f"    Retrieved {len(all_parks)}/{total} parks")
                start += 50
            else:
                break

        print(f"  ✓ Total parks retrieved: {len(all_parks)}")
        return all_parks

    def parse_park_location(self, park):
        """
        Parse location information from park record.

        Args:
            park: Park record dictionary

        Returns:
            dict: Parsed location with lat, lon, states
        """
        location = {
            'park_code': park.get('parkCode', ''),
            'park_name': park.get('fullName', ''),
            'designation': park.get('designation', ''),
            'states': park.get('states', ''),  # Comma-separated list
            'latitude': None,
            'longitude': None
        }

        # Parse coordinates
        if park.get('latitude') and park.get('longitude'):
            try:
                location['latitude'] = float(park['latitude'])
                location['longitude'] = float(park['longitude'])
            except (ValueError, TypeError):
                pass

        return location

    def save_response(self, data, filename):
        """
        Save API response to file.

        Args:
            data: Response data (dict or list)
            filename: Output filename (will be saved in data/raw/nps/)
        """
        output_dir = RAW_DATA_DIR / 'nps'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the NPS client
    print("Testing National Park Service API Client...")
    print("=" * 60)

    client = NPSClient()

    # Test 1: Get parks for Virginia
    print("\nTest 1: Parks in Virginia")
    print("-" * 60)
    try:
        parks = client.get_all_parks(state_codes=['VA'])
        print(f"✓ Retrieved {len(parks)} parks in Virginia")
        if parks:
            print(f"\nSample park:")
            print(f"  Name: {parks[0].get('fullName', 'N/A')}")
            print(f"  Code: {parks[0].get('parkCode', 'N/A')}")
            print(f"  Designation: {parks[0].get('designation', 'N/A')}")
            print(f"  States: {parks[0].get('states', 'N/A')}")
            print(f"  Lat/Lon: {parks[0].get('latitude', 'N/A')}, {parks[0].get('longitude', 'N/A')}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Parse location from first park
    if parks:
        print("\nTest 2: Parse Location")
        print("-" * 60)
        try:
            location = client.parse_park_location(parks[0])
            print(f"✓ Parsed location:")
            for key, value in location.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"✗ Error: {e}")

    # Test 3: Get parks for multiple states (just first page)
    print("\nTest 3: Parks in VA, MD, PA (first page only)")
    print("-" * 60)
    try:
        response = client.get_parks(state_code='VA,MD,PA', limit=10)
        if 'data' in response:
            print(f"✓ Retrieved {len(response['data'])} parks")
            print(f"  Total available: {response.get('total', 'N/A')}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("NPS API Client test complete")
