"""
Collect Manufacturing Employment Data using Census County Business Patterns

Collects manufacturing employment percentage for all regions using
Census County Business Patterns (CBP) API.

Variable 4: % Manufacturing Employment
- Manufacturing employment / Total employment * 100
- Source: Census CBP
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

from src.api_clients.census_api import CensusAPI
from src.utils.fips_to_region import get_region_for_fips
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def collect_manufacturing_cbp(census: CensusAPI, logger):
    """
    Collect manufacturing employment using Census CBP.

    Returns:
        Dict mapping region code to % manufacturing employment
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Manufacturing Employment via Census CBP")
    logger.info("=" * 70)

    state_fips_codes = {
        'VA': '51', 'MD': '24', 'WV': '54',
        'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'
    }

    manufacturing_pct = {}
    county_mfg = {}
    county_total = {}

    for state_abbr, state_fips in state_fips_codes.items():
        logger.info(f"\nProcessing {state_abbr}...")

        try:
            # CBP API endpoint for 2021 (most recent available)
            # Get manufacturing employment (NAICS 31-33)
            mfg_params = {
                'get': 'EMP,NAICS2017_LABEL',
                'for': 'county:*',
                'in': f'state:{state_fips}',
                'NAICS2017': '31-33'  # Manufacturing
            }

            logger.info(f"  Fetching manufacturing employment...")
            mfg_response = census.fetch('/2021/cbp', mfg_params)

            # Get total employment (all NAICS codes)
            total_params = {
                'get': 'EMP',
                'for': 'county:*',
                'in': f'state:{state_fips}',
                'NAICS2017': '00'  # All industries total
            }

            logger.info(f"  Fetching total employment...")
            total_response = census.fetch('/2021/cbp', total_params)

            # Parse manufacturing data
            if mfg_response and len(mfg_response) > 1:
                for row in mfg_response[1:]:  # Skip header row
                    emp_val = row[0]
                    state = row[-2]
                    county = row[-1]

                    if emp_val and emp_val != '(D)' and emp_val != 'N':  # Skip suppressed data
                        fips = f"{state}{county}"
                        try:
                            county_mfg[fips] = int(emp_val)
                        except (ValueError, TypeError):
                            pass

            # Parse total employment
            if total_response and len(total_response) > 1:
                for row in total_response[1:]:
                    emp_val = row[0]
                    state = row[-2]
                    county = row[-1]

                    if emp_val and emp_val != '(D)' and emp_val != 'N':
                        fips = f"{state}{county}"
                        try:
                            county_total[fips] = int(emp_val)
                        except (ValueError, TypeError):
                            pass

            logger.info(f"  Collected manufacturing for {len(county_mfg)} counties")
            logger.info(f"  Collected total employment for {len(county_total)} counties")

        except Exception as e:
            logger.error(f"  ✗ Failed for {state_abbr}: {e}")
            import traceback
            traceback.print_exc()

    # Calculate percentages at county level
    county_pct = {}
    for fips in county_mfg.keys():
        if fips in county_total and county_total[fips] > 0:
            pct = (county_mfg[fips] / county_total[fips]) * 100
            county_pct[fips] = pct

    logger.info(f"\nCalculated percentages for {len(county_pct)} counties")

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

    logger.info(f"✓ Calculated % manufacturing for {len(manufacturing_pct)} regions")

    return manufacturing_pct


def main():
    """Main execution."""
    logger = setup_logger('collect_manufacturing_cbp')

    logger.info("=" * 70)
    logger.info("COLLECTING MANUFACTURING EMPLOYMENT DATA (Census CBP)")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions across 7 states\n")

    # Initialize Census API client
    census = CensusAPI()

    # Collect manufacturing employment data
    manufacturing_pct = collect_manufacturing_cbp(census, logger)

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
    logger.info(f"Manufacturing employment: {len(manufacturing_pct)}/{len(ALL_REGIONS)} regions ({len(manufacturing_pct)/len(ALL_REGIONS)*100:.1f}%)")

    if manufacturing_pct:
        values = list(manufacturing_pct.values())
        logger.info(f"\nManufacturing % statistics:")
        logger.info(f"  Min: {min(values):.2f}%")
        logger.info(f"  Max: {max(values):.2f}%")
        logger.info(f"  Mean: {sum(values)/len(values):.2f}%")

    logger.info("=" * 70)


if __name__ == '__main__':
    main()
