"""
Configuration module for Virginia Thriving Index project.
Reads API keys from .Renviron file if available, otherwise falls back to
environment variables. This allows the code to work in multiple environments.
"""

import os
from pathlib import Path


def load_env_file(env_path=None):
    """
    Load environment variables from .Renviron file if it exists.

    Args:
        env_path: Path to .Renviron file. If None, looks in project root.

    Returns:
        dict: Dictionary of environment variables loaded from file (empty if file doesn't exist)
    """
    if env_path is None:
        # Find project root (where .Renviron is located)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        env_path = project_root / '.Renviron'
    else:
        env_path = Path(env_path)

    env_vars = {}

    if not env_path.exists():
        # File doesn't exist - will fall back to os.environ
        return env_vars

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
                # Also set in os.environ for compatibility
                os.environ[key.strip()] = value.strip()

    return env_vars


def get_api_key(key_name, env_file_vars):
    """
    Get API key from .Renviron file or environment variables.

    Args:
        key_name: Name of the environment variable
        env_file_vars: Dictionary of variables loaded from .Renviron

    Returns:
        str or None: API key value
    """
    # First check .Renviron file variables
    if key_name in env_file_vars:
        return env_file_vars[key_name]
    # Fall back to os.environ
    return os.environ.get(key_name)


# Load environment variables from .Renviron if available
ENV_VARS = load_env_file()

# API Keys - check both .Renviron and environment variables
CENSUS_API_KEY = get_api_key('CENSUS_KEY', ENV_VARS)
BEA_API_KEY = get_api_key('BEA_API_KEY', ENV_VARS)
BLS_API_KEY = get_api_key('BLS_API_KEY', ENV_VARS)
NASSQS_TOKEN = get_api_key('NASSQS_TOKEN', ENV_VARS)
FBI_UCR_KEY = get_api_key('FBI_UCR_KEY', ENV_VARS)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
RESULTS_DIR = DATA_DIR / 'results'

# State FIPS codes for our 10 states
STATE_FIPS = {
    'VA': '51',  # Virginia
    'PA': '42',  # Pennsylvania
    'MD': '24',  # Maryland
    'DE': '10',  # Delaware
    'WV': '54',  # West Virginia
    'KY': '21',  # Kentucky
    'TN': '47',  # Tennessee
    'NC': '37',  # North Carolina
    'SC': '45',  # South Carolina
    'GA': '13',  # Georgia
}

# State names
STATE_NAMES = {
    '51': 'Virginia',
    '42': 'Pennsylvania',
    '24': 'Maryland',
    '10': 'Delaware',
    '54': 'West Virginia',
    '21': 'Kentucky',
    '47': 'Tennessee',
    '37': 'North Carolina',
    '45': 'South Carolina',
    '13': 'Georgia',
}

# API endpoints
BEA_API_URL = 'https://apps.bea.gov/api/data/'
BLS_API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
CENSUS_API_BASE = 'https://api.census.gov/data'

# Data collection settings
REQUEST_DELAY = 0.5  # Seconds to wait between API requests
MAX_RETRIES = 3  # Maximum number of retries for failed requests
TIMEOUT = 30  # Request timeout in seconds


def validate_api_keys():
    """
    Validate that all required API keys are present.

    Returns:
        dict: Dictionary with validation results
    """
    required_keys = {
        'CENSUS_API_KEY': CENSUS_API_KEY,
        'BEA_API_KEY': BEA_API_KEY,
        'BLS_API_KEY': BLS_API_KEY,
    }

    results = {}
    for key_name, key_value in required_keys.items():
        if key_value:
            results[key_name] = 'OK'
        else:
            results[key_name] = 'MISSING'

    return results


if __name__ == '__main__':
    # Test the configuration
    print("API Key Validation:")
    print("-" * 40)
    validation = validate_api_keys()
    for key, status in validation.items():
        print(f"{key}: {status}")

    print("\nState FIPS Codes:")
    print("-" * 40)
    for abbr, fips in STATE_FIPS.items():
        print(f"{abbr} ({STATE_NAMES[fips]}): {fips}")

    print("\nProject Paths:")
    print("-" * 40)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Raw Data: {RAW_DATA_DIR}")
    print(f"Processed Data: {PROCESSED_DATA_DIR}")
