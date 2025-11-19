"""
Complete Component 2 Regional Aggregation

Aggregates the remaining 3 measures of Component 2 to regional level:
- 2.4: Nonemployer Share (recalculate from nonemployer + employer counts)
- 2.5: Industry Diversity (Herfindahl index from 19 NAICS sectors)
- 2.6: Occupation Diversity (Herfindahl index from 6 occupation categories)

Updates existing component2_economic_opportunity_regional.csv with these measures.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from regional_data_manager import RegionalDataManager


def calculate_herfindahl_index(shares: pd.Series) -> float:
    """
    Calculate Herfindahl-Hirschman Index (HHI) from employment/worker shares.

    HHI = sum(share_i^2) for all categories i
    Then convert to diversity: Diversity = 1 - HHI

    Higher diversity score = more diverse (closer to 1)
    Lower diversity score = less diverse (closer to 0)

    Args:
        shares: Series of employment shares (as decimals, not percentages)

    Returns:
        Diversity index (1 - HHI), range 0-1
    """
    # Remove NaN values
    shares = shares.dropna()

    # Ensure shares sum to 1 (normalize)
    share_sum = shares.sum()
    if share_sum > 0:
        shares = shares / share_sum

    # Calculate HHI
    hhi = (shares ** 2).sum()

    # Convert to diversity (1 - HHI)
    diversity = 1 - hhi

    return diversity


def aggregate_industry_diversity(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Calculate industry diversity for each region using Herfindahl index.

    Reads 19 NAICS sector employment files, aggregates employment by region,
    calculates employment shares, then computes Herfindahl diversity index.

    Returns:
        DataFrame with region_key and industry_diversity columns
    """
    print("\n" + "="*80)
    print("CALCULATING INDUSTRY DIVERSITY (Herfindahl Index)")
    print("="*80)

    # NAICS sectors (19 major 2-digit codes)
    naics_sectors = [
        '11', '21', '22', '23', '31-33', '42', '44-45', '48-49',
        '51', '52', '53', '54', '55', '56', '61', '62', '71', '72', '81'
    ]

    # Load employment data for all sectors
    data_dir = Path('data/processed')
    all_industry_data = []

    for naics in naics_sectors:
        filepath = data_dir / f'cbp_industry_naics{naics}_2021.csv'
        if filepath.exists():
            df = pd.read_csv(filepath)
            df['naics'] = naics
            all_industry_data.append(df)
            print(f"  Loaded NAICS {naics}: {len(df)} counties")
        else:
            print(f"  WARNING: Missing file for NAICS {naics}")

    # Combine all industry data
    industry_df = pd.concat(all_industry_data, ignore_index=True)
    print(f"\nTotal industry records: {len(industry_df)}")

    # Add FIPS codes
    industry_df['fips'] = (industry_df['state'].astype(str).str.zfill(2) +
                           industry_df['county'].astype(str).str.zfill(3))

    # Map counties to regions (extract region_key from dict)
    industry_df['region_key'] = industry_df['fips'].apply(
        lambda fips: rdm.county_to_region.get(fips, {}).get('region_key') if fips in rdm.county_to_region else None
    )

    # Remove unmapped counties
    unmapped = industry_df['region_key'].isna().sum()
    if unmapped > 0:
        print(f"WARNING: {unmapped} records without region mapping")
        industry_df = industry_df.dropna(subset=['region_key'])

    # Aggregate employment by region and NAICS sector
    regional_employment = industry_df.groupby(['region_key', 'naics'])['EMP'].sum().reset_index()

    print(f"\nRegional employment by sector: {len(regional_employment)} records")
    print(f"Regions: {regional_employment['region_key'].nunique()}")

    # Calculate diversity index for each region
    diversity_results = []

    for region in regional_employment['region_key'].unique():
        region_data = regional_employment[regional_employment['region_key'] == region]

        # Get employment by sector
        employment = region_data.set_index('naics')['EMP']

        # Calculate shares
        total_employment = employment.sum()
        if total_employment > 0:
            shares = employment / total_employment

            # Calculate Herfindahl diversity index
            diversity = calculate_herfindahl_index(shares)

            diversity_results.append({
                'region_key': region,
                'industry_diversity': diversity,
                'total_employment': total_employment,
                'num_sectors': len(employment)
            })

    diversity_df = pd.DataFrame(diversity_results)

    print(f"\nIndustry Diversity Statistics:")
    print(f"  Regions: {len(diversity_df)}")
    print(f"  Mean diversity: {diversity_df['industry_diversity'].mean():.4f}")
    print(f"  Std dev: {diversity_df['industry_diversity'].std():.4f}")
    print(f"  Min: {diversity_df['industry_diversity'].min():.4f}")
    print(f"  Max: {diversity_df['industry_diversity'].max():.4f}")

    return diversity_df[['region_key', 'industry_diversity']]


def aggregate_occupation_diversity(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Calculate occupation diversity for each region using Herfindahl index.

    Reads census occupation data (S2401), aggregates by region,
    calculates occupation shares, then computes Herfindahl diversity index.

    Returns:
        DataFrame with region_key and occupation_diversity columns
    """
    print("\n" + "="*80)
    print("CALCULATING OCCUPATION DIVERSITY (Herfindahl Index)")
    print("="*80)

    # Load occupation data
    occ_file = Path('data/processed/census_occupation_2022.csv')
    occ_df = pd.read_csv(occ_file)

    print(f"Loaded occupation data: {len(occ_df)} counties")

    # Occupation columns (6 major groups from S2401)
    # S2401_C01_001E = Total civilian employed population 16 years and over
    # S2401_C01_002E = Management, business, science, and arts
    # S2401_C01_003E = Service occupations
    # S2401_C01_004E = Sales and office occupations
    # S2401_C01_005E = Natural resources, construction, and maintenance
    # S2401_C01_006E = Production, transportation, and material moving

    occupation_cols = [
        'S2401_C01_002E',  # Management/business/science/arts
        'S2401_C01_003E',  # Service
        'S2401_C01_004E',  # Sales/office
        'S2401_C01_005E',  # Natural resources/construction
        'S2401_C01_006E'   # Production/transportation
    ]

    # Add FIPS codes
    occ_df['fips'] = (occ_df['state'].astype(str).str.zfill(2) +
                      occ_df['county'].astype(str).str.zfill(3))

    # Map counties to regions (extract region_key from dict)
    occ_df['region_key'] = occ_df['fips'].apply(
        lambda fips: rdm.county_to_region.get(fips, {}).get('region_key') if fips in rdm.county_to_region else None
    )

    # Remove unmapped counties
    unmapped = occ_df['region_key'].isna().sum()
    if unmapped > 0:
        print(f"WARNING: {unmapped} counties without region mapping")
        occ_df = occ_df.dropna(subset=['region_key'])

    # Aggregate occupation counts by region
    agg_cols = occupation_cols + ['S2401_C01_001E']  # Include total for verification
    regional_occ = occ_df.groupby('region_key')[agg_cols].sum().reset_index()

    print(f"\nRegional occupation data: {len(regional_occ)} regions")

    # Calculate diversity index for each region
    diversity_results = []

    for _, row in regional_occ.iterrows():
        region = row['region_key']

        # Get occupation counts
        occ_counts = row[occupation_cols]

        # Calculate shares
        total_employed = occ_counts.sum()
        if total_employed > 0:
            shares = occ_counts / total_employed

            # Calculate Herfindahl diversity index
            diversity = calculate_herfindahl_index(shares)

            diversity_results.append({
                'region_key': region,
                'occupation_diversity': diversity,
                'total_employed': total_employed
            })

    diversity_df = pd.DataFrame(diversity_results)

    print(f"\nOccupation Diversity Statistics:")
    print(f"  Regions: {len(diversity_df)}")
    print(f"  Mean diversity: {diversity_df['occupation_diversity'].mean():.4f}")
    print(f"  Std dev: {diversity_df['occupation_diversity'].std():.4f}")
    print(f"  Min: {diversity_df['occupation_diversity'].min():.4f}")
    print(f"  Max: {diversity_df['occupation_diversity'].max():.4f}")

    return diversity_df[['region_key', 'occupation_diversity']]


def aggregate_nonemployer_share(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Calculate nonemployer share for each region.

    Nonemployer Share = Nonemployer Establishments / (Nonemployer + Employer Establishments)

    Returns:
        DataFrame with region_key and nonemployer_share columns
    """
    print("\n" + "="*80)
    print("CALCULATING NONEMPLOYER SHARE")
    print("="*80)

    # Load nonemployer data
    nonemp_file = Path('data/processed/nonemp_firms_2021.csv')
    nonemp_df = pd.read_csv(nonemp_file)
    print(f"Loaded nonemployer data: {len(nonemp_df)} counties")

    # Load employer establishment data
    emp_file = Path('data/processed/cbp_establishments_2021.csv')
    emp_df = pd.read_csv(emp_file)
    print(f"Loaded employer data: {len(emp_df)} counties")

    # Add FIPS codes
    nonemp_df['fips'] = (nonemp_df['state'].astype(str).str.zfill(2) +
                         nonemp_df['county'].astype(str).str.zfill(3))
    emp_df['fips'] = (emp_df['state'].astype(str).str.zfill(2) +
                      emp_df['county'].astype(str).str.zfill(3))

    # Merge nonemployer and employer data
    merged = pd.merge(nonemp_df[['fips', 'NESTAB']],
                      emp_df[['fips', 'ESTAB']],
                      on='fips', how='outer')

    # Fill missing values with 0
    merged['NESTAB'] = merged['NESTAB'].fillna(0)
    merged['ESTAB'] = merged['ESTAB'].fillna(0)

    print(f"\nMerged data: {len(merged)} counties")

    # Map counties to regions (extract region_key from dict)
    merged['region_key'] = merged['fips'].apply(
        lambda fips: rdm.county_to_region.get(fips, {}).get('region_key') if fips in rdm.county_to_region else None
    )

    # Remove unmapped counties
    unmapped = merged['region_key'].isna().sum()
    if unmapped > 0:
        print(f"WARNING: {unmapped} counties without region mapping")
        merged = merged.dropna(subset=['region_key'])

    # Aggregate by region
    regional_data = merged.groupby('region_key')[['NESTAB', 'ESTAB']].sum().reset_index()

    # Calculate nonemployer share
    regional_data['total_establishments'] = regional_data['NESTAB'] + regional_data['ESTAB']
    regional_data['nonemployer_share'] = (
        regional_data['NESTAB'] / regional_data['total_establishments'] * 100
    )

    print(f"\nNonemployer Share Statistics:")
    print(f"  Regions: {len(regional_data)}")
    print(f"  Mean share: {regional_data['nonemployer_share'].mean():.2f}%")
    print(f"  Std dev: {regional_data['nonemployer_share'].std():.2f}%")
    print(f"  Min: {regional_data['nonemployer_share'].min():.2f}%")
    print(f"  Max: {regional_data['nonemployer_share'].max():.2f}%")

    return regional_data[['region_key', 'nonemployer_share']]


def main():
    """Main execution function."""
    print("="*80)
    print("COMPLETE COMPONENT 2 REGIONAL AGGREGATION")
    print("Adding measures 2.4, 2.5, 2.6 to existing regional data")
    print("="*80)

    # Initialize regional data manager
    print("\nInitializing Regional Data Manager...")
    rdm = RegionalDataManager()

    # Calculate each measure
    industry_div = aggregate_industry_diversity(rdm)
    occupation_div = aggregate_occupation_diversity(rdm)
    nonemployer = aggregate_nonemployer_share(rdm)

    # Load existing regional data
    regional_file = Path('data/regional/component2_economic_opportunity_regional.csv')
    if not regional_file.exists():
        print(f"\nERROR: Regional file not found: {regional_file}")
        return

    existing_df = pd.read_csv(regional_file)
    print(f"\n" + "="*80)
    print(f"MERGING WITH EXISTING REGIONAL DATA")
    print("="*80)
    print(f"Existing data: {len(existing_df)} regions, {len(existing_df.columns)} columns")
    print(f"Existing columns: {', '.join(existing_df.columns)}")

    # Merge new measures
    result_df = existing_df.copy()

    # Merge industry diversity
    result_df = pd.merge(result_df, industry_div, on='region_key', how='left')
    print(f"\nAfter merging industry diversity: {len(result_df)} regions")

    # Merge occupation diversity
    result_df = pd.merge(result_df, occupation_div, on='region_key', how='left')
    print(f"After merging occupation diversity: {len(result_df)} regions")

    # Merge nonemployer share
    result_df = pd.merge(result_df, nonemployer, on='region_key', how='left')
    print(f"After merging nonemployer share: {len(result_df)} regions")

    # Verify all regions have data
    missing_data = result_df[['industry_diversity', 'occupation_diversity', 'nonemployer_share']].isna().sum()
    if missing_data.any():
        print(f"\nWARNING: Missing data detected:")
        print(missing_data[missing_data > 0])

    # Reorder columns: region info, then all 7 measures
    column_order = [
        'region_key', 'region_name', 'state_name',
        'entrepreneurial_activity', 'proprietors_per_1000', 'establishments_per_1000',
        'industry_diversity', 'occupation_diversity', 'nonemployer_share',
        'telecommuter_pct'
    ]

    result_df = result_df[column_order]

    # Save updated regional data
    result_df.to_csv(regional_file, index=False)

    print(f"\n" + "="*80)
    print("AGGREGATION COMPLETE!")
    print("="*80)
    print(f"Updated file: {regional_file}")
    print(f"Total regions: {len(result_df)}")
    print(f"Total measures: {len(result_df.columns) - 3}  (7 of 7 Component 2 measures)")
    print("\nAll Component 2 measures now aggregated:")
    print("  ✓ 2.1: Entrepreneurial Activity")
    print("  ✓ 2.2: Proprietors per 1,000")
    print("  ✓ 2.3: Establishments per 1,000")
    print("  ✓ 2.4: Nonemployer Share")
    print("  ✓ 2.5: Industry Diversity")
    print("  ✓ 2.6: Occupation Diversity")
    print("  ✓ 2.7: Telecommuter Share")

    # Print summary statistics for new measures
    print("\n" + "="*80)
    print("SUMMARY STATISTICS FOR NEW MEASURES")
    print("="*80)

    for col in ['industry_diversity', 'occupation_diversity', 'nonemployer_share']:
        print(f"\n{col}:")
        print(f"  Mean: {result_df[col].mean():.4f}")
        print(f"  Std:  {result_df[col].std():.4f}")
        print(f"  Min:  {result_df[col].min():.4f}")
        print(f"  Max:  {result_df[col].max():.4f}")


if __name__ == "__main__":
    main()
