"""
Component Index 7: Quality of Life - Data Collection Script

Collects 6 of 8 measures for Component Index 7 for all counties in 10 states:
7.1 Commute Time (Census ACS S0801)
7.2 Percent of Housing Built Pre-1960 (Census ACS DP04)
7.3 Relative Weekly Wage (BLS QCEW)
7.6 Climate Amenities (USDA ERS Natural Amenities Scale)
7.7 Healthcare Access (Census CBP NAICS 621+622)
7.8 Count of National Parks (NPS API with boundaries)

States: VA, PA, MD, DE, WV, KY, TN, NC, SC, GA
"""

import sys
from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
from datetime import datetime
import requests

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import STATE_FIPS, RAW_DATA_DIR, PROCESSED_DATA_DIR
from api_clients.census_client import CensusClient
from api_clients.cbp_client import CBPClient
from api_clients.qcew_client import QCEWClient
from api_clients.nps_client import NPSClient


def collect_commute_time(census_client, year, state_fips_list):
    """
    Collect average commute time data (Measure 7.1).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end (e.g., 2022)
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with commute time data
    """
    print(f"\nCollecting Census ACS {year} Commute Time (Measure 7.1)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_commute_time(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_commute_time_{year}_{state_name}.json"
            census_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrame
    df = pd.DataFrame(all_data)
    print(f"\n✓ Total records: {len(df)}")

    return df


def collect_housing_age(census_client, year, state_fips_list):
    """
    Collect housing age data for pre-1960 calculation (Measure 7.2).

    Args:
        census_client: CensusClient instance
        year: Year of ACS 5-year period end
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with housing age data
    """
    print(f"\nCollecting Census ACS {year} Housing Age (Measure 7.2)...")
    print("-" * 60)

    all_data = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            response = census_client.get_housing_age(year, state_fips=state_fips)

            # Save raw response
            filename = f"census_housing_age_{year}_{state_name}.json"
            census_client.save_response(response, filename)

            # Convert to dict and add to list
            parsed = census_client.parse_response_to_dict(response)
            all_data.extend(parsed)
            print(f"    ✓ Retrieved {len(parsed)} counties")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrame
    df = pd.DataFrame(all_data)
    print(f"\n✓ Total records: {len(df)}")

    return df


def collect_relative_weekly_wage(qcew_client, year, state_fips_list):
    """
    Collect weekly wage data for relative wage calculation (Measure 7.3).

    Args:
        qcew_client: QCEWClient instance
        year: Year of data
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with weekly wage data (county and state level)
    """
    print(f"\nCollecting BLS QCEW {year} Weekly Wage Data (Measure 7.3)...")
    print("-" * 60)

    # Get private employment and wages for all states at once
    print("  Fetching QCEW data for all states...")
    try:
        # QCEW client method takes a list of state FIPS codes
        response = qcew_client.get_private_employment_wages(
            year=year,
            state_fips_list=state_fips_list
        )

        print(f"    ✓ Retrieved {len(response)} counties")

    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        response = []

    # Create DataFrame
    df = pd.DataFrame(response)

    # Calculate weekly wage from annual data
    if not df.empty and 'avg_annual_pay' in df.columns:
        df['weekly_wage'] = df['avg_annual_pay'] / 52

    print(f"\n✓ Total records: {len(df)}")

    return df


def collect_healthcare_employment(cbp_client, year, state_fips_list):
    """
    Collect healthcare employment data (Measure 7.7).

    Args:
        cbp_client: CBPClient instance
        year: Year of CBP data
        state_fips_list: List of state FIPS codes

    Returns:
        DataFrame with healthcare employment data
    """
    print(f"\nCollecting Census CBP {year} Healthcare Employment (Measure 7.7)...")
    print("-" * 60)

    all_ambulatory = []
    all_hospitals = []

    for state_name, state_fips in STATE_FIPS.items():
        if state_fips not in state_fips_list:
            continue

        print(f"  Fetching {state_name} (FIPS {state_fips})...")
        try:
            results = cbp_client.get_healthcare_employment(year, state_fips=state_fips)

            # Process ambulatory data (NAICS 621)
            if results['ambulatory']:
                filename = f"cbp_healthcare_621_{year}_{state_name}.json"
                cbp_client.save_response(results['ambulatory'], filename)
                parsed = cbp_client.parse_response_to_dict(results['ambulatory'])
                all_ambulatory.extend(parsed)

            # Process hospitals data (NAICS 622)
            if results['hospitals']:
                filename = f"cbp_healthcare_622_{year}_{state_name}.json"
                cbp_client.save_response(results['hospitals'], filename)
                parsed = cbp_client.parse_response_to_dict(results['hospitals'])
                all_hospitals.extend(parsed)

            print(f"    ✓ Retrieved ambulatory: {len(parsed) if results['ambulatory'] else 0}, hospitals: {len(parsed) if results['hospitals'] else 0}")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # Create DataFrames
    df_ambulatory = pd.DataFrame(all_ambulatory)
    df_hospitals = pd.DataFrame(all_hospitals)

    # Merge the two dataframes by county
    # Both should have state, county, NAME columns
    if not df_ambulatory.empty and not df_hospitals.empty:
        # Rename EMP columns to be specific
        df_ambulatory['EMP_ambulatory'] = pd.to_numeric(df_ambulatory['EMP'], errors='coerce')
        df_hospitals['EMP_hospitals'] = pd.to_numeric(df_hospitals['EMP'], errors='coerce')

        # Merge on state and county
        df = pd.merge(
            df_ambulatory[['state', 'county', 'NAME', 'EMP_ambulatory']],
            df_hospitals[['state', 'county', 'EMP_hospitals']],
            on=['state', 'county'],
            how='outer'
        )

        # Fill NaN with 0 (counties that don't have hospitals or ambulatory facilities)
        df['EMP_ambulatory'] = df['EMP_ambulatory'].fillna(0)
        df['EMP_hospitals'] = df['EMP_hospitals'].fillna(0)

        # Calculate total healthcare employment
        df['total_healthcare_employment'] = df['EMP_ambulatory'] + df['EMP_hospitals']

        print(f"\n✓ Total records: {len(df)}")
        return df
    else:
        print("\n✗ Error: Missing data for ambulatory or hospitals")
        return pd.DataFrame()


def load_county_boundaries(cache_file=None):
    """
    Load county boundary data from cache (Component 6).

    Args:
        cache_file: Path to cached county boundaries pickle file

    Returns:
        GeoDataFrame: County boundaries with FIPS codes
    """
    if cache_file is None:
        cache_file = RAW_DATA_DIR / 'usgs' / 'cache' / 'county_boundaries_2024.pkl'

    if not cache_file.exists():
        print(f"  County boundaries cache not found at {cache_file}")
        print(f"  Downloading from Census TIGER...")

        # Download county boundaries
        import requests

        url = "https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip"

        # Download ZIP file
        print(f"    Downloading {url}...")
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        # Save ZIP temporarily
        zip_path = cache_file.parent / 'temp_counties.zip'
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print(f"    ✓ Downloaded {len(response.content) / (1024*1024):.1f} MB")

        # Load with geopandas
        counties_gdf = gpd.read_file(f"zip://{zip_path}")

        # Cache for future use
        counties_gdf.to_pickle(cache_file)
        print(f"    ✓ Cached county boundaries to {cache_file}")

        # Clean up temp file
        zip_path.unlink()
        print(f"    ✓ Cleaned up temporary file")
    else:
        print(f"  Using cached county boundaries from {cache_file}")
        counties_gdf = pd.read_pickle(cache_file)

    return counties_gdf


def collect_climate_amenities(state_fips_list):
    """
    Download and process USDA ERS Natural Amenities Scale data (Measure 7.6).

    This dataset contains a composite index of climate amenities based on:
    - Mean January temperature (warm winter)
    - Mean January days with sun (winter sun)
    - Mean July temperature (temperate summer)
    - Mean July relative humidity (low summer humidity)
    - Topographic variation
    - Water area

    Data is based on 1941-1970 climate normals (static data, last updated 1999).

    Args:
        state_fips_list: List of state FIPS codes to filter for

    Returns:
        DataFrame with natural amenities scale data for counties in our 10 states
    """
    print(f"\nDownloading USDA ERS Natural Amenities Scale (Measure 7.6)...")
    print("-" * 60)

    # USDA ERS download URL
    url = 'https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/52201/natamenf_1_.xls?v=83168'

    # Create raw data directory
    raw_dir = RAW_DATA_DIR / 'usda_ers'
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Download file
    print(f"  Downloading from: {url}")
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        # Save raw XLS file
        xls_path = raw_dir / 'natural_amenities_scale.xls'
        with open(xls_path, 'wb') as f:
            f.write(response.content)

        print(f"    ✓ Downloaded {len(response.content) / (1024*1024):.2f} MB")
        print(f"    ✓ Saved to: {xls_path}")

    except Exception as e:
        print(f"    ✗ Error downloading: {e}")
        raise

    # Read XLS file with pandas
    # Note: First 104 rows contain documentation, row 104 has headers
    print(f"\n  Reading XLS file...")
    try:
        df = pd.read_excel(xls_path, skiprows=104)
        print(f"    ✓ Loaded {len(df)} counties")

    except Exception as e:
        print(f"    ✗ Error reading XLS: {e}")
        raise

    # Filter to our 10 states
    print(f"\n  Filtering to our 10 states...")

    # Convert FIPS to string with leading zeros
    df['fips_str'] = df['FIPS Code'].astype(str).str.zfill(5)
    df['state_fips'] = df['fips_str'].str[:2]
    df['county_fips'] = df['fips_str'].str[2:]

    # Filter to our states
    df_filtered = df[df['state_fips'].isin(state_fips_list)].copy()

    print(f"    ✓ Filtered to {len(df_filtered)} counties in our 10 states")

    # Save filtered data as JSON
    json_path = raw_dir / 'natural_amenities_scale_filtered.json'
    df_filtered.to_json(json_path, orient='records', indent=2)
    print(f"    ✓ Saved filtered data to: {json_path}")

    print(f"\n✓ Total records: {len(df_filtered)}")

    return df_filtered


def collect_nps_parks(nps_client, state_codes, state_fips_list):
    """
    Collect national parks data and map to counties (Measure 7.8).

    Args:
        nps_client: NPSClient instance
        state_codes: List of 2-letter state codes
        state_fips_list: List of state FIPS codes

    Returns:
        tuple: (county_counts DataFrame, park_assignments DataFrame, raw_park_data list)
    """
    print(f"\nCollecting NPS Parks and Boundaries (Measure 7.8)...")
    print("-" * 60)

    # Fetch all parks for our states
    all_parks = nps_client.get_all_parks(state_codes=state_codes)

    parks_with_boundaries = []
    parks_with_points_only = []
    park_raw_data = []

    print(f"\n  Fetching boundaries for {len(all_parks)} parks...")

    for i, park in enumerate(all_parks, 1):
        park_code = park.get('parkCode', '')

        # Parse basic location info
        location = nps_client.parse_park_location(park)
        park_raw_data.append(location)

        # Try to fetch boundary geometry
        boundary = nps_client.get_park_boundary(park_code)

        if boundary and 'geometry' in boundary:
            # Park has boundary data
            location['has_boundary'] = True
            location['geometry'] = boundary['geometry']
            parks_with_boundaries.append(location)
            if i % 5 == 0:
                print(f"    Progress: {i}/{len(all_parks)} parks (boundaries: {len(parks_with_boundaries)}, points: {len(parks_with_points_only)})")
        elif location['latitude'] and location['longitude']:
            # Fall back to point location
            location['has_boundary'] = False
            parks_with_points_only.append(location)
            if i % 5 == 0:
                print(f"    Progress: {i}/{len(all_parks)} parks (boundaries: {len(parks_with_boundaries)}, points: {len(parks_with_points_only)})")

    print(f"\n  ✓ Parks with boundaries: {len(parks_with_boundaries)}")
    print(f"  ✓ Parks with points only: {len(parks_with_points_only)}")
    print(f"  Total parks: {len(parks_with_boundaries) + len(parks_with_points_only)}")

    # Load county boundaries
    print("\n  Loading county boundaries...")
    counties_gdf = load_county_boundaries()
    print(f"  ✓ Loaded {len(counties_gdf)} county boundaries")

    # Filter counties to our 10 states
    counties_gdf = counties_gdf[counties_gdf['STATEFP'].isin(state_fips_list)].copy()
    print(f"  Counties in scope: {len(counties_gdf)}")

    # Ensure CRS is WGS84
    if counties_gdf.crs != "EPSG:4326":
        counties_gdf = counties_gdf.to_crs("EPSG:4326")

    all_park_county_assignments = []

    # Process parks with boundaries (polygon intersection)
    if parks_with_boundaries:
        print(f"\n  Processing {len(parks_with_boundaries)} parks with boundaries...")

        for park in parks_with_boundaries:
            try:
                # Convert GeoJSON geometry to Shapely geometry
                park_geom = shape(park['geometry'])

                # Find all counties that intersect with this park
                intersecting = counties_gdf[counties_gdf.intersects(park_geom)].copy()

                for _, county in intersecting.iterrows():
                    all_park_county_assignments.append({
                        'park_code': park['park_code'],
                        'park_name': park['park_name'],
                        'designation': park['designation'],
                        'states': park['states'],
                        'has_boundary': True,
                        'STATEFP': county['STATEFP'],
                        'COUNTYFP': county['COUNTYFP'],
                        'county_name': county['NAME']
                    })

            except Exception as e:
                print(f"    Error processing boundary for {park['park_name']}: {e}")

        print(f"    ✓ Mapped to {len(all_park_county_assignments)} park-county assignments")

    # Process parks with points only (point-in-polygon)
    if parks_with_points_only:
        print(f"\n  Processing {len(parks_with_points_only)} parks with points only...")

        park_points = []
        park_data = []

        for park in parks_with_points_only:
            if park['latitude'] and park['longitude']:
                point = Point(park['longitude'], park['latitude'])
                park_points.append(point)
                park_data.append(park)

        if park_points:
            parks_gdf = gpd.GeoDataFrame(
                park_data,
                geometry=park_points,
                crs="EPSG:4326"
            )

            # Spatial join: assign parks to counties
            parks_with_counties = gpd.sjoin(
                parks_gdf,
                counties_gdf[['STATEFP', 'COUNTYFP', 'NAME', 'geometry']],
                how='left',
                predicate='within'
            )

            # Check for unmapped parks
            unmapped = parks_with_counties[parks_with_counties['STATEFP'].isna()]
            if len(unmapped) > 0:
                print(f"    Warning: {len(unmapped)} parks could not be mapped:")
                for idx, park in unmapped.iterrows():
                    print(f"      - {park['park_name']} ({park['park_code']})")

            # Add mapped parks to assignments
            for idx, row in parks_with_counties.iterrows():
                if pd.notna(row['STATEFP']):
                    all_park_county_assignments.append({
                        'park_code': row['park_code'],
                        'park_name': row['park_name'],
                        'designation': row['designation'],
                        'states': row['states'],
                        'has_boundary': False,
                        'STATEFP': row['STATEFP'],
                        'COUNTYFP': row['COUNTYFP'],
                        'county_name': row['NAME']
                    })

            print(f"    ✓ Mapped {len(parks_with_counties[parks_with_counties['STATEFP'].notna()])} parks")

    # Create DataFrame of all park-county assignments
    park_assignments_df = pd.DataFrame(all_park_county_assignments)
    print(f"\n  Total park-county assignments: {len(park_assignments_df)}")

    # Count unique parks per county
    if not park_assignments_df.empty:
        county_park_counts = park_assignments_df.groupby(['STATEFP', 'COUNTYFP']).agg({
            'park_code': 'count'
        }).reset_index()
        county_park_counts.columns = ['STATEFP', 'COUNTYFP', 'park_count']

        # Add county names
        county_names = counties_gdf[['STATEFP', 'COUNTYFP', 'NAME']].drop_duplicates()
        county_park_counts = county_park_counts.merge(
            county_names,
            on=['STATEFP', 'COUNTYFP'],
            how='left'
        )
    else:
        county_park_counts = pd.DataFrame(columns=['STATEFP', 'COUNTYFP', 'park_count', 'NAME'])

    # Create full county list (all 802 counties) with 0 counts for counties without parks
    all_counties = counties_gdf[['STATEFP', 'COUNTYFP', 'NAME']].copy()
    all_counties = all_counties.merge(
        county_park_counts[['STATEFP', 'COUNTYFP', 'park_count']],
        on=['STATEFP', 'COUNTYFP'],
        how='left'
    )
    all_counties['park_count'] = all_counties['park_count'].fillna(0).astype(int)

    print(f"\n  Counties with parks: {len(county_park_counts)}")
    print(f"  Counties without parks: {len(all_counties[all_counties['park_count'] == 0])}")
    print(f"  Max parks in a county: {all_counties['park_count'].max()}")

    print(f"\n✓ Total records: {len(all_counties)}")

    return all_counties, park_assignments_df, park_raw_data


def process_and_save_data(
    commute_df, housing_df, wage_df, climate_df, healthcare_df, parks_df, park_details_df, nps_raw_data,
    acs_year, cbp_year, qcew_year
):
    """
    Process collected data and save to CSV files.

    Args:
        commute_df: DataFrame with commute time data
        housing_df: DataFrame with housing age data
        wage_df: DataFrame with weekly wage data
        climate_df: DataFrame with climate amenities data
        healthcare_df: DataFrame with healthcare employment data
        parks_df: DataFrame with park counts by county
        park_details_df: DataFrame with park-to-county mapping
        nps_raw_data: Raw NPS API park data
        acs_year: Year of ACS data
        cbp_year: Year of CBP data
        qcew_year: Year of QCEW data

    Returns:
        dict: Summary statistics
    """
    print("\nProcessing and saving Component 7 data...")
    print("=" * 60)

    processed_dir = PROCESSED_DATA_DIR
    processed_dir.mkdir(parents=True, exist_ok=True)

    summary = {}

    # Process 7.1: Commute Time
    if not commute_df.empty:
        commute_df['mean_commute_time'] = pd.to_numeric(
            commute_df['S0801_C01_046E'], errors='coerce'
        )

        output_file = processed_dir / f"census_commute_time_{acs_year}.csv"
        commute_df[['state', 'county', 'NAME', 'mean_commute_time']].to_csv(
            output_file, index=False
        )
        print(f"✓ Saved: {output_file}")

        summary['7.1_commute_time'] = {
            'records': len(commute_df),
            'mean': float(commute_df['mean_commute_time'].mean()),
            'min': float(commute_df['mean_commute_time'].min()),
            'max': float(commute_df['mean_commute_time'].max())
        }

    # Process 7.2: Housing Age (Pre-1960)
    if not housing_df.empty:
        housing_df['total_units'] = pd.to_numeric(housing_df['DP04_0033E'], errors='coerce')
        housing_df['built_1939_earlier'] = pd.to_numeric(housing_df['DP04_0035E'], errors='coerce')
        housing_df['built_1940_1949'] = pd.to_numeric(housing_df['DP04_0036E'], errors='coerce')
        housing_df['built_1950_1959'] = pd.to_numeric(housing_df['DP04_0037E'], errors='coerce')

        housing_df['units_pre_1960'] = (
            housing_df['built_1939_earlier'] +
            housing_df['built_1940_1949'] +
            housing_df['built_1950_1959']
        )
        housing_df['pct_pre_1960'] = (
            housing_df['units_pre_1960'] / housing_df['total_units'] * 100
        )

        output_file = processed_dir / f"census_housing_pre1960_{acs_year}.csv"
        housing_df[['state', 'county', 'NAME', 'pct_pre_1960', 'total_units', 'units_pre_1960']].to_csv(
            output_file, index=False
        )
        print(f"✓ Saved: {output_file}")

        summary['7.2_housing_pre1960'] = {
            'records': len(housing_df),
            'mean': float(housing_df['pct_pre_1960'].mean()),
            'min': float(housing_df['pct_pre_1960'].min()),
            'max': float(housing_df['pct_pre_1960'].max())
        }

    # Process 7.3: Relative Weekly Wage
    if not wage_df.empty:
        # Extract state FIPS from area_fips (first 2 digits)
        wage_df['area_fips_str'] = wage_df['area_fips'].astype(str).str.zfill(5)
        wage_df['state_fips'] = wage_df['area_fips_str'].str[:2]
        wage_df['county_fips'] = wage_df['area_fips_str'].str[2:]

        # Calculate state-level average wages
        state_wages = wage_df.groupby('state_fips')['weekly_wage'].mean().reset_index()
        state_wages.columns = ['state_fips', 'state_avg_weekly_wage']

        # Merge state average back to county data
        wage_df = wage_df.merge(state_wages, on='state_fips', how='left')

        # Calculate relative wage
        wage_df['relative_weekly_wage'] = (
            wage_df['weekly_wage'] / wage_df['state_avg_weekly_wage']
        )

        output_file = processed_dir / f"qcew_relative_weekly_wage_{qcew_year}.csv"
        wage_df[[
            'area_fips', 'state_fips', 'county_fips',
            'weekly_wage', 'state_avg_weekly_wage', 'relative_weekly_wage'
        ]].to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        summary['7.3_relative_wage'] = {
            'records': len(wage_df),
            'mean': float(wage_df['relative_weekly_wage'].mean()),
            'min': float(wage_df['relative_weekly_wage'].min()),
            'max': float(wage_df['relative_weekly_wage'].max())
        }

    # Process 7.6: Climate Amenities
    if not climate_df.empty:
        output_file = processed_dir / 'usda_ers_natural_amenities_scale.csv'
        climate_df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        # Check if 'Scale' column exists (composite amenities index)
        if 'Scale' in climate_df.columns:
            summary['7.6_climate_amenities'] = {
                'records': len(climate_df),
                'mean': float(climate_df['Scale'].mean()),
                'min': float(climate_df['Scale'].min()),
                'max': float(climate_df['Scale'].max())
            }
        else:
            summary['7.6_climate_amenities'] = {
                'records': len(climate_df),
                'note': 'Amenities scale column not found in data'
            }

    # Process 7.7: Healthcare Access
    if not healthcare_df.empty:
        output_file = processed_dir / f"cbp_healthcare_employment_{cbp_year}.csv"
        healthcare_df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        summary['7.7_healthcare_employment'] = {
            'records': len(healthcare_df),
            'mean': float(healthcare_df['total_healthcare_employment'].mean()),
            'min': float(healthcare_df['total_healthcare_employment'].min()),
            'max': float(healthcare_df['total_healthcare_employment'].max())
        }

    # Process 7.8: National Parks
    if not parks_df.empty:
        # Save county-level park counts
        output_file = processed_dir / 'nps_park_counts_by_county.csv'
        parks_df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        # Save detailed park-to-county mapping
        if not park_details_df.empty:
            output_file = processed_dir / 'nps_parks_county_mapping.csv'
            park_details_df.to_csv(output_file, index=False)
            print(f"✓ Saved: {output_file}")

        # Save raw NPS API data
        raw_dir = RAW_DATA_DIR / 'nps'
        raw_dir.mkdir(parents=True, exist_ok=True)
        output_file = raw_dir / 'nps_parks_raw_data.json'
        with open(output_file, 'w') as f:
            json.dump(nps_raw_data, f, indent=2)
        print(f"✓ Saved: {output_file}")

        summary['7.8_national_parks'] = {
            'records': len(parks_df),
            'counties_with_parks': int((parks_df['park_count'] > 0).sum()),
            'total_parks': len(nps_raw_data) if nps_raw_data else 0,
            'mean_parks_per_county': float(parks_df['park_count'].mean()),
            'max_parks_in_county': int(parks_df['park_count'].max())
        }

    # Save summary
    summary['collection_date'] = datetime.now().isoformat()
    summary['acs_year'] = acs_year
    summary['cbp_year'] = cbp_year
    summary['qcew_year'] = qcew_year
    summary['states'] = list(STATE_FIPS.keys())

    summary_file = processed_dir / 'component7_collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved: {summary_file}")

    return summary


def main():
    """Main execution function"""
    print("=" * 60)
    print("Component 7: Quality of Life - Data Collection")
    print("Measures: 7.1, 7.2, 7.3, 7.6, 7.7, 7.8")
    print("=" * 60)

    # Configuration
    ACS_YEAR = 2022  # 2018-2022 5-year estimates
    CBP_YEAR = 2021  # Most recent CBP year
    QCEW_YEAR = 2022  # Most recent QCEW year

    # All 10 states
    state_fips_list = list(STATE_FIPS.values())
    state_codes = list(STATE_FIPS.keys())

    # Initialize clients
    print("\nInitializing API clients...")
    census_client = CensusClient()
    cbp_client = CBPClient()
    qcew_client = QCEWClient()
    nps_client = NPSClient()
    print("✓ Clients initialized")

    # Collect data for each measure
    try:
        # 7.1: Commute Time
        commute_df = collect_commute_time(census_client, ACS_YEAR, state_fips_list)

        # 7.2: Housing Age (Pre-1960)
        housing_df = collect_housing_age(census_client, ACS_YEAR, state_fips_list)

        # 7.3: Relative Weekly Wage
        wage_df = collect_relative_weekly_wage(qcew_client, QCEW_YEAR, state_fips_list)

        # 7.6: Climate Amenities
        climate_df = collect_climate_amenities(state_fips_list)

        # 7.7: Healthcare Employment
        healthcare_df = collect_healthcare_employment(cbp_client, CBP_YEAR, state_fips_list)

        # 7.8: National Parks
        parks_df, park_details_df, nps_raw_data = collect_nps_parks(nps_client, state_codes, state_fips_list)

        # Process and save all data
        summary = process_and_save_data(
            commute_df, housing_df, wage_df, climate_df, healthcare_df, parks_df, park_details_df, nps_raw_data,
            ACS_YEAR, CBP_YEAR, QCEW_YEAR
        )

        # Print summary
        print("\n" + "=" * 60)
        print("COLLECTION COMPLETE")
        print("=" * 60)
        print(f"Total measures collected: 6 of 8 (75% complete)")
        print(f"\nSummary:")
        for measure, stats in summary.items():
            if measure.startswith('7.'):
                if measure == '7.8_national_parks':
                    print(f"  {measure}: {stats['records']} records ({stats['counties_with_parks']} counties with parks)")
                else:
                    print(f"  {measure}: {stats['records']} records")

    except Exception as e:
        print(f"\n✗ Error during collection: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
