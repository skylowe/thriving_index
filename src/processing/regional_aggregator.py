"""
Regional Data Aggregator

This module aggregates county-level data to multi-county regional groupings.
Essential for converting API data (collected at county level) to regional data
for the Virginia Thriving Index analysis.

Aggregation Methods:
- Extensive measures (totals): Simple sum
  - Examples: Population, total employment, number of establishments
- Intensive measures (rates/percentages): Population-weighted average
  - Examples: Unemployment rate, poverty rate, median income
- Special cases handled appropriately

Usage:
    from src.processing.regional_aggregator import RegionalAggregator

    aggregator = RegionalAggregator()

    # Aggregate county data to regions
    regional_data = aggregator.aggregate_to_regions(
        county_data=county_df,
        measure_type='intensive',  # or 'extensive'
        value_column='median_income',
        fips_column='fips',
        weight_column='population'  # for intensive measures
    )
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Literal
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.utils.fips_to_region import get_region_for_fips, get_all_fips_in_region
from src.utils.regions_v2 import get_all_region_codes, get_region_info
from src.utils.logging_setup import setup_logger

logger = setup_logger('regional_aggregator')


class RegionalAggregator:
    """
    Aggregates county-level data to multi-county regional groupings.
    """

    def __init__(self):
        """Initialize the aggregator."""
        self.region_codes = get_all_region_codes()
        logger.info(f"Initialized RegionalAggregator with {len(self.region_codes)} regions")

    def aggregate_to_regions(
        self,
        county_data: pd.DataFrame,
        measure_type: Literal['extensive', 'intensive'],
        value_column: str,
        fips_column: str = 'fips',
        weight_column: Optional[str] = None,
        region_column: str = 'region_code'
    ) -> pd.DataFrame:
        """
        Aggregate county-level data to regional level.

        Args:
            county_data: DataFrame with county-level data
            measure_type: 'extensive' (sum) or 'intensive' (weighted average)
            value_column: Column containing the values to aggregate
            fips_column: Column containing FIPS codes
            weight_column: Column for weights (required for intensive measures)
            region_column: Name for output region code column

        Returns:
            DataFrame with regional-level aggregated data

        Raises:
            ValueError: If required columns missing or invalid measure_type
        """
        # Validate inputs
        if measure_type not in ['extensive', 'intensive']:
            raise ValueError(f"measure_type must be 'extensive' or 'intensive', got '{measure_type}'")

        if fips_column not in county_data.columns:
            raise ValueError(f"FIPS column '{fips_column}' not found in data")

        if value_column not in county_data.columns:
            raise ValueError(f"Value column '{value_column}' not found in data")

        if measure_type == 'intensive' and not weight_column:
            raise ValueError("weight_column required for intensive measures")

        if measure_type == 'intensive' and weight_column not in county_data.columns:
            raise ValueError(f"Weight column '{weight_column}' not found in data")

        # Make a copy to avoid modifying original
        df = county_data.copy()

        # Ensure FIPS codes are strings
        df[fips_column] = df[fips_column].astype(str)

        # Map FIPS codes to regions
        df[region_column] = df[fips_column].apply(get_region_for_fips)

        # Drop counties that couldn't be mapped to a region
        unmapped = df[df[region_column].isna()]
        if len(unmapped) > 0:
            logger.warning(f"Dropping {len(unmapped)} rows with unmapped FIPS codes")
            df = df[df[region_column].notna()]

        # Aggregate based on measure type
        if measure_type == 'extensive':
            # Extensive: Simple sum
            regional_data = self._aggregate_extensive(
                df, value_column, region_column
            )
        else:
            # Intensive: Population-weighted average
            regional_data = self._aggregate_intensive(
                df, value_column, weight_column, region_column
            )

        logger.info(f"Aggregated {len(df)} county records to {len(regional_data)} regions")

        return regional_data

    def _aggregate_extensive(
        self,
        df: pd.DataFrame,
        value_column: str,
        region_column: str
    ) -> pd.DataFrame:
        """
        Aggregate extensive measures (simple sum).

        Args:
            df: DataFrame with county data and region codes
            value_column: Column to sum
            region_column: Region code column

        Returns:
            DataFrame with regional sums
        """
        # Group by region and sum
        regional_data = df.groupby(region_column).agg({
            value_column: 'sum'
        }).reset_index()

        # Count counties per region
        county_counts = df.groupby(region_column).size().reset_index(name='num_counties')
        regional_data = regional_data.merge(county_counts, on=region_column)

        return regional_data

    def _aggregate_intensive(
        self,
        df: pd.DataFrame,
        value_column: str,
        weight_column: str,
        region_column: str
    ) -> pd.DataFrame:
        """
        Aggregate intensive measures (population-weighted average).

        Args:
            df: DataFrame with county data and region codes
            value_column: Column to average
            weight_column: Column for weights (e.g., population)
            region_column: Region code column

        Returns:
            DataFrame with regional weighted averages
        """
        # Remove rows with missing values or weights
        df_clean = df.dropna(subset=[value_column, weight_column])

        if len(df_clean) < len(df):
            logger.warning(
                f"Dropped {len(df) - len(df_clean)} rows with missing "
                f"values or weights for intensive aggregation"
            )

        # Calculate weighted values
        df_clean['weighted_value'] = df_clean[value_column] * df_clean[weight_column]

        # Group by region and sum
        regional_data = df_clean.groupby(region_column).agg({
            'weighted_value': 'sum',
            weight_column: 'sum'
        }).reset_index()

        # Calculate weighted average
        regional_data[value_column] = (
            regional_data['weighted_value'] / regional_data[weight_column]
        )

        # Count counties per region
        county_counts = df_clean.groupby(region_column).size().reset_index(name='num_counties')
        regional_data = regional_data.merge(county_counts, on=region_column)

        # Clean up temporary columns
        regional_data = regional_data.drop(columns=['weighted_value'])
        regional_data = regional_data.rename(columns={weight_column: 'total_weight'})

        return regional_data

    def aggregate_multiple_measures(
        self,
        county_data: pd.DataFrame,
        measures: List[Dict],
        fips_column: str = 'fips'
    ) -> pd.DataFrame:
        """
        Aggregate multiple measures at once.

        Args:
            county_data: DataFrame with county-level data
            measures: List of measure specifications, each a dict with:
                - 'column': Column name
                - 'type': 'extensive' or 'intensive'
                - 'weight': Weight column name (for intensive measures)
            fips_column: Column containing FIPS codes

        Returns:
            DataFrame with all measures aggregated to regional level

        Example:
            measures = [
                {'column': 'population', 'type': 'extensive'},
                {'column': 'median_income', 'type': 'intensive', 'weight': 'population'},
                {'column': 'unemployment_rate', 'type': 'intensive', 'weight': 'labor_force'}
            ]
        """
        # Start with region codes
        df = county_data.copy()
        df[fips_column] = df[fips_column].astype(str)
        df['region_code'] = df[fips_column].apply(get_region_for_fips)
        df = df[df['region_code'].notna()]

        # Aggregate each measure
        regional_dfs = []

        for measure_spec in measures:
            column = measure_spec['column']
            measure_type = measure_spec['type']

            if column not in df.columns:
                logger.warning(f"Column '{column}' not found, skipping")
                continue

            if measure_type == 'extensive':
                # Sum
                agg_df = df.groupby('region_code')[column].sum().reset_index()
            elif measure_type == 'intensive':
                # Weighted average
                weight_col = measure_spec.get('weight')
                if not weight_col or weight_col not in df.columns:
                    logger.warning(
                        f"Weight column '{weight_col}' not found for '{column}', skipping"
                    )
                    continue

                df_clean = df.dropna(subset=[column, weight_col])
                df_clean['weighted'] = df_clean[column] * df_clean[weight_col]

                agg_df = df_clean.groupby('region_code').agg({
                    'weighted': 'sum',
                    weight_col: 'sum'
                }).reset_index()

                agg_df[column] = agg_df['weighted'] / agg_df[weight_col]
                agg_df = agg_df[['region_code', column]]

            regional_dfs.append(agg_df)

        # Merge all measures
        if not regional_dfs:
            logger.error("No measures successfully aggregated")
            return pd.DataFrame()

        result = regional_dfs[0]
        for df_to_merge in regional_dfs[1:]:
            result = result.merge(df_to_merge, on='region_code', how='outer')

        logger.info(f"Aggregated {len(measures)} measures to {len(result)} regions")

        return result

    def add_region_metadata(
        self,
        regional_data: pd.DataFrame,
        region_column: str = 'region_code'
    ) -> pd.DataFrame:
        """
        Add region metadata to aggregated data.

        Args:
            regional_data: DataFrame with regional data
            region_column: Column containing region codes

        Returns:
            DataFrame with added metadata columns
        """
        df = regional_data.copy()

        # Add region info
        df['region_name'] = df[region_column].apply(
            lambda code: get_region_info(code).get('name', '') if get_region_info(code) else ''
        )

        df['state'] = df[region_column].apply(
            lambda code: code.split('-')[0] if isinstance(code, str) else ''
        )

        return df


def validate_aggregation(
    county_data: pd.DataFrame,
    regional_data: pd.DataFrame,
    measure_column: str,
    measure_type: Literal['extensive', 'intensive']
) -> Dict:
    """
    Validate that aggregation was performed correctly.

    Args:
        county_data: Original county-level data
        regional_data: Aggregated regional data
        measure_column: Column that was aggregated
        measure_type: Type of aggregation performed

    Returns:
        Dict with validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    # Check for extensive measures (totals should match)
    if measure_type == 'extensive':
        county_total = county_data[measure_column].sum()
        regional_total = regional_data[measure_column].sum()

        diff_pct = abs(county_total - regional_total) / county_total * 100 if county_total > 0 else 0

        if diff_pct > 0.1:  # More than 0.1% difference
            results['valid'] = False
            results['errors'].append(
                f"Total mismatch: County={county_total:,.0f}, "
                f"Regional={regional_total:,.0f}, Diff={diff_pct:.2f}%"
            )
        else:
            results['warnings'].append(
                f"Totals match within tolerance: {diff_pct:.4f}% difference"
            )

    return results


if __name__ == '__main__':
    # Example usage and testing
    print("Regional Aggregator Module")
    print("=" * 70)

    # Create sample county data
    sample_data = pd.DataFrame({
        'fips': ['51059', '51510', '51013', '51107', '51153'],  # NoVA counties/cities
        'county_name': ['Fairfax County', 'Alexandria', 'Arlington', 'Loudoun', 'Prince William'],
        'population': [1150309, 159467, 238643, 421588, 481131],
        'median_income': [124831, 85930, 132830, 146847, 106610],
        'total_employment': [650000, 85000, 135000, 210000, 220000]
    })

    print("\nSample county data (Northern Virginia):")
    print(sample_data)

    # Initialize aggregator
    aggregator = RegionalAggregator()

    # Test extensive aggregation (population - should sum)
    print("\n" + "=" * 70)
    print("Test 1: Extensive Aggregation (Population)")
    print("-" * 70)

    pop_regional = aggregator.aggregate_to_regions(
        county_data=sample_data,
        measure_type='extensive',
        value_column='population',
        fips_column='fips'
    )

    pop_regional = aggregator.add_region_metadata(pop_regional)
    print(pop_regional[['region_code', 'region_name', 'population', 'num_counties']])

    # Test intensive aggregation (median income - should weight by population)
    print("\n" + "=" * 70)
    print("Test 2: Intensive Aggregation (Median Income)")
    print("-" * 70)

    income_regional = aggregator.aggregate_to_regions(
        county_data=sample_data,
        measure_type='intensive',
        value_column='median_income',
        fips_column='fips',
        weight_column='population'
    )

    income_regional = aggregator.add_region_metadata(income_regional)
    print(income_regional[['region_code', 'region_name', 'median_income', 'num_counties']])

    # Test multiple measures at once
    print("\n" + "=" * 70)
    print("Test 3: Multiple Measures Aggregation")
    print("-" * 70)

    measures = [
        {'column': 'population', 'type': 'extensive'},
        {'column': 'total_employment', 'type': 'extensive'},
        {'column': 'median_income', 'type': 'intensive', 'weight': 'population'}
    ]

    multi_regional = aggregator.aggregate_multiple_measures(
        county_data=sample_data,
        measures=measures
    )

    multi_regional = aggregator.add_region_metadata(multi_regional)
    print(multi_regional)

    # Validation
    print("\n" + "=" * 70)
    print("Validation")
    print("-" * 70)

    validation = validate_aggregation(
        county_data=sample_data,
        regional_data=pop_regional,
        measure_column='population',
        measure_type='extensive'
    )

    print(f"Valid: {validation['valid']}")
    for warning in validation['warnings']:
        print(f"  ⚠ {warning}")
    for error in validation['errors']:
        print(f"  ✗ {error}")
