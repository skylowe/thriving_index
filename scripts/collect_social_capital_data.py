#!/usr/bin/env python3
"""
Social Capital Index Data Collection Script

Component Index 8: Social Capital (5 measures)

All measures in this component require bulk data collection or manual mapping:
1. 501c3 Organizations Per 1,000 Persons - IRS EO BMF bulk download
2. Volunteer Rate (State) - AmeriCorps bulk data
3. Volunteer Hours Per Person (State) - AmeriCorps bulk data
4. Voter Turnout - State election data
5. Tree City USA Share - Arbor Day Foundation static list

This script provides guidance and helper functions for collecting and processing
these measures from their respective bulk data sources.

Author: Claude
Date: 2025-11-15
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import json
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import Config
from src.utils.logging_setup import setup_logging


# Setup logging
logger = setup_logging('social_capital_collection')


class SocialCapitalDataCollector:
    """
    Collector for Social Capital Index measures using bulk data sources.

    Since these measures don't have direct APIs, this class provides:
    1. Documentation of data sources
    2. Helper methods for processing bulk downloads
    3. Data validation and aggregation functions
    """

    def __init__(self, config: Config):
        self.config = config
        self.data_dir = Path(config.data_dir)
        self.cache_dir = Path(config.cache_dir) / 'social_capital'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def collect_501c3_organizations(self, regions: Dict[str, Any]) -> pd.DataFrame:
        """
        Measure 8.1: Number of 501(c)(3) Organizations Per 1,000 Persons

        Data Source: IRS Exempt Organizations Business Master File (EO BMF)
        URL: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf

        Process:
        1. Download IRS EO BMF Extract (CSV or JSON format)
        2. Filter for subsection code "03" (501(c)(3) organizations)
        3. Group by county FIPS code
        4. Count organizations per county
        5. Aggregate to regional level (sum counts)
        6. Calculate per 1,000 population

        Returns:
            DataFrame with columns: region_code, count_501c3, population, orgs_per_1000
        """
        logger.info("=" * 80)
        logger.info("Measure 8.1: 501(c)(3) Organizations Per 1,000 Persons")
        logger.info("=" * 80)

        logger.info("Data Source: IRS Exempt Organizations Business Master File")
        logger.info("Download URL: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf")
        logger.info("")
        logger.info("MANUAL STEPS REQUIRED:")
        logger.info("1. Visit IRS website and download latest EO BMF Extract")
        logger.info("2. Extract ZIP file and locate 'eo_xx.csv' file")
        logger.info("3. Place CSV file in: data/bulk_downloads/irs_eo_bmf/")
        logger.info("4. Run this script again with --process-irs flag")
        logger.info("")

        # Check if bulk data file exists
        bulk_data_dir = self.data_dir / 'bulk_downloads' / 'irs_eo_bmf'
        bulk_data_dir.mkdir(parents=True, exist_ok=True)

        eo_files = list(bulk_data_dir.glob('eo*.csv'))
        if not eo_files:
            logger.warning("No IRS EO BMF files found. Please download manually.")
            logger.info("Expected location: %s", bulk_data_dir)
            return pd.DataFrame()

        logger.info("Found IRS EO BMF file: %s", eo_files[0])
        logger.info("Processing...")

        # TODO: Process IRS EO BMF file
        # - Read CSV
        # - Filter subsection code = "03"
        # - Extract county FIPS from ZIP code or address
        # - Count by county
        # - Aggregate to regions

        return pd.DataFrame()

    def collect_volunteer_data(self, states: List[str]) -> pd.DataFrame:
        """
        Measures 8.2 and 8.3: Volunteer Rate and Volunteer Hours Per Person (State-level)

        Data Source: AmeriCorps Volunteering and Civic Life in America
        URL: https://americorps.gov/about/our-impact/volunteering-civic-engagement-research

        Process:
        1. Visit AmeriCorps website
        2. Download latest "Volunteering in America" state-level data
        3. Extract volunteer rate and volunteer hours per person for each state
        4. Apply state-level values to all regions within that state

        Returns:
            DataFrame with columns: state, volunteer_rate, volunteer_hours_per_person
        """
        logger.info("=" * 80)
        logger.info("Measures 8.2 & 8.3: Volunteer Rate and Hours Per Person (State-level)")
        logger.info("=" * 80)

        logger.info("Data Source: AmeriCorps Volunteering and Civic Life in America")
        logger.info("Download URL: https://americorps.gov/about/our-impact/volunteering-civic-engagement-research")
        logger.info("")
        logger.info("MANUAL STEPS REQUIRED:")
        logger.info("1. Visit AmeriCorps website")
        logger.info("2. Download 'Volunteering in America' state-level data (most recent year)")
        logger.info("3. Extract volunteer rate and volunteer hours per person for states:")
        logger.info("   - Virginia (VA)")
        logger.info("   - Maryland (MD)")
        logger.info("   - West Virginia (WV)")
        logger.info("   - North Carolina (NC)")
        logger.info("   - Tennessee (TN)")
        logger.info("   - Kentucky (KY)")
        logger.info("   - District of Columbia (DC)")
        logger.info("4. Create CSV file: data/bulk_downloads/americorps/volunteer_data.csv")
        logger.info("   with columns: state, volunteer_rate, volunteer_hours_per_person")
        logger.info("")

        # Check if bulk data file exists
        bulk_data_file = self.data_dir / 'bulk_downloads' / 'americorps' / 'volunteer_data.csv'
        if not bulk_data_file.exists():
            logger.warning("AmeriCorps volunteer data not found.")
            logger.info("Expected location: %s", bulk_data_file)
            logger.info("Please create CSV with columns: state, volunteer_rate, volunteer_hours_per_person")
            return pd.DataFrame()

        logger.info("Found AmeriCorps volunteer data: %s", bulk_data_file)
        logger.info("Loading...")

        try:
            df = pd.read_csv(bulk_data_file)
            logger.info("Loaded volunteer data for %d states", len(df))
            return df
        except Exception as e:
            logger.error("Error loading volunteer data: %s", e)
            return pd.DataFrame()

    def collect_voter_turnout(self, regions: Dict[str, Any]) -> pd.DataFrame:
        """
        Measure 8.4: Voter Turnout

        Data Source: State election offices and MIT Election Data + Science Lab
        URL: https://electionlab.mit.edu/

        Process:
        1. Download county-level election results from MIT Election Lab or state sources
        2. Use most recent general election (2022 or 2020)
        3. Calculate turnout: (Total Votes Cast / Registered Voters) * 100
        4. Aggregate to regional level (population-weighted average)

        Returns:
            DataFrame with columns: region_code, voter_turnout_pct
        """
        logger.info("=" * 80)
        logger.info("Measure 8.4: Voter Turnout")
        logger.info("=" * 80)

        logger.info("Data Source: State election offices or MIT Election Data + Science Lab")
        logger.info("Download URL: https://electionlab.mit.edu/")
        logger.info("")
        logger.info("MANUAL STEPS REQUIRED:")
        logger.info("1. Visit MIT Election Lab or state Secretary of State websites")
        logger.info("2. Download county-level election results for most recent general election (2022 or 2020)")
        logger.info("3. Extract total votes cast and registered voters for each county")
        logger.info("4. Create CSV file: data/bulk_downloads/election/voter_turnout.csv")
        logger.info("   with columns: state, county_fips, total_votes, registered_voters")
        logger.info("")

        # Check if bulk data file exists
        bulk_data_file = self.data_dir / 'bulk_downloads' / 'election' / 'voter_turnout.csv'
        if not bulk_data_file.exists():
            logger.warning("Voter turnout data not found.")
            logger.info("Expected location: %s", bulk_data_file)
            return pd.DataFrame()

        logger.info("Found voter turnout data: %s", bulk_data_file)
        logger.info("Processing...")

        # TODO: Process voter turnout data
        # - Calculate turnout by county
        # - Aggregate to regional level (weighted by population)

        return pd.DataFrame()

    def collect_tree_city_usa(self, regions: Dict[str, Any]) -> pd.DataFrame:
        """
        Measure 8.5: Share of Tree City USA Counties

        Data Source: Arbor Day Foundation Tree City USA Directory
        URL: https://www.arborday.org/programs/treecityusa/

        Process:
        1. Download or scrape list of Tree City USA communities
        2. Map communities to counties (manual mapping for cities within counties)
        3. Create binary variable: 1 if county has Tree City USA, 0 if not
        4. Calculate regional share: (Population in Tree City counties / Total regional population)

        Returns:
            DataFrame with columns: region_code, tree_city_share
        """
        logger.info("=" * 80)
        logger.info("Measure 8.5: Share of Tree City USA Counties")
        logger.info("=" * 80)

        logger.info("Data Source: Arbor Day Foundation Tree City USA Directory")
        logger.info("Directory URL: https://www.arborday.org/programs/treecityusa/")
        logger.info("")
        logger.info("MANUAL STEPS REQUIRED:")
        logger.info("1. Visit Arbor Day Foundation Tree City USA website")
        logger.info("2. Download or compile list of Tree City USA communities for:")
        logger.info("   - Virginia, Maryland, West Virginia, North Carolina, Tennessee, Kentucky, DC")
        logger.info("3. Map each community to its county FIPS code")
        logger.info("4. Create CSV file: data/bulk_downloads/tree_city_usa/tree_cities.csv")
        logger.info("   with columns: state, community_name, county_fips")
        logger.info("")

        # Check if bulk data file exists
        bulk_data_file = self.data_dir / 'bulk_downloads' / 'tree_city_usa' / 'tree_cities.csv'
        if not bulk_data_file.exists():
            logger.warning("Tree City USA data not found.")
            logger.info("Expected location: %s", bulk_data_file)
            return pd.DataFrame()

        logger.info("Found Tree City USA data: %s", bulk_data_file)
        logger.info("Processing...")

        # TODO: Process Tree City USA data
        # - Create binary county indicator (has Tree City = 1, no Tree City = 0)
        # - Aggregate to regions
        # - Calculate population share

        return pd.DataFrame()

    def collect_all_measures(self, regions: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Collect all Social Capital Index measures.

        Returns:
            Dictionary mapping measure names to DataFrames
        """
        logger.info("=" * 80)
        logger.info("SOCIAL CAPITAL INDEX - BULK DATA COLLECTION")
        logger.info("=" * 80)
        logger.info("")
        logger.info("This component requires manual bulk data collection for all measures:")
        logger.info("1. 501c3 Organizations - IRS bulk download")
        logger.info("2. Volunteer Rate - AmeriCorps bulk data")
        logger.info("3. Volunteer Hours - AmeriCorps bulk data")
        logger.info("4. Voter Turnout - State election data")
        logger.info("5. Tree City USA - Arbor Day Foundation directory")
        logger.info("")
        logger.info("See function documentation for detailed instructions.")
        logger.info("=" * 80)
        logger.info("")

        results = {}

        # Collect each measure
        results['501c3_orgs'] = self.collect_501c3_organizations(regions)
        results['volunteer_data'] = self.collect_volunteer_data(['VA', 'MD', 'WV', 'NC', 'TN', 'KY', 'DC'])
        results['voter_turnout'] = self.collect_voter_turnout(regions)
        results['tree_city_usa'] = self.collect_tree_city_usa(regions)

        # Log summary
        logger.info("=" * 80)
        logger.info("DATA COLLECTION SUMMARY")
        logger.info("=" * 80)
        for measure, df in results.items():
            status = "✓ DATA AVAILABLE" if not df.empty else "✗ NEEDS MANUAL COLLECTION"
            rows = len(df) if not df.empty else 0
            logger.info("%-20s: %s (%d records)", measure, status, rows)
        logger.info("=" * 80)

        return results


def main():
    """Main execution function."""
    logger.info("Starting Social Capital Index data collection")

    # Load configuration
    config = Config()

    # TODO: Load region definitions
    regions = {}

    # Create collector
    collector = SocialCapitalDataCollector(config)

    # Collect all measures
    results = collector.collect_all_measures(regions)

    # Save results
    output_dir = Path(config.data_dir) / 'processed' / 'social_capital'
    output_dir.mkdir(parents=True, exist_ok=True)

    for measure_name, df in results.items():
        if not df.empty:
            output_file = output_dir / f"{measure_name}.csv"
            df.to_csv(output_file, index=False)
            logger.info("Saved %s to %s", measure_name, output_file)

    logger.info("Social Capital Index data collection complete")


if __name__ == '__main__':
    main()
