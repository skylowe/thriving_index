"""Quick test to see BEA API response structure"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from api_clients.bea_client import BEAClient
import json

client = BEAClient()

# Test with all counties, 2022
print("Testing BEA API response structure...")
print("="  * 60)

try:
    # Try with just COUNTY to get all counties
    response = client.get_cainc5_data('COUNTY', '2022', 10)
    print("Response keys:", response.get('BEAAPI', {}).get('Results', {}).keys())

    if 'Data' in response.get('BEAAPI', {}).get('Results', {}):
        data = response['BEAAPI']['Results']['Data']
        print(f"Number of records: {len(data)}")
        print(f"Sample record: {data[0] if data else 'No data'}")
    elif 'Error' in response.get('BEAAPI', {}).get('Results', {}):
        print(f"Error: {response['BEAAPI']['Results']['Error']}")
except Exception as e:
    print(f"Error: {e}")
