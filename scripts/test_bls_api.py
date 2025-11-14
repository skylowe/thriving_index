"""
Test script for BLS API client.

Tests basic functionality and data collection for unemployment and employment data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bls_api import BLSAPI
from src.utils.logging_setup import setup_logger


def test_bls_api():
    """Test BLS API client with sample requests."""
    logger = setup_logger('test_bls_api')

    logger.info("=" * 70)
    logger.info("Testing BLS API Client")
    logger.info("=" * 70)

    # Initialize client
    try:
        client = BLSAPI()
        logger.info("✓ BLS API client initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize BLS API client: {e}")
        return

    # Test 1: Get unemployment rate for sample Virginia counties
    logger.info("\nTest 1: Get unemployment rates for sample Virginia localities")

    # Sample FIPS codes
    sample_fips = {
        '51059': 'Fairfax County',
        '51013': 'Arlington County',
        '51760': 'Richmond City',
        '51810': 'Virginia Beach City',
        '51003': 'Albemarle County'
    }

    try:
        for fips, name in sample_fips.items():
            logger.info(f"\n  Fetching data for {name} (FIPS: {fips})...")

            unemp_data = client.get_unemployment_rate(
                year=2023,
                state_fips=fips[:2],
                county_fips=fips[2:]
            )

            if unemp_data:
                logger.info(f"    ✓ Retrieved {len(unemp_data)} monthly records")

                # Show annual average
                rates = [float(record.get('value', 0)) for record in unemp_data
                        if record.get('value') and record.get('value') != 'N/A']

                if rates:
                    avg_rate = sum(rates) / len(rates)
                    logger.info(f"    Average unemployment rate: {avg_rate:.1f}%")
                    logger.info(f"    Range: {min(rates):.1f}% to {max(rates):.1f}%")
            else:
                logger.warning(f"    No data returned for {name}")

    except Exception as e:
        logger.error(f"✗ Failed to get unemployment rates: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Get labor force data
    logger.info("\n" + "=" * 70)
    logger.info("Test 2: Get labor force data")

    try:
        # Get data for Fairfax County
        fips = '51059'
        name = 'Fairfax County'

        logger.info(f"\n  Fetching labor force data for {name}...")

        lf_data = client.get_labor_force(
            year=2023,
            state_fips='51',
            county_fips='059'
        )

        if lf_data:
            logger.info(f"    ✓ Retrieved {len(lf_data)} monthly records")

            # Show recent month
            if lf_data:
                recent = lf_data[-1]
                period = recent.get('period', 'Unknown')
                value = recent.get('value', 'N/A')
                logger.info(f"    Most recent ({period}): {value:,} people in labor force")
        else:
            logger.warning(f"    No labor force data returned")

    except Exception as e:
        logger.error(f"✗ Failed to get labor force data: {e}")

    # Test 3: Get employment data
    logger.info("\n" + "=" * 70)
    logger.info("Test 3: Get employment data")

    try:
        emp_data = client.get_employment(
            year=2023,
            state_fips='51',
            county_fips='059'
        )

        if emp_data:
            logger.info(f"  ✓ Retrieved {len(emp_data)} monthly employment records")

            if emp_data:
                recent = emp_data[-1]
                period = recent.get('period', 'Unknown')
                value = recent.get('value', 'N/A')
                logger.info(f"    Most recent ({period}): {value:,} employed")
        else:
            logger.warning("  No employment data returned")

    except Exception as e:
        logger.error(f"✗ Failed to get employment data: {e}")

    # Test 4: Test caching
    logger.info("\n" + "=" * 70)
    logger.info("Test 4: Test caching")

    try:
        import time

        # First call
        start = time.time()
        _ = client.get_unemployment_rate(year=2023, state_fips='51', county_fips='059')
        first_call_time = time.time() - start

        # Second call (should use cache)
        start = time.time()
        _ = client.get_unemployment_rate(year=2023, state_fips='51', county_fips='059')
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
    logger.info("BLS API testing complete")
    logger.info("=" * 70)


if __name__ == '__main__':
    test_bls_api()
