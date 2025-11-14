"""
ORI to FIPS Code Mapping Utility

Creates a mapping from FBI Originating Agency Identifier (ORI) codes to
county FIPS codes for crime data aggregation.

ORI codes identify individual law enforcement agencies. This utility:
1. Fetches agency information from FBI UCR API for each state
2. Extracts county names from agency records
3. Matches county names to FIPS codes
4. Creates a persistent ORI-to-FIPS mapping file
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import time

from src.api_clients.fbi_ucr_api import FBIUCRAPI
from src.utils.config import CacheConfig
from src.utils.logging_setup import setup_logger


logger = setup_logger(__name__)


class ORIToFIPSMapper:
    """
    Maps FBI ORI codes to county FIPS codes.

    Uses FBI UCR API to fetch agency information and matches
    agencies to counties based on geographic information.
    """

    # State abbreviations for the study
    TARGET_STATES = ['VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC']

    # State FIPS codes
    STATE_FIPS = {
        'VA': '51',
        'MD': '24',
        'WV': '54',
        'NC': '37',
        'TN': '47',
        'KY': '21',
        'DC': '11'
    }

    def __init__(self):
        """Initialize the ORI to FIPS mapper."""
        self.api_client = FBIUCRAPI()
        self.mapping_file = Path('data/processed/ori_to_fips_mapping.json')
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)

        # Load county names to FIPS codes
        self.county_fips_map = self._load_county_fips_map()

    def _load_county_fips_map(self) -> Dict[str, Dict[str, str]]:
        """
        Load county name to FIPS code mapping.

        Returns:
            Dictionary mapping state -> county name -> FIPS code
        """
        from data.county_fips_reference import COUNTIES_BY_STATE

        logger.info(f"Loaded FIPS codes for {len(COUNTIES_BY_STATE)} states")
        return COUNTIES_BY_STATE

    def _normalize_county_name(self, county_name: str) -> str:
        """
        Normalize county name for matching.

        Args:
            county_name: Raw county name from API

        Returns:
            Normalized county name
        """
        if not county_name:
            return ""

        # Remove common suffixes
        name = county_name.strip().upper()
        for suffix in [' COUNTY', ' PARISH', ' CITY', ' BOROUGH']:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()

        return name

    def _match_county_to_fips(
        self,
        county_name: str,
        state_abbr: str
    ) -> Optional[str]:
        """
        Match a county name to its FIPS code.

        Args:
            county_name: County name from agency record
            state_abbr: State abbreviation

        Returns:
            5-digit FIPS code or None if not found
        """
        if not county_name or state_abbr not in self.STATE_FIPS:
            return None

        # Special case for DC
        if state_abbr == 'DC':
            return '11001'  # DC has single FIPS code

        # Get normalized county name
        normalized = self._normalize_county_name(county_name)

        if not normalized:
            return None

        # Look up in county FIPS map
        if state_abbr in self.county_fips_map:
            fips = self.county_fips_map[state_abbr].get(normalized)
            if fips:
                return fips

        # Try fuzzy matching for common variations
        # E.g., "ST. MARY'S" vs "ST. MARYS", "PRINCE GEORGE'S" vs "PRINCE GEORGES"
        if state_abbr in self.county_fips_map:
            # Try removing apostrophes and periods
            alt_normalized = normalized.replace("'", "").replace(".", "")
            for county, fips in self.county_fips_map[state_abbr].items():
                alt_county = county.replace("'", "").replace(".", "")
                if alt_normalized == alt_county:
                    return fips

        return None

    def fetch_agencies_for_state(self, state_abbr: str) -> List[Dict]:
        """
        Fetch all law enforcement agencies for a state.

        Args:
            state_abbr: State abbreviation (e.g., 'VA')

        Returns:
            List of agency records
        """
        logger.info(f"Fetching agencies for {state_abbr}")

        try:
            response = self.api_client.get_agencies_by_state(state_abbr)

            if response and 'data' in response:
                agencies = response['data']
                logger.info(f"Found {len(agencies)} agencies in {state_abbr}")
                return agencies
            else:
                logger.warning(f"No agency data returned for {state_abbr}")
                return []

        except Exception as e:
            logger.error(f"Failed to fetch agencies for {state_abbr}: {e}")
            return []

    def build_mapping(
        self,
        states: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Build ORI to FIPS mapping for target states.

        Args:
            states: List of state abbreviations (defaults to TARGET_STATES)

        Returns:
            Dictionary mapping ORI codes to FIPS codes
        """
        if states is None:
            states = self.TARGET_STATES

        ori_to_fips = {}

        for state_abbr in states:
            logger.info(f"Processing {state_abbr}...")

            # Fetch agencies
            agencies = self.fetch_agencies_for_state(state_abbr)

            # Map each agency to county FIPS
            for agency in agencies:
                ori = agency.get('ori')
                county_name = agency.get('county_name', '')

                if ori:
                    # Try to match county to FIPS
                    fips = self._match_county_to_fips(county_name, state_abbr)

                    if fips:
                        ori_to_fips[ori] = fips
                    else:
                        # Store with county name for manual matching
                        ori_to_fips[ori] = {
                            'county_name': county_name,
                            'state': state_abbr,
                            'agency_name': agency.get('agency_name', ''),
                            'needs_manual_mapping': True
                        }

            # Rate limiting
            time.sleep(1.0)

        logger.info(f"Built mapping for {len(ori_to_fips)} agencies")
        return ori_to_fips

    def save_mapping(self, mapping: Dict[str, str]):
        """
        Save ORI to FIPS mapping to file.

        Args:
            mapping: Dictionary mapping ORI codes to FIPS codes
        """
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)

        logger.info(f"Saved mapping to {self.mapping_file}")

    def load_mapping(self) -> Optional[Dict[str, str]]:
        """
        Load ORI to FIPS mapping from file.

        Returns:
            Dictionary mapping ORI codes to FIPS codes, or None if not found
        """
        if not self.mapping_file.exists():
            logger.warning(f"Mapping file not found: {self.mapping_file}")
            return None

        with open(self.mapping_file, 'r') as f:
            mapping = json.load(f)

        logger.info(f"Loaded mapping for {len(mapping)} agencies")
        return mapping

    def create_mapping(
        self,
        force_refresh: bool = False
    ) -> Dict[str, str]:
        """
        Create or load ORI to FIPS mapping.

        Args:
            force_refresh: If True, rebuild mapping even if file exists

        Returns:
            Dictionary mapping ORI codes to FIPS codes
        """
        # Check if mapping already exists
        if not force_refresh and self.mapping_file.exists():
            logger.info("Loading existing ORI to FIPS mapping")
            return self.load_mapping()

        # Build new mapping
        logger.info("Building new ORI to FIPS mapping")
        mapping = self.build_mapping()

        # Save to file
        self.save_mapping(mapping)

        return mapping


def create_ori_fips_mapping(force_refresh: bool = False) -> Dict[str, str]:
    """
    Convenience function to create ORI to FIPS mapping.

    Args:
        force_refresh: If True, rebuild mapping even if file exists

    Returns:
        Dictionary mapping ORI codes to FIPS codes
    """
    mapper = ORIToFIPSMapper()
    return mapper.create_mapping(force_refresh=force_refresh)


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create mapping
    print("Creating ORI to FIPS mapping...")
    mapping = create_ori_fips_mapping(force_refresh=True)

    # Print statistics
    mapped = sum(1 for v in mapping.values() if isinstance(v, str))
    needs_mapping = sum(1 for v in mapping.values() if isinstance(v, dict))

    print(f"\nMapping Statistics:")
    print(f"  Total agencies: {len(mapping)}")
    print(f"  Successfully mapped: {mapped}")
    print(f"  Needs manual mapping: {needs_mapping}")

    if needs_mapping > 0:
        print(f"\nSample agencies needing manual mapping:")
        count = 0
        for ori, info in mapping.items():
            if isinstance(info, dict):
                print(f"  {ori}: {info['agency_name']} - {info['county_name']}, {info['state']}")
                count += 1
                if count >= 10:
                    break
