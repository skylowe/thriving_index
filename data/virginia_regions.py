"""
Virginia Planning District Commission (PDC) region definitions.

Virginia has 21 Planning District Commissions that group localities
(counties and independent cities) for regional planning purposes.

This module defines these regions for use in the Thriving Index analysis.
"""

from typing import Dict, List, Set

# Virginia Planning District Commissions with their member localities
# Source: Virginia Association of Planning District Commissions (https://www.vapdc.org/)

VIRGINIA_PDCS = {
    1: {
        'name': 'Lenowisco Planning District Commission',
        'counties': ['Dickenson', 'Lee', 'Scott', 'Wise'],
        'cities': ['Norton']
    },
    2: {
        'name': 'Cumberland Plateau Planning District Commission',
        'counties': ['Buchanan', 'Russell', 'Tazewell'],
        'cities': []
    },
    3: {
        'name': 'Mount Rogers Planning District Commission',
        'counties': ['Bland', 'Carroll', 'Grayson', 'Smyth', 'Washington', 'Wythe'],
        'cities': ['Bristol', 'Galax']
    },
    4: {
        'name': 'New River Valley Planning District Commission',
        'counties': ['Floyd', 'Giles', 'Montgomery', 'Pulaski'],
        'cities': ['Radford']
    },
    5: {
        'name': 'Fifth Planning District Commission',
        'counties': ['Franklin', 'Henry', 'Patrick', 'Pittsylvania'],
        'cities': ['Martinsville']
    },
    6: {
        'name': 'West Piedmont Planning District Commission',
        'counties': [],
        'cities': ['Danville']  # Note: Danville is the sole member
    },
    7: {
        'name': 'Southside Planning District Commission',
        'counties': ['Brunswick', 'Charlotte', 'Halifax', 'Lunenburg', 'Mecklenburg'],
        'cities': ['South Boston']
    },
    8: {
        'name': 'Commonwealth Regional Council',
        'counties': ['Amelia', 'Buckingham', 'Cumberland', 'Lunenburg', 'Nottoway', 'Prince Edward'],
        'cities': []
    },
    9: {
        'name': 'Central Virginia Planning District Commission',
        'counties': ['Amherst', 'Appomattox', 'Bedford', 'Campbell'],
        'cities': ['Bedford', 'Lynchburg']
    },
    10: {
        'name': 'Thomas Jefferson Planning District Commission',
        'counties': ['Albemarle', 'Fluvanna', 'Greene', 'Louisa', 'Nelson'],
        'cities': ['Charlottesville']
    },
    11: {
        'name': 'Rappahannock-Rapidan Regional Commission',
        'counties': ['Culpeper', 'Fauquier', 'Madison', 'Orange', 'Rappahannock'],
        'cities': []
    },
    12: {
        'name': 'Northern Shenandoah Valley Regional Commission',
        'counties': ['Clarke', 'Frederick', 'Page', 'Shenandoah', 'Warren'],
        'cities': ['Winchester']
    },
    13: {
        'name': 'Central Shenandoah Planning District Commission',
        'counties': ['Augusta', 'Bath', 'Highland', 'Rockbridge', 'Rockingham'],
        'cities': ['Buena Vista', 'Harrisonburg', 'Lexington', 'Staunton', 'Waynesboro']
    },
    14: {
        'name': 'Alleghany-Highland Regional Commission',
        'counties': ['Alleghany'],
        'cities': ['Covington']
    },
    15: {
        'name': 'Northern Virginia Regional Commission',
        'counties': ['Arlington', 'Fairfax', 'Loudoun', 'Prince William'],
        'cities': ['Alexandria', 'Fairfax', 'Falls Church', 'Manassas', 'Manassas Park']
    },
    16: {
        'name': 'George Washington Regional Commission',
        'counties': ['Caroline', 'King George', 'Spotsylvania', 'Stafford'],
        'cities': ['Fredericksburg']
    },
    17: {
        'name': 'Northern Neck Planning District Commission',
        'counties': ['Lancaster', 'Northumberland', 'Richmond', 'Westmoreland'],
        'cities': []
    },
    18: {
        'name': 'Middle Peninsula Planning District Commission',
        'counties': ['Essex', 'Gloucester', 'King and Queen', 'King William', 'Mathews', 'Middlesex'],
        'cities': []
    },
    19: {
        'name': 'Crater Planning District Commission',
        'counties': ['Dinwiddie', 'Greensville', 'Prince George', 'Surry', 'Sussex'],
        'cities': ['Colonial Heights', 'Emporia', 'Hopewell', 'Petersburg']
    },
    20: {
        'name': 'Richmond Regional Planning District Commission',
        'counties': ['Charles City', 'Chesterfield', 'Goochland', 'Hanover', 'Henrico', 'New Kent', 'Powhatan'],
        'cities': ['Richmond']
    },
    21: {
        'name': 'Hampton Roads Planning District Commission',
        'counties': ['Gloucester', 'Isle of Wight', 'James City', 'Mathews', 'Southampton', 'Surry', 'York'],
        'cities': ['Chesapeake', 'Franklin', 'Hampton', 'Newport News', 'Norfolk',
                   'Poquoson', 'Portsmouth', 'Suffolk', 'Virginia Beach', 'Williamsburg']
    }
}

# Virginia County FIPS Codes (3-digit suffix)
# Full FIPS = '51' (state) + county code
VIRGINIA_COUNTY_FIPS = {
    'Accomack': '001',
    'Albemarle': '003',
    'Alleghany': '005',
    'Amelia': '007',
    'Amherst': '009',
    'Appomattox': '011',
    'Arlington': '013',
    'Augusta': '015',
    'Bath': '017',
    'Bedford': '019',
    'Bland': '021',
    'Botetourt': '023',
    'Brunswick': '025',
    'Buchanan': '027',
    'Buckingham': '029',
    'Campbell': '031',
    'Caroline': '033',
    'Carroll': '035',
    'Charles City': '036',
    'Charlotte': '037',
    'Chesterfield': '041',
    'Clarke': '043',
    'Craig': '045',
    'Culpeper': '047',
    'Cumberland': '049',
    'Dickenson': '051',
    'Dinwiddie': '053',
    'Essex': '057',
    'Fairfax': '059',
    'Fauquier': '061',
    'Floyd': '063',
    'Fluvanna': '065',
    'Franklin': '067',
    'Frederick': '069',
    'Giles': '071',
    'Gloucester': '073',
    'Goochland': '075',
    'Grayson': '077',
    'Greene': '079',
    'Greensville': '081',
    'Halifax': '083',
    'Hanover': '085',
    'Henrico': '087',
    'Henry': '089',
    'Highland': '091',
    'Isle of Wight': '093',
    'James City': '095',
    'King and Queen': '097',
    'King George': '099',
    'King William': '101',
    'Lancaster': '103',
    'Lee': '105',
    'Loudoun': '107',
    'Louisa': '109',
    'Lunenburg': '111',
    'Madison': '113',
    'Mathews': '115',
    'Mecklenburg': '117',
    'Middlesex': '119',
    'Montgomery': '121',
    'Nelson': '125',
    'New Kent': '127',
    'Northampton': '131',
    'Northumberland': '133',
    'Nottoway': '135',
    'Orange': '137',
    'Page': '139',
    'Patrick': '141',
    'Pittsylvania': '143',
    'Powhatan': '145',
    'Prince Edward': '147',
    'Prince George': '149',
    'Prince William': '153',
    'Pulaski': '155',
    'Rappahannock': '157',
    'Richmond': '159',  # County, not city
    'Roanoke': '161',
    'Rockbridge': '163',
    'Rockingham': '165',
    'Russell': '167',
    'Scott': '169',
    'Shenandoah': '171',
    'Smyth': '173',
    'Southampton': '175',
    'Spotsylvania': '177',
    'Stafford': '179',
    'Surry': '181',
    'Sussex': '183',
    'Tazewell': '185',
    'Warren': '187',
    'Washington': '191',
    'Westmoreland': '193',
    'Wise': '195',
    'Wythe': '197',
    'York': '199'
}

# Virginia Independent City FIPS Codes (3-digit suffix starting with 5)
# Full FIPS = '51' (state) + city code
VIRGINIA_CITY_FIPS = {
    'Alexandria': '510',
    'Bedford': '515',
    'Bristol': '520',
    'Buena Vista': '530',
    'Charlottesville': '540',
    'Chesapeake': '550',
    'Colonial Heights': '570',
    'Covington': '580',
    'Danville': '590',
    'Emporia': '595',
    'Fairfax': '600',
    'Falls Church': '610',
    'Franklin': '620',
    'Fredericksburg': '630',
    'Galax': '640',
    'Hampton': '650',
    'Harrisonburg': '660',
    'Hopewell': '670',
    'Lexington': '678',
    'Lynchburg': '680',
    'Manassas': '683',
    'Manassas Park': '685',
    'Martinsville': '690',
    'Newport News': '700',
    'Norfolk': '710',
    'Norton': '720',
    'Petersburg': '730',
    'Poquoson': '735',
    'Portsmouth': '740',
    'Radford': '750',
    'Richmond': '760',
    'Roanoke': '770',
    'Salem': '775',
    'South Boston': '780',
    'Staunton': '790',
    'Suffolk': '800',
    'Virginia Beach': '810',
    'Waynesboro': '820',
    'Williamsburg': '830',
    'Winchester': '840'
}


def get_pdc_members(pdc_id: int) -> Dict[str, List[str]]:
    """
    Get all member localities for a PDC.

    Args:
        pdc_id: PDC number (1-21)

    Returns:
        Dictionary with 'counties' and 'cities' lists
    """
    if pdc_id not in VIRGINIA_PDCS:
        raise ValueError(f"Invalid PDC ID: {pdc_id}")

    return {
        'counties': VIRGINIA_PDCS[pdc_id]['counties'].copy(),
        'cities': VIRGINIA_PDCS[pdc_id]['cities'].copy()
    }


def get_pdc_fips_codes(pdc_id: int) -> List[str]:
    """
    Get all FIPS codes for localities in a PDC.

    Args:
        pdc_id: PDC number (1-21)

    Returns:
        List of full FIPS codes (5-digit strings with state prefix '51')
    """
    if pdc_id not in VIRGINIA_PDCS:
        raise ValueError(f"Invalid PDC ID: {pdc_id}")

    pdc = VIRGINIA_PDCS[pdc_id]
    fips_codes = []

    # Add county FIPS codes
    for county in pdc['counties']:
        if county in VIRGINIA_COUNTY_FIPS:
            fips_codes.append(f"51{VIRGINIA_COUNTY_FIPS[county]}")

    # Add city FIPS codes
    for city in pdc['cities']:
        if city in VIRGINIA_CITY_FIPS:
            fips_codes.append(f"51{VIRGINIA_CITY_FIPS[city]}")

    return fips_codes


def get_all_virginia_fips() -> List[str]:
    """
    Get all Virginia county and city FIPS codes.

    Returns:
        List of full FIPS codes for all VA localities
    """
    fips_codes = []

    # Add all counties
    for county_code in VIRGINIA_COUNTY_FIPS.values():
        fips_codes.append(f"51{county_code}")

    # Add all cities
    for city_code in VIRGINIA_CITY_FIPS.values():
        fips_codes.append(f"51{city_code}")

    return sorted(fips_codes)


def get_locality_pdc(locality_name: str) -> int:
    """
    Find which PDC a locality belongs to.

    Args:
        locality_name: Name of county or city

    Returns:
        PDC ID (1-21)

    Raises:
        ValueError: If locality not found in any PDC
    """
    for pdc_id, pdc_info in VIRGINIA_PDCS.items():
        if locality_name in pdc_info['counties'] or locality_name in pdc_info['cities']:
            return pdc_id

    raise ValueError(f"Locality '{locality_name}' not found in any PDC")


def get_pdc_summary() -> Dict[int, Dict]:
    """
    Get summary statistics for all PDCs.

    Returns:
        Dictionary with PDC info including name and member counts
    """
    summary = {}

    for pdc_id, pdc_info in VIRGINIA_PDCS.items():
        summary[pdc_id] = {
            'name': pdc_info['name'],
            'num_counties': len(pdc_info['counties']),
            'num_cities': len(pdc_info['cities']),
            'total_localities': len(pdc_info['counties']) + len(pdc_info['cities']),
            'counties': pdc_info['counties'],
            'cities': pdc_info['cities']
        }

    return summary


def consolidate_pdcs_to_regions(pdc_groups: List[List[int]]) -> Dict[str, Dict]:
    """
    Consolidate multiple PDCs into larger regions.

    Args:
        pdc_groups: List of lists, where each sublist contains PDC IDs to group together

    Returns:
        Dictionary mapping region names to their combined localities

    Example:
        >>> # Consolidate PDCs 1, 2, 3 into "Southwest Virginia"
        >>> regions = consolidate_pdcs_to_regions([[1, 2, 3], [4, 5]])
    """
    regions = {}

    for idx, pdc_list in enumerate(pdc_groups, 1):
        region_name = f"Region {idx}"
        combined_counties = []
        combined_cities = []
        pdc_names = []

        for pdc_id in pdc_list:
            if pdc_id not in VIRGINIA_PDCS:
                raise ValueError(f"Invalid PDC ID: {pdc_id}")

            pdc = VIRGINIA_PDCS[pdc_id]
            combined_counties.extend(pdc['counties'])
            combined_cities.extend(pdc['cities'])
            pdc_names.append(pdc['name'])

        regions[region_name] = {
            'pdcs': pdc_list,
            'pdc_names': pdc_names,
            'counties': combined_counties,
            'cities': combined_cities,
            'total_localities': len(combined_counties) + len(combined_cities)
        }

    return regions


# Suggested regional consolidations (for reducing from 21 to ~8-12 regions)
SUGGESTED_REGIONAL_GROUPS = {
    'Far Southwest Virginia': [1, 2],  # Lenowisco + Cumberland Plateau
    'Southwest Virginia': [3, 4],  # Mount Rogers + New River Valley
    'Southside Virginia': [5, 6, 7],  # Fifth + West Piedmont + Southside
    'Southcentral Virginia': [8, 9],  # Commonwealth + Central Virginia
    'Central Virginia': [10, 11],  # Thomas Jefferson + Rappahannock-Rapidan
    'Shenandoah Valley': [12, 13, 14],  # Northern Shenandoah + Central Shenandoah + Alleghany-Highland
    'Northern Virginia': [15],  # Northern Virginia (already large)
    'Fredericksburg Region': [16],  # George Washington
    'Northern Neck and Middle Peninsula': [17, 18],  # Northern Neck + Middle Peninsula
    'Greater Richmond': [19, 20],  # Crater + Richmond Regional
    'Hampton Roads': [21]  # Hampton Roads (already large)
}


def get_consolidated_regions() -> Dict[str, Dict]:
    """
    Get the suggested consolidated regional groupings.

    Returns:
        Dictionary mapping region names to their localities
    """
    regions = {}

    for region_name, pdc_list in SUGGESTED_REGIONAL_GROUPS.items():
        combined_counties = []
        combined_cities = []
        pdc_names = []
        fips_codes = []

        for pdc_id in pdc_list:
            pdc = VIRGINIA_PDCS[pdc_id]
            combined_counties.extend(pdc['counties'])
            combined_cities.extend(pdc['cities'])
            pdc_names.append(pdc['name'])
            fips_codes.extend(get_pdc_fips_codes(pdc_id))

        regions[region_name] = {
            'pdcs': pdc_list,
            'pdc_names': pdc_names,
            'counties': combined_counties,
            'cities': combined_cities,
            'total_localities': len(combined_counties) + len(combined_cities),
            'fips_codes': sorted(set(fips_codes))  # Remove duplicates and sort
        }

    return regions


if __name__ == "__main__":
    # Print summary when run directly
    print("=" * 80)
    print("VIRGINIA PLANNING DISTRICT COMMISSIONS")
    print("=" * 80)

    summary = get_pdc_summary()
    for pdc_id in sorted(summary.keys()):
        info = summary[pdc_id]
        print(f"\nPDC {pdc_id}: {info['name']}")
        print(f"  Counties: {info['num_counties']}, Cities: {info['num_cities']}, Total: {info['total_localities']}")

    print("\n" + "=" * 80)
    print("SUGGESTED CONSOLIDATED REGIONS (11 regions)")
    print("=" * 80)

    regions = get_consolidated_regions()
    for region_name, info in regions.items():
        print(f"\n{region_name}")
        print(f"  PDCs: {', '.join(info['pdc_names'])}")
        print(f"  Total Localities: {info['total_localities']}")
        print(f"  FIPS Codes: {len(info['fips_codes'])} localities")
