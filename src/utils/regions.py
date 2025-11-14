"""
Region Utilities for Virginia Thriving Index

This module provides unified access to all region definitions for the
Virginia Thriving Index project, including:
- Virginia localities (counties and independent cities)
- Peer state regions (MD, WV, NC, TN, KY, DC)
- Region lookup functions
- Region metadata and summary statistics

Usage:
    from src.utils.regions import get_all_regions, get_virginia_regions

    # Get all regions
    all_regions = get_all_regions()

    # Get just Virginia
    va_regions = get_virginia_regions()

    # Look up by FIPS
    region = get_region_by_fips('51001')
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from data.virginia_regions import (
    VIRGINIA_PDCS,
    VIRGINIA_COUNTY_FIPS,
    VIRGINIA_CITY_FIPS,
    SUGGESTED_REGIONAL_GROUPS
)
from data.peer_states_regions import (
    ALL_PEER_REGIONS,
    get_all_peer_regions,
    get_regions_by_state,
    PEER_STATES_SUMMARY
)


# Cache for combined regions
_ALL_REGIONS_CACHE = None

# Convert Virginia FIPS dictionaries to region list format
def _build_virginia_regions():
    """Build Virginia regions list from FIPS dictionaries."""
    regions = []

    # Add counties
    for fips, name in VIRGINIA_COUNTY_FIPS.items():
        regions.append({
            'fips': fips,
            'name': name,
            'type': 'county',
            'state': 'VA'
        })

    # Add cities
    for fips, name in VIRGINIA_CITY_FIPS.items():
        regions.append({
            'fips': fips,
            'name': name,
            'type': 'city',
            'state': 'VA'
        })

    return regions

# Build Virginia regions once at module load
_VIRGINIA_REGIONS = _build_virginia_regions()


def get_virginia_regions(include_pdc=False):
    """
    Get all Virginia localities.

    Args:
        include_pdc (bool): If True, also include PDC region definitions

    Returns:
        dict: Dictionary with 'localities', and optionally 'pdcs' and 'consolidated'
    """
    result = {
        'localities': _VIRGINIA_REGIONS.copy(),
    }

    if include_pdc:
        result['pdcs'] = VIRGINIA_PDCS
        result['consolidated'] = SUGGESTED_REGIONAL_GROUPS

    return result


def get_all_virginia_localities():
    """
    Get a flat list of all Virginia localities (counties + cities).

    Returns:
        list: List of all Virginia locality dictionaries with 'state': 'VA' added
    """
    return _VIRGINIA_REGIONS.copy()


def get_all_regions():
    """
    Get all regions from Virginia and all peer states.

    Returns:
        list: List of all region dictionaries with state codes
    """
    global _ALL_REGIONS_CACHE

    if _ALL_REGIONS_CACHE is not None:
        return _ALL_REGIONS_CACHE

    all_regions = []

    # Add Virginia localities
    all_regions.extend(get_all_virginia_localities())

    # Add peer state regions
    all_regions.extend(get_all_peer_regions())

    _ALL_REGIONS_CACHE = all_regions
    return all_regions


def get_regions_by_state_code(state_code):
    """
    Get all regions for a specific state.

    Args:
        state_code (str): Two-letter state code (VA, MD, WV, NC, TN, KY, DC)

    Returns:
        list: List of region dictionaries for that state
    """
    state_code = state_code.upper()

    if state_code == 'VA':
        return get_all_virginia_localities()
    else:
        return get_regions_by_state(state_code)


def get_region_by_fips(fips_code):
    """
    Look up a specific region by its FIPS code.

    Args:
        fips_code (str): 5-digit FIPS code

    Returns:
        dict: Region information with state code, or None if not found
    """
    all_regions = get_all_regions()
    for region in all_regions:
        if region['fips'] == fips_code:
            return region
    return None


def get_region_summary():
    """
    Get summary statistics for all regions.

    Returns:
        dict: Summary statistics including counts by state
    """
    va_localities = get_all_virginia_localities()

    # Count Virginia counties and cities
    va_counties = sum(1 for r in va_localities if r['type'] == 'county')
    va_cities = sum(1 for r in va_localities if r['type'] == 'city')

    summary = {
        'total_regions': len(va_localities) + PEER_STATES_SUMMARY['total_regions'],
        'virginia': {
            'total': len(va_localities),
            'counties': va_counties,
            'cities': va_cities,
            'pdcs': len(VIRGINIA_PDCS),
        },
        'peer_states': PEER_STATES_SUMMARY['by_state'],
        'peer_states_total': PEER_STATES_SUMMARY['total_regions'],
    }

    return summary


def get_fips_list(state_codes=None):
    """
    Get a list of all FIPS codes, optionally filtered by state.

    Args:
        state_codes (list, optional): List of state codes to include (e.g., ['VA', 'MD'])
                                     If None, returns all FIPS codes

    Returns:
        list: List of FIPS code strings
    """
    if state_codes is None:
        regions = get_all_regions()
    else:
        state_codes = [s.upper() for s in state_codes]
        regions = []
        for state in state_codes:
            regions.extend(get_regions_by_state_code(state))

    return [region['fips'] for region in regions]


def validate_fips(fips_code):
    """
    Validate that a FIPS code exists in our region database.

    Args:
        fips_code (str): FIPS code to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return get_region_by_fips(fips_code) is not None


def get_state_from_fips(fips_code):
    """
    Extract state code from FIPS code.

    Args:
        fips_code (str): 5-digit FIPS code

    Returns:
        str: Two-letter state code, or None if not found
    """
    region = get_region_by_fips(fips_code)
    return region['state'] if region else None


if __name__ == '__main__':
    # Print summary when run directly
    print("Virginia Thriving Index - Region Summary")
    print("=" * 60)

    summary = get_region_summary()

    print(f"\nTotal regions across all states: {summary['total_regions']}")

    print("\nVirginia:")
    print(f"  Total localities: {summary['virginia']['total']}")
    print(f"  - Counties: {summary['virginia']['counties']}")
    print(f"  - Independent cities: {summary['virginia']['cities']}")
    print(f"  Planning District Commissions: {summary['virginia']['pdcs']}")

    print(f"\nPeer States: {summary['peer_states_total']} total regions")
    for state, count in summary['peer_states'].items():
        print(f"  {state}: {count} regions")

    print("\n" + "=" * 60)
    print("Sample lookups:")
    print("\nVirginia examples:")
    sample_va_fips = ['51001', '51510', '51059']  # Accomack County, Alexandria City, Fairfax County
    for fips in sample_va_fips:
        region = get_region_by_fips(fips)
        if region:
            print(f"  {fips}: {region['name']} ({region['type']})")

    print("\nPeer state examples:")
    sample_peer_fips = ['24031', '54061', '37063', '47037', '21111', '11001']
    for fips in sample_peer_fips:
        region = get_region_by_fips(fips)
        if region:
            print(f"  {fips}: {region['name']}, {region['state']} ({region['type']})")
