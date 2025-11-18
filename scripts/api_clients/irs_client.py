"""
IRS Exempt Organizations Business Master File (EO BMF) Client

This client downloads and parses IRS Exempt Organizations data.
Primary use: Count of 501(c)(3) organizations by county

Data Source: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
Documentation: https://www.irs.gov/pub/irs-soi/
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


class IRSExemptOrgClient:
    """Client for IRS Exempt Organizations Business Master File"""

    def __init__(self):
        """Initialize IRS EO BMF client."""
        self.base_url = "https://www.irs.gov/pub/irs-soi"
        self.session = requests.Session()
        self.raw_data_dir = Path(RAW_DATA_DIR) / "irs"
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.zip_to_fips = None  # Cache for ZIP-FIPS crosswalk

    def _download_state_file(self, state_abbr, retries=MAX_RETRIES):
        """
        Download IRS EO BMF file for a specific state.

        Args:
            state_abbr: Two-letter state abbreviation (lowercase)
            retries: Number of retries remaining

        Returns:
            str: CSV content as text
        """
        url = f"{self.base_url}/eo_{state_abbr.lower()}.csv"

        try:
            print(f"Downloading IRS EO BMF data for {state_abbr.upper()}...")
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()

            # Add small delay to be respectful
            time.sleep(REQUEST_DELAY)

            return response.text

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Error downloading {state_abbr.upper()} data: {e}. Retrying... ({retries} attempts left)")
                time.sleep(2)
                return self._download_state_file(state_abbr, retries - 1)
            else:
                print(f"Failed to download {state_abbr.upper()} data after {MAX_RETRIES} attempts: {e}")
                raise

    def get_501c3_organizations(self, state_abbr, cache=True):
        """
        Get all 501(c)(3) organizations for a specific state.

        Args:
            state_abbr: Two-letter state abbreviation
            cache: If True, cache the raw CSV file locally

        Returns:
            list: List of dictionaries with organization data
        """
        state_abbr_lower = state_abbr.lower()

        # Check cache first
        cache_file = self.raw_data_dir / f"eo_{state_abbr_lower}_raw.csv"

        if cache and cache_file.exists():
            print(f"Loading cached IRS EO BMF data for {state_abbr.upper()}...")
            with open(cache_file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            # Download from IRS
            csv_content = self._download_state_file(state_abbr_lower)

            # Cache if requested
            if cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                print(f"Cached raw data to {cache_file}")

        # Parse CSV
        organizations = []
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        for row in csv_reader:
            # Filter to 501(c)(3) organizations only
            # SUBSECTION code "03" indicates 501(c)(3)
            if row.get('SUBSECTION', '').strip() == '03':
                organizations.append({
                    'ein': row.get('EIN', '').strip(),
                    'name': row.get('NAME', '').strip(),
                    'city': row.get('CITY', '').strip(),
                    'state': row.get('STATE', '').strip(),
                    'zip': row.get('ZIP', '').strip(),
                    'subsection': row.get('SUBSECTION', '').strip(),
                    'classification': row.get('CLASSIFICATION', '').strip(),
                    'deductibility': row.get('DEDUCTIBILITY', '').strip(),
                    'foundation': row.get('FOUNDATION', '').strip(),
                    'ntee_cd': row.get('NTEE_CD', '').strip()
                })

        print(f"Found {len(organizations)} 501(c)(3) organizations in {state_abbr.upper()}")
        return organizations

    def save_organizations_json(self, organizations, state_abbr):
        """
        Save filtered 501(c)(3) organizations to JSON file.

        Args:
            organizations: List of organization dictionaries
            state_abbr: Two-letter state abbreviation
        """
        output_file = self.raw_data_dir / f"eo_{state_abbr.lower()}_501c3.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(organizations, f, indent=2)

        print(f"Saved {len(organizations)} organizations to {output_file}")
        return output_file

    def get_zip_to_fips_crosswalk(self, cache=True):
        """
        Download and cache ZIP code to county FIPS crosswalk.

        Args:
            cache: If True, cache the crosswalk file locally

        Returns:
            dict: Dictionary mapping ZIP codes to county FIPS codes
        """
        # Return cached version if already loaded
        if self.zip_to_fips is not None:
            return self.zip_to_fips

        # Check for cached file
        cache_file = self.raw_data_dir / "zip_to_fips_crosswalk.json"

        if cache and cache_file.exists():
            print("Loading cached ZIP-to-FIPS crosswalk...")
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.zip_to_fips = json.load(f)
            print(f"Loaded {len(self.zip_to_fips)} ZIP-FIPS mappings from cache")
            return self.zip_to_fips

        # Download from GitHub
        url = "https://raw.githubusercontent.com/bgruber/zip2fips/master/zip2fips.json"
        print("Downloading ZIP-to-FIPS crosswalk...")

        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            self.zip_to_fips = response.json()

            # Cache if requested
            if cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.zip_to_fips, f, indent=2)
                print(f"Cached {len(self.zip_to_fips)} ZIP-FIPS mappings to {cache_file}")

            return self.zip_to_fips

        except requests.exceptions.RequestException as e:
            print(f"Error downloading ZIP-to-FIPS crosswalk: {e}")
            raise

    def map_organizations_to_counties(self, organizations):
        """
        Map 501(c)(3) organizations to counties using ZIP-FIPS crosswalk.

        Args:
            organizations: List of organization dictionaries

        Returns:
            dict: Dictionary mapping county FIPS to list of organizations
        """
        # Get crosswalk if not already loaded
        if self.zip_to_fips is None:
            self.get_zip_to_fips_crosswalk()

        # Map organizations to counties
        county_orgs = {}
        mapped_count = 0
        unmapped_count = 0

        for org in organizations:
            # Extract 5-digit ZIP code
            zip_full = org.get('zip', '').strip()
            zip_5 = zip_full.split('-')[0]  # Get first 5 digits

            # Look up county FIPS
            fips = self.zip_to_fips.get(zip_5)

            if fips:
                if fips not in county_orgs:
                    county_orgs[fips] = []
                county_orgs[fips].append(org)
                mapped_count += 1
            else:
                unmapped_count += 1

        print(f"Mapped {mapped_count} organizations to {len(county_orgs)} counties")
        print(f"Could not map {unmapped_count} organizations (no ZIP-FIPS match)")

        return county_orgs

    def count_organizations_by_county(self, organizations):
        """
        Count 501(c)(3) organizations by county.

        Args:
            organizations: List of organization dictionaries

        Returns:
            dict: Dictionary mapping county FIPS to organization count
        """
        county_orgs = self.map_organizations_to_counties(organizations)

        # Convert to counts
        county_counts = {fips: len(orgs) for fips, orgs in county_orgs.items()}

        return county_counts


def main():
    """Test the IRS client with a single state"""
    print("Testing IRS Exempt Organizations Client")
    print("=" * 50)

    client = IRSExemptOrgClient()

    # Test with Virginia
    state = "VA"
    print(f"\nTesting with {state}...")

    # Get 501(c)(3) organizations
    orgs = client.get_501c3_organizations(state)

    # Save to JSON
    output_file = client.save_organizations_json(orgs, state)

    # Test ZIP-to-FIPS crosswalk
    print(f"\n{'='*50}")
    print("Testing ZIP-to-FIPS crosswalk...")
    client.get_zip_to_fips_crosswalk()

    # Map organizations to counties
    print(f"\n{'='*50}")
    print("Mapping organizations to counties...")
    county_counts = client.count_organizations_by_county(orgs)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Summary for {state}:")
    print(f"Total 501(c)(3) organizations: {len(orgs)}")
    print(f"Counties with organizations: {len(county_counts)}")

    if orgs:
        print(f"\nSample organization:")
        print(f"  EIN: {orgs[0]['ein']}")
        print(f"  Name: {orgs[0]['name']}")
        print(f"  City: {orgs[0]['city']}")
        print(f"  ZIP: {orgs[0]['zip']}")

    # Show top 10 counties by organization count
    print(f"\nTop 10 counties by 501(c)(3) organization count:")
    sorted_counties = sorted(county_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (fips, count) in enumerate(sorted_counties[:10], 1):
        print(f"  {i}. County FIPS {fips}: {count} organizations")

    print(f"\nData saved to: {output_file}")


if __name__ == "__main__":
    main()
