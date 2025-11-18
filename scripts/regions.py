"""
Virginia Regional Data Management
Provides functions to work with GO Virginia regions for the Thriving Index project.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class VirginiaRegions:
    """Manages Virginia GO Region data and provides lookup/aggregation functions."""

    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize Virginia regions data.

        Args:
            data_path: Path to virginia_go_regions.csv. If None, uses default location.
        """
        if data_path is None:
            # Default to data/regions/virginia_go_regions.csv
            project_root = Path(__file__).parent.parent
            data_path = project_root / "data" / "regions" / "virginia_go_regions.csv"

        self.data_path = data_path
        self.df = pd.read_csv(data_path)

        # Create lookup dictionaries for fast access
        self._build_lookups()

    def _build_lookups(self):
        """Build internal lookup dictionaries."""
        # Locality name -> Region mapping
        self.locality_to_region = {}
        for _, row in self.df.iterrows():
            self.locality_to_region[row['locality_name']] = {
                'region_id': row['region_id'],
                'region_name': row['region_name'],
                'locality_type': row['locality_type']
            }

        # Region ID -> Localities mapping
        self.region_to_localities = {}
        for region_id in self.df['region_id'].unique():
            region_data = self.df[self.df['region_id'] == region_id]
            self.region_to_localities[region_id] = {
                'region_name': region_data.iloc[0]['region_name'],
                'counties': region_data[region_data['locality_type'] == 'County']['locality_name'].tolist(),
                'cities': region_data[region_data['locality_type'] == 'City']['locality_name'].tolist()
            }

    def get_region(self, locality_name: str) -> Optional[Dict]:
        """
        Get region information for a given locality (county or city).

        Args:
            locality_name: Name of county or city (e.g., "Albemarle County", "Charlottesville city")

        Returns:
            Dictionary with region_id, region_name, locality_type, or None if not found
        """
        return self.locality_to_region.get(locality_name)

    def get_localities(self, region_id: int) -> Optional[Dict]:
        """
        Get all localities in a given region.

        Args:
            region_id: GO Virginia region ID (1-9)

        Returns:
            Dictionary with region_name, counties list, cities list, or None if not found
        """
        return self.region_to_localities.get(region_id)

    def get_all_regions(self) -> pd.DataFrame:
        """
        Get summary of all regions.

        Returns:
            DataFrame with region_id, region_name, num_counties, num_cities, total_localities
        """
        summary = []
        for region_id in sorted(self.region_to_localities.keys()):
            region_info = self.region_to_localities[region_id]
            summary.append({
                'region_id': region_id,
                'region_name': region_info['region_name'],
                'num_counties': len(region_info['counties']),
                'num_cities': len(region_info['cities']),
                'total_localities': len(region_info['counties']) + len(region_info['cities'])
            })

        return pd.DataFrame(summary)

    def filter_rural_regions(self, exclude_metro_regions: List[int] = None) -> List[int]:
        """
        Filter to rural regions by excluding major metropolitan areas.

        Args:
            exclude_metro_regions: List of region IDs to exclude.
                Default excludes Region 7 (Northern Virginia), Region 5 (Hampton Roads),
                Region 4 (Greater Richmond)

        Returns:
            List of rural region IDs
        """
        if exclude_metro_regions is None:
            # Default: exclude the three major metro areas
            exclude_metro_regions = [4, 5, 7]

        all_regions = set(self.df['region_id'].unique())
        rural_regions = sorted(all_regions - set(exclude_metro_regions))

        return rural_regions

    def get_fips_mapping(self) -> pd.DataFrame:
        """
        Get locality name to FIPS mapping.

        Note: This provides the state FIPS (51 for Virginia).
        County/city FIPS codes need to be added separately.

        Returns:
            DataFrame with locality_name, locality_type, state_fips, region_id, region_name
        """
        return self.df.copy()

    def validate_coverage(self) -> Dict:
        """
        Validate that all Virginia localities are covered.

        Returns:
            Dictionary with validation results
        """
        total_counties = len(self.df[self.df['locality_type'] == 'County'])
        total_cities = len(self.df[self.df['locality_type'] == 'City'])
        total_localities = len(self.df)

        # Virginia has 95 counties and 38 independent cities = 133 total
        expected_total = 133

        return {
            'total_localities': total_localities,
            'total_counties': total_counties,
            'total_cities': total_cities,
            'expected_total': expected_total,
            'is_complete': total_localities == expected_total,
            'num_regions': len(self.df['region_id'].unique())
        }

    def print_summary(self):
        """Print a formatted summary of all regions."""
        print("=" * 80)
        print("GO VIRGINIA REGIONS SUMMARY")
        print("=" * 80)
        print()

        summary_df = self.get_all_regions()
        print(summary_df.to_string(index=False))
        print()

        print("=" * 80)
        print("VALIDATION")
        print("=" * 80)
        validation = self.validate_coverage()
        print(f"Total Localities: {validation['total_localities']}")
        print(f"  - Counties: {validation['total_counties']}")
        print(f"  - Cities: {validation['total_cities']}")
        print(f"Expected Total: {validation['expected_total']}")
        print(f"Coverage Complete: {'✓' if validation['is_complete'] else '✗'}")
        print(f"Number of Regions: {validation['num_regions']}")
        print()

        # Rural regions
        rural = self.filter_rural_regions()
        print("=" * 80)
        print("RURAL REGIONS (excluding Northern VA, Hampton Roads, Greater Richmond)")
        print("=" * 80)
        for region_id in rural:
            region_info = self.region_to_localities[region_id]
            print(f"Region {region_id}: {region_info['region_name']}")
            print(f"  - {len(region_info['counties'])} counties, {len(region_info['cities'])} cities")
        print()


def main():
    """Example usage of VirginiaRegions class."""
    regions = VirginiaRegions()

    # Print summary
    regions.print_summary()

    # Example lookups
    print("=" * 80)
    print("EXAMPLE LOOKUPS")
    print("=" * 80)

    # Look up a county
    county_info = regions.get_region("Albemarle County")
    if county_info:
        print(f"Albemarle County is in Region {county_info['region_id']}: {county_info['region_name']}")

    # Get all localities in Region 9
    region9 = regions.get_localities(9)
    if region9:
        print(f"\nRegion 9 ({region9['region_name']}):")
        print(f"  Counties: {', '.join(region9['counties'][:3])}... ({len(region9['counties'])} total)")
        print(f"  Cities: {', '.join(region9['cities'])}")

    print()


if __name__ == "__main__":
    main()
