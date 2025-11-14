"""
Quick API test to verify API clients work with sample Virginia regions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.api_clients.bea_api import BEAAPI

# Test regions
TEST_REGIONS = [
    {'fips': '51059', 'name': 'Fairfax County'},
    {'fips': '51510', 'name': 'Alexandria City'},
]

print("=" * 70)
print("QUICK API TEST - Virginia Thriving Index")
print("=" * 70)
print()

# Test Census API
print("Testing Census API...")
print("-" * 70)

try:
    census = CensusAPI()
    print("✓ Census API client initialized")

    # Test median household income
    print("\nFetching median household income for Virginia (2022)...")
    try:
        data = census.get_median_household_income(year=2022, state='51')
        if data:
            print(f"  ✓ Retrieved data for {len(data)} Virginia localities")
            # Show sample for our test regions
            for region in TEST_REGIONS:
                region_data = [d for d in data if d.get('county') == region['fips'][2:]]
                if region_data:
                    income = region_data[0].get('median_household_income')
                    print(f"    - {region['name']}: ${income:,}" if income else f"    - {region['name']}: No income data")
        else:
            print(f"  ✗ No data returned")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

except Exception as e:
    print(f"✗ Census API error: {str(e)}")

print()

# Test BEA API
print("Testing BEA API...")
print("-" * 70)

try:
    bea = BEAAPI()
    print("✓ BEA API client initialized")

    # Test per capita personal income
    print("\nFetching per capita personal income for Virginia (2022)...")
    try:
        data = bea.get_personal_income_per_capita(year=2022, state='51')
        if data:
            print(f"  ✓ Retrieved data for {len(data)} regions")
            # Show sample for our test regions
            for region in TEST_REGIONS:
                region_data = [d for d in data if d.get('GeoFips') == region['fips']]
                if region_data:
                    income = region_data[0].get('DataValue')
                    print(f"    - {region['name']}: ${income:,}" if income else f"    - {region['name']}: No income data")
        else:
            print(f"  ✗ No data returned")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

except Exception as e:
    print(f"✗ BEA API error: {str(e)}")

print()
print("=" * 70)
print("Test complete!")
print("=" * 70)
