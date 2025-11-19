"""
Regional Map Page Implementation for Dashboard

Functions to create interactive map showing Virginia regions and their peers.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import geopandas as gpd


@st.cache_data
def load_geographic_data():
    """Load region and county boundary GeoJSON files."""
    regions_gdf = gpd.read_file('data/geojson/region_boundaries.geojson')
    counties_gdf = gpd.read_file('data/geojson/county_boundaries.geojson')

    return regions_gdf, counties_gdf


def create_regional_map(regions_gdf, counties_gdf, selected_va_region, peer_regions_df, components_df):
    """
    Create interactive choropleth map with region and county boundaries.

    Args:
        regions_gdf: GeoDataFrame of region boundaries
        counties_gdf: GeoDataFrame of county boundaries
        selected_va_region: Selected Virginia region key (e.g., '51_1')
        peer_regions_df: DataFrame of peer region selections
        components_df: DataFrame with component scores

    Returns:
        Plotly figure
    """
    # Get peer regions for selected VA region
    peer_rows = peer_regions_df[peer_regions_df['virginia_region_key'] == selected_va_region]
    peer_region_keys = peer_rows['region_key'].tolist()

    # Merge regions with component scores
    regions_with_scores = regions_gdf.merge(
        components_df[['virginia_region_key', 'component', 'component_score']].groupby('virginia_region_key')['component_score'].mean().reset_index().rename(columns={'virginia_region_key': 'region_key', 'component_score': 'overall_score'}),
        on='region_key',
        how='left'
    )

    # Create color column based on selection
    def assign_color(row):
        if row['region_key'] == selected_va_region:
            return 'Selected Virginia Region'
        elif row['region_key'] in peer_region_keys:
            return 'Peer Region'
        else:
            return 'Other Region'

    regions_with_scores['category'] = regions_with_scores.apply(assign_color, axis=1)

    # Color scheme
    color_map = {
        'Selected Virginia Region': '#1f77b4',  # Blue
        'Peer Region': '#ff7f0e',               # Orange
        'Other Region': '#d3d3d3'               # Light gray
    }

    # Create figure
    fig = go.Figure()

    # Add county boundaries (faint)
    for idx, row in counties_gdf.iterrows():
        # Get county boundary coordinates
        if row.geometry.geom_type == 'Polygon':
            coords = list(row.geometry.exterior.coords)
        else:  # MultiPolygon
            coords = list(row.geometry.geoms[0].exterior.coords)

        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]

        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(width=0.3, color='rgba(200,200,200,0.3)'),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add regions (colored by category)
    for category in ['Other Region', 'Peer Region', 'Selected Virginia Region']:
        subset = regions_with_scores[regions_with_scores['category'] == category]

        for idx, row in subset.iterrows():
            # Get region boundary coordinates
            if row.geometry.geom_type == 'Polygon':
                coords = list(row.geometry.exterior.coords)
            else:  # MultiPolygon - use first polygon
                coords = list(row.geometry.geoms[0].exterior.coords)

            lons = [coord[0] for coord in coords]
            lats = [coord[1] for coord in coords]

            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines',
                fill='toself',
                fillcolor=color_map[category],
                line=dict(width=1.5, color='rgba(0,0,0,0.5)'),
                name=category,
                legendgroup=category,
                showlegend=(idx == subset.index[0]),  # Only show legend for first in group
                text=f"{row['region_name']}<br>{row['state_name']}<br>Score: {row['overall_score']:.1f}" if pd.notna(row['overall_score']) else f"{row['region_name']}<br>{row['state_name']}",
                hoverinfo='text'
            ))

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Regional Map: {selected_va_region} and Peer Regions",
            x=0.5,
            xanchor='center'
        ),
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            center=dict(lat=37.5, lon=-79),
            projection_scale=8
        ),
        height=700,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)'
        )
    )

    return fig


def create_comparison_table(selected_va_region, peer_regions_df, components_df):
    """
    Create comparison table showing selected VA region and peers.

    Args:
        selected_va_region: Selected Virginia region key
        peer_regions_df: DataFrame of peer selections
        components_df: DataFrame with component scores

    Returns:
        DataFrame for display
    """
    # Get peer regions
    peer_rows = peer_regions_df[peer_regions_df['virginia_region_key'] == selected_va_region].copy()
    peer_rows = peer_rows.sort_values('peer_rank')

    # Get component scores - pivot to wide format
    scores_wide = components_df.pivot_table(
        index='virginia_region_key',
        columns='component',
        values='component_score'
    ).reset_index()

    # Calculate overall score (mean of components)
    component_cols = [col for col in scores_wide.columns if col != 'virginia_region_key']
    scores_wide['Overall'] = scores_wide[component_cols].mean(axis=1)

    # Get VA region scores
    va_scores = scores_wide[scores_wide['virginia_region_key'] == selected_va_region]

    if len(va_scores) == 0:
        return pd.DataFrame()

    # Build comparison table
    table_data = []

    # Add VA region
    va_row = {
        'Region': peer_rows['virginia_region_name'].iloc[0],
        'State': 'Virginia',
        'Type': 'Selected'
    }
    # Add component scores
    for col in component_cols:
        va_row[col.replace('Component ', 'C')] = va_scores[col].iloc[0]
    va_row['Overall'] = va_scores['Overall'].iloc[0]
    table_data.append(va_row)

    # Add peer regions
    for _, peer in peer_rows.iterrows():
        peer_scores = scores_wide[scores_wide['virginia_region_key'] == peer['region_key']]

        if len(peer_scores) > 0:
            peer_row = {
                'Region': peer['region_name'],
                'State': peer['state_name'],
                'Type': f"Peer #{peer['peer_rank']}"
            }
            # Add component scores
            for col in component_cols:
                peer_row[col.replace('Component ', 'C')] = peer_scores[col].iloc[0]
            peer_row['Overall'] = peer_scores['Overall'].iloc[0]
            table_data.append(peer_row)

    table_df = pd.DataFrame(table_data)

    return table_df


# Example usage in dashboard:
"""
# Regional Map Page
elif page == "Regional Map":
    st.markdown('<p class="main-header">Regional Comparison Map</p>', unsafe_allow_html=True)

    # Load geographic data
    regions_gdf, counties_gdf = load_geographic_data()

    # Get list of VA regions
    va_regions = overall_df[['virginia_region_key', 'virginia_region_name']].to_dict('records')
    va_region_options = {f"{r['virginia_region_name']}": r['virginia_region_key'] for r in va_regions}

    # Selection dropdown
    selected_name = st.selectbox(
        "Select Virginia Region:",
        options=list(va_region_options.keys()),
        index=0
    )
    selected_va_region = va_region_options[selected_name]

    # Create map
    st.subheader("Interactive Regional Map")
    fig_map = create_regional_map(
        regions_gdf,
        counties_gdf,
        selected_va_region,
        peers,
        components
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Comparison table
    st.subheader("Component Comparison Table")
    comparison_df = create_comparison_table(selected_va_region, peers, components)

    if len(comparison_df) > 0:
        st.dataframe(
            comparison_df.style.format({
                col: '{:.1f}' for col in comparison_df.columns if col not in ['Region', 'State', 'Type']
            }).background_gradient(
                subset=[col for col in comparison_df.columns if col not in ['Region', 'State', 'Type']],
                cmap='RdYlGn',
                vmin=50,
                vmax=150
            ),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("No comparison data available for this region.")
"""
