"""
Social Capital Atlas Client

This client downloads and parses Social Capital Atlas county-level data from Meta/Facebook.
Primary use: Volunteering rates and civic organizations density by county

Data Source: https://socialcapital.org / https://data.humdata.org/dataset/social-capital-atlas
Documentation: https://opportunityinsights.org/paper/socialcapital1/
"""

import requests
import pandas as pd
import json
from pathlib import Path
import sys
import time
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class SocialCapitalAtlasClient:
    """Client for Social Capital Atlas county-level data"""

    def __init__(self):
        """Initialize Social Capital Atlas client."""
        # Direct download URL from Humanitarian Data Exchange (HDX)
        self.base_url = "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ec896b64-c922-4737-b759-e4bd7f73b8cc/download/social_capital_county.csv"
        self.session = requests.Session()
        self.raw_data_dir = Path(RAW_DATA_DIR) / "social_capital"
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def _download_county_data(self, retries=MAX_RETRIES):
        """
        Download Social Capital Atlas county-level CSV file.

        Args:
            retries: Number of retries remaining

        Returns:
            DataFrame: County-level social capital data
        """
        cache_file = self.raw_data_dir / "social_capital_county.csv"

        # Check cache first
        if cache_file.exists():
            print("Loading cached Social Capital Atlas data...")
            try:
                df = pd.read_csv(cache_file)
                print(f"  ✓ Loaded {len(df)} counties from cache")
                return df
            except Exception as e:
                print(f"  ⚠ Error reading cache: {e}. Re-downloading...")

        # Download from HDX
        try:
            print("Downloading Social Capital Atlas county data from HDX...")
            print(f"  URL: {self.base_url}")

            response = self.session.get(self.base_url, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()

            # Parse CSV
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))

            print(f"  ✓ Downloaded {len(df)} counties")

            # Cache the data
            df.to_csv(cache_file, index=False)
            print(f"  ✓ Cached data to {cache_file}")

            # Add small delay to be respectful
            time.sleep(REQUEST_DELAY)

            return df

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"  ✗ Error downloading data: {e}. Retrying... ({retries} attempts left)")
                time.sleep(2)
                return self._download_county_data(retries - 1)
            else:
                print(f"  ✗ Failed to download data after {MAX_RETRIES} attempts: {e}")
                raise

    def get_volunteering_civic_data(self, state_fips_list=None):
        """
        Get volunteering and civic organizations data for all counties.

        Args:
            state_fips_list: Optional list of state FIPS codes to filter to (e.g., ['51', '42'])

        Returns:
            DataFrame: County data with volunteering_rate and civic_organizations columns
        """
        print("\nCollecting Social Capital Atlas Data...")
        print("-" * 60)

        # Download full dataset
        df = self._download_county_data()

        # Filter to target states if specified
        if state_fips_list:
            # Extract state FIPS (first 2 digits of county FIPS)
            df['state_fips'] = df['county'].astype(str).str.zfill(5).str[:2]
            df = df[df['state_fips'].isin(state_fips_list)].copy()
            print(f"  ✓ Filtered to {len(df)} counties in target states")

        # Ensure county FIPS is 5-digit string
        df['fips'] = df['county'].astype(str).str.zfill(5)

        # Select relevant columns
        columns_to_keep = [
            'fips',
            'county_name',
            'volunteering_rate_county',
            'civic_organizations_county'
        ]

        # Check if columns exist
        missing_cols = [col for col in columns_to_keep if col not in df.columns]
        if missing_cols:
            print(f"  ⚠ Warning: Missing columns: {missing_cols}")
            columns_to_keep = [col for col in columns_to_keep if col in df.columns]

        result_df = df[columns_to_keep].copy()

        # Convert to numeric
        if 'volunteering_rate_county' in result_df.columns:
            result_df['volunteering_rate_county'] = pd.to_numeric(
                result_df['volunteering_rate_county'],
                errors='coerce'
            )

        if 'civic_organizations_county' in result_df.columns:
            result_df['civic_organizations_county'] = pd.to_numeric(
                result_df['civic_organizations_county'],
                errors='coerce'
            )

        print(f"\n  ✓ Retrieved {len(result_df)} counties")

        if 'volunteering_rate_county' in result_df.columns:
            print(f"\n  Volunteering Rate:")
            print(f"    Mean: {result_df['volunteering_rate_county'].mean():.4f}")
            print(f"    Median: {result_df['volunteering_rate_county'].median():.4f}")
            print(f"    Range: {result_df['volunteering_rate_county'].min():.4f} - {result_df['volunteering_rate_county'].max():.4f}")
            print(f"    Missing: {result_df['volunteering_rate_county'].isna().sum()}")

        if 'civic_organizations_county' in result_df.columns:
            print(f"\n  Civic Organizations:")
            print(f"    Mean: {result_df['civic_organizations_county'].mean():.4f}")
            print(f"    Median: {result_df['civic_organizations_county'].median():.4f}")
            print(f"    Range: {result_df['civic_organizations_county'].min():.4f} - {result_df['civic_organizations_county'].max():.4f}")
            print(f"    Missing: {result_df['civic_organizations_county'].isna().sum()}")

        return result_df

    def save_metadata(self, df, output_file):
        """
        Save collection metadata to JSON file.

        Args:
            df: DataFrame with collected data
            output_file: Path to save metadata JSON
        """
        metadata = {
            'source': 'Social Capital Atlas (Meta/Facebook)',
            'source_url': 'https://socialcapital.org',
            'data_url': self.base_url,
            'download_date': datetime.now().isoformat(),
            'records_collected': len(df),
            'measures': {
                'volunteering_rate_county': 'Percentage of individuals in volunteering/activism groups',
                'civic_organizations_county': 'Number of civic organizations per 1,000 Facebook users'
            },
            'notes': 'County-level social capital data from Facebook network analysis'
        }

        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  ✓ Saved metadata to {output_file}")
        return metadata


if __name__ == "__main__":
    # Test the client
    client = SocialCapitalAtlasClient()

    # Test with a few states (Virginia, Maryland, North Carolina)
    test_states = ['51', '24', '37']
    df = client.get_volunteering_civic_data(state_fips_list=test_states)

    print(f"\nTest complete: Retrieved {len(df)} counties")
    print(f"\nSample data:")
    print(df.head(10))
