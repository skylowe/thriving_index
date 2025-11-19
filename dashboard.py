"""
Virginia Rural Thriving Index - Interactive Dashboard

A Streamlit dashboard for exploring thriving index scores across 6 Virginia rural regions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import geopandas as gpd
import json

# Page configuration
st.set_page_config(
    page_title="Virginia Rural Thriving Index",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .highlight-green {
        color: #28a745;
        font-weight: bold;
    }
    .highlight-red {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load all thriving index data."""
    overall = pd.read_csv('data/results/thriving_index_overall.csv')
    components = pd.read_csv('data/results/thriving_index_by_component.csv')
    detailed = pd.read_csv('data/results/thriving_index_detailed_scores.csv')
    peers = pd.read_csv('data/peer_regions_selected.csv')

    return overall, components, detailed, peers


@st.cache_data
def load_geographic_data():
    """Load simplified region and state boundary GeoJSON files."""
    regions_gdf = gpd.read_file('data/geojson/region_boundaries_simplified.geojson')
    states_gdf = gpd.read_file('data/geojson/state_boundaries.geojson')

    return regions_gdf, states_gdf


def create_rankings_chart(overall_df):
    """Create horizontal bar chart of overall rankings."""
    # Sort by score
    df_sorted = overall_df.sort_values('overall_thriving_index', ascending=True)

    # Color based on above/below peer average (100)
    colors = ['#28a745' if x >= 100 else '#dc3545'
              for x in df_sorted['overall_thriving_index']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_sorted['virginia_region_name'],
        x=df_sorted['overall_thriving_index'],
        orientation='h',
        marker=dict(color=colors),
        text=df_sorted['overall_thriving_index'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
    ))

    # Add vertical line at 100 (peer average)
    fig.add_vline(x=100, line_dash="dash", line_color="gray",
                  annotation_text="Peer Average", annotation_position="top")

    fig.update_layout(
        title="Overall Thriving Index Rankings",
        xaxis_title="Thriving Index Score",
        yaxis_title="",
        height=400,
        showlegend=False,
        xaxis=dict(range=[0, max(df_sorted['overall_thriving_index']) * 1.1])
    )

    return fig


def create_component_radar(components_df, selected_regions=None):
    """Create radar chart comparing components across regions."""
    # Get component columns
    component_cols = [col for col in components_df.columns
                     if col.startswith('Component')]

    # Filter regions if specified
    if selected_regions:
        df = components_df[components_df['virginia_region_name'].isin(selected_regions)]
    else:
        df = components_df

    # Shorten component names for display
    component_names = [col.replace('Component ', '').split(':')[1].strip()
                      for col in component_cols]

    fig = go.Figure()

    for _, row in df.iterrows():
        values = [row[col] for col in component_cols]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=component_names,
            fill='toself',
            name=row['virginia_region_name']
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 350]  # Max score can exceed 200
            )
        ),
        showlegend=True,
        title="Component Scores by Region",
        height=600
    )

    return fig


def create_component_heatmap(components_df):
    """Create heatmap of component scores."""
    # Prepare data
    component_cols = [col for col in components_df.columns
                     if col.startswith('Component')]

    # Shorten names
    short_names = [col.replace('Component ', '').split(':')[0] for col in component_cols]

    # Create matrix
    data_matrix = components_df[component_cols].values
    region_names = components_df['virginia_region_name'].values

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=short_names,
        y=region_names,
        colorscale='RdYlGn',
        zmid=100,  # Center at peer average
        text=np.round(data_matrix, 1),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Score")
    ))

    fig.update_layout(
        title="Component Scores Heatmap (100 = Peer Average)",
        xaxis_title="Component",
        yaxis_title="Region",
        height=400
    )

    return fig


def create_peer_comparison_chart(peers_df, va_region_key):
    """Create chart showing peer regions and their distances."""
    # Filter to selected VA region
    region_peers = peers_df[peers_df['virginia_region_key'] == va_region_key]
    region_peers = region_peers.sort_values('mahalanobis_distance')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=region_peers['peer_rank'],
        y=region_peers['mahalanobis_distance'],
        marker=dict(color=region_peers['mahalanobis_distance'],
                   colorscale='Viridis',
                   showscale=True,
                   colorbar=dict(title="Distance")),
        text=region_peers['region_name'],
        hovertemplate='<b>%{text}</b><br>' +
                     'Rank: %{x}<br>' +
                     'Distance: %{y:.3f}<br>' +
                     '<extra></extra>'
    ))

    fig.update_layout(
        title=f"Peer Regions for {region_peers['virginia_region_name'].values[0]}",
        xaxis_title="Peer Rank",
        yaxis_title="Mahalanobis Distance",
        height=400
    )

    return fig


def create_measure_comparison(detailed_df, va_region_key, component_filter=None):
    """Create detailed measure comparison chart."""
    # Filter to region
    region_data = detailed_df[detailed_df['virginia_region_key'] == va_region_key]

    # Exclude component averages
    region_data = region_data[region_data['measure'] != 'COMPONENT_AVERAGE']

    # Filter by component if specified
    if component_filter:
        region_data = region_data[region_data['component'] == component_filter]

    # Sort by score
    region_data = region_data.sort_values('score', ascending=True)

    # Color based on score
    colors = ['#28a745' if x >= 100 else '#dc3545'
              for x in region_data['score']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=region_data['measure'],
        x=region_data['score'],
        orientation='h',
        marker=dict(color=colors),
        text=region_data['score'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                     'Score: %{x:.1f}<br>' +
                     '<extra></extra>'
    ))

    # Add vertical line at 100
    fig.add_vline(x=100, line_dash="dash", line_color="gray")

    fig.update_layout(
        title="Measure Scores (100 = Peer Average)",
        xaxis_title="Score",
        yaxis_title="",
        height=max(400, len(region_data) * 25),
        showlegend=False
    )

    return fig


# Main app
def main():
    # Load data
    overall_df, components_df, detailed_df, peers_df = load_data()

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Component Analysis", "Regional Deep Dive", "Regional Map", "Peer Comparison", "Data Explorer"]
    )

    # Overview Page
    if page == "Overview":
        st.markdown('<p class="main-header">Virginia Rural Thriving Index</p>',
                   unsafe_allow_html=True)

        st.markdown("""
        This dashboard presents the Thriving Index scores for 6 rural Virginia regions,
        comparing them to peer regions across the United States.

        **Score Interpretation:**
        - **100** = Peer average performance
        - **>100** = Above peer average
        - **<100** = Below peer average
        """)

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            above_avg = (overall_df['overall_thriving_index'] >= 100).sum()
            st.metric("Regions Above Peer Average", f"{above_avg} of 6")

        with col2:
            top_score = overall_df['overall_thriving_index'].max()
            st.metric("Highest Score", f"{top_score:.1f}")

        with col3:
            avg_score = overall_df['overall_thriving_index'].mean()
            st.metric("Average Score", f"{avg_score:.1f}")

        with col4:
            range_score = overall_df['overall_thriving_index'].max() - overall_df['overall_thriving_index'].min()
            st.metric("Score Range", f"{range_score:.1f}")

        # Rankings chart
        st.plotly_chart(create_rankings_chart(overall_df), use_container_width=True)

        # Component heatmap
        st.plotly_chart(create_component_heatmap(components_df), use_container_width=True)

        # Top performers by component
        st.subheader("Top Performers by Component")

        component_cols = [col for col in components_df.columns if col.startswith('Component')]

        top_performers = []
        for col in component_cols:
            idx = components_df[col].idxmax()
            top_performers.append({
                'Component': col.split(':')[1].strip(),
                'Region': components_df.loc[idx, 'virginia_region_name'],
                'Score': components_df.loc[idx, col]
            })

        top_df = pd.DataFrame(top_performers).sort_values('Score', ascending=False)
        st.dataframe(top_df, hide_index=True, use_container_width=True)

    # Component Analysis Page
    elif page == "Component Analysis":
        st.markdown('<p class="main-header">Component Analysis</p>', unsafe_allow_html=True)

        # Region selector
        all_regions = components_df['virginia_region_name'].tolist()
        selected_regions = st.multiselect(
            "Select regions to compare (leave empty for all)",
            all_regions,
            default=None
        )

        # Radar chart
        st.plotly_chart(
            create_component_radar(components_df, selected_regions if selected_regions else None),
            use_container_width=True
        )

        # Component scores table
        st.subheader("Component Scores Detail")

        display_df = components_df.copy()
        if selected_regions:
            display_df = display_df[display_df['virginia_region_name'].isin(selected_regions)]

        # Rename columns for display
        component_cols = [col for col in display_df.columns if col.startswith('Component')]
        rename_dict = {col: col.split(':')[1].strip() for col in component_cols}
        display_df = display_df.rename(columns=rename_dict)

        st.dataframe(
            display_df[['virginia_region_name'] + list(rename_dict.values())],
            hide_index=True,
            use_container_width=True
        )

    # Regional Deep Dive Page
    elif page == "Regional Deep Dive":
        st.markdown('<p class="main-header">Regional Deep Dive</p>', unsafe_allow_html=True)

        # Region selector
        region_names = overall_df['virginia_region_name'].tolist()
        selected_region_name = st.selectbox("Select a region", region_names)

        # Get region key
        selected_region_key = overall_df[
            overall_df['virginia_region_name'] == selected_region_name
        ]['virginia_region_key'].values[0]

        # Overall score
        overall_score = overall_df[
            overall_df['virginia_region_name'] == selected_region_name
        ]['overall_thriving_index'].values[0]

        rank = overall_df.sort_values('overall_thriving_index', ascending=False).reset_index(drop=True)
        region_rank = rank[rank['virginia_region_name'] == selected_region_name].index[0] + 1

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Thriving Index", f"{overall_score:.1f}")
        with col2:
            st.metric("Rank", f"{region_rank} of 6")
        with col3:
            vs_peer = overall_score - 100
            st.metric("vs. Peer Average", f"{vs_peer:+.1f}",
                     delta_color="normal" if vs_peer >= 0 else "inverse")

        # Component scores
        st.subheader("Component Scores")

        component_filter = st.selectbox(
            "Filter by component (optional)",
            ["All Components"] + [col.split(':')[1].strip()
                                  for col in components_df.columns
                                  if col.startswith('Component')]
        )

        if component_filter == "All Components":
            filter_val = None
        else:
            # Find full component name
            filter_val = [col for col in components_df.columns
                         if col.startswith('Component') and filter_val in col][0]

        st.plotly_chart(
            create_measure_comparison(detailed_df, selected_region_key, filter_val),
            use_container_width=True
        )

        # Strengths and weaknesses
        col1, col2 = st.columns(2)

        region_measures = detailed_df[
            (detailed_df['virginia_region_key'] == selected_region_key) &
            (detailed_df['measure'] != 'COMPONENT_AVERAGE')
        ].copy()

        with col1:
            st.subheader("Top 5 Strengths")
            top5 = region_measures.nlargest(5, 'score')[['measure', 'score', 'component']]
            for _, row in top5.iterrows():
                st.markdown(f"**{row['measure']}**: {row['score']:.1f}")
                st.caption(row['component'])

        with col2:
            st.subheader("Top 5 Challenges")
            bottom5 = region_measures.nsmallest(5, 'score')[['measure', 'score', 'component']]
            for _, row in bottom5.iterrows():
                st.markdown(f"**{row['measure']}**: {row['score']:.1f}")
                st.caption(row['component'])

    # Regional Map Page
    elif page == "Regional Map":
        st.markdown('<p class="main-header">Regional Comparison Map</p>', unsafe_allow_html=True)

        st.markdown("""
        **Explore Virginia regions and their peer comparison regions on an interactive map.**

        Select a Virginia region using the dropdown below or by clicking on a blue/gray Virginia region on the map.
        The map shows peer regions identified using Mahalanobis distance matching:
        - **Blue**: Selected Virginia region
        - **Orange**: Peer comparison regions (top 8 matches)
        - **Gray**: Other regions

        *Hover over regions for details. Click Virginia regions to select. Use mouse to zoom and pan.*
        """)

        # Load geographic data
        try:
            regions_gdf, states_gdf = load_geographic_data()

            # Get list of VA regions
            va_regions = overall_df[['virginia_region_key', 'virginia_region_name']].drop_duplicates()
            va_region_options = {row['virginia_region_name']: row['virginia_region_key']
                                for _, row in va_regions.iterrows()}

            # Reverse mapping for looking up names from keys
            va_region_names = {v: k for k, v in va_region_options.items()}

            # Initialize session state for selected region if not exists
            if 'selected_va_region' not in st.session_state:
                st.session_state.selected_va_region = list(va_region_options.values())[0]

            # Check for map click event
            if 'regional_map' in st.session_state:
                map_state = st.session_state.regional_map
                # Debug: show what's in the map state
                # st.write("Debug - map_state:", map_state)

                if map_state and isinstance(map_state, dict):
                    selection = map_state.get('selection', {})
                    if selection and 'points' in selection and len(selection['points']) > 0:
                        point = selection['points'][0]
                        # Check if customdata exists and extract region key
                        if 'customdata' in point and point['customdata']:
                            clicked_region_key = point['customdata'][0]
                            # Only update if it's a Virginia region
                            if clicked_region_key in va_region_names:
                                st.session_state.selected_va_region = clicked_region_key
                                # Clear the selection to allow re-clicking
                                st.session_state.regional_map = None

            # Selection dropdown - sync with session state
            current_name = va_region_names.get(st.session_state.selected_va_region, list(va_region_options.keys())[0])
            selected_name = st.selectbox(
                "Select Virginia Region:",
                options=list(va_region_options.keys()),
                index=list(va_region_options.keys()).index(current_name),
                key='region_dropdown'
            )

            # Update session state from dropdown if changed
            if va_region_options[selected_name] != st.session_state.selected_va_region:
                st.session_state.selected_va_region = va_region_options[selected_name]

            selected_va_region = st.session_state.selected_va_region

            # Get peer regions for selected VA region
            peer_rows = peers_df[peers_df['virginia_region_key'] == selected_va_region].copy()
            peer_region_keys = peer_rows['region_key'].tolist()

            # Merge regions with component scores to get overall scores
            # Components are in wide format, so calculate overall score from all component columns
            component_cols = [col for col in components_df.columns if col.startswith('Component')]
            region_scores = components_df[['virginia_region_key'] + component_cols].copy()
            region_scores['overall_score'] = region_scores[component_cols].mean(axis=1)
            region_scores = region_scores[['virginia_region_key', 'overall_score']].rename(
                columns={'virginia_region_key': 'region_key'}
            )

            regions_with_scores = regions_gdf.merge(
                region_scores,
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
                'Other Region': '#e0e0e0'               # Light gray
            }

            # Create figure
            fig = go.Figure()

            # Add regions (colored by category)
            for category in ['Other Region', 'Peer Region', 'Selected Virginia Region']:
                subset = regions_with_scores[regions_with_scores['category'] == category]

                for idx, row in subset.iterrows():
                    # Get region boundary coordinates
                    if row.geometry.geom_type == 'Polygon':
                        coords = list(row.geometry.exterior.coords)
                    else:  # MultiPolygon - use largest polygon
                        geoms = list(row.geometry.geoms)
                        largest = max(geoms, key=lambda g: g.area)
                        coords = list(largest.exterior.coords)

                    lons = [coord[0] for coord in coords]
                    lats = [coord[1] for coord in coords]

                    hover_text = f"<b>{row['region_name']}</b><br>{row['state_name']}"
                    if pd.notna(row['overall_score']):
                        hover_text += f"<br>Score: {row['overall_score']:.1f}"

                    fig.add_trace(go.Scattergeo(
                        lon=lons,
                        lat=lats,
                        mode='lines',
                        fill='toself',
                        fillcolor=color_map[category],
                        line=dict(width=1, color='rgba(0,0,0,0.4)'),  # Thinner, lighter region borders
                        name=category,
                        legendgroup=category,
                        showlegend=bool(idx == subset.index[0]),  # Convert to Python bool
                        text=hover_text,
                        hoverinfo='text',
                        customdata=[[row['region_key']]]  # Store region_key for click events
                    ))

            # Add state boundaries AFTER regions (so they appear on top)
            for idx, row in states_gdf.iterrows():
                # Handle both Polygon and MultiPolygon geometries
                if row.geometry.geom_type == 'Polygon':
                    polygons = [row.geometry]
                else:  # MultiPolygon
                    polygons = list(row.geometry.geoms)

                # Draw boundary for each polygon in the state
                for poly in polygons:
                    coords = list(poly.exterior.coords)
                    lons = [coord[0] for coord in coords]
                    lats = [coord[1] for coord in coords]

                    fig.add_trace(go.Scattergeo(
                        lon=lons,
                        lat=lats,
                        mode='lines',
                        line=dict(width=4, color='rgba(30,30,30,0.8)'),  # Bold, dark state borders
                        showlegend=False,
                        hoverinfo='skip',
                        name=''
                    ))

            # Update layout
            fig.update_layout(
                title=dict(
                    text=f"<b>{selected_name}</b> and Peer Regions",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=18)
                ),
                geo=dict(
                    scope='usa',
                    projection_type='albers usa',
                    showland=True,
                    landcolor='rgb(250, 250, 250)',
                    coastlinecolor='rgb(180, 180, 180)',
                    showlakes=True,
                    lakecolor='rgb(220, 230, 240)',
                    showcountries=True,
                    countrycolor='rgb(150, 150, 150)',
                    showsubunits=True,
                    subunitcolor='rgb(200, 200, 200)',
                    center=dict(lat=37.5, lon=-81),
                    projection_scale=5.5
                ),
                height=750,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(0,0,0,0.3)',
                    borderwidth=1
                )
            )

            st.plotly_chart(fig, use_container_width=True, key='regional_map', on_select='rerun')

            # Comparison table
            st.subheader("Component Score Comparison")

            # Build comparison table
            # Component data is already in wide format
            scores_pivot = components_df.copy()

            # Calculate overall score
            component_cols = [col for col in scores_pivot.columns if col.startswith('Component')]
            scores_pivot['Overall'] = scores_pivot[component_cols].mean(axis=1)

            # Get VA region info
            va_region_info = overall_df[overall_df['virginia_region_key'] == selected_va_region].iloc[0]

            # Build table data
            table_data = []

            # Add VA region
            va_scores = scores_pivot[scores_pivot['virginia_region_key'] == selected_va_region]
            if len(va_scores) > 0:
                va_row = {
                    'Region': va_region_info['virginia_region_name'],
                    'State': 'Virginia',
                    'Type': '🎯 Selected'
                }
                for i, col in enumerate(component_cols, 1):
                    va_row[f'C{i}'] = va_scores.iloc[0][col]
                va_row['Overall'] = va_scores.iloc[0]['Overall']
                table_data.append(va_row)

            # Add peer regions (sorted by rank)
            peer_rows_sorted = peer_rows.sort_values('peer_rank')
            for _, peer in peer_rows_sorted.iterrows():
                peer_scores = scores_pivot[scores_pivot['virginia_region_key'] == peer['region_key']]

                if len(peer_scores) > 0:
                    peer_row = {
                        'Region': peer['region_name'],
                        'State': peer['state_name'],
                        'Type': f"Peer #{int(peer['peer_rank'])}"
                    }
                    for i, col in enumerate(component_cols, 1):
                        peer_row[f'C{i}'] = peer_scores.iloc[0][col]
                    peer_row['Overall'] = peer_scores.iloc[0]['Overall']
                    table_data.append(peer_row)

            if table_data:
                comparison_df = pd.DataFrame(table_data)

                # Format and style the table
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

                # Legend for table
                st.caption("""
                **Table Legend:** C1-C8 represent the 8 component indexes, Overall is the average.
                Color coding: Red (below peer average) → Yellow (at average) → Green (above peer average)
                """)
            else:
                st.warning("No comparison data available for this region.")

        except FileNotFoundError:
            st.error("""
            **Geographic data files not found!**

            Please run the following commands to create region boundary files:
            ```
            python scripts/create_region_boundaries.py
            python scripts/simplify_boundaries.py
            ```
            """)
        except Exception as e:
            st.error(f"Error loading geographic data: {e}")

    # Peer Comparison Page
    elif page == "Peer Comparison":
        st.markdown('<p class="main-header">Peer Region Comparison</p>', unsafe_allow_html=True)

        # Region selector
        region_names = overall_df['virginia_region_name'].tolist()
        selected_region_name = st.selectbox("Select Virginia region", region_names)

        # Get region key
        selected_region_key = overall_df[
            overall_df['virginia_region_name'] == selected_region_name
        ]['virginia_region_key'].values[0]

        # Peer distance chart
        st.plotly_chart(
            create_peer_comparison_chart(peers_df, selected_region_key),
            use_container_width=True
        )

        # Peer details table
        st.subheader("Peer Region Details")

        region_peers = peers_df[peers_df['virginia_region_key'] == selected_region_key]
        region_peers = region_peers.sort_values('peer_rank')

        display_cols = [
            'peer_rank', 'region_name', 'state_name', 'mahalanobis_distance',
            'population', 'micropolitan_pct', 'services_employment_pct',
            'manufacturing_employment_pct', 'mining_employment_pct'
        ]

        st.dataframe(
            region_peers[display_cols].round(2),
            hide_index=True,
            use_container_width=True
        )

    # Data Explorer Page
    elif page == "Data Explorer":
        st.markdown('<p class="main-header">Data Explorer</p>', unsafe_allow_html=True)

        st.markdown("Explore and download the full dataset.")

        # Dataset selector
        dataset = st.selectbox(
            "Select dataset",
            ["Overall Index", "Component Scores", "Detailed Measures", "Peer Regions"]
        )

        if dataset == "Overall Index":
            df = overall_df
        elif dataset == "Component Scores":
            df = components_df
        elif dataset == "Detailed Measures":
            df = detailed_df
        else:
            df = peers_df

        # Display
        st.dataframe(df, use_container_width=True, height=600)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{dataset.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
