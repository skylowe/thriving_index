"""
Collect Manufacturing Employment Data using BLS QCEW

Collects manufacturing employment percentage for all regions using
BLS Quarterly Census of Employment and Wages (QCEW) data.

Variable 4: % Manufacturing Employment
- Manufacturing employment / Total employment * 100
- Source: BLS QCEW
- NAICS 31-33: Manufacturing
"""

import sys
from pathlib import Path
import json
from typing import Dict
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bls_api import BLSAPI
from src.utils.fips_to_region import get_region_for_fips, get_all_fips_in_region
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def test_qcew_series_format(bls: BLSAPI, logger):
    """
    Test QCEW series ID format to verify it works.

    Tests with a known county to validate series ID construction.
    """
    logger.info("Testing QCEW series ID format...")

    # Test with Fairfax County, VA (51059)
    test_series_ids = []

    # Try different series ID formats
    formats_to_test = [
        # Format 1: ENU + state + county + ownership + industry + data_type
        f"ENU510590531-3301",  # Manufacturing employment
        f"ENU51059051001",     # Total employment

        # Format 2: Different padding
        f"ENU5105905031-3301",
        f"ENU510590510001",
    ]

    for series_id in formats_to_test:
        logger.info(f"  Testing: {series_id}")
        response = bls.get_multiple_series([series_id], 2022, 2022)

        if response.get('status') == 'REQUEST_SUCCEEDED':
            logger.info(f"    ✓ Valid format: {series_id}")
            return series_id[:13]  # Return the pattern
        else:
            logger.info(f"    ✗ Invalid: {response.get('message', 'Unknown error')}")

    logger.warning("  Could not determine valid QCEW series ID format")
    return None


def collect_manufacturing_employment(bls: BLSAPI, logger):
    """
    Collect manufacturing employment percentages using BLS QCEW.

    Returns:
        Dict mapping region code to % manufacturing employment
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Manufacturing Employment via BLS QCEW")
    logger.info("=" * 70)

    # First, test the series ID format
    valid_format = test_qcew_series_format(bls, logger)

    if not valid_format:
        logger.error("\nQCEW series ID format could not be determined")
        logger.error("BLS QCEW timeseries API may not support county-level industry data")
        logger.info("\nAlternative: Use Census County Business Patterns (CBP) API")
        logger.info("  CBP provides employment by NAICS industry at county level")
        logger.info("  API: https://api.census.gov/data/2021/cbp")
        logger.info("  Variable: EMP (Total Employees)")
        logger.info("  NAICS codes: 31-33 (Manufacturing), 00 (Total)")
        return {}

    state_fips_codes = {
        'VA': '51', 'MD': '24', 'WV': '54',
        'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'
    }

    manufacturing_pct = {}

    for state_abbr, state_fips in state_fips_codes.items():
        logger.info(f"\nProcessing {state_abbr}...")

        try:
            # Get all counties in this state from our regional groupings
            state_counties = set()
            for region_code, region_data in ALL_REGIONS.items():
                if region_code.startswith(f"{state_abbr}-"):
                    fips_list = get_all_fips_in_region(region_code)
                    state_counties.update(fips_list)

            logger.info(f"  Found {len(state_counties)} counties in {state_abbr}")

            # Collect data for each county
            county_mfg = {}
            county_total = {}

            for county_fips in state_counties:
                if len(county_fips) != 5:
                    continue

                county_code = county_fips[2:]  # Last 3 digits

                # Build series IDs for manufacturing and total employment
                series_ids = [
                    bls.build_qcew_series_id(state_fips, county_code, '31-33', '5', '01'),  # Mfg
                    bls.build_qcew_series_id(state_fips, county_code, '10', '5', '01'),     # Total
                ]

                response = bls.get_multiple_series(series_ids, 2022, 2022)

                if response.get('status') == 'REQUEST_SUCCEEDED':
                    parsed = bls.parse_series_data(response)

                    # Extract annual average values
                    for series_id, data in parsed.items():
                        if not data:
                            continue

                        # Get annual average (period M13) or Q4 value
                        annual_val = None
                        for point in data:
                            if point.get('period') == 'M13':  # Annual average
                                annual_val = float(point.get('value', 0))
                                break

                        if annual_val:
                            if '3133' in series_id or '31-33' in series_id:
                                county_mfg[county_fips] = annual_val
                            elif series_id.endswith('1001'):
                                county_total[county_fips] = annual_val

            logger.info(f"  Collected manufacturing data for {len(county_mfg)} counties")
            logger.info(f"  Collected total employment for {len(county_total)} counties")

            # Calculate percentages at county level
            county_pct = {}
            for fips in county_mfg.keys():
                if fips in county_total and county_total[fips] > 0:
                    pct = (county_mfg[fips] / county_total[fips]) * 100
                    county_pct[fips] = pct

            # Aggregate to regional level
            regional_sums = defaultdict(float)
            regional_counts = defaultdict(int)

            for fips, pct in county_pct.items():
                region = get_region_for_fips(fips)
                if region:
                    regional_sums[region] += pct
                    regional_counts[region] += 1

            for region in regional_sums:
                if regional_counts[region] > 0:
                    manufacturing_pct[region] = regional_sums[region] / regional_counts[region]

            logger.info(f"  ✓ Calculated % manufacturing for {len(manufacturing_pct)} regions")

        except Exception as e:
            logger.error(f"  ✗ Failed for {state_abbr}: {e}")
            import traceback
            traceback.print_exc()

    return manufacturing_pct


def main():
    """Main execution."""
    logger = setup_logger('collect_manufacturing_qcew')

    logger.info("=" * 70)
    logger.info("COLLECTING MANUFACTURING EMPLOYMENT DATA (BLS QCEW)")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions across 7 states\n")

    # Initialize BLS API client
    bls = BLSAPI()

    # Collect manufacturing employment data
    manufacturing_pct = collect_manufacturing_employment(bls, logger)

    if not manufacturing_pct:
        logger.warning("\n" + "=" * 70)
        logger.warning("NO DATA COLLECTED - QCEW API May Not Support This Use Case")
        logger.warning("=" * 70)
        logger.info("\nRecommendation: Use Census County Business Patterns (CBP) instead")
        logger.info("  CBP is specifically designed for county-level employment by industry")
        logger.info("  Run: python scripts/collect_manufacturing_cbp.py")
        return

    # Load existing matching variables
    matching_vars_file = project_root / 'data' / 'processed' / 'matching_variables.json'

    if matching_vars_file.exists():
        with open(matching_vars_file) as f:
            matching_vars = json.load(f)
    else:
        matching_vars = {
            'metadata': {
                'collection_date': '2025-11-14',
                'regions': len(ALL_REGIONS),
                'description': 'Matching variables for peer region identification'
            },
            'variables': {}
        }

    # Update with manufacturing data
    matching_vars['variables']['pct_manufacturing'] = manufacturing_pct

    # Save results
    with open(matching_vars_file, 'w') as f:
        json.dump(matching_vars, f, indent=2)

    logger.info(f"\n✓ Saved updated matching variables to: {matching_vars_file}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Manufacturing employment: {len(manufacturing_pct)}/{len(ALL_REGIONS)} regions")
    logger.info(f"Coverage: {len(manufacturing_pct)/len(ALL_REGIONS)*100:.1f}%")

    if manufacturing_pct:
        values = list(manufacturing_pct.values())
        logger.info(f"\nManufacturing % statistics:")
        logger.info(f"  Min: {min(values):.2f}%")
        logger.info(f"  Max: {max(values):.2f}%")
        logger.info(f"  Mean: {sum(values)/len(values):.2f}%")

    logger.info("=" * 70)


if __name__ == '__main__':
    main()
