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
            df = pd.read_csv(cache_file, dtype={'county_fips': str})
            print(f"✓ Loaded {len(df):,} records from cache")
            return df

        # Try to download from known FCC Box.com URLs
        # FCC hosts files on us-fcc.app.box.com or us-fcc.box.com
        # URL patterns vary by release, so we try multiple patterns

        # Convert date format: '2024-06-30' -> 'June_2024'
        from datetime import datetime
        date_obj = datetime.strptime(as_of_date, '%Y-%m-%d')
        month_year = date_obj.strftime('%B_%Y')  # e.g., 'June_2024'

        # Possible URL patterns (based on FCC file hosting patterns)
        download_urls = [
            # Pattern 1: Direct Box.com shared folder
            f"https://us-fcc.app.box.com/v/bdc-data/file/{month_year}/county_summary.csv",
            # Pattern 2: Box.com with underscore date format
            f"https://us-fcc.app.box.com/shared/static/bdc_{as_of_date}_county.csv",
            # Pattern 3: Alternative naming
            f"https://us-fcc.box.com/v/bdc-public-data-{month_year}-county-summary",
        ]

        print(f"Attempting to download county summary for {as_of_date}...")

        # Try each URL pattern
        for url in download_urls:
            try:
                print(f"  Trying: {url[:60]}...")
                response = self._make_request(url, stream=True)

                # If successful, save to cache
                with open(cache_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"✓ Downloaded county summary to cache: {cache_file}")

                # Load and return the DataFrame
                df = pd.read_csv(cache_file, dtype={'county_fips': str})
                print(f"✓ Loaded {len(df):,} records")
                return df

            except Exception as e:
                print(f"  Failed: {str(e)[:80]}")
                continue

        # If all automatic downloads failed, provide manual download instructions
        print(f"\n" + "="*80)
        print(f"AUTOMATIC DOWNLOAD FAILED - MANUAL DOWNLOAD REQUIRED")
        print(f"="*80)
        print(f"\nPlease manually download the FCC county summary CSV file:")
        print(f"\n1. Visit: https://broadbandmap.fcc.gov/data-download")
        print(f"2. Select 'County' geographic level")
        print(f"3. Select data date: {as_of_date} (or latest available)")
        print(f"4. Download the county summary CSV file")
        print(f"5. Save it to: {cache_file}")
        print(f"\nRequired columns in the CSV file:")
        print(f"  - County FIPS code (may be named: county_fips, fips, geoid, etc.)")
        print(f"  - Total locations (may be named: locations, bsl, total_locations, etc.)")
        print(f"  - Locations served at various speed tiers")
        print(f"    (e.g., served_100_20, locations_100_10, etc.)")
        print(f"\nAfter downloading, re-run this script.")
        print(f"="*80)

        raise FileNotFoundError(
            f"County summary CSV not found. Please download manually and save to:\n"
            f"{cache_file}"
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
        print(f"\nProcessing county summary data...")
        print(f"  Input records: {len(df):,}")
        print(f"  Speed tier: ≥{min_download_mbps}/{min_upload_mbps} Mbps")

        # Make a copy to avoid modifying original
        result = df.copy()

        # Identify county FIPS column (various possible names)
        fips_column = None
        for col in ['county_fips', 'fips', 'geoid', 'county_id', 'fips_code', 'CountyFIPS']:
            if col in result.columns:
                fips_column = col
                break

        if not fips_column:
            # Try to find a column that looks like FIPS (5-digit codes)
            for col in result.columns:
                if result[col].astype(str).str.match(r'^\d{5}$').any():
                    fips_column = col
                    print(f"  Auto-detected FIPS column: {col}")
                    break

        if not fips_column:
            raise ValueError(f"Could not find county FIPS column. Available columns: {list(result.columns)}")

        # Normalize FIPS column name
        result = result.rename(columns={fips_column: 'county_fips'})
        result['county_fips'] = result['county_fips'].astype(str).str.zfill(5)

        # Filter to specific states if requested
        if state_fips_list:
            result['state_fips'] = result['county_fips'].str[:2]
            result = result[result['state_fips'].isin(state_fips_list)].copy()
            print(f"  Filtered to {len(state_fips_list)} states: {len(result):,} counties")

        # Identify total locations column
        total_locations_col = None
        for col in ['total_locations', 'bsl', 'locations', 'total_bsl', 'fabric_count']:
            if col in result.columns:
                total_locations_col = col
                break

        if not total_locations_col:
            raise ValueError(f"Could not find total locations column. Available columns: {list(result.columns)}")

        # Identify served locations column for the specified speed tier
        # Common patterns:
        #   - served_100_10, locations_100_10, bsl_100_10
        #   - served_100_20, locations_100_20 (FCC "served" tier)
        #   - served_{down}_{up}, locations_{down}_{up}

        # Build list of possible column names
        speed_patterns = [
            f'served_{min_download_mbps}_{min_upload_mbps}',
            f'locations_{min_download_mbps}_{min_upload_mbps}',
            f'bsl_{min_download_mbps}_{min_upload_mbps}',
            f'bsl_served_{min_download_mbps}_{min_upload_mbps}',
            # Also check for FCC "served" tier (100/20)
            'served_100_20',
            'locations_100_20',
            'bsl_100_20',
        ]

        served_col = None
        for pattern in speed_patterns:
            for col in result.columns:
                if pattern.lower() in col.lower():
                    served_col = col
                    print(f"  Found served locations column: {col}")
                    break
            if served_col:
                break

        if not served_col:
            # Show available columns to help user
            print(f"\n  Warning: Could not find served locations column for {min_download_mbps}/{min_upload_mbps} Mbps")
            print(f"  Available columns: {list(result.columns)}")

            # Try to find any column with speed tier info
            speed_cols = [col for col in result.columns if any(x in col.lower() for x in ['served', 'locations', 'bsl']) and any(c.isdigit() for c in col)]
            if speed_cols:
                print(f"\n  Columns that might contain speed tier data:")
                for col in speed_cols[:10]:
                    print(f"    - {col}")

            raise ValueError(f"Could not find served locations column for speed tier {min_download_mbps}/{min_upload_mbps}")

        # Calculate percentage covered
        result['served_locations'] = pd.to_numeric(result[served_col], errors='coerce').fillna(0)
        result['total_locations'] = pd.to_numeric(result[total_locations_col], errors='coerce').fillna(1)

        # Avoid division by zero
        result['percent_covered'] = 0.0
        mask = result['total_locations'] > 0
        result.loc[mask, 'percent_covered'] = (result.loc[mask, 'served_locations'] / result.loc[mask, 'total_locations']) * 100

        # Create clean output DataFrame
        output = pd.DataFrame({
            'county_fips': result['county_fips'],
            'total_locations': result['total_locations'],
            'served_locations': result['served_locations'],
            'percent_covered': result['percent_covered'],
            'min_download_mbps': min_download_mbps,
            'min_upload_mbps': min_upload_mbps
        })

        # Remove any rows with invalid FIPS codes
        output = output[output['county_fips'].str.match(r'^\d{5}$')].copy()

        print(f"\n  Output records: {len(output):,}")
        print(f"  Average coverage: {output['percent_covered'].mean():.2f}%")
        print(f"  Coverage range: {output['percent_covered'].min():.2f}% - {output['percent_covered'].max():.2f}%")

        return output

    def get_broadband_availability(self, state_fips_list, min_download_mbps=100,
                                   min_upload_mbps=10, as_of_date=None, use_cache=True):
        """
        Get broadband availability data for specified states.

        This is the main entry point for downloading and processing FCC broadband data.

        Args:
            state_fips_list: List of 2-digit state FIPS codes
            min_download_mbps: Minimum download speed (default 100)
            min_upload_mbps: Minimum upload speed (default 10)
            as_of_date: Data version date or None for latest
            use_cache: Whether to use cached data

        Returns:
            DataFrame: County-level broadband availability with columns:
                - county_fips: 5-digit FIPS code
                - total_locations: Total broadband serviceable locations
                - served_locations: Locations served at specified speed tier
                - percent_covered: Percentage of locations covered
                - min_download_mbps: Speed tier (download)
                - min_upload_mbps: Speed tier (upload)
        """
        print(f"\n" + "="*80)
        print(f"FCC BROADBAND BULK DATA DOWNLOAD")
        print(f"="*80)
        print(f"Speed tier: ≥{min_download_mbps}/{min_upload_mbps} Mbps")
        print(f"States: {len(state_fips_list)}")
        if as_of_date:
            print(f"Data date: {as_of_date}")

        # Download/load county summary data
        df = self.download_county_summary_csv(as_of_date=as_of_date, use_cache=use_cache)

        # Process and filter
        result = self.process_county_summary(
            df,
            state_fips_list=state_fips_list,
            min_download_mbps=min_download_mbps,
            min_upload_mbps=min_upload_mbps
        )

        print(f"\n✓ Successfully retrieved broadband data for {len(result):,} counties")
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
            min_upload_mbps=10,
            as_of_date='2024-06-30'
        )

        print(f"\n" + "="*80)
        print(f"SUCCESS - Retrieved {len(df):,} counties")
        print(f"="*80)
        print(f"\nSample data:")
        print(df.head(10).to_string(index=False))

        print(f"\n--- Summary Statistics ---")
        print(f"Counties: {len(df):,}")
        print(f"Average coverage: {df['percent_covered'].mean():.2f}%")
        print(f"Median coverage: {df['percent_covered'].median():.2f}%")
        print(f"Min coverage: {df['percent_covered'].min():.2f}%")
        print(f"Max coverage: {df['percent_covered'].max():.2f}%")

        # Coverage distribution
        bins = [0, 25, 50, 75, 90, 100]
        labels = ['0-25%', '25-50%', '50-75%', '75-90%', '90-100%']
        df['coverage_bin'] = pd.cut(df['percent_covered'], bins=bins, labels=labels, include_lowest=True)
        print(f"\nCoverage distribution:")
        print(df['coverage_bin'].value_counts().sort_index())

    except FileNotFoundError as e:
        print(f"\n{str(e)}")
        print("\nNote: This is expected if you haven't downloaded the file yet.")
        print("Follow the instructions above to manually download the FCC county summary file.")

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
