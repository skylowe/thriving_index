#!/usr/bin/env python3
"""
Simplified Census ACS Data Collection - Using Detailed B-tables Only

Collects HIGH-confidence ACS measures using only B-tables (Detailed Tables).
S-tables (Subject Tables) have been removed as they cause 400 errors.

Usage:
    python scripts/collect_census_acs_simple.py --year 2022
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


STATES = {
    'VA': '51', 'MD': '24', 'WV': '54',
    'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'
}


class SimpleCensusCollector:
    """Simplified Census ACS collector using B-tables only."""

    def __init__(self, year: int = 2022):
        self.year = year
        self.census = CensusAPI()
        self.aggregator = RegionalAggregator()
        self.logger = setup_logger('simple_census_collector')
        self.logger.info(f"Initialized for {year} ACS 5-year estimates")

    def collect_measure(self, name: str, variables: list, calc_func=None, measure_type='intensive') -> pd.DataFrame:
        """Generic measure collection."""
        self.logger.info(f"Collecting: {name}")

        all_data = []

        for state_abbr, state_fips in STATES.items():
            try:
                data = self.census.get_acs5_data(
                    year=self.year,
                    variables=variables,
                    geography='county:*',
                    state=state_fips
                )

                if not data:
                    continue

                df = pd.DataFrame(data)

                # Build FIPS
                if 'county' in df.columns:
                    df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
                else:  # DC
                    df['fips'] = '11001'

                # Convert to numeric
                for var in variables:
                    if var in df.columns:
                        df[var] = pd.to_numeric(df[var], errors='coerce')

                # Apply calculation if provided
                if calc_func:
                    df = calc_func(df)

                all_data.append(df)
                self.logger.debug(f"  {state_abbr}: {len(df)} counties")

            except Exception as e:
                self.logger.error(f"  Error {state_abbr}: {str(e)}")

        if not all_data:
            self.logger.error(f"No data for {name}")
            return pd.DataFrame()

        combined = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"  Combined: {len(combined)} counties")

        # Determine value column and weight
        value_col = name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('%', 'pct')

        # For measures with "pct" or "rate" or "median", use population weighting
        if 'pct' in value_col or 'rate' in value_col or 'median' in value_col:
            # Use total population or universe as weight if available
            weight_col = combined.columns[combined.columns.str.contains('total|universe', case=False)].tolist()
            weight_col = weight_col[0] if weight_col else 'B01001_001E'  # Default to total pop

            # If weight column doesn't exist, get population
            if weight_col not in combined.columns:
                # Add population
                for state_abbr, state_fips in STATES.items():
                    try:
                        pop_data = self.census.get_population(year=self.year, state=state_fips)
                        pop_df = pd.DataFrame(pop_data)
                        if 'county' in pop_df.columns:
                            pop_df['fips'] = state_fips + pop_df['county'].astype(str).str.zfill(3)
                        else:
                            pop_df['fips'] = '11001'
                        pop_df = pop_df.rename(columns={'B01001_001E': 'population'})
                        combined = combined.merge(pop_df[['fips', 'population']], on='fips', how='left')
                    except:
                        pass
                weight_col = 'population'
        else:
            weight_col = None

        # Aggregate
        regional = self.aggregator.aggregate_to_regions(
            county_data=combined,
            measure_type=measure_type,
            value_column=value_col,
            fips_column='fips',
            weight_column=weight_col if measure_type == 'intensive' else None
        )

        regional = self.aggregator.add_region_metadata(regional)
        self.logger.info(f"  Aggregated: {len(regional)} regions")

        return regional

    def collect_all(self) -> dict:
        """Collect all measures."""
        self.logger.info("=" * 80)
        self.logger.info("CENSUS ACS DATA COLLECTION (B-TABLES ONLY)")
        self.logger.info("=" * 80)

        measures = {}

        # 1. Educational Attainment (B15003 - Detailed Educational Attainment)
        def calc_education(df):
            total = df['B15003_001E']  # Total 25+
            # High school grad or higher (includes GED through doctorate)
            hs_or_higher = sum(df[f'B15003_{str(i).zfill(3)}E'] for i in range(17, 26))  # HS diploma through doctorate
            # Some college (some college + associates)
            some_college = df['B15003_019E'] + df['B15003_020E'] + df['B15003_021E']
            # Bachelor's or higher
            bachelors_plus = df['B15003_022E'] + df['B15003_023E'] + df['B15003_024E'] + df['B15003_025E']

            df['pct_hs_or_higher'] = (hs_or_higher / total * 100).round(2)
            df['pct_some_college'] = (some_college / total * 100).round(2)
            df['pct_bachelors_or_higher'] = (bachelors_plus / total * 100).round(2)
            df['total_25plus'] = total
            return df

        # Get all needed education variables
        ed_vars = ['B15003_001E'] + [f'B15003_{str(i).zfill(3)}E' for i in range(17, 26)]

        ed_df = self.collect_measure(
            'educational_attainment',
            ed_vars,
            calc_func=calc_education
        )

        # Split into separate measures
        if not ed_df.empty:
            for measure in ['pct_hs_or_higher', 'pct_some_college', 'pct_bachelors_or_higher']:
                subset = ed_df[['region_code', 'region_name', 'state', measure]].copy()
                measures[measure] = subset

        # 2. Age Distribution (B01001 - Sex by Age)
        def calc_age(df):
            total = df['B01001_001E']
            # Age 25-54: males (columns 11-16) + females (columns 35-40)
            male_25_54 = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(11, 17))
            female_25_54 = sum(df[f'B01001_{str(i).zfill(3)}E'] for i in range(35, 41))
            total_25_54 = male_25_54 + female_25_54

            df['pct_age_25_54'] = (total_25_54 / total * 100).round(2)
            df['total_pop'] = total
            return df

        age_vars = ['B01001_001E'] + [f'B01001_{str(i).zfill(3)}E' for i in list(range(11, 17)) + list(range(35, 41))]
        measures['pct_age_25_54'] = self.collect_measure('pct_age_25_54', age_vars, calc_func=calc_age)

        # 3. Median Age (B01002)
        measures['median_age'] = self.collect_measure('median_age', ['B01002_001E'])

        # 4. Median Household Income (B19013)
        measures['median_household_income'] = self.collect_measure('median_household_income', ['B19013_001E'])

        # 5. Poverty Rate (B17001)
        def calc_poverty(df):
            universe = df['B17001_001E']
            below_poverty = df['B17001_002E']
            df['poverty_rate'] = (below_poverty / universe * 100).round(2)
            df['poverty_universe'] = universe
            return df

        measures['poverty_rate'] = self.collect_measure('poverty_rate', ['B17001_001E', 'B17001_002E'], calc_func=calc_poverty)

        # 6. Housing (B25077 - Median Home Value, B25064 - Median Gross Rent)
        measures['median_home_value'] = self.collect_measure('median_home_value', ['B25077_001E'])
        measures['median_gross_rent'] = self.collect_measure('median_gross_rent', ['B25064_001E'])

        # 7. Housing Age (B25034 - Year Structure Built)
        def calc_housing_age(df):
            total = df['B25034_001E']
            # Built 2014 or later + 2010-2013
            recent = df['B25034_002E'] + df['B25034_003E']
            df['pct_housing_built_last_10_years'] = (recent / total * 100).round(2)
            df['total_housing_units'] = total
            return df

        measures['pct_housing_built_last_10_years'] = self.collect_measure(
            'pct_housing_built_last_10_years',
            ['B25034_001E', 'B25034_002E', 'B25034_003E'],
            calc_func=calc_housing_age
        )

        # 8. Health Insurance (B27001 - Health Insurance Coverage Status)
        def calc_uninsured(df):
            total = df['B27001_001E']
            # No insurance: Male + Female
            no_insurance = df['B27001_005E'] + df['B27001_008E'] + df['B27001_011E'] + df['B27001_014E'] + \
                          df['B27001_017E'] + df['B27001_020E'] + df['B27001_023E'] + df['B27001_026E'] + \
                          df['B27001_029E'] + df['B27001_033E'] + df['B27001_036E'] + df['B27001_039E'] + \
                          df['B27001_042E'] + df['B27001_045E'] + df['B27001_048E'] + df['B27001_051E'] + \
                          df['B27001_054E'] + df['B27001_057E']
            df['pct_uninsured'] = (no_insurance / total * 100).round(2)
            df['health_insurance_universe'] = total
            return df

        # Simplified - use total universe and sum of uninsured
        uninsured_vars = ['B27001_001E', 'B27001_005E', 'B27001_008E', 'B27001_011E', 'B27001_014E',
                         'B27001_017E', 'B27001_020E', 'B27001_023E', 'B27001_026E', 'B27001_029E',
                         'B27001_033E', 'B27001_036E', 'B27001_039E', 'B27001_042E', 'B27001_045E',
                         'B27001_048E', 'B27001_051E', 'B27001_054E', 'B27001_057E']
        measures['pct_uninsured'] = self.collect_measure('pct_uninsured', uninsured_vars, calc_func=calc_uninsured)

        # 9. Single Parent Households (B09002 - Own Children by Family Type)
        def calc_single_parent(df):
            total = df['B09002_001E']
            single_parent = df['B09002_009E'] + df['B09002_015E']
            df['pct_single_parent_households'] = (single_parent / total * 100).round(2)
            df['children_universe'] = total
            return df

        measures['pct_single_parent_households'] = self.collect_measure(
            'pct_single_parent_households',
            ['B09002_001E', 'B09002_009E', 'B09002_015E'],
            calc_func=calc_single_parent
        )

        # 10. Gini Coefficient (B19083)
        measures['gini_coefficient'] = self.collect_measure('gini_coefficient', ['B19083_001E'])

        self.logger.info("=" * 80)
        self.logger.info(f"COLLECTED {len([m for m in measures.values() if not m.empty])} MEASURES")
        self.logger.info("=" * 80)

        return measures

    def save_all(self, measures: dict, output_dir: Path):
        """Save measures to CSV."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, df in measures.items():
            if df is not None and not df.empty:
                filepath = output_dir / f"{name}_{self.year}_regional.csv"
                df.to_csv(filepath, index=False)
                self.logger.info(f"  Saved: {filepath.name} ({len(df)} regions)")


def main():
    parser = argparse.ArgumentParser(description="Collect Census ACS data (B-tables)")
    parser.add_argument('--year', type=int, default=2022)
    parser.add_argument('--output-dir', type=Path, default=None)
    args = parser.parse_args()

    output_dir = args.output_dir or project_root / 'data' / 'regional_data'

    collector = SimpleCensusCollector(year=args.year)

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
    print(f"Measures: {len([m for m in measures.values() if not m.empty])}")
    print("=" * 80)


if __name__ == '__main__':
    main()
