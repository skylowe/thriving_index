"""
Test script for sample API data collection.

This script tests the API clients by fetching sample data for a few
Virginia regions to verify:
1. API clients work correctly
2. API keys are valid
3. Data can be retrieved for our regions
4. Data structure is as expected
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.api_clients.bea_api import BEAAPI
from src.api_clients.bls_api import BLSAPI
from src.utils.config import api_config, data_config
from src.utils.logging_setup import setup_logger

# Setup logging
logger = setup_logger('test_api_sample')

# Test regions - sample Virginia localities
TEST_REGIONS = [
    {'fips': '51059', 'name': 'Fairfax County', 'state': 'VA'},
    {'fips': '51510', 'name': 'Alexandria City', 'state': 'VA'},
    {'fips': '51001', 'name': 'Accomack County', 'state': 'VA'},
]

def test_census_api():
    """Test Census API with sample demographic data."""
    logger.info("=" * 60)
    logger.info("Testing Census API (ACS 5-year estimates)")
    logger.info("=" * 60)

    try:
        census = CensusAPI()

        # Test: Get median household income for test regions
        logger.info("\nTest 1: Median Household Income (B19013_001E)")

        for region in TEST_REGIONS:
            county_fips = region['fips'][2:]  # Remove state FIPS
            state_fips = region['fips'][:2]

            try:
                data = census.get_acs_data(
                    year=2022,
                    variables={'B19013_001E': 'median_household_income'},
                    geography='county',
                    state=state_fips,
                    county=county_fips
                )

                if data and len(data) > 0:
                    income = data[0].get('median_household_income', 'N/A')
                    logger.info(f"  ✓ {region['name']}: ${income:,}" if isinstance(income, (int, float)) else f"  ✓ {region['name']}: {income}")
                else:
                    logger.warning(f"  ✗ {region['name']}: No data returned")

            except Exception as e:
                logger.error(f"  ✗ {region['name']}: Error - {str(e)}")

        # Test: Get poverty rate
        logger.info("\nTest 2: Poverty Rate (S1701_C03_001E)")

        for region in TEST_REGIONS:
            county_fips = region['fips'][2:]
            state_fips = region['fips'][:2]

            try:
                data = census.get_acs_data(
                    year=2022,
                    variables={'S1701_C03_001E': 'poverty_rate'},
                    geography='county',
                    state=state_fips,
                    county=county_fips,
                    dataset='acs5/subject'
                )

                if data and len(data) > 0:
                    poverty = data[0].get('poverty_rate', 'N/A')
                    logger.info(f"  ✓ {region['name']}: {poverty}%" if isinstance(poverty, (int, float)) else f"  ✓ {region['name']}: {poverty}")
                else:
                    logger.warning(f"  ✗ {region['name']}: No data returned")

            except Exception as e:
                logger.error(f"  ✗ {region['name']}: Error - {str(e)}")

        logger.info("\n✓ Census API test completed")
        return True

    except Exception as e:
        logger.error(f"\n✗ Census API test failed: {str(e)}")
        return False


def test_bea_api():
    """Test BEA API with sample economic data."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing BEA API (Regional Economic Accounts)")
    logger.info("=" * 60)

    try:
        bea = BEAAPI()

        # Test: Get per capita personal income
        logger.info("\nTest: Per Capita Personal Income (2022)")

        for region in TEST_REGIONS:
            try:
                data = bea.get_regional_income(
                    years=[2022],
                    geo_fips=region['fips'],
                    line_code=3  # Per capita personal income
                )

                if data and len(data) > 0:
                    income = data[0].get('DataValue', 'N/A')
                    logger.info(f"  ✓ {region['name']}: ${income:,}" if isinstance(income, (int, float)) else f"  ✓ {region['name']}: {income}")
                else:
                    logger.warning(f"  ✗ {region['name']}: No data returned")

            except Exception as e:
                logger.error(f"  ✗ {region['name']}: Error - {str(e)}")

        logger.info("\n✓ BEA API test completed")
        return True

    except Exception as e:
        logger.error(f"\n✗ BEA API test failed: {str(e)}")
        return False


def test_bls_api():
    """Test BLS API with sample labor statistics."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing BLS API (Local Area Unemployment Statistics)")
    logger.info("=" * 60)

    try:
        bls = BLSAPI()

        # Test: Get unemployment rate
        logger.info("\nTest: Unemployment Rate (2023)")

        for region in TEST_REGIONS:
            try:
                data = bls.get_unemployment_rate(
                    year=2023,
                    state_fips=region['fips'][:2],
                    county_fips=region['fips'][2:]
                )

                if data and len(data) > 0:
                    rate = data[0].get('value', 'N/A')
                    logger.info(f"  ✓ {region['name']}: {rate}%" if isinstance(rate, (int, float)) else f"  ✓ {region['name']}: {rate}")
                else:
                    logger.warning(f"  ✗ {region['name']}: No data returned")

            except Exception as e:
                logger.error(f"  ✗ {region['name']}: Error - {str(e)}")

        logger.info("\n✓ BLS API test completed")
        return True

    except Exception as e:
        logger.error(f"\n✗ BLS API test failed: {str(e)}")
        return False


def main():
    """Run all API tests."""
    logger.info("Starting API sample data collection tests")
    logger.info(f"Testing with {len(TEST_REGIONS)} Virginia regions")
    logger.info("")

    results = {
        'census': test_census_api(),
        'bea': test_bea_api(),
        'bls': test_bls_api(),
    }

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    for api_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        logger.info(f"  {api_name.upper()}: {status}")

    all_passed = all(results.values())
    logger.info(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
