"""
Collect BEA Data for Matching Variables

Collects farm income and manufacturing employment data from BEA API
for all 54 regions.

Variables collected:
- Variable 3: % Farm Income (farm proprietors income / total personal income)
- Variable 4: % Manufacturing Employment (manufacturing jobs / total employment)
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.api_clients.bea_api import BEAAPI
from src.data_processing.aggregate_data import DataAggregator
from src.utils.fips_to_region import get_region_for_fips
from data.regional_groupings import ALL_REGIONS
from src.utils.logging_setup import setup_logger


def collect_farm_income_percentage(bea: BEAAPI, agg: DataAggregator, logger):
    """
    Collect % farm income for all regions.

    Returns:
        Dict mapping region code to % farm income
    """
    logger.info("=" * 70)
    logger.info("Collecting Variable 3: % Farm Income")
    logger.info("=" * 70)

    state_fips_codes = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}

    farm_income_pct = {}

    for state_abbr, state_fips in state_fips_codes.items():
        logger.info(f"\nProcessing {state_abbr}...")

        try:
            # Get farm proprietors income
            logger.info(f"  Fetching farm income...")
            farm_data = bea.get_farm_proprietors_income(year=2022, state=state_fips)

            # Get total personal income
            logger.info(f"  Fetching total income...")
            total_data = bea.get_regional_income(year=2022, state=state_fips, line_codes=[1])

            # Parse responses
            farm_dict = {}
            total_dict = {}

            if farm_data and farm_data.get('BEAAPI'):
                for record in farm_data['BEAAPI'].get('Results', {}).get('Data', []):
                    geo_fips = record.get('GeoFips')
                    value = record.get('DataValue')

                    if geo_fips and value and value not in ['(D)', '(NA)', '(NM)']:
                        try:
                            # GeoFips format: 'XX' + 'YYY' (state + county)
                            if len(geo_fips) == 5:
                                farm_dict[geo_fips] = float(value)
                        except (ValueError, TypeError):
                            pass

            if total_data and total_data.get('BEAAPI'):
                for record in total_data['BEAAPI'].get('Results', {}).get('Data', []):
                    geo_fips = record.get('GeoFips')
                    value = record.get('DataValue')

                    if geo_fips and value and value not in ['(D)', '(NA)', '(NM)']:
                        try:
                            if len(geo_fips) == 5:
                                total_dict[geo_fips] = float(value)
                        except (ValueError, TypeError):
                            pass

            logger.info(f"  Parsed {len(farm_dict)} farm income records")
            logger.info(f"  Parsed {len(total_dict)} total income records")

            # Calculate percentages at county level
            county_pct = {}
            for fips in farm_dict.keys():
                if fips in total_dict and total_dict[fips] > 0:
                    pct = (farm_dict[fips] / total_dict[fips]) * 100
                    county_pct[fips] = pct

            # Aggregate to regional level (use population weighting)
            # For simplicity, use simple average since we're dealing with percentages
            from collections import defaultdict
            regional_sums = defaultdict(float)
            regional_counts = defaultdict(int)

            for fips, pct in county_pct.items():
                region = get_region_for_fips(fips)
                if region:
                    regional_sums[region] += pct
                    regional_counts[region] += 1

            for region in regional_sums:
                if regional_counts[region] > 0:
                    farm_income_pct[region] = regional_sums[region] / regional_counts[region]

            logger.info(f"  ✓ Calculated % farm income for {len(farm_income_pct)} regions")

        except Exception as e:
            logger.error(f"  ✗ Failed for {state_abbr}: {e}")
            import traceback
            traceback.print_exc()

    return farm_income_pct


def collect_manufacturing_percentage(bea: BEAAPI, agg: DataAggregator, logger):
    """
    Collect % manufacturing employment for all regions.

    Returns:
        Dict mapping region code to % manufacturing employment
    """
    logger.info("\n" + "=" * 70)
    logger.info("Collecting Variable 4: % Manufacturing Employment")
    logger.info("=" * 70)

    state_fips_codes = {'VA': '51', 'MD': '24', 'WV': '54', 'NC': '37', 'TN': '47', 'KY': '21', 'DC': '11'}

    mfg_employment_pct = {}

    for state_abbr, state_fips in state_fips_codes.items():
        logger.info(f"\nProcessing {state_abbr}...")

        try:
            # Get manufacturing + total wages (as proxy for employment share)
            logger.info(f"  Fetching wages data (proxy for employment)...")
            wages_data = bea.get_wages_by_industry(
                year=2022,
                state=state_fips,
                industry_codes=[200, 310]  # 200 = Farm, 310 = Manufacturing
            )

            # Also get total earnings
            logger.info(f"  Fetching total earnings...")
            total_data = bea.get_regional_income(
                year=2022,
                state=state_fips,
                line_codes=[10]  # 10 = Wages and salaries (total)
            )

            # Parse manufacturing wages
            mfg_dict = {}
            if wages_data and wages_data.get('BEAAPI'):
                for record in wages_data['BEAAPI'].get('Results', {}).get('Data', []):
                    geo_fips = record.get('GeoFips')
                    line_code = record.get('LineCode')
                    value = record.get('DataValue')

                    if geo_fips and value and value not in ['(D)', '(NA)', '(NM)']:
                        try:
                            if len(geo_fips) == 5 and str(line_code) == '310':
                                mfg_dict[geo_fips] = float(value)
                        except (ValueError, TypeError):
                            pass

            # Parse total wages
            total_dict = {}
            if total_data and total_data.get('BEAAPI'):
                for record in total_data['BEAAPI'].get('Results', {}).get('Data', []):
                    geo_fips = record.get('GeoFips')
                    value = record.get('DataValue')

                    if geo_fips and value and value not in ['(D)', '(NA)', '(NM)']:
                        try:
                            if len(geo_fips) == 5:
                                total_dict[geo_fips] = float(value)
                        except (ValueError, TypeError):
                            pass

            logger.info(f"  Parsed {len(mfg_dict)} manufacturing wage records")
            logger.info(f"  Parsed {len(total_dict)} total wage records")

            # Calculate percentages at county level
            county_pct = {}
            for fips in mfg_dict.keys():
                if fips in total_dict and total_dict[fips] > 0:
                    pct = (mfg_dict[fips] / total_dict[fips]) * 100
                    county_pct[fips] = pct

            # Aggregate to regional level
            from collections import defaultdict
            regional_sums = defaultdict(float)
            regional_counts = defaultdict(int)

            for fips, pct in county_pct.items():
                region = get_region_for_fips(fips)
                if region:
                    regional_sums[region] += pct
                    regional_counts[region] += 1

            for region in regional_sums:
                if regional_counts[region] > 0:
                    mfg_employment_pct[region] = regional_sums[region] / regional_counts[region]

            logger.info(f"  ✓ Calculated % manufacturing for {len(mfg_employment_pct)} regions")

        except Exception as e:
            logger.error(f"  ✗ Failed for {state_abbr}: {e}")
            import traceback
            traceback.print_exc()

    return mfg_employment_pct


def main():
    """Main execution."""
    logger = setup_logger('collect_bea_data')

    logger.info("=" * 70)
    logger.info("COLLECTING BEA DATA FOR MATCHING VARIABLES 3 & 4")
    logger.info("=" * 70)
    logger.info(f"\nTarget: {len(ALL_REGIONS)} regions across 7 states\n")

    # Initialize clients
    bea = BEAAPI()
    agg = DataAggregator()

    # Collect farm income percentage
    farm_income_pct = collect_farm_income_percentage(bea, agg, logger)

    # Collect manufacturing employment percentage
    mfg_employment_pct = collect_manufacturing_percentage(bea, agg, logger)

    # Load existing matching variables
    existing_file = project_root / 'data' / 'processed' / 'matching_variables.json'
    if existing_file.exists():
        with open(existing_file) as f:
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

    # Update with new data
    matching_vars['variables']['pct_farm_income'] = farm_income_pct
    matching_vars['variables']['pct_manufacturing'] = mfg_employment_pct

    # Save results
    output_path = project_root / 'data' / 'processed' / 'matching_variables.json'
    with open(output_path, 'w') as f:
        json.dump(matching_vars, f, indent=2)

    logger.info(f"\n✓ Saved updated matching variables to: {output_path}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 70)

    coverage = {
        'pct_farm_income': len(farm_income_pct),
        'pct_manufacturing': len(mfg_employment_pct)
    }

    for var_name, count in coverage.items():
        pct = (count / len(ALL_REGIONS) * 100) if ALL_REGIONS else 0
        status = "✓ COMPLETE" if count >= len(ALL_REGIONS) * 0.9 else "⏳ PARTIAL"
        logger.info(f"{var_name:25s}: {count:2d}/{len(ALL_REGIONS)} regions ({pct:5.1f}%) {status}")

    logger.info("\n" + "=" * 70)


if __name__ == '__main__':
    main()
