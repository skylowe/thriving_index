"""
CBSA (Core-Based Statistical Area) Classifications

Maps counties to their metropolitan/micropolitan/rural status based on
Census Bureau CBSA definitions (2023).

Classifications:
- Metropolitan: Urban area 50,000+ population
- Micropolitan: Urban area 10,000-49,999 population
- Rural: Neither metropolitan nor micropolitan

Source: U.S. Census Bureau CBSA Delineation Files
"""

from typing import Dict

# CBSA classifications for all counties in the study
# Format: {FIPS: {'name': 'County Name', 'cbsa': 'metro'|'micro'|'rural', 'cbsa_name': 'MSA Name'}}

CBSA_CLASSIFICATIONS = {
    # Virginia - Major Metro Areas
    '51013': {'name': 'Arlington', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51059': {'name': 'Fairfax', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51107': {'name': 'Loudoun', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51153': {'name': 'Prince William', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51510': {'name': 'Alexandria City', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51600': {'name': 'Fairfax City', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51610': {'name': 'Falls Church City', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51683': {'name': 'Manassas City', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51685': {'name': 'Manassas Park City', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},

    # Virginia - Richmond Metro
    '51041': {'name': 'Chesterfield', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51085': {'name': 'Hanover', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51087': {'name': 'Henrico', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51760': {'name': 'Richmond City', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},

    # Virginia - Hampton Roads Metro
    '51093': {'name': 'Isle of Wight', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51095': {'name': 'James City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51199': {'name': 'York', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51550': {'name': 'Chesapeake City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51650': {'name': 'Hampton City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51700': {'name': 'Newport News City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51710': {'name': 'Norfolk City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51735': {'name': 'Poquoson City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51740': {'name': 'Portsmouth City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51800': {'name': 'Suffolk City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},
    '51810': {'name': 'Virginia Beach City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Norfolk-Newport News, VA-NC'},

    # District of Columbia
    '11001': {'name': 'District of Columbia', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},

    # Maryland - Baltimore Metro
    '24005': {'name': 'Baltimore', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24013': {'name': 'Carroll', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24025': {'name': 'Harford', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24027': {'name': 'Howard', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24510': {'name': 'Baltimore City', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},

    # Maryland - DC Metro
    '24021': {'name': 'Frederick', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '24031': {'name': 'Montgomery', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '24033': {'name': "Prince George's", 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
}

# Classification summary counts
CBSA_SUMMARY = {
    'total_counties': 0,  # Will be updated when all classifications added
    'metropolitan': 0,
    'micropolitan': 0,
    'rural': 0
}


def get_cbsa_classification(fips: str) -> Dict:
    """
    Get CBSA classification for a county.

    Args:
        fips: 5-digit FIPS code

    Returns:
        Dictionary with classification info, or default rural if not found
    """
    return CBSA_CLASSIFICATIONS.get(fips, {
        'name': 'Unknown',
        'cbsa': 'rural',
        'cbsa_name': None
    })


def get_micropolitan_percentage(fips_list: list) -> float:
    """
    Calculate percentage of population in micropolitan areas.

    Args:
        fips_list: List of FIPS codes for a region

    Returns:
        Percentage (0-100) of area classified as micropolitan
    """
    total = len(fips_list)
    if total == 0:
        return 0.0

    micro_count = sum(1 for fips in fips_list
                      if get_cbsa_classification(fips)['cbsa'] == 'micro')

    return (micro_count / total) * 100


def classify_region_type(fips_list: list) -> str:
    """
    Classify a region as predominantly metro, micro, or rural.

    Args:
        fips_list: List of FIPS codes for a region

    Returns:
        'metro', 'micro', or 'rural'
    """
    classifications = [get_cbsa_classification(fips)['cbsa'] for fips in fips_list]

    counts = {
        'metro': classifications.count('metro'),
        'micro': classifications.count('micro'),
        'rural': classifications.count('rural')
    }

    # Return classification with highest count
    return max(counts, key=counts.get)


# TODO: Complete CBSA classifications for all 530 counties
# This is a subset showing the pattern. Full implementation would include:
# - All Virginia localities (135)
# - All Maryland counties (24)
# - All West Virginia counties (55)
# - All North Carolina counties (100)
# - All Tennessee counties (95)
# - All Kentucky counties (120)
# - District of Columbia (1)
#
# Data source: https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html
