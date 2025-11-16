"""
Component Index 3, Measure 3.3: Life Expectancy - Data Collection Script

Downloads and processes life expectancy data from County Health Rankings & Roadmaps
via Zenodo API for all counties in 10 states.

Data Source: County Health Rankings & Roadmaps 2025 Release
Zenodo DOI: 10.5281/zenodo.17584421
States: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
"""

import sys
from pathlib import Path
import json
import pandas as pd
import requests
import zipfile
import io
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import STATE_FIPS, RAW_DATA_DIR, PROCESSED_DATA_DIR


def download_chr_data(year=2025):
    """
    Download County Health Rankings data from Zenodo.

    Args:
        year: Year of data release (default: 2025)

    Returns:
        BytesIO object containing the ZIP file
    """
    print(f"\nDownloading County Health Rankings {year} data from Zenodo...")
    print("-" * 60)

    # Zenodo API URL for 2025 data
    url = f"https://zenodo.org/api/records/17584421/files/{year}.zip/content"

    print(f"URL: {url}")
    print(f"Downloading... (this may take a minute, ~52 MB)")

    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()

        file_size_mb = len(response.content) / (1024 * 1024)
        print(f"✓ Downloaded {file_size_mb:.1f} MB")

        return io.BytesIO(response.content)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download CHR data: {str(e)}")


def extract_and_find_life_expectancy(zip_data):
    """
    Extract ZIP file and locate life expectancy data.

    Args:
        zip_data: BytesIO object containing ZIP file

    Returns:
        DataFrame with life expectancy data
    """
    print("\nExtracting ZIP file and locating life expectancy data...")
    print("-" * 60)

    try:
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            # List all files in the ZIP
            file_list = zip_ref.namelist()
            print(f"ZIP contains {len(file_list)} files")

            # Look for analytic data file (usually contains all measures)
            # Common patterns: analytic_data, chr_analytic, data
            analytic_files = [
                f for f in file_list
                if ('analytic' in f.lower() or 'data' in f.lower())
                and (f.endswith('.csv') or f.endswith('.xlsx'))
                and not f.startswith('__MACOSX')
            ]

            print(f"\nFound {len(analytic_files)} potential data files:")
            for f in analytic_files[:10]:  # Show first 10
                print(f"  - {f}")

            if not analytic_files:
                # If no analytic files, look for any CSV or Excel files
                data_files = [
                    f for f in file_list
                    if (f.endswith('.csv') or f.endswith('.xlsx'))
                    and not f.startswith('__MACOSX')
                ]
                print(f"\nNo 'analytic' files found. Found {len(data_files)} CSV/Excel files:")
                for f in data_files[:10]:
                    print(f"  - {f}")
                analytic_files = data_files

            if not analytic_files:
                raise Exception("No CSV or Excel data files found in ZIP")

            # Try each file to find life expectancy data
            for filename in analytic_files:
                print(f"\nTrying to read: {filename}")

                try:
                    with zip_ref.open(filename) as f:
                        if filename.endswith('.csv'):
                            df = pd.read_csv(f, encoding='utf-8', low_memory=False)
                        elif filename.endswith('.xlsx'):
                            df = pd.read_excel(f, engine='openpyxl')
                        else:
                            continue

                    print(f"  Columns: {len(df.columns)}")
                    print(f"  Rows: {len(df)}")

                    # Look for life expectancy columns
                    # Common patterns: life_expectancy, v147, lifespan, life expectancy
                    le_columns = [
                        col for col in df.columns
                        if any(pattern in str(col).lower() for pattern in [
                            'life expectancy', 'life_expectancy', 'lifespan', 'v147'
                        ])
                    ]

                    if le_columns:
                        print(f"  ✓ Found life expectancy columns: {le_columns}")
                        print(f"\nUsing file: {filename}")
                        return df, filename, le_columns

                except Exception as e:
                    print(f"  ✗ Error reading file: {e}")
                    continue

            raise Exception("Could not find life expectancy data in any file")

    except zipfile.BadZipFile:
        raise Exception("Downloaded file is not a valid ZIP file")


def process_life_expectancy(df, le_columns, state_fips_dict):
    """
    Process life expectancy data and filter to target states.

    Args:
        df: DataFrame with CHR data
        le_columns: List of life expectancy column names
        state_fips_dict: Dictionary of state abbreviations to FIPS codes

    Returns:
        Processed DataFrame with life expectancy data
    """
    print("\nProcessing life expectancy data...")
    print("-" * 60)

    # Identify FIPS columns
    fips_columns = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in [
            'fips', 'statecode', 'countycode', 'state_fips', 'county_fips'
        ])
    ]

    print(f"FIPS-related columns: {fips_columns}")
    print(f"Life expectancy columns: {le_columns}")

    # Try to construct 5-digit FIPS code
    # Check for 5-digit FIPS column (various naming patterns)
    fips_5digit_cols = [c for c in df.columns if '5-digit' in c.lower() and 'fips' in c.lower()]
    if fips_5digit_cols:
        df['full_fips'] = df[fips_5digit_cols[0]].astype(str).str.zfill(5)
    elif any('fipscode' in c.lower() for c in df.columns):
        fips_col = next((c for c in df.columns if 'fipscode' in c.lower()), None)
        df['full_fips'] = df[fips_col].astype(str).str.zfill(5)
    else:
        # Look for state and county FIPS columns (case-insensitive)
        state_cols = [c for c in df.columns if 'state' in c.lower() and 'fips' in c.lower()]
        county_cols = [c for c in df.columns if 'county' in c.lower() and 'fips' in c.lower()]

        if state_cols and county_cols:
            df['full_fips'] = (
                df[state_cols[0]].astype(str).str.zfill(2) +
                df[county_cols[0]].astype(str).str.zfill(3)
            )
        else:
            raise Exception(f"Cannot determine FIPS code structure. Available columns: {list(df.columns)[:20]}")

    # Extract state FIPS (first 2 digits)
    df['state_fips'] = df['full_fips'].str[:2]

    # Filter to target states
    target_state_fips = list(state_fips_dict.values())
    filtered_df = df[df['state_fips'].isin(target_state_fips)].copy()

    print(f"\n✓ Filtered from {len(df)} to {len(filtered_df)} counties in target states")

    # Select relevant columns
    # Use the first life expectancy column found (usually the main measure)
    le_col = le_columns[0]

    columns_to_keep = ['full_fips', 'state_fips'] + fips_columns + [le_col]

    # Add county name if available
    name_columns = [
        col for col in df.columns
        if any(pattern in str(col).lower() for pattern in ['name', 'county_name', 'county name'])
    ]
    if name_columns:
        columns_to_keep.append(name_columns[0])

    # Keep only columns that exist
    columns_to_keep = [c for c in columns_to_keep if c in filtered_df.columns]
    processed_df = filtered_df[columns_to_keep].copy()

    # Rename life expectancy column to standard name
    processed_df = processed_df.rename(columns={le_col: 'life_expectancy'})

    # Convert life expectancy to numeric
    processed_df['life_expectancy'] = pd.to_numeric(
        processed_df['life_expectancy'],
        errors='coerce'
    )

    # Summary statistics
    print(f"\nLife Expectancy Statistics:")
    print(f"  Mean: {processed_df['life_expectancy'].mean():.2f} years")
    print(f"  Median: {processed_df['life_expectancy'].median():.2f} years")
    print(f"  Min: {processed_df['life_expectancy'].min():.2f} years")
    print(f"  Max: {processed_df['life_expectancy'].max():.2f} years")
    print(f"  Null values: {processed_df['life_expectancy'].isna().sum()}")

    # State breakdown
    print(f"\nCounties by state:")
    state_counts = processed_df['state_fips'].value_counts().sort_index()
    for state_fips, count in state_counts.items():
        state_abbr = [k for k, v in state_fips_dict.items() if v == state_fips]
        state_name = state_abbr[0] if state_abbr else 'Unknown'
        print(f"  {state_name} ({state_fips}): {count} counties")

    return processed_df


def main():
    """Main execution function."""
    print("=" * 80)
    print("COMPONENT INDEX 3, MEASURE 3.3: LIFE EXPECTANCY - DATA COLLECTION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configuration
    YEAR = 2025

    try:
        # Step 1: Download data from Zenodo
        zip_data = download_chr_data(YEAR)

        # Step 2: Extract and find life expectancy data
        df, source_filename, le_columns = extract_and_find_life_expectancy(zip_data)

        # Step 3: Process and filter data
        processed_df = process_life_expectancy(df, le_columns, STATE_FIPS)

        # Step 4: Save raw data (save the source file info)
        raw_dir = RAW_DATA_DIR / 'chr'
        raw_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            'source': 'County Health Rankings & Roadmaps',
            'zenodo_doi': '10.5281/zenodo.17584421',
            'year': YEAR,
            'download_date': datetime.now().isoformat(),
            'source_file': source_filename,
            'life_expectancy_columns': le_columns,
            'records_downloaded': len(df),
            'records_filtered': len(processed_df)
        }

        metadata_file = raw_dir / f'chr_life_expectancy_{YEAR}_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"\n✓ Saved metadata: {metadata_file}")

        # Step 5: Save processed data
        output_file = PROCESSED_DATA_DIR / f'chr_life_expectancy_{YEAR}.csv'
        processed_df.to_csv(output_file, index=False)
        print(f"✓ Saved processed data: {output_file}")

        # Step 6: Update collection summary
        summary = {
            'collection_date': datetime.now().isoformat(),
            'measure': '3.3_life_expectancy',
            'status': 'complete',
            'source': 'County Health Rankings & Roadmaps (Zenodo)',
            'year': YEAR,
            'records': len(processed_df),
            'states': len(processed_df['state_fips'].unique()),
            'mean_life_expectancy': float(processed_df['life_expectancy'].mean()),
            'null_values': int(processed_df['life_expectancy'].isna().sum())
        }

        summary_file = PROCESSED_DATA_DIR / 'life_expectancy_collection_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Saved summary: {summary_file}")

        print("\n" + "=" * 80)
        print("COLLECTION SUMMARY")
        print("=" * 80)
        print(f"Total records collected: {len(processed_df)}")
        print(f"States covered: {len(processed_df['state_fips'].unique())}")
        print(f"Mean life expectancy: {processed_df['life_expectancy'].mean():.2f} years")
        print(f"Data completeness: {(1 - processed_df['life_expectancy'].isna().mean()) * 100:.1f}%")
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
