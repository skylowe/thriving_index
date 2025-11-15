"""
Data Collection Script: Component Index 6 - Infrastructure & Cost of Doing Business

This script collects all 6 measures for the Infrastructure & Cost of Doing Business Index
following the Nebraska Thriving Index methodology exactly.

Measures:
  6.1: Broadband Internet Access (% with 100/10Mbps capacity) - FCC API
  6.2: Presence of Interstate Highway (share of pop in county with interstate) - Manual/GIS
  6.3: Count of 4-Year Colleges (average count in counties) - NCES IPEDS
  6.4: Weekly Wage Rate (average weekly wage) - BLS QCEW API
  6.5: Top Marginal Income Tax Rate (state tax rate) - Static data
  6.6: Count of Qualified Opportunity Zones (average count in counties) - Treasury data

Data Sources:
  - FCC Broadband Map (API or bulk download)
  - Census TIGER/Line (for interstate highway mapping)
  - NCES IPEDS (bulk download)
  - BLS QCEW API (average weekly wages)
  - Tax Foundation (state income tax rates)
  - U.S. Treasury CDFI Fund (Qualified Opportunity Zones)

Author: Virginia Thriving Index Project
Date: 2025-11-15
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from api_clients.bls_api import BLSAPIClient
from utils.config import Config
from utils.logging_setup import setup_logging
from data.regional_groupings import REGIONS

# Initialize logging
logger = setup_logging(__name__)

# Initialize configuration
config = Config()


def collect_broadband_access(regions: dict) -> pd.DataFrame:
    """
    Measure 6.1: Broadband Internet Access

    FCC Broadband Map data showing percent of population with access to
    100/10Mbps broadband service.

    Args:
        regions: Dictionary of region definitions

    Returns:
        DataFrame with columns: region_code, broadband_pct

    Notes:
        - FCC API key not yet available
        - This is a placeholder implementation
        - Will use FCC bulk data download when API key is obtained
        - See FCC_PLACEHOLDER_DESIGN.md for implementation strategy
    """
    logger.info("Collecting Broadband Internet Access data (Measure 6.1)")
    logger.warning("FCC API key not yet available - placeholder implementation")

    # Placeholder: Return empty DataFrame with structure
    # TODO: Implement FCC API call when key is available
    # TODO: Alternative - download FCC Broadband Map bulk data

    data = []
    for region_code, region_info in regions.items():
        data.append({
            'region_code': region_code,
            'region_name': region_info['name'],
            'broadband_pct': None,  # Placeholder - no data yet
            'data_year': None,
            'source': 'FCC Broadband Map (pending)',
            'notes': 'Placeholder - FCC API key not yet available'
        })

    df = pd.DataFrame(data)
    logger.info(f"Broadband access data prepared for {len(df)} regions (placeholder)")

    return df


def collect_interstate_presence(regions: dict) -> pd.DataFrame:
    """
    Measure 6.2: Presence of Interstate Highway

    Share of population in counties that contain an interstate highway.
    For multi-county regions, this is the weighted average.

    Args:
        regions: Dictionary of region definitions

    Returns:
        DataFrame with columns: region_code, interstate_share

    Notes:
        - No API available
        - Requires manual mapping of which counties contain interstates
        - Can use Census TIGER/Line shapefiles for spatial analysis
        - Binary variable at county level: 1 if interstate present, 0 if not
        - For regions: weighted by population
    """
    logger.info("Collecting Interstate Highway Presence data (Measure 6.2)")
    logger.warning("Manual data collection required - no API available")

    # Placeholder: Return empty DataFrame with structure
    # TODO: Manual mapping of interstate highways by county
    # TODO: Use Census TIGER/Line roads shapefile for spatial analysis
    # TODO: Or use manual research with state DOT maps

    # Interstate highways in the study area:
    # Virginia: I-64, I-66, I-77, I-81, I-85, I-95, I-264, I-295, I-395, I-495, I-581, I-664
    # Maryland: I-68, I-70, I-81, I-83, I-95, I-97, I-270, I-495, I-695, I-795, I-895
    # West Virginia: I-64, I-68, I-70, I-77, I-79, I-81
    # North Carolina: I-26, I-40, I-73, I-74, I-77, I-85, I-95, I-240, I-440, I-540
    # Tennessee: I-24, I-26, I-40, I-55, I-65, I-75, I-81, I-155, I-240, I-440, I-640
    # Kentucky: I-24, I-64, I-65, I-69, I-71, I-75, I-165, I-169, I-264, I-265, I-275, I-471
    # DC: I-66, I-95, I-295, I-395, I-495, I-695

    data = []
    for region_code, region_info in regions.items():
        data.append({
            'region_code': region_code,
            'region_name': region_info['name'],
            'interstate_share': None,  # Placeholder - manual mapping needed
            'counties_with_interstate': None,
            'total_counties': len(region_info.get('counties', [])),
            'source': 'Census TIGER/Line (manual mapping)',
            'notes': 'Placeholder - manual interstate mapping required'
        })

    df = pd.DataFrame(data)
    logger.info(f"Interstate presence data prepared for {len(df)} regions (placeholder)")

    return df


def collect_four_year_colleges(regions: dict) -> pd.DataFrame:
    """
    Measure 6.3: Count of 4-Year Colleges

    Average number of 4-year degree-granting colleges in the counties where
    regional residents live.

    Args:
        regions: Dictionary of region definitions

    Returns:
        DataFrame with columns: region_code, college_count_avg

    Notes:
        - NCES IPEDS data available as bulk download
        - Filter for 4-year degree-granting institutions
        - Geocode institutions to counties using addresses
        - For multi-county regions: average count weighted by population
    """
    logger.info("Collecting 4-Year Colleges Count data (Measure 6.3)")
    logger.warning("NCES IPEDS bulk download required - no direct API")

    # Placeholder: Return empty DataFrame with structure
    # TODO: Download IPEDS institutional characteristics data
    # TODO: Filter for 4-year institutions (institutional category = 4-year)
    # TODO: Filter for degree-granting institutions
    # TODO: Geocode institutions to counties using ZIP codes or addresses
    # TODO: Count institutions by county
    # TODO: Aggregate to regional level (population-weighted average)

    # IPEDS download: https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx
    # Use "Institutional Characteristics" file
    # Filter variables:
    #   - ICLEVEL (Level of institution): 1 = 4-year
    #   - DEGGRANT (Degree-granting status): 1 = Degree-granting
    #   - FIPS (State FIPS code)
    #   - COUNTYCD (County FIPS code) or COUNTYNM (County name)

    data = []
    for region_code, region_info in regions.items():
        data.append({
            'region_code': region_code,
            'region_name': region_info['name'],
            'college_count': None,  # Placeholder - IPEDS download needed
            'colleges_per_county_avg': None,
            'data_year': None,
            'source': 'NCES IPEDS (bulk download)',
            'notes': 'Placeholder - IPEDS data download required'
        })

    df = pd.DataFrame(data)
    logger.info(f"4-year colleges data prepared for {len(df)} regions (placeholder)")

    return df


def collect_weekly_wage_rate(regions: dict, year: int = 2023, quarter: int = 2) -> pd.DataFrame:
    """
    Measure 6.4: Weekly Wage Rate

    Average weekly wage rate in the region from BLS QCEW data.
    Uses Q2 (April-June) for consistency with Nebraska methodology.

    Args:
        regions: Dictionary of region definitions
        year: Year for data collection (default: 2023)
        quarter: Quarter (1-4, default: 2 for Q2)

    Returns:
        DataFrame with columns: region_code, weekly_wage

    Notes:
        - BLS QCEW API provides average weekly wage directly
        - All industries, total covered employment
        - Inverse scoring: Higher wages = higher cost of doing business
        - But also reflects worker quality and purchasing power
    """
    logger.info(f"Collecting Weekly Wage Rate data (Measure 6.4) for {year} Q{quarter}")

    bls_client = BLSAPIClient(
        api_key=config.BLS_API_KEY,
        cache_dir=config.CACHE_DIR / 'bls',
        rate_limit=500
    )

    data = []

    for region_code, region_info in regions.items():
        logger.info(f"Processing {region_code}: {region_info['name']}")

        # Get state and counties for this region
        state = region_info['state']
        counties = region_info.get('counties', [])

        if not counties:
            logger.warning(f"No counties defined for {region_code}")
            continue

        # Collect weekly wage data for each county in the region
        county_wages = []
        county_employment = []

        for county_name in counties:
            # TODO: Map county name to FIPS code
            # TODO: Use fips_to_region.py mapping or create reverse mapping
            # For now, placeholder
            county_fips = None  # Placeholder

            if not county_fips:
                logger.warning(f"County FIPS code not found for {county_name} in {state}")
                continue

            try:
                # Get weekly wage data from BLS QCEW
                # Series ID format: ENU + state FIPS + county FIPS + ownership + industry + data type
                # For weekly wage: data type = average weekly wage
                # TODO: Implement BLS QCEW weekly wage method in BLS API client

                wage_data = None  # Placeholder - need to implement in BLS client

                if wage_data:
                    county_wages.append(wage_data['weekly_wage'])
                    county_employment.append(wage_data['employment'])

            except Exception as e:
                logger.error(f"Error fetching weekly wage for {county_name}, {state}: {e}")
                continue

        # Calculate employment-weighted average weekly wage for region
        if county_wages and county_employment:
            total_employment = sum(county_employment)
            weighted_wage = sum(w * e for w, e in zip(county_wages, county_employment)) / total_employment
        else:
            weighted_wage = None
            total_employment = None

        data.append({
            'region_code': region_code,
            'region_name': region_info['name'],
            'weekly_wage': weighted_wage,
            'total_employment': total_employment,
            'counties_with_data': len(county_wages),
            'total_counties': len(counties),
            'data_year': year,
            'data_quarter': quarter,
            'source': 'BLS QCEW',
            'notes': 'Employment-weighted average across counties'
        })

    df = pd.DataFrame(data)
    logger.info(f"Weekly wage data collected for {len(df)} regions")

    return df


def collect_state_income_tax_rates(regions: dict) -> pd.DataFrame:
    """
    Measure 6.5: Top Marginal Income Tax Rate

    Highest marginal income tax rate in the state where the region is located.
    Static data from Tax Foundation, updated annually.

    Args:
        regions: Dictionary of region definitions

    Returns:
        DataFrame with columns: region_code, tax_rate

    Notes:
        - State-level data (all regions in same state have same rate)
        - Data from Tax Foundation 2024
        - Inverse scoring: Lower tax rate = better for business
    """
    logger.info("Collecting State Income Tax Rates (Measure 6.5)")

    # State income tax rates (2024 data from Tax Foundation)
    # Source: https://taxfoundation.org/state-income-tax-rates/
    state_tax_rates = {
        'VA': 5.75,   # Virginia - flat rate
        'MD': 5.75,   # Maryland - top marginal rate
        'WV': 6.50,   # West Virginia - top marginal rate
        'NC': 4.75,   # North Carolina - flat rate
        'TN': 0.00,   # Tennessee - no state income tax on wages
        'KY': 4.50,   # Kentucky - flat rate (as of 2024)
        'DC': 10.75   # District of Columbia - top marginal rate
    }

    data = []

    for region_code, region_info in regions.items():
        state_abbr = region_info['state']
        tax_rate = state_tax_rates.get(state_abbr)

        if tax_rate is None:
            logger.warning(f"Tax rate not found for state: {state_abbr}")

        data.append({
            'region_code': region_code,
            'region_name': region_info['name'],
            'state': state_abbr,
            'top_marginal_tax_rate': tax_rate,
            'data_year': 2024,
            'source': 'Tax Foundation',
            'source_url': 'https://taxfoundation.org/state-income-tax-rates/',
            'notes': 'State-level data; top marginal rate or flat rate'
        })

    df = pd.DataFrame(data)
    logger.info(f"State income tax rates assigned to {len(df)} regions")

    return df


def collect_qualified_opportunity_zones(regions: dict) -> pd.DataFrame:
    """
    Measure 6.6: Count of Qualified Opportunity Zones

    Average number of qualified opportunity zones in the counties where
    regional residents live.

    Args:
        regions: Dictionary of region definitions

    Returns:
        DataFrame with columns: region_code, qoz_count_avg

    Notes:
        - QOZs designated in 2018 under Tax Cuts and Jobs Act
        - Static list from U.S. Treasury CDFI Fund
        - QOZ data at census tract level
        - Count QOZ tracts by county
        - For multi-county regions: average count weighted by population
    """
    logger.info("Collecting Qualified Opportunity Zones Count data (Measure 6.6)")
    logger.warning("Treasury CDFI Fund bulk download required - no API")

    # Placeholder: Return empty DataFrame with structure
    # TODO: Download QOZ tract list from Treasury
    # TODO: Source: https://www.cdfifund.gov/opportunity-zones
    # TODO: Map census tracts to counties
    # TODO: Count QOZ tracts by county
    # TODO: Aggregate to regional level (population-weighted average)

    # QOZ data structure (from Treasury):
    #   - State
    #   - County
    #   - Census Tract
    #   - Designation (Low-Income Community or Contiguous)

    data = []
    for region_code, region_info in regions.items():
        data.append({
            'region_code': region_code,
            'region_name': region_info['name'],
            'qoz_count': None,  # Placeholder - Treasury download needed
            'qoz_per_county_avg': None,
            'data_year': 2018,  # QOZ designations
            'source': 'U.S. Treasury CDFI Fund',
            'source_url': 'https://www.cdfifund.gov/opportunity-zones',
            'notes': 'Placeholder - Treasury QOZ data download required'
        })

    df = pd.DataFrame(data)
    logger.info(f"QOZ count data prepared for {len(df)} regions (placeholder)")

    return df


def main():
    """
    Main execution function to collect all Component Index 6 measures.
    """
    logger.info("=" * 80)
    logger.info("Component Index 6: Infrastructure & Cost of Doing Business")
    logger.info("Data Collection Script - Nebraska Methodology")
    logger.info("=" * 80)

    # Load region definitions
    logger.info(f"Total regions defined: {len(REGIONS)}")

    # Create output directory
    output_dir = Path(config.DATA_DIR) / 'component_6_infrastructure_cost'
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Collect each measure
    all_data = {}

    # Measure 6.1: Broadband Internet Access
    try:
        broadband_df = collect_broadband_access(REGIONS)
        all_data['broadband_access'] = broadband_df
        output_file = output_dir / 'measure_6.1_broadband_access.csv'
        broadband_df.to_csv(output_file, index=False)
        logger.info(f"Saved: {output_file}")
    except Exception as e:
        logger.error(f"Error collecting broadband access data: {e}")

    # Measure 6.2: Interstate Presence
    try:
        interstate_df = collect_interstate_presence(REGIONS)
        all_data['interstate_presence'] = interstate_df
        output_file = output_dir / 'measure_6.2_interstate_presence.csv'
        interstate_df.to_csv(output_file, index=False)
        logger.info(f"Saved: {output_file}")
    except Exception as e:
        logger.error(f"Error collecting interstate presence data: {e}")

    # Measure 6.3: 4-Year Colleges Count
    try:
        colleges_df = collect_four_year_colleges(REGIONS)
        all_data['four_year_colleges'] = colleges_df
        output_file = output_dir / 'measure_6.3_four_year_colleges.csv'
        colleges_df.to_csv(output_file, index=False)
        logger.info(f"Saved: {output_file}")
    except Exception as e:
        logger.error(f"Error collecting 4-year colleges data: {e}")

    # Measure 6.4: Weekly Wage Rate
    try:
        wages_df = collect_weekly_wage_rate(REGIONS, year=2023, quarter=2)
        all_data['weekly_wage'] = wages_df
        output_file = output_dir / 'measure_6.4_weekly_wage_rate.csv'
        wages_df.to_csv(output_file, index=False)
        logger.info(f"Saved: {output_file}")
    except Exception as e:
        logger.error(f"Error collecting weekly wage data: {e}")

    # Measure 6.5: State Income Tax Rates
    try:
        tax_df = collect_state_income_tax_rates(REGIONS)
        all_data['state_tax_rates'] = tax_df
        output_file = output_dir / 'measure_6.5_state_income_tax.csv'
        tax_df.to_csv(output_file, index=False)
        logger.info(f"Saved: {output_file}")
    except Exception as e:
        logger.error(f"Error collecting state income tax data: {e}")

    # Measure 6.6: Qualified Opportunity Zones Count
    try:
        qoz_df = collect_qualified_opportunity_zones(REGIONS)
        all_data['opportunity_zones'] = qoz_df
        output_file = output_dir / 'measure_6.6_qualified_opportunity_zones.csv'
        qoz_df.to_csv(output_file, index=False)
        logger.info(f"Saved: {output_file}")
    except Exception as e:
        logger.error(f"Error collecting QOZ count data: {e}")

    # Create summary report
    summary = {
        'collection_date': datetime.now().isoformat(),
        'component_index': 6,
        'component_name': 'Infrastructure & Cost of Doing Business',
        'total_measures': 6,
        'measures_collected': len(all_data),
        'total_regions': len(REGIONS),
        'output_directory': str(output_dir),
        'measures': {
            '6.1': 'Broadband Internet Access (placeholder)',
            '6.2': 'Interstate Presence (placeholder)',
            '6.3': '4-Year Colleges Count (placeholder)',
            '6.4': 'Weekly Wage Rate (BLS QCEW)',
            '6.5': 'State Income Tax Rate (Tax Foundation)',
            '6.6': 'Qualified Opportunity Zones (placeholder)'
        },
        'notes': {
            'broadband': 'FCC API key pending; placeholder implementation',
            'interstate': 'Manual mapping required; Census TIGER/Line shapefiles',
            'colleges': 'NCES IPEDS bulk download required',
            'weekly_wage': 'BLS QCEW API (need to implement method)',
            'tax_rate': 'Static data from Tax Foundation 2024',
            'qoz': 'Treasury CDFI Fund bulk download required'
        }
    }

    summary_file = output_dir / 'collection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 80)
    logger.info("Component Index 6 Data Collection Complete")
    logger.info(f"Measures collected: {len(all_data)}/6")
    logger.info(f"Summary saved: {summary_file}")
    logger.info("=" * 80)

    # Print implementation status
    print("\n" + "=" * 80)
    print("IMPLEMENTATION STATUS - Component Index 6")
    print("=" * 80)
    print("\n✅ READY (Implementation Complete):")
    print("  • 6.5 State Income Tax Rate - Hardcoded from Tax Foundation 2024")
    print("\n🔨 IN PROGRESS (Need to complete implementation):")
    print("  • 6.4 Weekly Wage Rate - BLS QCEW API (need weekly wage method)")
    print("\n📋 MANUAL DATA COLLECTION REQUIRED:")
    print("  • 6.2 Interstate Presence - Census TIGER/Line shapefile analysis")
    print("  • 6.3 4-Year Colleges - NCES IPEDS bulk download")
    print("  • 6.6 Qualified Opportunity Zones - Treasury CDFI Fund download")
    print("\n⏳ PENDING API ACCESS:")
    print("  • 6.1 Broadband Access - FCC API key not yet available")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
