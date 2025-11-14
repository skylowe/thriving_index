"""
Generate Complete CBSA Classifications

Parses the Census Bureau CBSA delineation file and creates a complete
classification dictionary for all ~530 counties in the study region.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Study states and their FIPS codes
STUDY_STATES = {
    '51': 'Virginia',
    '24': 'Maryland',
    '54': 'West Virginia',
    '37': 'North Carolina',
    '47': 'Tennessee',
    '21': 'Kentucky',
    '11': 'District of Columbia'
}


def parse_cbsa_file(filepath: str) -> pd.DataFrame:
    """
    Parse CBSA delineation file.

    Args:
        filepath: Path to CBSA Excel file

    Returns:
        DataFrame with CBSA classifications
    """
    # Read Excel file, skipping first 2 rows
    df = pd.read_excel(filepath, skiprows=2)

    # Rename columns for clarity
    df.columns = [
        'cbsa_code',
        'metro_div_code',
        'csa_code',
        'cbsa_title',
        'metro_micro',
        'metro_div_title',
        'csa_title',
        'county_name',
        'state_name',
        'fips_state',
        'fips_county',
        'central_outlying'
    ]

    return df


def create_classification_dict(df: pd.DataFrame) -> dict:
    """
    Create classification dictionary from CBSA dataframe.

    Args:
        df: Parsed CBSA data

    Returns:
        Dict mapping FIPS codes to classification info
    """
    classifications = {}

    # Filter to study states only (handle float FIPS codes)
    df['fips_state_str'] = df['fips_state'].fillna(0).astype(int).astype(str).str.zfill(2)
    df_filtered = df[df['fips_state_str'].isin(STUDY_STATES.keys())]

    print(f"  Filtered to {len(df_filtered)} counties in study states")

    for _, row in df_filtered.iterrows():
        # Create 5-digit FIPS code (handle NaN values)
        try:
            state_fips = str(int(row['fips_state'])).zfill(2)
            county_fips = str(int(row['fips_county'])).zfill(3)
            full_fips = state_fips + county_fips
        except (ValueError, TypeError):
            print(f"    Skipping row with invalid FIPS: {row['county_name']}")
            continue

        # Determine metro/micro classification
        metro_micro_text = str(row['metro_micro']).lower()
        if 'metropolitan' in metro_micro_text:
            cbsa_type = 'metro'
        elif 'micropolitan' in metro_micro_text:
            cbsa_type = 'micro'
        else:
            cbsa_type = 'rural'

        # Get CBSA name
        cbsa_name = row['cbsa_title'] if pd.notna(row['cbsa_title']) else None

        # Get county name (clean it up and escape quotes)
        county_name = row['county_name']
        if pd.isna(county_name):
            county_name = 'Unknown'
        else:
            # Remove "County", "city", etc. suffixes for cleaner names
            county_name = str(county_name).replace(' County', '').replace(' city', '').strip()
            # Escape single quotes for Python string
            county_name = county_name.replace("'", "\\'")


        classifications[full_fips] = {
            'name': county_name,
            'cbsa': cbsa_type,
            'cbsa_name': cbsa_name
        }

    return classifications


def generate_python_file(classifications: dict, output_path: Path):
    """
    Generate Python file with CBSA classifications.

    Args:
        classifications: Classification dictionary
        output_path: Where to save the Python file
    """
    # Count classifications by type
    counts = {'metro': 0, 'micro': 0, 'rural': 0}
    for data in classifications.values():
        counts[data['cbsa']] += 1

    # Generate Python file content
    content = f'''"""
CBSA (Core-Based Statistical Area) Classifications

Maps counties to their metropolitan/micropolitan/rural status based on
Census Bureau CBSA delineation files (July 2023).

Classifications:
- Metropolitan: Urban area 50,000+ population
- Micropolitan: Urban area 10,000-49,999 population
- Rural: Neither metropolitan nor micropolitan

Generated automatically from Census Bureau delineation files.
Source: https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html
Date: July 2023

Coverage:
- Total counties: {len(classifications)}
- Metropolitan: {counts['metro']} ({counts['metro']/len(classifications)*100:.1f}%)
- Micropolitan: {counts['micro']} ({counts['micro']/len(classifications)*100:.1f}%)
- Rural: {counts['rural']} ({counts['rural']/len(classifications)*100:.1f}%)

Study states: VA, MD, WV, NC, TN, KY, DC
"""

from typing import Dict

# CBSA classifications for all counties in the study
# Format: {{FIPS: {{'name': 'County Name', 'cbsa': 'metro'|'micro'|'rural', 'cbsa_name': 'MSA Name'}}}}

CBSA_CLASSIFICATIONS = {{
'''

    # Add all classifications, sorted by FIPS
    for fips in sorted(classifications.keys()):
        data = classifications[fips]
        name = data['name']
        cbsa_type = data['cbsa']
        cbsa_name = data.get('cbsa_name')

        # Format cbsa_name for Python string (escape quotes)
        if cbsa_name:
            cbsa_name_escaped = str(cbsa_name).replace("'", "\\'")
            cbsa_name_str = f"'{cbsa_name_escaped}'"
        else:
            cbsa_name_str = 'None'

        content += f"    '{fips}': {{'name': '{name}', 'cbsa': '{cbsa_type}', 'cbsa_name': {cbsa_name_str}}},\n"

    # Add footer
    content += '''}

# Classification summary counts
CBSA_SUMMARY = {
    'total_counties': ''' + str(len(classifications)) + ''',
    'metropolitan': ''' + str(counts['metro']) + ''',
    'micropolitan': ''' + str(counts['micro']) + ''',
    'rural': ''' + str(counts['rural']) + '''
}


def get_cbsa_classification(fips: str) -> Dict:
    """
    Get CBSA classification for a county.

    Args:
        fips: 5-digit FIPS code

    Returns:
        Dictionary with classification info, or default rural if not found
    """
    return CBSA_CLASSIFICATIONS.get(fips, {
        'name': 'Unknown',
        'cbsa': 'rural',
        'cbsa_name': None
    })


def get_micropolitan_percentage(fips_list: list) -> float:
    """
    Calculate percentage of population in micropolitan areas.

    Args:
        fips_list: List of FIPS codes for a region

    Returns:
        Percentage (0-100) of area classified as micropolitan
    """
    total = len(fips_list)
    if total == 0:
        return 0.0

    micro_count = sum(1 for fips in fips_list
                      if get_cbsa_classification(fips)['cbsa'] == 'micro')

    return (micro_count / total) * 100


def classify_region_type(fips_list: list) -> str:
    """
    Classify a region as predominantly metro, micro, or rural.

    Args:
        fips_list: List of FIPS codes for a region

    Returns:
        'metro', 'micro', or 'rural'
    """
    classifications = [get_cbsa_classification(fips)['cbsa'] for fips in fips_list]

    counts = {
        'metro': classifications.count('metro'),
        'micro': classifications.count('micro'),
        'rural': classifications.count('rural')
    }

    # Return classification with highest count
    return max(counts, key=counts.get)
'''

    # Write to file
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✓ Generated {output_path}")
    print(f"  Total counties: {len(classifications)}")
    print(f"  Metropolitan: {counts['metro']} ({counts['metro']/len(classifications)*100:.1f}%)")
    print(f"  Micropolitan: {counts['micro']} ({counts['micro']/len(classifications)*100:.1f}%)")
    print(f"  Rural: {counts['rural']} ({counts['rural']/len(classifications)*100:.1f}%)")


def main():
    """Main execution."""
    print("=" * 70)
    print("GENERATING CBSA CLASSIFICATIONS")
    print("=" * 70)

    cbsa_file = project_root / 'data' / 'raw' / 'cbsa_2023.xlsx'
    output_file = project_root / 'data' / 'cbsa_classifications.py'

    print(f"\nInput file: {cbsa_file}")
    print(f"Output file: {output_file}")

    # Parse CBSA file
    print("\nParsing CBSA delineation file...")
    df = parse_cbsa_file(cbsa_file)
    print(f"  Total CBSAs: {len(df)}")

    # Create classification dictionary
    print("\nCreating classification dictionary...")
    classifications = create_classification_dict(df)
    print(f"  Study region counties: {len(classifications)}")

    # Show sample micropolitan areas
    micro_areas = {fips: data for fips, data in classifications.items() if data['cbsa'] == 'micro'}
    print(f"\nSample micropolitan areas found:")
    for fips, data in list(micro_areas.items())[:10]:
        print(f"  {fips}: {data['name']} - {data['cbsa_name']}")

    # Generate Python file
    print("\nGenerating Python file...")
    generate_python_file(classifications, output_file)

    print("\n" + "=" * 70)
    print("CBSA CLASSIFICATIONS COMPLETE")
    print("=" * 70)
    print(f"\nNext step: Run 'python scripts/aggregate_micropolitan_data.py' to recalculate micropolitan percentages")


if __name__ == '__main__':
    main()
