"""
Regional Aggregation Configuration for Thriving Index Measures

Defines how each of the 47 measures should be aggregated from county-level
to regional-level data.

Aggregation Methods:
- 'sum': Sum county values (for absolute counts)
- 'weighted_mean': Population-weighted average (for rates/percentages)
- 'recalculate': Recalculate from aggregated components (for growth rates)
- 'mean': Simple average (rarely used)
- 'max': Maximum value (for binary indicators like highway presence)
"""

# Component 1: Growth Index (5 measures)
# Note: Growth rates must be RECALCULATED from aggregated base/current values
COMPONENT1_CONFIG = {
    '1.1_employment_growth': {
        'description': 'Growth in Total Employment',
        'method': 'recalculate',
        'base_measure': 'employment_2020',
        'current_measure': 'employment_2022',
        'aggregation': 'sum',  # Sum employment counts
        'formula': '((current - base) / base) * 100'
    },
    '1.2_private_employment': {
        'description': 'Private Employment (level)',
        'method': 'sum',  # Sum private employment
        'value_column': 'annual_avg_emplvl'
    },
    '1.3_wage_growth': {
        'description': 'Growth in Private Wages Per Job',
        'method': 'recalculate',
        'base_measure': 'avg_annual_pay_2020',
        'current_measure': 'avg_annual_pay_2022',
        'aggregation': 'weighted_mean',  # Weighted by employment
        'weight_column': 'annual_avg_emplvl',
        'formula': '((current - base) / base) * 100'
    },
    '1.4_households_children_growth': {
        'description': 'Growth in Households with Children',
        'method': 'recalculate',
        'base_measure': 'households_with_children_2017',
        'current_measure': 'households_with_children_2022',
        'aggregation': 'sum',  # Sum household counts
        'formula': '((current - base) / base) * 100'
    },
    '1.5_dir_income_growth': {
        'description': 'Growth in DIR Income',
        'method': 'recalculate',
        'base_measure': 'dir_income_2020',
        'current_measure': 'dir_income_2022',
        'aggregation': 'sum',  # Sum income dollars
        'formula': '((current - base) / base) * 100'
    }
}

# Component 2: Economic Opportunity & Diversity (7 measures)
COMPONENT2_CONFIG = {
    '2.1_entrepreneurial_activity': {
        'description': 'Entrepreneurial Activity (per capita)',
        'method': 'recalculate',
        'numerator': 'entrepreneurial_activity_count',  # births + deaths
        'denominator': 'population',
        'aggregation': 'sum',  # Sum both numerator and denominator
        'formula': 'numerator / denominator'
    },
    '2.2_proprietors_per_1000': {
        'description': 'Non-Farm Proprietors Per 1,000 Persons',
        'method': 'recalculate',
        'numerator': 'nonfarm_proprietors',
        'denominator': 'population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 1000'
    },
    '2.3_establishments_per_1000': {
        'description': 'Employer Establishments Per 1,000 Persons',
        'method': 'recalculate',
        'numerator': 'establishments',
        'denominator': 'population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 1000'
    },
    '2.4_nonemployer_share': {
        'description': 'Share of Non-Employer Workers',
        'method': 'recalculate',
        'numerator': 'nonemployer_count',
        'denominator': 'total_workers',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100'
    },
    '2.5_industry_diversity': {
        'description': 'Industry Diversity (Herfindahl index)',
        'method': 'recalculate',
        'note': 'Calculate regional employment shares across 19 NAICS sectors',
        'requires_multi_file': True,
        'files': 'cbp_industry_naics*_2021.csv',
        'formula': '1 - sum(share_i^2) for all industries i'
    },
    '2.6_occupation_diversity': {
        'description': 'Occupation Diversity (Herfindahl index)',
        'method': 'recalculate',
        'note': 'Calculate regional occupation shares across major occupation groups',
        'formula': '1 - sum(share_i^2) for all occupations i'
    },
    '2.7_telecommuter_share': {
        'description': 'Share of Telecommuters',
        'method': 'weighted_mean',
        'value_column': 'telecommuter_pct',
        'weight_column': 'total_workers'
    }
}

# Component 3: Other Economic Prosperity (5 measures)
COMPONENT3_CONFIG = {
    '3.1_proprietor_income_pct': {
        'description': 'Non-Farm Proprietor Income as % of Total Income',
        'method': 'recalculate',
        'numerator': 'proprietor_income',
        'denominator': 'total_personal_income',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100'
    },
    '3.2_income_stability': {
        'description': 'Personal Income Stability (CV)',
        'method': 'recalculate',
        'note': 'Calculate coefficient of variation for regional income time series',
        'requires_timeseries': True,
        'years': range(2008, 2023),
        'formula': 'std_dev / mean'
    },
    '3.3_life_expectancy': {
        'description': 'Life Expectancy (years)',
        'method': 'weighted_mean',
        'value_column': 'life_expectancy',
        'weight_column': 'population'
    },
    '3.4_poverty_rate': {
        'description': 'Poverty Rate (%)',
        'method': 'weighted_mean',
        'value_column': 'poverty_pct',
        'weight_column': 'total_population'
    },
    '3.5_dir_income_share': {
        'description': 'Share of DIR Income',
        'method': 'recalculate',
        'numerator': 'dir_income',
        'denominator': 'total_personal_income',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100'
    }
}

# Component 4: Demographic Growth & Renewal (6 measures)
COMPONENT4_CONFIG = {
    '4.1_population_growth': {
        'description': 'Long-Run Population Growth (2000-2022)',
        'method': 'recalculate',
        'base_measure': 'population_2000',
        'current_measure': 'population_2022',
        'aggregation': 'sum',
        'formula': '((current - base) / base) * 100'
    },
    '4.2_dependency_ratio': {
        'description': 'Dependency Ratio',
        'method': 'recalculate',
        'note': 'Recalculate from age distribution',
        'numerator': 'dependent_population',  # <18 + 65+
        'denominator': 'working_age_population',  # 18-64
        'aggregation': 'sum',
        'formula': 'numerator / denominator'
    },
    '4.3_median_age': {
        'description': 'Median Age',
        'method': 'weighted_mean',
        'value_column': 'median_age',
        'weight_column': 'total_population'
    },
    '4.4_millennial_genz_change': {
        'description': 'Millennial/Gen Z Balance Change',
        'method': 'recalculate',
        'base_measure': 'millennial_genz_pct_2017',
        'current_measure': 'millennial_genz_pct_2022',
        'note': 'Recalculate percentages from age counts',
        'formula': 'current - base (percentage point change)'
    },
    '4.5_hispanic_pct': {
        'description': 'Percent Hispanic',
        'method': 'recalculate',
        'numerator': 'hispanic_population',
        'denominator': 'total_population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100'
    },
    '4.6_nonwhite_pct': {
        'description': 'Percent Non-White',
        'method': 'recalculate',
        'numerator': 'nonwhite_population',
        'denominator': 'total_population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100'
    }
}

# Component 5: Education & Skill (5 measures)
COMPONENT5_CONFIG = {
    '5.1_hs_attainment': {
        'description': 'High School Only Attainment Rate',
        'method': 'weighted_mean',
        'value_column': 'hs_only_pct',
        'weight_column': 'population_25_plus'
    },
    '5.2_associates_attainment': {
        'description': "Associate's Degree Only Attainment Rate",
        'method': 'weighted_mean',
        'value_column': 'associates_only_pct',
        'weight_column': 'population_25_plus'
    },
    '5.3_bachelors_attainment': {
        'description': "Bachelor's Degree Only Attainment Rate",
        'method': 'weighted_mean',
        'value_column': 'bachelors_only_pct',
        'weight_column': 'population_25_plus'
    },
    '5.4_labor_force_participation': {
        'description': 'Labor Force Participation Rate',
        'method': 'weighted_mean',
        'value_column': 'lfpr',
        'weight_column': 'population_16_plus'
    },
    '5.5_knowledge_workers': {
        'description': 'Percent of Knowledge Workers',
        'method': 'weighted_mean',
        'value_column': 'knowledge_worker_pct',
        'weight_column': 'total_employed'
    }
}

# Component 6: Infrastructure & Cost of Doing Business (6 measures)
COMPONENT6_CONFIG = {
    '6.1_broadband_access': {
        'description': 'Broadband Internet Access (% households)',
        'method': 'weighted_mean',
        'value_column': 'broadband_pct',
        'weight_column': 'total_locations'  # or population
    },
    '6.2_interstate_highway': {
        'description': 'Interstate Highway Presence',
        'method': 'max',  # If any county in region has interstate, region has it
        'value_column': 'has_interstate',
        'note': 'Binary measure: 1 if region has interstate, 0 otherwise'
    },
    '6.3_four_year_colleges': {
        'description': 'Count of 4-Year Colleges',
        'method': 'weighted_mean',
        'value_column': 'college_count',
        'weight_column': 'population',
        'note': 'Population-weighted average per Nebraska methodology ("average number of colleges where residents live")'
    },
    '6.4_weekly_wage': {
        'description': 'Weekly Wage Rate',
        'method': 'weighted_mean',
        'value_column': 'avg_weekly_wage',
        'weight_column': 'annual_avg_emplvl'
    },
    '6.5_income_tax_rate': {
        'description': 'Top Marginal Income Tax Rate',
        'method': 'state_level',
        'note': 'State-level measure, same for all regions in a state'
    },
    '6.6_opportunity_zones': {
        'description': 'Qualified Opportunity Zones',
        'method': 'weighted_mean',
        'value_column': 'oz_tract_count',
        'weight_column': 'population',
        'note': 'Population-weighted average per Nebraska methodology ("average number of OZs where residents live")'
    }
}

# Component 7: Quality of Life (8 measures)
COMPONENT7_CONFIG = {
    '7.1_commute_time': {
        'description': 'Mean Commute Time (minutes)',
        'method': 'weighted_mean',
        'value_column': 'mean_commute_time',
        'weight_column': 'workers_16_plus'
    },
    '7.2_housing_pre1960': {
        'description': 'Percent Housing Built Pre-1960',
        'method': 'weighted_mean',
        'value_column': 'housing_pre1960_pct',
        'weight_column': 'total_housing_units'
    },
    '7.3_relative_wage': {
        'description': 'Relative Weekly Wage',
        'method': 'recalculate',
        'note': 'Calculate regional wage relative to state average',
        'formula': 'regional_avg_wage / state_avg_wage'
    },
    '7.4_violent_crime_rate': {
        'description': 'Violent Crime Rate (per 100k)',
        'method': 'recalculate',
        'numerator': 'total_violent_crimes',
        'denominator': 'population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100000'
    },
    '7.5_property_crime_rate': {
        'description': 'Property Crime Rate (per 100k)',
        'method': 'recalculate',
        'numerator': 'total_property_crimes',
        'denominator': 'population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 100000'
    },
    '7.6_climate_amenities': {
        'description': 'Climate Amenities Scale',
        'method': 'mean',  # Simple average of amenity scale
        'value_column': 'natural_amenities_scale'
    },
    '7.7_healthcare_access': {
        'description': 'Healthcare Access (workers per 1k)',
        'method': 'recalculate',
        'numerator': 'healthcare_employment',
        'denominator': 'population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 1000'
    },
    '7.8_national_parks': {
        'description': 'Count of National Parks',
        'method': 'sum',
        'value_column': 'park_count'
    }
}

# Component 8: Social Capital (5 measures)
COMPONENT8_CONFIG = {
    '8.1_nonprofits_per_1000': {
        'description': '501(c)(3) Organizations Per 1,000 Persons',
        'method': 'recalculate',
        'numerator': 'org_count_501c3',
        'denominator': 'total_population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 1000'
    },
    '8.2_volunteer_rate': {
        'description': 'Volunteer Rate (%)',
        'method': 'weighted_mean',
        'value_column': 'volunteering_rate',
        'weight_column': 'total_population'
    },
    '8.3_social_associations': {
        'description': 'Social Associations Per 10k',
        'method': 'recalculate',
        'numerator': 'social_associations_count',
        'denominator': 'total_population',
        'aggregation': 'sum',
        'formula': '(numerator / denominator) * 10000'
    },
    '8.4_voter_turnout': {
        'description': 'Voter Turnout (%)',
        'method': 'weighted_mean',
        'value_column': 'voter_turnout_pct',
        'weight_column': 'eligible_voters'  # or total_population if not available
    },
    '8.5_civic_orgs_density': {
        'description': 'Civic Organizations Density (per 1k users)',
        'method': 'weighted_mean',
        'value_column': 'civic_organizations_per_1k',
        'weight_column': 'total_population'
    }
}

# Master configuration combining all components
AGGREGATION_CONFIG = {
    'component1': COMPONENT1_CONFIG,
    'component2': COMPONENT2_CONFIG,
    'component3': COMPONENT3_CONFIG,
    'component4': COMPONENT4_CONFIG,
    'component5': COMPONENT5_CONFIG,
    'component6': COMPONENT6_CONFIG,
    'component7': COMPONENT7_CONFIG,
    'component8': COMPONENT8_CONFIG
}


def get_measure_config(component: str, measure: str) -> dict:
    """
    Get aggregation configuration for a specific measure.

    Args:
        component: Component name (e.g., 'component1')
        measure: Measure ID (e.g., '1.1_employment_growth')

    Returns:
        Dictionary with aggregation configuration
    """
    if component not in AGGREGATION_CONFIG:
        raise ValueError(f"Unknown component: {component}")

    if measure not in AGGREGATION_CONFIG[component]:
        raise ValueError(f"Unknown measure {measure} in {component}")

    return AGGREGATION_CONFIG[component][measure]


def get_all_measures() -> dict:
    """
    Get flat dictionary of all measures across all components.

    Returns:
        Dictionary mapping measure ID to config
    """
    all_measures = {}
    for component, measures in AGGREGATION_CONFIG.items():
        for measure_id, config in measures.items():
            all_measures[measure_id] = {
                'component': component,
                **config
            }
    return all_measures


def print_aggregation_summary():
    """Print summary of aggregation methods across all measures."""
    print("=" * 80)
    print("AGGREGATION METHODS SUMMARY")
    print("=" * 80)
    print()

    method_counts = {}
    for component, measures in AGGREGATION_CONFIG.items():
        for measure_id, config in measures.items():
            method = config.get('method', 'unknown')
            if method not in method_counts:
                method_counts[method] = 0
            method_counts[method] += 1

    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        print(f"{method:20} - {count:2} measures")

    print()
    print(f"Total measures: {sum(method_counts.values())}")
    print()


if __name__ == "__main__":
    print_aggregation_summary()
