"""
Configuration module for Virginia Thriving Index project.
Reads API keys from .Renviron file and provides configuration constants.
"""

import os
from pathlib import Path


def load_env_file(env_path=None):
    """
    Load environment variables from .Renviron file.

    Args:
        env_path: Path to .Renviron file. If None, looks in project root.

    Returns:
        dict: Dictionary of environment variables
    """
    if env_path is None:
        # Find project root (where .Renviron is located)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        env_path = project_root / '.Renviron'
    else:
        env_path = Path(env_path)

    if not env_path.exists():
        raise FileNotFoundError(f".Renviron file not found at {env_path}")

    env_vars = {}
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


# Load environment variables at module import
ENV_VARS = load_env_file()

# API Keys
CENSUS_API_KEY = ENV_VARS.get('CENSUS_KEY')
BEA_API_KEY = ENV_VARS.get('BEA_API_KEY')
BLS_API_KEY = ENV_VARS.get('BLS_API_KEY')
NASSQS_TOKEN = ENV_VARS.get('NASSQS_TOKEN')
FBI_UCR_KEY = ENV_VARS.get('FBI_UCR_KEY')

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
