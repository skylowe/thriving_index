"""
Test script for Census API client.

Tests basic functionality and data collection for Virginia.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.utils.logging_setup import setup_logger


def test_census_api():
    """Test Census API client with sample requests."""
    logger = setup_logger('test_census_api')

    logger.info("=" * 70)
    logger.info("Testing Census API Client")
    logger.info("=" * 70)

    # Initialize client
    try:
        client = CensusAPI()
        logger.info("✓ Census API client initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Census API client: {e}")
        return

    # Test 1: Get Virginia population data
    logger.info("\nTest 1: Get Virginia population (2022 ACS 5-year)")
    try:
        va_pop = client.get_population(year=2022, state='51')
        logger.info(f"✓ Retrieved data for {len(va_pop)} Virginia localities")

        # Show first 5 records
        logger.info("  Sample records:")
        for record in va_pop[:5]:
            name = record.get('NAME', 'Unknown')
            pop = record.get('B01001_001E', 'N/A')
            logger.info(f"    {name}: {pop}")

    except Exception as e:
        logger.error(f"✗ Failed to get Virginia population: {e}")

    # Test 2: Get median household income
    logger.info("\nTest 2: Get Virginia median household income")
    try:
        va_income = client.get_median_household_income(year=2022, state='51')
        logger.info(f"✓ Retrieved income data for {len(va_income)} localities")

        # Show first 5 records
        logger.info("  Sample records:")
        for record in va_income[:5]:
            name = record.get('NAME', 'Unknown')
            income = record.get('B19013_001E', 'N/A')
            if income != 'N/A' and income is not None:
                logger.info(f"    {name}: ${int(income):,}")
            else:
                logger.info(f"    {name}: {income}")

    except Exception as e:
        logger.error(f"✗ Failed to get median income: {e}")

    # Test 3: Get poverty rate data
    logger.info("\nTest 3: Get Virginia poverty rate data")
    try:
        va_poverty = client.get_poverty_rate(year=2022, state='51')
        logger.info(f"✓ Retrieved poverty data for {len(va_poverty)} localities")

        # Calculate and show poverty rates for first 5
        logger.info("  Sample records:")
        for record in va_poverty[:5]:
            name = record.get('NAME', 'Unknown')
            total = record.get('B17001_001E')
            below = record.get('B17001_002E')

            if total and below and total != 'N/A' and below != 'N/A':
                try:
                    total = int(total)
                    below = int(below)
                    if total > 0:
                        rate = (below / total) * 100
                        logger.info(f"    {name}: {rate:.1f}% poverty rate")
                    else:
                        logger.info(f"    {name}: N/A (no population)")
                except:
                    logger.info(f"    {name}: N/A (invalid data)")
            else:
                logger.info(f"    {name}: N/A")

    except Exception as e:
        logger.error(f"✗ Failed to get poverty data: {e}")

    # Test 4: Get educational attainment
    logger.info("\nTest 4: Get Virginia educational attainment")
    try:
        va_education = client.get_educational_attainment(year=2022, state='51')
        logger.info(f"✓ Retrieved education data for {len(va_education)} localities")

        # Calculate bachelor's degree or higher percentage
        logger.info("  Sample records (Bachelor's degree or higher %):")
        for record in va_education[:5]:
            name = record.get('NAME', 'Unknown')
            total = record.get('B15003_001E')
            bachelors = record.get('B15003_022E')
            masters = record.get('B15003_023E')
            professional = record.get('B15003_024E')
            doctorate = record.get('B15003_025E')

            try:
                total = int(total) if total and total != 'N/A' else 0
                ba_plus = sum([
                    int(x) if x and x != 'N/A' else 0
                    for x in [bachelors, masters, professional, doctorate]
                ])

                if total > 0:
                    pct = (ba_plus / total) * 100
                    logger.info(f"    {name}: {pct:.1f}%")
                else:
                    logger.info(f"    {name}: N/A")
            except:
                logger.info(f"    {name}: N/A (error)")

    except Exception as e:
        logger.error(f"✗ Failed to get education data: {e}")

    # Test 5: Test caching
    logger.info("\nTest 5: Test caching (should be faster on second call)")
    try:
        import time

        # First call (should hit API)
        start = time.time()
        _ = client.get_population(year=2022, state='51')
        first_call_time = time.time() - start

        # Second call (should use cache)
        start = time.time()
        _ = client.get_population(year=2022, state='51')
        second_call_time = time.time() - start

        logger.info(f"  First call: {first_call_time:.3f} seconds")
        logger.info(f"  Second call (cached): {second_call_time:.3f} seconds")

        if second_call_time < first_call_time:
            logger.info("  ✓ Caching working correctly")
        else:
            logger.warning("  ? Cache may not be working as expected")

    except Exception as e:
        logger.error(f"✗ Caching test failed: {e}")

    logger.info("\n" + "=" * 70)
    logger.info("Census API testing complete")
    logger.info("=" * 70)


if __name__ == '__main__':
    test_census_api()
