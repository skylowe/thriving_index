"""
BLS QCEW (Quarterly Census of Employment and Wages) Data Access Client

This client retrieves QCEW data using the BLS downloadable data files.
Documentation: https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm

QCEW data is provided as ZIP files containing CSV data.
URL format: https://data.bls.gov/cew/data/files/[YEAR]/csv/[YEAR]_annual_singlefile.zip
"""

import requests
import time
import pandas as pd
import io
import zipfile
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class QCEWClient:
    """Client for BLS QCEW Data Files"""

    def __init__(self):
        """Initialize QCEW client."""
        self.base_url = 'https://data.bls.gov/cew/data/files'
        self.session = requests.Session()
        self.cache_dir = RAW_DATA_DIR / 'qcew' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _download_file(self, url, retries=MAX_RETRIES):
        """
        Download file with retry logic.

        Args:
            url: Full URL to file
            retries: Number of retries remaining

        Returns:
            bytes: File content
        """
        try:
            print(f"  Downloading {url}...", flush=True)
            response = self.session.get(url, timeout=300, stream=True)  # Longer timeout for large files
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            content = bytearray()

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content.extend(chunk)
                    downloaded += len(chunk)
                    if total_size > 0 and downloaded % (10 * 1024 * 1024) == 0:  # Print every 10 MB
                        progress = (downloaded / total_size) * 100
                        print(f"    Progress: {progress:.1f}% ({downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)", flush=True)

            time.sleep(REQUEST_DELAY)
            print(f"  ✓ Downloaded {len(content) / (1024*1024):.1f} MB")
            return bytes(content)

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"  Download failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._download_file(url, retries - 1)
            else:
                raise Exception(f"QCEW download failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_annual_singlefile(self, year, use_cache=True):
        """
        Download and extract the annual single file for a year.
        This file contains all QCEW data for the year.

        Args:
            year: Year (e.g., 2022)
            use_cache: If True, use cached file if available

        Returns:
            DataFrame: All QCEW data for the year
        """
        cache_file = self.cache_dir / f"{year}_annual_singlefile.csv"

        # Check cache
        if use_cache and cache_file.exists():
            print(f"  Using cached file: {cache_file}")
            return pd.read_csv(cache_file)

        # Download ZIP file
        url = f"{self.base_url}/{year}/csv/{year}_annual_singlefile.zip"
        zip_content = self._download_file(url)

        # Extract CSV from ZIP
        print(f"  Extracting CSV from ZIP...")
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            # Get the CSV filename (usually year.annual.singlefile.csv)
            csv_filename = f"{year}.annual.singlefile.csv"
            with zf.open(csv_filename) as csv_file:
                df = pd.read_csv(csv_file)

        # Cache the CSV
        print(f"  Caching data to {cache_file}...")
        df.to_csv(cache_file, index=False)

        return df

    def filter_private_total(self, df):
        """
        Filter QCEW data to private sector, all industries total.

        Args:
            df: QCEW DataFrame

        Returns:
            DataFrame: Filtered data with private sector totals
        """
        if df.empty:
            return df

        # Filter for:
        # - own_code = 5 (Private)
        # - industry_code = '10' (Total, all industries)
        # This gives us private sector totals for each area

        filtered = df[
            (df['own_code'] == 5) &  # Private ownership
            (df['industry_code'] == '10')  # Total, all industries
        ].copy()

        # Filter out state-level (area_fips ending in 000) and special codes (999)
        # Keep only county-level data (5-digit FIPS where last 3 digits are 001-899)
        if 'area_fips_str' in filtered.columns:
            filtered = filtered[
                ~filtered['area_fips_str'].str.endswith('000') &
                ~filtered['area_fips_str'].str.endswith('999')
            ].copy()

        return filtered

    def get_private_employment_wages(self, year, state_fips_list):
        """
        Get private sector employment and wages for counties in specified states.

        Args:
            year: Year
            state_fips_list: List of 2-digit state FIPS codes

        Returns:
            DataFrame: County-level private employment and wages data
        """
        # Download annual data for the year
        df = self.get_annual_singlefile(year)

        if df.empty:
            return pd.DataFrame()

        # Filter to our states (first 2 digits of area_fips)
        # area_fips is integer, so convert to string with zero-padding
        df['area_fips_str'] = df['area_fips'].astype(str).str.zfill(5)
        df_states = df[df['area_fips_str'].str[:2].isin(state_fips_list)].copy()

        # Filter to private sector county totals
        filtered = self.filter_private_total(df_states)

        # Select relevant columns
        columns_to_keep = [
            'area_fips',           # County FIPS code
            'own_code',            # Ownership code
            'year',                # Year
            'annual_avg_emplvl',   # Annual average employment
            'total_annual_wages',  # Total annual wages
            'annual_avg_wkly_wage',# Average weekly wage
            'avg_annual_pay'       # Average annual pay
        ]

        # Check which columns exist in the dataframe
        available_cols = [col for col in columns_to_keep if col in filtered.columns]
        result = filtered[available_cols].copy()

        print(f"  ✓ Retrieved {len(result)} county records for {len(state_fips_list)} states")

        return result

    def collect_multi_year_data(self, years, state_fips_list):
        """
        Collect QCEW data for multiple years and states.

        Args:
            years: List of years
            state_fips_list: List of 2-digit state FIPS codes

        Returns:
            DataFrame: Combined data for all states and years
        """
        all_data = []

        for year in years:
            print(f"\nCollecting QCEW data for {year}...")
            try:
                df = self.get_private_employment_wages(year, state_fips_list)
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                print(f"  ✗ Year {year}: {e}")

        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            return combined
        else:
            return pd.DataFrame()

    def save_data(self, df, filename):
        """
        Save QCEW data to CSV file.

        Args:
            df: DataFrame to save
            filename: Output filename (will be saved in data/raw/qcew/)
        """
        output_dir = RAW_DATA_DIR / 'qcew'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        df.to_csv(output_path, index=False)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the QCEW client
    print("Testing QCEW Data File Client...")
    print("=" * 60)

    client = QCEWClient()

    # Test 1: Download 2022 data and filter for Delaware
    print("\nTest 1: Download 2022 Annual Data")
    print("-" * 60)
    try:
        # This will download ~500MB ZIP file on first run
        print("Note: First run will download large file (~500MB)")
        df = client.get_annual_singlefile(2022)
        print(f"✓ Retrieved {len(df):,} total records")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Sample columns: {list(df.columns[:5])}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get private sector data for Delaware
    print("\n\nTest 2: Private Employment and Wages - Delaware")
    print("-" * 60)
    try:
        df = client.get_private_employment_wages(2022, ['10'])
        print(f"✓ Retrieved {len(df)} county records")
        if not df.empty:
            print(f"\nColumns: {df.columns.tolist()}")
            print(f"\nSample data:")
            print(df.to_string())
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Multi-year collection for small states
    print("\n\nTest 3: Multi-Year Data - Delaware (2020-2022)")
    print("-" * 60)
    try:
        df = client.collect_multi_year_data([2020, 2021, 2022], ['10'])
        print(f"✓ Retrieved {len(df)} total records across 3 years")
        if not df.empty:
            print(f"\nRecords by year:")
            print(df.groupby('year').size())
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("QCEW Client test complete")
