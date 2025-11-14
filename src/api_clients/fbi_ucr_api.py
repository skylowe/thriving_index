"""
FBI Uniform Crime Reporting (UCR) API client.

Provides access to crime statistics including:
- Violent crime rates (murder, rape, robbery, aggravated assault)
- Property crime rates (burglary, larceny-theft, motor vehicle theft)
- Clearance rates
- Arrest data

API Documentation: https://cde.ucr.cde.fbi.gov/LATEST/webapp/#/pages/docApi
"""

from typing import Dict, List, Optional, Union
import time

from .base_api import BaseAPIClient
from ..utils.config import APIConfig, CacheConfig
from ..utils.logging_setup import setup_logger


class FBIUCRAPI(BaseAPIClient):
    """
    FBI UCR Crime Data Explorer API client.

    Provides access to crime statistics at state and agency level.
    Note: County-level aggregation requires summing agency-level data.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FBI UCR API client.

        Args:
            api_key: FBI UCR API key (defaults to config value)
        """
        if api_key is None:
            api_key = APIConfig.FBI_UCR_KEY

        super().__init__(
            api_key=api_key,
            base_url=APIConfig.FBI_UCR_BASE_URL,
            cache_expiry=CacheConfig.FBI_UCR_CACHE_EXPIRY,
            rate_limit=None,  # No explicit rate limit documented
            service_name="FBI_UCR"
        )

        self.logger = setup_logger(f"{__name__}.FBIUCRAPI")

    def _should_add_key_to_params(self) -> bool:
        """FBI UCR API uses 'API_KEY' header."""
        return False

    def _get_key_param_name(self) -> str:
        """FBI UCR API key is in header."""
        return "API_KEY"

    def fetch(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True,
        method: str = "GET"
    ) -> Dict:
        """
        Override fetch to add API key to headers.

        Args:
            endpoint: API endpoint
            params: Request parameters
            use_cache: Whether to use cache
            method: HTTP method

        Returns:
            API response data
        """
        # Add API key to headers if available
        import requests

        if params is None:
            params = {}

        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key

        # Build full URL
        url = self.base_url + endpoint

        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(url, params)
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        # Make request
        self.logger.info(f"Fetching from FBI UCR API: {endpoint}")

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            else:
                response = requests.post(url, json=params, headers=headers)

            response.raise_for_status()
            data = response.json()

            # Cache the response
            if use_cache:
                self._save_cache(cache_key, data)

            return data

        except Exception as e:
            self.logger.error(f"FBI UCR API request failed: {e}")
            raise

    def get_state_crime_summary(
        self,
        state_abbr: str,
        year: int
    ) -> Dict:
        """
        Get crime summary for a state.

        Args:
            state_abbr: State abbreviation (e.g., 'VA', 'MD')
            year: Year for data collection

        Returns:
            API response with state crime data

        Example:
            >>> client = FBIUCRAPI()
            >>> data = client.get_state_crime_summary('VA', 2022)
        """
        endpoint = f"/api/summarized/state/{state_abbr}/offense/{year}"
        return self.fetch(endpoint)

    def get_agencies_by_state(
        self,
        state_abbr: str
    ) -> Dict:
        """
        Get list of reporting agencies in a state.

        Args:
            state_abbr: State abbreviation

        Returns:
            API response with agency list
        """
        endpoint = f"/api/agencies/byStateAbbr/{state_abbr}"
        return self.fetch(endpoint)

    def get_agency_crime_data(
        self,
        ori: str,
        year: int
    ) -> Dict:
        """
        Get crime data for a specific agency.

        Args:
            ori: Originating Agency Identifier (9-character code)
            year: Year for data collection

        Returns:
            API response with agency crime data

        Note:
            ORIs are unique identifiers for law enforcement agencies.
            Use get_agencies_by_state() to find ORIs.
        """
        endpoint = f"/api/summarized/agency/{ori}/offense/{year}"
        return self.fetch(endpoint)

    def get_violent_crime_rate(
        self,
        state_abbr: str,
        year: int
    ) -> Dict:
        """
        Get violent crime rate for a state.

        Args:
            state_abbr: State abbreviation
            year: Year for data collection

        Returns:
            API response with violent crime data
        """
        endpoint = f"/api/summarized/state/{state_abbr}/offense/{year}"

        response = self.fetch(endpoint)

        # Filter for violent crimes
        if response and 'data' in response:
            violent_crimes = ['violent-crime', 'murder', 'rape', 'robbery', 'aggravated-assault']
            response['violent_data'] = [
                item for item in response['data']
                if item.get('offense') in violent_crimes
            ]

        return response

    def get_property_crime_rate(
        self,
        state_abbr: str,
        year: int
    ) -> Dict:
        """
        Get property crime rate for a state.

        Args:
            state_abbr: State abbreviation
            year: Year for data collection

        Returns:
            API response with property crime data
        """
        endpoint = f"/api/summarized/state/{state_abbr}/offense/{year}"

        response = self.fetch(endpoint)

        # Filter for property crimes
        if response and 'data' in response:
            property_crimes = ['property-crime', 'burglary', 'larceny', 'motor-vehicle-theft']
            response['property_data'] = [
                item for item in response['data']
                if item.get('offense') in property_crimes
            ]

        return response

    def get_county_crime_estimate(
        self,
        state_abbr: str,
        county_name: str,
        year: int
    ) -> Dict:
        """
        Estimate county crime rates by aggregating agency data.

        Args:
            state_abbr: State abbreviation
            county_name: County name
            year: Year for data collection

        Returns:
            Aggregated crime data for the county

        Note:
            FBI UCR doesn't provide direct county-level data.
            This method aggregates data from agencies within the county.
        """
        # Get all agencies in the state
        agencies_response = self.get_agencies_by_state(state_abbr)

        if not agencies_response or 'data' not in agencies_response:
            return {'error': 'No agency data available'}

        # Filter agencies by county
        county_agencies = [
            agency for agency in agencies_response['data']
            if county_name.lower() in agency.get('county_name', '').lower()
        ]

        # Aggregate crime data from all agencies in the county
        county_crimes = {
            'violent': 0,
            'property': 0,
            'population': 0,
            'agencies': len(county_agencies)
        }

        for agency in county_agencies:
            ori = agency.get('ori')
            if ori:
                try:
                    agency_data = self.get_agency_crime_data(ori, year)
                    if agency_data and 'data' in agency_data:
                        for offense in agency_data['data']:
                            offense_type = offense.get('offense', '')
                            actual = offense.get('actual', 0)

                            if offense_type == 'violent-crime':
                                county_crimes['violent'] += actual
                            elif offense_type == 'property-crime':
                                county_crimes['property'] += actual

                        # Add population
                        county_crimes['population'] += agency.get('population', 0)

                    # Rate limiting
                    time.sleep(0.2)

                except Exception as e:
                    self.logger.warning(f"Failed to get data for agency {ori}: {e}")

        # Calculate rates per 100,000 population
        if county_crimes['population'] > 0:
            county_crimes['violent_rate'] = (county_crimes['violent'] / county_crimes['population']) * 100000
            county_crimes['property_rate'] = (county_crimes['property'] / county_crimes['population']) * 100000

        return county_crimes

    def get_all_states_crime_data(
        self,
        year: int,
        state_list: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Get crime data for multiple states.

        Args:
            year: Year for data collection
            state_list: List of state abbreviations (defaults to study states)

        Returns:
            Dictionary mapping state codes to crime data
        """
        if state_list is None:
            state_list = ['VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC']

        results = {}

        for state_abbr in state_list:
            self.logger.info(f"Fetching crime data for {state_abbr}")
            try:
                data = self.get_state_crime_summary(state_abbr, year)
                results[state_abbr] = data
                # Rate limiting
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"Failed to fetch crime data for {state_abbr}: {e}")
                results[state_abbr] = None

        return results


# FBI UCR offense codes
UCR_OFFENSE_CODES = {
    'violent': {
        'murder': 'Murder and nonnegligent manslaughter',
        'rape': 'Rape',
        'robbery': 'Robbery',
        'aggravated-assault': 'Aggravated assault'
    },
    'property': {
        'burglary': 'Burglary',
        'larceny': 'Larceny-theft',
        'motor-vehicle-theft': 'Motor vehicle theft',
        'arson': 'Arson'
    }
}

# State abbreviation to FIPS mapping
STATE_ABBR_TO_FIPS = {
    'VA': '51',
    'MD': '24',
    'WV': '54',
    'NC': '37',
    'TN': '47',
    'KY': '21',
    'DC': '11'
}
