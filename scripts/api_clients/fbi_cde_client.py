"""
FBI Crime Data Explorer API Client

This client retrieves summarized crime data from the FBI Crime Data Explorer API
for law enforcement agencies using ORI codes.

API Documentation: https://api.usa.gov/crime/fbi/cde/
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import FBI_UCR_KEY, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class FBICrimeClient:
    """Client for FBI Crime Data Explorer API"""

    def __init__(self, api_key=None, cache_dir=None):
        """
        Initialize FBI Crime Data Explorer API client.

        Args:
            api_key: FBI API key. If None, uses key from config.
            cache_dir: Directory for caching API responses. If None, uses default.
        """
        self.api_key = api_key or FBI_UCR_KEY
        if not self.api_key:
            raise ValueError("FBI_UCR_KEY is required")

        self.base_url = "https://api.usa.gov/crime/fbi/cde"
        self.session = requests.Session()

        # Set up cache directory
        if cache_dir is None:
            self.cache_dir = RAW_DATA_DIR / 'fbi_cde'
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Track API calls
        self.api_calls_made = 0

    def _get_cache_path(self, ori, offense, from_date, to_date):
        """
        Get the cache file path for a specific request.

        Args:
            ori: ORI code
            offense: 'V' for violent, 'P' for property
            from_date: Start date (MM-YYYY)
            to_date: End date (MM-YYYY)

        Returns:
            Path: Path to cache file
        """
        # Create filename from parameters
        offense_name = 'violent' if offense == 'V' else 'property'
        filename = f"{ori}_{offense_name}_{from_date}_{to_date}.json"
        filename = filename.replace('-', '_')
        return self.cache_dir / filename

    def _load_from_cache(self, cache_path):
        """
        Load data from cache file if it exists.

        Args:
            cache_path: Path to cache file

        Returns:
            dict or None: Cached data if exists, None otherwise
        """
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cache from {cache_path}: {e}")
                return None
        return None

    def _save_to_cache(self, cache_path, data):
        """
        Save data to cache file.

        Args:
            cache_path: Path to cache file
            data: Data to cache
        """
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache to {cache_path}: {e}")

    def _make_request(self, endpoint, params, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            endpoint: API endpoint path
            params: Dictionary of query parameters
            retries: Number of retries remaining

        Returns:
            dict: JSON response from API or None if failed
        """
        # Add API key to params
        params['API_KEY'] = self.api_key

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=TIMEOUT
            )

            # Track API call
            self.api_calls_made += 1

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
                print(f"FBI API request failed after {MAX_RETRIES} attempts: {str(e)}")
                return None

    def get_summarized_data(self, ori, offense, from_date, to_date, use_cache=True):
        """
        Get summarized crime data for a specific agency and offense type.

        Args:
            ori: 7-character ORI code (e.g., 'VA0010100')
            offense: Offense type - 'V' for violent crime, 'P' for property crime
            from_date: Start date in format 'MM-YYYY' (e.g., '01-2022')
            to_date: End date in format 'MM-YYYY' (e.g., '12-2022')
            use_cache: Whether to use cached data if available

        Returns:
            dict or None: Crime data or None if request fails
        """
        # Validate offense type
        if offense not in ['V', 'P']:
            raise ValueError(f"Invalid offense type: {offense}. Must be 'V' or 'P'")

        # Check cache first
        cache_path = self._get_cache_path(ori, offense, from_date, to_date)
        if use_cache:
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data

        # Build endpoint
        endpoint = f"/summarized/agency/{ori}/{offense}"

        # Build query parameters
        params = {
            'from': from_date,
            'to': to_date
        }

        # Make request
        data = self._make_request(endpoint, params)

        # Cache the result (even if None/error)
        if use_cache:
            self._save_to_cache(cache_path, data)

        return data

    def get_violent_crime(self, ori, from_date, to_date, use_cache=True):
        """
        Get violent crime data for a specific agency.

        Args:
            ori: 7-character ORI code
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'
            use_cache: Whether to use cached data

        Returns:
            dict or None: Violent crime data or None if request fails
        """
        return self.get_summarized_data(ori, 'V', from_date, to_date, use_cache)

    def get_property_crime(self, ori, from_date, to_date, use_cache=True):
        """
        Get property crime data for a specific agency.

        Args:
            ori: 7-character ORI code
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'
            use_cache: Whether to use cached data

        Returns:
            dict or None: Property crime data or None if request fails
        """
        return self.get_summarized_data(ori, 'P', from_date, to_date, use_cache)

    def get_all_crime_data(self, ori, from_date, to_date, use_cache=True):
        """
        Get both violent and property crime data for a specific agency.

        Args:
            ori: 7-character ORI code
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'
            use_cache: Whether to use cached data

        Returns:
            dict: Dictionary with 'violent' and 'property' keys containing crime data
        """
        return {
            'violent': self.get_violent_crime(ori, from_date, to_date, use_cache),
            'property': self.get_property_crime(ori, from_date, to_date, use_cache)
        }


if __name__ == '__main__':
    # Test the FBI CDE API client
    import os

    api_key = os.getenv('FBI_UCR_KEY')
    if not api_key:
        print("Error: FBI_UCR_KEY not found in environment")
        exit(1)

    client = FBICrimeClient(api_key=api_key)

    # Test with a Virginia agency (small test)
    print("\n" + "="*60)
    print("Testing FBI Crime Data Explorer API Client")
    print("="*60)

    test_ori = 'VA0010100'  # Example Virginia ORI
    print(f"\nTesting with ORI: {test_ori}")
    print(f"Date range: 01-2022 to 12-2022")

    print("\nFetching violent crime data...")
    violent = client.get_violent_crime(test_ori, '01-2022', '12-2022')
    if violent:
        print(f"✓ Violent crime data retrieved")
        # Print summary if data exists
        if 'data' in violent:
            print(f"  Records: {len(violent.get('data', []))}")
    else:
        print(f"✗ No violent crime data")

    print("\nFetching property crime data...")
    property_crime = client.get_property_crime(test_ori, '01-2022', '12-2022')
    if property_crime:
        print(f"✓ Property crime data retrieved")
        if 'data' in property_crime:
            print(f"  Records: {len(property_crime.get('data', []))}")
    else:
        print(f"✗ No property crime data")

    print(f"\nTotal API calls made: {client.api_calls_made}")
    print(f"Cache directory: {client.cache_dir}")
    print("\nTest complete!")
