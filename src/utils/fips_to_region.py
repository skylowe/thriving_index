"""
FIPS Code to Region Mapping

This module provides mapping from individual county FIPS codes to regional codes.
Essential for aggregating county-level data to multi-county regions.

Usage:
    from src.utils.fips_to_region import get_region_for_fips, get_all_fips_in_region

    # Get region code for a county
    region = get_region_for_fips('51059')  # Returns 'VA-8' (Northern Virginia)

    # Get all FIPS codes in a region
    fips_list = get_all_fips_in_region('VA-8')
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from data.virginia_regions import VIRGINIA_COUNTY_FIPS, VIRGINIA_CITY_FIPS
from data.peer_states_regions import (
    MARYLAND_COUNTIES, WEST_VIRGINIA_COUNTIES, NORTH_CAROLINA_COUNTIES,
    TENNESSEE_COUNTIES, KENTUCKY_COUNTIES, DISTRICT_OF_COLUMBIA
)
from data.regional_groupings import ALL_REGIONS


def _build_fips_to_region_mapping() -> Dict[str, str]:
    """
    Build a comprehensive mapping from FIPS codes to region codes.

    Returns:
        Dict mapping FIPS code (str) to region code (str)
    """
    mapping = {}

    # Process each region
    for region_code, region_info in ALL_REGIONS.items():
        state_code = region_code.split('-')[0]

        # Get county and city names for this region
        county_names = region_info.get('counties', [])
        city_names = region_info.get('cities', [])

        # Map based on state
        if state_code == 'VA':
            # Virginia counties
            # Note: VIRGINIA_COUNTY_FIPS has county name as key, county code as value
            for county_name, county_code in VIRGINIA_COUNTY_FIPS.items():
                if county_name in county_names:
                    # Build full FIPS code: state (51) + county code
                    full_fips = '51' + county_code
                    mapping[full_fips] = region_code

            # Virginia cities
            # Note: VIRGINIA_CITY_FIPS has city name as key, city code as value
            for city_name, city_code in VIRGINIA_CITY_FIPS.items():
                if city_name in city_names:
                    # Build full FIPS code: state (51) + city code
                    full_fips = '51' + city_code
                    mapping[full_fips] = region_code

        elif state_code == 'MD':
            # Maryland counties and Baltimore City
            for county_info in MARYLAND_COUNTIES:
                county_fips = county_info['fips']
                county_name = county_info['name']

                # Remove "County" or "City" suffix
                clean_name = county_name.replace(' County', '').replace(' City', '')

                if clean_name in county_names or clean_name in city_names:
                    mapping[county_fips] = region_code

        elif state_code == 'WV':
            # West Virginia counties
            for county_info in WEST_VIRGINIA_COUNTIES:
                county_fips = county_info['fips']
                county_name = county_info['name'].replace(' County', '')

                if county_name in county_names:
                    mapping[county_fips] = region_code

        elif state_code == 'NC':
            # North Carolina counties
            for county_info in NORTH_CAROLINA_COUNTIES:
                county_fips = county_info['fips']
                county_name = county_info['name'].replace(' County', '')

                if county_name in county_names:
                    mapping[county_fips] = region_code

        elif state_code == 'TN':
            # Tennessee counties
            for county_info in TENNESSEE_COUNTIES:
                county_fips = county_info['fips']
                county_name = county_info['name'].replace(' County', '')

                if county_name in county_names:
                    mapping[county_fips] = region_code

        elif state_code == 'KY':
            # Kentucky counties
            for county_info in KENTUCKY_COUNTIES:
                county_fips = county_info['fips']
                county_name = county_info['name'].replace(' County', '')

                if county_name in county_names:
                    mapping[county_fips] = region_code

        elif state_code == 'DC':
            # District of Columbia (special case)
            for dc_info in DISTRICT_OF_COLUMBIA:
                mapping[dc_info['fips']] = region_code

    return mapping


# Build mapping at module load time
_FIPS_TO_REGION = _build_fips_to_region_mapping()

# Build reverse mapping (region to list of FIPS codes)
_REGION_TO_FIPS = {}
for fips, region in _FIPS_TO_REGION.items():
    if region not in _REGION_TO_FIPS:
        _REGION_TO_FIPS[region] = []
    _REGION_TO_FIPS[region].append(fips)


def get_region_for_fips(fips_code: str) -> Optional[str]:
    """
    Get the region code for a given FIPS code.

    Args:
        fips_code: 5-digit FIPS code

    Returns:
        Region code (e.g., 'VA-8') or None if not found
    """
    return _FIPS_TO_REGION.get(fips_code)


def get_all_fips_in_region(region_code: str) -> List[str]:
    """
    Get all FIPS codes that belong to a region.

    Args:
        region_code: Region code (e.g., 'VA-8')

    Returns:
        List of FIPS codes
    """
    return _REGION_TO_FIPS.get(region_code, [])


def get_state_from_region_code(region_code: str) -> str:
    """
    Extract state code from region code.

    Args:
        region_code: Region code (e.g., 'VA-8')

    Returns:
        Two-letter state code (e.g., 'VA')
    """
    return region_code.split('-')[0]


def validate_mapping_completeness() -> Dict:
    """
    Validate that all FIPS codes are mapped to regions.

    Returns:
        Dict with validation results
    """
    total_fips = (
        len(VIRGINIA_COUNTY_FIPS) +
        len(VIRGINIA_CITY_FIPS) +
        len(MARYLAND_COUNTIES) +
        len(WEST_VIRGINIA_COUNTIES) +
        len(NORTH_CAROLINA_COUNTIES) +
        len(TENNESSEE_COUNTIES) +
        len(KENTUCKY_COUNTIES) +
        len(DISTRICT_OF_COLUMBIA)
    )

    mapped_fips = len(_FIPS_TO_REGION)

    return {
        'total_fips_codes': total_fips,
        'mapped_fips_codes': mapped_fips,
        'unmapped_count': total_fips - mapped_fips,
        'coverage_percent': (mapped_fips / total_fips * 100) if total_fips > 0 else 0,
        'total_regions': len(_REGION_TO_FIPS),
        'complete': total_fips == mapped_fips
    }


def get_mapping_summary() -> Dict:
    """
    Get summary statistics about the FIPS to region mapping.

    Returns:
        Dict with summary information
    """
    by_state = {}
    for region_code, fips_list in _REGION_TO_FIPS.items():
        state = get_state_from_region_code(region_code)
        if state not in by_state:
            by_state[state] = {'regions': 0, 'localities': 0}
        by_state[state]['regions'] += 1
        by_state[state]['localities'] += len(fips_list)

    return {
        'total_regions': len(_REGION_TO_FIPS),
        'total_localities': len(_FIPS_TO_REGION),
        'by_state': by_state
    }


if __name__ == '__main__':
    print("FIPS to Region Mapping")
    print("=" * 70)

    summary = get_mapping_summary()
    print(f"\nTotal regions: {summary['total_regions']}")
    print(f"Total localities (counties + cities): {summary['total_localities']}")

    print("\nLocalities per region by state:")
    for state, stats in sorted(summary['by_state'].items()):
        avg_per_region = stats['localities'] / stats['regions'] if stats['regions'] > 0 else 0
        print(f"  {state}: {stats['localities']} localities across {stats['regions']} regions")
        print(f"       (avg {avg_per_region:.1f} localities per region)")

    # Validation
    print("\n" + "=" * 70)
    validation = validate_mapping_completeness()
    print(f"Mapping completeness: {validation['coverage_percent']:.1f}%")
    print(f"  Mapped: {validation['mapped_fips_codes']} FIPS codes")
    print(f"  Unmapped: {validation['unmapped_count']} FIPS codes")

    if validation['complete']:
        print("  ✓ All FIPS codes successfully mapped to regions")
    else:
        print("  ✗ Some FIPS codes not mapped")

    # Sample lookups
    print("\n" + "=" * 70)
    print("Sample lookups:")

    samples = [
        ('51059', 'Fairfax County, VA'),
        ('51510', 'Alexandria City, VA'),
        ('24031', 'Montgomery County, MD'),
        ('37063', 'Durham County, NC'),
        ('47037', 'Davidson County, TN (Nashville)'),
        ('21111', 'Jefferson County, KY (Louisville)'),
        ('11001', 'District of Columbia')
    ]

    for fips, description in samples:
        region = get_region_for_fips(fips)
        if region:
            region_info = ALL_REGIONS.get(region, {})
            region_name = region_info.get('name', 'Unknown')
            print(f"  {fips} ({description})")
            print(f"    → {region}: {region_name}")
        else:
            print(f"  {fips} ({description}): NOT MAPPED")

    # Show sample region
    print("\n" + "=" * 70)
    print("Sample region composition:")
    sample_region = 'VA-8'  # Northern Virginia
    fips_list = get_all_fips_in_region(sample_region)
    region_info = ALL_REGIONS.get(sample_region, {})
    print(f"\n{sample_region}: {region_info.get('name')}")
    print(f"  Contains {len(fips_list)} localities (FIPS codes):")
    print(f"  {', '.join(fips_list[:10])}")
    if len(fips_list) > 10:
        print(f"  ... and {len(fips_list) - 10} more")
