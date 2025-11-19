"""
Aggregate County-Level Data to Regional Level

This script aggregates all 47 measures from county-level to regional-level
using the appropriate aggregation methods defined in aggregation_config.py.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

from regional_data_manager import RegionalDataManager
from aggregation_config import AGGREGATION_CONFIG


class RegionalAggregator:
    """Handles aggregation of county-level data to regional level."""

    def __init__(self, data_dir: Path, output_dir: Path):
        """
        Initialize the regional aggregator.

        Args:
            data_dir: Path to data/processed directory (county-level data)
            output_dir: Path to output directory for regional data
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize regional data manager
        self.manager = RegionalDataManager()

        # Track aggregation statistics
        self.stats = {
            'measures_processed': 0,
            'measures_failed': 0,
            'total_measures': 47,
            'errors': []
        }

    def aggregate_component2(self) -> pd.DataFrame:
        """
        Aggregate Component 2: Economic Opportunity & Diversity.

        Returns:
            DataFrame with regional-level data
        """
        print("\n" + "=" * 80)
        print("COMPONENT 2: ECONOMIC OPPORTUNITY & DIVERSITY")
        print("=" * 80)

        # Load data files
        print("  Loading Component 2 data files...")
        bds_df = pd.read_csv(self.data_dir / "bds_business_dynamics_2021.csv")
        proprietors_df = pd.read_csv(self.data_dir / "bea_proprietors_2022.csv")
        cbp_est_df = pd.read_csv(self.data_dir / "cbp_establishments_2021.csv")
        nonemp_df = pd.read_csv(self.data_dir / "nonemp_firms_2021.csv")
        occupation_df = pd.read_csv(self.data_dir / "census_occupation_2022.csv")
        telecommuter_df = pd.read_csv(self.data_dir / "census_telecommuter_2022.csv")

        # Add fips columns where needed
        if 'fips' not in cbp_est_df.columns:
            cbp_est_df['fips'] = cbp_est_df['state'].astype(str).str.zfill(2) + cbp_est_df['county'].astype(str).str.zfill(3)
        if 'fips' not in nonemp_df.columns:
            nonemp_df['fips'] = nonemp_df['state'].astype(str).str.zfill(2) + nonemp_df['county'].astype(str).str.zfill(3)
        if 'fips' not in occupation_df.columns:
            occupation_df['fips'] = occupation_df['state'].astype(str).str.zfill(2) + occupation_df['county'].astype(str).str.zfill(3)
        if 'fips' not in telecommuter_df.columns:
            telecommuter_df['fips'] = telecommuter_df['state'].astype(str).str.zfill(2) + telecommuter_df['county'].astype(str).str.zfill(3)

        # Get population data for per-capita calculations
        pop_df = pd.read_csv(self.data_dir / "census_population_growth_2000_2022.csv")
        pop_df['fips'] = pop_df['fips'].astype(str).str.zfill(5)
        pop_df = pop_df[['fips', 'population_2022']].copy()

        # 2.1: Entrepreneurial activity (per capita)
        print("  Processing 2.1: Entrepreneurial activity...")
        bds_df['fips'] = bds_df['state'].astype(str).str.zfill(2) + bds_df['county'].astype(str).str.zfill(3)
        bds_df['entrep_count'] = bds_df['ESTABS_ENTRY'] + bds_df['ESTABS_EXIT']
        bds_with_pop = bds_df.merge(pop_df, on='fips', how='left')

        entrep_agg = self.manager.aggregate_county_data(
            bds_with_pop,
            value_column='entrep_count',
            aggregation_method='sum'
        )
        pop_agg = self.manager.aggregate_county_data(
            bds_with_pop,
            value_column='population_2022',
            aggregation_method='sum'
        )
        entrep_agg['entrepreneurial_activity'] = entrep_agg['entrep_count'] / pop_agg['population_2022']

        # 2.2: Proprietors per 1000
        print("  Processing 2.2: Proprietors per 1,000...")
        proprietors_df['fips'] = proprietors_df['GeoFips'].astype(str).str.zfill(5)
        prop_with_pop = proprietors_df.merge(pop_df, on='fips', how='left')

        prop_agg = self.manager.aggregate_county_data(
            prop_with_pop,
            value_column='DataValue',
            aggregation_method='sum'
        )
        prop_pop_agg = self.manager.aggregate_county_data(
            prop_with_pop,
            value_column='population_2022',
            aggregation_method='sum'
        )
        prop_agg['proprietors_per_1000'] = (prop_agg['DataValue'] / prop_pop_agg['population_2022']) * 1000

        # 2.3: Establishments per 1000
        print("  Processing 2.3: Establishments per 1,000...")
        cbp_with_pop = cbp_est_df.merge(pop_df, on='fips', how='left')

        est_agg = self.manager.aggregate_county_data(
            cbp_with_pop,
            value_column='ESTAB',
            aggregation_method='sum'
        )
        est_pop_agg = self.manager.aggregate_county_data(
            cbp_with_pop,
            value_column='population_2022',
            aggregation_method='sum'
        )
        est_agg['establishments_per_1000'] = (est_agg['ESTAB'] / est_pop_agg['population_2022']) * 1000

        # 2.7: Telecommuter share (skip diversity measures for now - they require special calculation)
        print("  Processing 2.7: Telecommuter share...")
        telecommuter_df['total_workers'] = telecommuter_df['B08128_001E'].astype(float)
        telecommuter_df['worked_at_home'] = telecommuter_df['B08128_002E'].astype(float)
        telecommuter_df['telecommuter_pct'] = (telecommuter_df['worked_at_home'] / telecommuter_df['total_workers']) * 100
        telecom_agg = self.manager.aggregate_county_data(
            telecommuter_df,
            value_column='telecommuter_pct',
            aggregation_method='weighted_mean',
            weight_column='total_workers'
        )

        # Merge results
        result = entrep_agg[['region_key', 'region_name', 'state_name', 'entrepreneurial_activity']].copy()
        result = result.merge(prop_agg[['region_key', 'proprietors_per_1000']], on='region_key', how='left')
        result = result.merge(est_agg[['region_key', 'establishments_per_1000']], on='region_key', how='left')
        result = result.merge(telecom_agg[['region_key', 'telecommuter_pct']], on='region_key', how='left')

        self.stats['measures_processed'] += 4  # 2.1, 2.2, 2.3, 2.7 (skipping 2.4, 2.5, 2.6 for now)
        print(f"  ✓ Component 2 complete: {len(result)} regions (4 of 7 measures)")

        return result

    def aggregate_component1(self) -> pd.DataFrame:
        """
        Aggregate Component 1: Growth Index.

        Returns:
            DataFrame with regional-level data
        """
        print("\n" + "=" * 80)
        print("COMPONENT 1: GROWTH INDEX")
        print("=" * 80)

        regional_data = []

        # Load BEA employment data
        print("  Processing 1.1: Employment growth...")
        employment_df = pd.read_csv(self.data_dir / "bea_employment_processed.csv")

        # Pivot to get 2020 and 2022 columns
        emp_pivot = employment_df.pivot_table(
            index='GeoFips',
            columns='TimePeriod',
            values='DataValue',
            aggfunc='first'
        ).reset_index()
        emp_pivot.columns.name = None
        emp_pivot = emp_pivot.rename(columns={'GeoFips': 'fips'})

        # Aggregate employment to regional level
        emp_2020 = self.manager.aggregate_county_data(
            emp_pivot[['fips', 2020]].rename(columns={2020: 'employment'}),
            value_column='employment',
            aggregation_method='sum'
        )
        emp_2022 = self.manager.aggregate_county_data(
            emp_pivot[['fips', 2022]].rename(columns={2022: 'employment'}),
            value_column='employment',
            aggregation_method='sum'
        )

        # Calculate growth rate
        employment_growth = emp_2020[['region_key', 'region_name', 'state_name']].copy()
        employment_growth['employment_2020'] = emp_2020['employment']
        employment_growth['employment_2022'] = emp_2022['employment']
        employment_growth['employment_growth_pct'] = (
            (employment_growth['employment_2022'] - employment_growth['employment_2020'])
            / employment_growth['employment_2020'] * 100
        )

        regional_data.append(employment_growth)

        # Load QCEW data for measures 1.2 and 1.3
        print("  Processing 1.2: Private employment...")
        print("  Processing 1.3: Wage growth...")
        qcew_df = pd.read_csv(self.data_dir / "qcew_private_employment_wages_2020_2022.csv")

        # Get 2022 private employment (measure 1.2)
        qcew_2022 = qcew_df[qcew_df['year'] == 2022].copy()
        private_emp = self.manager.aggregate_county_data(
            qcew_2022,
            value_column='annual_avg_emplvl',
            aggregation_method='sum',
            county_fips_column='area_fips'
        )
        private_emp = private_emp.rename(columns={'annual_avg_emplvl': 'private_employment_2022'})

        # Calculate wage growth (measure 1.3)
        qcew_2020 = qcew_df[qcew_df['year'] == 2020].copy()

        wage_2020 = self.manager.aggregate_county_data(
            qcew_2020,
            value_column='avg_annual_pay',
            aggregation_method='weighted_mean',
            weight_column='annual_avg_emplvl',
            county_fips_column='area_fips'
        )
        wage_2022 = self.manager.aggregate_county_data(
            qcew_2022,
            value_column='avg_annual_pay',
            aggregation_method='weighted_mean',
            weight_column='annual_avg_emplvl',
            county_fips_column='area_fips'
        )

        wage_growth = wage_2020[['region_key']].copy()
        wage_growth['avg_annual_pay_2020'] = wage_2020['avg_annual_pay']
        wage_growth['avg_annual_pay_2022'] = wage_2022['avg_annual_pay']
        wage_growth['wage_growth_pct'] = (
            (wage_growth['avg_annual_pay_2022'] - wage_growth['avg_annual_pay_2020'])
            / wage_growth['avg_annual_pay_2020'] * 100
        )

        # Measure 1.4: Households with children growth
        print("  Processing 1.4: Households with children growth...")
        hh_df = pd.read_csv(self.data_dir / "census_households_children_processed.csv")

        # Separate 2017 and 2022 data
        hh_2017 = hh_df[hh_df['year'] == 2017].copy()
        hh_2022 = hh_df[hh_df['year'] == 2022].copy()

        hh_agg_2017 = self.manager.aggregate_county_data(
            hh_2017,
            value_column='households_with_children',
            aggregation_method='sum'
        )
        hh_agg_2022 = self.manager.aggregate_county_data(
            hh_2022,
            value_column='households_with_children',
            aggregation_method='sum'
        )

        hh_growth = hh_agg_2017[['region_key']].copy()
        hh_growth['households_with_children_2017'] = hh_agg_2017['households_with_children']
        hh_growth['households_with_children_2022'] = hh_agg_2022['households_with_children']
        hh_growth['hh_children_growth_pct'] = (
            (hh_growth['households_with_children_2022'] - hh_growth['households_with_children_2017'])
            / hh_growth['households_with_children_2017'] * 100
        )

        # Measure 1.5: DIR income growth
        print("  Processing 1.5: DIR income growth...")
        dir_df = pd.read_csv(self.data_dir / "bea_dir_income_processed.csv")

        dir_pivot = dir_df.pivot_table(
            index='GeoFips',
            columns='TimePeriod',
            values='DataValue',
            aggfunc='first'
        ).reset_index()
        dir_pivot.columns.name = None
        dir_pivot = dir_pivot.rename(columns={'GeoFips': 'fips'})

        dir_2020 = self.manager.aggregate_county_data(
            dir_pivot[['fips', 2020]].rename(columns={2020: 'dir_income'}),
            value_column='dir_income',
            aggregation_method='sum'
        )
        dir_2022 = self.manager.aggregate_county_data(
            dir_pivot[['fips', 2022]].rename(columns={2022: 'dir_income'}),
            value_column='dir_income',
            aggregation_method='sum'
        )

        dir_growth = dir_2020[['region_key']].copy()
        dir_growth['dir_income_2020'] = dir_2020['dir_income']
        dir_growth['dir_income_2022'] = dir_2022['dir_income']
        dir_growth['dir_income_growth_pct'] = (
            (dir_growth['dir_income_2022'] - dir_growth['dir_income_2020'])
            / dir_growth['dir_income_2020'] * 100
        )

        # Merge all Component 1 measures
        result = employment_growth
        result = result.merge(private_emp[['region_key', 'private_employment_2022']], on='region_key', how='left')
        result = result.merge(wage_growth[['region_key', 'wage_growth_pct', 'avg_annual_pay_2022']], on='region_key', how='left')
        result = result.merge(hh_growth[['region_key', 'hh_children_growth_pct']], on='region_key', how='left')
        result = result.merge(dir_growth[['region_key', 'dir_income_growth_pct']], on='region_key', how='left')

        self.stats['measures_processed'] += 5
        print(f"  ✓ Component 1 complete: {len(result)} regions")

        return result

    def aggregate_component8(self) -> pd.DataFrame:
        """
        Aggregate Component 8: Social Capital.

        Returns:
            DataFrame with regional-level data
        """
        print("\n" + "=" * 80)
        print("COMPONENT 8: SOCIAL CAPITAL")
        print("=" * 80)

        # Load component 8 data (already has all 5 measures in one file)
        print("  Loading social capital data...")
        sc_df = pd.read_csv(self.data_dir / "component8_social_capital_2022.csv")

        # Ensure fips column exists
        sc_df['fips'] = sc_df['fips'].astype(str).str.zfill(5)

        # Measure 8.1: Nonprofits per 1000
        print("  Processing 8.1: Nonprofits per 1,000...")
        nonprofits_agg = self.manager.aggregate_county_data(
            sc_df[['fips', 'org_count_501c3', 'total_population']],
            value_column='org_count_501c3',
            aggregation_method='sum'
        )
        pop_agg = self.manager.aggregate_county_data(
            sc_df[['fips', 'total_population']],
            value_column='total_population',
            aggregation_method='sum'
        )
        nonprofits_agg['orgs_per_1000'] = (
            nonprofits_agg['org_count_501c3'] / pop_agg['total_population'] * 1000
        )

        # Measure 8.2: Volunteer rate (weighted mean)
        print("  Processing 8.2: Volunteer rate...")
        volunteer_agg = self.manager.aggregate_county_data(
            sc_df[sc_df['volunteering_rate'].notna()][['fips', 'volunteering_rate', 'total_population']],
            value_column='volunteering_rate',
            aggregation_method='weighted_mean',
            weight_column='total_population'
        )

        # Measure 8.3: Social associations per 10k
        print("  Processing 8.3: Social associations...")
        # Calculate count from rate
        sc_df['social_assoc_count'] = (
            sc_df['social_associations_per_10k'] * sc_df['total_population'] / 10000
        )
        assoc_agg = self.manager.aggregate_county_data(
            sc_df[sc_df['social_assoc_count'].notna()][['fips', 'social_assoc_count', 'total_population']],
            value_column='social_assoc_count',
            aggregation_method='sum'
        )
        pop_assoc = self.manager.aggregate_county_data(
            sc_df[sc_df['social_assoc_count'].notna()][['fips', 'total_population']],
            value_column='total_population',
            aggregation_method='sum'
        )
        assoc_agg['social_associations_per_10k'] = (
            assoc_agg['social_assoc_count'] / pop_assoc['total_population'] * 10000
        )

        # Measure 8.4: Voter turnout (weighted mean)
        print("  Processing 8.4: Voter turnout...")
        turnout_agg = self.manager.aggregate_county_data(
            sc_df[sc_df['voter_turnout_pct'].notna()][['fips', 'voter_turnout_pct', 'total_population']],
            value_column='voter_turnout_pct',
            aggregation_method='weighted_mean',
            weight_column='total_population'
        )

        # Measure 8.5: Civic organizations density (weighted mean)
        print("  Processing 8.5: Civic organizations density...")
        civic_agg = self.manager.aggregate_county_data(
            sc_df[sc_df['civic_organizations_per_1k'].notna()][['fips', 'civic_organizations_per_1k', 'total_population']],
            value_column='civic_organizations_per_1k',
            aggregation_method='weighted_mean',
            weight_column='total_population'
        )

        # Merge all Component 8 measures
        result = nonprofits_agg[['region_key', 'region_name', 'state_name', 'orgs_per_1000', 'org_count_501c3']].copy()
        result['total_population'] = pop_agg['total_population']
        result = result.merge(
            volunteer_agg[['region_key', 'volunteering_rate']],
            on='region_key', how='left'
        )
        result = result.merge(
            assoc_agg[['region_key', 'social_associations_per_10k']],
            on='region_key', how='left'
        )
        result = result.merge(
            turnout_agg[['region_key', 'voter_turnout_pct']],
            on='region_key', how='left'
        )
        result = result.merge(
            civic_agg[['region_key', 'civic_organizations_per_1k']],
            on='region_key', how='left'
        )

        self.stats['measures_processed'] += 5
        print(f"  ✓ Component 8 complete: {len(result)} regions")

        return result

    def save_regional_data(self, data: pd.DataFrame, filename: str):
        """
        Save regional data to CSV file.

        Args:
            data: DataFrame with regional data
            filename: Output filename
        """
        output_path = self.output_dir / filename
        data.to_csv(output_path, index=False)
        print(f"  ✓ Saved: {output_path}")

    def print_summary(self):
        """Print aggregation summary statistics."""
        print("\n" + "=" * 80)
        print("AGGREGATION SUMMARY")
        print("=" * 80)
        print(f"Measures processed: {self.stats['measures_processed']}/{self.stats['total_measures']}")
        print(f"Measures failed: {self.stats['measures_failed']}")

        if self.stats['errors']:
            print("\nErrors encountered:")
            for error in self.stats['errors']:
                print(f"  - {error}")

        print()


def main():
    """Main aggregation workflow."""
    print("=" * 80)
    print("REGIONAL DATA AGGREGATION")
    print("Starting:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    # Get project paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "processed"
    output_dir = project_root / "data" / "regional"

    # Initialize aggregator
    aggregator = RegionalAggregator(data_dir, output_dir)

    # Component 1: Growth Index
    try:
        comp1_data = aggregator.aggregate_component1()
        aggregator.save_regional_data(comp1_data, "component1_growth_index_regional.csv")
    except Exception as e:
        print(f"ERROR in Component 1: {e}")
        import traceback
        traceback.print_exc()
        aggregator.stats['measures_failed'] += 5
        aggregator.stats['errors'].append(f"Component 1: {str(e)}")

    # Component 2: Economic Opportunity & Diversity
    try:
        comp2_data = aggregator.aggregate_component2()
        aggregator.save_regional_data(comp2_data, "component2_economic_opportunity_regional.csv")
    except Exception as e:
        print(f"ERROR in Component 2: {e}")
        import traceback
        traceback.print_exc()
        aggregator.stats['measures_failed'] += 7
        aggregator.stats['errors'].append(f"Component 2: {str(e)}")

    # Component 8: Social Capital
    try:
        comp8_data = aggregator.aggregate_component8()
        aggregator.save_regional_data(comp8_data, "component8_social_capital_regional.csv")
    except Exception as e:
        print(f"ERROR in Component 8: {e}")
        aggregator.stats['measures_failed'] += 5
        aggregator.stats['errors'].append(f"Component 8: {str(e)}")

    # Print summary
    aggregator.print_summary()

    print("=" * 80)
    print("COMPLETE")
    print("Finished:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)


if __name__ == "__main__":
    main()
