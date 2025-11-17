"""
Census ACS (American Community Survey) API Client

This client retrieves data from the Census ACS API.
Primary use: Demographic, household, education, and housing data

Documentation: https://www.census.gov/data/developers/data-sets/acs-5year.html
"""

import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CENSUS_API_KEY, CENSUS_API_BASE, REQUEST_DELAY, MAX_RETRIES, TIMEOUT, RAW_DATA_DIR


class CensusClient:
    """Client for Census ACS API"""

    def __init__(self, api_key=None):
        """
        Initialize Census API client.

        Args:
            api_key: Census API key. If None, uses key from config.
        """
        self.api_key = api_key or CENSUS_API_KEY
        if not self.api_key:
            raise ValueError("Census API key is required")

        self.base_url = CENSUS_API_BASE
        self.session = requests.Session()

    def _make_request(self, url, params, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            url: Full API URL
            params: Dictionary of query parameters
            retries: Number of retries remaining

        Returns:
            dict: JSON response from API
        """
        params['key'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # Census API returns errors as JSON with single element containing error message
            if len(data) == 1 and isinstance(data[0], str) and 'error' in data[0].lower():
                raise Exception(f"Census API Error: {data[0]}")

            time.sleep(REQUEST_DELAY)
            return data

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1)
            else:
                raise Exception(f"Census API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_acs5_data(self, year, variables, geography, state_fips=None):
        """
        Get ACS 5-year estimates data.

        Args:
            year: Year of ACS 5-year period end (e.g., 2022 for 2018-2022)
            variables: List of variable codes or comma-separated string
            geography: Geographic level (e.g., 'county:*' for all counties)
            state_fips: State FIPS code (required for county-level data)

        Returns:
            list: API response as list of lists (first row is headers)
        """
        if isinstance(variables, list):
            variables = ','.join(variables)

        url = f"{self.base_url}/{year}/acs/acs5"

        params = {
            'get': variables,
            'for': geography
        }

        # Add state filter if provided
        if state_fips:
            params['in'] = f'state:{state_fips}'

        return self._make_request(url, params)

    def get_acs5_subject_table(self, year, variables, geography, state_fips=None):
        """
        Get ACS 5-year subject table data (S-tables).

        Args:
            year: Year of ACS 5-year period end
            variables: List of variable codes or comma-separated string
            geography: Geographic level
            state_fips: State FIPS code (required for county-level data)

        Returns:
            list: API response as list of lists
        """
        if isinstance(variables, list):
            variables = ','.join(variables)

        url = f"{self.base_url}/{year}/acs/acs5/subject"

        params = {
            'get': variables,
            'for': geography
        }

        if state_fips:
            params['in'] = f'state:{state_fips}'

        return self._make_request(url, params)

    def get_households_with_children(self, year, state_fips=None):
        """
        Get households with children data from Table S1101.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code (None for all states)

        Returns:
            list: API response with household data
        """
        # S1101_C01_002E = Households with one or more people under 18 years
        # S1101_C01_001E = Total households
        variables = ['NAME', 'S1101_C01_002E', 'S1101_C01_001E']

        if state_fips:
            geography = 'county:*'
            return self.get_acs5_subject_table(year, variables, geography, state_fips)
        else:
            # Get for all counties (need to specify state)
            raise ValueError("state_fips required for county-level data")

    def get_poverty_rate(self, year, state_fips=None):
        """
        Get poverty rate data from ACS.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with poverty data
        """
        # S1701_C03_001E = Percent below poverty level
        variables = ['NAME', 'S1701_C03_001E']

        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    def get_education_attainment(self, year, state_fips):
        """
        Get educational attainment data.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with education data
        """
        # S1501 - Educational Attainment
        # S1501_C02_015E = Percent bachelor's degree or higher (25+ population)
        # S1501_C02_014E = Percent associate's degree or higher
        # S1501_C02_009E = Percent high school graduate or higher
        variables = [
            'NAME',
            'S1501_C02_015E',  # Bachelor's or higher
            'S1501_C02_014E',  # Associate's or higher
            'S1501_C02_009E'   # HS diploma or higher
        ]

        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    def get_housing_values(self, year, state_fips):
        """
        Get median housing value and gross rent data.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with housing data
        """
        # B25077_001E = Median value (owner-occupied units)
        # B25064_001E = Median gross rent
        variables = ['NAME', 'B25077_001E', 'B25064_001E']

        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_occupation_data(self, year, state_fips):
        """
        Get occupation by major groups from Table S2401 for diversity calculations.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with occupation data
        """
        # S2401 - Occupation by Sex and Median Earnings
        # Get employment counts by major occupation group
        variables = [
            'NAME',
            'S2401_C01_001E',  # Total civilian employed population 16 years and over
            'S2401_C01_002E',  # Management, business, science, and arts occupations
            'S2401_C01_003E',  # Service occupations
            'S2401_C01_004E',  # Sales and office occupations
            'S2401_C01_005E',  # Natural resources, construction, and maintenance occupations
            'S2401_C01_006E',  # Production, transportation, and material moving occupations
        ]

        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    def get_telecommuter_data(self, year, state_fips):
        """
        Get telecommuter (work from home) data from Table B08128.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with telecommuter data
        """
        # B08128 - Means of Transportation to Work by Class of Worker
        # B08128_001E = Total workers 16 years and over
        # B08128_002E = Workers who worked at home
        # B08128_003E = Worked at home: Private wage and salary workers
        # B08128_009E = Worked at home: Self-employed in own not incorporated business workers
        # B08128_013E = Worked at home: Self-employed in own incorporated business workers
        variables = [
            'NAME',
            'B08128_001E',  # Total workers
            'B08128_002E',  # Total worked at home
            'B08128_003E',  # Worked at home: Private wage and salary
            'B08128_009E',  # Worked at home: Self-employed not incorporated
            'B08128_013E',  # Worked at home: Self-employed incorporated
        ]

        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    # ===== Component 4: Demographic Growth & Renewal Methods =====

    def get_decennial_population_2000(self, state_fips):
        """
        Get total population from 2000 Decennial Census (for long-run growth).

        Args:
            state_fips: State FIPS code

        Returns:
            list: API response with population data
        """
        # P001001 = Total population (SF1 table)
        url = f"{self.base_url}/2000/dec/sf1"

        params = {
            'get': 'NAME,P001001',
            'for': 'county:*',
            'in': f'state:{state_fips}',
            'key': self.api_key
        }

        return self._make_request(url, params)

    def get_population_total(self, year, state_fips):
        """
        Get total population from ACS (for current population and growth calculations).

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with population data
        """
        # B01001_001E = Total population
        variables = ['NAME', 'B01001_001E']
        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_age_distribution(self, year, state_fips):
        """
        Get detailed age distribution from ACS for dependency ratio calculations.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with age distribution data
        """
        # B01001 - Sex by Age
        # We need age breakdowns to calculate dependency ratio
        # Under 15: sum of age 0-14 groups
        # 15-64: working age population
        # 65+: elderly dependents
        variables = [
            'NAME',
            'B01001_001E',  # Total population
            # Male population by age
            'B01001_003E',  # Male: Under 5 years
            'B01001_004E',  # Male: 5 to 9 years
            'B01001_005E',  # Male: 10 to 14 years
            'B01001_006E',  # Male: 15 to 17 years
            'B01001_007E',  # Male: 18 and 19 years
            'B01001_008E',  # Male: 20 years
            'B01001_009E',  # Male: 21 years
            'B01001_010E',  # Male: 22 to 24 years
            'B01001_011E',  # Male: 25 to 29 years
            'B01001_012E',  # Male: 30 to 34 years
            'B01001_013E',  # Male: 35 to 39 years
            'B01001_014E',  # Male: 40 to 44 years
            'B01001_015E',  # Male: 45 to 49 years
            'B01001_016E',  # Male: 50 to 54 years
            'B01001_017E',  # Male: 55 to 59 years
            'B01001_018E',  # Male: 60 and 61 years
            'B01001_019E',  # Male: 62 to 64 years
            'B01001_020E',  # Male: 65 and 66 years
            'B01001_021E',  # Male: 67 to 69 years
            'B01001_022E',  # Male: 70 to 74 years
            'B01001_023E',  # Male: 75 to 79 years
            'B01001_024E',  # Male: 80 to 84 years
            'B01001_025E',  # Male: 85 years and over
            # Female population by age
            'B01001_027E',  # Female: Under 5 years
            'B01001_028E',  # Female: 5 to 9 years
            'B01001_029E',  # Female: 10 to 14 years
            'B01001_030E',  # Female: 15 to 17 years
            'B01001_031E',  # Female: 18 and 19 years
            'B01001_032E',  # Female: 20 years
            'B01001_033E',  # Female: 21 years
            'B01001_034E',  # Female: 22 to 24 years
            'B01001_035E',  # Female: 25 to 29 years
            'B01001_036E',  # Female: 30 to 34 years
            'B01001_037E',  # Female: 35 to 39 years
            'B01001_038E',  # Female: 40 to 44 years
            'B01001_039E',  # Female: 45 to 49 years
            'B01001_040E',  # Female: 50 to 54 years
            'B01001_041E',  # Female: 55 to 59 years
            'B01001_042E',  # Female: 60 and 61 years
            'B01001_043E',  # Female: 62 to 64 years
            'B01001_044E',  # Female: 65 and 66 years
            'B01001_045E',  # Female: 67 to 69 years
            'B01001_046E',  # Female: 70 to 74 years
            'B01001_047E',  # Female: 75 to 79 years
            'B01001_048E',  # Female: 80 to 84 years
            'B01001_049E',  # Female: 85 years and over
        ]

        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_median_age(self, year, state_fips):
        """
        Get median age from ACS.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with median age data
        """
        # B01002_001E = Median age
        variables = ['NAME', 'B01002_001E']
        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_hispanic_data(self, year, state_fips):
        """
        Get Hispanic/Latino population data from ACS.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with Hispanic data
        """
        # B03003 - Hispanic or Latino Origin
        # B03003_001E = Total population
        # B03003_003E = Hispanic or Latino
        variables = ['NAME', 'B03003_001E', 'B03003_003E']
        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_race_data(self, year, state_fips):
        """
        Get race distribution data from ACS for non-white percentage calculation.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with race data
        """
        # B02001 - Race
        # B02001_001E = Total population
        # B02001_002E = White alone
        variables = ['NAME', 'B02001_001E', 'B02001_002E']
        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    # ===== Component 5: Education & Skill Methods =====

    def get_education_detailed(self, year, state_fips):
        """
        Get detailed educational attainment data for EXCLUSIVE categories.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with detailed education data
        """
        # B15003 - Educational Attainment for the Population 25 Years and Over
        # Need exclusive categories (highest level achieved)
        variables = [
            'NAME',
            'B15003_001E',  # Total population 25 years and over
            'B15003_017E',  # Regular high school diploma
            'B15003_018E',  # GED or alternative credential
            'B15003_021E',  # Associate's degree
            'B15003_022E',  # Bachelor's degree
        ]
        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_labor_force_participation(self, year, state_fips):
        """
        Get labor force participation data from ACS.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with labor force data
        """
        # B23025 - Employment Status for the Population 16 Years and Over
        # B23025_001E = Total population 16 years and over
        # B23025_002E = In labor force
        variables = ['NAME', 'B23025_001E', 'B23025_002E']
        geography = 'county:*'
        return self.get_acs5_data(year, variables, geography, state_fips)

    def get_knowledge_workers(self, year, state_fips):
        """
        Get employment by occupation for knowledge worker calculation.

        Uses occupational categories as a proxy for knowledge workers since industry tables
        have variable naming issues. Management/professional/science/arts occupations
        serve as a good proxy for knowledge-intensive work.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with occupation employment data
        """
        # S2401 - Occupation by Sex and Median Earnings
        # Use occupation groups as proxy for knowledge workers
        variables = [
            'NAME',
            'S2401_C01_001E',  # Total civilian employed population 16 years and over
            'S2401_C01_002E',  # Management, business, science, and arts occupations
        ]
        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    # ===== Component 7: Quality of Life Methods =====

    def get_commute_time(self, year, state_fips):
        """
        Get average commute time data from ACS Table S0801.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with commute time data
        """
        # S0801 - Commuting Characteristics by Sex
        # S0801_C01_046E = Mean travel time to work (minutes)
        variables = ['NAME', 'S0801_C01_046E']
        geography = 'county:*'
        return self.get_acs5_subject_table(year, variables, geography, state_fips)

    def get_housing_age(self, year, state_fips):
        """
        Get housing age data from ACS for pre-1960 housing calculation.

        Args:
            year: Year of ACS 5-year period end
            state_fips: State FIPS code

        Returns:
            list: API response with housing age data
        """
        # DP04 - Selected Housing Characteristics (Profile table)
        # Need to use profile endpoint
        url = f"{self.base_url}/{year}/acs/acs5/profile"

        variables = [
            'NAME',
            'DP04_0033E',  # Total housing units
            'DP04_0035E',  # Built 1939 or earlier
            'DP04_0036E',  # Built 1940 to 1949
            'DP04_0037E',  # Built 1950 to 1959
        ]

        params = {
            'get': ','.join(variables),
            'for': 'county:*',
            'in': f'state:{state_fips}',
            'key': self.api_key
        }

        return self._make_request(url, params)

    def parse_response_to_dict(self, response):
        """
        Convert Census API response to list of dictionaries.

        Args:
            response: Census API response (list of lists)

        Returns:
            list: List of dictionaries with column names as keys
        """
        if not response or len(response) < 2:
            return []

        headers = response[0]
        data_rows = response[1:]

        return [dict(zip(headers, row)) for row in data_rows]

    def save_response(self, data, filename):
        """
        Save API response to file.

        Args:
            data: Response data (list)
            filename: Output filename (will be saved in data/raw/census/)
        """
        output_dir = RAW_DATA_DIR / 'census'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved: {output_path}")


if __name__ == '__main__':
    # Test the Census client
    print("Testing Census ACS API Client...")
    print("=" * 60)

    client = CensusClient()

    # Test 1: Get households with children for Virginia (2022)
    print("\nTest 1: Households with Children - Virginia (2022)")
    print("-" * 60)
    try:
        data = client.get_households_with_children(2022, state_fips='51')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
        print(f"Headers: {data[0]}")
        if len(data) > 1:
            print(f"Sample row: {data[1]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get poverty rate for Delaware (2022)
    print("\nTest 2: Poverty Rate - Delaware (2022)")
    print("-" * 60)
    try:
        data = client.get_poverty_rate(2022, state_fips='10')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
        parsed = client.parse_response_to_dict(data)
        if parsed:
            print(f"Sample parsed record: {parsed[0]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Get housing values for Maryland (2022)
    print("\nTest 3: Housing Values - Maryland (2022)")
    print("-" * 60)
    try:
        data = client.get_housing_values(2022, state_fips='24')
        print(f"✓ Retrieved data for {len(data) - 1} counties")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Census ACS API Client test complete")
