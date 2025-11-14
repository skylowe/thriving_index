"""
Test USDA NASS and FBI UCR API Implementations

Quick verification that the new API clients work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.usda_nass_api import USDANASSAPI
from src.api_clients.fbi_ucr_api import FBIUCRAPI
from src.utils.logging_setup import setup_logger


def test_usda_nass_api(logger):
    """Test USDA NASS API client."""
    logger.info("\n" + "=" * 70)
    logger.info("Testing USDA NASS API")
    logger.info("=" * 70)

    usda = USDANASSAPI()

    # Test 1: Get farm income for Virginia counties
    logger.info("\n1. Testing farm income data for Virginia (2022)...")
    try:
        response = usda.get_farm_income(year=2022, state_fips='51')

        if response and 'data' in response:
            data_count = len(response['data'])
            logger.info(f"   ✓ Retrieved {data_count} records")

            if data_count > 0:
                # Show first record
                first = response['data'][0]
                logger.info(f"   Sample: {first.get('county_name', 'N/A')} - ${first.get('Value', 'N/A')}")
            else:
                logger.warning("   ⚠ No data records found")
        else:
            logger.warning(f"   ⚠ Unexpected response format: {type(response)}")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")

    # Test 2: Get crop production
    logger.info("\n2. Testing crop production data...")
    try:
        response = usda.get_crop_production(year=2022, commodity='CORN', state_fips='51')

        if response and 'data' in response:
            logger.info(f"   ✓ Retrieved {len(response['data'])} records")
        else:
            logger.warning(f"   ⚠ No data or unexpected format")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")

    logger.info("\n✓ USDA NASS API testing complete")


def test_fbi_ucr_api(logger):
    """Test FBI UCR API client."""
    logger.info("\n" + "=" * 70)
    logger.info("Testing FBI UCR API")
    logger.info("=" * 70)

    fbi = FBIUCRAPI()

    # Test 1: Get state crime summary
    logger.info("\n1. Testing state crime summary for Virginia (2021)...")
    try:
        response = fbi.get_state_crime_summary(state_abbr='VA', year=2021)

        if response and 'data' in response:
            data_count = len(response['data'])
            logger.info(f"   ✓ Retrieved {data_count} records")

            if data_count > 0:
                first = response['data'][0]
                logger.info(f"   Sample keys: {list(first.keys())[:5]}")
        else:
            logger.warning(f"   ⚠ Unexpected response format")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")

    # Test 2: Get violent crime rate
    logger.info("\n2. Testing violent crime rate...")
    try:
        response = fbi.get_violent_crime_rate(state_abbr='VA', year=2021)

        if response:
            logger.info(f"   ✓ Retrieved response")
        else:
            logger.warning(f"   ⚠ No response")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")

    # Test 3: Get agencies by state
    logger.info("\n3. Testing get agencies by state...")
    try:
        response = fbi.get_agencies_by_state(state_abbr='VA')

        if response and 'data' in response:
            logger.info(f"   ✓ Retrieved {len(response['data'])} agencies")
        else:
            logger.warning(f"   ⚠ No data")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")

    logger.info("\n✓ FBI UCR API testing complete")


def main():
    """Main execution."""
    logger = setup_logger('test_usda_fbi_apis')

    logger.info("=" * 70)
    logger.info("TESTING NEW API CLIENTS: USDA NASS & FBI UCR")
    logger.info("=" * 70)

    # Test USDA NASS API
    test_usda_nass_api(logger)

    # Test FBI UCR API
    test_fbi_ucr_api(logger)

    logger.info("\n" + "=" * 70)
    logger.info("ALL API TESTS COMPLETE")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
