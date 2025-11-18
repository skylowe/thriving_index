"""
County Health Rankings & Roadmaps (CHR&R) Client

This client downloads and parses County Health Rankings data.
Primary use: Voter Turnout data (measure 8.4)

Data Source: https://www.countyhealthrankings.org/
Documentation: https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation
"""

import requests
import csv
import io
import json
from pathlib import Path
import sys
import time

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class CountyHealthRankingsClient:
    """Client for County Health Rankings & Roadmaps data"""

    def __init__(self):
        """Initialize CHR client."""
        self.base_url = "https://www.countyhealthrankings.org/sites/default/files/media/document"
        self.session = requests.Session()
        self.raw_data_dir = Path(RAW_DATA_DIR) / "chr"
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def download_analytic_data(self, year, retries=MAX_RETRIES):
        """
        Download County Health Rankings analytic dataset for a specific year.

        Args:
            year: Year of data release (e.g., 2025, 2024)
            retries: Number of retries remaining

        Returns:
            str: CSV content as text
        """
        url = f"{self.base_url}/analytic_data{year}.csv"

        try:
            print(f"Downloading CHR analytic data for {year}...")
            print(f"  URL: {url}")

            # Download the file (may be large, ~10 MB)
            response = self.session.get(url, timeout=120)  # Increase timeout for large file
            response.raise_for_status()

            # Decode bytes to string
            csv_content = response.content.decode('utf-8')
            print(f"  Downloaded {len(csv_content)} bytes")

            # Add small delay to be respectful
            time.sleep(REQUEST_DELAY)

            return csv_content

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Error downloading CHR data: {e}. Retrying... ({retries} attempts left)")
                time.sleep(5)  # Longer delay between retries
                return self.download_analytic_data(year, retries - 1)
            else:
                print(f"Failed to download CHR data after {MAX_RETRIES} attempts: {e}")
                raise

    def get_voter_turnout(self, year=2025, cache=True):
        """
        Get voter turnout data from County Health Rankings.

        Args:
            year: Year of CHR data release (default: 2025)
            cache: If True, cache the raw CSV file locally

        Returns:
            list: List of dictionaries with county voter turnout data
        """
        # Check cache first
        cache_file = self.raw_data_dir / f"chr_voter_turnout_{year}_raw.csv"

        if cache and cache_file.exists():
            print(f"Loading cached CHR voter turnout data for {year}...")
            with open(cache_file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            # Download from CHR
            csv_content = self.download_analytic_data(year)

            # Cache if requested
            if cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                print(f"Cached raw data to {cache_file}")

        # Parse CSV
        voter_turnout_data = []
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        # Get all field names to find voter turnout column
        fieldnames = csv_reader.fieldnames
        print(f"  CSV has {len(fieldnames)} columns")

        # Look for voter turnout column (variable name might vary by year)
        # Common patterns: v147_rawvalue, voterturnout, etc.
        turnout_col = None
        for field in fieldnames:
            if 'voter' in field.lower() and 'turnout' in field.lower():
                turnout_col = field
                print(f"  Found voter turnout column: {turnout_col}")
                break

        # If not found, try specific variable codes
        if not turnout_col:
            # Try common CHR variable codes for voter turnout
            for code in ['v147_rawvalue', 'v155_rawvalue', 'voter_turnout_raw_value']:
                if code in fieldnames:
                    turnout_col = code
                    print(f"  Found voter turnout column: {turnout_col}")
                    break

        if not turnout_col:
            print("  Warning: Could not automatically identify voter turnout column")
            print(f"  Available columns (first 20): {fieldnames[:20]}")
            raise ValueError("Could not find voter turnout column in CHR data")

        # Parse rows
        for row in csv_reader:
            try:
                # Get county identifiers
                fips = row.get('fipscode', row.get('FIPS', '')).strip()
                state_name = row.get('state', row.get('State', '')).strip()
                county_name = row.get('county', row.get('County', '')).strip()

                # Get voter turnout value
                turnout = row.get(turnout_col, '').strip()

                # Only include counties with valid FIPS and turnout data
                if fips and turnout and len(fips) == 5:
                    voter_turnout_data.append({
                        'fips': fips,
                        'state': state_name,
                        'county': county_name,
                        'voter_turnout_pct': turnout,
                        'data_year': year
                    })
            except Exception as e:
                # Skip rows with parsing errors
                continue

        print(f"Found {len(voter_turnout_data)} counties with voter turnout data")
        return voter_turnout_data

    def filter_to_states(self, data, state_fips_list):
        """
        Filter voter turnout data to specific states.

        Args:
            data: List of county voter turnout dictionaries
            state_fips_list: List of 2-digit state FIPS codes

        Returns:
            list: Filtered data
        """
        filtered = []
        for county in data:
            state_fips = county['fips'][:2]  # First 2 digits are state FIPS
            if state_fips in state_fips_list:
                filtered.append(county)

        print(f"Filtered to {len(filtered)} counties in target states")
        return filtered

    def save_voter_turnout_json(self, data, year):
        """
        Save voter turnout data to JSON file.

        Args:
            data: List of voter turnout dictionaries
            year: Year of data

        Returns:
            Path: Path to saved file
        """
        output_file = self.raw_data_dir / f"chr_voter_turnout_{year}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"Saved {len(data)} counties to {output_file}")
        return output_file


def main():
    """Test the CHR client"""
    print("Testing County Health Rankings Client")
    print("=" * 50)

    client = CountyHealthRankingsClient()

    # Test with 2024 data (2025 may have server issues)
    year = 2024
    print(f"\nTesting with {year} data...")

    try:
        # Get voter turnout data
        data = client.get_voter_turnout(year)

        # Filter to our 10 states
        state_fips_list = ['51', '42', '24', '10', '54', '21', '47', '37', '45', '13']
        filtered_data = client.filter_to_states(data, state_fips_list)

        # Save to JSON
        output_file = client.save_voter_turnout_json(filtered_data, year)

        # Print summary
        print(f"\n{'='*50}")
        print(f"Summary for {year}:")
        print(f"Total counties with voter turnout: {len(data)}")
        print(f"Counties in target states: {len(filtered_data)}")

        if filtered_data:
            # Print first few counties
            print(f"\nSample counties:")
            for i, county in enumerate(filtered_data[:5], 1):
                print(f"  {i}. {county['county']}, {county['state']}: {county['voter_turnout_pct']}%")

        print(f"\nData saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
