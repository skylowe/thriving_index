"""
USDA National Agricultural Statistics Service (NASS) API client.

Provides access to agricultural statistics including:
- Farm income and revenue
- Crop production and yields
- Livestock inventory and sales
- Agricultural land values
- Farm counts and sizes

API Documentation: https://quickstats.nass.usda.gov/api
"""

from typing import Dict, List, Optional, Union
import time

from .base_api import BaseAPIClient
from ..utils.config import APIConfig, CacheConfig
from ..utils.logging_setup import setup_logger


class USDANASSAPI(BaseAPIClient):
    """
    USDA NASS QuickStats API client.

    Provides access to comprehensive agricultural statistics at state and county level.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize USDA NASS API client.

        Args:
            api_key: USDA NASS API key (defaults to config value)
        """
        if api_key is None:
            api_key = APIConfig.NASSQS_TOKEN

        super().__init__(
            api_key=api_key,
            base_url=APIConfig.NASS_BASE_URL,
            cache_expiry=CacheConfig.NASS_CACHE_EXPIRY,
            rate_limit=None,  # No explicit rate limit documented
            service_name="USDA_NASS"
        )

        self.logger = setup_logger(f"{__name__}.USDANASSAPI")

    def _should_add_key_to_params(self) -> bool:
        """NASS API uses 'key' parameter."""
        return True

    def _get_key_param_name(self) -> str:
        """NASS API key parameter is 'key'."""
        return "key"

    def get_farm_income(
        self,
        year: int,
        state_fips: Optional[str] = None,
        county_fips: Optional[str] = None
    ) -> Dict:
        """
        Get farm income data.

        Args:
            year: Year for data collection
            state_fips: State FIPS code (e.g., '51' for Virginia)
            county_fips: County FIPS code (3 digits, e.g., '059')

        Returns:
            API response with farm income data

        Example:
            >>> client = USDANASSAPI()
            >>> data = client.get_farm_income(2022, state_fips='51')
        """
        params = {
            'source_desc': 'CENSUS',
            'sector_desc': 'ECONOMICS',
            'group_desc': 'INCOME',
            'year': str(year),
            'agg_level_desc': 'COUNTY',
            'format': 'JSON'
        }

        if state_fips:
            params['state_fips_code'] = state_fips

        if county_fips:
            params['county_code'] = county_fips

        return self.fetch('/api_GET', params)

    def get_crop_production(
        self,
        year: int,
        commodity: str,
        state_fips: Optional[str] = None
    ) -> Dict:
        """
        Get crop production data.

        Args:
            year: Year for data collection
            commodity: Commodity name (e.g., 'CORN', 'SOYBEANS', 'WHEAT')
            state_fips: State FIPS code

        Returns:
            API response with crop production data
        """
        params = {
            'source_desc': 'SURVEY',
            'commodity_desc': commodity.upper(),
            'year': str(year),
            'agg_level_desc': 'COUNTY',
            'format': 'JSON'
        }

        if state_fips:
            params['state_fips_code'] = state_fips

        return self.fetch('/api_GET', params)

    def get_livestock_inventory(
        self,
        year: int,
        commodity: str,
        state_fips: Optional[str] = None
    ) -> Dict:
        """
        Get livestock inventory data.

        Args:
            year: Year for data collection
            commodity: Commodity name (e.g., 'CATTLE', 'HOGS', 'CHICKENS')
            state_fips: State FIPS code

        Returns:
            API response with livestock data
        """
        params = {
            'source_desc': 'SURVEY',
            'commodity_desc': commodity.upper(),
            'statisticcat_desc': 'INVENTORY',
            'year': str(year),
            'agg_level_desc': 'COUNTY',
            'format': 'JSON'
        }

        if state_fips:
            params['state_fips_code'] = state_fips

        return self.fetch('/api_GET', params)

    def get_farm_counts(
        self,
        year: int,
        state_fips: Optional[str] = None
    ) -> Dict:
        """
        Get number of farms by county.

        Args:
            year: Year for data collection
            state_fips: State FIPS code

        Returns:
            API response with farm count data
        """
        params = {
            'source_desc': 'CENSUS',
            'sector_desc': 'DEMOGRAPHICS',
            'group_desc': 'FARMS & LAND & ASSETS',
            'short_desc': 'FARM OPERATIONS - NUMBER OF OPERATIONS',
            'year': str(year),
            'agg_level_desc': 'COUNTY',
            'format': 'JSON'
        }

        if state_fips:
            params['state_fips_code'] = state_fips

        return self.fetch('/api_GET', params)

    def get_agricultural_land_value(
        self,
        year: int,
        state_fips: Optional[str] = None
    ) -> Dict:
        """
        Get agricultural land values.

        Args:
            year: Year for data collection
            state_fips: State FIPS code

        Returns:
            API response with land value data
        """
        params = {
            'source_desc': 'CENSUS',
            'sector_desc': 'ECONOMICS',
            'group_desc': 'FARMS & LAND & ASSETS',
            'commodity_desc': 'AG LAND',
            'statisticcat_desc': 'ASSET VALUE',
            'year': str(year),
            'agg_level_desc': 'COUNTY',
            'format': 'JSON'
        }

        if state_fips:
            params['state_fips_code'] = state_fips

        return self.fetch('/api_GET', params)

    def get_farm_sales(
        self,
        year: int,
        state_fips: Optional[str] = None
    ) -> Dict:
        """
        Get farm product sales data.

        Args:
            year: Year for data collection
            state_fips: State FIPS code

        Returns:
            API response with sales data
        """
        params = {
            'source_desc': 'CENSUS',
            'sector_desc': 'ECONOMICS',
            'group_desc': 'SALES',
            'commodity_desc': 'COMMODITY TOTALS',
            'year': str(year),
            'agg_level_desc': 'COUNTY',
            'format': 'JSON'
        }

        if state_fips:
            params['state_fips_code'] = state_fips

        return self.fetch('/api_GET', params)

    def search_parameters(
        self,
        param_name: str,
        search_term: Optional[str] = None
    ) -> Dict:
        """
        Search available parameter values.

        Args:
            param_name: Parameter name (e.g., 'commodity_desc', 'group_desc')
            search_term: Optional search term to filter results

        Returns:
            API response with available parameter values

        Example:
            >>> client = USDANASSAPI()
            >>> # Get all available commodities
            >>> commodities = client.search_parameters('commodity_desc')
        """
        params = {
            'param': param_name,
            'format': 'JSON'
        }

        if search_term:
            params['search'] = search_term

        return self.fetch('/get_param_values', params)

    def get_all_states_farm_income(
        self,
        year: int,
        state_list: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Get farm income for multiple states.

        Args:
            year: Year for data collection
            state_list: List of state FIPS codes (defaults to study states)

        Returns:
            Dictionary mapping state codes to farm income data
        """
        if state_list is None:
            state_list = ['51', '24', '54', '37', '47', '21', '11']

        results = {}

        for state_fips in state_list:
            self.logger.info(f"Fetching farm income for state {state_fips}")
            try:
                data = self.get_farm_income(year, state_fips=state_fips)
                results[state_fips] = data
                # Rate limiting - be nice to the API
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"Failed to fetch farm income for {state_fips}: {e}")
                results[state_fips] = None

        return results

    @staticmethod
    def parse_response(api_response: Dict) -> List[Dict]:
        """
        Parse NASS API response into list of records.

        Args:
            api_response: Raw API response

        Returns:
            List of data records
        """
        if isinstance(api_response, dict) and 'data' in api_response:
            return api_response['data']
        return []


# Common parameter values for NASS API
NASS_COMMODITIES = {
    'crops': ['CORN', 'SOYBEANS', 'WHEAT', 'COTTON', 'HAY', 'TOBACCO'],
    'livestock': ['CATTLE', 'HOGS', 'CHICKENS', 'TURKEYS', 'SHEEP'],
    'specialty': ['APPLES', 'GRAPES', 'BERRIES', 'VEGETABLES']
}

NASS_DATA_ITEMS = {
    'farm_operations': 'FARM OPERATIONS - NUMBER OF OPERATIONS',
    'farm_income': 'INCOME, NET CASH FARM, OF OPERATIONS',
    'land_value': 'AG LAND, INCL BUILDINGS - ASSET VALUE, MEASURED IN $',
    'crop_acres': 'ACRES HARVESTED',
    'livestock_inventory': 'INVENTORY'
}
