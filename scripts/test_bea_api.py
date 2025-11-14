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

    # Test 1: Get personal income per capita for Virginia counties
    logger.info("\nTest 1: Get Virginia per capita income (2022)")
    try:
        va_income = client.get_personal_income_per_capita(
            year=2022,
            state='51'
        )

        # Parse response
        if va_income and va_income.get('BEAAPI'):
            results = va_income['BEAAPI'].get('Results', {})
            data = results.get('Data', [])

            if data:
                logger.info(f"✓ Retrieved per capita income for {len(data)} Virginia localities")

                # Show first 5 records
                logger.info("  Sample records:")
                for record in data[:5]:
                    geo_name = record.get('GeoName', 'Unknown')
                    value = record.get('DataValue', 'N/A')
                    if value not in ['N/A', '(NA)', '(D)']:
                        try:
                            value_dollars = float(value)
                            logger.info(f"    {geo_name}: ${value_dollars:,.0f}")
                        except:
                            logger.info(f"    {geo_name}: {value}")
            else:
                logger.warning("  No data returned")
        else:
            logger.warning("  No valid response")

    except Exception as e:
        logger.error(f"✗ Failed to get Virginia personal income: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Get farm proprietors income
    logger.info("\nTest 2: Get Virginia farm proprietors income (2022)")
    try:
        va_farm = client.get_farm_proprietors_income(
            year=2022,
            state='51'
        )

        # Parse response
        if va_farm and va_farm.get('BEAAPI'):
            results = va_farm['BEAAPI'].get('Results', {})
            data = results.get('Data', [])

            if data:
                logger.info(f"✓ Retrieved farm income for {len(data)} localities")

                # Show first 5 records
                logger.info("  Sample records:")
                for record in data[:5]:
                    geo_name = record.get('GeoName', 'Unknown')
                    value = record.get('DataValue', 'N/A')
                    if value not in ['N/A', '(NA)', '(D)']:
                        try:
                            value_thousands = float(value)
                            logger.info(f"    {geo_name}: ${value_thousands:,.0f} thousand")
                        except:
                            logger.info(f"    {geo_name}: {value}")
            else:
                logger.warning("  No data returned")
        else:
            logger.warning("  No valid response")

    except Exception as e:
        logger.error(f"✗ Failed to get farm income: {e}")

    # Test 3: Get employment by industry
    logger.info("\nTest 3: Get Virginia employment by industry (2022)")
    try:
        va_employment = client.get_employment_by_industry(
            year=2022,
            state='51',
            industry_codes=[10, 310]  # Total and Manufacturing
        )

        # Parse response
        if va_employment and va_employment.get('BEAAPI'):
            results = va_employment['BEAAPI'].get('Results', {})
            data = results.get('Data', [])

            if data:
                logger.info(f"✓ Retrieved employment data ({len(data)} records)")

                # Show sample manufacturing employment
                logger.info("  Sample manufacturing employment records:")
                mfg_records = [r for r in data if r.get('LineCode') == '310'][:5]
                for record in mfg_records:
                    geo_name = record.get('GeoName', 'Unknown')
                    value = record.get('DataValue', 'N/A')
                    if value not in ['N/A', '(NA)', '(D)']:
                        try:
                            emp_count = float(value)
                            logger.info(f"    {geo_name}: {emp_count:,.0f} jobs")
                        except:
                            logger.info(f"    {geo_name}: {value}")
            else:
                logger.warning("  No data returned")
        else:
            logger.warning("  No valid response")

    except Exception as e:
        logger.error(f"✗ Failed to get employment data: {e}")

    # Test 4: Test caching
    logger.info("\nTest 4: Test caching (should be faster on second call)")
    try:
        import time

        # First call (should hit API or use existing cache)
        start = time.time()
        _ = client.get_personal_income_per_capita(year=2022, state='51')
        first_call_time = time.time() - start

        # Second call (should use cache)
        start = time.time()
        _ = client.get_personal_income_per_capita(year=2022, state='51')
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
