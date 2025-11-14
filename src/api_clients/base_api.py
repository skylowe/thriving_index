"""
Base API client with caching and rate limiting functionality.

All specific API clients should inherit from BaseAPIClient.
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.config import CACHE_DIR, RateLimitConfig
from ..utils.logging_setup import setup_logger


class BaseAPIClient(ABC):
    """
    Base class for all API clients with built-in caching and rate limiting.

    Attributes:
        api_key: API authentication key
        base_url: Base URL for API endpoints
        cache_dir: Directory for caching responses
        cache_expiry: Cache expiration time in seconds
        rate_limit: Maximum requests per day (None for unlimited)
        logger: Logger instance
    """

    def __init__(
        self,
        api_key: Optional[str],
        base_url: str,
        cache_dir: Optional[Path] = None,
        cache_expiry: int = 30 * 24 * 3600,  # 30 days default
        rate_limit: Optional[int] = None,
        service_name: str = "API"
    ):
        """
        Initialize base API client.

        Args:
            api_key: API authentication key (can be None for public APIs)
            base_url: Base URL for API endpoints
            cache_dir: Directory for caching (defaults to CACHE_DIR/service_name)
            cache_expiry: Cache expiration in seconds
            rate_limit: Maximum requests per day (None for unlimited)
            service_name: Name of the service for logging and caching
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.cache_expiry = cache_expiry
        self.rate_limit = rate_limit
        self.service_name = service_name

        # Set up cache directory
        if cache_dir is None:
            cache_dir = CACHE_DIR / service_name.lower().replace(' ', '_')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = setup_logger(f"{__name__}.{service_name}")

        # Rate limiting state file
        self.rate_limit_file = self.cache_dir / "_rate_limit_state.json"

        # Set up requests session with retry logic
        self.session = self._create_session()

        self.logger.info(f"Initialized {service_name} API client")

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry logic.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=RateLimitConfig.MAX_RETRIES,
            backoff_factor=RateLimitConfig.RETRY_BACKOFF_FACTOR,
            status_forcelist=RateLimitConfig.RETRY_STATUS_CODES,
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _generate_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """
        Generate cache key from endpoint and parameters.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Cache key (hex digest)
        """
        # Normalize params
        if params is None:
            params = {}

        # Sort params for consistent hashing
        param_str = urlencode(sorted(params.items()))
        cache_str = f"{endpoint}?{param_str}"

        # Generate hash
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get cache file path for a given cache key.

        Args:
            cache_key: Cache key

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"

    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Load data from cache if available and not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached data if available and valid, None otherwise
        """
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)

            # Check expiration
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            expiry_time = cached_time + timedelta(seconds=self.cache_expiry)

            if datetime.now() > expiry_time:
                self.logger.debug(f"Cache expired for key {cache_key}")
                return None

            self.logger.debug(f"Cache hit for key {cache_key}")
            return cached_data['data']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.warning(f"Error loading cache for key {cache_key}: {e}")
            return None

    def _save_to_cache(self, cache_key: str, data: Any) -> None:
        """
        Save data to cache.

        Args:
            cache_key: Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(cache_key)

        try:
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }

            with open(cache_path, 'w') as f:
                json.dump(cached_data, f, indent=2)

            self.logger.debug(f"Saved to cache with key {cache_key}")

        except Exception as e:
            self.logger.warning(f"Error saving to cache for key {cache_key}: {e}")

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            True if within limits, False otherwise
        """
        if self.rate_limit is None:
            return True

        # Load rate limit state
        if not self.rate_limit_file.exists():
            state = {'requests': [], 'daily_count': 0, 'date': datetime.now().date().isoformat()}
        else:
            try:
                with open(self.rate_limit_file, 'r') as f:
                    state = json.load(f)
            except (json.JSONDecodeError, KeyError):
                state = {'requests': [], 'daily_count': 0, 'date': datetime.now().date().isoformat()}

        # Reset if new day
        current_date = datetime.now().date().isoformat()
        if state.get('date') != current_date:
            state = {'requests': [], 'daily_count': 0, 'date': current_date}

        # Check limit
        if state['daily_count'] >= self.rate_limit:
            self.logger.warning(f"Rate limit exceeded: {state['daily_count']}/{self.rate_limit} requests today")
            return False

        return True

    def _record_request(self) -> None:
        """Record an API request for rate limiting."""
        if self.rate_limit is None:
            return

        # Load or initialize state
        if not self.rate_limit_file.exists():
            state = {'requests': [], 'daily_count': 0, 'date': datetime.now().date().isoformat()}
        else:
            try:
                with open(self.rate_limit_file, 'r') as f:
                    state = json.load(f)
            except (json.JSONDecodeError, KeyError):
                state = {'requests': [], 'daily_count': 0, 'date': datetime.now().date().isoformat()}

        # Reset if new day
        current_date = datetime.now().date().isoformat()
        if state.get('date') != current_date:
            state = {'requests': [], 'daily_count': 0, 'date': current_date}

        # Record request
        state['requests'].append(datetime.now().isoformat())
        state['daily_count'] = state.get('daily_count', 0) + 1

        # Save state
        try:
            with open(self.rate_limit_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Error saving rate limit state: {e}")

    def fetch(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True,
        method: str = "GET"
    ) -> Dict:
        """
        Fetch data from API with caching and rate limiting.

        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            use_cache: Whether to use cached data if available
            method: HTTP method (GET or POST)

        Returns:
            API response data

        Raises:
            requests.exceptions.RequestException: If request fails
            ValueError: If rate limit exceeded
        """
        if params is None:
            params = {}

        # Add API key to params if required
        if self.api_key and self._should_add_key_to_params():
            params[self._get_key_param_name()] = self.api_key

        # Generate cache key
        cache_key = self._generate_cache_key(endpoint, params)

        # Try cache first
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # Check rate limit
        if not self._check_rate_limit():
            raise ValueError(f"Rate limit exceeded for {self.service_name} API")

        # Build URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Make request
        self.logger.info(f"Fetching from {self.service_name} API: {endpoint}")

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Record request for rate limiting
            self._record_request()

            # Parse response
            data = self._parse_response(response)

            # Save to cache
            if use_cache:
                self._save_to_cache(cache_key, data)

            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching from {self.service_name} API: {e}")
            raise

    @abstractmethod
    def _should_add_key_to_params(self) -> bool:
        """
        Determine if API key should be added to query parameters.

        Some APIs use headers for authentication instead of query params.

        Returns:
            True if key should be in params, False if in headers
        """
        pass

    @abstractmethod
    def _get_key_param_name(self) -> str:
        """
        Get the parameter name for API key.

        Returns:
            Parameter name (e.g., 'key', 'api_key', 'token')
        """
        pass

    def _parse_response(self, response: requests.Response) -> Dict:
        """
        Parse API response.

        Default implementation returns JSON. Override for custom parsing.

        Args:
            response: HTTP response

        Returns:
            Parsed response data
        """
        return response.json()

    def clear_cache(self) -> None:
        """Clear all cached data for this API client."""
        cache_files = list(self.cache_dir.glob("*.json"))

        for cache_file in cache_files:
            if cache_file.name != "_rate_limit_state.json":
                try:
                    cache_file.unlink()
                    self.logger.debug(f"Deleted cache file: {cache_file.name}")
                except Exception as e:
                    self.logger.warning(f"Error deleting cache file {cache_file.name}: {e}")

        self.logger.info(f"Cleared cache for {self.service_name} API")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = [f for f in self.cache_dir.glob("*.json") if f.name != "_rate_limit_state.json"]
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'service': self.service_name,
            'cache_dir': str(self.cache_dir),
            'num_cached_items': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
