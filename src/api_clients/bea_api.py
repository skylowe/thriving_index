"""
Bureau of Economic Analysis (BEA) API client.

Provides access to regional economic data including personal income,
GDP, wages, and proprietors income at county level.
"""

from typing import Dict, List, Optional, Union

from .base_api import BaseAPIClient
from ..utils.config import APIConfig, CacheConfig
from ..utils.logging_setup import setup_logger


# State FIPS to abbreviation mapping for BEA API
FIPS_TO_ABBR = {
    '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE',
    '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA',
    '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN',
    '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM',
    '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
    '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA',
    '54': 'WV', '55': 'WI', '56': 'WY'
}


class BEAAPI(BaseAPIClient):
    """
    BEA API client for Regional Economic Accounts.

    Supports querying personal income, GDP, wages, farm income,
    and other economic indicators at county level.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BEA API client.

        Args:
            api_key: BEA API key (defaults to config value)
        """
        if api_key is None:
            api_key = APIConfig.BEA_API_KEY

        super().__init__(
            api_key=api_key,
            base_url=APIConfig.BEA_BASE_URL,
            cache_expiry=CacheConfig.BEA_CACHE_EXPIRY,
            rate_limit=1000,  # 1000 requests per day
            service_name="BEA"
        )

        self.logger = setup_logger(f"{__name__}.BEAAPI")

    def _should_add_key_to_params(self) -> bool:
        """BEA API uses 'UserID' parameter."""
        return True

    def _get_key_param_name(self) -> str:
        """BEA API key parameter is 'UserID'."""
        return "UserID"

    def get_regional_income(
        self,
        year: Union[int, str],
        state: Optional[str] = None,
        line_codes: Optional[List[int]] = None
    ) -> Dict:
        """
        Get regional personal income data.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code (e.g., '51' for Virginia) or None for all states
            line_codes: Line codes to retrieve (see BEA documentation)
                Common codes:
                - 1: Personal income
                - 3: Net earnings by place of residence
                - 10: Wages and salaries
                - 35: Farm earnings
                - 40: Nonfarm earnings

        Returns:
            API response with regional income data

        Example:
            >>> client = BEAAPI()
            >>> data = client.get_regional_income(
            ...     year=2022,
            ...     state='51',
            ...     line_codes=[1, 10, 35]
            ... )
        """
        if line_codes is None:
            # Default to key income measures
            line_codes = [1, 10, 35]  # Personal income, Wages, Farm earnings

        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC1',  # County and MSA personal income summary
            'LineCode': ','.join(str(code) for code in line_codes),
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_personal_income_per_capita(
        self,
        year: Union[int, str],
        state: Optional[str] = None
    ) -> Dict:
        """
        Get per capita personal income by county.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code (2-digit) or state abbreviation, or None for all states

        Returns:
            API response with per capita income data
        """
        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC1',
            'LineCode': '2',  # Per capita personal income
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_farm_proprietors_income(
        self,
        year: Union[int, str],
        state: Optional[str] = None
    ) -> Dict:
        """
        Get farm proprietors' income by county.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code (2-digit) or state abbreviation, or None for all states

        Returns:
            API response with farm income data
        """
        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            # If it's a 2-digit FIPS code, convert to abbreviation
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                # Assume it's already an abbreviation
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC4',  # Personal income and employment by major component
            'LineCode': '50',  # Farm proprietors' income
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_nonfarm_proprietors_income(
        self,
        year: Union[int, str],
        state: Optional[str] = None
    ) -> Dict:
        """
        Get nonfarm proprietors' income by county.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code (2-digit) or state abbreviation, or None for all states

        Returns:
            API response with nonfarm income data
        """
        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC4',
            'LineCode': '60',  # Nonfarm proprietors' income
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_wages_by_industry(
        self,
        year: Union[int, str],
        state: Optional[str] = None,
        industry_codes: Optional[List[int]] = None
    ) -> Dict:
        """
        Get wages and salaries by industry.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code or None for all states
            industry_codes: Industry line codes (see BEA documentation)

        Returns:
            API response with wages by industry
        """
        if industry_codes is None:
            # Default to key industries
            industry_codes = [
                200,  # Farm employment
                310,  # Manufacturing
                400,  # Retail trade
                500,  # Information
                600,  # Finance and insurance
                700,  # Real estate
                820   # Health care and social assistance
            ]

        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC5N',  # Personal income by major component and earnings by NAICS industry
            'LineCode': ','.join(str(code) for code in industry_codes),
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_employment_by_industry(
        self,
        year: Union[int, str],
        state: Optional[str] = None,
        industry_codes: Optional[List[int]] = None
    ) -> Dict:
        """
        Get employment by industry.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code or None for all states
            industry_codes: Industry line codes

        Returns:
            API response with employment by industry
        """
        if industry_codes is None:
            # Default to key industries
            industry_codes = [
                200,  # Farm employment
                310,  # Manufacturing
                400,  # Retail trade
                820   # Health care and social assistance
            ]

        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAEMP25',  # Total full-time and part-time employment by industry
            'LineCode': ','.join(str(code) for code in industry_codes),
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_gdp_by_county(
        self,
        year: Union[int, str],
        state: Optional[str] = None
    ) -> Dict:
        """
        Get GDP by county.

        Args:
            year: Year or 'LAST5' for last 5 years
            state: State FIPS code (2-digit) or state abbreviation, or None for all states

        Returns:
            API response with GDP data
        """
        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAGDP1',  # GDP by county
            'LineCode': '1',  # All industry total
            'Year': str(year),
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_income_growth(
        self,
        start_year: int,
        end_year: int,
        state: Optional[str] = None
    ) -> Dict:
        """
        Get personal income data for calculating growth rates.

        Args:
            start_year: Starting year
            end_year: Ending year
            state: State FIPS code (2-digit) or state abbreviation, or None for all states

        Returns:
            API response with income data for both years
        """
        # Fetch data for year range
        year_range = f"{start_year},{end_year}"

        # Convert FIPS code to abbreviation if needed
        geo_param = 'COUNTY'
        if state:
            if state in FIPS_TO_ABBR:
                geo_param = FIPS_TO_ABBR[state]
            else:
                geo_param = state

        params = {
            'method': 'GetData',
            'datasetname': 'Regional',
            'TableName': 'CAINC1',
            'LineCode': '1',  # Personal income
            'Year': year_range,
            'GeoFips': geo_param,
            'ResultFormat': 'JSON'
        }

        return self.fetch('', params)

    def get_all_states_data(
        self,
        year: Union[int, str],
        method_name: str,
        **kwargs
    ) -> Dict[str, Dict]:
        """
        Get data for all states in the study.

        Args:
            year: Year or 'LAST5' for last 5 years
            method_name: Name of method to call (e.g., 'get_personal_income_per_capita')
            **kwargs: Additional keyword arguments to pass to method

        Returns:
            Dictionary mapping state abbreviations to data
        """
        from .census_api import CensusAPI

        states = CensusAPI.get_state_fips_codes()
        results = {}

        method = getattr(self, method_name)

        for state_abbr, state_fips in states.items():
            self.logger.info(f"Fetching {method_name} for {state_abbr}")
            results[state_abbr] = method(year=year, state=state_fips, **kwargs)

        return results


# BEA Table and Line Code reference
BEA_TABLE_CODES = {
    # Personal Income tables
    'CAINC1': 'County and MSA personal income summary',
    'CAINC4': 'Personal income and employment by major component',
    'CAINC5N': 'Personal income by major component and earnings by NAICS industry',

    # Employment tables
    'CAEMP25N': 'Total full-time and part-time employment by NAICS industry',

    # GDP tables
    'CAGDP1': 'GDP by county',
    'CAGDP2': 'GDP by county and industry',
}

BEA_INCOME_LINE_CODES = {
    1: 'Personal income',
    2: 'Per capita personal income',
    3: 'Net earnings by place of residence',
    10: 'Wages and salaries',
    35: 'Farm earnings',
    40: 'Nonfarm earnings',
    50: 'Farm proprietors income',
    60: 'Nonfarm proprietors income',
}

BEA_INDUSTRY_LINE_CODES = {
    10: 'Total employment',
    200: 'Farm employment',
    300: 'Forestry, fishing, and related activities',
    310: 'Manufacturing',
    400: 'Retail trade',
    500: 'Information',
    600: 'Finance and insurance',
    700: 'Real estate and rental and leasing',
    800: 'Professional and business services',
    820: 'Health care and social assistance',
    900: 'Arts, entertainment, and recreation',
    910: 'Accommodation and food services',
}
