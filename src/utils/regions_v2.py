"""
Region Utilities for Virginia Thriving Index (Regional Groupings Version)

This module provides access to multi-county regional groupings for the
Virginia Thriving Index project, following the Nebraska methodology.

Key concepts:
- Regions are multi-county groupings (not individual counties)
- 54 total regions across 7 states/districts
- Each region aggregates data from multiple counties
- Regions are comparable units for peer matching

Usage:
    from src.utils.regions_v2 import get_all_regions, get_region_info

    # Get all regions
    regions = get_all_regions()  # Returns 54 regions

    # Get specific region
    region = get_region_info('VA-8')  # Northern Virginia

    # Get regions by state
    va_regions = get_regions_by_state('VA')  # 11 Virginia regions
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from data.regional_groupings import (
    ALL_REGIONS,
    REGIONAL_SUMMARY,
    get_region_by_code,
    get_regions_by_state as get_regions_by_state_code,
    find_region_for_county
)
from src.utils.fips_to_region import (
    get_region_for_fips,
    get_all_fips_in_region,
    get_state_from_region_code
)


def get_all_regions() -> Dict[str, Dict]:
    """
    Get all regional groupings.

    Returns:
        Dict mapping region code to region information
    """
    return ALL_REGIONS.copy()


def get_region_info(region_code: str) -> Optional[Dict]:
    """
    Get information about a specific region.

    Args:
        region_code: Region code (e.g., 'VA-8', 'MD-3')

    Returns:
        Dict with region information or None if not found
    """
    return get_region_by_code(region_code)


def get_regions_by_state(state_code: str) -> Dict[str, Dict]:
    """
    Get all regions for a specific state.

    Args:
        state_code: Two-letter state code (VA, MD, WV, NC, TN, KY, DC)

    Returns:
        Dict of regions for that state
    """
    return get_regions_by_state_code(state_code)


def get_region_summary() -> Dict:
    """
    Get summary statistics for all regions.

    Returns:
        Dict with summary information
    """
    return REGIONAL_SUMMARY.copy()


def get_region_fips_codes(region_code: str) -> List[str]:
    """
    Get all FIPS codes (counties/cities) that belong to a region.

    Args:
        region_code: Region code (e.g., 'VA-8')

    Returns:
        List of 5-digit FIPS codes
    """
    return get_all_fips_in_region(region_code)


def find_region_by_fips(fips_code: str) -> Optional[str]:
    """
    Find which region a county/city belongs to.

    Args:
        fips_code: 5-digit FIPS code

    Returns:
        Region code or None if not found
    """
    return get_region_for_fips(fips_code)


def get_all_region_codes() -> List[str]:
    """
    Get a list of all region codes.

    Returns:
        List of region codes (e.g., ['VA-1', 'VA-2', ...])
    """
    return list(ALL_REGIONS.keys())


def get_region_characteristics(region_code: str) -> List[str]:
    """
    Get the characteristics of a region.

    Args:
        region_code: Region code

    Returns:
        List of characteristic strings
    """
    region = get_region_by_code(region_code)
    return region.get('characteristics', []) if region else []


def get_regions_with_characteristic(characteristic: str) -> List[str]:
    """
    Find all regions that have a specific characteristic.

    Args:
        characteristic: Characteristic to search for (e.g., 'Urban', 'Rural')

    Returns:
        List of region codes
    """
    matching_regions = []
    for region_code, region_info in ALL_REGIONS.items():
        characteristics = region_info.get('characteristics', [])
        if any(characteristic.lower() in char.lower() for char in characteristics):
            matching_regions.append(region_code)
    return matching_regions


def count_localities_in_region(region_code: str) -> int:
    """
    Count the number of counties/cities in a region.

    Args:
        region_code: Region code

    Returns:
        Number of localities (counties + cities)
    """
    region = get_region_by_code(region_code)
    if not region:
        return 0
    counties = len(region.get('counties', []))
    cities = len(region.get('cities', []))
    return counties + cities


if __name__ == '__main__':
    print("Virginia Thriving Index - Regional Structure")
    print("=" * 70)

    summary = get_region_summary()
    print(f"\nTotal analysis regions: {summary['total_regions']}")
    print("\nRegions by state:")
    for state, count in summary['by_state'].items():
        print(f"  {state}: {count} regions")

    print("\n" + "=" * 70)
    print("Sample regions:")

    for state in ['VA', 'MD', 'NC']:
        regions = get_regions_by_state(state)
        print(f"\n{state} regions:")
        for code, info in list(regions.items())[:2]:  # Show first 2
            num_localities = count_localities_in_region(code)
            fips_codes = get_region_fips_codes(code)
            print(f"  {code}: {info['name']}")
            print(f"       {num_localities} localities, {len(fips_codes)} FIPS codes")
            print(f"       Characteristics: {', '.join(info['characteristics'][:3])}")

    print("\n" + "=" * 70)
    print("FIPS code lookups:")

    sample_fips = [
        ('51059', 'Fairfax County'),
        ('24031', 'Montgomery County, MD'),
        ('37063', 'Durham County, NC')
    ]

    for fips, description in sample_fips:
        region_code = find_region_by_fips(fips)
        if region_code:
            region = get_region_info(region_code)
            print(f"  {fips} ({description})")
            print(f"    → {region_code}: {region['name']}")

    print("\n" + "=" * 70)
    print("Characteristic-based search:")

    for characteristic in ['Urban', 'Rural', 'Appalachian']:
        regions = get_regions_with_characteristic(characteristic)
        print(f"\n  Regions with '{characteristic}': {len(regions)}")
        print(f"    {', '.join(regions[:5])}" + (" ..." if len(regions) > 5 else ""))
