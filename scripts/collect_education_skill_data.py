#!/usr/bin/env python3
"""
Component Index 5: Education & Skill Data Collection

Collects all 5 measures for Education & Skill Index following Nebraska methodology exactly:
1. High School Attainment Rate (HS/GED as highest level)
2. Associate's Degree Attainment Rate (Associate's as highest level)
3. College Attainment Rate (Bachelor's as highest level)
4. Labor Force Participation Rate
5. Percent of Knowledge Workers

All measures use exclusive educational categories (not cumulative "or higher").

Usage:
    python scripts/collect_education_skill_data.py --year 2022
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


class EducationSkillCollector:
    """Collects Component Index 5: Education & Skill measures."""

    def __init__(self, year: int = 2022):
        self.year = year
        self.census = CensusAPI()
        self.aggregator = RegionalAggregator()
        self.logger = setup_logger('education_skill_collector')
        self.logger.info(f"=" * 80)
        self.logger.info(f"COMPONENT INDEX 5: EDUCATION & SKILL DATA COLLECTION")
        self.logger.info(f"Year: {year} ACS 5-year estimates")
        self.logger.info(f"=" * 80)

    def collect_county_data(self, variables: list, table_name: str) -> pd.DataFrame:
        """Generic county data collection across all states."""
        all_data = []

        for state_abbr, state_fips in STATES.items():
            try:
                self.logger.debug(f"  Fetching {state_abbr}...")
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

                # Build FIPS code
                if 'county' in df.columns:
                    df['fips'] = state_fips + df['county'].astype(str).str.zfill(3)
                else:  # DC
                    df['fips'] = '11001'

                # Convert variables to numeric
                for var in variables:
                    if var in df.columns:
                        df[var] = pd.to_numeric(df[var], errors='coerce')

                all_data.append(df)
                self.logger.debug(f"  {state_abbr}: {len(df)} counties")

            except Exception as e:
                self.logger.error(f"  Error {state_abbr}: {str(e)}")

        if not all_data:
            self.logger.error(f"No data collected for {table_name}")
            return pd.DataFrame()

        combined = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"  Combined: {len(combined)} counties")
        return combined

    def measure_5_1_high_school_attainment(self) -> pd.DataFrame:
        """
        Measure 5.1: High School Attainment Rate

        Share of population age 25+ with HS degree (or GED) as their HIGHEST level of education.
        EXCLUSIVE category - does NOT include those with any college education.

        Source: Census ACS B15003 (Detailed Educational Attainment)
        """
        self.logger.info("=" * 80)
        self.logger.info("MEASURE 5.1: High School Attainment Rate")
        self.logger.info("=" * 80)

        variables = [
            'B15003_001E',  # Total population 25 years and over
            'B15003_017E',  # Regular high school diploma
            'B15003_018E',  # GED or alternative credential
        ]

        df = self.collect_county_data(variables, "B15003 Educational Attainment")

        if df.empty:
            return pd.DataFrame()

        # Calculate: (HS diploma + GED) / Total * 100
        df['hs_attainment_rate'] = (
            (df['B15003_017E'] + df['B15003_018E']) / df['B15003_001E'] * 100
        ).round(2)

        # Aggregate to regions (intensive measure - use population weighting)
        regional = self.aggregator.aggregate_to_regions(
            county_data=df,
            measure_type='intensive',
            value_column='hs_attainment_rate',
            fips_column='fips',
            weight_column='B15003_001E'  # Weight by total 25+ population
        )

        regional = self.aggregator.add_region_metadata(regional)
        self.logger.info(f"✓ Aggregated: {len(regional)} regions")

        return regional[['region_code', 'region_name', 'state', 'hs_attainment_rate']]

    def measure_5_2_associates_attainment(self) -> pd.DataFrame:
        """
        Measure 5.2: Associate's Degree Attainment Rate

        Share of population age 25+ with Associate's degree as their HIGHEST level of education.
        EXCLUSIVE category - does NOT include those with Bachelor's or higher.

        Source: Census ACS B15003
        """
        self.logger.info("=" * 80)
        self.logger.info("MEASURE 5.2: Associate's Degree Attainment Rate")
        self.logger.info("=" * 80)

        variables = [
            'B15003_001E',  # Total population 25 years and over
            'B15003_021E',  # Associate's degree
        ]

        df = self.collect_county_data(variables, "B15003 Educational Attainment")

        if df.empty:
            return pd.DataFrame()

        # Calculate: Associate's / Total * 100
        df['associates_attainment_rate'] = (
            df['B15003_021E'] / df['B15003_001E'] * 100
        ).round(2)

        # Aggregate to regions
        regional = self.aggregator.aggregate_to_regions(
            county_data=df,
            measure_type='intensive',
            value_column='associates_attainment_rate',
            fips_column='fips',
            weight_column='B15003_001E'
        )

        regional = self.aggregator.add_region_metadata(regional)
        self.logger.info(f"✓ Aggregated: {len(regional)} regions")

        return regional[['region_code', 'region_name', 'state', 'associates_attainment_rate']]

    def measure_5_3_bachelors_attainment(self) -> pd.DataFrame:
        """
        Measure 5.3: College Attainment Rate (Bachelor's Degree)

        Share of population age 25+ with Bachelor's degree as their HIGHEST level of education.
        EXCLUSIVE category - does NOT include Master's, Professional, or Doctoral degrees.

        Source: Census ACS B15003
        """
        self.logger.info("=" * 80)
        self.logger.info("MEASURE 5.3: College Attainment Rate (Bachelor's)")
        self.logger.info("=" * 80)

        variables = [
            'B15003_001E',  # Total population 25 years and over
            'B15003_022E',  # Bachelor's degree
        ]

        df = self.collect_county_data(variables, "B15003 Educational Attainment")

        if df.empty:
            return pd.DataFrame()

        # Calculate: Bachelor's / Total * 100
        df['bachelors_attainment_rate'] = (
            df['B15003_022E'] / df['B15003_001E'] * 100
        ).round(2)

        # Aggregate to regions
        regional = self.aggregator.aggregate_to_regions(
            county_data=df,
            measure_type='intensive',
            value_column='bachelors_attainment_rate',
            fips_column='fips',
            weight_column='B15003_001E'
        )

        regional = self.aggregator.add_region_metadata(regional)
        self.logger.info(f"✓ Aggregated: {len(regional)} regions")

        return regional[['region_code', 'region_name', 'state', 'bachelors_attainment_rate']]

    def measure_5_4_labor_force_participation(self) -> pd.DataFrame:
        """
        Measure 5.4: Labor Force Participation Rate

        Share of population age 16+ who are in the labor force (employed + unemployed).
        Workers gain job experience fastest in regions where larger share participates.

        Source: Census ACS B23025 (Employment Status for Population 16+)
        """
        self.logger.info("=" * 80)
        self.logger.info("MEASURE 5.4: Labor Force Participation Rate")
        self.logger.info("=" * 80)

        variables = [
            'B23025_001E',  # Total population 16 years and over
            'B23025_002E',  # In labor force
        ]

        df = self.collect_county_data(variables, "B23025 Employment Status")

        if df.empty:
            return pd.DataFrame()

        # Calculate: In labor force / Total 16+ * 100
        df['labor_force_participation_rate'] = (
            df['B23025_002E'] / df['B23025_001E'] * 100
        ).round(2)

        # Aggregate to regions
        regional = self.aggregator.aggregate_to_regions(
            county_data=df,
            measure_type='intensive',
            value_column='labor_force_participation_rate',
            fips_column='fips',
            weight_column='B23025_001E'
        )

        regional = self.aggregator.add_region_metadata(regional)
        self.logger.info(f"✓ Aggregated: {len(regional)} regions")

        return regional[['region_code', 'region_name', 'state', 'labor_force_participation_rate']]

    def measure_5_5_knowledge_workers(self) -> pd.DataFrame:
        """
        Measure 5.5: Percent of Knowledge Workers

        Share of employed workers in knowledge industries:
        - Information
        - Finance, insurance, real estate
        - Professional, scientific, management
        - Educational, health, social services

        Source: Census ACS C24030 (Sex by Industry for Civilian Employed 16+)
        """
        self.logger.info("=" * 80)
        self.logger.info("MEASURE 5.5: Percent of Knowledge Workers")
        self.logger.info("=" * 80)

        variables = [
            'C24030_001E',  # Total civilian employed population 16 years and over
            # Information
            'C24030_013E',  # Male - Information
            'C24030_040E',  # Female - Information
            # Finance, insurance, real estate, rental and leasing
            'C24030_014E',  # Male - Finance/insurance/real estate (combined total)
            'C24030_041E',  # Female - Finance/insurance/real estate (combined total)
            # Professional, scientific, management, administrative
            'C24030_017E',  # Male - Professional/scientific/management (combined total)
            'C24030_044E',  # Female - Professional/scientific/management (combined total)
            # Educational, health, social services
            'C24030_021E',  # Male - Education/health/social (combined total)
            'C24030_048E',  # Female - Education/health/social (combined total)
        ]

        df = self.collect_county_data(variables, "C24030 Industry by Sex")

        if df.empty:
            return pd.DataFrame()

        # Calculate total knowledge workers
        df['knowledge_workers'] = (
            df['C24030_013E'] + df['C24030_040E'] +  # Information
            df['C24030_014E'] + df['C24030_041E'] +  # Finance
            df['C24030_017E'] + df['C24030_044E'] +  # Professional
            df['C24030_021E'] + df['C24030_048E']    # Education/health
        )

        # Calculate percentage
        df['pct_knowledge_workers'] = (
            df['knowledge_workers'] / df['C24030_001E'] * 100
        ).round(2)

        # Aggregate to regions
        regional = self.aggregator.aggregate_to_regions(
            county_data=df,
            measure_type='intensive',
            value_column='pct_knowledge_workers',
            fips_column='fips',
            weight_column='C24030_001E'
        )

        regional = self.aggregator.add_region_metadata(regional)
        self.logger.info(f"✓ Aggregated: {len(regional)} regions")

        return regional[['region_code', 'region_name', 'state', 'pct_knowledge_workers']]

    def collect_all(self) -> dict:
        """Collect all 5 Education & Skill measures."""
        measures = {}

        # Measure 5.1: High School Attainment Rate
        measures['hs_attainment_rate'] = self.measure_5_1_high_school_attainment()

        # Measure 5.2: Associate's Degree Attainment Rate
        measures['associates_attainment_rate'] = self.measure_5_2_associates_attainment()

        # Measure 5.3: College Attainment Rate (Bachelor's)
        measures['bachelors_attainment_rate'] = self.measure_5_3_bachelors_attainment()

        # Measure 5.4: Labor Force Participation Rate
        measures['labor_force_participation_rate'] = self.measure_5_4_labor_force_participation()

        # Measure 5.5: Percent of Knowledge Workers
        measures['pct_knowledge_workers'] = self.measure_5_5_knowledge_workers()

        return measures

    def save_all(self, measures: dict, output_dir: Path):
        """Save all measures to CSV files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("=" * 80)
        self.logger.info("SAVING DATA")
        self.logger.info("=" * 80)

        for name, df in measures.items():
            if df is not None and not df.empty:
                filepath = output_dir / f"{name}_{self.year}_regional.csv"
                df.to_csv(filepath, index=False)
                self.logger.info(f"✓ Saved: {filepath.name} ({len(df)} regions)")
            else:
                self.logger.warning(f"✗ Skipped: {name} (no data)")


def main():
    parser = argparse.ArgumentParser(
        description="Collect Component Index 5: Education & Skill data"
    )
    parser.add_argument('--year', type=int, default=2022,
                       help='ACS 5-year estimate ending year (default: 2022)')
    parser.add_argument('--output-dir', type=Path, default=None,
                       help='Output directory (default: data/regional_data)')
    args = parser.parse_args()

    output_dir = args.output_dir or project_root / 'data' / 'regional_data'

    collector = EducationSkillCollector(year=args.year)

    start_time = datetime.now()
    measures = collector.collect_all()
    end_time = datetime.now()

    collector.save_all(measures, output_dir)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Component Index: Education & Skill")
    print(f"Time elapsed: {end_time - start_time}")
    print(f"Measures collected: {len([m for m in measures.values() if not m.empty])}/5")
    print(f"Output directory: {output_dir}")
    print("=" * 80)


if __name__ == '__main__':
    main()
