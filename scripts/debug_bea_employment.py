"""
Debug BEA Employment API Response

Quick script to see what the BEA employment API is returning.
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

    print("Testing BEA Employment API with Virginia (FIPS: 51)")
    print("=" * 70)

    # Test employment by industry
    print("\n1. Employment by Industry (2022, Virginia, codes [310, 10]):")
    emp_data = bea.get_employment_by_industry(year=2022, state='51')
    print(f"Response type: {type(emp_data)}")
    print(f"Response keys: {emp_data.keys() if isinstance(emp_data, dict) else 'N/A'}")

    if emp_data.get('BEAAPI'):
        if 'Error' in emp_data['BEAAPI']:
            print("\nERROR FROM API:")
            print(json.dumps(emp_data['BEAAPI']['Error'], indent=2))
        elif 'Results' in emp_data['BEAAPI']:
            print("\nResults found!")
            results = emp_data['BEAAPI']['Results']
            print(f"Table: {results.get('PublicTable', 'N/A')}")
            print(f"Data records: {len(results.get('Data', []))}")
            if results.get('Data'):
                print("\nFirst 3 data records:")
                for i, record in enumerate(results['Data'][:3]):
                    print(f"\nRecord {i+1}:")
                    print(json.dumps(record, indent=2))

    print("\n" + "=" * 70)

    # Try with default line codes
    print("\n2. Employment by Industry with default codes:")
    emp_data2 = bea.get_employment_by_industry(year=2022, state='51', industry_codes=[10, 310])
    if emp_data2.get('BEAAPI', {}).get('Results', {}).get('Data'):
        print(f"Data records: {len(emp_data2['BEAAPI']['Results']['Data'])}")
        print("\nFirst record:")
        print(json.dumps(emp_data2['BEAAPI']['Results']['Data'][0], indent=2))
    elif 'Error' in emp_data2.get('BEAAPI', {}):
        print("\nERROR:")
        print(json.dumps(emp_data2['BEAAPI']['Error'], indent=2))

    print("\n" + "=" * 70)

    # Check what line codes work
    print("\n3. Trying line code 10 only (Total employment):")
    emp_data3 = bea.get_employment_by_industry(year=2022, state='51', industry_codes=[10])
    if emp_data3.get('BEAAPI', {}).get('Results', {}).get('Data'):
        data = emp_data3['BEAAPI']['Results']['Data']
        print(f"Data records: {len(data)}")
        print("\nFirst 2 records:")
        for record in data[:2]:
            print(f"  {record.get('GeoName')}: {record.get('DataValue')}")
    elif 'Error' in emp_data3.get('BEAAPI', {}):
        print("\nERROR:")
        print(json.dumps(emp_data3['BEAAPI']['Error'], indent=2))

if __name__ == '__main__':
    main()
