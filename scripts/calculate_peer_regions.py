"""
Calculate Peer Regions using Mahalanobis Distance

Implements the Nebraska Thriving Index peer region matching methodology.
For each Virginia region, find the 10 nearest peer regions from surrounding
states based on Mahalanobis distance using 6 matching variables.

Matching Variables:
1. Total population
2. % in micropolitan area
3. % farm income
4. % manufacturing employment
5. Distance to small MSA (<250k population)
6. Distance to large MSA (>250k population)

Source: Comparison Regions methodology from Nebraska Thriving Index 2022
"""

import sys
from pathlib import Path
import json
import numpy as np
from typing import Dict, List, Tuple


def mahalanobis_distance(vec1: np.ndarray, vec2: np.ndarray, inv_cov: np.ndarray) -> float:
    """
    Calculate Mahalanobis distance between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector
        inv_cov: Inverse covariance matrix

    Returns:
        Mahalanobis distance
    """
    diff = vec1 - vec2
    return np.sqrt(diff @ inv_cov @ diff.T)

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def load_matching_variables(logger) -> Dict:
    """
    Load all 6 matching variables.

    Returns:
        Dict with variables data
    """
    matching_vars_file = project_root / 'data' / 'processed' / 'matching_variables.json'

    if not matching_vars_file.exists():
        logger.error(f"Matching variables file not found: {matching_vars_file}")
        return {}

    with open(matching_vars_file) as f:
        data = json.load(f)

    logger.info(f"Loaded matching variables from: {matching_vars_file}")

    # Check which variables are available
    variables = data.get('variables', {})
    var_names = ['population', 'pct_micropolitan', 'pct_farm_income',
                 'pct_manufacturing', 'small_msa_distance', 'large_msa_distance']

    available = []
    for var in var_names:
        if var in variables and variables[var]:
            count = len(variables[var])
            logger.info(f"  {var}: {count} regions")
            available.append(var)
        else:
            logger.warning(f"  {var}: NOT AVAILABLE")

    logger.info(f"\n✓ Available variables: {len(available)}/6")

    return data


def prepare_data_matrix(matching_vars: Dict, logger) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Prepare data matrix for Mahalanobis distance calculation.

    Args:
        matching_vars: Matching variables dict

    Returns:
        Tuple of (data matrix, region codes, variable names)
    """
    logger.info("\n" + "=" * 70)
    logger.info("Preparing Data Matrix")
    logger.info("=" * 70)

    variables = matching_vars.get('variables', {})

    # Define variable names in order
    var_names = []
    var_data = []

    # Add each variable if available
    if 'population' in variables and variables['population']:
        var_names.append('population')
        var_data.append(variables['population'])

    if 'pct_micropolitan' in variables and variables['pct_micropolitan']:
        # Skip micropolitan if all values are 0 (incomplete data)
        values = list(variables['pct_micropolitan'].values())
        if max(values) > 0:
            var_names.append('pct_micropolitan')
            var_data.append(variables['pct_micropolitan'])
        else:
            logger.warning("Skipping pct_micropolitan (all values are 0)")

    if 'pct_farm_income' in variables and variables['pct_farm_income']:
        var_names.append('pct_farm_income')
        var_data.append(variables['pct_farm_income'])

    if 'pct_manufacturing' in variables and variables['pct_manufacturing']:
        var_names.append('pct_manufacturing')
        var_data.append(variables['pct_manufacturing'])

    # Extract MSA distances from nested structure
    if 'msa_distances' in variables and variables['msa_distances']:
        msa_data = variables['msa_distances']

        # Extract small MSA distances
        small_msa = {region: data['small_msa_distance']
                     for region, data in msa_data.items()
                     if 'small_msa_distance' in data}
        if small_msa:
            var_names.append('small_msa_distance')
            var_data.append(small_msa)

        # Extract large MSA distances
        large_msa = {region: data['large_msa_distance']
                     for region, data in msa_data.items()
                     if 'large_msa_distance' in data}
        if large_msa:
            var_names.append('large_msa_distance')
            var_data.append(large_msa)

    logger.info(f"\nUsing {len(var_names)} variables:")
    for var in var_names:
        logger.info(f"  - {var}")

    # Get region codes (intersection of all variables)
    region_sets = [set(var.keys()) for var in var_data]
    common_regions = set.intersection(*region_sets) if region_sets else set()

    region_codes = sorted(list(common_regions))

    logger.info(f"\nRegions with complete data: {len(region_codes)}")

    # Build data matrix
    data_matrix = np.zeros((len(region_codes), len(var_names)))

    for i, region_code in enumerate(region_codes):
        for j, var_dict in enumerate(var_data):
            data_matrix[i, j] = var_dict[region_code]

    logger.info(f"Data matrix shape: {data_matrix.shape}")

    # Show summary statistics
    logger.info("\nVariable statistics:")
    for j, var_name in enumerate(var_names):
        col = data_matrix[:, j]
        logger.info(f"  {var_name}:")
        logger.info(f"    Min: {np.min(col):.2f}, Max: {np.max(col):.2f}")
        logger.info(f"    Mean: {np.mean(col):.2f}, Std: {np.std(col):.2f}")

    return data_matrix, region_codes, var_names


def calculate_mahalanobis_distances(
    data_matrix: np.ndarray,
    region_codes: List[str],
    logger
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Calculate Mahalanobis distances and find peer regions.

    Args:
        data_matrix: Data matrix (regions × variables)
        region_codes: List of region codes
        logger: Logger instance

    Returns:
        Dict mapping Virginia region codes to list of (peer_code, distance) tuples
    """
    logger.info("\n" + "=" * 70)
    logger.info("Calculating Mahalanobis Distances")
    logger.info("=" * 70)

    # Calculate covariance matrix
    cov_matrix = np.cov(data_matrix.T)
    logger.info(f"Covariance matrix shape: {cov_matrix.shape}")

    # Calculate inverse covariance (precision matrix)
    try:
        inv_cov = np.linalg.inv(cov_matrix)
        logger.info("✓ Calculated inverse covariance matrix")
    except np.linalg.LinAlgError:
        logger.error("Covariance matrix is singular, using pseudoinverse")
        inv_cov = np.linalg.pinv(cov_matrix)

    # Identify Virginia regions
    va_regions = [code for code in region_codes if code.startswith('VA-')]
    peer_candidates = [code for code in region_codes if not code.startswith('VA-')]

    logger.info(f"\nVirginia regions: {len(va_regions)}")
    logger.info(f"Peer candidates: {len(peer_candidates)}")

    # Calculate distances for each Virginia region
    peer_matches = {}

    for va_code in va_regions:
        va_idx = region_codes.index(va_code)
        va_vector = data_matrix[va_idx, :]

        distances = []

        for peer_code in peer_candidates:
            peer_idx = region_codes.index(peer_code)
            peer_vector = data_matrix[peer_idx, :]

            # Calculate Mahalanobis distance
            distance = mahalanobis_distance(va_vector, peer_vector, inv_cov)
            distances.append((peer_code, distance))

        # Sort by distance and take top 10
        distances.sort(key=lambda x: x[1])
        top_10 = distances[:10]

        peer_matches[va_code] = top_10

        logger.info(f"\n{va_code} ({ALL_REGIONS[va_code]['name']}):")
        logger.info("  Top 10 peer regions:")
        for i, (peer_code, dist) in enumerate(top_10, 1):
            peer_name = ALL_REGIONS[peer_code]['name']
            logger.info(f"    {i}. {peer_code} - {peer_name} (distance: {dist:.3f})")

    return peer_matches


def save_peer_matches(peer_matches: Dict, var_names: List[str], logger):
    """
    Save peer region matches to file.

    Args:
        peer_matches: Dict mapping VA regions to peer regions
        var_names: List of variable names used
        logger: Logger instance
    """
    output_file = project_root / 'data' / 'processed' / 'peer_regions.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output = {
        'metadata': {
            'method': 'Mahalanobis distance',
            'variables_used': var_names,
            'num_variables': len(var_names),
            'peers_per_region': 10,
            'virginia_regions': len(peer_matches)
        },
        'peer_matches': {}
    }

    # Format peer matches for JSON
    for va_code, peers in peer_matches.items():
        output['peer_matches'][va_code] = {
            'region_name': ALL_REGIONS[va_code]['name'],
            'peers': [
                {
                    'rank': i + 1,
                    'region_code': peer_code,
                    'region_name': ALL_REGIONS[peer_code]['name'],
                    'distance': round(distance, 4)
                }
                for i, (peer_code, distance) in enumerate(peers)
            ]
        }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"\n✓ Saved peer region matches to: {output_file}")


def main():
    """Main execution."""
    logger = setup_logger('calculate_peer_regions')

    logger.info("=" * 70)
    logger.info("CALCULATING PEER REGIONS (Mahalanobis Distance)")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len([r for r in ALL_REGIONS if r.startswith('VA-')])} Virginia regions\n")

    # Load matching variables
    matching_vars = load_matching_variables(logger)

    if not matching_vars:
        logger.error("Failed to load matching variables")
        return

    # Prepare data matrix
    data_matrix, region_codes, var_names = prepare_data_matrix(matching_vars, logger)

    if data_matrix.size == 0:
        logger.error("No data available for analysis")
        return

    # Calculate Mahalanobis distances
    peer_matches = calculate_mahalanobis_distances(data_matrix, region_codes, logger)

    # Save results
    save_peer_matches(peer_matches, var_names, logger)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Virginia regions analyzed: {len(peer_matches)}")
    logger.info(f"Variables used: {len(var_names)}")
    logger.info(f"Peer regions identified: {len(peer_matches) * 10}")
    logger.info("\n✓ Peer region matching complete!")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
