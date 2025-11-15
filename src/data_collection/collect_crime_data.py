"""
Crime Data Collection Script

Fetches crime data from the FBI Crime Data Explorer API for all law enforcement
agencies in target states, aggregates to county and regional levels, and
calculates crime rates for the Thriving Index.

Usage:
    python src/data_collection/collect_crime_data.py --year 2024
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api_clients.fbi_cde_api import FBICrimeDataExplorerAPI
from src.utils.ori_crosswalk import ORICrosswalk
from src.utils.regions_v2 import get_all_regions, get_region_fips_codes

logger = logging.getLogger(__name__)


class CrimeDataCollector:
    """Collects and aggregates crime data from FBI API."""

    def __init__(self, api_key: str, year: int = 2024):
        """
        Initialize the crime data collector.

        Args:
            api_key: FBI API key
            year: Year for which to collect data
        """
        self.api_key = api_key
        self.year = year
        self.from_date = f"01-{year}"
        self.to_date = f"12-{year}"

        # Initialize API client and crosswalk
        self.api_client = FBICrimeDataExplorerAPI(api_key=api_key)
        self.crosswalk = ORICrosswalk()

        # Output directory
        self.output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_all_agency_data(
        self,
        states: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Dict]:
        """
        Fetch crime data for all agencies in specified states.

        Args:
            states: List of state names (e.g., ['VIRGINIA']). If None, fetches all target states.
            limit: Maximum number of agencies to fetch (for testing). None = fetch all.

        Returns:
            Dictionary mapping ORI codes to crime data
        """
        # Get all ORI codes for specified states
        if states is None:
            ori_codes = self.crosswalk.get_all_ori_codes()
        else:
            ori_codes = []
            for state in states:
                ori_codes.extend(self.crosswalk.get_all_oris_for_state(state))

        # Apply limit if specified
        if limit:
            ori_codes = ori_codes[:limit]
            logger.info(f"Limiting to first {limit} agencies for testing")

        logger.info(f"Fetching crime data for {len(ori_codes)} agencies")

        # Fetch crime data
        results = self.api_client.fetch_crimes_for_oris(
            ori_list=ori_codes,
            from_date=self.from_date,
            to_date=self.to_date,
            delay=0.1  # 100ms delay between requests
        )

        # Save raw agency data
        output_file = self.output_dir / f'crime_agency_data_{self.year}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved agency-level data to {output_file}")

        return results

    def aggregate_to_counties(self, agency_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Aggregate agency-level crime data to county level.

        Args:
            agency_data: Dictionary mapping ORI codes to crime data

        Returns:
            Dictionary mapping FIPS codes to aggregated county crime data
        """
        county_data = {}

        for ori, crime_data in agency_data.items():
            # Get FIPS code for this ORI
            fips = self.crosswalk.get_fips_for_ori(ori)
            if not fips:
                logger.warning(f"No FIPS code found for ORI {ori}")
                continue

            # Get agency info
            agency_info = self.crosswalk.get_ori_info(ori)

            # Initialize county if not exists
            if fips not in county_data:
                county_data[fips] = {
                    'fips': fips,
                    'state': agency_info['state'],
                    'county': agency_info['county'],
                    'agencies': [],
                    'violent_crime': {
                        'total_count': 0,
                        'monthly_counts': {f"{m:02d}-{self.year}": 0 for m in range(1, 13)}
                    },
                    'property_crime': {
                        'total_count': 0,
                        'monthly_counts': {f"{m:02d}-{self.year}": 0 for m in range(1, 13)}
                    }
                }

            county_data[fips]['agencies'].append(ori)

            # Aggregate violent crime
            violent_data = crime_data.get('violent')
            if violent_data and 'offenses' in violent_data:
                actuals = violent_data['offenses'].get('actuals')
                if actuals:  # Check if actuals is not None
                    # Find the agency name in actuals (it varies)
                    for agency_name, monthly_data in actuals.items():
                        if 'Clearances' in agency_name:
                            continue  # Skip clearance data
                        if monthly_data:  # Check if monthly_data is not None
                            for month, count in monthly_data.items():
                                if count:  # Only add if not None
                                    county_data[fips]['violent_crime']['monthly_counts'][month] += count
                                    county_data[fips]['violent_crime']['total_count'] += count

            # Aggregate property crime
            property_data = crime_data.get('property')
            if property_data and 'offenses' in property_data:
                actuals = property_data['offenses'].get('actuals')
                if actuals:  # Check if actuals is not None
                    for agency_name, monthly_data in actuals.items():
                        if 'Clearances' in agency_name:
                            continue
                        if monthly_data:  # Check if monthly_data is not None
                            for month, count in monthly_data.items():
                                if count:
                                    county_data[fips]['property_crime']['monthly_counts'][month] += count
                                    county_data[fips]['property_crime']['total_count'] += count

        logger.info(f"Aggregated data for {len(county_data)} counties")

        # Save county-level data
        output_file = self.output_dir / f'crime_county_data_{self.year}.json'
        with open(output_file, 'w') as f:
            json.dump(county_data, f, indent=2)
        logger.info(f"Saved county-level data to {output_file}")

        return county_data

    def aggregate_to_regions(self, county_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Aggregate county-level crime data to regional level.

        Args:
            county_data: Dictionary mapping FIPS codes to county crime data

        Returns:
            Dictionary mapping region codes to aggregated regional crime data
        """
        region_data = {}
        all_regions = get_all_regions()

        for region_code, region in all_regions.items():
            region_fips = get_region_fips_codes(region_code)

            # Extract state from region code (e.g., 'VA-1' -> 'VA')
            state_abbr = region_code.split('-')[0]

            region_data[region_code] = {
                'region_code': region_code,
                'region_name': region['name'],
                'state': state_abbr,
                'counties': [],
                'violent_crime': {
                    'total_count': 0
                },
                'property_crime': {
                    'total_count': 0
                }
            }

            # Aggregate counties in this region
            for fips in region_fips:
                if fips in county_data:
                    region_data[region_code]['counties'].append(fips)
                    region_data[region_code]['violent_crime']['total_count'] += \
                        county_data[fips]['violent_crime']['total_count']
                    region_data[region_code]['property_crime']['total_count'] += \
                        county_data[fips]['property_crime']['total_count']

        logger.info(f"Aggregated data for {len(region_data)} regions")

        # Save regional data
        output_file = self.output_dir / f'crime_regional_data_{self.year}.json'
        with open(output_file, 'w') as f:
            json.dump(region_data, f, indent=2)
        logger.info(f"Saved regional data to {output_file}")

        return region_data

    def calculate_crime_rates(
        self,
        county_data: Dict[str, Dict],
        population_data: Optional[Dict[str, int]] = None
    ) -> Dict[str, Dict]:
        """
        Calculate crime rates per 100,000 population for counties.

        Args:
            county_data: Dictionary mapping FIPS codes to county crime data
            population_data: Optional dictionary mapping FIPS codes to population.
                           If None, rates won't be calculated.

        Returns:
            Dictionary with calculated crime rates
        """
        rates_data = {}

        for fips, crime_data in county_data.items():
            rates_data[fips] = {
                'fips': fips,
                'state': crime_data['state'],
                'county': crime_data['county'],
                'violent_crime_count': crime_data['violent_crime']['total_count'],
                'property_crime_count': crime_data['property_crime']['total_count']
            }

            # Calculate rates if population data available
            if population_data and fips in population_data:
                pop = population_data[fips]
                if pop > 0:
                    rates_data[fips]['population'] = pop
                    rates_data[fips]['violent_crime_rate'] = \
                        (crime_data['violent_crime']['total_count'] / pop) * 100000
                    rates_data[fips]['property_crime_rate'] = \
                        (crime_data['property_crime']['total_count'] / pop) * 100000

        # Save rates data
        output_file = self.output_dir / f'crime_rates_{self.year}.json'
        with open(output_file, 'w') as f:
            json.dump(rates_data, f, indent=2)
        logger.info(f"Saved crime rates to {output_file}")

        return rates_data

    def run_full_collection(
        self,
        states: Optional[List[str]] = None,
        limit: Optional[int] = None
    ):
        """
        Run the full crime data collection pipeline.

        Args:
            states: List of state names to collect. None = all states.
            limit: Maximum number of agencies to fetch (for testing).
        """
        logger.info(f"Starting crime data collection for year {self.year}")

        # Step 1: Fetch agency-level data
        logger.info("Step 1: Fetching agency-level data from FBI API...")
        agency_data = self.fetch_all_agency_data(states=states, limit=limit)

        # Step 2: Aggregate to counties
        logger.info("Step 2: Aggregating to county level...")
        county_data = self.aggregate_to_counties(agency_data)

        # Step 3: Aggregate to regions
        logger.info("Step 3: Aggregating to regional level...")
        region_data = self.aggregate_to_regions(county_data)

        # Step 4: Calculate rates (would need Census population data)
        logger.info("Step 4: Calculating crime rates...")
        # rates_data = self.calculate_crime_rates(county_data)
        logger.info("(Skipping rate calculation - needs Census population data)")

        logger.info("Crime data collection complete!")
        logger.info(f"  - {len(agency_data)} agencies")
        logger.info(f"  - {len(county_data)} counties")
        logger.info(f"  - {len(region_data)} regions")


def main():
    """Main entry point for crime data collection."""
    parser = argparse.ArgumentParser(description='Collect FBI crime data for Thriving Index')
    parser.add_argument('--year', type=int, default=2024, help='Year to collect data for')
    parser.add_argument('--states', nargs='+', help='Specific states to collect (e.g., VIRGINIA MARYLAND)')
    parser.add_argument('--limit', type=int, help='Limit number of agencies (for testing)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get API key from environment
    api_key = os.getenv('FBI_UCR_KEY')
    if not api_key:
        logger.error("FBI_UCR_KEY environment variable not set")
        sys.exit(1)

    # Create collector and run
    collector = CrimeDataCollector(api_key=api_key, year=args.year)
    collector.run_full_collection(states=args.states, limit=args.limit)


if __name__ == '__main__':
    main()
