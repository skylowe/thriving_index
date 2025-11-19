"""
Gather 7 variables for Mahalanobis distance peer region matching.

Variables:
1. Population (2022)
2. Percentage in micropolitan area
3. Farm income percentage
4. Services employment percentage
5. Manufacturing employment percentage
6. Distance to MSAs (small and large)
7. Mining/extraction employment percentage
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))
from regional_data_manager import RegionalDataManager


def gather_population(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 1: Total population (2022)
    Source: Census population data, aggregated to regional level
    """
    print("\n[1/7] Gathering population data...")

    # Read county-level population data
    pop_data = pd.read_csv('data/processed/census_population_growth_2000_2022.csv')

    # Ensure FIPS column
    pop_data['fips'] = pop_data['fips'].astype(str).str.zfill(5)

    # Add region_key
    pop_data['region_key'] = pop_data['fips'].apply(
        lambda fips: rdm.county_to_region.get(str(fips), {}).get('region_key')
        if str(fips) in rdm.county_to_region else None
    )

    # Aggregate to regional level
    regional_pop = pop_data.groupby('region_key')['population_2022'].sum().reset_index()
    regional_pop.columns = ['region_key', 'population']

    print(f"  Regions: {len(regional_pop)}, Mean: {regional_pop['population'].mean():,.0f}")

    return regional_pop


def gather_micropolitan_percentage(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 2: Percentage of population in micropolitan areas

    NOTE: Requires identifying which counties are in micropolitan statistical areas.
    This will need additional data from Census Bureau or OMB definitions.
    For now, returning placeholder.
    """
    print("\n[2/7] Calculating micropolitan percentage...")
    print("  ⚠️  PLACEHOLDER - Requires micropolitan area definitions")

    # TODO: Get micropolitan area definitions and calculate percentage
    # For now, return zeros as placeholder
    regions = rdm.get_all_regions()
    result = pd.DataFrame({
        'region_key': regions['region_key'],
        'micropolitan_pct': 0.0  # Placeholder
    })

    return result


def gather_farm_income_percentage(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 3: Farm income as percentage of total income
    Source: BEA farm income data (need to extract from CAINC45 table)

    NOTE: We have proprietor income but need to isolate farm income specifically.
    This requires BEA CAINC45 table (Farm Income and Expenses).
    For now, returning placeholder.
    """
    print("\n[3/7] Extracting farm income percentage...")
    print("  ⚠️  PLACEHOLDER - Requires BEA CAINC45 farm income data")

    # TODO: Collect BEA farm income data and aggregate to regional level
    regions = rdm.get_all_regions()
    result = pd.DataFrame({
        'region_key': regions['region_key'],
        'farm_income_pct': 0.0  # Placeholder
    })

    return result


def gather_services_employment_percentage(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 4: Services employment as percentage of total employment
    Source: CBP data by industry (NAICS codes for services sectors)

    Services sectors (NAICS):
    - 44-45: Retail Trade
    - 48-49: Transportation and Warehousing
    - 51: Information
    - 52: Finance and Insurance
    - 53: Real Estate and Rental and Leasing
    - 54: Professional, Scientific, and Technical Services
    - 55: Management of Companies and Enterprises
    - 56: Administrative and Support and Waste Management
    - 61: Educational Services
    - 62: Health Care and Social Assistance
    - 71: Arts, Entertainment, and Recreation
    - 72: Accommodation and Food Services
    - 81: Other Services (except Public Administration)
    """
    print("\n[4/7] Calculating services employment percentage...")

    # Services NAICS codes
    services_naics = [
        'naics44-45', 'naics48-49', 'naics51', 'naics52', 'naics53',
        'naics54', 'naics55', 'naics56', 'naics61', 'naics62',
        'naics71', 'naics72', 'naics81'
    ]

    # Read and combine all services sectors
    services_employment = []

    for naics in services_naics:
        file = f'data/processed/cbp_industry_{naics}_2021.csv'
        try:
            df = pd.read_csv(file)
            df['fips'] = (df['state'].astype(str).str.zfill(2) +
                         df['county'].astype(str).str.zfill(3))
            df['region_key'] = df['fips'].apply(
                lambda fips: rdm.county_to_region.get(str(fips), {}).get('region_key')
                if str(fips) in rdm.county_to_region else None
            )
            df = df[df['region_key'].notna()]
            services_employment.append(df[['region_key', 'EMP']])
        except FileNotFoundError:
            print(f"  Warning: {file} not found, skipping")
            continue

    # Combine and sum
    if services_employment:
        services_df = pd.concat(services_employment, ignore_index=True)
        services_total = services_df.groupby('region_key')['EMP'].sum().reset_index()
        services_total.columns = ['region_key', 'services_employment']
    else:
        regions = rdm.get_all_regions()
        services_total = pd.DataFrame({
            'region_key': regions['region_key'],
            'services_employment': 0
        })

    print(f"  Regions: {len(services_total)}, Mean employment: {services_total['services_employment'].mean():,.0f}")

    # Will calculate percentage after we have total employment
    return services_total


def gather_manufacturing_employment_percentage(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 5: Manufacturing employment as percentage of total employment
    Source: CBP NAICS 31-33 (Manufacturing)
    """
    print("\n[5/7] Extracting manufacturing employment...")

    # Read manufacturing data
    mfg = pd.read_csv('data/processed/cbp_industry_naics31-33_2021.csv')

    # Add FIPS and region_key
    mfg['fips'] = (mfg['state'].astype(str).str.zfill(2) +
                   mfg['county'].astype(str).str.zfill(3))
    mfg['region_key'] = mfg['fips'].apply(
        lambda fips: rdm.county_to_region.get(str(fips), {}).get('region_key')
        if str(fips) in rdm.county_to_region else None
    )

    # Aggregate to regional level
    mfg_clean = mfg[mfg['region_key'].notna()]
    regional_mfg = mfg_clean.groupby('region_key')['EMP'].sum().reset_index()
    regional_mfg.columns = ['region_key', 'manufacturing_employment']

    print(f"  Regions: {len(regional_mfg)}, Mean employment: {regional_mfg['manufacturing_employment'].mean():,.0f}")

    return regional_mfg


def gather_msa_distances(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 6: Distance to nearest small MSA and large MSA

    Requires:
    - List of MSAs with population sizes
    - County centroids (lat/lon)
    - Distance calculation (haversine or driving distance)

    NOTE: This is complex and will require additional data sources.
    """
    print("\n[6/7] Calculating distance to MSAs...")
    print("  ⚠️  PLACEHOLDER - Requires MSA definitions and geospatial calculation")

    # TODO: Get MSA locations, calculate regional centroids, compute distances
    regions = rdm.get_all_regions()
    result = pd.DataFrame({
        'region_key': regions['region_key'],
        'distance_to_small_msa': 0.0,  # Placeholder
        'distance_to_large_msa': 0.0   # Placeholder
    })

    return result


def gather_mining_employment_percentage(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Variable 7: Mining/extraction employment as percentage of total employment
    Source: CBP NAICS 21 (Mining, Quarrying, and Oil and Gas Extraction)
    """
    print("\n[7/7] Calculating mining/extraction employment...")

    # Read mining data
    mining = pd.read_csv('data/processed/cbp_industry_naics21_2021.csv')

    # Add FIPS and region_key
    mining['fips'] = (mining['state'].astype(str).str.zfill(2) +
                     mining['county'].astype(str).str.zfill(3))
    mining['region_key'] = mining['fips'].apply(
        lambda fips: rdm.county_to_region.get(str(fips), {}).get('region_key')
        if str(fips) in rdm.county_to_region else None
    )

    # Aggregate to regional level
    mining_clean = mining[mining['region_key'].notna()]
    regional_mining = mining_clean.groupby('region_key')['EMP'].sum().reset_index()
    regional_mining.columns = ['region_key', 'mining_employment']

    print(f"  Regions: {len(regional_mining)}, Mean employment: {regional_mining['mining_employment'].mean():,.0f}")

    return regional_mining


def main():
    """Gather all 7 peer matching variables."""
    print("="*80)
    print("GATHERING PEER MATCHING VARIABLES")
    print("7 variables for Mahalanobis distance matching")
    print("="*80)

    # Initialize regional data manager
    rdm = RegionalDataManager()

    # Gather each variable
    var1 = gather_population(rdm)
    var2 = gather_micropolitan_percentage(rdm)
    var3 = gather_farm_income_percentage(rdm)
    var4_emp = gather_services_employment_percentage(rdm)  # Returns employment count
    var5_emp = gather_manufacturing_employment_percentage(rdm)  # Returns employment count
    var6 = gather_msa_distances(rdm)
    var7_emp = gather_mining_employment_percentage(rdm)  # Returns employment count

    # Calculate total employment and percentages
    print("\n" + "="*80)
    print("CALCULATING EMPLOYMENT PERCENTAGES")
    print("="*80)

    # Merge employment data
    employment = var4_emp
    employment = pd.merge(employment, var5_emp, on='region_key', how='outer')
    employment = pd.merge(employment, var7_emp, on='region_key', how='outer')

    # Fill NaN with 0 (regions with no employment in that sector)
    employment = employment.fillna(0)

    # Calculate total employment
    employment['total_employment'] = (employment['services_employment'] +
                                     employment['manufacturing_employment'] +
                                     employment['mining_employment'])

    # Calculate percentages
    employment['services_employment_pct'] = (employment['services_employment'] /
                                            employment['total_employment'] * 100)
    employment['manufacturing_employment_pct'] = (employment['manufacturing_employment'] /
                                                 employment['total_employment'] * 100)
    employment['mining_employment_pct'] = (employment['mining_employment'] /
                                          employment['total_employment'] * 100)

    # Handle division by zero
    employment = employment.fillna(0)

    print(f"  Mean services %: {employment['services_employment_pct'].mean():.2f}%")
    print(f"  Mean manufacturing %: {employment['manufacturing_employment_pct'].mean():.2f}%")
    print(f"  Mean mining %: {employment['mining_employment_pct'].mean():.2f}%")

    # Keep only percentage columns for final dataset
    var4 = employment[['region_key', 'services_employment_pct']]
    var5 = employment[['region_key', 'manufacturing_employment_pct']]
    var7 = employment[['region_key', 'mining_employment_pct']]

    # Merge all variables
    print("\n" + "="*80)
    print("MERGING ALL VARIABLES")
    print("="*80)

    result = var1
    result = pd.merge(result, var2, on='region_key', how='outer')
    result = pd.merge(result, var3, on='region_key', how='outer')
    result = pd.merge(result, var4, on='region_key', how='outer')
    result = pd.merge(result, var5, on='region_key', how='outer')
    result = pd.merge(result, var6, on='region_key', how='outer')
    result = pd.merge(result, var7, on='region_key', how='outer')

    # Add region names
    result = rdm.add_region_names(result)

    # Save to file
    output_file = Path('data/peer_matching_variables.csv')
    result.to_csv(output_file, index=False)

    print(f"\n✓ Saved peer matching variables: {output_file}")
    print(f"  Regions: {len(result)}")
    print(f"  Variables: {len(result.columns) - 3}")  # Minus ID columns

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("✅ Variable 1: Population - COMPLETE")
    print("⚠️  Variable 2: Micropolitan % - NEEDS DATA (Census metro/micro definitions)")
    print("⚠️  Variable 3: Farm income % - NEEDS DATA (BEA CAINC45 farm income)")
    print("✅ Variable 4: Services employment % - COMPLETE")
    print("✅ Variable 5: Manufacturing employment % - COMPLETE")
    print("⚠️  Variable 6: Distance to MSAs - NEEDS DATA (Geospatial calculation)")
    print("✅ Variable 7: Mining employment % - COMPLETE")
    print(f"\n📊 Progress: 4 of 7 variables complete (57%)")
    print("\nNext steps:")
    print("1. Collect BEA farm income data (CAINC45 table)")
    print("2. Get micropolitan area definitions from Census/OMB")
    print("3. Calculate MSA distances using geospatial data (lat/lon centroids)")


if __name__ == '__main__':
    main()
