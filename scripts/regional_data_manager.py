"""
Regional Data Manager - Multi-State Support

Manages regional definitions for all 10 states in the Thriving Index project.
Provides functions for county-to-region lookups and regional data aggregation.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class RegionalDataManager:
    """Manages multi-state regional data and provides lookup/aggregation functions."""

    # State names and FIPS codes
    STATE_INFO = {
        '10': {'name': 'Delaware', 'abbr': 'DE', 'file': None},  # No regions
        '13': {'name': 'Georgia', 'abbr': 'GA', 'file': 'georgia_rc_regions.csv'},
        '21': {'name': 'Kentucky', 'abbr': 'KY', 'file': 'kentucky_add_regions.csv'},
        '24': {'name': 'Maryland', 'abbr': 'MD', 'file': 'maryland_edd_regions.csv'},
        '37': {'name': 'North Carolina', 'abbr': 'NC', 'file': 'northcarolina_cog_regions.csv'},
        '42': {'name': 'Pennsylvania', 'abbr': 'PA', 'file': 'pennsylvania_edd_regions.csv'},
        '45': {'name': 'South Carolina', 'abbr': 'SC', 'file': 'southcarolina_cog_regions.csv'},
        '47': {'name': 'Tennessee', 'abbr': 'TN', 'file': 'tennessee_dd_regions.csv'},
        '51': {'name': 'Virginia', 'abbr': 'VA', 'file': 'virginia_go_regions.csv'},
        '54': {'name': 'West Virginia', 'abbr': 'WV', 'file': 'westvirginia_edd_regions.csv'},
    }

    def __init__(self, regions_dir: Optional[Path] = None):
        """
        Initialize regional data manager.

        Args:
            regions_dir: Path to data/regions directory. If None, uses default location.
        """
        if regions_dir is None:
            # Default to data/regions/
            project_root = Path(__file__).parent.parent
            regions_dir = project_root / "data" / "regions"

        self.regions_dir = regions_dir
        self.regional_data = {}  # Store DataFrames by state FIPS
        self.county_to_region = {}  # Fast lookup: county_fips -> region info
        self.region_to_counties = {}  # Fast lookup: (state_fips, region_id) -> counties

        # Load all regional data
        self._load_regional_data()

    def _load_regional_data(self):
        """Load all regional CSV files and build lookup tables."""
        for state_fips, state_info in self.STATE_INFO.items():
            if state_info['file'] is None:
                # Delaware has no regions (will use county-level data)
                continue

            file_path = self.regions_dir / state_info['file']
            if not file_path.exists():
                print(f"WARNING: Regional file not found: {file_path}")
                continue

            # Load regional data
            df = pd.read_csv(file_path)
            self.regional_data[state_fips] = df

            # Build county-to-region lookup
            for _, row in df.iterrows():
                county_fips = str(row['county_fips']).zfill(5)
                region_id = row['region_id']
                region_name = row['region_name']

                self.county_to_region[county_fips] = {
                    'state_fips': state_fips,
                    'state_name': state_info['name'],
                    'region_id': region_id,
                    'region_name': region_name,
                    'region_key': f"{state_fips}_{region_id}"  # Unique identifier
                }

            # Build region-to-counties lookup
            for region_id in df['region_id'].unique():
                region_counties = df[df['region_id'] == region_id]
                region_key = f"{state_fips}_{region_id}"

                self.region_to_counties[region_key] = {
                    'state_fips': state_fips,
                    'state_name': state_info['name'],
                    'region_id': region_id,
                    'region_name': region_counties.iloc[0]['region_name'],
                    'county_fips_list': region_counties['county_fips'].tolist(),
                    'num_counties': len(region_counties)
                }

    def get_region_for_county(self, county_fips: str) -> Optional[Dict]:
        """
        Get region information for a given county FIPS code.

        Args:
            county_fips: 5-digit county FIPS code (e.g., "51001")

        Returns:
            Dictionary with region info, or None if not found
        """
        county_fips = str(county_fips).zfill(5)
        return self.county_to_region.get(county_fips)

    def get_counties_in_region(self, region_key: str) -> Optional[Dict]:
        """
        Get all counties in a given region.

        Args:
            region_key: Region identifier in format "state_fips_region_id" (e.g., "51_1")

        Returns:
            Dictionary with region info and county list, or None if not found
        """
        return self.region_to_counties.get(region_key)

    def get_all_regions(self, state_fips: Optional[str] = None) -> pd.DataFrame:
        """
        Get summary of all regions.

        Args:
            state_fips: If provided, filter to specific state. Otherwise returns all states.

        Returns:
            DataFrame with region_key, state_fips, state_name, region_id, region_name, num_counties
        """
        summary = []

        # Filter by state if requested
        if state_fips:
            regions_to_process = {state_fips: self.region_to_counties}
            region_keys = [k for k in self.region_to_counties.keys() if k.startswith(f"{state_fips}_")]
        else:
            region_keys = self.region_to_counties.keys()

        for region_key in sorted(region_keys):
            region_info = self.region_to_counties[region_key]
            summary.append({
                'region_key': region_key,
                'state_fips': region_info['state_fips'],
                'state_name': region_info['state_name'],
                'region_id': region_info['region_id'],
                'region_name': region_info['region_name'],
                'num_counties': region_info['num_counties']
            })

        return pd.DataFrame(summary)

    def aggregate_county_data(
        self,
        county_data: pd.DataFrame,
        value_column: str,
        aggregation_method: str = 'sum',
        weight_column: Optional[str] = None,
        county_fips_column: str = 'fips'
    ) -> pd.DataFrame:
        """
        Aggregate county-level data to regional level.

        Args:
            county_data: DataFrame with county-level data
            value_column: Name of column containing values to aggregate
            aggregation_method: How to aggregate ('sum', 'mean', 'weighted_mean', 'median', 'count')
            weight_column: Column to use for weighted_mean (e.g., 'population')
            county_fips_column: Name of column containing county FIPS codes

        Returns:
            DataFrame with regional aggregated data
        """
        # Ensure FIPS codes are strings with 5 digits
        county_data = county_data.copy()
        county_data[county_fips_column] = county_data[county_fips_column].astype(str).str.zfill(5)

        # Add region information to county data
        region_info = []
        for fips in county_data[county_fips_column]:
            region = self.get_region_for_county(fips)
            if region:
                region_info.append(region)
            else:
                # County not in any region (e.g., Delaware or metro counties in PA/MD)
                region_info.append({
                    'region_key': None,
                    'state_fips': fips[:2],
                    'region_id': None,
                    'region_name': None
                })

        county_data['region_key'] = [r['region_key'] for r in region_info]
        county_data['region_name'] = [r['region_name'] for r in region_info]
        county_data['state_fips'] = [r['state_fips'] for r in region_info]

        # Filter out counties not in any region
        regional_data = county_data[county_data['region_key'].notna()].copy()

        if len(regional_data) == 0:
            print("WARNING: No counties matched to regions")
            return pd.DataFrame()

        # Perform aggregation
        if aggregation_method == 'sum':
            aggregated = regional_data.groupby('region_key')[value_column].sum().reset_index()

        elif aggregation_method == 'mean':
            aggregated = regional_data.groupby('region_key')[value_column].mean().reset_index()

        elif aggregation_method == 'median':
            aggregated = regional_data.groupby('region_key')[value_column].median().reset_index()

        elif aggregation_method == 'count':
            aggregated = regional_data.groupby('region_key')[value_column].count().reset_index()

        elif aggregation_method == 'weighted_mean':
            if weight_column is None:
                raise ValueError("weight_column required for weighted_mean aggregation")

            def weighted_avg(group):
                weights = group[weight_column]
                values = group[value_column]
                # Handle missing values
                mask = values.notna() & weights.notna()
                if mask.sum() == 0:
                    return np.nan
                return (values[mask] * weights[mask]).sum() / weights[mask].sum()

            aggregated = regional_data.groupby('region_key').apply(weighted_avg).reset_index()
            aggregated.columns = ['region_key', value_column]

        else:
            raise ValueError(f"Unknown aggregation method: {aggregation_method}")

        # Add region metadata
        aggregated = aggregated.merge(
            self.get_all_regions()[['region_key', 'state_fips', 'state_name', 'region_id', 'region_name']],
            on='region_key',
            how='left'
        )

        # Add county count
        county_counts = regional_data.groupby('region_key').size().reset_index(name='num_counties_with_data')
        aggregated = aggregated.merge(county_counts, on='region_key', how='left')

        return aggregated

    def get_virginia_rural_regions(self) -> List[str]:
        """
        Get list of Virginia rural region keys (excluding metro areas).

        Returns:
            List of region_key values for rural Virginia regions
        """
        # Exclude Northern Virginia (7), Hampton Roads (5), Greater Richmond (4)
        excluded_regions = [4, 5, 7]

        va_regions = self.get_all_regions(state_fips='51')
        rural_regions = va_regions[~va_regions['region_id'].isin(excluded_regions)]

        return rural_regions['region_key'].tolist()

    def validate_coverage(self, county_fips_list: List[str]) -> Dict:
        """
        Validate which counties from a list are covered by regional definitions.

        Args:
            county_fips_list: List of county FIPS codes

        Returns:
            Dictionary with validation statistics
        """
        covered = 0
        not_covered = 0
        by_state = {}

        for fips in county_fips_list:
            fips = str(fips).zfill(5)
            state_fips = fips[:2]

            if state_fips not in by_state:
                by_state[state_fips] = {'covered': 0, 'not_covered': 0}

            region = self.get_region_for_county(fips)
            if region:
                covered += 1
                by_state[state_fips]['covered'] += 1
            else:
                not_covered += 1
                by_state[state_fips]['not_covered'] += 1

        return {
            'total_counties': len(county_fips_list),
            'covered': covered,
            'not_covered': not_covered,
            'coverage_pct': (covered / len(county_fips_list) * 100) if county_fips_list else 0,
            'by_state': by_state
        }

    def print_summary(self):
        """Print a formatted summary of all regions."""
        print("=" * 80)
        print("REGIONAL DATA MANAGER SUMMARY")
        print("=" * 80)
        print()

        # Overall summary
        all_regions = self.get_all_regions()
        print(f"Total Regions: {len(all_regions)}")
        print(f"Total Counties in Regions: {sum(all_regions['num_counties'])}")
        print()

        # By state
        print("=" * 80)
        print("REGIONS BY STATE")
        print("=" * 80)
        for state_fips in sorted(self.STATE_INFO.keys()):
            state_info = self.STATE_INFO[state_fips]
            state_regions = all_regions[all_regions['state_fips'] == state_fips]

            if len(state_regions) == 0:
                print(f"{state_info['name']:20} - No regional definitions (county-level only)")
            else:
                total_counties = state_regions['num_counties'].sum()
                print(f"{state_info['name']:20} - {len(state_regions):2} regions, {total_counties:3} counties")

        print()

        # Virginia rural regions
        print("=" * 80)
        print("VIRGINIA RURAL REGIONS")
        print("=" * 80)
        rural_regions = self.get_virginia_rural_regions()
        for region_key in rural_regions:
            region_info = self.region_to_counties[region_key]
            print(f"  {region_key}: {region_info['region_name']} ({region_info['num_counties']} counties)")
        print()


def main():
    """Example usage of RegionalDataManager class."""
    manager = RegionalDataManager()

    # Print summary
    manager.print_summary()

    # Example: Look up a county
    print("=" * 80)
    print("EXAMPLE COUNTY LOOKUP")
    print("=" * 80)
    albemarle_fips = "51003"  # Albemarle County, VA
    region = manager.get_region_for_county(albemarle_fips)
    if region:
        print(f"County FIPS {albemarle_fips} is in:")
        print(f"  Region: {region['region_name']} (Region {region['region_id']})")
        print(f"  State: {region['state_name']}")
        print(f"  Region Key: {region['region_key']}")
    print()

    # Example: Get counties in a region
    print("=" * 80)
    print("EXAMPLE REGION LOOKUP")
    print("=" * 80)
    region_info = manager.get_counties_in_region("51_9")  # Central Virginia
    if region_info:
        print(f"Region: {region_info['region_name']}")
        print(f"Counties: {region_info['num_counties']}")
        print(f"First 5 FIPS codes: {region_info['county_fips_list'][:5]}")
    print()

    # Example: Aggregate data
    print("=" * 80)
    print("EXAMPLE DATA AGGREGATION")
    print("=" * 80)

    # Load sample county data
    project_root = Path(__file__).parent.parent
    sample_file = project_root / "data" / "processed" / "census_population_growth_2000_2022.csv"

    if sample_file.exists():
        county_data = pd.read_csv(sample_file)

        # Aggregate population to regional level
        regional_pop = manager.aggregate_county_data(
            county_data=county_data,
            value_column='population_2022',
            aggregation_method='sum',
            county_fips_column='fips'
        )

        print("Regional Population (2022) - Top 10:")
        print(regional_pop.nlargest(10, 'population_2022')[
            ['region_name', 'state_name', 'population_2022', 'num_counties_with_data']
        ].to_string(index=False))
        print()


if __name__ == "__main__":
    main()
