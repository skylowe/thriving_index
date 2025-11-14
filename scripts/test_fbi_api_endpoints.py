"""
Test FBI UCR API Endpoints

This script tests the FBI Crime Data API to verify:
1. API key authentication works
2. Correct endpoint structure
3. Available data for our study states
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.fbi_ucr_api import FBIUCRAPI
from src.utils.logging_setup import setup_logger


def test_state_summary(api: FBIUCRAPI, logger):
    """Test state-level crime summary endpoint."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: State Crime Summary")
    logger.info("=" * 70)

    try:
        # Test Virginia 2022 data
        logger.info("Fetching Virginia 2022 crime data...")
        data = api.get_state_crime_summary('VA', 2022)

        if data:
            logger.info(f"✓ Success! Retrieved data structure:")
            logger.info(f"  Keys in response: {list(data.keys())}")

            if 'data' in data and len(data['data']) > 0:
                logger.info(f"  Number of records: {len(data['data'])}")
                logger.info(f"  Sample record: {json.dumps(data['data'][0], indent=2)}")
            else:
                logger.warning(f"  Full response: {json.dumps(data, indent=2)}")

            return True
        else:
            logger.error("✗ No data returned")
            return False

    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agencies_list(api: FBIUCRAPI, logger):
    """Test agencies endpoint."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Agency List")
    logger.info("=" * 70)

    try:
        logger.info("Fetching agencies for Virginia...")
        data = api.get_agencies_by_state('VA')

        if data:
            logger.info(f"✓ Success! Retrieved agency data:")
            logger.info(f"  Keys in response: {list(data.keys())}")

            if 'data' in data and len(data['data']) > 0:
                logger.info(f"  Number of agencies: {len(data['data'])}")
                logger.info(f"  Sample agency: {json.dumps(data['data'][0], indent=2)}")
            else:
                logger.warning(f"  Full response: {json.dumps(data, indent=2)}")

            return True
        else:
            logger.error("✗ No data returned")
            return False

    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agency_crime_data(api: FBIUCRAPI, logger):
    """Test individual agency crime data endpoint."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Agency-Level Crime Data")
    logger.info("=" * 70)

    try:
        # First get an agency ORI
        logger.info("Getting agency list to find sample ORI...")
        agencies = api.get_agencies_by_state('VA')

        if not agencies or 'data' not in agencies or len(agencies['data']) == 0:
            logger.error("✗ Could not get agencies to test")
            return False

        # Get first agency ORI
        sample_ori = agencies['data'][0].get('ori')
        sample_name = agencies['data'][0].get('agency_name', 'Unknown')

        logger.info(f"Testing with agency: {sample_name} (ORI: {sample_ori})")

        data = api.get_agency_crime_data(sample_ori, 2022)

        if data:
            logger.info(f"✓ Success! Retrieved agency crime data:")
            logger.info(f"  Keys in response: {list(data.keys())}")

            if 'data' in data and len(data['data']) > 0:
                logger.info(f"  Number of offense records: {len(data['data'])}")
                logger.info(f"  Sample offense: {json.dumps(data['data'][0], indent=2)}")
            else:
                logger.warning(f"  Full response: {json.dumps(data, indent=2)}")

            return True
        else:
            logger.error("✗ No data returned")
            return False

    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_raw_endpoint(api: FBIUCRAPI, logger):
    """Test raw API endpoint to see actual response."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Raw API Endpoint Test")
    logger.info("=" * 70)

    # Try different endpoint patterns
    test_endpoints = [
        "/api/summarized/state/VA/offense/2022",
        "/summarized/state/VA/offense/2022",
        "/states/VA/offense/2022",
        "/v1/state/VA/2022",
    ]

    for endpoint in test_endpoints:
        logger.info(f"\nTrying endpoint: {endpoint}")
        try:
            data = api.fetch(endpoint, use_cache=False)
            logger.info(f"✓ Success with endpoint: {endpoint}")
            logger.info(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed: {str(e)[:100]}")

    return False


def main():
    """Run all FBI UCR API tests."""
    logger = setup_logger('test_fbi_api')

    logger.info("=" * 70)
    logger.info("FBI UCR API ENDPOINT TESTING")
    logger.info("=" * 70)

    # Initialize API client
    api = FBIUCRAPI()

    # Check API key
    if not api.api_key:
        logger.error("FBI UCR API key not found in environment!")
        logger.error("Please set FBI_UCR_KEY environment variable")
        return
    else:
        logger.info(f"✓ API key found: {api.api_key[:10]}...")
        logger.info(f"✓ Base URL: {api.base_url}")

    # Run tests
    results = {
        'state_summary': test_state_summary(api, logger),
        'agencies_list': test_agencies_list(api, logger),
        'agency_crime_data': test_agency_crime_data(api, logger),
        'raw_endpoint': test_raw_endpoint(api, logger),
    }

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    logger.info(f"\nOverall: {passed_count}/{total_count} tests passed")

    if passed_count == 0:
        logger.error("\n⚠ All tests failed - API endpoint structure may be incorrect")
        logger.error("Recommended actions:")
        logger.error("  1. Check FBI UCR API documentation for current endpoints")
        logger.error("  2. Verify API key is valid and active")
        logger.error("  3. Check if API base URL has changed")
    elif passed_count < total_count:
        logger.warning(f"\n⚠ Some tests failed - partial API functionality")
    else:
        logger.info("\n✓ All tests passed - API is working correctly")


if __name__ == '__main__':
    main()
