"""
Parse FBI UCR ASR (Age, Sex, and Race) data files
ASR data contains ARREST statistics, not crime incident statistics
"""

import pandas as pd
from collections import defaultdict

def parse_asr_record(line):
    """Parse a single ASR record according to the documentation"""
    record = {
        'identifier': line[0:1],
        'state_code': line[1:3],
        'ori_code': line[3:10],
        'group': line[10:12],
        'division': line[12:13],
        'year': line[13:15],
        'msa': line[15:18].strip(),
        'offense_code': line[22:25],
        'county_code': line[32:35].strip(),
        'core_city': line[39:40],
        'population': line[40:50].strip(),
        'agency_name': line[110:135].strip(),
        'state_name': line[135:141].strip(),
    }

    # Only parse detail records (not headers)
    if record['offense_code'] != '000':
        # For detail records, there's age/sex/race data
        # We'll just sum total arrests for now
        pass

    return record

def extract_virginia_county_arrests(filepath):
    """
    Extract Virginia county-level arrest data from ASR file
    """
    print("Parsing ASR file...")
    print("Note: This is ARREST data, not crime incident data\n")

    counties = defaultdict(lambda: defaultdict(int))
    agencies = {}

    with open(filepath, 'r') as f:
        for line in f:
            if len(line) < 564:
                continue

            # Check if Virginia (state code 45)
            if line[1:3] != '45':
                continue

            # Check if county (groups 8 or 9)
            group = line[10:12]
            if group[0] not in ['8', '9']:
                continue

            record = parse_asr_record(line)

            # Header record - store agency info
            if record['offense_code'] == '000':
                key = (record['ori_code'], record['county_code'])
                agencies[key] = {
                    'agency_name': record['agency_name'],
                    'population': int(record['population']) if record['population'] else 0,
                    'group': record['group'],
                    'county_code': record['county_code']
                }
            else:
                # Detail record - count arrests by offense type
                key = (record['ori_code'], record['county_code'])
                offense = record['offense_code']

                # Sum up arrests from age/sex breakdowns
                # Total arrests are in the detail record
                # For now, we'll just count records
                counties[key][offense] += 1

    print(f"Found {len(agencies)} Virginia county agencies")
    print("\nSample agencies:")
    for i, (key, info) in enumerate(list(agencies.items())[:10]):
        print(f"  {info['agency_name']}: Pop={info['population']}, County={info['county_code']}")

    return agencies, counties

if __name__ == '__main__':
    filepath = '/home/user/thriving_index/data/crime/raw/asr-2024/2024_ASR12MON_NATIONAL_MASTER_FILE.txt'

    agencies, arrests = extract_virginia_county_arrests(filepath)

    # Offense code mapping
    offense_names = {
        '011': 'Murder',
        '020': 'Rape',
        '030': 'Robbery',
        '040': 'Aggravated Assault',
        '050': 'Burglary',
        '060': 'Larceny-Theft',
        '070': 'Motor Vehicle Theft',
    }

    print("\n" + "="*80)
    print("IMPORTANT FINDINGS:")
    print("="*80)
    print("\n1. This ASR data contains ARREST statistics, not CRIME statistics")
    print("   - Arrests != Crimes (one crime may have 0, 1, or multiple arrests)")
    print("   - For crime RATES, we need 'Offenses Known to Police' data\n")
    print("2. For accurate crime rates like Nebraska used, we would need:")
    print("   - FBI UCR 'Return A' data (Summary Reporting System)")
    print("   - OR: FBI NIBRS data (National Incident-Based Reporting)")
    print("   - OR: State-level crime data from Virginia State Police\n")
    print("3. If we use arrest data as a proxy:")
    print("   - It will underestimate crime rates (not all crimes result in arrest)")
    print("   - Different arrest rates across jurisdictions may reflect policing")
    print("     practices rather than actual crime levels")
    print("   - This would be methodologically different from Nebraska study")
