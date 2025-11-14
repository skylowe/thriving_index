"""
Test script for BEA API client.

Tests basic functionality and data collection for regional income data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bea_api import BEAAPI
from src.utils.logging_setup import setup_logger


def test_bea_api():
    """Test BEA API client with sample requests."""
    logger = setup_logger('test_bea_api')

    logger.info("=" * 70)
    logger.info("Testing BEA API Client")
    logger.info("=" * 70)

    # Initialize client
    try:
        client = BEAAPI()
        logger.info("✓ BEA API client initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize BEA API client: {e}")
        return

    # Test 1: Get personal income for Virginia counties
    logger.info("\nTest 1: Get Virginia personal income (2022)")
    try:
        va_income = client.get_personal_income(
            year=2022,
            state_fips='51',
            geo_level='county'
        )

        if va_income:
            logger.info(f"✓ Retrieved income data for {len(va_income)} Virginia localities")

            # Show first 5 records
            logger.info("  Sample records:")
            for record in va_income[:5]:
                geo_name = record.get('GeoName', 'Unknown')
                value = record.get('DataValue', 'N/A')
                if value != 'N/A':
                    try:
                        value_millions = float(value)
                        logger.info(f"    {geo_name}: ${value_millions:.1f} million")
                    except:
                        logger.info(f"    {geo_name}: {value}")
                else:
                    logger.info(f"    {geo_name}: {value}")
        else:
            logger.warning("  No data returned")

    except Exception as e:
        logger.error(f"✗ Failed to get Virginia personal income: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Get per capita income
    logger.info("\nTest 2: Get Virginia per capita income (2022)")
    try:
        va_per_capita = client.get_per_capita_income(
            year=2022,
            state_fips='51',
            geo_level='county'
        )

        if va_per_capita:
            logger.info(f"✓ Retrieved per capita income for {len(va_per_capita)} localities")

            # Show first 5 records
            logger.info("  Sample records:")
            for record in va_per_capita[:5]:
                geo_name = record.get('GeoName', 'Unknown')
                value = record.get('DataValue', 'N/A')
                if value != 'N/A':
                    try:
                        value_dollars = float(value)
                        logger.info(f"    {geo_name}: ${value_dollars:,.0f}")
                    except:
                        logger.info(f"    {geo_name}: {value}")
                else:
                    logger.info(f"    {geo_name}: {value}")
        else:
            logger.warning("  No data returned")

    except Exception as e:
        logger.error(f"✗ Failed to get per capita income: {e}")

    # Test 3: Get wage and salary data
    logger.info("\nTest 3: Get Virginia wages and salaries (2022)")
    try:
        va_wages = client.get_wages_salaries(
            year=2022,
            state_fips='51',
            geo_level='county'
        )

        if va_wages:
            logger.info(f"✓ Retrieved wage data for {len(va_wages)} localities")

            logger.info("  Sample records:")
            for record in va_wages[:5]:
                geo_name = record.get('GeoName', 'Unknown')
                value = record.get('DataValue', 'N/A')
                if value != 'N/A':
                    try:
                        value_millions = float(value)
                        logger.info(f"    {geo_name}: ${value_millions:.1f} million")
                    except:
                        logger.info(f"    {geo_name}: {value}")
        else:
            logger.warning("  No data returned")

    except Exception as e:
        logger.error(f"✗ Failed to get wages: {e}")

    # Test 4: Test caching
    logger.info("\nTest 4: Test caching (should be faster on second call)")
    try:
        import time

        # First call (should hit API or use existing cache)
        start = time.time()
        _ = client.get_personal_income(year=2022, state_fips='51', geo_level='county')
        first_call_time = time.time() - start

        # Second call (should use cache)
        start = time.time()
        _ = client.get_personal_income(year=2022, state_fips='51', geo_level='county')
        second_call_time = time.time() - start

        logger.info(f"  First call: {first_call_time:.3f} seconds")
        logger.info(f"  Second call (cached): {second_call_time:.3f} seconds")

        if second_call_time < first_call_time or second_call_time < 0.01:
            logger.info("  ✓ Caching working correctly")
        else:
            logger.warning("  ? Cache may not be working as expected")

    except Exception as e:
        logger.error(f"✗ Caching test failed: {e}")

    logger.info("\n" + "=" * 70)
    logger.info("BEA API testing complete")
    logger.info("=" * 70)


if __name__ == '__main__':
    test_bea_api()
