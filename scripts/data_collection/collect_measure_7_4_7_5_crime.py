"""
Data Collection Script for Component 7 Measures 7.4 and 7.5
Violent Crime Rate and Property Crime Rate

This script collects FBI UCR crime data for law enforcement agencies
in our 10-state region and aggregates to county level.

FBI Crime Data Explorer API: https://api.usa.gov/crime/fbi/cde/
"""

import csv
import json
import time
from pathlib import Path
from collections import defaultdict
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from api_clients.fbi_cde_client import FBICrimeClient
from config import STATE_FIPS, STATE_NAMES, PROCESSED_DATA_DIR, PROJECT_ROOT


def load_ori_crosswalk(crosswalk_path):
    """
    Load ORI crosswalk file and filter to our 10 states.

    Args:
        crosswalk_path: Path to ori_crosswalk.tsv file

    Returns:
        list: List of dictionaries containing ORI records
    """
    target_states = [
        'VIRGINIA', 'PENNSYLVANIA', 'MARYLAND', 'DELAWARE',
        'WEST VIRGINIA', 'KENTUCKY', 'TENNESSEE',
        'NORTH CAROLINA', 'SOUTH CAROLINA', 'GEORGIA'
    ]

    oris = []

    with open(crosswalk_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to our states, valid ORI9 (FBI API uses 9-character codes), and reporting agencies
            if (row.get('STATENAME', '') in target_states and
                row.get('ORI9', '') and
                row.get('ORI9', '') != '-1' and
                row.get('REPORT_FLAG', '') == '1' and
                row.get('FIPS', '')):  # Must have county FIPS
                oris.append({
                    'ori': row['ORI9'],  # Use ORI9 for FBI API
                    'ori7': row.get('ORI7', ''),
                    'ori9': row['ORI9'],
                    'name': row.get('NAME', ''),
                    'fips': row['FIPS'],
                    'state_fips': row['FIPS_ST'],
                    'county_fips': row['FIPS_COUNTY'],
                    'state_name': row['STATENAME'],
                    'county_name': row.get('COUNTYNAME', ''),
                    'population': row.get('U_TPOP', '0')
                })

    return oris


def extract_crime_totals(crime_data):
    """
    Extract total crimes from FBI API response.

    Args:
        crime_data: API response dictionary

    Returns:
        int: Total crime count, or 0 if no data
    """
    if not crime_data or 'offenses' not in crime_data:
        return 0

    offenses = crime_data['offenses']
    actuals = offenses.get('actuals')

    if not actuals:
        # No actual data reported for this agency
        return 0

    # Sum up all crime counts across all months for this agency
    # The actuals dict has agency names as keys, with monthly data as values
    # We want the agency's data, not the clearances
    total = 0
    for agency_name, monthly_data in actuals.items():
        # Skip clearances entries
        if 'Clearances' in agency_name:
            continue

        # Sum all monthly values
        if isinstance(monthly_data, dict):
            for month, count in monthly_data.items():
                try:
                    total += int(count)
                except (ValueError, TypeError):
                    pass

    return total


def collect_crime_data_for_oris(client, oris, from_date, to_date, limit=None):
    """
    Collect crime data for list of ORIs.

    Args:
        client: FBICrimeClient instance
        oris: List of ORI records
        from_date: Start date (MM-YYYY)
        to_date: End date (MM-YYYY)
        limit: Maximum number of ORIs to process (for testing)

    Returns:
        dict: Dictionary mapping ORI to crime data
    """
    results = {}
    total = len(oris) if limit is None else min(limit, len(oris))
    oris_to_process = oris[:limit] if limit else oris

    print(f"\nCollecting crime data for {total} agencies...")
    print(f"Date range: {from_date} to {to_date}")
    print(f"Total API calls that will be made: {total * 2} (2 per agency)")
    print(f"API calls from cache will not count against daily limit\n")

    for i, ori_record in enumerate(oris_to_process, 1):
        ori = ori_record['ori']  # Use ORI9 for API calls

        if i % 50 == 0 or i == 1:
            print(f"Progress: {i}/{total} agencies ({i/total*100:.1f}%) - "
                  f"API calls made: {client.api_calls_made}")

        try:
            # Get both violent and property crime data
            crime_data = client.get_all_crime_data(ori, from_date, to_date)

            # Extract totals
            violent_total = extract_crime_totals(crime_data['violent'])
            property_total = extract_crime_totals(crime_data['property'])

            results[ori] = {
                'ori': ori,
                'name': ori_record['name'],
                'fips': ori_record['fips'],
                'state_fips': ori_record['state_fips'],
                'county_fips': ori_record['county_fips'],
                'state_name': ori_record['state_name'],
                'county_name': ori_record['county_name'],
                'violent_crimes': violent_total,
                'property_crimes': property_total,
                'violent_data': crime_data['violent'],
                'property_data': crime_data['property']
            }

        except Exception as e:
            print(f"Error processing ORI {ori}: {e}")
            results[ori] = {
                'ori': ori,
                'error': str(e)
            }

    print(f"\nCollection complete!")
    print(f"Total API calls made: {client.api_calls_made}")
    print(f"Successfully collected data for: {len([r for r in results.values() if 'error' not in r])} agencies")

    return results


def aggregate_to_county_level(ori_results):
    """
    Aggregate agency-level crime data to county level.

    Args:
        ori_results: Dictionary of ORI crime data

    Returns:
        dict: Dictionary mapping county FIPS to aggregated crime data
    """
    county_data = defaultdict(lambda: {
        'violent_crimes': 0,
        'property_crimes': 0,
        'agency_count': 0,
        'agencies': []
    })

    for ori, data in ori_results.items():
        if 'error' in data:
            continue

        fips = data['fips']
        county_data[fips]['violent_crimes'] += data.get('violent_crimes', 0)
        county_data[fips]['property_crimes'] += data.get('property_crimes', 0)
        county_data[fips]['agency_count'] += 1
        county_data[fips]['agencies'].append(ori)

        # Store metadata (use first agency's data)
        if 'state_fips' not in county_data[fips]:
            county_data[fips]['state_fips'] = data['state_fips']
            county_data[fips]['county_fips'] = data['county_fips']
            county_data[fips]['state_name'] = data['state_name']
            county_data[fips]['county_name'] = data['county_name']
            county_data[fips]['fips'] = fips

    return dict(county_data)


def save_results(ori_results, county_results, output_dir, year):
    """
    Save results to files.

    Args:
        ori_results: Agency-level results
        county_results: County-level aggregated results
        output_dir: Output directory path
        year: Year of data
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save agency-level data (JSON)
    agency_file = output_dir / f'fbi_crime_agencies_{year}.json'
    with open(agency_file, 'w') as f:
        json.dump(ori_results, f, indent=2)
    print(f"Saved agency-level data: {agency_file}")

    # Save county-level data (CSV)
    county_file = output_dir / f'fbi_crime_counties_{year}.csv'
    with open(county_file, 'w', newline='') as f:
        fieldnames = ['fips', 'state_fips', 'county_fips', 'state_name', 'county_name',
                      'violent_crimes', 'property_crimes', 'agency_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for fips in sorted(county_results.keys()):
            data = county_results[fips]
            writer.writerow({
                'fips': data['fips'],
                'state_fips': data['state_fips'],
                'county_fips': data['county_fips'],
                'state_name': data['state_name'],
                'county_name': data['county_name'],
                'violent_crimes': data['violent_crimes'],
                'property_crimes': data['property_crimes'],
                'agency_count': data['agency_count']
            })

    print(f"Saved county-level data: {county_file}")

    # Save summary
    summary = {
        'year': year,
        'total_agencies': len(ori_results),
        'agencies_with_data': len([r for r in ori_results.values() if 'error' not in r]),
        'agencies_with_errors': len([r for r in ori_results.values() if 'error' in r]),
        'total_counties': len(county_results),
        'total_violent_crimes': sum(c['violent_crimes'] for c in county_results.values()),
        'total_property_crimes': sum(c['property_crimes'] for c in county_results.values())
    }

    summary_file = output_dir / f'fbi_crime_summary_{year}.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary: {summary_file}")

    print(f"\nSummary Statistics:")
    print(f"  Total agencies processed: {summary['total_agencies']}")
    print(f"  Agencies with data: {summary['agencies_with_data']}")
    print(f"  Counties with data: {summary['total_counties']}")
    print(f"  Total violent crimes: {summary['total_violent_crimes']:,}")
    print(f"  Total property crimes: {summary['total_property_crimes']:,}")


def main():
    """Main execution function"""

    print("="*70)
    print("FBI Crime Data Collection - Measures 7.4 and 7.5")
    print("Violent Crime Rate and Property Crime Rate")
    print("="*70)

    # Configuration
    CROSSWALK_FILE = PROJECT_ROOT / 'ori_crosswalk.tsv'
    OUTPUT_DIR = PROCESSED_DATA_DIR
    FROM_DATE = '01-2023'  # Full year 2023
    TO_DATE = '12-2023'
    YEAR = '2023'

    # TEST MODE: Set to a small number for testing, None for full collection
    # WARNING: Full collection requires ~11,486 API calls (5,743 agencies × 2)
    # TEST_LIMIT = 30  # Test with 30 agencies
    TEST_STATE = 'VIRGINIA'  # Collecting Virginia agencies only
    TEST_LIMIT = None  # Full collection for Virginia
    # TEST_STATE = None  # Uncomment to include all states

    if TEST_LIMIT or TEST_STATE:
        if TEST_LIMIT:
            print(f"\n⚠️  TEST MODE: Processing up to {TEST_LIMIT} agencies")
        if TEST_STATE:
            print(f"⚠️  TEST MODE: Filtering to {TEST_STATE} only")
        print(f"⚠️  Set TEST_LIMIT = None and TEST_STATE = None for full collection\n")

    # Load ORI crosswalk
    print(f"\nLoading ORI crosswalk from: {CROSSWALK_FILE}")
    oris = load_ori_crosswalk(CROSSWALK_FILE)
    print(f"Loaded {len(oris)} reporting agencies across 10 states")

    # Filter to test state if specified
    if TEST_STATE:
        oris = [ori for ori in oris if ori['state_name'] == TEST_STATE]
        print(f"Filtered to {len(oris)} agencies in {TEST_STATE}")

    # Show state breakdown
    state_counts = defaultdict(int)
    for ori in oris:
        state_counts[ori['state_name']] += 1

    print("\nAgencies by state:")
    for state in sorted(state_counts.keys()):
        print(f"  {state}: {state_counts[state]}")

    # Initialize API client
    print(f"\nInitializing FBI Crime Data Explorer API client...")
    client = FBICrimeClient()
    print(f"Cache directory: {client.cache_dir}")

    # Collect crime data
    ori_results = collect_crime_data_for_oris(
        client=client,
        oris=oris,
        from_date=FROM_DATE,
        to_date=TO_DATE,
        limit=TEST_LIMIT
    )

    # Aggregate to county level
    print("\nAggregating data to county level...")
    county_results = aggregate_to_county_level(ori_results)
    print(f"Aggregated data for {len(county_results)} counties")

    # Save results
    print("\nSaving results...")
    save_results(ori_results, county_results, OUTPUT_DIR, YEAR)

    print("\n" + "="*70)
    print("Collection complete!")
    print("="*70)

    if TEST_LIMIT:
        print(f"\n⚠️  REMINDER: This was a test run with {TEST_LIMIT} agencies")
        print("⚠️  To collect full data, set TEST_LIMIT = None and re-run")
        print(f"⚠️  Full collection requires ~{len(oris) * 2} API calls")
        print("⚠️  With 1000 call/day limit, this will take ~{} days".format(
            (len(oris) * 2) // 1000 + 1))
        print("⚠️  Caching will prevent re-downloading on subsequent runs")


if __name__ == '__main__':
    main()
