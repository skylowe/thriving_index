"""
ORI Crosswalk Loader

Loads and parses the FBI ORI-to-FIPS crosswalk file to map law enforcement
agencies (identified by ORI codes) to county FIPS codes.

Source: Law Enforcement Agency Identifiers Crosswalk, United States, 2012 (ICPSR 35158)
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Target states for the Thriving Index project
TARGET_STATES = {
    'VIRGINIA': '51',
    'MARYLAND': '24',
    'WEST VIRGINIA': '54',
    'NORTH CAROLINA': '37',
    'TENNESSEE': '47',
    'KENTUCKY': '21',
    'DISTRICT OF COLUMBIA': '11'
}


class ORICrosswalk:
    """Manages ORI-to-FIPS mapping for law enforcement agencies."""

    def __init__(self, crosswalk_path: Optional[str] = None):
        """
        Initialize the ORI crosswalk.

        Args:
            crosswalk_path: Path to the ori_crosswalk.tsv file.
                           If None, uses default location.
        """
        if crosswalk_path is None:
            # Default to data/crime/raw/ori_crosswalk.tsv
            base_path = Path(__file__).parent.parent.parent
            crosswalk_path = base_path / 'data' / 'crime' / 'raw' / 'ori_crosswalk.tsv'

        self.crosswalk_path = Path(crosswalk_path)
        self.ori_to_fips: Dict[str, Dict] = {}  # ORI9 -> FIPS mapping
        self.fips_to_oris: Dict[str, List[str]] = {}  # FIPS -> list of ORI9 codes

        self._load_crosswalk()

    def _load_crosswalk(self):
        """Load the ORI crosswalk file and build lookup dictionaries."""
        logger.info(f"Loading ORI crosswalk from {self.crosswalk_path}")

        if not self.crosswalk_path.exists():
            raise FileNotFoundError(f"Crosswalk file not found: {self.crosswalk_path}")

        with open(self.crosswalk_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                # Extract key fields
                ori7 = row.get('ORI7', '').strip()
                ori9 = row.get('ORI9', '').strip()
                fips = row.get('FIPS', '').strip()
                fstate = row.get('FSTATE', '').strip()
                fcounty = row.get('FCOUNTY', '').strip()
                statename = row.get('STATENAME', '').strip().upper()
                countyname = row.get('COUNTYNAME', '').strip()
                agency_name = row.get('NAME', '').strip()

                # Skip records without valid ORI9, ORI7, or FIPS
                if ori9 == '-1' or ori7 == '-1' or not ori9 or not fips or fips == '-9':
                    continue

                # Filter for target states only
                if statename not in TARGET_STATES:
                    continue

                # Store ORI9-to-FIPS mapping (FBI API uses ORI9)
                self.ori_to_fips[ori9] = {
                    'ori7': ori7,
                    'ori9': ori9,
                    'fips': fips,
                    'fips_state': fstate,
                    'fips_county': fcounty,
                    'state': statename,
                    'county': countyname,
                    'agency_name': agency_name
                }

                # Store FIPS-to-ORIs reverse mapping (one county has multiple agencies)
                # Store ORI9 codes since that's what the FBI API requires
                if fips not in self.fips_to_oris:
                    self.fips_to_oris[fips] = []
                self.fips_to_oris[fips].append(ori9)

        logger.info(f"Loaded {len(self.ori_to_fips)} ORI codes for target states")
        logger.info(f"Covering {len(self.fips_to_oris)} counties")

        # Log counts by state
        state_counts = {}
        for ori_data in self.ori_to_fips.values():
            state = ori_data['state']
            state_counts[state] = state_counts.get(state, 0) + 1

        for state, count in sorted(state_counts.items()):
            logger.info(f"  {state}: {count} agencies")

    def get_fips_for_ori(self, ori: str) -> Optional[str]:
        """
        Get the FIPS county code for a given ORI code.

        Args:
            ori: 9-character ORI code (FBI API format)

        Returns:
            FIPS code (5-character) or None if not found
        """
        ori_data = self.ori_to_fips.get(ori)
        return ori_data['fips'] if ori_data else None

    def get_oris_for_fips(self, fips: str) -> List[str]:
        """
        Get all ORI codes for a given FIPS county code.

        Args:
            fips: 5-character FIPS code

        Returns:
            List of ORI9 codes for that county (FBI API format)
        """
        return self.fips_to_oris.get(fips, [])

    def get_all_oris_for_state(self, state_name: str) -> List[str]:
        """
        Get all ORI codes for a given state.

        Args:
            state_name: State name (e.g., 'VIRGINIA')

        Returns:
            List of ORI9 codes for that state (FBI API format)
        """
        state_name = state_name.upper()
        return [
            ori for ori, data in self.ori_to_fips.items()
            if data['state'] == state_name
        ]

    def get_all_fips_codes(self) -> List[str]:
        """Get all FIPS codes in the crosswalk."""
        return list(self.fips_to_oris.keys())

    def get_all_ori_codes(self) -> List[str]:
        """
        Get all ORI codes in the crosswalk.

        Returns:
            List of ORI9 codes (FBI API format)
        """
        return list(self.ori_to_fips.keys())

    def get_ori_info(self, ori: str) -> Optional[Dict]:
        """
        Get full information for an ORI code.

        Args:
            ori: 9-character ORI code (FBI API format)

        Returns:
            Dictionary with ORI information or None if not found
        """
        return self.ori_to_fips.get(ori)


if __name__ == '__main__':
    # Test the crosswalk loader
    logging.basicConfig(level=logging.INFO)

    crosswalk = ORICrosswalk()

    print("\nSample Virginia agencies:")
    va_oris = crosswalk.get_all_oris_for_state('VIRGINIA')
    for ori in va_oris[:10]:
        info = crosswalk.get_ori_info(ori)
        print(f"  {ori}: {info['agency_name']} ({info['county']} County)")

    print(f"\nTotal VA agencies: {len(va_oris)}")
