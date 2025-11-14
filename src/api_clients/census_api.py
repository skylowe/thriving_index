"""
Census Bureau API client for American Community Survey (ACS) data.

Provides access to demographic, economic, and social characteristics at county level.
"""

from typing import Dict, List, Optional, Union

from .base_api import BaseAPIClient
from ..utils.config import APIConfig, CacheConfig
from ..utils.logging_setup import setup_logger


class CensusAPI(BaseAPIClient):
    """
    Census Bureau API client for ACS 5-year estimates.

    Supports querying demographic, income, poverty, education, housing,
    and employment data at county level.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Census API client.

        Args:
            api_key: Census API key (defaults to config value)
        """
        if api_key is None:
            api_key = APIConfig.CENSUS_API_KEY

        super().__init__(
            api_key=api_key,
            base_url=APIConfig.CENSUS_BASE_URL,
            cache_expiry=CacheConfig.CENSUS_CACHE_EXPIRY,
            rate_limit=None,  # Census API has no explicit rate limit
            service_name="Census"
        )

        self.logger = setup_logger(f"{__name__}.CensusAPI")

    def _should_add_key_to_params(self) -> bool:
        """Census API uses 'key' parameter."""
        return True

    def _get_key_param_name(self) -> str:
        """Census API key parameter is 'key'."""
        return "key"

    def get_acs5_data(
        self,
        year: int,
        variables: Union[str, List[str]],
        geography: str = "county:*",
        state: Optional[str] = None,
        predicates: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        """
        Get ACS 5-year estimate data.

        Args:
            year: Year of ACS 5-year estimates (e.g., 2022 for 2018-2022)
            variables: Variable code(s) to retrieve (e.g., 'B01001_001E' for total population)
            geography: Geographic level (default: 'county:*' for all counties)
            state: State FIPS code (e.g., '51' for Virginia) or '*' for all states
            predicates: Additional query predicates

        Returns:
            List of dictionaries containing variable data by geography

        Example:
            >>> client = CensusAPI()
            >>> data = client.get_acs5_data(
            ...     year=2022,
            ...     variables=['B01001_001E', 'B19013_001E'],
            ...     geography='county:*',
            ...     state='51'
            ... )
        """
        # Handle variable input
        if isinstance(variables, str):
            variables = [variables]

        # Build endpoint
        endpoint = f"/{year}/acs/acs5"

        # Build parameters
        params = {
            'get': ','.join(['NAME'] + variables),
            'for': geography
        }

        # Add state filter if specified
        if state:
            params['in'] = f'state:{state}'

        # Add additional predicates
        if predicates:
            params.update(predicates)

        # Fetch data
        data = self.fetch(endpoint, params)

        # Parse response into list of dicts
        if isinstance(data, list) and len(data) > 1:
            headers = data[0]
            rows = data[1:]
            return [dict(zip(headers, row)) for row in rows]

        return []

    def get_population(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get total population by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with county population data
        """
        return self.get_acs5_data(
            year=year,
            variables='B01001_001E',  # Total population
            state=state
        )

    def get_median_household_income(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get median household income by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with median household income data
        """
        return self.get_acs5_data(
            year=year,
            variables='B19013_001E',  # Median household income
            state=state
        )

    def get_poverty_rate(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get poverty rate by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with poverty data
        """
        variables = [
            'B17001_001E',  # Total population for poverty determination
            'B17001_002E'   # Population below poverty level
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_educational_attainment(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get educational attainment data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with educational attainment data
        """
        variables = [
            'B15003_001E',  # Total population 25 years and over
            'B15003_022E',  # Bachelor's degree
            'B15003_023E',  # Master's degree
            'B15003_024E',  # Professional school degree
            'B15003_025E'   # Doctorate degree
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_housing_costs(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get housing cost data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with housing cost data
        """
        variables = [
            'B25077_001E',  # Median home value
            'B25064_001E'   # Median gross rent
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_labor_force_participation(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get labor force participation data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with labor force data
        """
        variables = [
            'B23025_001E',  # Total population 16 years and over
            'B23025_002E',  # In labor force
            'B23025_003E',  # Civilian labor force
            'B23025_004E'   # Employed
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_age_distribution(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get age distribution data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with age distribution data
        """
        # Get key age groups for demographic analysis
        variables = [
            'B01001_001E',  # Total population
            'B01001_003E',  # Male under 5
            'B01001_027E',  # Female under 5
            'B01001_007E',  # Male 18-19
            'B01001_031E',  # Female 18-19
            'B01001_020E',  # Male 65-66
            'B01001_044E'   # Female 65-66
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_commuting_patterns(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get commuting pattern data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with commuting data
        """
        variables = [
            'B08303_001E',  # Total workers 16 years and over
            'B08303_013E'   # Mean travel time to work (minutes)
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_industry_employment(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get industry employment data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with industry employment data
        """
        variables = [
            'C24030_001E',  # Total civilian employed population 16 years and over
            'C24030_003E',  # Agriculture, forestry, fishing, hunting, mining
            'C24030_009E',  # Manufacturing
            'C24030_022E',  # Educational services, health care, social assistance
            'C24030_028E'   # Arts, entertainment, recreation, accommodation, food services
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    def get_health_insurance_coverage(
        self,
        year: int,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Get health insurance coverage data by county.

        Args:
            year: Year of ACS 5-year estimates
            state: State FIPS code or '*' for all states

        Returns:
            List of dicts with health insurance data
        """
        variables = [
            'B27001_001E',  # Total civilian noninstitutionalized population
            'B27001_005E'   # No health insurance coverage
        ]

        return self.get_acs5_data(
            year=year,
            variables=variables,
            state=state
        )

    @staticmethod
    def get_state_fips_codes() -> Dict[str, str]:
        """
        Get FIPS codes for states in the study.

        Returns:
            Dictionary mapping state abbreviations to FIPS codes
        """
        return {
            'VA': '51',
            'MD': '24',
            'WV': '54',
            'NC': '37',
            'TN': '47',
            'KY': '21',
            'DC': '11'
        }

    def get_all_states_data(
        self,
        year: int,
        method_name: str,
        **kwargs
    ) -> Dict[str, List[Dict]]:
        """
        Get data for all states in the study.

        Args:
            year: Year of ACS 5-year estimates
            method_name: Name of method to call (e.g., 'get_population')
            **kwargs: Additional keyword arguments to pass to method

        Returns:
            Dictionary mapping state abbreviations to data lists
        """
        states = self.get_state_fips_codes()
        results = {}

        method = getattr(self, method_name)

        for state_abbr, state_fips in states.items():
            self.logger.info(f"Fetching {method_name} for {state_abbr}")
            results[state_abbr] = method(year=year, state=state_fips, **kwargs)

        return results


# Variable code reference for common measures
ACS_VARIABLE_CODES = {
    # Population
    'total_population': 'B01001_001E',
    'median_age': 'B01002_001E',

    # Income
    'median_household_income': 'B19013_001E',
    'per_capita_income': 'B19301_001E',

    # Poverty
    'poverty_total': 'B17001_001E',
    'poverty_below': 'B17001_002E',

    # Education
    'education_total_25plus': 'B15003_001E',
    'education_bachelors': 'B15003_022E',
    'education_graduate': 'B15003_023E',  # Master's
    'education_professional': 'B15003_024E',
    'education_doctorate': 'B15003_025E',

    # Housing
    'median_home_value': 'B25077_001E',
    'median_gross_rent': 'B25064_001E',

    # Labor force
    'labor_force_total': 'B23025_001E',
    'labor_force_in': 'B23025_002E',
    'labor_force_employed': 'B23025_004E',

    # Health insurance
    'health_insurance_total': 'B27001_001E',
    'health_insurance_none': 'B27001_005E',

    # Commuting
    'commute_total': 'B08303_001E',
    'commute_mean_time': 'B08303_013E',
}
