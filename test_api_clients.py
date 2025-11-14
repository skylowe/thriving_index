"""
Quick test script for API clients.
"""

from src.api_clients.census_api import CensusAPI
from src.utils.config import data_config


def test_census_api():
    """Test Census API client."""
    print("=" * 60)
    print("Testing Census API Client")
    print("=" * 60)

    # Initialize client
    client = CensusAPI()
    print(f"✅ Census API client initialized")

    # Test fetching population for Virginia (FIPS: 51)
    print("\nFetching population data for Virginia counties...")
    try:
        data = client.get_population(year=data_config.REFERENCE_YEAR, state='51')
        print(f"✅ Retrieved data for {len(data)} Virginia counties")

        if data:
            # Show first 3 counties
            print("\nSample data (first 3 counties):")
            for i, row in enumerate(data[:3]):
                name = row.get('NAME', 'Unknown')
                pop = row.get('B01001_001E', 'N/A')
                print(f"  {i+1}. {name}: Population = {pop}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test caching
    print("\nTesting cache...")
    try:
        data_cached = client.get_population(year=data_config.REFERENCE_YEAR, state='51')
        print(f"✅ Retrieved data from cache: {len(data_cached)} counties")
    except Exception as e:
        print(f"❌ Cache error: {e}")
        return False

    # Get cache stats
    stats = client.get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Cached items: {stats['num_cached_items']}")
    print(f"  Cache size: {stats['total_size_mb']} MB")
    print(f"  Cache directory: {stats['cache_dir']}")

    print("\n" + "=" * 60)
    print("✅ Census API client test passed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    test_census_api()
