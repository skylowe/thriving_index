"""
Regional Data Collector for Virginia Thriving Index

This module orchestrates data collection from Census, BEA, and BLS APIs
and aggregates county-level data to multi-county regional groupings.

Usage:
    collector = RegionalDataCollector()
    data = collector.collect_all_measures(year=2022)
"""

from typing import Dict, List, Optional, Literal
import pandas as pd
from pathlib import Path

from ..api_clients.census_api import CensusAPI
from ..api_clients.bea_api import BEAAPI
from ..api_clients.bls_api import BLSAPI
from ..processing.regional_aggregator import RegionalAggregator
from ..utils.logging_setup import setup_logger
from ..utils.regions_v2 import get_all_regions


class RegionalDataCollector:
    """
    Collects county-level data from APIs and aggregates to regional groupings.

    Handles data from:
    - Census Bureau (ACS 5-year estimates)
    - Bureau of Economic Analysis (BEA)
    - Bureau of Labor Statistics (BLS)
    """

    def __init__(self):
        """Initialize API clients and aggregator."""
        self.census = CensusAPI()
        self.bea = BEAAPI()
        self.bls = BLSAPI()
        self.aggregator = RegionalAggregator()
        self.logger = setup_logger('regional_data_collector')

        # State FIPS codes for all states in study
        self.states = {
            'VA': '51',
            'MD': '24',
            'WV': '54',
            'NC': '37',
            'TN': '47',
            'KY': '21',
            'DC': '11'
        }

        self.logger.info(f"Initialized RegionalDataCollector for {len(self.states)} states")

    def _fetch_census_measure(
        self,
        year: int,
        method_name: str,
        measure_column: str,
        measure_type: Literal['extensive', 'intensive'],
        weight_column: Optional[str] = None,
        rename_map: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Fetch a Census measure for all states and aggregate to regions.

        Args:
            year: Year of ACS 5-year estimates
            method_name: Census API method name (e.g., 'get_population')
            measure_column: Column name for the measure to aggregate
            measure_type: 'extensive' (sum) or 'intensive' (weighted avg)
            weight_column: Column to use as weight (required for intensive)
            rename_map: Dict to rename variable codes to friendly names

        Returns:
            DataFrame with regional aggregated data
        """
        self.logger.info(f"Fetching {method_name} from Census API for {year}")

        all_data = []
        method = getattr(self.census, method_name)

        # Fetch data for each state
        for state_abbr, state_fips in self.states.items():
            try:
                data = method(year=year, state=state_fips)
                if data:
                    df = pd.DataFrame(data)

                    # Build FIPS codes
                    if 'county' in df.columns:
                        df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
                    elif 'state' in df.columns and state_fips == '11':
                        # DC special case
                        df['fips'] = '11001'

                    # Rename variable codes if provided
                    if rename_map:
                        df = df.rename(columns=rename_map)

                    all_data.append(df)
                    self.logger.debug(f"  Retrieved {len(df)} records for {state_abbr}")
            except Exception as e:
                self.logger.error(f"  Error fetching {state_abbr} data: {str(e)}")

        if not all_data:
            self.logger.warning(f"No data retrieved for {method_name}")
            return pd.DataFrame()

        # Combine all states
        combined = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"  Combined {len(combined)} county records across all states")

        # Convert to numeric
        for col in [measure_column] + ([weight_column] if weight_column else []):
            if col in combined.columns:
                combined[col] = pd.to_numeric(combined[col], errors='coerce')

        # Aggregate to regions
        regional = self.aggregator.aggregate_to_regions(
            county_data=combined,
            measure_type=measure_type,
            value_column=measure_column,
            fips_column='fips',
            weight_column=weight_column
        )

        # Add metadata
        regional = self.aggregator.add_region_metadata(regional)

        self.logger.info(f"  Aggregated to {len(regional)} regions")

        return regional

    def collect_population(self, year: int = 2022) -> pd.DataFrame:
        """
        Collect total population by region.

        Args:
            year: Year of ACS 5-year estimates

        Returns:
            DataFrame with regional population
        """
        return self._fetch_census_measure(
            year=year,
            method_name='get_population',
            measure_column='population',
            measure_type='extensive',
            rename_map={'B01001_001E': 'population'}
        )

    def collect_median_household_income(
        self,
        year: int = 2022,
        population_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Collect median household income by region (population-weighted).

        Args:
            year: Year of ACS 5-year estimates
            population_df: Optional pre-fetched population data for weighting

        Returns:
            DataFrame with regional median household income
        """
        # Need population for weighting
        if population_df is None:
            self.logger.info("Fetching population data for weighting")
            population_df = self.collect_population(year=year)

        # Fetch income data
        self.logger.info(f"Fetching median household income from Census API for {year}")

        all_data = []

        for state_abbr, state_fips in self.states.items():
            try:
                # Get income data
                income_data = self.census.get_median_household_income(year=year, state=state_fips)

                # Get population data for this state
                pop_data = self.census.get_population(year=year, state=state_fips)

                if income_data and pop_data:
                    income_df = pd.DataFrame(income_data)
                    pop_df = pd.DataFrame(pop_data)

                    # Build FIPS codes
                    if 'county' in income_df.columns:
                        income_df['fips'] = state_fips + income_df['county'].astype(str).str.zfill(3)
                        pop_df['fips'] = state_fips + pop_df['county'].astype(str).str.zfill(3)
                    elif state_fips == '11':
                        income_df['fips'] = '11001'
                        pop_df['fips'] = '11001'

                    # Rename columns
                    income_df = income_df.rename(columns={'B19013_001E': 'median_household_income'})
                    pop_df = pop_df.rename(columns={'B01001_001E': 'population'})

                    # Merge
                    merged = income_df.merge(
                        pop_df[['fips', 'population']],
                        on='fips',
                        how='left'
                    )

                    all_data.append(merged)
                    self.logger.debug(f"  Retrieved {len(merged)} records for {state_abbr}")
            except Exception as e:
                self.logger.error(f"  Error fetching {state_abbr} data: {str(e)}")

        if not all_data:
            self.logger.warning("No income data retrieved")
            return pd.DataFrame()

        # Combine all states
        combined = pd.concat(all_data, ignore_index=True)

        # Convert to numeric
        combined['median_household_income'] = pd.to_numeric(
            combined['median_household_income'],
            errors='coerce'
        )
        combined['population'] = pd.to_numeric(combined['population'], errors='coerce')

        # Aggregate to regions (population-weighted)
        regional = self.aggregator.aggregate_to_regions(
            county_data=combined,
            measure_type='intensive',
            value_column='median_household_income',
            fips_column='fips',
            weight_column='population'
        )

        # Add metadata
        regional = self.aggregator.add_region_metadata(regional)

        self.logger.info(f"  Aggregated to {len(regional)} regions")

        return regional

    def collect_poverty_rate(self, year: int = 2022) -> pd.DataFrame:
        """
        Collect poverty rate by region (population-weighted).

        Args:
            year: Year of ACS 5-year estimates

        Returns:
            DataFrame with regional poverty rate
        """
        self.logger.info(f"Fetching poverty data from Census API for {year}")

        all_data = []

        for state_abbr, state_fips in self.states.items():
            try:
                data = self.census.get_poverty_rate(year=year, state=state_fips)
                if data:
                    df = pd.DataFrame(data)

                    # Build FIPS codes
                    if 'county' in df.columns:
                        df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
                    elif state_fips == '11':
                        df['fips'] = '11001'

                    # Rename columns
                    df = df.rename(columns={
                        'B17001_001E': 'poverty_universe',
                        'B17001_002E': 'poverty_below'
                    })

                    # Calculate poverty rate
                    df['poverty_universe'] = pd.to_numeric(df['poverty_universe'], errors='coerce')
                    df['poverty_below'] = pd.to_numeric(df['poverty_below'], errors='coerce')
                    df['poverty_rate'] = (df['poverty_below'] / df['poverty_universe'] * 100).round(2)

                    all_data.append(df)
                    self.logger.debug(f"  Retrieved {len(df)} records for {state_abbr}")
            except Exception as e:
                self.logger.error(f"  Error fetching {state_abbr} data: {str(e)}")

        if not all_data:
            self.logger.warning("No poverty data retrieved")
            return pd.DataFrame()

        # Combine all states
        combined = pd.concat(all_data, ignore_index=True)

        # Aggregate to regions (population-weighted)
        regional = self.aggregator.aggregate_to_regions(
            county_data=combined,
            measure_type='intensive',
            value_column='poverty_rate',
            fips_column='fips',
            weight_column='poverty_universe'
        )

        # Add metadata
        regional = self.aggregator.add_region_metadata(regional)

        self.logger.info(f"  Aggregated to {len(regional)} regions")

        return regional

    def collect_bls_unemployment(self, year: int = 2022) -> pd.DataFrame:
        """
        Collect unemployment rate by region from BLS.

        Args:
            year: Year of data

        Returns:
            DataFrame with regional unemployment rate
        """
        self.logger.info(f"Fetching unemployment data from BLS API for {year}")
        self.logger.warning("BLS unemployment collection not yet implemented - returning empty DataFrame")
        # TODO: Implement BLS unemployment data collection
        return pd.DataFrame()

    def collect_all_demographic_measures(self, year: int = 2022) -> Dict[str, pd.DataFrame]:
        """
        Collect all available demographic measures and aggregate to regions.

        Args:
            year: Year of ACS 5-year estimates

        Returns:
            Dict mapping measure names to DataFrames with regional data
        """
        self.logger.info(f"Collecting all demographic measures for {year}")

        measures = {}

        # Population (extensive measure - sum)
        self.logger.info("=" * 70)
        self.logger.info("1/3: Population")
        measures['population'] = self.collect_population(year=year)

        # Median household income (intensive measure - weighted avg)
        self.logger.info("=" * 70)
        self.logger.info("2/3: Median Household Income")
        measures['median_household_income'] = self.collect_median_household_income(
            year=year,
            population_df=measures['population']
        )

        # Poverty rate (intensive measure - weighted avg)
        self.logger.info("=" * 70)
        self.logger.info("3/3: Poverty Rate")
        measures['poverty_rate'] = self.collect_poverty_rate(year=year)

        self.logger.info("=" * 70)
        self.logger.info(f"Collected {len(measures)} demographic measures")

        return measures

    def save_regional_data(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: Path,
        year: int
    ):
        """
        Save regional data to CSV files.

        Args:
            data: Dict mapping measure names to DataFrames
            output_dir: Directory to save files
            year: Year of data (for filename)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for measure_name, df in data.items():
            filename = f"{measure_name}_{year}_regional.csv"
            filepath = output_dir / filename
            df.to_csv(filepath, index=False)
            self.logger.info(f"Saved {measure_name} to {filepath}")

        self.logger.info(f"Saved {len(data)} measure files to {output_dir}")


if __name__ == '__main__':
    """
    Example usage: Collect demographic measures and save to CSV
    """
    import sys
    from pathlib import Path

    # Setup
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / 'data' / 'regional_data'

    print("=" * 80)
    print("REGIONAL DATA COLLECTION")
    print("=" * 80)
    print()

    # Initialize collector
    collector = RegionalDataCollector()

    # Collect all demographic measures
    year = 2022
    data = collector.collect_all_demographic_measures(year=year)

    # Save to CSV
    print()
    print("=" * 80)
    print("Saving data to CSV files...")
    print("-" * 80)
    collector.save_regional_data(data, output_dir, year)

    # Display summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("-" * 80)
    for measure_name, df in data.items():
        print(f"\n{measure_name}:")
        print(f"  Regions: {len(df)}")
        print(f"  Sample values:")
        value_col = [c for c in df.columns if c not in ['region_code', 'region_name', 'state', 'num_counties', 'total_weight']][0]
        print(f"    Min: {df[value_col].min():.2f}")
        print(f"    Max: {df[value_col].max():.2f}")
        print(f"    Mean: {df[value_col].mean():.2f}")

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)
