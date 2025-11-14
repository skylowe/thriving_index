"""
Regional Groupings for Virginia Thriving Index Analysis

This module defines multi-county regional groupings for all states in the analysis.
Following the Nebraska Thriving Index methodology, counties are grouped into regions
based on:
- Geographic proximity
- Economic characteristics (urban/rural, industries)
- Population density and size
- Metropolitan/micropolitan statistical areas
- Natural geographic divisions

Each region contains multiple counties that share similar characteristics,
allowing for meaningful regional comparisons across states.

Structure:
- Virginia: 11 regions (based on consolidated PDC groupings)
- Maryland: 6 regions
- West Virginia: 7 regions
- North Carolina: 10 regions
- Tennessee: 9 regions
- Kentucky: 10 regions
- District of Columbia: 1 region (special case)

Total: ~54 regions for analysis
"""

from typing import Dict, List

# =============================================================================
# VIRGINIA REGIONS (11 consolidated regions)
# =============================================================================

VIRGINIA_REGIONS = {
    'VA-1': {
        'name': 'Southwest Virginia',
        'description': 'Appalachian coalfield region',
        'counties': ['Buchanan', 'Dickenson', 'Lee', 'Russell', 'Scott', 'Tazewell', 'Wise'],
        'cities': ['Norton'],
        'characteristics': ['Rural', 'Appalachian', 'Coal mining', 'Low population density']
    },
    'VA-2': {
        'name': 'New River Valley & Highlands',
        'description': 'Mountain region with college towns',
        'counties': ['Bland', 'Carroll', 'Floyd', 'Giles', 'Grayson', 'Montgomery',
                     'Pulaski', 'Smyth', 'Washington', 'Wythe'],
        'cities': ['Bristol', 'Galax', 'Radford'],
        'characteristics': ['Mountains', 'University presence', 'Mixed rural-urban']
    },
    'VA-3': {
        'name': 'Southside & Danville',
        'description': 'South-central rural Virginia',
        'counties': ['Brunswick', 'Charlotte', 'Franklin', 'Halifax', 'Henry',
                     'Lunenburg', 'Mecklenburg', 'Patrick', 'Pittsylvania'],
        'cities': ['Danville', 'Martinsville', 'South Boston'],
        'characteristics': ['Rural', 'Tobacco heritage', 'Declining manufacturing']
    },
    'VA-4': {
        'name': 'Roanoke Valley & Alleghany Highlands',
        'description': 'Western Virginia urban corridor',
        'counties': ['Alleghany', 'Bath', 'Botetourt', 'Craig', 'Rockbridge', 'Roanoke'],
        'cities': ['Buena Vista', 'Clifton Forge', 'Covington', 'Lexington', 'Roanoke', 'Salem'],
        'characteristics': ['Urban center', 'Manufacturing', 'Healthcare']
    },
    'VA-5': {
        'name': 'Shenandoah Valley',
        'description': 'Valley and ridge region',
        'counties': ['Augusta', 'Frederick', 'Page', 'Rockingham', 'Shenandoah', 'Warren'],
        'cities': ['Harrisonburg', 'Staunton', 'Waynesboro', 'Winchester'],
        'characteristics': ['Agriculture', 'Tourism', 'Growing urban areas']
    },
    'VA-6': {
        'name': 'Charlottesville-Central Virginia',
        'description': 'Central Piedmont region',
        'counties': ['Albemarle', 'Amherst', 'Appomattox', 'Bedford', 'Campbell',
                     'Fluvanna', 'Greene', 'Louisa', 'Madison', 'Nelson', 'Orange'],
        'cities': ['Charlottesville', 'Lynchburg'],
        'characteristics': ['University', 'Wine country', 'Mixed economy']
    },
    'VA-7': {
        'name': 'Richmond Metro',
        'description': 'State capital region',
        'counties': ['Charles City', 'Chesterfield', 'Goochland', 'Hanover',
                     'Henrico', 'New Kent', 'Powhatan'],
        'cities': ['Colonial Heights', 'Hopewell', 'Petersburg', 'Richmond'],
        'characteristics': ['Urban', 'Government', 'Finance', 'Manufacturing']
    },
    'VA-8': {
        'name': 'Northern Virginia',
        'description': 'Washington DC suburbs',
        'counties': ['Arlington', 'Fairfax', 'Fauquier', 'Loudoun', 'Prince William', 'Stafford'],
        'cities': ['Alexandria', 'Fairfax', 'Falls Church', 'Manassas', 'Manassas Park'],
        'characteristics': ['Wealthy', 'Federal employment', 'Technology', 'High education']
    },
    'VA-9': {
        'name': 'Rappahannock',
        'description': 'Northern Neck and Middle Peninsula',
        'counties': ['Caroline', 'Essex', 'Gloucester', 'King and Queen', 'King George',
                     'King William', 'Lancaster', 'Mathews', 'Middlesex', 'Northumberland',
                     'Richmond', 'Westmoreland'],
        'cities': ['Fredericksburg'],
        'characteristics': ['Rural', 'Coastal', 'Tourism', 'Retirement']
    },
    'VA-10': {
        'name': 'Hampton Roads',
        'description': 'Tidewater metropolitan region',
        'counties': ['Gloucester', 'Isle of Wight', 'James City', 'Southampton', 'Surry', 'York'],
        'cities': ['Chesapeake', 'Franklin', 'Hampton', 'Newport News', 'Norfolk',
                   'Poquoson', 'Portsmouth', 'Suffolk', 'Virginia Beach', 'Williamsburg'],
        'characteristics': ['Military', 'Port', 'Tourism', 'Urban']
    },
    'VA-11': {
        'name': 'Eastern Shore',
        'description': 'Delmarva Peninsula counties',
        'counties': ['Accomack', 'Northampton'],
        'cities': [],
        'characteristics': ['Coastal', 'Agriculture', 'Seafood', 'Tourism', 'Rural']
    }
}

# =============================================================================
# MARYLAND REGIONS (6 regions)
# =============================================================================

MARYLAND_REGIONS = {
    'MD-1': {
        'name': 'Western Maryland',
        'description': 'Appalachian mountain region',
        'counties': ['Allegany', 'Garrett', 'Washington'],
        'cities': [],
        'characteristics': ['Appalachian', 'Rural', 'Manufacturing', 'Coal heritage']
    },
    'MD-2': {
        'name': 'Central Maryland',
        'description': 'Baltimore metropolitan area',
        'counties': ['Baltimore', 'Carroll', 'Harford', 'Howard'],
        'cities': ['Baltimore City'],
        'characteristics': ['Urban', 'Port', 'Healthcare', 'Education']
    },
    'MD-3': {
        'name': 'Capital Region',
        'description': 'Washington DC suburbs',
        'counties': ['Frederick', 'Montgomery', "Prince George's"],
        'cities': [],
        'characteristics': ['Wealthy', 'Federal employment', 'Diverse', 'High education']
    },
    'MD-4': {
        'name': 'Southern Maryland',
        'description': 'Chesapeake Bay southern counties',
        'counties': ['Anne Arundel', 'Calvert', 'Charles', "St. Mary's"],
        'cities': [],
        'characteristics': ['Suburban', 'Military bases', 'Commuter', 'Coastal']
    },
    'MD-5': {
        'name': 'Upper Eastern Shore',
        'description': 'Northern Delmarva Peninsula',
        'counties': ['Caroline', 'Cecil', 'Kent', "Queen Anne's", 'Talbot'],
        'cities': [],
        'characteristics': ['Rural', 'Agriculture', 'Coastal', 'Tourism']
    },
    'MD-6': {
        'name': 'Lower Eastern Shore',
        'description': 'Southern Delmarva Peninsula',
        'counties': ['Dorchester', 'Somerset', 'Wicomico', 'Worcester'],
        'cities': [],
        'characteristics': ['Rural', 'Agriculture', 'Seafood', 'Tourism', 'Poultry']
    }
}

# =============================================================================
# WEST VIRGINIA REGIONS (7 regions)
# =============================================================================

WEST_VIRGINIA_REGIONS = {
    'WV-1': {
        'name': 'Northern Panhandle',
        'description': 'Ohio River industrial region',
        'counties': ['Brooke', 'Hancock', 'Marshall', 'Ohio', 'Wetzel'],
        'cities': [],
        'characteristics': ['Steel heritage', 'Ohio River', 'Manufacturing decline']
    },
    'WV-2': {
        'name': 'North Central',
        'description': 'Morgantown region',
        'counties': ['Barbour', 'Doddridge', 'Harrison', 'Marion', 'Monongalia',
                     'Preston', 'Taylor', 'Tucker'],
        'cities': [],
        'characteristics': ['University', 'Coal', 'Natural gas', 'Growing']
    },
    'WV-3': {
        'name': 'Eastern Panhandle',
        'description': 'Washington DC exurbs',
        'counties': ['Berkeley', 'Grant', 'Hampshire', 'Hardy', 'Jefferson',
                     'Mineral', 'Morgan', 'Pendleton'],
        'cities': [],
        'characteristics': ['Growing', 'Commuter', 'Agriculture', 'Tourism']
    },
    'WV-4': {
        'name': 'Central',
        'description': 'Charleston metropolitan area',
        'counties': ['Braxton', 'Calhoun', 'Clay', 'Gilmer', 'Kanawha', 'Lewis',
                     'Nicholas', 'Roane', 'Upshur', 'Webster', 'Wirt'],
        'cities': [],
        'characteristics': ['State capital', 'Chemical industry', 'Natural gas']
    },
    'WV-5': {
        'name': 'Western',
        'description': 'Ohio River valley',
        'counties': ['Cabell', 'Jackson', 'Mason', 'Pleasants', 'Putnam',
                     'Ritchie', 'Tyler', 'Wood'],
        'cities': [],
        'characteristics': ['Huntington', 'University', 'Ohio River', 'Manufacturing']
    },
    'WV-6': {
        'name': 'Southern Coalfields',
        'description': 'Appalachian coal region',
        'counties': ['Boone', 'Fayette', 'Greenbrier', 'Lincoln', 'Logan', 'McDowell',
                     'Mercer', 'Mingo', 'Monroe', 'Pocahontas', 'Raleigh', 'Summers',
                     'Wayne', 'Wyoming'],
        'cities': [],
        'characteristics': ['Coal mining', 'Economic decline', 'Appalachian', 'Rural']
    },
    'WV-7': {
        'name': 'Randolph-Pocahontas',
        'description': 'Mountain tourism region',
        'counties': ['Pocahontas', 'Randolph'],
        'cities': [],
        'characteristics': ['Tourism', 'Forestry', 'Mountains', 'Low population']
    }
}

# =============================================================================
# NORTH CAROLINA REGIONS (10 regions)
# =============================================================================

NORTH_CAROLINA_REGIONS = {
    'NC-1': {
        'name': 'Western Mountains',
        'description': 'Appalachian highlands',
        'counties': ['Ashe', 'Avery', 'Cherokee', 'Clay', 'Graham', 'Haywood',
                     'Jackson', 'Macon', 'Madison', 'Mitchell', 'Swain',
                     'Transylvania', 'Watauga', 'Yancey'],
        'cities': [],
        'characteristics': ['Mountains', 'Tourism', 'Retirement', 'Rural']
    },
    'NC-2': {
        'name': 'Asheville Metro',
        'description': 'Western urban center',
        'counties': ['Buncombe', 'Henderson'],
        'cities': [],
        'characteristics': ['Urban', 'Tourism', 'Arts', 'Growing', 'Wealthy']
    },
    'NC-3': {
        'name': 'Western Piedmont',
        'description': 'Foothills region',
        'counties': ['Alexander', 'Alleghany', 'Burke', 'Caldwell', 'Catawba',
                     'Cleveland', 'Lincoln', 'McDowell', 'Polk', 'Rutherford',
                     'Surry', 'Wilkes', 'Yadkin'],
        'cities': [],
        'characteristics': ['Manufacturing', 'Furniture heritage', 'Mixed economy']
    },
    'NC-4': {
        'name': 'Charlotte Metro',
        'description': 'Major urban center',
        'counties': ['Cabarrus', 'Gaston', 'Iredell', 'Mecklenburg', 'Rowan',
                     'Stanly', 'Union'],
        'cities': [],
        'characteristics': ['Banking', 'Urban', 'Wealthy', 'Growing', 'Diverse']
    },
    'NC-5': {
        'name': 'Triad',
        'description': 'Greensboro-Winston-Salem-High Point',
        'counties': ['Alamance', 'Caswell', 'Davidson', 'Davie', 'Forsyth',
                     'Guilford', 'Randolph', 'Rockingham', 'Stokes'],
        'cities': [],
        'characteristics': ['Urban', 'Manufacturing', 'Universities', 'Tobacco heritage']
    },
    'NC-6': {
        'name': 'Triangle',
        'description': 'Raleigh-Durham-Chapel Hill',
        'counties': ['Chatham', 'Durham', 'Franklin', 'Granville', 'Orange',
                     'Person', 'Vance', 'Wake', 'Warren'],
        'cities': [],
        'characteristics': ['Universities', 'Research', 'Technology', 'State capital', 'Growing']
    },
    'NC-7': {
        'name': 'Sandhills',
        'description': 'South-central region',
        'counties': ['Anson', 'Cumberland', 'Harnett', 'Hoke', 'Lee', 'Montgomery',
                     'Moore', 'Richmond', 'Scotland'],
        'cities': [],
        'characteristics': ['Military', 'Agriculture', 'Mixed economy']
    },
    'NC-8': {
        'name': 'Eastern Piedmont',
        'description': 'Eastern transition zone',
        'counties': ['Edgecombe', 'Halifax', 'Johnston', 'Nash', 'Northampton',
                     'Wayne', 'Wilson'],
        'cities': [],
        'characteristics': ['Agriculture', 'Tobacco', 'Rural', 'Manufacturing']
    },
    'NC-9': {
        'name': 'Coastal Plain',
        'description': 'Inner coastal region',
        'counties': ['Beaufort', 'Bertie', 'Bladen', 'Columbus', 'Craven',
                     'Duplin', 'Greene', 'Jones', 'Lenoir', 'Martin', 'Pitt',
                     'Robeson', 'Sampson', 'Washington'],
        'cities': [],
        'characteristics': ['Agriculture', 'Rural', 'Military', 'Low income']
    },
    'NC-10': {
        'name': 'Coast',
        'description': 'Atlantic coastal counties',
        'counties': ['Brunswick', 'Camden', 'Carteret', 'Chowan', 'Currituck',
                     'Dare', 'Gates', 'Hyde', 'New Hanover', 'Onslow', 'Pamlico',
                     'Pasquotank', 'Pender', 'Perquimans', 'Tyrrell'],
        'cities': [],
        'characteristics': ['Coastal', 'Tourism', 'Military', 'Fishing', 'Retirement']
    }
}

# =============================================================================
# TENNESSEE REGIONS (9 regions)
# =============================================================================

TENNESSEE_REGIONS = {
    'TN-1': {
        'name': 'First Tennessee',
        'description': 'Upper East Tennessee',
        'counties': ['Carter', 'Greene', 'Hancock', 'Hawkins', 'Johnson',
                     'Sullivan', 'Unicoi', 'Washington'],
        'cities': [],
        'characteristics': ['Appalachian', 'Manufacturing', 'Healthcare']
    },
    'TN-2': {
        'name': 'Knoxville Metro',
        'description': 'East Tennessee urban center',
        'counties': ['Anderson', 'Blount', 'Campbell', 'Claiborne', 'Cocke',
                     'Grainger', 'Hamblen', 'Jefferson', 'Knox', 'Loudon',
                     'Monroe', 'Morgan', 'Roane', 'Scott', 'Sevier', 'Union'],
        'cities': [],
        'characteristics': ['Urban', 'University', 'Oak Ridge', 'Tourism']
    },
    'TN-3': {
        'name': 'Southeast Tennessee',
        'description': 'Chattanooga region',
        'counties': ['Bledsoe', 'Bradley', 'Franklin', 'Grundy', 'Hamilton',
                     'Marion', 'McMinn', 'Meigs', 'Polk', 'Rhea', 'Sequatchie'],
        'cities': [],
        'characteristics': ['Urban', 'Manufacturing', 'Tourism', 'Mountains']
    },
    'TN-4': {
        'name': 'Upper Cumberland',
        'description': 'North-central plateau',
        'counties': ['Cannon', 'Clay', 'Cumberland', 'DeKalb', 'Fentress',
                     'Jackson', 'Macon', 'Overton', 'Pickett', 'Putnam',
                     'Smith', 'Trousdale', 'Van Buren', 'Warren', 'White'],
        'cities': [],
        'characteristics': ['Rural', 'Agriculture', 'Plateau', 'Mixed economy']
    },
    'TN-5': {
        'name': 'Nashville Metro',
        'description': 'Middle Tennessee urban center',
        'counties': ['Cheatham', 'Davidson', 'Dickson', 'Hickman', 'Houston',
                     'Humphreys', 'Montgomery', 'Robertson', 'Rutherford',
                     'Stewart', 'Sumner', 'Williamson', 'Wilson'],
        'cities': [],
        'characteristics': ['Urban', 'Music industry', 'Healthcare', 'Growing', 'Wealthy']
    },
    'TN-6': {
        'name': 'South Central',
        'description': 'Southern Highland Rim',
        'counties': ['Bedford', 'Coffee', 'Giles', 'Lawrence', 'Lewis',
                     'Lincoln', 'Marshall', 'Maury', 'Moore', 'Perry', 'Wayne'],
        'cities': [],
        'characteristics': ['Rural', 'Agriculture', 'Manufacturing']
    },
    'TN-7': {
        'name': 'Northwest Tennessee',
        'description': 'Mississippi River region',
        'counties': ['Benton', 'Carroll', 'Crockett', 'Decatur', 'Dyer',
                     'Gibson', 'Hardin', 'Haywood', 'Henderson', 'Henry',
                     'Lake', 'Lauderdale', 'McNairy', 'Obion', 'Tipton', 'Weakley'],
        'cities': [],
        'characteristics': ['Agriculture', 'Rural', 'Manufacturing']
    },
    'TN-8': {
        'name': 'Memphis Metro',
        'description': 'Southwest Tennessee urban center',
        'counties': ['Fayette', 'Shelby'],
        'cities': [],
        'characteristics': ['Urban', 'Logistics', 'Diverse', 'River commerce']
    },
    'TN-9': {
        'name': 'Southern Middle Tennessee',
        'description': 'South-central rural region',
        'counties': ['Chester', 'Hardeman', 'Hardin', 'Wayne'],
        'cities': [],
        'characteristics': ['Rural', 'Agriculture', 'Low population']
    }
}

# =============================================================================
# KENTUCKY REGIONS (10 regions)
# =============================================================================

KENTUCKY_REGIONS = {
    'KY-1': {
        'name': 'Northern Kentucky',
        'description': 'Cincinnati metro area',
        'counties': ['Boone', 'Bracken', 'Campbell', 'Gallatin', 'Grant',
                     'Kenton', 'Pendleton'],
        'cities': [],
        'characteristics': ['Urban', 'Cincinnati suburbs', 'Growing', 'Wealthy']
    },
    'KY-2': {
        'name': 'Bluegrass',
        'description': 'Lexington region',
        'counties': ['Anderson', 'Bourbon', 'Boyle', 'Clark', 'Fayette',
                     'Franklin', 'Garrard', 'Harrison', 'Jessamine', 'Lincoln',
                     'Madison', 'Mercer', 'Nicholas', 'Scott', 'Woodford'],
        'cities': [],
        'characteristics': ['Horse farms', 'Urban', 'Wealthy', 'Universities']
    },
    'KY-3': {
        'name': 'Louisville Metro',
        'description': 'Major urban center',
        'counties': ['Bullitt', 'Henry', 'Jefferson', 'Oldham', 'Shelby',
                     'Spencer', 'Trimble'],
        'cities': [],
        'characteristics': ['Urban', 'Manufacturing', 'Logistics', 'Derby']
    },
    'KY-4': {
        'name': 'Eastern Mountains',
        'description': 'Appalachian coal region',
        'counties': ['Bell', 'Breathitt', 'Clay', 'Floyd', 'Harlan', 'Johnson',
                     'Knott', 'Knox', 'Laurel', 'Lee', 'Leslie', 'Letcher',
                     'McCreary', 'Magoffin', 'Martin', 'Owsley', 'Perry',
                     'Pike', 'Rockcastle', 'Whitley', 'Wolfe'],
        'cities': [],
        'characteristics': ['Coal', 'Appalachian', 'High poverty', 'Rural']
    },
    'KY-5': {
        'name': 'Northeast',
        'description': 'Ohio River valley',
        'counties': ['Bath', 'Boyd', 'Carter', 'Elliott', 'Fleming', 'Greenup',
                     'Lewis', 'Mason', 'Menifee', 'Montgomery', 'Morgan',
                     'Robertson', 'Rowan'],
        'cities': [],
        'characteristics': ['Ohio River', 'Manufacturing', 'Rural']
    },
    'KY-6': {
        'name': 'South Central',
        'description': 'Bowling Green region',
        'counties': ['Adair', 'Allen', 'Barren', 'Butler', 'Casey', 'Clinton',
                     'Cumberland', 'Edmonson', 'Grayson', 'Green', 'Hart',
                     'Larue', 'Marion', 'Metcalfe', 'Monroe', 'Russell',
                     'Simpson', 'Taylor', 'Warren', 'Washington'],
        'cities': [],
        'characteristics': ['Caves', 'Tourism', 'Manufacturing', 'University']
    },
    'KY-7': {
        'name': 'Pennyrile',
        'description': 'Western coal fields',
        'counties': ['Caldwell', 'Christian', 'Crittenden', 'Hopkins', 'Livingston',
                     'Lyon', 'McLean', 'Muhlenberg', 'Todd', 'Trigg', 'Webster'],
        'cities': [],
        'characteristics': ['Coal', 'Agriculture', 'Military', 'Rural']
    },
    'KY-8': {
        'name': 'Purchase',
        'description': 'Far western Kentucky',
        'counties': ['Ballard', 'Calloway', 'Carlisle', 'Fulton', 'Graves',
                     'Hickman', 'Marshall', 'McCracken'],
        'cities': [],
        'characteristics': ['Agriculture', 'Mississippi River', 'Rural']
    },
    'KY-9': {
        'name': 'Western',
        'description': 'Ohio River valley west',
        'counties': ['Breckinridge', 'Daviess', 'Hancock', 'Henderson', 'Meade',
                     'Ohio', 'Union'],
        'cities': [],
        'characteristics': ['Ohio River', 'Coal', 'Manufacturing']
    },
    'KY-10': {
        'name': 'East Central',
        'description': 'Daniel Boone region',
        'counties': ['Estill', 'Jackson', 'Laurel', 'Pulaski'],
        'cities': [],
        'characteristics': ['Rural', 'Manufacturing', 'Tourism']
    }
}

# =============================================================================
# DISTRICT OF COLUMBIA (1 region)
# =============================================================================

DC_REGION = {
    'DC-1': {
        'name': 'District of Columbia',
        'description': 'Federal district',
        'counties': [],  # DC has no counties
        'cities': ['District of Columbia'],
        'characteristics': ['Federal government', 'Urban', 'Wealthy', 'Diverse']
    }
}

# =============================================================================
# ALL REGIONS COMBINED
# =============================================================================

ALL_REGIONS = {
    **VIRGINIA_REGIONS,
    **MARYLAND_REGIONS,
    **WEST_VIRGINIA_REGIONS,
    **NORTH_CAROLINA_REGIONS,
    **TENNESSEE_REGIONS,
    **KENTUCKY_REGIONS,
    **DC_REGION
}

# Summary statistics
REGIONAL_SUMMARY = {
    'total_regions': len(ALL_REGIONS),
    'by_state': {
        'VA': len(VIRGINIA_REGIONS),
        'MD': len(MARYLAND_REGIONS),
        'WV': len(WEST_VIRGINIA_REGIONS),
        'NC': len(NORTH_CAROLINA_REGIONS),
        'TN': len(TENNESSEE_REGIONS),
        'KY': len(KENTUCKY_REGIONS),
        'DC': 1
    }
}


def get_region_by_code(region_code: str) -> Dict:
    """
    Get region details by region code (e.g., 'VA-1', 'MD-3').

    Args:
        region_code: Region code

    Returns:
        Dict with region information, or None if not found
    """
    return ALL_REGIONS.get(region_code)


def get_regions_by_state(state_code: str) -> Dict:
    """
    Get all regions for a specific state.

    Args:
        state_code: Two-letter state code (VA, MD, WV, NC, TN, KY, DC)

    Returns:
        Dict of regions for that state
    """
    state_code = state_code.upper()
    return {k: v for k, v in ALL_REGIONS.items() if k.startswith(f'{state_code}-')}


def find_region_for_county(state_code: str, county_name: str) -> str:
    """
    Find which region a county belongs to.

    Args:
        state_code: Two-letter state code
        county_name: County name (without "County" suffix)

    Returns:
        Region code, or None if not found
    """
    state_regions = get_regions_by_state(state_code)
    for region_code, region_info in state_regions.items():
        if county_name in region_info['counties']:
            return region_code
    return None


if __name__ == '__main__':
    print("Virginia Thriving Index - Regional Groupings")
    print("=" * 70)
    print(f"\nTotal analysis regions: {REGIONAL_SUMMARY['total_regions']}")
    print("\nRegions by state:")
    for state, count in REGIONAL_SUMMARY['by_state'].items():
        print(f"  {state}: {count} regions")

    print("\n" + "=" * 70)
    print("Sample regions:")

    for state in ['VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC']:
        regions = get_regions_by_state(state)
        print(f"\n{state} ({len(regions)} regions):")
        for code, info in list(regions.items())[:2]:  # Show first 2
            num_counties = len(info['counties'])
            num_cities = len(info.get('cities', []))
            print(f"  {code}: {info['name']}")
            print(f"       {num_counties} counties, {num_cities} cities")
            print(f"       {', '.join(info['characteristics'][:3])}")
