"""
Debug BEA API Response

Quick script to see what the BEA API is actually returning.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bea_api import BEAAPI

def main():
    bea = BEAAPI()

    print("Testing BEA API with Virginia (FIPS: 51)")
    print("=" * 70)

    # Test farm income
    print("\n1. Farm Proprietors Income (2022, Virginia):")
    farm_data = bea.get_farm_proprietors_income(year=2022, state='51')
    print(f"Response type: {type(farm_data)}")
    print(f"Response keys: {farm_data.keys() if isinstance(farm_data, dict) else 'N/A'}")
    print("\nFull response:")
    print(json.dumps(farm_data, indent=2)[:2000])  # First 2000 chars

    print("\n" + "=" * 70)

    # Test total income
    print("\n2. Total Personal Income (2022, Virginia):")
    total_data = bea.get_regional_income(year=2022, state='51', line_codes=[1])
    print(f"Response type: {type(total_data)}")
    print(f"Response keys: {total_data.keys() if isinstance(total_data, dict) else 'N/A'}")
    print("\nFull response:")
    print(json.dumps(total_data, indent=2)[:2000])  # First 2000 chars

    print("\n" + "=" * 70)

    # Test employment by industry
    print("\n3. Employment by Industry (2022, Virginia):")
    emp_data = bea.get_employment_by_industry(year=2022, state='51', line_codes=[310, 10])
    print(f"Response type: {type(emp_data)}")
    print(f"Response keys: {emp_data.keys() if isinstance(emp_data, dict) else 'N/A'}")
    print("\nFull response:")
    print(json.dumps(emp_data, indent=2)[:2000])  # First 2000 chars

if __name__ == '__main__':
    main()
