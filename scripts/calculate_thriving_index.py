"""
Calculate Thriving Index scores for Virginia rural regions.

For each Virginia region, calculate scores for all 47 measures across 8 components
using peer region averages as benchmarks.

Scoring formula: score = 100 + ((value - peer_mean) / peer_std_dev) * 100
Where:
- 100 = peer average
- 0 = one standard deviation below peer average
- 200 = one standard deviation above peer average
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Component measure mappings
COMPONENT_MEASURES = {
    'Component 1: Growth Index': {
        'file': 'data/regional/component1_growth_index_regional.csv',
        'measures': [
            'employment_growth_pct',
            'private_employment_2022',  # Will need to convert to per capita
            'wage_growth_pct',
            'hh_children_growth_pct',
            'dir_income_growth_pct'
        ]
    },
    'Component 2: Economic Opportunity & Diversity': {
        'file': 'data/regional/component2_economic_opportunity_regional.csv',
        'measures': [
            'entrepreneurial_activity_per_1000',
            'proprietors_per_1000',
            'establishments_per_1000',
            'telecommuter_share'
            # Note: 3 measures (diversity indexes) not yet aggregated
        ]
    },
    'Component 3: Other Prosperity': {
        'file': 'data/regional/component3_other_prosperity_regional.csv',
        'measures': [
            'gini_index',
            'income_stability_cv',
            'business_stability_score',
            'life_expectancy_years',
            'employer_firm_share'
        ]
    },
    'Component 4: Demographic Growth & Renewal': {
        'file': 'data/regional/component4_demographic_growth_regional.csv',
        'measures': [
            'population_growth_pct',
            'domestic_migration_net_per_1000',
            'working_age_share',
            'median_age',
            'dependency_ratio',
            'aging_rate'
        ]
    },
    'Component 5: Education & Skill': {
        'file': 'data/regional/component5_education_skill_regional.csv',
        'measures': [
            'bachelors_or_higher_pct',
            'high_school_grad_pct',
            'knowledge_workers_pct',
            'avg_test_scores',
            'student_teacher_ratio'
        ]
    },
    'Component 6: Infrastructure & Cost': {
        'file': 'data/regional/component6_infrastructure_cost_regional.csv',
        'measures': [
            'broadband_access',
            'has_interstate',
            'college_count',  # Will need to convert to per capita
            'weekly_wage',
            'income_tax_rate',
            'oz_tract_count'  # Will need to convert to per capita
        ]
    },
    'Component 7: Quality of Life': {
        'file': 'data/regional/component7_quality_of_life_regional.csv',
        'measures': [
            'housing_affordability_ratio',
            'violent_crime_rate',
            'property_crime_rate',
            'national_parks_binary',
            'rec_trails_binary',
            'four_year_college_binary',
            'natural_amenities_scale'
            # Note: health insurance from ACS not yet aggregated
        ]
    },
    'Component 8: Social Capital': {
        'file': 'data/regional/component8_social_capital_regional.csv',
        'measures': [
            'nonprofits_per_1000',
            'volunteer_rate',
            'social_associations_per_10k',
            'voter_turnout',
            'civic_orgs_density'
        ]
    }
}


def load_component_data():
    """Load all component regional data files."""
    component_data = {}

    for component_name, info in COMPONENT_MEASURES.items():
        file_path = Path(info['file'])
        if file_path.exists():
            df = pd.read_csv(file_path)
            component_data[component_name] = df
            print(f"  Loaded {component_name}: {len(df)} regions, {len(info['measures'])} measures")
        else:
            print(f"  ⚠️  Missing: {file_path}")

    return component_data


def load_peer_selections():
    """Load peer region selections."""
    peer_file = Path('data/peer_regions_selected.csv')
    peers_df = pd.read_csv(peer_file)

    # Create a dictionary: VA region key -> list of peer region keys
    peer_map = {}
    for va_key in peers_df['virginia_region_key'].unique():
        peer_regions = peers_df[peers_df['virginia_region_key'] == va_key]['region_key'].tolist()
        peer_map[va_key] = peer_regions

    return peer_map


def calculate_per_capita_measures(df):
    """Convert absolute measures to per capita where needed."""
    df_calc = df.copy()

    # Component 1: Private employment per capita (per 1000)
    if 'private_employment_2022' in df_calc.columns and 'population' not in df_calc.columns:
        # Need to load population data
        pop_data = pd.read_csv('data/processed/census_population_growth_2000_2022.csv')
        pop_data['fips'] = pop_data['fips'].astype(str).str.zfill(5)

        # Aggregate population to regional level
        import sys
        sys.path.append(str(Path(__file__).parent))
        from regional_data_manager import RegionalDataManager
        rdm = RegionalDataManager()

        pop_data['region_key'] = pop_data['fips'].apply(
            lambda fips: rdm.county_to_region.get(str(fips), {}).get('region_key')
            if str(fips) in rdm.county_to_region else None
        )
        pop_data = pop_data[pop_data['region_key'].notna()]
        regional_pop = pop_data.groupby('region_key')['population_2022'].sum().reset_index()
        regional_pop.columns = ['region_key', 'population']

        # Merge with df_calc
        df_calc = df_calc.merge(regional_pop, on='region_key', how='left')

    if 'private_employment_2022' in df_calc.columns and 'population' in df_calc.columns:
        df_calc['private_employment_per_1000'] = (df_calc['private_employment_2022'] /
                                                    df_calc['population'] * 1000)

    # Component 6: College count per 100k
    if 'college_count' in df_calc.columns and 'population' in df_calc.columns:
        df_calc['college_per_100k'] = (df_calc['college_count'] /
                                        df_calc['population'] * 100000)

    # Component 6: OZ tracts per 100k
    if 'oz_tract_count' in df_calc.columns and 'population' in df_calc.columns:
        df_calc['oz_tracts_per_100k'] = (df_calc['oz_tract_count'] /
                                          df_calc['population'] * 100000)

    return df_calc


def calculate_measure_score(va_value, peer_values):
    """
    Calculate score for a single measure.

    Score = 100 + ((value - peer_mean) / peer_std_dev) * 100

    Returns:
        dict with score, peer_mean, peer_std, percentile
    """
    peer_mean = np.mean(peer_values)
    peer_std = np.std(peer_values, ddof=1)  # Sample std dev

    if peer_std == 0:
        # All peers have same value
        score = 100
    else:
        score = 100 + ((va_value - peer_mean) / peer_std) * 100

    # Calculate percentile (where does VA rank among peers + VA)
    all_values = list(peer_values) + [va_value]
    percentile = (sum(v <= va_value for v in all_values) / len(all_values)) * 100

    return {
        'score': score,
        'va_value': va_value,
        'peer_mean': peer_mean,
        'peer_std': peer_std,
        'percentile': percentile
    }


def invert_score_for_negative_measures(score_dict, measure_name):
    """
    Invert scores for measures where lower is better.

    Negative measures (lower is better):
    - Gini index (inequality)
    - Income stability CV (volatility)
    - Median age (older)
    - Dependency ratio (higher)
    - Aging rate (faster)
    - Student-teacher ratio (higher)
    - Weekly wage (cost of doing business - lower wage is better for business, but we'll keep as-is)
    - Income tax rate (lower is better)
    - Violent crime rate (lower is better)
    - Property crime rate (lower is better)
    - Housing affordability ratio (lower is better for affordability)
    """
    negative_measures = [
        'gini_index',
        'income_stability_cv',
        'median_age',
        'dependency_ratio',
        'aging_rate',
        'student_teacher_ratio',
        'income_tax_rate',
        'violent_crime_rate',
        'property_crime_rate',
        'housing_affordability_ratio'
    ]

    if measure_name in negative_measures:
        # Invert: new_score = 200 - old_score
        score_dict['score'] = 200 - score_dict['score']
        score_dict['inverted'] = True
    else:
        score_dict['inverted'] = False

    return score_dict


def calculate_component_scores(va_regions, peer_map, component_data):
    """Calculate scores for all components."""
    results = []

    for va_key in va_regions:
        va_name = None
        peer_keys = peer_map[va_key]

        print(f"\n{'='*80}")
        print(f"Calculating scores for {va_key}")
        print(f"{'='*80}")

        for component_name, info in COMPONENT_MEASURES.items():
            if component_name not in component_data:
                print(f"\n⚠️  Skipping {component_name} - data not loaded")
                continue

            df = component_data[component_name]

            # Add per capita calculations if needed
            if component_name in ['Component 1: Growth Index', 'Component 6: Infrastructure & Cost']:
                df = calculate_per_capita_measures(df)

            # Update measure list if we created per capita versions
            measures = info['measures'].copy()
            if 'private_employment_2022' in measures and 'private_employment_per_1000' in df.columns:
                measures[measures.index('private_employment_2022')] = 'private_employment_per_1000'
            if 'college_count' in measures and 'college_per_100k' in df.columns:
                measures[measures.index('college_count')] = 'college_per_100k'
            if 'oz_tract_count' in measures and 'oz_tracts_per_100k' in df.columns:
                measures[measures.index('oz_tract_count')] = 'oz_tracts_per_100k'

            print(f"\n{component_name}")
            print("-" * 80)

            component_scores = []

            for measure in measures:
                if measure not in df.columns:
                    print(f"  ⚠️  {measure}: Not found in data")
                    continue

                # Get VA value
                va_row = df[df['region_key'] == va_key]
                if len(va_row) == 0:
                    print(f"  ⚠️  {measure}: VA region not found")
                    continue

                if va_name is None:
                    va_name = va_row['region_name'].values[0]

                va_value = va_row[measure].values[0]

                # Get peer values
                peer_rows = df[df['region_key'].isin(peer_keys)]
                peer_values = peer_rows[measure].dropna().values

                if len(peer_values) < 2:
                    print(f"  ⚠️  {measure}: Insufficient peer data ({len(peer_values)} peers)")
                    continue

                # Calculate score
                score_dict = calculate_measure_score(va_value, peer_values)
                score_dict = invert_score_for_negative_measures(score_dict, measure)
                score_dict['measure'] = measure
                score_dict['component'] = component_name
                score_dict['virginia_region_key'] = va_key
                score_dict['virginia_region_name'] = va_name

                component_scores.append(score_dict['score'])

                # Display
                inv_marker = " (inverted)" if score_dict['inverted'] else ""
                print(f"  {measure}{inv_marker}:")
                print(f"    VA: {va_value:.2f} | Peer avg: {score_dict['peer_mean']:.2f} "
                      f"± {score_dict['peer_std']:.2f}")
                print(f"    Score: {score_dict['score']:.1f} | Percentile: {score_dict['percentile']:.0f}%")

                results.append(score_dict)

            # Component average
            if component_scores:
                component_avg = np.mean(component_scores)
                print(f"\n  Component Average: {component_avg:.1f}")

                # Save component score
                results.append({
                    'virginia_region_key': va_key,
                    'virginia_region_name': va_name,
                    'component': component_name,
                    'measure': 'COMPONENT_AVERAGE',
                    'score': component_avg,
                    'va_value': None,
                    'peer_mean': None,
                    'peer_std': None,
                    'percentile': None,
                    'inverted': False
                })

    return pd.DataFrame(results)


def calculate_overall_index(scores_df):
    """Calculate overall Thriving Index from component averages."""
    component_avgs = scores_df[scores_df['measure'] == 'COMPONENT_AVERAGE'].copy()

    overall_scores = []
    for va_key in component_avgs['virginia_region_key'].unique():
        va_components = component_avgs[component_avgs['virginia_region_key'] == va_key]
        va_name = va_components['virginia_region_name'].values[0]

        overall_score = va_components['score'].mean()

        overall_scores.append({
            'virginia_region_key': va_key,
            'virginia_region_name': va_name,
            'overall_thriving_index': overall_score,
            'components_included': len(va_components)
        })

    return pd.DataFrame(overall_scores)


def main():
    """Calculate Thriving Index scores for all Virginia rural regions."""
    print("="*80)
    print("THRIVING INDEX CALCULATION")
    print("="*80)

    # Load data
    print("\n[1/5] Loading component data...")
    component_data = load_component_data()

    print("\n[2/5] Loading peer region selections...")
    peer_map = load_peer_selections()
    print(f"  Loaded peer selections for {len(peer_map)} Virginia regions")
    for va_key, peers in peer_map.items():
        print(f"    {va_key}: {len(peers)} peer regions")

    # Virginia rural regions
    va_regions = list(peer_map.keys())

    # Calculate scores
    print("\n[3/5] Calculating component scores...")
    scores_df = calculate_component_scores(va_regions, peer_map, component_data)

    # Calculate overall index
    print("\n[4/5] Calculating overall Thriving Index...")
    overall_df = calculate_overall_index(scores_df)

    print("\n" + "="*80)
    print("OVERALL THRIVING INDEX SCORES")
    print("="*80)
    overall_sorted = overall_df.sort_values('overall_thriving_index', ascending=False)
    for _, row in overall_sorted.iterrows():
        print(f"{row['virginia_region_name']:50s} {row['overall_thriving_index']:6.1f}")

    # Save results
    print("\n[5/5] Saving results...")

    # Save detailed scores
    scores_file = Path('data/results/thriving_index_detailed_scores.csv')
    scores_file.parent.mkdir(parents=True, exist_ok=True)
    scores_df.to_csv(scores_file, index=False)
    print(f"  ✓ Detailed scores: {scores_file}")

    # Save overall scores
    overall_file = Path('data/results/thriving_index_overall.csv')
    overall_df.to_csv(overall_file, index=False)
    print(f"  ✓ Overall index: {overall_file}")

    # Save component averages
    component_avgs = scores_df[scores_df['measure'] == 'COMPONENT_AVERAGE'][
        ['virginia_region_key', 'virginia_region_name', 'component', 'score']
    ].pivot(index=['virginia_region_key', 'virginia_region_name'],
            columns='component',
            values='score').reset_index()

    component_file = Path('data/results/thriving_index_by_component.csv')
    component_avgs.to_csv(component_file, index=False)
    print(f"  ✓ Component scores: {component_file}")

    print("\n" + "="*80)
    print("🎉 THRIVING INDEX CALCULATION COMPLETE!")
    print("="*80)


if __name__ == '__main__':
    main()
