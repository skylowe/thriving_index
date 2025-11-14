"""
Test script for FBI UCR Return A parser

This script:
1. Extracts the RETA data file from the zip
2. Parses the data file
3. Displays sample results for target states
4. Shows data quality metrics
"""

import sys
from pathlib import Path
import zipfile
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.fbi_ucr_parser import FBIUCRReturnAParser


def main():
    # Paths
    reta_zip = project_root / "data" / "crime" / "raw" / "reta-2024.zip"

    print("FBI UCR Return A Parser Test")
    print("=" * 60)
    print()

    # Extract zip file to temporary directory
    print(f"Extracting {reta_zip.name}...")
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(reta_zip, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Find the extracted file
        reta_file = Path(tmpdir) / "2024_RETA_NATIONAL_MASTER_FILE.txt"

        if not reta_file.exists():
            print(f"ERROR: Could not find extracted file")
            return

        print(f"Found: {reta_file.name}")
        print(f"File size: {reta_file.stat().st_size:,} bytes")
        print()

        # Parse the file
        print("Parsing RETA data...")
        parser = FBIUCRReturnAParser(reta_file)
        results = parser.parse()

        print(f"\nParsing complete!")
        print(f"Total agencies found: {len(results)}")
        print()

        # Analyze results by state
        print("Agencies by state:")
        print("-" * 40)
        state_counts = {}
        for agency in results:
            state = agency['state']
            state_counts[state] = state_counts.get(state, 0) + 1

        for state in sorted(state_counts.keys()):
            print(f"  {state}: {state_counts[state]} agencies")
        print()

        # Show sample Virginia agencies
        print("Sample Virginia agencies:")
        print("-" * 80)
        va_agencies = [a for a in results if a['state'] == 'VA'][:10]

        for agency in va_agencies:
            print(f"ORI: {agency['ori']}")
            print(f"  Violent crimes: {agency['violent_crime']:,}")
            print(f"    Murder: {agency['murder']}, Rape: {agency['rape_total']}, "
                  f"Robbery: {agency['robbery_total']}, Assault: {agency['assault_total']}")
            print(f"  Property crimes: {agency['property_crime']:,}")
            print(f"    Burglary: {agency['burglary_total']}, Larceny: {agency['larceny_total']}, "
                  f"MVT: {agency['mvt_total']}")
            print(f"  Population: {agency['population']:,}")
            print(f"  Months reported: {agency['months_reported']}")
            print()

        # Data quality check
        print("Data Quality Metrics:")
        print("-" * 40)

        full_year = [a for a in results if a['months_reported'] == 12]
        print(f"Agencies with 12 months data: {len(full_year)} ({len(full_year)/len(results)*100:.1f}%)")

        has_pop = [a for a in results if a['population'] > 0]
        print(f"Agencies with population data: {len(has_pop)} ({len(has_pop)/len(results)*100:.1f}%)")

        has_crime = [a for a in results if a['violent_crime'] > 0 or a['property_crime'] > 0]
        print(f"Agencies with crime data: {len(has_crime)} ({len(has_crime)/len(results)*100:.1f}%)")

        # Calculate total crimes for target states
        print()
        print("Total crimes by state (2024):")
        print("-" * 60)

        state_totals = {}
        for agency in results:
            state = agency['state']
            if state not in state_totals:
                state_totals[state] = {
                    'violent': 0, 'property': 0, 'population': 0, 'agencies': 0
                }

            state_totals[state]['violent'] += agency['violent_crime']
            state_totals[state]['property'] += agency['property_crime']
            state_totals[state]['population'] += agency['population']
            state_totals[state]['agencies'] += 1

        for state in sorted(state_totals.keys()):
            data = state_totals[state]
            violent_rate = (data['violent'] / data['population'] * 100000) if data['population'] > 0 else 0
            property_rate = (data['property'] / data['population'] * 100000) if data['population'] > 0 else 0

            print(f"{state}:")
            print(f"  Agencies: {data['agencies']}")
            print(f"  Population: {data['population']:,}")
            print(f"  Violent crimes: {data['violent']:,} ({violent_rate:.1f} per 100K)")
            print(f"  Property crimes: {data['property']:,} ({property_rate:.1f} per 100K)")
            print()


if __name__ == "__main__":
    main()
