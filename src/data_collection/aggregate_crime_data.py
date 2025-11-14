"""
Aggregate FBI UCR RETA Crime Data to County Level

Parses RETA data, aggregates from agencies to counties using ORI-to-FIPS mapping,
and calculates crime rates using Census population data.
"""

import json
import logging
from pathlib import Path
from typing import Dict
import pandas as pd

from src.parsers.fbi_ucr_parser import extract_crime_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_ori_to_fips_mapping(mapping_file: Path) -> Dict[str, str]:
    """Load ORI-to-FIPS mapping from JSON file."""
    logger.info(f"Loading ORI-to-FIPS mapping from {mapping_file}")

    with open(mapping_file, 'r') as f:
        mapping = json.load(f)

    logger.info(f"Loaded mapping for {len(mapping)} agencies")
    return mapping


def aggregate_crime_to_counties(
    reta_file: Path,
    ori_mapping_file: Path
) -> Dict[str, Dict]:
    """
    Aggregate crime data from agencies to counties.

    Args:
        reta_file: Path to RETA master file
        ori_mapping_file: Path to ORI-to-FIPS mapping JSON

    Returns:
        Dictionary mapping FIPS codes to aggregated crime data
    """
    # Load ORI-to-FIPS mapping
    ori_to_fips = load_ori_to_fips_mapping(ori_mapping_file)

    # Parse RETA data and aggregate to counties
    logger.info("Parsing RETA data and aggregating to counties...")
    county_data = extract_crime_data(reta_file, ori_to_fips)

    return county_data


def save_county_crime_data(county_data: Dict[str, Dict], output_file: Path):
    """Save county-level crime data to JSON."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(county_data, f, indent=2)

    logger.info(f"Saved county crime data to {output_file}")


def export_to_csv(county_data: Dict[str, Dict], output_file: Path):
    """Export county crime data to CSV for analysis."""
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(county_data, orient='index')

    # Save to CSV
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    logger.info(f"Exported county crime data to {output_file}")


def print_statistics(county_data: Dict[str, Dict]):
    """Print summary statistics."""
    print("\n" + "="*60)
    print("County-Level Crime Data Statistics")
    print("="*60)

    # Total counties
    print(f"Total counties with data: {len(county_data)}")

    # By state
    state_counts = {}
    for fips, data in county_data.items():
        state = data.get('state', 'Unknown')
        if state not in state_counts:
            state_counts[state] = 0
        state_counts[state] += 1

    print("\nCounties by state:")
    for state in sorted(state_counts.keys()):
        print(f"  {state}: {state_counts[state]}")

    # Total crimes
    total_violent = sum(d.get('violent_crime', 0) for d in county_data.values())
    total_property = sum(d.get('property_crime', 0) for d in county_data.values())

    print(f"\nTotal crimes:")
    print(f"  Violent crimes: {total_violent:,}")
    print(f"  Property crimes: {total_property:,}")

    # Sample data
    print(f"\nSample county data (first 3 counties):")
    for i, (fips, data) in enumerate(list(county_data.items())[:3]):
        print(f"\n  FIPS: {fips} ({data['state']})")
        print(f"    Agencies: {len(data['agencies'])}")
        print(f"    Population: {data.get('population', 0):,}")
        print(f"    Violent crimes: {data.get('violent_crime', 0):,}")
        print(f"    Property crimes: {data.get('property_crime', 0):,}")


def main():
    """Main execution."""
    # File paths
    reta_file = Path('data/crime/raw/2024_RETA_NATIONAL_MASTER_FILE.txt')
    ori_mapping_file = Path('data/processed/ori_to_fips_mapping.json')
    output_json = Path('data/processed/county_crime_data.json')
    output_csv = Path('data/processed/county_crime_data.csv')

    # Check inputs
    if not reta_file.exists():
        logger.error(f"RETA file not found: {reta_file}")
        return

    if not ori_mapping_file.exists():
        logger.error(f"ORI mapping file not found: {ori_mapping_file}")
        logger.info("Run build_ori_mapping_from_reta.py first to create the mapping")
        return

    # Aggregate data
    county_data = aggregate_crime_to_counties(reta_file, ori_mapping_file)

    # Save results
    save_county_crime_data(county_data, output_json)
    export_to_csv(county_data, output_csv)

    # Print statistics
    print_statistics(county_data)

    print("\n" + "="*60)
    print("Crime data aggregation complete!")
    print("="*60)
    print(f"JSON output: {output_json}")
    print(f"CSV output: {output_csv}")


if __name__ == '__main__':
    main()
