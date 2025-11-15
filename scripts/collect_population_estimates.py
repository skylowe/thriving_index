#!/usr/bin/env python3
"""
Collect Census Population Estimates for growth rates and demographic components.

Collects:
- Historical population (2017-2022) for 5-year growth rate calculation
- Components of change: births, deaths, natural increase, migration
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import requests

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.processing.regional_aggregator import RegionalAggregator
from src.utils.config import APIConfig
from src.utils.logging_setup import setup_logger

STATES = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}


class PopulationEstimatesCollector:
    """Collects Census Population Estimates data."""

    def __init__(self):
        self.api_key = APIConfig.CENSUS_API_KEY
        self.base_url = "https://api.census.gov/data"
        self.aggregator = RegionalAggregator()
        self.logger = setup_logger('pop_estimates')

    def fetch_population_time_series(self, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Fetch population for multiple years.

        Args:
            start_year: Starting year
            end_year: Ending year

        Returns:
            DataFrame with population by year and county
        """
        self.logger.info(f"Collecting population time series {start_year}-{end_year}")

        all_data = []

        for year in range(start_year, end_year + 1):
            self.logger.info(f"  Fetching {year}...")

            for state_abbr, state_fips in STATES.items():
                try:
                    # Use vintage population estimates
                    url = f"{self.base_url}/{year}/pep/population"
                    params = {
                        'get': 'POP,NAME',
                        'for': 'county:*',
                        'in': f'state:{state_fips}',
                        'key': self.api_key
                    }

                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()

                    data = response.json()

                    if len(data) > 1:  # Has data beyond header
                        df = pd.DataFrame(data[1:], columns=data[0])
                        df['year'] = year
                        df['state_abbr'] = state_abbr

                        # Build FIPS
                        if 'county' in df.columns and 'state' in df.columns:
                            df['fips'] = df['state'] + df['county']
                        elif state_fips == '11':  # DC
                            df['fips'] = '11001'

                        # Convert population to numeric
                        df['POP'] = pd.to_numeric(df['POP'], errors='coerce')

                        all_data.append(df[['fips', 'year', 'POP', 'NAME']])

                except Exception as e:
                    self.logger.error(f"    Error fetching {state_abbr} {year}: {str(e)}")

        if not all_data:
            self.logger.error("No population time series data collected")
            return pd.DataFrame()

        combined = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"  Collected {len(combined)} county-year records")

        return combined

    def fetch_components_of_change(self, year: int) -> pd.DataFrame:
        """
        Fetch components of population change (births, deaths, migration).

        Args:
            year: Year of estimates

        Returns:
            DataFrame with births, deaths, migration by county
        """
        self.logger.info(f"Collecting components of change for {year}")

        all_data = []

        for state_abbr, state_fips in STATES.items():
            try:
                # Population estimates with components
                url = f"{self.base_url}/{year}/pep/components"
                params = {
                    'get': 'BIRTHS,DEATHS,NATURALINC,INTERNATIONALMIG,DOMESTICMIG,NETMIG,NAME',
                    'for': 'county:*',
                    'in': f'state:{state_fips}',
                    'key': self.api_key
                }

                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                if len(data) > 1:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    df['state_abbr'] = state_abbr

                    # Build FIPS
                    if 'county' in df.columns and 'state' in df.columns:
                        df['fips'] = df['state'] + df['county']
                    elif state_fips == '11':
                        df['fips'] = '11001'

                    # Convert to numeric
                    for col in ['BIRTHS', 'DEATHS', 'NATURALINC', 'INTERNATIONALMIG', 'DOMESTICMIG', 'NETMIG']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                    all_data.append(df)
                    self.logger.debug(f"    {state_abbr}: {len(df)} counties")

            except Exception as e:
                self.logger.error(f"    Error fetching {state_abbr}: {str(e)}")

        if not all_data:
            self.logger.error("No components data collected")
            return pd.DataFrame()

        combined = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"  Collected {len(combined)} county records")

        return combined

    def calculate_growth_rate(self, pop_ts: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Calculate annualized population growth rate.

        Args:
            pop_ts: Population time series DataFrame
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with growth rate by county
        """
        self.logger.info(f"Calculating {end_year - start_year}-year growth rate")

        # Pivot to wide format
        pop_wide = pop_ts.pivot(index='fips', columns='year', values='POP')

        # Calculate annualized growth rate
        if start_year in pop_wide.columns and end_year in pop_wide.columns:
            years = end_year - start_year
            pop_wide['population_growth_rate'] = (
                ((pop_wide[end_year] / pop_wide[start_year]) ** (1/years) - 1) * 100
            ).round(2)

            # Also keep the populations for reference
            pop_wide['population_start'] = pop_wide[start_year]
            pop_wide['population_end'] = pop_wide[end_year]

            result = pop_wide[['population_start', 'population_end', 'population_growth_rate']].reset_index()

            self.logger.info(f"  Calculated growth rates for {len(result)} counties")
            return result
        else:
            self.logger.error(f"Missing year columns: {start_year} or {end_year}")
            return pd.DataFrame()

    def aggregate_to_regions(self, county_data: pd.DataFrame, measure_name: str,
                            measure_type: str = 'extensive') -> pd.DataFrame:
        """
        Aggregate county data to regional groupings.

        Args:
            county_data: County-level data with 'fips' column
            measure_name: Name of measure column
            measure_type: 'extensive' or 'intensive'

        Returns:
            Regional DataFrame
        """
        # For growth rates, use population-weighted average
        weight_col = None
        if measure_type == 'intensive':
            # Use end-year population as weight if available
            if 'population_end' in county_data.columns:
                weight_col = 'population_end'
            elif 'POP' in county_data.columns:
                weight_col = 'POP'

        regional = self.aggregator.aggregate_to_regions(
            county_data=county_data,
            measure_type=measure_type,
            value_column=measure_name,
            fips_column='fips',
            weight_column=weight_col
        )

        regional = self.aggregator.add_region_metadata(regional)
        return regional

    def collect_all(self) -> dict:
        """Collect all population estimates measures."""

        self.logger.info("=" * 80)
        self.logger.info("CENSUS POPULATION ESTIMATES COLLECTION")
        self.logger.info("=" * 80)

        measures = {}

        # 1. Population time series (2017-2022 for 5-year growth)
        pop_ts = self.fetch_population_time_series(2017, 2022)

        if not pop_ts.empty:
            # 2. Calculate 5-year population growth rate
            growth = self.calculate_growth_rate(pop_ts, 2017, 2022)

            if not growth.empty:
                measures['population_growth_rate'] = self.aggregate_to_regions(
                    growth,
                    'population_growth_rate',
                    measure_type='intensive'
                )

        # 3. Components of change for most recent year
        components = self.fetch_components_of_change(2022)

        if not components.empty:
            # Get population for rate calculations
            pop_2022 = pop_ts[pop_ts['year'] == 2022].copy()
            components = components.merge(
                pop_2022[['fips', 'POP']],
                on='fips',
                how='left'
            )

            # Calculate natural increase rate (births - deaths per 1000)
            components['natural_increase_rate'] = (
                (components['NATURALINC'] / components['POP'] * 1000).round(2)
            )

            # Calculate net migration rate (per 1000)
            components['net_migration_rate'] = (
                (components['NETMIG'] / components['POP'] * 1000).round(2)
            )

            # Aggregate to regions
            measures['natural_increase_rate'] = self.aggregate_to_regions(
                components,
                'natural_increase_rate',
                measure_type='intensive'
            )

            measures['net_migration_rate'] = self.aggregate_to_regions(
                components,
                'net_migration_rate',
                measure_type='intensive'
            )

        self.logger.info("=" * 80)
        self.logger.info(f"COLLECTED {len(measures)} MEASURES")
        self.logger.info("=" * 80)

        return measures

    def save_all(self, measures: dict, output_dir: Path):
        """Save measures to CSV."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, df in measures.items():
            if df is not None and not df.empty:
                filepath = output_dir / f"{name}_2022_regional.csv"
                df.to_csv(filepath, index=False)
                self.logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")


def main():
    """Main execution."""

    output_dir = project_root / 'data' / 'regional_data'

    collector = PopulationEstimatesCollector()

    start_time = datetime.now()
    measures = collector.collect_all()
    end_time = datetime.now()

    print()
    print("=" * 80)
    print("SAVING DATA")
    print("=" * 80)
    collector.save_all(measures, output_dir)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Time: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if not m.empty])}")
    print("=" * 80)


if __name__ == '__main__':
    main()
