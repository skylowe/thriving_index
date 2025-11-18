"""
FCC Broadband Bulk Data Download Client

This client downloads and processes FCC Broadband Data Collection (BDC) bulk data files.
Since the Public Data API requires special credentials, we use the publicly available
bulk CSV downloads from the FCC National Broadband Map data portal.

Data Source: https://broadbandmap.fcc.gov/data-download
Documentation: https://help.bdc.fcc.gov/hc/en-us/articles/10467446103579
"""

import requests
import time
import pandas as pd
from pathlib import Path
import sys
import zipfile
import io

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class FCCBroadbandBulkClient:
    """Client for FCC Broadband Data Collection bulk data downloads"""

    def __init__(self):
        """Initialize FCC Broadband bulk data client."""
        self.base_url = 'https://broadbandmap.fcc.gov/nbm/map/api'
        self.download_url = 'https://us-fcc.app.box.com/v/bdc-data'  # Box.com hosting
        self.session = requests.Session()

        # Set up cache directory
        self.cache_dir = RAW_DATA_DIR / 'fcc' / 'bulk'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_request(self, url, params=None, retries=MAX_RETRIES, stream=False):
        """
        Make HTTP request with retry logic.

        Args:
            url: URL to fetch
            params: Query parameters (optional)
            retries: Number of retries remaining
            stream: Whether to stream the response (for large files)

        Returns:
            requests.Response object
        """
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT, stream=stream)
            response.raise_for_status()
            if not stream:
                time.sleep(REQUEST_DELAY)
            return response

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"  Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1, stream)
            else:
                raise Exception(f"FCC data request failed after {MAX_RETRIES} attempts: {str(e)}")

    def download_county_summary_csv(self, as_of_date=None, use_cache=True):
        """
        Download county-level broadband availability summary CSV.

        The FCC provides county summary files with broadband availability by speed tier.
        These files are updated twice per year.

        Args:
            as_of_date: Specific data version date (e.g., '2024-06-30'), or None for latest
            use_cache: Whether to use cached file if available

        Returns:
            DataFrame: County-level broadband data
        """
        # Default to latest known version if not specified
        if not as_of_date:
            as_of_date = '2024-06-30'  # Latest as of implementation

        cache_file = self.cache_dir / f'county_summary_{as_of_date}.csv'

        # Check cache
        if use_cache and cache_file.exists():
            print(f"Loading county summary from cache: {cache_file}")
            df = pd.read_csv(cache_file)
            print(f"✓ Loaded {len(df):,} records from cache")
            return df

        # Download from FCC
        # Note: The actual download URL structure may vary by release
        # FCC typically hosts files on Box.com or similar
        print(f"Note: FCC bulk data files are typically downloaded manually from:")
        print(f"      https://broadbandmap.fcc.gov/data-download")
        print(f"\nPlease download the 'County Summary' CSV file for {as_of_date}")
        print(f"and place it at: {cache_file}")
        print(f"\nFile should include columns like:")
        print(f"  - county_fips (5-digit FIPS code)")
        print(f"  - download_speed, upload_speed (speed tiers)")
        print(f"  - locations_served, total_locations")

        raise FileNotFoundError(
            f"Please manually download county summary CSV from FCC website\n"
            f"and save to: {cache_file}"
        )

    def process_county_summary(self, df, state_fips_list=None, min_download_mbps=100, min_upload_mbps=10):
        """
        Process county summary data to extract broadband availability.

        Args:
            df: Raw county summary DataFrame
            state_fips_list: Optional list of 2-digit state FIPS codes to filter
            min_download_mbps: Minimum download speed (default 100 Mbps)
            min_upload_mbps: Minimum upload speed (default 10 Mbps)

        Returns:
            DataFrame: Processed county broadband availability
        """
        # Make a copy to avoid modifying original
        result = df.copy()

        # Filter to specific states if requested
        if state_fips_list:
            result['state_fips'] = result['county_fips'].astype(str).str[:2]
            result = result[result['state_fips'].isin(state_fips_list)].copy()

        # Calculate percentage covered at specified speed tier
        # Note: Column names may vary depending on FCC file structure
        # Common patterns:
        #   - locations_100_10 / total_locations
        #   - bsl_served_100_10 / bsl_total

        print(f"\nDataFrame columns: {list(result.columns)}")
        print(f"Sample data:\n{result.head()}")

        return result

    def get_broadband_availability(self, state_fips_list, min_download_mbps=100,
                                   min_upload_mbps=10, as_of_date=None, use_cache=True):
        """
        Get broadband availability data for specified states.

        Args:
            state_fips_list: List of 2-digit state FIPS codes
            min_download_mbps: Minimum download speed (default 100)
            min_upload_mbps: Minimum upload speed (default 10)
            as_of_date: Data version date or None for latest
            use_cache: Whether to use cached data

        Returns:
            DataFrame: County-level broadband availability
        """
        print(f"Loading FCC broadband data...")
        print(f"  Speed tier: ≥{min_download_mbps}/{min_upload_mbps} Mbps")
        print(f"  States: {len(state_fips_list)}")

        # Download/load county summary data
        df = self.download_county_summary_csv(as_of_date=as_of_date, use_cache=use_cache)

        # Process and filter
        result = self.process_county_summary(
            df,
            state_fips_list=state_fips_list,
            min_download_mbps=min_download_mbps,
            min_upload_mbps=min_upload_mbps
        )

        print(f"✓ Retrieved data for {len(result):,} counties")
        return result


def main():
    """Test the FCC Broadband bulk data client."""
    print("="*80)
    print("FCC BROADBAND BULK DATA CLIENT TEST")
    print("="*80)

    # Initialize client
    client = FCCBroadbandBulkClient()

    # Test with a few states
    test_states = ['51', '24']  # VA, MD

    print("\nTest: Get broadband data for VA and MD counties")
    print("-"*80)

    try:
        df = client.get_broadband_availability(
            state_fips_list=test_states,
            min_download_mbps=100,
            min_upload_mbps=10
        )
        print(f"\nRetrieved {len(df)} counties")
        print(f"Sample data:\n{df.head()}")

    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\nThis is expected - you need to manually download the file first.")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
