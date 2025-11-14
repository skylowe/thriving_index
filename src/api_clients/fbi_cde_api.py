"""
FBI Crime Data Explorer API Client

Provides access to the FBI Crime Data Explorer API for fetching summarized
crime data by law enforcement agency (ORI code).

API Documentation: https://api.usa.gov/crime/fbi/cde/
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

from src.api_clients.base_api import BaseAPIClient

logger = logging.getLogger(__name__)


class FBICrimeDataExplorerAPI(BaseAPIClient):
    """
    Client for the FBI Crime Data Explorer API.

    Fetches summarized crime data for law enforcement agencies using ORI codes.
    """

    BASE_URL = "https://api.usa.gov/crime/fbi/cde"

    def __init__(self, api_key: str, cache_dir: Optional[str] = None, rate_limit: int = 1000):
        """
        Initialize the FBI Crime Data Explorer API client.

        Args:
            api_key: FBI API key
            cache_dir: Directory for caching API responses
            rate_limit: Maximum API requests per day
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / 'cache' / 'fbi_cde'

        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            cache_dir=cache_dir,
            rate_limit=rate_limit,
            service_name='FBI_CDE'
        )

        self.api_key_param = api_key  # Store for URL params

    def _should_add_key_to_params(self) -> bool:
        """
        FBI API uses API_KEY in query parameters.

        Returns:
            True (API key goes in query params)
        """
        return True

    def _get_key_param_name(self) -> str:
        """
        Get the parameter name for the FBI API key.

        Returns:
            'API_KEY'
        """
        return 'API_KEY'

    def get_summarized_data(
        self,
        ori: str,
        offense: str,
        from_date: str,
        to_date: str
    ) -> Optional[Dict]:
        """
        Get summarized crime data for a specific agency and offense type.

        Args:
            ori: 7-character ORI code (e.g., 'VA0010100')
            offense: Offense type - 'V' for violent crime, 'P' for property crime
            from_date: Start date in format 'MM-YYYY' (e.g., '01-2024')
            to_date: End date in format 'MM-YYYY' (e.g., '12-2024')

        Returns:
            Dictionary with crime data or None if request fails
        """
        # Validate offense type
        if offense not in ['V', 'P']:
            raise ValueError(f"Invalid offense type: {offense}. Must be 'V' or 'P'")

        # Build endpoint
        endpoint = f"/summarized/agency/{ori}/{offense}"

        # Build query parameters
        params = {
            'from': from_date,
            'to': to_date,
            'API_KEY': self.api_key_param
        }

        # Make request
        try:
            data = self.fetch(
                endpoint=endpoint,
                params=params
            )

            if data:
                logger.debug(f"Successfully fetched {offense} crime data for ORI {ori}")
                return data
            else:
                logger.warning(f"No data returned for ORI {ori}, offense {offense}")
                return None

        except Exception as e:
            logger.error(f"Error fetching crime data for ORI {ori}, offense {offense}: {e}")
            return None

    def get_violent_crime(
        self,
        ori: str,
        from_date: str,
        to_date: str
    ) -> Optional[Dict]:
        """
        Get violent crime data for a specific agency.

        Args:
            ori: 7-character ORI code
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'

        Returns:
            Dictionary with violent crime data or None if request fails
        """
        return self.get_summarized_data(ori, 'V', from_date, to_date)

    def get_property_crime(
        self,
        ori: str,
        from_date: str,
        to_date: str
    ) -> Optional[Dict]:
        """
        Get property crime data for a specific agency.

        Args:
            ori: 7-character ORI code
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'

        Returns:
            Dictionary with property crime data or None if request fails
        """
        return self.get_summarized_data(ori, 'P', from_date, to_date)

    def get_all_crime_data(
        self,
        ori: str,
        from_date: str,
        to_date: str
    ) -> Dict[str, Optional[Dict]]:
        """
        Get both violent and property crime data for a specific agency.

        Args:
            ori: 7-character ORI code
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'

        Returns:
            Dictionary with 'violent' and 'property' keys containing crime data
        """
        return {
            'violent': self.get_violent_crime(ori, from_date, to_date),
            'property': self.get_property_crime(ori, from_date, to_date)
        }

    def fetch_crimes_for_oris(
        self,
        ori_list: List[str],
        from_date: str,
        to_date: str,
        delay: float = 0.1
    ) -> Dict[str, Dict]:
        """
        Fetch crime data for multiple ORI codes.

        Args:
            ori_list: List of 7-character ORI codes
            from_date: Start date in format 'MM-YYYY'
            to_date: End date in format 'MM-YYYY'
            delay: Delay between requests in seconds (to respect rate limits)

        Returns:
            Dictionary mapping ORI codes to crime data
        """
        results = {}
        total = len(ori_list)

        for i, ori in enumerate(ori_list, 1):
            logger.info(f"Fetching crime data for {ori} ({i}/{total})")

            try:
                crime_data = self.get_all_crime_data(ori, from_date, to_date)
                results[ori] = crime_data

                # Add delay to respect rate limits (unless data came from cache)
                if delay > 0:
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Error fetching data for ORI {ori}: {e}")
                results[ori] = {'violent': None, 'property': None}

            # Log progress every 100 agencies
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{total} agencies ({i/total*100:.1f}%)")

        return results


if __name__ == '__main__':
    # Test the FBI CDE API client
    import os

    logging.basicConfig(level=logging.INFO)

    api_key = os.getenv('FBI_UCR_KEY')
    if not api_key:
        print("Error: FBI_UCR_KEY not found in environment")
        exit(1)

    client = FBICrimeDataExplorerAPI(api_key=api_key)

    # Test with a Virginia agency
    test_ori = 'VA0010100'  # Example ORI
    print(f"\nTesting API with ORI: {test_ori}")

    violent = client.get_violent_crime(test_ori, '01-2024', '12-2024')
    print(f"\nViolent crime data: {violent}")

    property_crime = client.get_property_crime(test_ori, '01-2024', '12-2024')
    print(f"\nProperty crime data: {property_crime}")
