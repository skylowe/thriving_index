"""
Data Aggregation Module

Aggregates county-level data to multi-county regional groupings.
Handles both extensive measures (sums) and intensive measures (weighted averages).
"""

from typing import Dict, List, Optional, Union
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.utils.fips_to_region import get_region_for_fips, get_all_fips_in_region
from data.regional_groupings import ALL_REGIONS


logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Aggregates county-level data to regional level.

    Handles two types of aggregation:
    1. Extensive measures (counts, totals): Simple sum
    2. Intensive measures (rates, percentages): Population-weighted average
    """

    def __init__(self):
        """Initialize the data aggregator."""
        self.logger = logging.getLogger(f"{__name__}.DataAggregator")

    def aggregate_extensive_measure(
        self,
        county_data: Dict[str, float],
        fips_field: str = 'fips'
    ) -> Dict[str, float]:
        """
        Aggregate an extensive measure (e.g., total population, total employment).

        Uses simple summation across counties in each region.

        Args:
            county_data: Dictionary mapping FIPS code to value
            fips_field: Name of the FIPS code field (if county_data contains dicts)

        Returns:
            Dictionary mapping region code to aggregated value

        Example:
            >>> county_pop = {'51059': 1000000, '51013': 200000}  # Fairfax, Arlington
            >>> agg = DataAggregator()
            >>> regional_pop = agg.aggregate_extensive_measure(county_pop)
            >>> regional_pop['VA-8']  # Northern Virginia
            1200000
        """
        regional_data = {}

        for fips_code, value in county_data.items():
            # Skip if value is None or invalid
            if value is None:
                continue

            # Get region for this FIPS code
            region_code = get_region_for_fips(fips_code)

            if region_code is None:
                self.logger.warning(f"FIPS {fips_code} not mapped to any region")
                continue

            # Add to regional total
            if region_code not in regional_data:
                regional_data[region_code] = 0

            regional_data[region_code] += float(value)

        return regional_data

    def aggregate_intensive_measure(
        self,
        county_data: Dict[str, float],
        population_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Aggregate an intensive measure (e.g., median income, poverty rate).

        Uses population-weighted average across counties in each region.

        Args:
            county_data: Dictionary mapping FIPS code to value
            population_weights: Dictionary mapping FIPS code to population

        Returns:
            Dictionary mapping region code to weighted average value

        Example:
            >>> county_income = {'51059': 120000, '51013': 110000}
            >>> county_pop = {'51059': 1000000, '51013': 200000}
            >>> agg = DataAggregator()
            >>> regional_income = agg.aggregate_intensive_measure(county_income, county_pop)
            >>> regional_income['VA-8']  # Weighted average
            118333.33
        """
        regional_data = {}
        regional_weights = {}

        for fips_code, value in county_data.items():
            # Skip if value is None or invalid
            if value is None or fips_code not in population_weights:
                continue

            weight = population_weights[fips_code]
            if weight is None or weight <= 0:
                continue

            # Get region for this FIPS code
            region_code = get_region_for_fips(fips_code)

            if region_code is None:
                self.logger.warning(f"FIPS {fips_code} not mapped to any region")
                continue

            # Add to regional weighted sum
            if region_code not in regional_data:
                regional_data[region_code] = 0
                regional_weights[region_code] = 0

            regional_data[region_code] += float(value) * float(weight)
            regional_weights[region_code] += float(weight)

        # Calculate weighted averages
        result = {}
        for region_code in regional_data:
            if regional_weights[region_code] > 0:
                result[region_code] = regional_data[region_code] / regional_weights[region_code]
            else:
                result[region_code] = None

        return result

    def aggregate_from_list(
        self,
        county_data_list: List[Dict],
        value_field: str,
        fips_field: str = 'fips',
        aggregation_type: str = 'extensive',
        population_field: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Aggregate data from a list of county records.

        Args:
            county_data_list: List of dictionaries with county data
            value_field: Name of the field containing the value to aggregate
            fips_field: Name of the field containing the FIPS code (default: 'fips')
            aggregation_type: 'extensive' or 'intensive'
            population_field: Name of population field (required for intensive aggregation)

        Returns:
            Dictionary mapping region code to aggregated value

        Example:
            >>> data = [
            ...     {'fips': '51059', 'population': 1000000, 'median_income': 120000},
            ...     {'fips': '51013', 'population': 200000, 'median_income': 110000}
            ... ]
            >>> agg = DataAggregator()
            >>> # Extensive aggregation (sum)
            >>> pop = agg.aggregate_from_list(data, 'population', aggregation_type='extensive')
            >>> # Intensive aggregation (weighted average)
            >>> income = agg.aggregate_from_list(
            ...     data, 'median_income',
            ...     aggregation_type='intensive',
            ...     population_field='population'
            ... )
        """
        # Convert list to dictionary
        county_data = {}
        population_weights = {}

        for record in county_data_list:
            fips = record.get(fips_field)
            value = record.get(value_field)

            if fips and value is not None:
                county_data[fips] = value

                if population_field and population_field in record:
                    population_weights[fips] = record[population_field]

        # Aggregate based on type
        if aggregation_type == 'extensive':
            return self.aggregate_extensive_measure(county_data)
        elif aggregation_type == 'intensive':
            if not population_weights:
                raise ValueError("Intensive aggregation requires population weights")
            return self.aggregate_intensive_measure(county_data, population_weights)
        else:
            raise ValueError(f"Unknown aggregation type: {aggregation_type}")

    def get_regional_summary(self, regional_data: Dict[str, float]) -> Dict:
        """
        Get summary statistics for regional data.

        Args:
            regional_data: Dictionary mapping region code to value

        Returns:
            Dictionary with summary statistics
        """
        values = [v for v in regional_data.values() if v is not None]

        if not values:
            return {
                'count': 0,
                'min': None,
                'max': None,
                'mean': None,
                'median': None
            }

        values_sorted = sorted(values)
        n = len(values)

        return {
            'count': n,
            'min': values_sorted[0],
            'max': values_sorted[-1],
            'mean': sum(values) / n,
            'median': values_sorted[n // 2] if n % 2 == 1 else (values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2
        }

    def validate_completeness(
        self,
        regional_data: Dict[str, float],
        expected_regions: Optional[List[str]] = None
    ) -> Dict:
        """
        Validate that all expected regions have data.

        Args:
            regional_data: Dictionary mapping region code to value
            expected_regions: List of expected region codes (default: all 54 regions)

        Returns:
            Dictionary with validation results
        """
        if expected_regions is None:
            expected_regions = list(ALL_REGIONS.keys())

        missing = []
        present = []

        for region in expected_regions:
            if region in regional_data and regional_data[region] is not None:
                present.append(region)
            else:
                missing.append(region)

        return {
            'total_expected': len(expected_regions),
            'present': len(present),
            'missing': len(missing),
            'coverage_percent': (len(present) / len(expected_regions) * 100) if expected_regions else 0,
            'missing_regions': missing,
            'complete': len(missing) == 0
        }


# Convenience functions for common aggregations

def aggregate_population(county_population: Dict[str, float]) -> Dict[str, float]:
    """
    Aggregate total population to regional level.

    Args:
        county_population: Dictionary mapping FIPS code to population

    Returns:
        Dictionary mapping region code to total population
    """
    agg = DataAggregator()
    return agg.aggregate_extensive_measure(county_population)


def aggregate_income(
    county_income: Dict[str, float],
    county_population: Dict[str, float]
) -> Dict[str, float]:
    """
    Aggregate median income to regional level (population-weighted).

    Args:
        county_income: Dictionary mapping FIPS code to median income
        county_population: Dictionary mapping FIPS code to population

    Returns:
        Dictionary mapping region code to weighted average income
    """
    agg = DataAggregator()
    return agg.aggregate_intensive_measure(county_income, county_population)


def aggregate_rate(
    county_rate: Dict[str, float],
    county_population: Dict[str, float]
) -> Dict[str, float]:
    """
    Aggregate a rate/percentage to regional level (population-weighted).

    Args:
        county_rate: Dictionary mapping FIPS code to rate (e.g., poverty rate)
        county_population: Dictionary mapping FIPS code to population

    Returns:
        Dictionary mapping region code to weighted average rate
    """
    agg = DataAggregator()
    return agg.aggregate_intensive_measure(county_rate, county_population)


if __name__ == '__main__':
    # Example usage
    print("Data Aggregation Module")
    print("=" * 70)

    # Example: Aggregate population for Northern Virginia
    example_county_pop = {
        '51059': 1150309,  # Fairfax County
        '51013': 238643,   # Arlington County
        '51107': 456599,   # Loudoun County
        '51510': 159467,   # Alexandria City
        '51153': 470335    # Prince William County
    }

    agg = DataAggregator()

    print("\nExample 1: Extensive Aggregation (Total Population)")
    print("County-level data (Northern Virginia counties):")
    for fips, pop in example_county_pop.items():
        print(f"  {fips}: {pop:,}")

    regional_pop = agg.aggregate_extensive_measure(example_county_pop)
    print(f"\nRegional total:")
    for region, pop in regional_pop.items():
        region_info = ALL_REGIONS.get(region, {})
        print(f"  {region} ({region_info.get('name', 'Unknown')}): {pop:,}")

    # Example: Aggregate median income (intensive)
    print("\n" + "=" * 70)
    print("Example 2: Intensive Aggregation (Median Income)")

    example_county_income = {
        '51059': 124831,  # Fairfax County
        '51013': 137387,  # Arlington County
        '51107': 147055,  # Loudoun County
        '51510': 93847,   # Alexandria City
        '51153': 101258   # Prince William County
    }

    print("County-level data:")
    for fips in example_county_pop.keys():
        pop = example_county_pop[fips]
        income = example_county_income[fips]
        print(f"  {fips}: ${income:,} (pop: {pop:,})")

    regional_income = agg.aggregate_intensive_measure(example_county_income, example_county_pop)
    print(f"\nRegional weighted average:")
    for region, income in regional_income.items():
        region_info = ALL_REGIONS.get(region, {})
        print(f"  {region} ({region_info.get('name', 'Unknown')}): ${income:,.2f}")

    # Validation example
    print("\n" + "=" * 70)
    print("Example 3: Validation")

    validation = agg.validate_completeness(regional_pop)
    print(f"Coverage: {validation['coverage_percent']:.1f}%")
    print(f"  Present: {validation['present']} regions")
    print(f"  Missing: {validation['missing']} regions")
    if validation['missing_regions']:
        print(f"  Missing regions: {', '.join(validation['missing_regions'][:5])}")
