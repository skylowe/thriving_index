"""
Comprehensive data quality validation for county-level data.

Checks all processed data files for:
- Missing values
- FIPS code validity
- Duplicate records
- Outliers
- Data range issues
- Coverage statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime


# Valid FIPS codes for our 10 states
VALID_STATE_FIPS = ['13', '21', '24', '37', '42', '45', '47', '51', '54']
EXPECTED_COUNTIES = 802  # Total counties in 10 states


def load_all_processed_files():
    """Find and load all processed CSV files."""
    data_dir = Path('data/processed')
    csv_files = list(data_dir.glob('*.csv'))

    datasets = {}
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            datasets[file.name] = df
            print(f"  ✓ Loaded {file.name}: {len(df)} records")
        except Exception as e:
            print(f"  ✗ Error loading {file.name}: {e}")

    return datasets


def validate_fips_codes(df, file_name):
    """Validate FIPS codes are properly formatted and valid."""
    issues = []

    # Check if FIPS column exists - expanded list of possible column names
    fips_col = None
    possible_fips_cols = [
        'fips', 'FIPS', 'county_fips', 'GeoFips',
        'full_fips', 'area_fips', 'FIPS Code', 'fips_str',
        'geoid', 'GEOID', 'geo_id'
    ]

    for col in possible_fips_cols:
        if col in df.columns:
            fips_col = col
            break

    # Special case: some files have separate state/county columns
    if fips_col is None:
        if 'state' in df.columns and 'county' in df.columns:
            # Create combined FIPS from state + county
            df_check = df.copy()
            df_check['fips'] = (
                df_check['state'].astype(str).str.zfill(2) +
                df_check['county'].astype(str).str.zfill(3)
            )
            fips_col = 'fips'
        else:
            issues.append("No FIPS code column found")
            return issues
    else:
        df_check = df.copy()

    # Check FIPS format (ensure 5-digit format)
    df_check[fips_col] = df_check[fips_col].astype(str).str.zfill(5)

    # Check for invalid length
    invalid_length = df_check[df_check[fips_col].str.len() != 5]
    if len(invalid_length) > 0:
        issues.append(f"{len(invalid_length)} records with invalid FIPS length")

    # Check for invalid state codes
    df_check['state_fips'] = df_check[fips_col].str[:2]
    invalid_states = df_check[~df_check['state_fips'].isin(VALID_STATE_FIPS)]
    if len(invalid_states) > 0:
        issues.append(f"{len(invalid_states)} records with invalid state FIPS")

    # Check for duplicates
    duplicates = df_check[df_check.duplicated(subset=[fips_col], keep=False)]
    if len(duplicates) > 0:
        issues.append(f"{len(duplicates)} duplicate FIPS codes")

    return issues


def check_missing_values(df, file_name):
    """Check for missing values in critical columns."""
    issues = []

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            pct_missing = (missing_count / len(df)) * 100
            issues.append(f"{col}: {missing_count} missing ({pct_missing:.1f}%)")

    return issues


def detect_outliers(df, file_name):
    """Detect outliers using IQR method."""
    outliers = []

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        if col in ['fips', 'FIPS', 'year', 'state', 'county']:
            continue

        values = df[col].dropna()
        if len(values) < 10:  # Skip if too few values
            continue

        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1

        # Define outlier boundaries
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR

        outlier_mask = (values < lower_bound) | (values > upper_bound)
        outlier_count = outlier_mask.sum()

        if outlier_count > 0:
            pct_outliers = (outlier_count / len(values)) * 100
            outliers.append({
                'column': col,
                'count': int(outlier_count),
                'percentage': round(pct_outliers, 2),
                'range': f"[{values.min():.2f}, {values.max():.2f}]",
                'bounds': f"({lower_bound:.2f}, {upper_bound:.2f})"
            })

    return outliers


def check_data_ranges(df, file_name):
    """Check if values are within expected ranges."""
    issues = []

    # Check percentage columns (should be 0-100)
    # Exclude growth_pct columns which can be negative or >100%
    pct_cols = [col for col in df.columns if 'pct' in col.lower() or 'percent' in col.lower()]
    growth_keywords = ['growth', 'change', 'delta']

    for col in pct_cols:
        if col in df.columns:
            # Skip growth/change percentages (can be negative or >100%)
            if any(keyword in col.lower() for keyword in growth_keywords):
                continue

            values = df[col].dropna()
            if len(values) > 0:
                if values.min() < 0:
                    issues.append(f"{col}: Has negative values (min: {values.min():.2f})")
                if values.max() > 100:
                    issues.append(f"{col}: Exceeds 100% (max: {values.max():.2f})")

    # Check rate columns (should be positive)
    # Note: Some rates like interest rates can be negative, but crime/poverty rates should not be
    rate_cols = [col for col in df.columns if 'rate' in col.lower()]
    for col in rate_cols:
        if col in df.columns:
            values = df[col].dropna()
            if len(values) > 0:
                # Only flag if significantly negative (not just rounding errors)
                if values.min() < -0.01:
                    issues.append(f"{col}: Has negative values (min: {values.min():.2f})")

    return issues


def calculate_coverage_stats(df, file_name):
    """Calculate coverage statistics."""
    stats = {}

    # Count unique FIPS codes - use expanded list
    fips_col = None
    possible_fips_cols = [
        'fips', 'FIPS', 'county_fips', 'GeoFips',
        'full_fips', 'area_fips', 'FIPS Code', 'fips_str',
        'geoid', 'GEOID', 'geo_id'
    ]

    for col in possible_fips_cols:
        if col in df.columns:
            fips_col = col
            break

    # Special case: create FIPS from state + county
    if fips_col is None and 'state' in df.columns and 'county' in df.columns:
        df = df.copy()
        df['fips'] = (
            df['state'].astype(str).str.zfill(2) +
            df['county'].astype(str).str.zfill(3)
        )
        fips_col = 'fips'

    if fips_col:
        df_check = df.copy()
        df_check[fips_col] = df_check[fips_col].astype(str).str.zfill(5)
        df_check['state_fips'] = df_check[fips_col].str[:2]

        # Filter to valid states
        df_valid = df_check[df_check['state_fips'].isin(VALID_STATE_FIPS)]

        stats['total_records'] = len(df)
        stats['valid_state_records'] = len(df_valid)
        stats['unique_counties'] = df_valid[fips_col].nunique()
        stats['coverage_pct'] = round((stats['unique_counties'] / EXPECTED_COUNTIES) * 100, 1)

        # Count by state
        state_counts = df_valid.groupby('state_fips')[fips_col].nunique().to_dict()
        stats['counties_by_state'] = state_counts

    return stats


def validate_dataset(df, file_name):
    """Run all validations on a dataset."""
    print(f"\n{'='*80}")
    print(f"Validating: {file_name}")
    print('='*80)

    results = {
        'file_name': file_name,
        'validation_date': datetime.now().isoformat(),
        'record_count': len(df),
        'column_count': len(df.columns),
        'columns': list(df.columns),
        'issues': {}
    }

    # 1. FIPS validation
    print("\n[1/5] Checking FIPS codes...")
    fips_issues = validate_fips_codes(df, file_name)
    if fips_issues:
        results['issues']['fips'] = fips_issues
        for issue in fips_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✓ No FIPS issues found")

    # 2. Missing values
    print("\n[2/5] Checking for missing values...")
    missing_issues = check_missing_values(df, file_name)
    if missing_issues:
        results['issues']['missing_values'] = missing_issues
        for issue in missing_issues[:10]:  # Show first 10
            print(f"  ⚠️  {issue}")
        if len(missing_issues) > 10:
            print(f"  ... and {len(missing_issues) - 10} more columns with missing values")
    else:
        print("  ✓ No missing values found")

    # 3. Outliers
    print("\n[3/5] Detecting outliers...")
    outlier_list = detect_outliers(df, file_name)
    if outlier_list:
        results['issues']['outliers'] = outlier_list
        for outlier in outlier_list[:5]:  # Show first 5
            print(f"  ⚠️  {outlier['column']}: {outlier['count']} outliers ({outlier['percentage']}%)")
        if len(outlier_list) > 5:
            print(f"  ... and {len(outlier_list) - 5} more columns with outliers")
    else:
        print("  ✓ No extreme outliers detected")

    # 4. Data ranges
    print("\n[4/5] Checking data ranges...")
    range_issues = check_data_ranges(df, file_name)
    if range_issues:
        results['issues']['data_ranges'] = range_issues
        for issue in range_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✓ All values within expected ranges")

    # 5. Coverage stats
    print("\n[5/5] Calculating coverage...")
    coverage = calculate_coverage_stats(df, file_name)
    results['coverage'] = coverage
    if coverage:
        print(f"  Total records: {coverage.get('total_records', 'N/A')}")
        print(f"  Unique counties: {coverage.get('unique_counties', 'N/A')} of {EXPECTED_COUNTIES}")
        print(f"  Coverage: {coverage.get('coverage_pct', 'N/A')}%")

    # Summary
    total_issues = sum(len(v) if isinstance(v, list) else 1
                      for v in results['issues'].values())

    if total_issues == 0:
        print(f"\n✅ No data quality issues found in {file_name}")
    else:
        print(f"\n⚠️  Found {total_issues} potential issues in {file_name}")

    return results


def generate_summary_report(all_results):
    """Generate overall summary report."""
    print("\n" + "="*80)
    print("DATA QUALITY SUMMARY REPORT")
    print("="*80)

    total_files = len(all_results)
    files_with_issues = sum(1 for r in all_results if r['issues'])

    print(f"\nFiles analyzed: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Files clean: {total_files - files_with_issues}")

    # Coverage summary
    print("\n" + "-"*80)
    print("COVERAGE SUMMARY")
    print("-"*80)

    coverage_data = []
    for result in all_results:
        if 'coverage' in result and result['coverage']:
            coverage_data.append({
                'file': result['file_name'],
                'counties': result['coverage'].get('unique_counties', 0),
                'coverage_pct': result['coverage'].get('coverage_pct', 0)
            })

    if coverage_data:
        coverage_df = pd.DataFrame(coverage_data).sort_values('coverage_pct', ascending=False)
        print(coverage_df.to_string(index=False))

    # Issue summary
    print("\n" + "-"*80)
    print("ISSUES BY TYPE")
    print("-"*80)

    issue_counts = {
        'FIPS errors': 0,
        'Missing values': 0,
        'Outliers': 0,
        'Range errors': 0
    }

    for result in all_results:
        if 'fips' in result['issues']:
            issue_counts['FIPS errors'] += len(result['issues']['fips'])
        if 'missing_values' in result['issues']:
            issue_counts['Missing values'] += len(result['issues']['missing_values'])
        if 'outliers' in result['issues']:
            issue_counts['Outliers'] += len(result['issues']['outliers'])
        if 'data_ranges' in result['issues']:
            issue_counts['Range errors'] += len(result['issues']['data_ranges'])

    for issue_type, count in issue_counts.items():
        print(f"  {issue_type}: {count}")

    return {
        'summary': {
            'total_files': total_files,
            'files_with_issues': files_with_issues,
            'files_clean': total_files - files_with_issues,
            'issue_counts': issue_counts
        },
        'coverage': coverage_data,
        'detailed_results': all_results
    }


def main():
    """Run comprehensive data validation."""
    print("="*80)
    print("COUNTY-LEVEL DATA VALIDATION")
    print("="*80)

    # Load all processed files
    print("\nLoading processed data files...")
    datasets = load_all_processed_files()

    if not datasets:
        print("\n⚠️  No data files found in data/processed/")
        return

    print(f"\nFound {len(datasets)} data files to validate")

    # Validate each dataset
    all_results = []
    for file_name, df in datasets.items():
        result = validate_dataset(df, file_name)
        all_results.append(result)

    # Generate summary report
    summary = generate_summary_report(all_results)

    # Save detailed results
    output_dir = Path('data/validation')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON report
    report_file = output_dir / f'data_quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Detailed validation report saved: {report_file}")

    # Save CSV summary
    if summary['coverage']:
        coverage_file = output_dir / 'data_coverage_summary.csv'
        pd.DataFrame(summary['coverage']).to_csv(coverage_file, index=False)
        print(f"✓ Coverage summary saved: {coverage_file}")

    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
