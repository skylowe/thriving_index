"""
FBI UCR Return A (RETA) Data Parser

This module parses the FBI Uniform Crime Reporting Return A master file,
which contains monthly crime statistics from law enforcement agencies.

Data Format: Fixed-length, unpacked format (7,385 bytes per record)
Coverage: Law enforcement agencies nationwide
Time Period: Monthly data for a single year

For the Virginia Thriving Index, we extract:
- Violent crime counts (murder, rape, robbery, assault)
- Property crime counts (burglary, larceny, motor vehicle theft)
- Agency population for rate calculations
- Agency location (state, county) for aggregation
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FBIUCRReturnAParser:
    """
    Parser for FBI UCR Return A (RETA) master files.

    The Return A contains monthly crime statistics from participating
    law enforcement agencies. Data is in fixed-width format.
    """

    # Record length
    RECORD_LENGTH = 7385

    # Header field positions (1-indexed as per documentation)
    IDENTIFIER = (1, 1)
    STATE_CODE = (2, 3)
    GROUP = (11, 12)
    DIVISION = (13, 13)
    YEAR = (14, 15)
    SEQUENCE_NUMBER = (16, 20)
    JUVENILE_AGE = (21, 22)
    CORE_CITY = (23, 23)
    ORI_CODE = (4, 10)
    COVERED_BY = (24, 30)
    COVERED_BY_GROUP = (31, 31)
    LAST_UPDATE = (32, 37)
    FIELD_OFFICE = (38, 41)
    NUM_MONTHS = (42, 43)

    # Population fields
    POP_CITY = (45, 53)
    POP_COUNTY = (54, 56)
    POP_MSA = (57, 59)
    POP_DATA_2 = (60, 74)
    POP_DATA_3 = (75, 89)
    POPULATION_LAST_CENSUS = (90, 116)

    # Agency identification
    CITY_NAME = (45, 69)  # Position adjusted based on actual data
    STATE_NAME = (70, 95)
    AGENCY_NAME = (121, 144)
    ADDRESS_LINE_1 = (151, 180)
    ADDRESS_LINE_2 = (181, 210)
    ZIP_CODE = (271, 275)

    # State codes (numeric)
    STATE_CODES = {
        '01': 'AL', '02': 'AZ', '03': 'AR', '04': 'AS', '05': 'CO',
        '06': 'CT', '07': 'DE', '08': 'DC', '09': 'FL', '10': 'GA',
        '11': 'ID', '12': 'IL', '13': 'IN', '14': 'IA', '15': 'KS',
        '16': 'KY', '17': 'LA', '18': 'ME', '19': 'MD', '20': 'MA',
        '21': 'MI', '22': 'MN', '23': 'MS', '24': 'MO', '25': 'MT',
        '26': 'NE', '27': 'NV', '28': 'NH', '29': 'NJ', '30': 'NM',
        '31': 'NY', '32': 'NC', '33': 'ND', '34': 'OH', '35': 'OK',
        '36': 'OR', '37': 'PA', '38': 'RI', '39': 'SC', '40': 'SD',
        '41': 'TN', '42': 'TX', '43': 'UT', '44': 'VT', '45': 'VA',
        '46': 'WA', '47': 'WV', '48': 'WI', '49': 'WY', '50': 'AK',
        '51': 'HI', '52': 'CZ', '53': 'PR', '54': 'AS', '55': 'GM',
        '62': 'VI'
    }

    # Monthly data starts at position 306
    # Each month occupies 590 bytes (positions 306-895 for 12 months)
    MONTH_DATA_START = 306
    MONTH_DATA_LENGTH = 590

    # Card 0 - Number of Unfounded Offenses (positions 323-462 within each month)
    # Card 1 - Number of Actual Offenses (positions 463-602 within each month)
    # Offsets within each month block
    CARD_0_OFFSET = 17   # positions 323-462 (unfounded)
    CARD_1_OFFSET = 157  # positions 463-602 (actual)

    # Crime field positions within each card (28 fields, 5 digits each = 140 bytes)
    # Positions relative to card start
    MURDER = (0, 4)              # Field 1
    MANSLAUGHTER = (5, 9)        # Field 2
    RAPE_TOTAL = (10, 14)        # Field 3
    RAPE_BY_FORCE = (15, 19)     # Field 4
    ATTEMPTED_RAPE = (20, 24)    # Field 5
    ROBBERY_TOTAL = (25, 29)     # Field 6
    ROBBERY_GUN = (30, 34)       # Field 7
    ROBBERY_KNIFE = (35, 39)     # Field 8
    ROBBERY_OTHER = (40, 44)     # Field 9
    ROBBERY_STRONGARM = (45, 49) # Field 10
    ASSAULT_TOTAL = (50, 54)     # Field 11
    ASSAULT_GUN = (55, 59)       # Field 12
    ASSAULT_KNIFE = (60, 64)     # Field 13
    ASSAULT_OTHER = (65, 69)     # Field 14
    ASSAULT_HANDS = (70, 74)     # Field 15
    SIMPLE_ASSAULT = (75, 79)    # Field 16
    BURGLARY_TOTAL = (80, 84)    # Field 17
    BURGLARY_FORCIBLE = (85, 89) # Field 18
    BURGLARY_NO_FORCE = (90, 94) # Field 19
    BURGLARY_ATTEMPT = (95, 99)  # Field 20
    LARCENY_TOTAL = (100, 104)   # Field 21
    MVT_TOTAL = (105, 109)       # Field 22
    AUTO_THEFT = (110, 114)      # Field 23
    TRUCK_THEFT = (115, 119)     # Field 24
    OTHER_VEHICLE = (120, 124)   # Field 25
    GRAND_TOTAL = (125, 129)     # Field 26
    LARCENY_UNDER_50 = (130, 134)# Field 27
    # Field 28 (135-139) is unused

    # Negative value encoding
    NEGATIVE_CODES = {
        '}': 0, 'J': -1, 'K': -2, 'L': -3, 'M': -4, 'N': -5, 'O': -6,
        'P': -7, 'Q': -8, 'R': -9, '1}': -10, '1J': -11, '1K': -12,
        '1L': -13, '1M': -14, '1N': -15
    }

    def __init__(self, data_file: Path):
        """
        Initialize parser with path to RETA master file.

        Args:
            data_file: Path to the fixed-width RETA master file
        """
        self.data_file = data_file

    def _extract_field(self, record: str, positions: Tuple[int, int]) -> str:
        """
        Extract a field from a fixed-width record.

        Args:
            record: The full record string
            positions: Tuple of (start, end) positions (1-indexed)

        Returns:
            Extracted field value, stripped of whitespace
        """
        start, end = positions
        # Convert from 1-indexed to 0-indexed
        return record[start-1:end].strip()

    def _parse_numeric_field(self, value: str) -> Optional[int]:
        """
        Parse a numeric field, handling negative value codes.

        Args:
            value: String value which may contain negative codes

        Returns:
            Integer value, or None if blank/invalid
        """
        if not value or value.isspace():
            return 0

        # Check for negative value codes
        for code, num in self.NEGATIVE_CODES.items():
            if code in value:
                return num

        # Regular numeric value
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Could not parse numeric value: {value}")
            return None

    def _extract_month_data(self, record: str, month_index: int) -> Dict[str, int]:
        """
        Extract crime data for a specific month.

        Args:
            record: The full record string
            month_index: Month number (0-11 for Jan-Dec)

        Returns:
            Dictionary of crime counts for the month
        """
        # Calculate starting position for this month's data
        month_start = self.MONTH_DATA_START - 1 + (month_index * self.MONTH_DATA_LENGTH)

        # Extract Card 1 (Actual Offenses) - this is what we want for crime rates
        card1_start = month_start + self.CARD_1_OFFSET

        # Extract crime counts
        crimes = {}

        # Helper function to extract crime count
        def get_count(field_positions):
            start, end = field_positions
            value = record[card1_start + start:card1_start + end + 1]
            return self._parse_numeric_field(value) or 0

        # Extract all crime categories
        crimes['murder'] = get_count(self.MURDER)
        crimes['manslaughter'] = get_count(self.MANSLAUGHTER)
        crimes['rape_total'] = get_count(self.RAPE_TOTAL)
        crimes['robbery_total'] = get_count(self.ROBBERY_TOTAL)
        crimes['assault_total'] = get_count(self.ASSAULT_TOTAL)
        crimes['burglary_total'] = get_count(self.BURGLARY_TOTAL)
        crimes['larceny_total'] = get_count(self.LARCENY_TOTAL)
        crimes['mvt_total'] = get_count(self.MVT_TOTAL)

        # Calculate composite rates
        crimes['violent_crime'] = (
            crimes['murder'] + crimes['manslaughter'] +
            crimes['rape_total'] + crimes['robbery_total'] +
            crimes['assault_total']
        )

        crimes['property_crime'] = (
            crimes['burglary_total'] + crimes['larceny_total'] +
            crimes['mvt_total']
        )

        return crimes

    def _parse_record(self, record: str) -> Optional[Dict]:
        """
        Parse a single RETA record.

        Args:
            record: Fixed-width record string

        Returns:
            Dictionary of parsed data, or None if record is invalid
        """
        if len(record) < self.RECORD_LENGTH:
            logger.warning(f"Record too short: {len(record)} bytes")
            return None

        # Extract header information
        state_code = self._extract_field(record, self.STATE_CODE)
        state = self.STATE_CODES.get(state_code, state_code)

        # Filter to our target states
        target_states = {'VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC'}
        if state not in target_states:
            return None

        ori = self._extract_field(record, self.ORI_CODE)
        year = self._extract_field(record, self.YEAR)
        num_months = self._extract_field(record, self.NUM_MONTHS)

        # Extract population (from population fields)
        pop_str = self._extract_field(record, self.POP_CITY)
        population = self._parse_numeric_field(pop_str) or 0

        # Group code tells us what type of jurisdiction
        group = self._extract_field(record, self.GROUP)

        # Aggregate annual crime data
        annual_crimes = {
            'murder': 0, 'manslaughter': 0, 'rape_total': 0,
            'robbery_total': 0, 'assault_total': 0, 'burglary_total': 0,
            'larceny_total': 0, 'mvt_total': 0,
            'violent_crime': 0, 'property_crime': 0
        }

        # Extract and sum data for all reported months
        months_reported = self._parse_numeric_field(num_months) or 0
        for month_idx in range(min(months_reported, 12)):
            month_data = self._extract_month_data(record, month_idx)
            for crime_type, count in month_data.items():
                annual_crimes[crime_type] += count

        return {
            'ori': ori,
            'state': state,
            'state_code': state_code,
            'year': f"20{year}" if len(year) == 2 else year,
            'group': group,
            'population': population,
            'months_reported': months_reported,
            **annual_crimes
        }

    def parse(self) -> List[Dict]:
        """
        Parse the entire RETA master file.

        Returns:
            List of dictionaries containing parsed agency crime data
        """
        logger.info(f"Parsing FBI UCR RETA file: {self.data_file}")

        results = []

        with open(self.data_file, 'r', encoding='latin-1') as f:
            record_num = 0
            for line in f:
                record_num += 1

                if record_num % 1000 == 0:
                    logger.info(f"Processed {record_num} records, found {len(results)} target agencies")

                parsed = self._parse_record(line)
                if parsed:
                    results.append(parsed)

        logger.info(f"Parsing complete: {len(results)} agencies from target states")
        return results

    def aggregate_by_county(self, parsed_data: List[Dict],
                           ori_to_fips_map: Dict[str, str]) -> Dict[str, Dict]:
        """
        Aggregate agency-level crime data to county level.

        Args:
            parsed_data: List of parsed agency records
            ori_to_fips_map: Mapping of ORI codes to county FIPS codes

        Returns:
            Dictionary mapping FIPS codes to aggregated crime data
        """
        logger.info("Aggregating crime data to county level")

        county_data = {}

        for agency in parsed_data:
            ori = agency['ori']

            # Look up county FIPS code
            fips = ori_to_fips_map.get(ori)
            if not fips:
                logger.debug(f"No FIPS mapping found for ORI: {ori}")
                continue

            # Initialize county data if not exists
            if fips not in county_data:
                county_data[fips] = {
                    'fips': fips,
                    'state': agency['state'],
                    'population': 0,
                    'agencies': [],
                    'murder': 0, 'manslaughter': 0, 'rape_total': 0,
                    'robbery_total': 0, 'assault_total': 0,
                    'burglary_total': 0, 'larceny_total': 0, 'mvt_total': 0,
                    'violent_crime': 0, 'property_crime': 0
                }

            # Add agency data to county totals
            county_data[fips]['agencies'].append(ori)
            county_data[fips]['population'] += agency['population']

            for crime_type in ['murder', 'manslaughter', 'rape_total', 'robbery_total',
                              'assault_total', 'burglary_total', 'larceny_total',
                              'mvt_total', 'violent_crime', 'property_crime']:
                county_data[fips][crime_type] += agency[crime_type]

        logger.info(f"Aggregated data for {len(county_data)} counties")
        return county_data


def extract_crime_data(reta_file: Path, ori_to_fips_map: Dict[str, str]) -> Dict[str, Dict]:
    """
    Main function to extract and aggregate FBI UCR crime data.

    Args:
        reta_file: Path to RETA master file
        ori_to_fips_map: Mapping of ORI codes to county FIPS codes

    Returns:
        Dictionary mapping FIPS codes to aggregated crime statistics
    """
    parser = FBIUCRReturnAParser(reta_file)
    parsed_data = parser.parse()
    county_data = parser.aggregate_by_county(parsed_data, ori_to_fips_map)

    return county_data
