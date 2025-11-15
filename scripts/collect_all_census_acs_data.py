#!/usr/bin/env python3
"""
Comprehensive Census ACS Data Collection Script

Collects all HIGH-confidence measures from Census ACS API for all 54 regions.

Measures collected:
- Demographics: Age distribution, median age
- Education: High school, some college, bachelor's degree attainment
- Economic: Labor force participation, unemployment
- Housing: Median home value, median rent, housing age
- Health: Percent uninsured
- Social: Single-parent households, Gini coefficient

Usage:
    python scripts/collect_all_census_acs_data.py --year 2022
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.census_api import CensusAPI
from src.processing.regional_aggregator import RegionalAggregator
from src.utils.logging_setup import setup_logger


# State FIPS codes
STATES = {
    'VA': '51',
    'MD': '24',
    'WV': '54',
    'NC': '37',
    'TN': '47',
    'KY': '21',
    'DC': '11'
}


class CensusACSCollector:
    """Collects all ACS measures for thriving index."""

    def __init__(self, year: int = 2022):
        """
        Initialize collector.

        Args:
            year: Year of ACS 5-year estimates
        """
        self.year = year
        self.census = CensusAPI()
        self.aggregator = RegionalAggregator()
        self.logger = setup_logger('census_acs_collector')

        self.logger.info(f"Initialized CensusACSCollector for {year} ACS 5-year estimates")

    def _fetch_and_aggregate(
        self,
        variable_codes: dict,
        measure_name: str,
        measure_type: str,
        calculation_func=None,
        weight_column: str = None
    ) -> pd.DataFrame:
        """
        Fetch ACS data for all states and aggregate to regions.

        Args:
            variable_codes: Dict mapping variable names to ACS codes
            measure_name: Name of the measure
            measure_type: 'extensive' or 'intensive'
            calculation_func: Optional function to calculate derived measure
            weight_column: Column to use for weighting (for intensive measures)

        Returns:
            DataFrame with regional data
        """
        self.logger.info(f"Collecting {measure_name}")

        all_data = []

        for state_abbr, state_fips in STATES.items():
            try:
                # Fetch data using existing methods or generic get_acs5_data
                variables = list(variable_codes.values())
                data = self.census.get_acs5_data(
                    year=self.year,
                    variables=variables,
                    geography='county:*',
                    state=state_fips
                )

                if not data:
                    self.logger.warning(f"  No data for {state_abbr}")
                    continue

                df = pd.DataFrame(data)

                # Rename columns
                rename_map = {v: k for k, v in variable_codes.items()}
                df = df.rename(columns=rename_map)

                # Build FIPS codes
                if 'county' in df.columns:
                    df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
                elif state_fips == '11':  # DC
                    df['fips'] = '11001'

                # Convert to numeric
                for col in variable_codes.keys():
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                # Apply calculation function if provided
                if calculation_func:
                    df = calculation_func(df)

                all_data.append(df)
                self.logger.debug(f"  Collected {len(df)} counties from {state_abbr}")

            except Exception as e:
                self.logger.error(f"  Error fetching {state_abbr}: {str(e)}")

        if not all_data:
            self.logger.error(f"No data collected for {measure_name}")
            return pd.DataFrame()

        # Combine all states
        combined = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"  Combined {len(combined)} county records")

        # Determine value column (the calculated measure)
        if calculation_func:
            # Assume calculation_func creates a column with the measure name
            value_column = measure_name.lower().replace(' ', '_').replace('-', '_')
        else:
            # Use the first variable as the value
            value_column = list(variable_codes.keys())[0]

        # Aggregate to regions
        regional = self.aggregator.aggregate_to_regions(
            county_data=combined,
            measure_type=measure_type,
            value_column=value_column,
            fips_column='fips',
            weight_column=weight_column
        )

        # Add metadata
        regional = self.aggregator.add_region_metadata(regional)

        self.logger.info(f"  Aggregated to {len(regional)} regions")

        return regional

    def collect_educational_attainment(self) -> dict:
        """
        Collect educational attainment measures.

        Returns:
            Dict with 3 DataFrames:
            - high_school_or_higher: % adults 25+ with HS diploma or higher
            - some_college: % adults 25+ with some college
            - bachelors_or_higher: % adults 25+ with bachelor's or higher
        """
        self.logger.info("=" * 70)
        self.logger.info("EDUCATIONAL ATTAINMENT")
        self.logger.info("=" * 70)

        results = {}

        # 1. High school graduate or higher (Table S1501)
        results['high_school_or_higher'] = self._fetch_and_aggregate(
            variable_codes={
                'pct_hs_or_higher': 'S1501_C02_014E'  # Percent HS grad or higher, 25+
            },
            measure_name='pct_hs_or_higher',
            measure_type='intensive',
            weight_column=None  # Already a percentage
        )

        # 2. Some college (Table B15003 - detailed educational attainment)
        # Sum of: Some college (<1 yr), Some college (>=1 yr, no degree), Associate's
        def calc_some_college(df):
            """Calculate % with some college from detailed table."""
            # Total population 25+
            total = df['total_25plus']
            # Some college, <1 year (B15003_019E)
            # Some college, >=1 year no degree (B15003_020E)
            # Associate's degree (B15003_021E)
            some_college_count = df['some_college_lt1'] + df['some_college_gte1'] + df['associates']
            df['pct_some_college'] = (some_college_count / total * 100).round(2)
            return df

        results['some_college'] = self._fetch_and_aggregate(
            variable_codes={
                'total_25plus': 'B15003_001E',
                'some_college_lt1': 'B15003_019E',
                'some_college_gte1': 'B15003_020E',
                'associates': 'B15003_021E'
            },
            measure_name='pct_some_college',
            measure_type='intensive',
            calculation_func=calc_some_college,
            weight_column='total_25plus'
        )

        # 3. Bachelor's degree or higher (Table S1501)
        results['bachelors_or_higher'] = self._fetch_and_aggregate(
            variable_codes={
                'pct_bachelors_or_higher': 'S1501_C02_015E'  # Percent bachelor's or higher, 25+
            },
            measure_name='pct_bachelors_or_higher',
            measure_type='intensive',
            weight_column=None  # Already a percentage
        )

        self.logger.info(f"Collected {len(results)} educational attainment measures")

        return results

    def collect_age_distribution(self) -> dict:
        """
        Collect age-related measures.

        Returns:
            Dict with 2 DataFrames:
            - median_age: Median age
            - pct_age_25_54: Percent of population age 25-54 (prime working age)
        """
        self.logger.info("=" * 70)
        self.logger.info("AGE DISTRIBUTION")
        self.logger.info("=" * 70)

        results = {}

        # 1. Median age (Table B01002)
        results['median_age'] = self._fetch_and_aggregate(
            variable_codes={
                'median_age': 'B01002_001E'
            },
            measure_name='median_age',
            measure_type='intensive',
            weight_column=None  # Use simple average for median
        )

        # 2. Percent age 25-54 (Table B01001 - Sex by Age)
        # Need to sum specific age ranges and divide by total population
        def calc_pct_age_25_54(df):
            """Calculate % age 25-54 from detailed age table."""
            total_pop = df['total_pop']

            # Males 25-54: B01001_011E through B01001_019E
            # Females 25-54: B01001_035E through B01001_043E
            male_25_54 = (
                df['male_25_29'] + df['male_30_34'] + df['male_35_39'] +
                df['male_40_44'] + df['male_45_49'] + df['male_50_54']
            )
            female_25_54 = (
                df['female_25_29'] + df['female_30_34'] + df['female_35_39'] +
                df['female_40_44'] + df['female_45_49'] + df['female_50_54']
            )

            total_25_54 = male_25_54 + female_25_54
            df['pct_age_25_54'] = (total_25_54 / total_pop * 100).round(2)
            df['total_age_25_54'] = total_25_54  # For weighting

            return df

        results['pct_age_25_54'] = self._fetch_and_aggregate(
            variable_codes={
                'total_pop': 'B01001_001E',
                'male_25_29': 'B01001_011E',
                'male_30_34': 'B01001_012E',
                'male_35_39': 'B01001_013E',
                'male_40_44': 'B01001_014E',
                'male_45_49': 'B01001_015E',
                'male_50_54': 'B01001_016E',
                'female_25_29': 'B01001_035E',
                'female_30_34': 'B01001_036E',
                'female_35_39': 'B01001_037E',
                'female_40_44': 'B01001_038E',
                'female_45_49': 'B01001_039E',
                'female_50_54': 'B01001_040E'
            },
            measure_name='pct_age_25_54',
            measure_type='intensive',
            calculation_func=calc_pct_age_25_54,
            weight_column='total_pop'
        )

        self.logger.info(f"Collected {len(results)} age distribution measures")

        return results

    def collect_labor_force(self) -> dict:
        """
        Collect labor force participation measures.

        Returns:
            Dict with 1 DataFrame:
            - labor_force_participation_rate: % of population 16+ in labor force
        """
        self.logger.info("=" * 70)
        self.logger.info("LABOR FORCE PARTICIPATION")
        self.logger.info("=" * 70)

        results = {}

        # Labor force participation rate (Table S2301)
        results['labor_force_participation_rate'] = self._fetch_and_aggregate(
            variable_codes={
                'labor_force_participation_rate': 'S2301_C02_001E'  # Percent, population 16+
            },
            measure_name='labor_force_participation_rate',
            measure_type='intensive',
            weight_column=None  # Already a percentage
        )

        self.logger.info(f"Collected labor force participation rate")

        return results

    def collect_housing(self) -> dict:
        """
        Collect housing-related measures.

        Returns:
            Dict with 3 DataFrames:
            - median_home_value: Median home value
            - median_gross_rent: Median gross rent
            - pct_housing_built_last_10_years: % of housing units built in last 10 years
        """
        self.logger.info("=" * 70)
        self.logger.info("HOUSING MEASURES")
        self.logger.info("=" * 70)

        results = {}

        # 1. Median home value (Table B25077)
        results['median_home_value'] = self._fetch_and_aggregate(
            variable_codes={
                'median_home_value': 'B25077_001E'
            },
            measure_name='median_home_value',
            measure_type='intensive',
            weight_column=None  # Use simple average for median
        )

        # 2. Median gross rent (Table B25064)
        results['median_gross_rent'] = self._fetch_and_aggregate(
            variable_codes={
                'median_gross_rent': 'B25064_001E'
            },
            measure_name='median_gross_rent',
            measure_type='intensive',
            weight_column=None  # Use simple average for median
        )

        # 3. Percent housing built in last 10 years (Table B25034)
        # For 2022 data (2018-2022 estimates), "last 10 years" = 2012 or later
        def calc_pct_recent_housing(df):
            """Calculate % of housing built in last 10 years."""
            total_units = df['total_housing_units']

            # Built 2014 or later (B25034_002E)
            # Built 2010 to 2013 (B25034_003E)
            recent_units = df['built_2014_later'] + df['built_2010_2013']

            df['pct_housing_built_last_10_years'] = (recent_units / total_units * 100).round(2)

            return df

        results['pct_housing_built_last_10_years'] = self._fetch_and_aggregate(
            variable_codes={
                'total_housing_units': 'B25034_001E',
                'built_2014_later': 'B25034_002E',
                'built_2010_2013': 'B25034_003E'
            },
            measure_name='pct_housing_built_last_10_years',
            measure_type='intensive',
            calculation_func=calc_pct_recent_housing,
            weight_column='total_housing_units'
        )

        self.logger.info(f"Collected {len(results)} housing measures")

        return results

    def collect_health_insurance(self) -> dict:
        """
        Collect health insurance coverage.

        Returns:
            Dict with 1 DataFrame:
            - pct_uninsured: % of population without health insurance
        """
        self.logger.info("=" * 70)
        self.logger.info("HEALTH INSURANCE")
        self.logger.info("=" * 70)

        results = {}

        # Percent uninsured (Table S2701)
        results['pct_uninsured'] = self._fetch_and_aggregate(
            variable_codes={
                'pct_uninsured': 'S2701_C05_001E'  # Percent uninsured
            },
            measure_name='pct_uninsured',
            measure_type='intensive',
            weight_column=None  # Already a percentage
        )

        self.logger.info(f"Collected health insurance coverage")

        return results

    def collect_family_structure(self) -> dict:
        """
        Collect family structure measures.

        Returns:
            Dict with 1 DataFrame:
            - pct_single_parent_households: % of children in single-parent households
        """
        self.logger.info("=" * 70)
        self.logger.info("FAMILY STRUCTURE")
        self.logger.info("=" * 70)

        results = {}

        # Percent of children in single-parent households (Table B09002)
        def calc_pct_single_parent(df):
            """Calculate % of children in single-parent households."""
            total_children = df['total_children_in_families']

            # Single parent = male householder, no spouse present + female householder, no spouse present
            single_parent_children = df['male_householder_no_spouse'] + df['female_householder_no_spouse']

            df['pct_single_parent_households'] = (single_parent_children / total_children * 100).round(2)

            return df

        results['pct_single_parent_households'] = self._fetch_and_aggregate(
            variable_codes={
                'total_children_in_families': 'B09002_001E',
                'male_householder_no_spouse': 'B09002_009E',
                'female_householder_no_spouse': 'B09002_015E'
            },
            measure_name='pct_single_parent_households',
            measure_type='intensive',
            calculation_func=calc_pct_single_parent,
            weight_column='total_children_in_families'
        )

        self.logger.info(f"Collected family structure measures")

        return results

    def collect_income_inequality(self) -> dict:
        """
        Collect income inequality measure.

        Returns:
            Dict with 1 DataFrame:
            - gini_coefficient: Gini index of income inequality
        """
        self.logger.info("=" * 70)
        self.logger.info("INCOME INEQUALITY")
        self.logger.info("=" * 70)

        results = {}

        # Gini coefficient (Table B19083)
        results['gini_coefficient'] = self._fetch_and_aggregate(
            variable_codes={
                'gini_coefficient': 'B19083_001E'
            },
            measure_name='gini_coefficient',
            measure_type='intensive',
            weight_column=None  # Use simple average
        )

        self.logger.info(f"Collected Gini coefficient")

        return results

    def collect_all(self) -> dict:
        """
        Collect all Census ACS measures.

        Returns:
            Dict mapping measure categories to DataFrames
        """
        self.logger.info("=" * 80)
        self.logger.info("COMPREHENSIVE CENSUS ACS DATA COLLECTION")
        self.logger.info(f"Year: {self.year} (5-year estimates)")
        self.logger.info("=" * 80)

        all_measures = {}

        # Collect each category
        all_measures.update(self.collect_educational_attainment())
        all_measures.update(self.collect_age_distribution())
        all_measures.update(self.collect_labor_force())
        all_measures.update(self.collect_housing())
        all_measures.update(self.collect_health_insurance())
        all_measures.update(self.collect_family_structure())
        all_measures.update(self.collect_income_inequality())

        self.logger.info("=" * 80)
        self.logger.info(f"TOTAL MEASURES COLLECTED: {len(all_measures)}")
        self.logger.info("=" * 80)

        return all_measures

    def save_all(self, measures: dict, output_dir: Path):
        """
        Save all measures to CSV files.

        Args:
            measures: Dict mapping measure names to DataFrames
            output_dir: Directory to save files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Saving {len(measures)} measures to {output_dir}")

        for measure_name, df in measures.items():
            if df is not None and not df.empty:
                filename = f"{measure_name}_{self.year}_regional.csv"
                filepath = output_dir / filename
                df.to_csv(filepath, index=False)
                self.logger.info(f"  Saved {measure_name}: {len(df)} regions → {filepath.name}")
            else:
                self.logger.warning(f"  Skipped {measure_name}: No data")

        self.logger.info(f"All measures saved to {output_dir}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Collect comprehensive Census ACS data for Virginia Thriving Index"
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2022,
        help='Year of ACS 5-year estimates (default: 2022)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory for CSV files (default: data/regional_data)'
    )

    args = parser.parse_args()

    # Set output directory
    if args.output_dir is None:
        output_dir = project_root / 'data' / 'regional_data'
    else:
        output_dir = args.output_dir

    # Initialize collector
    collector = CensusACSCollector(year=args.year)

    # Collect all measures
    start_time = datetime.now()
    measures = collector.collect_all()
    end_time = datetime.now()

    # Save to CSV
    print()
    print("=" * 80)
    print("SAVING DATA")
    print("=" * 80)
    collector.save_all(measures, output_dir)

    # Print summary
    print()
    print("=" * 80)
    print("COLLECTION SUMMARY")
    print("=" * 80)
    print(f"Year: {args.year}")
    print(f"Measures collected: {len(measures)}")
    print(f"Output directory: {output_dir}")
    print(f"Time elapsed: {end_time - start_time}")
    print()

    for measure_name, df in measures.items():
        if df is not None and not df.empty:
            value_col = [c for c in df.columns if c not in ['region_code', 'region_name', 'state', 'num_counties', 'total_weight']]
            if value_col:
                value_col = value_col[0]
                print(f"{measure_name}:")
                print(f"  Regions: {len(df)}")
                print(f"  Range: {df[value_col].min():.2f} - {df[value_col].max():.2f}")
                print(f"  Mean: {df[value_col].mean():.2f}")

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
