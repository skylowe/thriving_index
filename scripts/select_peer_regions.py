"""
Select peer regions for Virginia rural regions using Mahalanobis distance.

For each of the 6 rural Virginia regions, identify 5-8 comparable peer regions
from the other 9 states based on:
1. Population
2. Micropolitan percentage
3. Farm income percentage
4. Services employment percentage
5. Manufacturing employment percentage
6. Distance to small MSA
7. Distance to large MSA
8. Mining employment percentage

Uses Mahalanobis distance to account for correlations between variables.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_peer_matching_data():
    """Load the peer matching variables dataset."""
    data_file = Path('data/peer_matching_variables.csv')
    df = pd.read_csv(data_file)

    # Select only the matching variables (excluding metadata)
    variable_cols = [
        'population',
        'micropolitan_pct',
        'farm_income_pct',
        'services_employment_pct',
        'manufacturing_employment_pct',
        'distance_to_small_msa',
        'distance_to_large_msa',
        'mining_employment_pct'
    ]

    return df, variable_cols


def identify_virginia_rural_regions(df):
    """
    Identify the 6 rural Virginia regions.

    Rural regions (based on GO Virginia):
    - Region 1: Southwest Virginia
    - Region 2: Central/Western Virginia
    - Region 3: Southside Virginia
    - Region 6: Mary Ball Washington Regional Council
    - Region 8: Shenandoah Valley
    - Region 9: Central Virginia

    Excluded (metro):
    - Region 4: Greater Richmond
    - Region 5: Hampton Roads
    - Region 7: Northern Virginia
    """
    rural_regions = ['51_1', '51_2', '51_3', '51_6', '51_8', '51_9']

    va_rural = df[df['region_key'].isin(rural_regions)].copy()

    print("Virginia Rural Regions:")
    for _, row in va_rural.iterrows():
        print(f"  {row['region_key']}: {row['region_name']}")

    return va_rural, rural_regions


def standardize_variables(df, variable_cols):
    """
    Standardize variables using z-score normalization.

    Returns:
        standardized_df: DataFrame with standardized variables
        means: Mean values for each variable
        stds: Standard deviation for each variable
    """
    standardized_df = df.copy()

    means = {}
    stds = {}

    for col in variable_cols:
        means[col] = df[col].mean()
        stds[col] = df[col].std()
        standardized_df[col] = (df[col] - means[col]) / stds[col]

    return standardized_df, means, stds


def calculate_mahalanobis_distances(target_region, all_regions_std, variable_cols, cov_matrix_inv):
    """
    Calculate Mahalanobis distance from target region to all other regions.

    Args:
        target_region: Single row DataFrame with target region (standardized)
        all_regions_std: DataFrame with all regions (standardized)
        variable_cols: List of variable column names
        cov_matrix_inv: Inverse covariance matrix

    Returns:
        Series with Mahalanobis distances for each region
    """
    target_vector = target_region[variable_cols].values[0]

    distances = []
    for idx, row in all_regions_std.iterrows():
        candidate_vector = row[variable_cols].values

        # Calculate Mahalanobis distance
        diff = candidate_vector - target_vector
        distance = np.sqrt(diff @ cov_matrix_inv @ diff.T)
        distances.append(distance)

    return pd.Series(distances, index=all_regions_std.index)


def select_peer_regions(va_region_key, df_std, df_original, variable_cols, cov_matrix_inv,
                        exclude_regions, n_peers=8):
    """
    Select peer regions for a Virginia region.

    Args:
        va_region_key: Virginia region key (e.g., '51_1')
        df_std: Standardized DataFrame
        df_original: Original (unstandardized) DataFrame
        variable_cols: List of variable column names
        cov_matrix_inv: Inverse covariance matrix
        exclude_regions: List of region keys to exclude (other Virginia regions)
        n_peers: Number of peer regions to select (default 8)

    Returns:
        DataFrame with peer regions and their distances
    """
    # Get target region
    target_region_std = df_std[df_std['region_key'] == va_region_key]
    target_region_orig = df_original[df_original['region_key'] == va_region_key]

    # Filter to candidate regions (exclude Virginia regions)
    candidates_std = df_std[~df_std['region_key'].isin(exclude_regions)].copy()
    candidates_orig = df_original[~df_original['region_key'].isin(exclude_regions)].copy()

    # Calculate distances
    distances = calculate_mahalanobis_distances(
        target_region_std,
        candidates_std,
        variable_cols,
        cov_matrix_inv
    )

    # Add distances to candidates
    candidates_orig['mahalanobis_distance'] = distances.values

    # Sort by distance and select top N
    peers = candidates_orig.nsmallest(n_peers, 'mahalanobis_distance')

    # Add rank
    peers['peer_rank'] = range(1, len(peers) + 1)

    return peers, target_region_orig


def main():
    """Select peer regions for all 6 Virginia rural regions."""
    print("="*80)
    print("PEER REGION SELECTION USING MAHALANOBIS DISTANCE")
    print("="*80)

    # Load data
    print("\n[1/6] Loading peer matching variables...")
    df, variable_cols = load_peer_matching_data()
    print(f"  Loaded {len(df)} regions with {len(variable_cols)} matching variables")

    # Identify Virginia rural regions
    print("\n[2/6] Identifying Virginia rural regions...")
    va_rural, va_region_keys = identify_virginia_rural_regions(df)
    print(f"  Found {len(va_rural)} rural Virginia regions")

    # Standardize variables
    print("\n[3/6] Standardizing variables...")
    df_std, means, stds = standardize_variables(df, variable_cols)
    print("  Variables standardized (z-score normalization)")

    # Calculate covariance matrix
    print("\n[4/6] Calculating covariance matrix...")
    X_std = df_std[variable_cols].values
    cov_matrix = np.cov(X_std.T)

    # Calculate inverse covariance matrix
    try:
        cov_matrix_inv = np.linalg.inv(cov_matrix)
        print("  Covariance matrix inverted successfully")
    except np.linalg.LinAlgError:
        print("  Warning: Covariance matrix is singular, using pseudo-inverse")
        cov_matrix_inv = np.linalg.pinv(cov_matrix)

    # Select peer regions for each Virginia region
    print("\n[5/6] Selecting peer regions...")
    print("  Target: 8 peer regions per Virginia region")
    print()

    all_peer_selections = []

    for va_key in va_region_keys:
        va_name = df[df['region_key'] == va_key]['region_name'].values[0]

        print(f"\n{va_key}: {va_name}")
        print("-" * 80)

        peers, target = select_peer_regions(
            va_key,
            df_std,
            df,
            variable_cols,
            cov_matrix_inv,
            va_region_keys,  # Exclude all Virginia regions from peer selection
            n_peers=8
        )

        # Display target region characteristics
        print(f"\nTarget Region Characteristics:")
        print(f"  Population: {target['population'].values[0]:,.0f}")
        print(f"  Micropolitan %: {target['micropolitan_pct'].values[0]:.1f}%")
        print(f"  Farm income %: {target['farm_income_pct'].values[0]:.2f}%")
        print(f"  Services employment %: {target['services_employment_pct'].values[0]:.1f}%")
        print(f"  Manufacturing employment %: {target['manufacturing_employment_pct'].values[0]:.1f}%")
        print(f"  Distance to small MSA: {target['distance_to_small_msa'].values[0]:.1f} mi")
        print(f"  Distance to large MSA: {target['distance_to_large_msa'].values[0]:.1f} mi")
        print(f"  Mining employment %: {target['mining_employment_pct'].values[0]:.2f}%")

        # Display peer regions
        print(f"\nSelected Peer Regions (sorted by Mahalanobis distance):")
        for _, peer in peers.iterrows():
            print(f"  {peer['peer_rank']}. {peer['region_name']}, {peer['state_name']}")
            print(f"     Distance: {peer['mahalanobis_distance']:.3f}")
            print(f"     Pop: {peer['population']:,.0f} | "
                  f"Micro: {peer['micropolitan_pct']:.1f}% | "
                  f"Farm: {peer['farm_income_pct']:.2f}% | "
                  f"Svc: {peer['services_employment_pct']:.1f}% | "
                  f"Mfg: {peer['manufacturing_employment_pct']:.1f}% | "
                  f"Mining: {peer['mining_employment_pct']:.2f}%")

        # Store for export
        peers['virginia_region_key'] = va_key
        peers['virginia_region_name'] = va_name
        all_peer_selections.append(peers)

    # Save results
    print("\n" + "="*80)
    print("[6/6] Saving peer region selections...")

    # Combine all peer selections
    all_peers_df = pd.concat(all_peer_selections, ignore_index=True)

    # Reorder columns
    output_cols = [
        'virginia_region_key', 'virginia_region_name',
        'peer_rank', 'mahalanobis_distance',
        'region_key', 'region_name', 'state_name',
        'population', 'micropolitan_pct', 'farm_income_pct',
        'services_employment_pct', 'manufacturing_employment_pct',
        'distance_to_small_msa', 'distance_to_large_msa',
        'mining_employment_pct'
    ]

    all_peers_df = all_peers_df[output_cols]

    # Save to CSV
    output_file = Path('data/peer_regions_selected.csv')
    all_peers_df.to_csv(output_file, index=False)

    print(f"\n✓ Saved peer region selections: {output_file}")
    print(f"  {len(all_peers_df)} peer regions selected")
    print(f"  {len(va_region_keys)} Virginia regions × 8 peers each = {len(va_region_keys) * 8} total")

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Selected {len(all_peers_df)} peer regions for {len(va_region_keys)} Virginia rural regions")
    print(f"📊 Mahalanobis distance range: {all_peers_df['mahalanobis_distance'].min():.3f} to {all_peers_df['mahalanobis_distance'].max():.3f}")
    print(f"📊 Mean distance: {all_peers_df['mahalanobis_distance'].mean():.3f}")

    # State distribution
    print("\n📍 Peer regions by state:")
    state_counts = all_peers_df['state_name'].value_counts()
    for state, count in state_counts.items():
        print(f"  {state}: {count} peer regions")

    print("\n🎉 PEER REGION SELECTION COMPLETE!")
    print("\nNext steps:")
    print("1. Review peer region selections for appropriateness")
    print("2. Validate that peer regions are truly comparable")
    print("3. Calculate thriving index scores using peer averages")


if __name__ == '__main__':
    main()
