"""
Metropolitan and Micropolitan Statistical Area Database

Contains MSA/μSA definitions, populations, and geographic coordinates
for distance calculations in peer region matching.

Based on Census Bureau CBSA definitions (2023).
"""

from typing import Dict, List

# MSA Database
# Format: {cbsa_code: {name, population, lat, lon, type}}

MSA_DATABASE = {
    # Large MSAs (Population > 250,000)
    '47900': {
        'name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV',
        'population': 6385162,
        'lat': 38.9072,
        'lon': -77.0369,
        'type': 'metro',
        'size': 'large'
    },
    '12060': {
        'name': 'Atlanta-Sandy Springs-Alpharetta, GA',
        'population': 6144050,
        'lat': 33.7490,
        'lon': -84.3880,
        'type': 'metro',
        'size': 'large'
    },
    '40060': {
        'name': 'Richmond, VA',
        'population': 1327552,
        'lat': 37.5407,
        'lon': -77.4360,
        'type': 'metro',
        'size': 'large'
    },
    '47260': {
        'name': 'Virginia Beach-Norfolk-Newport News, VA-NC',
        'population': 1799674,
        'lat': 36.8529,
        'lon': -76.2859,
        'type': 'metro',
        'size': 'large'
    },
    '12580': {
        'name': 'Baltimore-Columbia-Towson, MD',
        'population': 2834316,
        'lat': 39.2904,
        'lon': -76.6122,
        'type': 'metro',
        'size': 'large'
    },
    '16740': {
        'name': 'Charlotte-Concord-Gastonia, NC-SC',
        'population': 2660329,
        'lat': 35.2271,
        'lon': -80.8431,
        'type': 'metro',
        'size': 'large'
    },
    '39580': {
        'name': 'Raleigh-Cary, NC',
        'population': 1467069,
        'lat': 35.7796,
        'lon': -78.6382,
        'type': 'metro',
        'size': 'large'
    },
    '24660': {
        'name': 'Greensboro-High Point, NC',
        'population': 789842,
        'lat': 36.0726,
        'lon': -79.7920,
        'type': 'metro',
        'size': 'large'
    },
    '20500': {
        'name': 'Durham-Chapel Hill, NC',
        'population': 649903,
        'lat': 35.9940,
        'lon': -78.8986,
        'type': 'metro',
        'size': 'large'
    },
    '34980': {
        'name': 'Nashville-Davidson--Murfreesboro--Franklin, TN',
        'population': 2012649,
        'lat': 36.1627,
        'lon': -86.7816,
        'type': 'metro',
        'size': 'large'
    },
    '28940': {
        'name': 'Knoxville, TN',
        'population': 903300,
        'lat': 35.9606,
        'lon': -83.9207,
        'type': 'metro',
        'size': 'large'
    },
    '32820': {
        'name': 'Memphis, TN-MS-AR',
        'population': 1346045,
        'lat': 35.1495,
        'lon': -90.0490,
        'type': 'metro',
        'size': 'large'
    },
    '31140': {
        'name': 'Louisville/Jefferson County, KY-IN',
        'population': 1306129,
        'lat': 38.2527,
        'lon': -85.7585,
        'type': 'metro',
        'size': 'large'
    },
    '30460': {
        'name': 'Lexington-Fayette, KY',
        'population': 517056,
        'lat': 38.0406,
        'lon': -84.5037,
        'type': 'metro',
        'size': 'large'
    },

    # Small MSAs (Population 50,000 - 250,000)
    '16820': {
        'name': 'Charlottesville, VA',
        'population': 235232,
        'lat': 38.0293,
        'lon': -78.4767,
        'type': 'metro',
        'size': 'small'
    },
    '40220': {
        'name': 'Roanoke, VA',
        'population': 315251,
        'lat': 37.2710,
        'lon': -79.9414,
        'type': 'metro',
        'size': 'small'
    },
    '11700': {
        'name': 'Asheville, NC',
        'population': 469015,
        'lat': 35.5951,
        'lon': -82.5515,
        'type': 'metro',
        'size': 'small'
    },
    '11260': {
        'name': 'Annapolis, MD',
        'population': 587994,
        'lat': 38.9784,
        'lon': -76.4922,
        'type': 'metro',
        'size': 'small'
    },
    '25180': {
        'name': 'Hagerstown-Martinsburg, MD-WV',
        'population': 293844,
        'lat': 39.6418,
        'lon': -77.7200,
        'type': 'metro',
        'size': 'small'
    },
    '16620': {
        'name': 'Charleston, WV',
        'population': 208089,
        'lat': 38.3498,
        'lon': -81.6326,
        'type': 'metro',
        'size': 'small'
    },
    '26580': {
        'name': 'Huntington-Ashland, WV-KY-OH',
        'population': 356298,
        'lat': 38.4192,
        'lon': -82.4452,
        'type': 'metro',
        'size': 'small'
    },
    '33460': {
        'name': 'Minneapolis-St. Paul-Bloomington, MN-WI',
        'population': 3690261,
        'lat': 44.9778,
        'lon': -93.2650,
        'type': 'metro',
        'size': 'large'
    },

    # Micropolitan Areas (Population 10,000 - 50,000)
    '11820': {
        'name': 'Blacksburg-Christiansburg, VA',
        'population': 181863,
        'lat': 37.2296,
        'lon': -80.4139,
        'type': 'micro',
        'size': 'micro'
    },
    '40740': {
        'name': 'Danville, VA',
        'population': 42590,
        'lat': 36.5860,
        'lon': -79.3950,
        'type': 'micro',
        'size': 'micro'
    },
    '47900': {
        'name': 'Martinsville, VA',
        'population': 45699,
        'lat': 36.6915,
        'lon': -79.8725,
        'type': 'micro',
        'size': 'micro'
    },
}


def get_msa_by_code(cbsa_code: str) -> Dict:
    """
    Get MSA information by CBSA code.

    Args:
        cbsa_code: 5-digit CBSA code

    Returns:
        Dictionary with MSA info
    """
    return MSA_DATABASE.get(cbsa_code, None)


def get_msas_by_size(size: str) -> List[Dict]:
    """
    Get all MSAs of a specific size category.

    Args:
        size: 'large', 'small', or 'micro'

    Returns:
        List of MSA dictionaries
    """
    return [msa for msa in MSA_DATABASE.values() if msa['size'] == size]


def get_nearest_msa(lat: float, lon: float, size: str = None) -> Dict:
    """
    Find nearest MSA to a given coordinate.

    Args:
        lat: Latitude
        lon: Longitude
        size: Optional size filter ('large', 'small', 'micro')

    Returns:
        Nearest MSA dictionary with distance
    """
    from math import radians, sin, cos, sqrt, atan2

    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate great circle distance in miles."""
        R = 3959  # Earth radius in miles

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    nearest = None
    min_distance = float('inf')

    msas = MSA_DATABASE.values()
    if size:
        msas = [msa for msa in msas if msa['size'] == size]

    for msa in msas:
        distance = haversine_distance(lat, lon, msa['lat'], msa['lon'])
        if distance < min_distance:
            min_distance = distance
            nearest = {**msa, 'distance': distance}

    return nearest


# TODO: Complete MSA database with all relevant metropolitan and micropolitan areas
# This is a representative subset. Full implementation would include:
# - All MSAs in VA, MD, WV, NC, TN, KY, DC
# - All micropolitan areas in the study region
# - Accurate 2023 population estimates
# - Precise geographic coordinates (city centers or population centroids)
#
# Data sources:
# - Census Bureau CBSA Delineation Files
# - Annual Estimates of Metropolitan and Micropolitan Statistical Areas
# - Tiger/Line Shapefiles for geographic coordinates
