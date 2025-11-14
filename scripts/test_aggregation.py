"""
Test script for data aggregation module.

Tests aggregation from county to regional level.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.data_processing.aggregate_data import DataAggregator
from src.api_clients.census_api import CensusAPI
from src.utils.logging_setup import setup_logger


def test_aggregation_with_real_data():
    """Test aggregation using real Census data."""
    logger = setup_logger('test_aggregation')

    logger.info("=" * 70)
    logger.info("Testing Data Aggregation with Real Census Data")
    logger.info("=" * 70)

    # Initialize clients
    census = CensusAPI()
    agg = DataAggregator()

    # Test 1: Get Virginia population and aggregate
    logger.info("\nTest 1: Aggregate Virginia population to regions")
    try:
        # Get county-level population data
        va_pop_data = census.get_population(year=2022, state='51')
        logger.info(f"Retrieved data for {len(va_pop_data)} Virginia localities")

        # Convert to dict with FIPS as key
        county_pop = {}
        for record in va_pop_data:
            state_fips = record.get('state')
            county_fips = record.get('county')

            if state_fips and county_fips:
                # Build full FIPS code
                fips = state_fips + county_fips
                pop = record.get('B01001_001E')

                if pop and pop != 'N/A':
                    county_pop[fips] = int(pop)

        logger.info(f"Parsed {len(county_pop)} county population values")

        # Aggregate to regional level
        regional_pop = agg.aggregate_extensive_measure(county_pop)

        logger.info(f"\n✓ Aggregated to {len(regional_pop)} regions:")
        for region_code in sorted(regional_pop.keys()):
            from data.regional_groupings import ALL_REGIONS
            region_info = ALL_REGIONS.get(region_code, {})
            region_name = region_info.get('name', 'Unknown')
            pop = regional_pop[region_code]
            logger.info(f"  {region_code} ({region_name}): {pop:,}")

        # Get summary statistics
        summary = agg.get_regional_summary(regional_pop)
        logger.info(f"\nSummary Statistics:")
        logger.info(f"  Count: {summary['count']} regions")
        logger.info(f"  Total: {sum(regional_pop.values()):,}")
        logger.info(f"  Mean: {summary['mean']:,.0f}")
        logger.info(f"  Min: {summary['min']:,}")
        logger.info(f"  Max: {summary['max']:,}")

    except Exception as e:
        logger.error(f"✗ Population aggregation failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Aggregate median income (intensive measure)
    logger.info("\n" + "=" * 70)
    logger.info("Test 2: Aggregate Virginia median income (population-weighted)")
    try:
        # Get income data
        va_income_data = census.get_median_household_income(year=2022, state='51')
        logger.info(f"Retrieved income data for {len(va_income_data)} localities")

        # Convert to dict
        county_income = {}
        for record in va_income_data:
            state_fips = record.get('state')
            county_fips = record.get('county')

            if state_fips and county_fips:
                fips = state_fips + county_fips
                income = record.get('B19013_001E')

                if income and income != 'N/A' and income != '-666666666':
                    try:
                        county_income[fips] = int(income)
                    except:
                        pass

        logger.info(f"Parsed {len(county_income)} county income values")

        # Aggregate using population weights
        regional_income = agg.aggregate_intensive_measure(county_income, county_pop)

        logger.info(f"\n✓ Aggregated to {len(regional_income)} regions:")
        for region_code in sorted(regional_income.keys()):
            from data.regional_groupings import ALL_REGIONS
            region_info = ALL_REGIONS.get(region_code, {})
            region_name = region_info.get('name', 'Unknown')
            income = regional_income[region_code]
            if income:
                logger.info(f"  {region_code} ({region_name}): ${income:,.0f}")

        # Summary
        summary = agg.get_regional_summary(regional_income)
        logger.info(f"\nSummary Statistics:")
        logger.info(f"  Count: {summary['count']} regions")
        logger.info(f"  Mean: ${summary['mean']:,.0f}")
        logger.info(f"  Min: ${summary['min']:,}")
        logger.info(f"  Max: ${summary['max']:,}")

    except Exception as e:
        logger.error(f"✗ Income aggregation failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Validate completeness
    logger.info("\n" + "=" * 70)
    logger.info("Test 3: Validate data completeness")
    try:
        from data.regional_groupings import ALL_REGIONS

        # Get expected VA regions
        va_regions = [code for code in ALL_REGIONS.keys() if code.startswith('VA-')]

        validation = agg.validate_completeness(regional_pop, va_regions)

        logger.info(f"Coverage: {validation['coverage_percent']:.1f}%")
        logger.info(f"  Present: {validation['present']} / {validation['total_expected']}")
        logger.info(f"  Missing: {validation['missing']}")

        if validation['complete']:
            logger.info("  ✓ All expected regions have data")
        else:
            logger.warning(f"  Missing regions: {', '.join(validation['missing_regions'])}")

    except Exception as e:
        logger.error(f"✗ Validation failed: {e}")

    logger.info("\n" + "=" * 70)
    logger.info("Aggregation testing complete")
    logger.info("=" * 70)


if __name__ == '__main__':
    test_aggregation_with_real_data()
