"""
Bureau of Labor Statistics (BLS) API client.

Provides access to unemployment rates, employment data, and wages
through the Local Area Unemployment Statistics (LAUS) and
Quarterly Census of Employment and Wages (QCEW) programs.
"""

from typing import Dict, List, Optional, Union

from .base_api import BaseAPIClient
from ..utils.config import APIConfig, CacheConfig
from ..utils.logging_setup import setup_logger


class BLSAPI(BaseAPIClient):
    """
    BLS API client for LAUS and QCEW data.

    Supports querying unemployment rates, employment by industry,
    and wages at county level.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BLS API client.

        Args:
            api_key: BLS API key (defaults to config value)
        """
        if api_key is None:
            api_key = APIConfig.BLS_API_KEY

        super().__init__(
            api_key=api_key,
            base_url=APIConfig.BLS_BASE_URL,
            cache_expiry=CacheConfig.BLS_CACHE_EXPIRY,
            rate_limit=500,  # 500 queries per day for registered users
            service_name="BLS"
        )

        self.logger = setup_logger(f"{__name__}.BLSAPI")

    def _should_add_key_to_params(self) -> bool:
        """BLS API uses POST with key in JSON body."""
        return False

    def _get_key_param_name(self) -> str:
        """BLS API key parameter is 'registrationkey'."""
        return "registrationkey"

    def fetch(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True,
        method: str = "POST"
    ) -> Dict:
        """
        Override fetch to handle BLS API-specific authentication.

        BLS API uses POST requests with API key in the JSON body.

        Args:
            endpoint: API endpoint
            params: Request parameters
            use_cache: Whether to use cache
            method: HTTP method (BLS primarily uses POST)

        Returns:
            API response data
        """
        if params is None:
            params = {}

        # Add API key to request body for POST requests
        if self.api_key and method.upper() == "POST":
            params[self._get_key_param_name()] = self.api_key

        return super().fetch(endpoint, params, use_cache, method)

    def get_unemployment_rate(
        self,
        state_fips: str,
        county_fips: str,
        start_year: int,
        end_year: int
    ) -> Dict:
        """
        Get unemployment rate for a specific county.

        Args:
            state_fips: State FIPS code (e.g., '51' for Virginia)
            county_fips: County FIPS code (3 digits, e.g., '001')
            start_year: Starting year
            end_year: Ending year

        Returns:
            API response with unemployment data

        Example:
            >>> client = BLSAPI()
            >>> data = client.get_unemployment_rate('51', '001', 2017, 2022)
        """
        # Build LAUS series ID: LAUCCOOOOOOO03
        # Where: LAUCC + state_fips (2) + county_fips (3) + 00000 + measure (03 = unemployment rate)
        series_id = f"LAUCC{state_fips}{county_fips}0000000003"

        params = {
            'seriesid': [series_id],
            'startyear': str(start_year),
            'endyear': str(end_year)
        }

        return self.fetch('/timeseries/data/', params, method='POST')

    def get_multiple_series(
        self,
        series_ids: List[str],
        start_year: int,
        end_year: int,
        calculations: bool = False,
        annual_average: bool = False
    ) -> Dict:
        """
        Get data for multiple series.

        Args:
            series_ids: List of BLS series IDs (max 50 for v2 API)
            start_year: Starting year
            end_year: Ending year
            calculations: Whether to include calculations (changes, etc.)
            annual_average: Whether to include annual averages

        Returns:
            API response with data for all series
        """
        params = {
            'seriesid': series_ids,
            'startyear': str(start_year),
            'endyear': str(end_year),
            'calculations': calculations,
            'annualaverage': annual_average
        }

        return self.fetch('/timeseries/data/', params, method='POST')

    def build_laus_series_id(
        self,
        state_fips: str,
        county_fips: str,
        measure: str = '03'
    ) -> str:
        """
        Build LAUS series ID for a county.

        Args:
            state_fips: State FIPS code (2 digits)
            county_fips: County FIPS code (3 digits)
            measure: Measure code:
                '03' = unemployment rate
                '04' = unemployment
                '05' = employment
                '06' = labor force

        Returns:
            BLS series ID
        """
        return f"LAUCC{state_fips}{county_fips}0000000{measure}"

    def get_county_unemployment_rates(
        self,
        state_fips: str,
        county_fips_list: List[str],
        start_year: int,
        end_year: int
    ) -> Dict:
        """
        Get unemployment rates for multiple counties.

        Args:
            state_fips: State FIPS code
            county_fips_list: List of county FIPS codes
            start_year: Starting year
            end_year: Ending year

        Returns:
            API response with unemployment rates for all counties
        """
        # Build series IDs for all counties
        series_ids = [
            self.build_laus_series_id(state_fips, county_fips, '03')
            for county_fips in county_fips_list
        ]

        # BLS API v2 allows max 50 series per request
        if len(series_ids) > 50:
            self.logger.warning(
                f"Requesting {len(series_ids)} series; will need multiple requests"
            )

        return self.get_multiple_series(series_ids, start_year, end_year)

    def get_labor_force_data(
        self,
        state_fips: str,
        county_fips: str,
        start_year: int,
        end_year: int
    ) -> Dict:
        """
        Get comprehensive labor force data for a county.

        Args:
            state_fips: State FIPS code
            county_fips: County FIPS code
            start_year: Starting year
            end_year: Ending year

        Returns:
            API response with unemployment rate, unemployment, employment, and labor force
        """
        series_ids = [
            self.build_laus_series_id(state_fips, county_fips, '03'),  # Unemployment rate
            self.build_laus_series_id(state_fips, county_fips, '04'),  # Unemployment
            self.build_laus_series_id(state_fips, county_fips, '05'),  # Employment
            self.build_laus_series_id(state_fips, county_fips, '06'),  # Labor force
        ]

        return self.get_multiple_series(series_ids, start_year, end_year)

    def get_state_unemployment_rates(
        self,
        state_abbr: str,
        start_year: int,
        end_year: int
    ) -> Dict:
        """
        Get statewide unemployment rate.

        Args:
            state_abbr: State abbreviation (e.g., 'VA' for Virginia)
            start_year: Starting year
            end_year: Ending year

        Returns:
            API response with state unemployment rate
        """
        # State series ID format: LASST{state_fips}0000000003
        state_to_fips = {
            'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37',
            'TN': '47', 'KY': '21', 'DC': '11'
        }

        state_fips = state_to_fips.get(state_abbr.upper())
        if not state_fips:
            raise ValueError(f"Unknown state abbreviation: {state_abbr}")

        series_id = f"LASST{state_fips}0000000003"

        params = {
            'seriesid': [series_id],
            'startyear': str(start_year),
            'endyear': str(end_year)
        }

        return self.fetch('/timeseries/data/', params, method='POST')

    @staticmethod
    def parse_series_data(api_response: Dict) -> Dict[str, List[Dict]]:
        """
        Parse BLS API response into more usable format.

        Args:
            api_response: Raw API response

        Returns:
            Dictionary mapping series IDs to their data points
        """
        if api_response.get('status') != 'REQUEST_SUCCEEDED':
            raise ValueError(f"BLS API request failed: {api_response.get('message')}")

        parsed = {}
        for series in api_response.get('Results', {}).get('series', []):
            series_id = series.get('seriesID')
            data = series.get('data', [])
            parsed[series_id] = data

        return parsed

    @staticmethod
    def get_annual_average(series_data: List[Dict]) -> Dict[int, float]:
        """
        Calculate annual averages from monthly data.

        Args:
            series_data: List of data points from BLS API

        Returns:
            Dictionary mapping years to annual average values
        """
        annual_data = {}

        for point in series_data:
            year = int(point.get('year'))
            period = point.get('period')

            # Skip annual averages if already included
            if period == 'M13':
                annual_data[year] = float(point.get('value'))
            elif year not in annual_data and period.startswith('M'):
                # Accumulate monthly values
                if year not in annual_data:
                    annual_data[year] = []
                annual_data[year].append(float(point.get('value')))

        # Calculate averages for years without M13 period
        for year, values in annual_data.items():
            if isinstance(values, list):
                annual_data[year] = sum(values) / len(values)

        return annual_data


# BLS Series ID structure reference
BLS_LAUS_MEASURES = {
    '03': 'Unemployment rate',
    '04': 'Unemployment',
    '05': 'Employment',
    '06': 'Labor force'
}

# State FIPS codes for the study
BLS_STATE_FIPS = {
    'VA': '51',
    'MD': '24',
    'WV': '54',
    'NC': '37',
    'TN': '47',
    'KY': '21',
    'DC': '11'
}
