"""
Add county FIPS codes to regional CSV files.

This script reads county FIPS codes from processed data files and adds them
to all regional CSV files to enable regional data aggregation.
"""

import pandas as pd
from pathlib import Path
import re


def build_county_fips_lookup(data_dir: Path) -> dict:
    """
    Build a master lookup of county names to FIPS codes.

    Args:
        data_dir: Path to data/processed directory

    Returns:
        Dictionary mapping (county_name, state_fips) -> fips
    """
    # Read from census population data which has complete coverage
    pop_file = data_dir / "census_population_growth_2000_2022.csv"
    df = pd.read_csv(pop_file)

    lookup = {}

    for _, row in df.iterrows():
        fips = str(row['fips']).zfill(5)  # Ensure 5-digit FIPS
        name = row['NAME']

        # Parse "County Name, State" format
        # Handle various formats: "Kent County, Delaware" or "Kent, DE"
        match = re.match(r'^(.+?)\s+(?:County|city|parish),\s+(.+)$', name)
        if match:
            county_part = match.group(1).strip()
            state_part = match.group(2).strip()

            # Get state FIPS (first 2 digits)
            state_fips = fips[:2]

            # Store multiple formats for matching
            # Format 1: "County Name County" (e.g., "Kent County")
            county_name_full = f"{county_part} County"
            lookup[(county_name_full, state_fips)] = fips

            # Format 2: "City Name city" (e.g., "Bristol city")
            if "city" in name.lower():
                city_name_full = f"{county_part} city"
                lookup[(city_name_full, state_fips)] = fips

            # Format 3: Just the base name (e.g., "Kent")
            lookup[(county_part, state_fips)] = fips

    return lookup


def add_fips_to_regional_file(regional_file: Path, fips_lookup: dict) -> None:
    """
    Add county_fips column to a regional CSV file.

    Args:
        regional_file: Path to regional CSV file
        fips_lookup: Dictionary mapping (county_name, state_fips) -> fips
    """
    print(f"\nProcessing: {regional_file.name}")
    df = pd.read_csv(regional_file)

    # Determine the column name for counties (varies by file)
    if 'county_name' in df.columns:
        county_col = 'county_name'
    elif 'locality_name' in df.columns:
        county_col = 'locality_name'
    else:
        print(f"  ERROR: No county/locality column found in {regional_file.name}")
        return

    # Check if county_fips already exists
    if 'county_fips' in df.columns:
        print(f"  ✓ county_fips column already exists")
        return

    # Add county_fips column
    county_fips_list = []
    missing_count = 0

    for _, row in df.iterrows():
        county_name = row[county_col]
        state_fips = str(row['state_fips']).zfill(2)

        # Try to find FIPS code
        fips = None

        # Try exact match first
        if (county_name, state_fips) in fips_lookup:
            fips = fips_lookup[(county_name, state_fips)]
        else:
            # Try without "County" or "city" suffix
            base_name = county_name.replace(" County", "").replace(" city", "").strip()
            if (base_name, state_fips) in fips_lookup:
                fips = fips_lookup[(base_name, state_fips)]

        if fips:
            county_fips_list.append(fips)
        else:
            county_fips_list.append(None)
            missing_count += 1
            print(f"  WARNING: No FIPS found for '{county_name}' in state {state_fips}")

    # Add the new column
    df['county_fips'] = county_fips_list

    # Reorder columns to put county_fips after state_fips
    cols = df.columns.tolist()
    state_fips_idx = cols.index('state_fips')
    cols.remove('county_fips')
    cols.insert(state_fips_idx + 1, 'county_fips')
    df = df[cols]

    # Save the updated file
    df.to_csv(regional_file, index=False)

    print(f"  ✓ Added county_fips column ({len(df)} rows, {missing_count} missing)")


def main():
    """Add FIPS codes to all regional CSV files."""
    # Get project paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "processed"
    regions_dir = project_root / "data" / "regions"

    print("=" * 80)
    print("ADDING COUNTY FIPS CODES TO REGIONAL CSV FILES")
    print("=" * 80)

    # Build master FIPS lookup
    print("\n1. Building master county FIPS lookup...")
    fips_lookup = build_county_fips_lookup(data_dir)
    print(f"   ✓ Loaded {len(fips_lookup)} county FIPS mappings")

    # Process all regional CSV files
    print("\n2. Processing regional CSV files...")
    regional_files = sorted(regions_dir.glob("*.csv"))

    for regional_file in regional_files:
        add_fips_to_regional_file(regional_file, fips_lookup)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"\nProcessed {len(regional_files)} regional files")
    print()


if __name__ == "__main__":
    main()
