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
import zipfile

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR, FCC_BB_KEY, FCC_USERNAME


class FCCBroadbandClient:
    """Client for FCC Broadband Data Collection Public Data API"""

    def __init__(self, api_key=None, username=None):
        """
        Initialize FCC Broadband client.

        Args:
            api_key: FCC API hash_value (defaults to FCC_BB_KEY from config)
            username: FCC API username/email (optional, defaults to FCC_USERNAME)
        """
        self.api_key = api_key or FCC_BB_KEY
        # Username should be from FCC User Registration
        self.username = username or FCC_USERNAME
        self.base_url = 'https://broadbandmap.fcc.gov/api/public'  # Per swagger spec
        self.session = requests.Session()

        # Set up authentication headers (per BDC Public Data API swagger spec)
        # IMPORTANT: Custom user-agent required to avoid blocking (per Stack Overflow workaround)
        if self.api_key and self.username:
            self.session.headers.update({
                'username': self.username,
                'hash_value': self.api_key,
                'user-agent': 'python-requests/2.0.0'  # Custom UA to bypass filtering
            })

        # Set up cache directory
        self.cache_dir = RAW_DATA_DIR / 'fcc' / 'api_cache'
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

        Per Swagger spec: GET /map/listAsOfDates
        Requires authentication headers: username, hash_value

        Returns:
            list: Available as-of dates for broadband data
                  Format: [{'data_type': 'availability', 'as_of_date': '2024-06-30'}, ...]
        """
        print("Fetching available data collection dates...")

        if not self.api_key or not self.username:
            raise ValueError("API credentials required. Set FCC_BB_KEY and FCC_USERNAME in .Renviron")

        response = self._make_request('map/listAsOfDates')

        if isinstance(response, dict) and 'data' in response:
            dates = response['data']
            print(f"  Found {len(dates)} available date(s)")

            # Extract just availability dates for easier use
            availability_dates = [item['as_of_date'] for item in dates if item.get('data_type') == 'availability']
            return availability_dates
        else:
            print(f"  Warning: Unexpected response format: {response}")
            return []

    def list_availability_data(self, as_of_date, category='Summary', subcategory=None,
                               technology_type='Fixed Broadband', speed_tier=None):
        """
        Get list of available data files for download.

        Per Swagger spec: GET /map/downloads/listAvailabilityData/{as_of_date}
        Returns file_id values that can be used with download_file()

        Args:
            as_of_date: Data collection date (YYYY-MM-DD format)
            category: 'Summary', 'State', or 'Provider' (default: 'Summary')
            subcategory: Optional subcategory filter
                Options: 'Summary by Geography Type - Census Place',
                        'Summary by Geography Type - Other Geographies', etc.
            technology_type: 'Fixed Broadband', 'Mobile Broadband', or 'Mobile Voice'
            speed_tier: Optional speed tier filter (e.g., '35/3', '7/1')

        Returns:
            list: Available files with metadata
                  Each item: {file_id, category, subcategory, file_name, record_count, ...}
        """
        if not self.api_key or not self.username:
            raise ValueError("API credentials required. Set FCC_BB_KEY and FCC_USERNAME in .Renviron")

        endpoint = f'map/downloads/listAvailabilityData/{as_of_date}'
        params = {}

        if category:
            params['category'] = category
        if subcategory:
            params['subcategory'] = subcategory
        if technology_type:
            params['technology_type'] = technology_type
        if speed_tier:
            params['speed_tier'] = speed_tier

        print(f"Listing availability data for {as_of_date}...")
        if category:
            print(f"  Category: {category}")
        if subcategory:
            print(f"  Subcategory: {subcategory}")

        response = self._make_request(endpoint, params=params)

        if isinstance(response, dict) and 'data' in response:
            files = response['data']
            print(f"  Found {len(files)} file(s)")
            return files
        else:
            print(f"  Warning: Unexpected response format")
            return []

    def download_file(self, data_type, file_id, output_path):
        """
        Download a data file.

        Per Swagger spec: GET /map/downloads/downloadFile/{data_type}/{file_id}
        Returns binary file content (CSV, ZIP, etc.)

        Args:
            data_type: Type of data ('availability' or 'challenge')
            file_id: File ID from list_availability_data()
            output_path: Path to save the downloaded file

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key or not self.username:
            raise ValueError("API credentials required. Set FCC_BB_KEY and FCC_USERNAME in .Renviron")

        endpoint = f'map/downloads/downloadFile/{data_type}/{file_id}'

        print(f"Downloading file ID {file_id}...")

        try:
            # Make request with streaming for large files
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, timeout=TIMEOUT, stream=True)
            response.raise_for_status()

            # Save the file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write in chunks for memory efficiency
            total_size = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)

            # Convert to MB
            total_mb = total_size / (1024 * 1024)
            print(f"  ✓ Downloaded {total_mb:.2f} MB to: {output_path}")
            return True

        except Exception as e:
            print(f"  Error downloading file {file_id}: {str(e)}")
            return False

    def download_county_summary(self, as_of_date=None, state_fips_list=None,
                                min_download_mbps=100, min_upload_mbps=10, use_cache=True):
        """
        Download and process county-level broadband summary via API.

        This method:
        1. Lists available files via API
        2. Finds the county summary file
        3. Downloads it via API
        4. Processes and filters the data

        Args:
            as_of_date: Data collection date (YYYY-MM-DD) or None for latest
            state_fips_list: List of 2-digit state FIPS codes to filter
            min_download_mbps: Minimum download speed (default 100)
            min_upload_mbps: Minimum upload speed (default 10)
            use_cache: Whether to use cached download

        Returns:
            DataFrame: County-level broadband availability
        """
        print("\n" + "="*80)
        print("FCC BROADBAND API DOWNLOAD")
        print("="*80)

        # Get available dates if not specified
        if not as_of_date:
            print("Fetching latest available date...")
            dates = self.get_available_dates()
            if dates:
                as_of_date = dates[-1]  # Use most recent
                print(f"  Using latest date: {as_of_date}")
            else:
                raise ValueError("No data dates available from API")

        # Check cache
        cache_file = self.cache_dir / f'county_summary_{as_of_date}.csv'
        if use_cache and cache_file.exists():
            print(f"\nLoading from cache: {cache_file}")
            df = pd.read_csv(cache_file, dtype={'county_fips': str})
            print(f"✓ Loaded {len(df):,} records from cache")

            # Apply filtering if needed
            if state_fips_list:
                df = df[df['county_fips'].str[:2].isin(state_fips_list)]
                print(f"✓ Filtered to {len(state_fips_list)} states: {len(df):,} counties")

            return df

        # List available files
        print(f"\nListing available county summary files...")
        files = self.list_availability_data(
            as_of_date=as_of_date,
            category='Summary',
            subcategory='Summary by Geography Type - Other Geographies',
            technology_type='Fixed Broadband'
        )

        # Find geography summary file (contains county data)
        geo_file = None
        for file in files:
            file_name = file.get('file_name', '').lower()
            # Look for "summary_by_geography" file (contains all geography types including county)
            if 'summary_by_geography' in file_name and '_us_' in file_name:
                geo_file = file
                print(f"\n  Found geography summary file: {file['file_name']}")
                print(f"    File ID: {file['file_id']}")
                print(f"    Records: {file.get('record_count', 'unknown')}")
                break

        if not geo_file:
            raise FileNotFoundError(f"Geography summary file not found for {as_of_date}")

        # Download the file (it's a ZIP)
        print(f"\nDownloading geography summary file (ZIP)...")
        zip_path = cache_file.parent / f"geo_summary_{as_of_date}.zip"
        success = self.download_file(
            data_type='availability',
            file_id=geo_file['file_id'],
            output_path=zip_path
        )

        if not success:
            raise Exception("Failed to download geography summary file")

        # Extract the ZIP file
        print(f"\nExtracting ZIP file...")
        extract_dir = cache_file.parent / 'extracted'
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            file_list = zip_ref.namelist()
            print(f"  Extracted: {file_list[0]}")

        # Read the extracted CSV
        csv_file = extract_dir / file_list[0]
        print(f"\nLoading extracted CSV...")
        df = pd.read_csv(csv_file, low_memory=False)
        print(f"  ✓ Loaded {len(df):,} total records")

        # Filter to county records only
        print(f"\nFiltering to county-level data...")
        counties = df[
            (df['geography_type'] == 'County') &
            (df['technology'] == 'Any Technology') &
            (df['area_data_type'] == 'Total') &
            (df['biz_res'] == 'R')  # Residential (avoids duplication with Business)
        ].copy()

        print(f"  ✓ Found {len(counties):,} counties")

        # Extract county FIPS from geography_id
        counties['county_fips'] = counties['geography_id'].astype(str).str.zfill(5)
        counties['state_fips'] = counties['county_fips'].str[:2]

        # Apply state filtering if needed
        if state_fips_list:
            counties = counties[counties['state_fips'].isin(state_fips_list)]
            print(f"  ✓ Filtered to {len(state_fips_list)} states: {len(counties):,} counties")

        # Select and rename columns for clarity
        result = counties[[
            'county_fips',
            'geography_desc',
            'total_units',
            'speed_100_20'
        ]].copy()

        result = result.rename(columns={
            'geography_desc': 'county_name',
            'total_units': 'total_locations',
            'speed_100_20': 'percent_covered_100_20'
        })

        # Convert percent to actual percentage (it's a decimal 0-1)
        result['percent_covered_100_20'] = result['percent_covered_100_20'] * 100

        # Cache the processed result
        result.to_csv(cache_file, index=False)
        print(f"\n✓ Cached processed data: {cache_file}")

        return result


def main():
    """Test the FCC Broadband API client."""
    print("="*80)
    print("FCC BROADBAND DATA COLLECTION API CLIENT TEST")
    print("="*80)

    try:
        # Initialize client
        client = FCCBroadbandClient()

        # Test 1: Get available dates
        print("\nTest 1: Get available data collection dates")
        print("-"*80)

        try:
            dates = client.get_available_dates()
            if dates:
                print(f"✓ Available dates: {dates}")
                latest_date = dates[-1]
                print(f"✓ Latest date: {latest_date}")
            else:
                print("⚠ No dates available")
                return

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            print("\nNote: This requires valid FCC API credentials (FCC_BB_KEY and FCC_USERNAME)")
            print("      Set these in your .Renviron file or environment variables")
            return

        # Test 2: List available data files
        print("\nTest 2: List county summary files")
        print("-"*80)

        try:
            files = client.list_availability_data(
                as_of_date=latest_date,
                category='Summary',
                subcategory='Summary by Geography Type - Other Geographies',
                technology_type='Fixed Broadband'
            )

            if files:
                print(f"\n✓ Found {len(files)} files")
                print(f"\nCounty summary files:")
                for f in files:
                    if 'county' in f.get('file_name', '').lower():
                        print(f"  - File ID: {f.get('file_id')}")
                        print(f"    Name: {f.get('file_name')}")
                        print(f"    Records: {f.get('record_count')}")
                        print()
            else:
                print("⚠ No files found")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return

        # Test 3: Download county summary (for 2 states only as test)
        print("\nTest 3: Download and process county summary (VA, MD)")
        print("-"*80)

        try:
            test_states = ['51', '24']  # VA, MD
            df = client.download_county_summary(
                as_of_date=latest_date,
                state_fips_list=test_states,
                use_cache=True
            )

            print(f"\n✓ SUCCESS - Retrieved {len(df):,} counties")
            print(f"\nColumn names:")
            print(f"  {list(df.columns)}")
            print(f"\nSample data (first 5 rows):")
            print(df.head().to_string(index=False))

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
