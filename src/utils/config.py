"""
Configuration management for Virginia Thriving Index project.

Loads API keys and configuration settings from environment variables.
"""

import os
from pathlib import Path
from typing import Optional


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


class APIConfig:
    """API configuration and credentials."""

    # Census Bureau
    CENSUS_API_KEY: Optional[str] = os.getenv('CENSUS_KEY')
    CENSUS_BASE_URL: str = "https://api.census.gov/data"

    # Bureau of Economic Analysis
    BEA_API_KEY: Optional[str] = os.getenv('BEA_API_KEY')
    BEA_BASE_URL: str = "https://apps.bea.gov/api/data"

    # Bureau of Labor Statistics
    BLS_API_KEY: Optional[str] = os.getenv('BLS_API_KEY')
    BLS_BASE_URL: str = "https://api.bls.gov/publicAPI/v2"

    # Federal Reserve Economic Data (bonus source)
    FRED_API_KEY: Optional[str] = os.getenv('FRED_API_KEY')
    FRED_BASE_URL: str = "https://api.stlouisfed.org/fred"

    # USDA National Agricultural Statistics Service
    NASSQS_API_KEY: Optional[str] = os.getenv('NASSQS_TOKEN')
    NASSQS_BASE_URL: str = "https://quickstats.nass.usda.gov/api"

    # FBI Uniform Crime Reporting
    FBI_UCR_API_KEY: Optional[str] = os.getenv('FBI_UCR_KEY')
    FBI_UCR_BASE_URL: str = "https://api.usa.gov/crime/fbi/sapi/api"

    # FCC Broadband (pending)
    FCC_API_KEY: Optional[str] = os.getenv('FCC_API_KEY')
    FCC_BASE_URL: str = "https://broadbandmap.fcc.gov/api"
    FCC_API_ENABLED: bool = FCC_API_KEY is not None

    # CMS NPPES NPI Registry (no key required)
    CMS_NPPES_BASE_URL: str = "https://npiregistry.cms.hhs.gov/api"
    CMS_NPPES_DOWNLOAD_URL: str = "https://download.cms.gov/nppes/NPI_Files.html"

    # IRS Exempt Organizations (no key required)
    IRS_EO_BMF_BASE_URL: str = "https://www.irs.gov/pub/irs-soi"

    @classmethod
    def validate_required_keys(cls) -> dict[str, bool]:
        """
        Validate that required API keys are present.

        Returns:
            dict: Mapping of API name to availability status
        """
        return {
            'Census': cls.CENSUS_API_KEY is not None,
            'BEA': cls.BEA_API_KEY is not None,
            'BLS': cls.BLS_API_KEY is not None,
            'FRED': cls.FRED_API_KEY is not None,
            'USDA NASS': cls.NASSQS_API_KEY is not None,
            'FBI UCR': cls.FBI_UCR_API_KEY is not None,
            'FCC': cls.FCC_API_KEY is not None,
        }

    @classmethod
    def get_missing_keys(cls) -> list[str]:
        """
        Get list of missing API keys.

        Returns:
            list: Names of APIs with missing keys
        """
        validation = cls.validate_required_keys()
        return [api for api, available in validation.items() if not available]


class RateLimitConfig:
    """Rate limiting configuration for API clients."""

    # Default rate limits (requests per day unless specified)
    CENSUS_RATE_LIMIT = None  # No explicit limit documented
    BEA_RATE_LIMIT = 1000  # 1000 calls per day
    BLS_RATE_LIMIT = 500  # 500 queries per day (registered)
    FRED_RATE_LIMIT = None  # No explicit limit documented
    NASSQS_RATE_LIMIT = None  # No explicit limit documented
    FBI_UCR_RATE_LIMIT = None  # No explicit limit documented

    # Default retry settings
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 2s, 4s, 8s
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]  # Retry on these HTTP status codes


class CacheConfig:
    """Cache configuration."""

    # Cache expiration times (in seconds)
    CENSUS_CACHE_EXPIRY = 30 * 24 * 3600  # 30 days
    BEA_CACHE_EXPIRY = 30 * 24 * 3600  # 30 days
    BLS_CACHE_EXPIRY = 30 * 24 * 3600  # 30 days
    FRED_CACHE_EXPIRY = 30 * 24 * 3600  # 30 days
    NASSQS_CACHE_EXPIRY = 30 * 24 * 3600  # 30 days
    FBI_UCR_CACHE_EXPIRY = 30 * 24 * 3600  # 30 days

    # Bulk download refresh intervals
    CMS_NPPES_REFRESH_DAYS = 30  # Refresh monthly (updated weekly, but monthly is sufficient)
    IRS_EO_BMF_REFRESH_DAYS = 90  # Refresh quarterly (updated monthly)


class DataConfig:
    """Data processing configuration."""

    # States to include in analysis
    STATES = ['VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC']

    # Reference year for data
    REFERENCE_YEAR = 2022

    # ACS data vintage
    ACS_VINTAGE = 2022  # Most recent 5-year estimates

    # Number of peer regions to find for matching
    N_PEER_REGIONS = 10

    # Matching variables for Mahalanobis distance
    MATCHING_VARIABLES = [
        'total_population',
        'pct_micropolitan',
        'pct_farm_income',
        'pct_manufacturing',
        'distance_small_msa',
        'distance_large_msa'
    ]

    # MSA population thresholds for distance calculations
    SMALL_MSA_THRESHOLD = 250000
    LARGE_MSA_THRESHOLD = 250000  # Same as Nebraska study

    # Primary care physician taxonomy codes
    PRIMARY_CARE_TAXONOMY_CODES = [
        '207Q00000X',  # Family Medicine
        '208D00000X',  # General Practice
        '207R00000X',  # Internal Medicine
        '2080P0216X',  # Pediatrics
    ]

    # IRS nonprofit organization types to include
    IRS_NONPROFIT_TYPES = ['3']  # 501(c)(3) organizations only


class LoggingConfig:
    """Logging configuration."""

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# Configuration instances for easy import
api_config = APIConfig()
rate_limit_config = RateLimitConfig()
cache_config = CacheConfig()
data_config = DataConfig()
logging_config = LoggingConfig()


def print_config_status():
    """Print configuration status for debugging."""
    print("=" * 60)
    print("Virginia Thriving Index - Configuration Status")
    print("=" * 60)
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")

    print("\nAPI Keys Status:")
    validation = APIConfig.validate_required_keys()
    for api, available in validation.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {api}: {status}")

    missing = APIConfig.get_missing_keys()
    if missing:
        print(f"\n⚠️  Missing API keys: {', '.join(missing)}")
    else:
        print("\n✅ All API keys configured!")

    print("\nData Configuration:")
    print(f"  States: {', '.join(data_config.STATES)}")
    print(f"  Reference Year: {data_config.REFERENCE_YEAR}")
    print(f"  ACS Vintage: {data_config.ACS_VINTAGE}")
    print(f"  Peer Regions: {data_config.N_PEER_REGIONS}")

    print("=" * 60)


if __name__ == "__main__":
    print_config_status()
