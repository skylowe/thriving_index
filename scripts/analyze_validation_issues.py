"""
Analyze data validation report and prioritize fixes.
"""

import json
import pandas as pd
from pathlib import Path


def load_validation_report():
    """Load the most recent validation report."""
    validation_dir = Path('data/validation')
    report_files = list(validation_dir.glob('data_quality_report_*.json'))

    if not report_files:
        print("No validation report found!")
        return None

    # Get most recent report
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading: {latest_report.name}\n")

    with open(latest_report, 'r') as f:
        return json.load(f)


def analyze_critical_issues(report):
    """Identify and prioritize critical data quality issues."""
    print("="*80)
    print("CRITICAL DATA QUALITY ISSUES")
    print("="*80)

    critical_issues = []

    # Check coverage issues
    print("\n[1] FILES WITH ZERO OR LOW COVERAGE (<90%)")
    print("-"*80)
    for item in report['coverage']:
        if item['coverage_pct'] < 90:
            critical_issues.append({
                'severity': 'CRITICAL',
                'file': item['file'],
                'issue': f"Coverage: {item['coverage_pct']}% ({item['counties']}/802 counties)",
                'type': 'coverage'
            })
            print(f"  ⚠️  {item['file']}: {item['coverage_pct']}% coverage")

    if not any(item['coverage_pct'] < 90 for item in report['coverage']):
        print("  ✓ All files have adequate coverage (>=90%)")

    # Check for range violations
    print("\n[2] DATA RANGE VIOLATIONS")
    print("-"*80)
    range_issues_found = False
    for result in report['detailed_results']:
        if 'data_ranges' in result.get('issues', {}):
            range_issues_found = True
            for issue in result['issues']['data_ranges']:
                critical_issues.append({
                    'severity': 'HIGH',
                    'file': result['file_name'],
                    'issue': issue,
                    'type': 'range'
                })
                print(f"  ⚠️  {result['file_name']}: {issue}")

    if not range_issues_found:
        print("  ✓ All values within expected ranges")

    # Check for missing FIPS columns
    print("\n[3] FIPS CODE ISSUES")
    print("-"*80)
    fips_issues_found = False
    for result in report['detailed_results']:
        if 'fips' in result.get('issues', {}):
            for issue in result['issues']['fips']:
                if 'No FIPS code column found' in issue:
                    critical_issues.append({
                        'severity': 'MEDIUM',
                        'file': result['file_name'],
                        'issue': issue,
                        'type': 'fips_missing'
                    })
                    print(f"  ⚠️  {result['file_name']}: {issue}")
                    fips_issues_found = True
                elif 'duplicate' in issue.lower():
                    # Duplicates might be OK for time series data
                    print(f"  ℹ️  {result['file_name']}: {issue} (may be time series)")
                else:
                    critical_issues.append({
                        'severity': 'HIGH',
                        'file': result['file_name'],
                        'issue': issue,
                        'type': 'fips_invalid'
                    })
                    print(f"  ⚠️  {result['file_name']}: {issue}")
                    fips_issues_found = True

    if not fips_issues_found:
        print("  ✓ All FIPS codes valid")

    # Check for excessive missing values
    print("\n[4] EXCESSIVE MISSING VALUES (>10%)")
    print("-"*80)
    missing_issues_found = False
    for result in report['detailed_results']:
        if 'missing_values' in result.get('issues', {}):
            for issue in result['issues']['missing_values']:
                # Extract percentage
                if '(' in issue and '%' in issue:
                    pct_str = issue.split('(')[1].split('%')[0]
                    try:
                        pct = float(pct_str)
                        if pct > 10:
                            critical_issues.append({
                                'severity': 'MEDIUM',
                                'file': result['file_name'],
                                'issue': issue,
                                'type': 'missing_values'
                            })
                            print(f"  ⚠️  {result['file_name']}: {issue}")
                            missing_issues_found = True
                    except ValueError:
                        pass

    if not missing_issues_found:
        print("  ✓ No excessive missing values (all <10%)")

    # Summary
    print("\n" + "="*80)
    print(f"TOTAL CRITICAL ISSUES: {len(critical_issues)}")
    print("="*80)

    severity_counts = {}
    for issue in critical_issues:
        severity = issue['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
        count = severity_counts.get(severity, 0)
        print(f"  {severity}: {count}")

    return critical_issues


def create_fix_plan(critical_issues):
    """Generate prioritized fix plan."""
    print("\n" + "="*80)
    print("RECOMMENDED FIX PLAN")
    print("="*80)

    # Group by type
    by_type = {}
    for issue in critical_issues:
        issue_type = issue['type']
        if issue_type not in by_type:
            by_type[issue_type] = []
        by_type[issue_type].append(issue)

    priorities = [
        ('coverage', 'CRITICAL', 'Fix files with zero or low coverage'),
        ('range', 'HIGH', 'Fix data range violations (percentages > 100%, negative values)'),
        ('fips_invalid', 'HIGH', 'Fix invalid FIPS codes'),
        ('fips_missing', 'MEDIUM', 'Add FIPS columns to files missing them'),
        ('missing_values', 'MEDIUM', 'Investigate excessive missing values')
    ]

    print("\nPriority Order:")
    for i, (issue_type, severity, description) in enumerate(priorities, 1):
        issues = by_type.get(issue_type, [])
        if issues:
            print(f"\n{i}. {description} [{severity}]")
            print(f"   Affected files: {len(issues)}")
            for issue in issues[:3]:  # Show first 3
                print(f"     - {issue['file']}")
            if len(issues) > 3:
                print(f"     ... and {len(issues) - 3} more")

    return by_type


def main():
    """Run validation analysis."""
    report = load_validation_report()

    if not report:
        return

    # Analyze issues
    critical_issues = analyze_critical_issues(report)

    # Create fix plan
    fix_plan = create_fix_plan(critical_issues)

    # Save analysis
    output_file = Path('data/validation/critical_issues_analysis.json')
    with open(output_file, 'w') as f:
        json.dump({
            'total_critical_issues': len(critical_issues),
            'issues_by_type': {k: len(v) for k, v in fix_plan.items()},
            'detailed_issues': critical_issues
        }, f, indent=2)

    print(f"\n✓ Analysis saved to: {output_file}")


if __name__ == '__main__':
    main()
