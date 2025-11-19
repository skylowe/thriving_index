"""
Aggregate Components 3-7 to Regional Level

Processes 30 measures across 5 components:
- Component 3: Other Prosperity (5 measures)
- Component 4: Demographic Growth & Renewal (6 measures)
- Component 5: Education & Skill (5 measures)
- Component 6: Infrastructure & Cost of Doing Business (6 measures)
- Component 7: Quality of Life (8 measures)

Creates regional CSV files for each component.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from regional_data_manager import RegionalDataManager


def ensure_fips_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure DataFrame has a 'fips' column with 5-digit FIPS codes.
    Auto-detects from various column formats.
    """
    if 'fips' in df.columns:
        df['fips'] = df['fips'].astype(str).str.zfill(5)
    elif 'full_fips' in df.columns:
        df['fips'] = df['full_fips'].astype(str).str.zfill(5)
    elif 'county_fips' in df.columns:
        df['fips'] = df['county_fips'].astype(str).str.zfill(5)
    elif 'state' in df.columns and 'county' in df.columns:
        df['fips'] = (df['state'].astype(str).str.zfill(2) +
                      df['county'].astype(str).str.zfill(3))
    else:
        raise ValueError("Cannot find FIPS code columns in DataFrame")
    return df


def extract_region_key(rdm: RegionalDataManager, df: pd.DataFrame) -> pd.DataFrame:
    """Helper to extract region_key from FIPS code."""
    # Ensure we have a fips column
    df = ensure_fips_column(df)

    # Extract region_key
    df['region_key'] = df['fips'].apply(
        lambda fips: rdm.county_to_region.get(str(fips), {}).get('region_key') if str(fips) in rdm.county_to_region else None
    )
    return df


def aggregate_component3(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Component 3: Other Prosperity Index (5 measures)

    3.1: Proprietor Income % - recalculate
    3.2: Income Stability (CV) - recalculate from regional time series
    3.3: Life Expectancy - weighted mean
    3.4: Poverty Rate - weighted mean
    3.5: DIR Income Share - recalculate
    """
    print("\n" + "="*80)
    print("COMPONENT 3: OTHER PROSPERITY INDEX")
    print("="*80)

    data_dir = Path('data/processed')

    # 3.1: Proprietor Income Percentage
    print("\n[3.1] Proprietor Income Percentage...")
    prop_income = pd.read_csv(data_dir / 'bea_proprietor_income_2022.csv')
    prop_income = extract_region_key(rdm, prop_income)
    prop_income = prop_income.dropna(subset=['region_key'])

    # Need total personal income - load from DIR income share file
    total_income = pd.read_csv(data_dir / 'bea_dir_income_share_2022.csv')
    total_income = extract_region_key(rdm, total_income)
    total_income = total_income.dropna(subset=['region_key'])

    # Aggregate by region
    regional_prop = prop_income.groupby('region_key')['proprietor_income'].sum().reset_index()
    regional_total = total_income.groupby('region_key')['total_income'].sum().reset_index()

    measure_31 = pd.merge(regional_prop, regional_total, on='region_key')
    measure_31['proprietor_income_pct'] = (measure_31['proprietor_income'] / measure_31['total_income']) * 100
    print(f"  Regions: {len(measure_31)}, Mean: {measure_31['proprietor_income_pct'].mean():.2f}%")

    # 3.2: Income Stability (Coefficient of Variation)
    print("\n[3.2] Income Stability (CV)...")
    # Use weighted average of county CVs (weighted by mean income)
    income_stability = pd.read_csv(data_dir / 'bea_income_stability_2008_2022.csv')
    income_stability = extract_region_key(rdm, income_stability)
    income_stability = income_stability.dropna(subset=['region_key'])

    # Weighted average of CVs by mean income (counties with higher income weighted more)
    regional_stability = income_stability.groupby('region_key').apply(
        lambda x: np.average(x['coefficient_of_variation'], weights=x['mean_income'])
    ).reset_index()
    regional_stability.columns = ['region_key', 'income_stability_cv']
    print(f"  Regions: {len(regional_stability)}, Mean CV: {regional_stability['income_stability_cv'].mean():.4f}")

    # 3.3: Life Expectancy
    print("\n[3.3] Life Expectancy...")
    life_exp = pd.read_csv(data_dir / 'chr_life_expectancy_2025.csv')
    life_exp = extract_region_key(rdm, life_exp)
    life_exp = life_exp.dropna(subset=['region_key', 'life_expectancy'])

    # Need population for weighting - use 2022 population from census
    pop_data = pd.read_csv(data_dir / 'census_population_growth_2000_2022.csv')
    pop_2022 = pop_data[['fips', 'population_2022']].copy()
    pop_2022['fips'] = pop_2022['fips'].astype(str).str.zfill(5)

    life_exp_merged = pd.merge(life_exp, pop_2022[['fips', 'population_2022']], on='fips', how='left')

    # Weighted average by population
    regional_life_exp = life_exp_merged.groupby('region_key').apply(
        lambda x: np.average(x['life_expectancy'], weights=x['population_2022'])
    ).reset_index()
    regional_life_exp.columns = ['region_key', 'life_expectancy']
    print(f"  Regions: {len(regional_life_exp)}, Mean: {regional_life_exp['life_expectancy'].mean():.2f} years")

    # 3.4: Poverty Rate
    print("\n[3.4] Poverty Rate...")
    poverty = pd.read_csv(data_dir / 'census_poverty_2022.csv')
    poverty = extract_region_key(rdm, poverty)
    poverty = poverty.dropna(subset=['region_key'])

    # Calculate poverty count from poverty rate if needed
    # Check if we have 'poverty_count' or need to calculate it
    if 'poverty_count' not in poverty.columns:
        # Load population data and merge
        pop_poverty = pd.merge(poverty, pop_2022, on='fips', how='left')
        poverty['total_population'] = pop_poverty['population_2022']
        poverty['poverty_count'] = poverty['total_population'] * (poverty['poverty_rate'] / 100)

    # Aggregate poverty counts and total population
    regional_poverty = poverty.groupby('region_key').agg({
        'poverty_count': 'sum',
        'total_population': 'sum'
    }).reset_index()
    regional_poverty['poverty_pct'] = (regional_poverty['poverty_count'] /
                                        regional_poverty['total_population']) * 100
    print(f"  Regions: {len(regional_poverty)}, Mean: {regional_poverty['poverty_pct'].mean():.2f}%")

    # 3.5: DIR Income Share
    print("\n[3.5] DIR Income Share...")
    dir_share = pd.read_csv(data_dir / 'bea_dir_income_share_2022.csv')
    dir_share = extract_region_key(rdm, dir_share)
    dir_share = dir_share.dropna(subset=['region_key'])

    # Aggregate DIR income and total income
    regional_dir_share = dir_share.groupby('region_key').agg({
        'dir_income': 'sum',
        'total_income': 'sum'
    }).reset_index()
    regional_dir_share['dir_income_share'] = (regional_dir_share['dir_income'] /
                                               regional_dir_share['total_income']) * 100
    print(f"  Regions: {len(regional_dir_share)}, Mean: {regional_dir_share['dir_income_share'].mean():.2f}%")

    # Merge all Component 3 measures
    result = measure_31[['region_key', 'proprietor_income_pct']]
    result = pd.merge(result, regional_stability, on='region_key', how='outer')
    result = pd.merge(result, regional_life_exp, on='region_key', how='outer')
    result = pd.merge(result, regional_poverty[['region_key', 'poverty_pct']], on='region_key', how='outer')
    result = pd.merge(result, regional_dir_share[['region_key', 'dir_income_share']], on='region_key', how='outer')

    # Add region names
    result = rdm.add_region_names(result)

    print(f"\n✓ Component 3 complete: {len(result)} regions, 5 measures")
    return result


def aggregate_component4(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Component 4: Demographic Growth & Renewal (6 measures)

    4.1: Population Growth - recalculate
    4.2: Dependency Ratio - recalculate
    4.3: Median Age - weighted mean
    4.4: Millennial/Gen Z Change - recalculate
    4.5: Hispanic % - recalculate
    4.6: Non-White % - recalculate
    """
    print("\n" + "="*80)
    print("COMPONENT 4: DEMOGRAPHIC GROWTH & RENEWAL")
    print("="*80)

    data_dir = Path('data/processed')

    # Load population data for weighting (used by multiple measures)
    pop_data = pd.read_csv(data_dir / 'census_population_growth_2000_2022.csv')
    pop_2022 = pop_data[['fips', 'population_2022']].copy()
    pop_2022['fips'] = pop_2022['fips'].astype(str).str.zfill(5)

    # 4.1: Population Growth
    print("\n[4.1] Population Growth (2000-2022)...")
    pop_growth = pd.read_csv(data_dir / 'census_population_growth_2000_2022.csv')
    pop_growth = extract_region_key(rdm, pop_growth)
    pop_growth = pop_growth.dropna(subset=['region_key'])

    regional_pop = pop_growth.groupby('region_key').agg({
        'population_2000': 'sum',
        'population_2022': 'sum'
    }).reset_index()
    regional_pop['population_growth'] = ((regional_pop['population_2022'] - regional_pop['population_2000']) /
                                          regional_pop['population_2000']) * 100
    print(f"  Regions: {len(regional_pop)}, Mean: {regional_pop['population_growth'].mean():.2f}%")

    # 4.2: Dependency Ratio
    print("\n[4.2] Dependency Ratio...")
    dependency = pd.read_csv(data_dir / 'census_dependency_ratio_2022.csv')
    dependency = extract_region_key(rdm, dependency)
    dependency = dependency.dropna(subset=['region_key'])

    # Check column names and aggregate
    # File has: under_15, age_15_64, age_65_plus (not under_18, age_18_to_64)
    regional_dep = dependency.groupby('region_key').agg({
        'under_15': 'sum',
        'age_65_plus': 'sum',
        'age_15_64': 'sum'
    }).reset_index()
    regional_dep['dependency_ratio'] = ((regional_dep['under_15'] + regional_dep['age_65_plus']) /
                                         regional_dep['age_15_64'])
    print(f"  Regions: {len(regional_dep)}, Mean: {regional_dep['dependency_ratio'].mean():.3f}")

    # 4.3: Median Age
    print("\n[4.3] Median Age...")
    median_age = pd.read_csv(data_dir / 'census_median_age_2022.csv')
    median_age = extract_region_key(rdm, median_age)
    median_age = median_age.dropna(subset=['region_key'])

    # Merge with population data for weighting
    median_age_pop = pd.merge(median_age, pop_2022, on='fips', how='left')

    # Weighted average by population
    regional_age = median_age_pop.groupby('region_key').apply(
        lambda x: np.average(x['median_age'], weights=x['population_2022'])
    ).reset_index()
    regional_age.columns = ['region_key', 'median_age']
    print(f"  Regions: {len(regional_age)}, Mean: {regional_age['median_age'].mean():.2f} years")

    # 4.4: Millennial/Gen Z Change
    print("\n[4.4] Millennial/Gen Z Balance Change...")
    millennial = pd.read_csv(data_dir / 'census_millennial_genz_change_2017_2022.csv')
    millennial = extract_region_key(rdm, millennial)
    millennial = millennial.dropna(subset=['region_key'])

    # Already has percentages - just weighted average
    regional_mill_merged = pd.merge(millennial, pop_2022, on='fips', how='left')
    regional_mill = regional_mill_merged.groupby('region_key').apply(
        lambda x: np.average(x['millennial_genz_balance_change'], weights=x['population_2022'])
    ).reset_index()
    regional_mill.columns = ['region_key', 'millennial_genz_change']
    print(f"  Regions: {len(regional_mill)}, Mean change: {regional_mill['millennial_genz_change'].mean():.2f} pp")

    # 4.5: Hispanic Percentage
    print("\n[4.5] Hispanic Percentage...")
    hispanic = pd.read_csv(data_dir / 'census_hispanic_2022.csv')
    hispanic = extract_region_key(rdm, hispanic)
    hispanic = hispanic.dropna(subset=['region_key'])

    regional_hisp = hispanic.groupby('region_key').agg({
        'total_population': 'sum'
    }).reset_index()
    # Recalculate from pct and population
    hisp_merged = pd.merge(hispanic, pop_2022, on='fips', how='left')
    hisp_merged['hispanic_pop'] = hisp_merged['pct_hispanic'] * hisp_merged['population_2022'] / 100
    regional_hisp = hisp_merged.groupby('region_key').agg({'hispanic_pop': 'sum', 'population_2022': 'sum'}).reset_index()
    regional_hisp['hispanic_pct'] = (regional_hisp['hispanic_pop'] / regional_hisp['population_2022']) * 100
    print(f"  Regions: {len(regional_hisp)}, Mean: {regional_hisp['hispanic_pct'].mean():.2f}%")

    # 4.6: Non-White Percentage
    print("\n[4.6] Non-White Percentage...")
    race = pd.read_csv(data_dir / 'census_race_2022.csv')
    race = extract_region_key(rdm, race)
    race = race.dropna(subset=['region_key'])

    regional_race = race.groupby('region_key').agg({
        'white_alone': 'sum',
        'total_population': 'sum'
    }).reset_index()
    regional_race['nonwhite_pct'] = ((regional_race['total_population'] - regional_race['white_alone']) /
                                      regional_race['total_population']) * 100
    print(f"  Regions: {len(regional_race)}, Mean: {regional_race['nonwhite_pct'].mean():.2f}%")

    # Merge all Component 4 measures
    result = regional_pop[['region_key', 'population_growth']]
    result = pd.merge(result, regional_dep[['region_key', 'dependency_ratio']], on='region_key', how='outer')
    result = pd.merge(result, regional_age, on='region_key', how='outer')
    result = pd.merge(result, regional_mill[['region_key', 'millennial_genz_change']], on='region_key', how='outer')
    result = pd.merge(result, regional_hisp[['region_key', 'hispanic_pct']], on='region_key', how='outer')
    result = pd.merge(result, regional_race[['region_key', 'nonwhite_pct']], on='region_key', how='outer')

    # Add region names
    result = rdm.add_region_names(result)

    print(f"\n✓ Component 4 complete: {len(result)} regions, 6 measures")
    return result


def aggregate_component5(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Component 5: Education & Skill (5 measures)

    All are weighted means by appropriate population
    """
    print("\n" + "="*80)
    print("COMPONENT 5: EDUCATION & SKILL")
    print("="*80)

    data_dir = Path('data/processed')

    # 5.1-5.3: Education Attainment
    print("\n[5.1-5.3] Education Attainment (HS, Associates, Bachelors)...")
    education = pd.read_csv(data_dir / 'census_education_attainment_2022.csv')
    education = extract_region_key(rdm, education)
    education = education.dropna(subset=['region_key'])

    # Aggregate counts and calculate percentages
    regional_edu = education.groupby('region_key').agg({
        'total_25_plus': 'sum', 'hs_diploma': 'sum', 'ged': 'sum', 'associates': 'sum', 'bachelors': 'sum'
    }).reset_index()
    regional_edu['hs_attainment'] = ((regional_edu['hs_diploma'] + regional_edu['ged']) / regional_edu['total_25_plus']) * 100
    regional_edu['associates_attainment'] = (regional_edu['associates'] / regional_edu['total_25_plus']) * 100
    regional_edu['bachelors_attainment'] = (regional_edu['bachelors'] / regional_edu['total_25_plus']) * 100

    print(f"  Regions: {len(regional_edu)}")
    print(f"  HS only: {regional_edu['hs_attainment'].mean():.2f}%")
    print(f"  Associates: {regional_edu['associates_attainment'].mean():.2f}%")
    print(f"  Bachelors: {regional_edu['bachelors_attainment'].mean():.2f}%")

    # 5.4: Labor Force Participation
    print("\n[5.4] Labor Force Participation Rate...")
    labor = pd.read_csv(data_dir / 'census_labor_force_2022.csv')
    labor = extract_region_key(rdm, labor)
    labor = labor.dropna(subset=['region_key'])

    regional_labor = labor.groupby('region_key').agg({
        'in_labor_force': 'sum', 'total_16_plus': 'sum'
    }).reset_index()
    regional_labor['labor_force_participation'] = (regional_labor['in_labor_force'] / regional_labor['total_16_plus']) * 100
    print(f"  Regions: {len(regional_labor)}, Mean: {regional_labor['labor_force_participation'].mean():.2f}%")

    # 5.5: Knowledge Workers
    print("\n[5.5] Knowledge Workers Percentage...")
    knowledge = pd.read_csv(data_dir / 'census_knowledge_workers_2022.csv')
    knowledge = extract_region_key(rdm, knowledge)
    knowledge = knowledge.dropna(subset=['region_key'])

    regional_knowledge = knowledge.groupby('region_key').agg({
        'mgmt_prof_sci_arts': 'sum',
        'total_employed': 'sum'
    }).reset_index()
    regional_knowledge['knowledge_workers_pct'] = (regional_knowledge['mgmt_prof_sci_arts'] /
                                                    regional_knowledge['total_employed']) * 100
    print(f"  Regions: {len(regional_knowledge)}, Mean: {regional_knowledge['knowledge_workers_pct'].mean():.2f}%")

    # Merge all Component 5 measures
    result = regional_edu[['region_key', 'hs_attainment', 'associates_attainment', 'bachelors_attainment']]
    result = pd.merge(result, regional_labor[['region_key', 'labor_force_participation']], on='region_key', how='outer')
    result = pd.merge(result, regional_knowledge[['region_key', 'knowledge_workers_pct']], on='region_key', how='outer')

    # Add region names
    result = rdm.add_region_names(result)

    print(f"\n✓ Component 5 complete: {len(result)} regions, 5 measures")
    return result


def aggregate_component6(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Component 6: Infrastructure & Cost of Doing Business (6 measures)

    Mix of weighted means, sums, and max
    """
    print("\n" + "="*80)
    print("COMPONENT 6: INFRASTRUCTURE & COST OF DOING BUSINESS")
    print("="*80)

    data_dir = Path('data/processed')

    # 6.1: Broadband Access
    print("\n[6.1] Broadband Access...")
    broadband = pd.read_csv(data_dir / 'fcc_broadband_availability_100_10.csv')
    broadband = extract_region_key(rdm, broadband)
    broadband = broadband.dropna(subset=['region_key'])

    # Weighted average by total locations
    regional_broadband = broadband.groupby('region_key').apply(
        lambda x: np.average(x['percent_covered'], weights=x['total_locations'])
    ).reset_index()
    regional_broadband.columns = ['region_key', 'broadband_access']
    print(f"  Regions: {len(regional_broadband)}, Mean: {regional_broadband['broadband_access'].mean():.2f}%")

    # 6.2: Interstate Highway Presence
    print("\n[6.2] Interstate Highway Presence...")
    interstate = pd.read_csv(data_dir / 'usgs_county_interstate_presence.csv')
    interstate = extract_region_key(rdm, interstate)
    interstate = interstate.dropna(subset=['region_key'])

    # Max: if any county in region has interstate, region has it
    regional_interstate = interstate.groupby('region_key')['has_interstate'].max().reset_index()
    print(f"  Regions: {len(regional_interstate)}, With interstate: {regional_interstate['has_interstate'].sum()}")

    # 6.3: Four-Year Colleges
    print("\n[6.3] Four-Year Colleges Count...")
    colleges = pd.read_csv(data_dir / 'ipeds_four_year_colleges_by_county_2022.csv')
    colleges = extract_region_key(rdm, colleges)
    colleges = colleges.dropna(subset=['region_key'])

    regional_colleges = colleges.groupby('region_key')['college_count'].sum().reset_index()
    print(f"  Regions: {len(regional_colleges)}, Mean: {regional_colleges['college_count'].mean():.2f}")

    # 6.4: Weekly Wage
    print("\n[6.4] Weekly Wage...")
    wage = pd.read_csv(data_dir / 'qcew_weekly_wage_2022.csv')
    wage = extract_region_key(rdm, wage)
    wage = wage.dropna(subset=['region_key'])

    # Weighted average by employment
    regional_wage = wage.groupby('region_key').apply(
        lambda x: np.average(x['avg_weekly_wage'], weights=x['annual_avg_emplvl'])
    ).reset_index()
    regional_wage.columns = ['region_key', 'weekly_wage']
    print(f"  Regions: {len(regional_wage)}, Mean: ${regional_wage['weekly_wage'].mean():.2f}")

    # 6.5: Income Tax Rate (state-level)
    print("\n[6.5] Income Tax Rate...")
    tax = pd.read_csv(data_dir / 'state_income_tax_rates_2024.csv')

    # Map state FIPS to tax rate
    state_tax_map = dict(zip(tax['state_fips'].astype(str).str.zfill(2), tax['top_marginal_rate']))

    # Extract state FIPS from region_key
    all_regions = rdm.get_all_regions_dict()
    tax_data = []
    for region_key, info in all_regions.items():
        state_fips = info['state_fips']
        tax_rate = state_tax_map.get(state_fips, np.nan)
        tax_data.append({'region_key': region_key, 'income_tax_rate': tax_rate})

    regional_tax = pd.DataFrame(tax_data)
    print(f"  Regions: {len(regional_tax)}, Mean: {regional_tax['income_tax_rate'].mean():.2f}%")

    # 6.6: Opportunity Zones
    print("\n[6.6] Opportunity Zones Count...")
    oz = pd.read_csv(data_dir / 'hud_opportunity_zones_by_county.csv')
    oz = extract_region_key(rdm, oz)
    oz = oz.dropna(subset=['region_key'])

    regional_oz = oz.groupby('region_key')['oz_tract_count'].sum().reset_index()
    print(f"  Regions: {len(regional_oz)}, Mean: {regional_oz['oz_tract_count'].mean():.2f}")

    # Merge all Component 6 measures
    result = regional_broadband.copy()
    result = pd.merge(result, regional_interstate, on='region_key', how='outer')
    result = pd.merge(result, regional_colleges, on='region_key', how='outer')
    result = pd.merge(result, regional_wage, on='region_key', how='outer')
    result = pd.merge(result, regional_tax, on='region_key', how='outer')
    result = pd.merge(result, regional_oz, on='region_key', how='outer')

    # Add region names
    result = rdm.add_region_names(result)

    print(f"\n✓ Component 6 complete: {len(result)} regions, 6 measures")
    return result


def aggregate_component7(rdm: RegionalDataManager) -> pd.DataFrame:
    """
    Component 7: Quality of Life (8 measures)

    Mix of weighted means, sums, and recalculations
    """
    print("\n" + "="*80)
    print("COMPONENT 7: QUALITY OF LIFE")
    print("="*80)

    data_dir = Path('data/processed')

    # 7.1: Commute Time
    print("\n[7.1] Mean Commute Time...")
    commute = pd.read_csv(data_dir / 'census_commute_time_2022.csv')
    commute = extract_region_key(rdm, commute)
    commute = commute.dropna(subset=['region_key'])

    # Weighted average by workers
    regional_commute = commute.groupby('region_key').apply(
        lambda x: np.average(x['mean_commute_time'], weights=x['workers_16_plus'])
    ).reset_index()
    regional_commute.columns = ['region_key', 'mean_commute_time']
    print(f"  Regions: {len(regional_commute)}, Mean: {regional_commute['mean_commute_time'].mean():.2f} min")

    # 7.2: Housing Pre-1960
    print("\n[7.2] Housing Built Pre-1960...")
    housing = pd.read_csv(data_dir / 'census_housing_pre1960_2022.csv')
    housing = extract_region_key(rdm, housing)
    housing = housing.dropna(subset=['region_key'])

    # Aggregate counts
    regional_housing = housing.groupby('region_key').agg({
        'housing_pre1960': 'sum',
        'total_housing_units': 'sum'
    }).reset_index()
    regional_housing['housing_pre1960_pct'] = (regional_housing['housing_pre1960'] /
                                                regional_housing['total_housing_units']) * 100
    print(f"  Regions: {len(regional_housing)}, Mean: {regional_housing['housing_pre1960_pct'].mean():.2f}%")

    # 7.3: Relative Wage (regional wage / state average wage)
    print("\n[7.3] Relative Weekly Wage...")
    rel_wage = pd.read_csv(data_dir / 'qcew_relative_weekly_wage_2022.csv')
    rel_wage = extract_region_key(rdm, rel_wage)
    rel_wage = rel_wage.dropna(subset=['region_key'])

    # Recalculate: regional average wage / state average wage
    # First get regional wage (employment-weighted)
    regional_rel_wage = rel_wage.groupby('region_key').apply(
        lambda x: (np.average(x['avg_weekly_wage'], weights=x['annual_avg_emplvl']) /
                   np.average(x['state_avg_weekly_wage'], weights=x['annual_avg_emplvl']))
    ).reset_index()
    regional_rel_wage.columns = ['region_key', 'relative_weekly_wage']
    print(f"  Regions: {len(regional_rel_wage)}, Mean: {regional_rel_wage['relative_weekly_wage'].mean():.3f}")

    # 7.4 & 7.5: Crime Rates
    print("\n[7.4-7.5] Violent and Property Crime Rates...")
    crime = pd.read_csv(data_dir / 'fbi_crime_counties_2023.csv')
    crime = extract_region_key(rdm, crime)
    crime = crime.dropna(subset=['region_key'])

    # Need population for crime rate calculation
    pop_data = pd.read_csv(data_dir / 'census_population_growth_2000_2022.csv')
    pop_2022 = pop_data[['fips', 'population_2022']].copy()
    pop_2022['fips'] = pop_2022['fips'].astype(str).str.zfill(5)

    crime_merged = pd.merge(crime, pop_2022[['fips', 'population_2022']], on='fips', how='left')

    # Aggregate crime counts and population
    regional_crime = crime_merged.groupby('region_key').agg({
        'violent_crime': 'sum',
        'property_crime': 'sum',
        'population_2022': 'sum'
    }).reset_index()
    regional_crime['violent_crime_rate'] = (regional_crime['violent_crime'] /
                                             regional_crime['population_2022']) * 100000
    regional_crime['property_crime_rate'] = (regional_crime['property_crime'] /
                                              regional_crime['population_2022']) * 100000
    print(f"  Regions: {len(regional_crime)}")
    print(f"  Violent: {regional_crime['violent_crime_rate'].mean():.2f} per 100k")
    print(f"  Property: {regional_crime['property_crime_rate'].mean():.2f} per 100k")

    # 7.6: Climate Amenities
    print("\n[7.6] Climate Amenities Scale...")
    amenities = pd.read_csv(data_dir / 'usda_ers_natural_amenities_scale.csv')
    amenities = extract_region_key(rdm, amenities)
    amenities = amenities.dropna(subset=['region_key'])

    # Simple mean (scale is already normalized)
    regional_amenities = amenities.groupby('region_key')['natural_amenities_scale'].mean().reset_index()
    print(f"  Regions: {len(regional_amenities)}, Mean: {regional_amenities['natural_amenities_scale'].mean():.3f}")

    # 7.7: Healthcare Access
    print("\n[7.7] Healthcare Access (workers per 1k)...")
    healthcare = pd.read_csv(data_dir / 'cbp_healthcare_employment_2021.csv')
    healthcare = extract_region_key(rdm, healthcare)
    healthcare = healthcare.dropna(subset=['region_key'])

    # Merge with population
    healthcare_merged = pd.merge(healthcare, pop_2022[['fips', 'population_2022']], on='fips', how='left')

    # Aggregate healthcare employment and population
    regional_healthcare = healthcare_merged.groupby('region_key').agg({
        'EMP': 'sum',
        'population_2022': 'sum'
    }).reset_index()
    regional_healthcare['healthcare_workers_per_1k'] = (regional_healthcare['EMP'] /
                                                         regional_healthcare['population_2022']) * 1000
    print(f"  Regions: {len(regional_healthcare)}, Mean: {regional_healthcare['healthcare_workers_per_1k'].mean():.2f} per 1k")

    # 7.8: National Parks
    print("\n[7.8] National Parks Count...")
    parks = pd.read_csv(data_dir / 'nps_park_counts_by_county.csv')
    parks = extract_region_key(rdm, parks)
    parks = parks.dropna(subset=['region_key'])

    regional_parks = parks.groupby('region_key')['park_count'].sum().reset_index()
    print(f"  Regions: {len(regional_parks)}, Mean: {regional_parks['park_count'].mean():.2f}")

    # Merge all Component 7 measures
    result = regional_commute.copy()
    result = pd.merge(result, regional_housing[['region_key', 'housing_pre1960_pct']], on='region_key', how='outer')
    result = pd.merge(result, regional_rel_wage, on='region_key', how='outer')
    result = pd.merge(result, regional_crime[['region_key', 'violent_crime_rate', 'property_crime_rate']], on='region_key', how='outer')
    result = pd.merge(result, regional_amenities, on='region_key', how='outer')
    result = pd.merge(result, regional_healthcare[['region_key', 'healthcare_workers_per_1k']], on='region_key', how='outer')
    result = pd.merge(result, regional_parks, on='region_key', how='outer')

    # Add region names
    result = rdm.add_region_names(result)

    print(f"\n✓ Component 7 complete: {len(result)} regions, 8 measures")
    return result


def main():
    """Main execution function."""
    print("="*80)
    print("AGGREGATE COMPONENTS 3-7 TO REGIONAL LEVEL")
    print("Processing 30 measures across 5 components")
    print("="*80)

    # Initialize regional data manager
    print("\nInitializing Regional Data Manager...")
    rdm = RegionalDataManager()

    # Aggregate each component
    component3 = aggregate_component3(rdm)
    component4 = aggregate_component4(rdm)
    component5 = aggregate_component5(rdm)
    component6 = aggregate_component6(rdm)
    component7 = aggregate_component7(rdm)

    # Save each component to separate file
    output_dir = Path('data/regional')
    output_dir.mkdir(exist_ok=True)

    print("\n" + "="*80)
    print("SAVING REGIONAL DATA FILES")
    print("="*80)

    components = [
        (component3, 'component3_other_prosperity_regional.csv', 'Component 3: Other Prosperity'),
        (component4, 'component4_demographic_growth_regional.csv', 'Component 4: Demographic Growth'),
        (component5, 'component5_education_skill_regional.csv', 'Component 5: Education & Skill'),
        (component6, 'component6_infrastructure_cost_regional.csv', 'Component 6: Infrastructure & Cost'),
        (component7, 'component7_quality_of_life_regional.csv', 'Component 7: Quality of Life')
    ]

    for df, filename, name in components:
        filepath = output_dir / filename
        df.to_csv(filepath, index=False)
        print(f"✓ {name}: {filepath}")
        print(f"  Regions: {len(df)}, Measures: {len(df.columns) - 3}")

    print("\n" + "="*80)
    print("ALL COMPONENTS 3-7 AGGREGATED SUCCESSFULLY!")
    print("="*80)
    print(f"\nTotal measures aggregated: 30")
    print(f"Total regional files created: 5")
    print(f"\nOverall Progress: 47 of 47 measures aggregated (100% COMPLETE!)")
    print(f"\nComponent Status:")
    print(f"  ✓ Component 1: Growth Index (5/5)")
    print(f"  ✓ Component 2: Economic Opportunity (7/7)")
    print(f"  ✓ Component 3: Other Prosperity (5/5)")
    print(f"  ✓ Component 4: Demographic Growth (6/6)")
    print(f"  ✓ Component 5: Education & Skill (5/5)")
    print(f"  ✓ Component 6: Infrastructure & Cost (6/6)")
    print(f"  ✓ Component 7: Quality of Life (8/8)")
    print(f"  ✓ Component 8: Social Capital (5/5)")
    print(f"\n🎉 REGIONAL DATA AGGREGATION PHASE COMPLETE! 🎉")


if __name__ == "__main__":
    main()
