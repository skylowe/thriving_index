"""
Identify unmapped FIPS codes.

This script finds FIPS codes that are in peer_states_regions.py or virginia_regions.py
but not successfully mapped to regions in fips_to_region.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from data.virginia_regions import VIRGINIA_COUNTY_FIPS, VIRGINIA_CITY_FIPS
from data.peer_states_regions import (
    MARYLAND_COUNTIES, WEST_VIRGINIA_COUNTIES, NORTH_CAROLINA_COUNTIES,
    TENNESSEE_COUNTIES, KENTUCKY_COUNTIES, DISTRICT_OF_COLUMBIA
)
from src.utils.fips_to_region import get_region_for_fips


def identify_unmapped():
    """Find all FIPS codes that are not mapped to regions."""
    unmapped = []

    # Check Virginia counties
    print("Checking Virginia counties...")
    for county_name, county_code in VIRGINIA_COUNTY_FIPS.items():
        fips = '51' + county_code
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'VA',
                'name': county_name + ' County',
                'type': 'county'
            })

    # Check Virginia cities
    print("Checking Virginia cities...")
    for city_name, city_code in VIRGINIA_CITY_FIPS.items():
        fips = '51' + city_code
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'VA',
                'name': city_name,
                'type': 'city'
            })

    # Check Maryland
    print("Checking Maryland counties...")
    for county_info in MARYLAND_COUNTIES:
        fips = county_info['fips']
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'MD',
                'name': county_info['name'],
                'type': 'county'
            })

    # Check West Virginia
    print("Checking West Virginia counties...")
    for county_info in WEST_VIRGINIA_COUNTIES:
        fips = county_info['fips']
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'WV',
                'name': county_info['name'],
                'type': 'county'
            })

    # Check North Carolina
    print("Checking North Carolina counties...")
    for county_info in NORTH_CAROLINA_COUNTIES:
        fips = county_info['fips']
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'NC',
                'name': county_info['name'],
                'type': 'county'
            })

    # Check Tennessee
    print("Checking Tennessee counties...")
    for county_info in TENNESSEE_COUNTIES:
        fips = county_info['fips']
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'TN',
                'name': county_info['name'],
                'type': 'county'
            })

    # Check Kentucky
    print("Checking Kentucky counties...")
    for county_info in KENTUCKY_COUNTIES:
        fips = county_info['fips']
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'KY',
                'name': county_info['name'],
                'type': 'county'
            })

    # Check DC
    print("Checking District of Columbia...")
    for dc_info in DISTRICT_OF_COLUMBIA:
        fips = dc_info['fips']
        region = get_region_for_fips(fips)
        if region is None:
            unmapped.append({
                'fips': fips,
                'state': 'DC',
                'name': dc_info['name'],
                'type': 'district'
            })

    return unmapped


if __name__ == '__main__':
    print("=" * 70)
    print("Identifying Unmapped FIPS Codes")
    print("=" * 70)
    print()

    unmapped = identify_unmapped()

    print()
    print("=" * 70)
    print(f"Found {len(unmapped)} unmapped FIPS codes:")
    print()

    if unmapped:
        # Group by state
        by_state = {}
        for item in unmapped:
            state = item['state']
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(item)

        for state in sorted(by_state.keys()):
            items = by_state[state]
            print(f"{state}: {len(items)} unmapped")
            for item in items:
                print(f"  {item['fips']}: {item['name']} ({item['type']})")
            print()
    else:
        print("All FIPS codes successfully mapped!")
