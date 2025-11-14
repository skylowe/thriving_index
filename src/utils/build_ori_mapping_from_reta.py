"""
Build ORI-to-FIPS mapping from RETA data

Parses the RETA master file to extract unique agencies and their locations,
then matches them to county FIPS codes.
"""

import logging
from pathlib import Path
from typing import Dict, Set
import json

from src.parsers.fbi_ucr_parser import FBIUCRReturnAParser
from data.county_fips_reference import get_county_fips

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RETAORIMapper:
    """Extract ORI-to-FIPS mapping from RETA data."""

    # Extended field positions for address extraction
    # Based on RETA record description
    CITY_NAME = (45, 69)
    STATE_NAME = (70, 95)
    COUNTY_CODE = (270, 272)  # 3-digit county code within state

    def __init__(self, reta_file: Path):
        """Initialize with RETA file path."""
        self.reta_file = reta_file
        self.parser = FBIUCRReturnAParser(reta_file)

    def _extract_field(self, record: str, positions: tuple) -> str:
        """Extract field from record."""
        start, end = positions
        return record[start-1:end].strip()

    def _match_city_to_county(self, city: str, state: str) -> str:
        """
        Match a city name to its county.

        This is a simplified approach - in practice, cities can span
        multiple counties or be independent cities (in Virginia).

        Args:
            city: City name
            state: State abbreviation

        Returns:
            County FIPS code or None
        """
        # Handle Virginia independent cities
        if state == 'VA':
            from data.county_fips_reference import VIRGINIA_COUNTIES
            city_norm = city.upper().strip()

            # Check if it's an independent city
            if city_norm in VIRGINIA_COUNTIES:
                return VIRGINIA_COUNTIES[city_norm]

        # For other cases, we'll need a city-to-county mapping
        # This is complex and would require a comprehensive database
        # For now, return None and handle manually
        return None

    def extract_agencies(self) -> Dict[str, Dict]:
        """
        Extract unique agencies from RETA file.

        Returns:
            Dictionary mapping ORI -> agency info
        """
        logger.info(f"Parsing RETA file: {self.reta_file}")

        agencies = {}
        target_states = {'VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC'}

        with open(self.reta_file, 'r', encoding='latin-1') as f:
            record_num = 0
            for line in f:
                record_num += 1

                if len(line) < 7385:
                    continue

                # Extract state code
                state_code = self._extract_field(line, (2, 3))
                state = self.parser.STATE_CODES.get(state_code, '')

                if state not in target_states:
                    continue

                # Extract agency info
                ori = self._extract_field(line, (4, 10))
                city = self._extract_field(line, self.CITY_NAME)
                county_code = self._extract_field(line, self.COUNTY_CODE)

                if ori and ori not in agencies:
                    agencies[ori] = {
                        'ori': ori,
                        'state': state,
                        'state_code': state_code,
                        'city': city,
                        'county_code': county_code
                    }

                if record_num % 10000 == 0:
                    logger.info(f"Processed {record_num} records, found {len(agencies)} target agencies")

        logger.info(f"Extracted {len(agencies)} unique agencies")
        return agencies

    def build_ori_to_fips_mapping(self, agencies: Dict[str, Dict]) -> Dict[str, str]:
        """
        Build ORI-to-FIPS mapping from agency data.

        Args:
            agencies: Dictionary of agency information

        Returns:
            Dictionary mapping ORI -> FIPS code
        """
        from data.county_fips_reference import COUNTIES_BY_STATE

        STATE_FIPS = {
            'VA': '51', 'MD': '24', 'WV': '54',
            'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'
        }

        mapping = {}

        for ori, info in agencies.items():
            state = info['state']
            county_code = info['county_code']

            # DC special case
            if state == 'DC':
                mapping[ori] = '11001'
                continue

            # Try to build FIPS from state + county code
            if county_code and county_code.strip():
                # Clean county code
                county_code_clean = county_code.strip()

                # Check if it's numeric
                if county_code_clean.isdigit():
                    state_fips = STATE_FIPS.get(state)
                    if state_fips:
                        fips = f"{state_fips}{county_code_clean.zfill(3)}"

                        # For debugging, just accept all county codes for now
                        # We'll validate later
                        mapping[ori] = fips
                        continue

            # If county code didn't work, try city matching
            city = info['city']
            fips = self._match_city_to_county(city, state)
            if fips:
                mapping[ori] = fips

        logger.info(f"Mapped {len(mapping)} agencies to FIPS codes")
        return mapping

    def save_mapping(self, mapping: Dict[str, str], output_file: Path):
        """Save mapping to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        logger.info(f"Saved mapping to {output_file}")

    def save_agencies(self, agencies: Dict[str, Dict], output_file: Path):
        """Save agency info for manual mapping."""
        with open(output_file, 'w') as f:
            json.dump(agencies, f, indent=2)
        logger.info(f"Saved agency info to {output_file}")


def main():
    """Main execution."""
    reta_file = Path('data/crime/raw/2024_RETA_NATIONAL_MASTER_FILE.txt')

    if not reta_file.exists():
        logger.error(f"RETA file not found: {reta_file}")
        return

    # Create mapper
    mapper = RETAORIMapper(reta_file)

    # Extract agencies
    logger.info("Extracting agencies from RETA file...")
    agencies = mapper.extract_agencies()

    # Save agency info for reference
    agencies_file = Path('data/processed/reta_agencies.json')
    agencies_file.parent.mkdir(parents=True, exist_ok=True)
    mapper.save_agencies(agencies, agencies_file)

    # Build ORI-to-FIPS mapping
    logger.info("Building ORI-to-FIPS mapping...")
    mapping = mapper.build_ori_to_fips_mapping(agencies)

    # Save mapping
    mapping_file = Path('data/processed/ori_to_fips_mapping.json')
    mapper.save_mapping(mapping, mapping_file)

    # Print statistics
    print("\n" + "="*60)
    print("ORI-to-FIPS Mapping Statistics")
    print("="*60)
    print(f"Total agencies extracted: {len(agencies)}")
    print(f"Successfully mapped: {len(mapping)}")
    print(f"Need manual mapping: {len(agencies) - len(mapping)}")

    # Show breakdown by state
    print("\nBy State:")
    for state in ['VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC']:
        state_agencies = [a for a in agencies.values() if a['state'] == state]
        state_mapped = [o for o, a in agencies.items() if a['state'] == state and o in mapping]
        print(f"  {state}: {len(state_mapped)}/{len(state_agencies)} mapped")

    # Show some unmapped agencies
    unmapped = [a for o, a in agencies.items() if o not in mapping]
    if unmapped:
        print(f"\nSample of {min(10, len(unmapped))} unmapped agencies:")
        for agency in unmapped[:10]:
            print(f"  {agency['ori']}: {agency['city']}, {agency['state']} (county code: {agency['county_code']})")


if __name__ == '__main__':
    main()
