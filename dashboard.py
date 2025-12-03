"""
Virginia Rural Thriving Index - Interactive Dashboard

A Streamlit dashboard for exploring thriving index scores across 6 Virginia rural regions.
Now includes advanced Research Lab capabilities for deep dive analysis.
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
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card-red {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .metric-delta {
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .highlight-green {
        color: #28a745;
        font-weight: bold;
    }
    .highlight-red {
        color: #dc3545;
        font-weight: bold;
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .score-badge-green {
        background-color: #d4edda;
        color: #155724;
    }
    .score-badge-yellow {
        background-color: #fff3cd;
        color: #856404;
    }
    .score-badge-red {
        background-color: #f8d7da;
        color: #721c24;
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
def load_regional_raw_data():
    """Load the raw values for all 47 measures across 94 regions."""
    files = [
        'data/regional/component1_growth_index_regional.csv',
        'data/regional/component2_economic_opportunity_regional.csv',
        'data/regional/component3_other_prosperity_regional.csv',
        'data/regional/component4_demographic_growth_regional.csv',
        'data/regional/component5_education_skill_regional.csv',
        'data/regional/component6_infrastructure_cost_regional.csv',
        'data/regional/component7_quality_of_life_regional.csv',
        'data/regional/component8_social_capital_regional.csv'
    ]
    
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            # Filter columns to avoid duplication when merging
            cols_to_keep = ['region_key'] + [c for c in df.columns if c not in ['region_name', 'state_name', 'region_key']]
            dfs.append(df)
        except Exception as e:
            st.error(f"Failed to load {f}: {e}")
            
    if not dfs:
        return None
        
    full_raw = dfs[0]
    for df in dfs[1:]:
        # Only merge new columns, keeping region_key as the join key
        cols = ['region_key'] + [c for c in df.columns if c not in full_raw.columns and c != 'region_key']
        if len(cols) > 1: # If there are new columns besides region_key
             full_raw = full_raw.merge(df[cols], on='region_key', how='left')
        
    return full_raw


@st.cache_data
def load_geographic_data():
    """Load simplified region and state boundary GeoJSON files."""
    regions_gdf = gpd.read_file('data/geojson/region_boundaries_simplified.geojson')
    states_gdf = gpd.read_file('data/geojson/state_boundaries.geojson')

    return regions_gdf, states_gdf

# --- VISUALIZATION FUNCTIONS ---

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


def score_to_color(score, selected=False, is_peer=False):
    """Convert a score to a color using RdYlGn colorscale."""
    if pd.isna(score):
        return 'rgba(200, 200, 200, 0.6)'

    # Normalize score: 50-150 range mapped to 0-1
    normalized = max(0, min(1, (score - 50) / 100))

    # RdYlGn colorscale interpolation
    if normalized < 0.5:
        # Red to Yellow
        r = 215 + int((255 - 215) * (normalized * 2))
        g = 48 + int((255 - 48) * (normalized * 2))
        b = 39 + int((0 - 39) * (normalized * 2))
    else:
        # Yellow to Green
        r = 255 - int((255 - 39) * ((normalized - 0.5) * 2))
        g = 255 - int((255 - 174) * ((normalized - 0.5) * 2))
        b = 0 + int((96 - 0) * ((normalized - 0.5) * 2))

    # Adjust opacity and brightness based on selection
    if selected:
        return f'rgba({r}, {g}, {b}, 1.0)'
    elif is_peer:
        return f'rgba({r}, {g}, {b}, 0.85)'
    else:
        return f'rgba({r}, {g}, {b}, 0.5)'


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

def create_correlation_matrix(df, cols):
    """Create a correlation matrix heatmap."""
    corr = df[cols].corr()
    
    fig = px.imshow(
        corr,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        title="Correlation Matrix"
    )
    return fig

def create_distribution_plot(df, measure_col, highlight_region_key=None):
    """Create a violin/box plot with swarm strip to show distribution."""
    fig = go.Figure()
    
    # Violin for distribution
    fig.add_trace(go.Violin(
        y=df[measure_col],
        box_visible=True,
        line_color='black',
        meanline_visible=True,
        fillcolor='lightseagreen',
        opacity=0.6,
        x0=measure_col,
        name="Distribution"
    ))
    
    # Strip plot for individual regions
    fig.add_trace(go.Box(
        y=df[measure_col],
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        fillcolor='rgba(0,0,0,0)',
        line=dict(color='rgba(0,0,0,0)'),
        marker=dict(color='darkblue', opacity=0.5, size=6),
        name="Regions",
        # Using region_key as we might not have name for all
        hovertext=df['region_key'], 
    ))

    # Highlight specific region
    if highlight_region_key:
        row = df[df['region_key'] == highlight_region_key]
        if not row.empty:
            val = row[measure_col].values[0]
            fig.add_trace(go.Scatter(
                x=[measure_col],
                y=[val],
                mode='markers',
                marker=dict(color='red', size=15, symbol='star'),
                name="Selected Region"
            ))

    fig.update_layout(
        title=f"Distribution of {measure_col}",
        showlegend=False,
        height=500
    )
    return fig

def create_scatter_explorer(df, x_col, y_col, color_col=None, hover_name=None):
    """Interactive scatter plot."""
    fig = px.scatter(
        df, x=x_col, y=y_col,
        color=color_col,
        hover_name=hover_name,
        trendline="ols",
        title=f"{y_col} vs {x_col}",
        height=600
    )
    return fig


# Main app
def main():
    # Load data
    overall_df, components_df, detailed_df, peers_df = load_data()
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Standard Views
    st.sidebar.header("Standard Views")
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Component Analysis", "Regional Deep Dive", "Regional Map", "Peer Comparison", "Data Explorer", "Research Lab"]
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

        # Key metrics with styled cards
        col1, col2, col3, col4 = st.columns(4)

        above_avg = (overall_df['overall_thriving_index'] >= 100).sum()
        top_region = overall_df.loc[overall_df['overall_thriving_index'].idxmax()]
        top_score = top_region['overall_thriving_index']
        top_name = top_region['virginia_region_name']
        avg_score = overall_df['overall_thriving_index'].mean()
        lowest_region = overall_df.loc[overall_df['overall_thriving_index'].idxmin()]
        lowest_score = lowest_region['overall_thriving_index']

        with col1:
            card_class = "metric-card-green" if above_avg >= 3 else "metric-card-red"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="metric-label">Regions Above Peer Average</div>
                <div class="metric-value">{above_avg} of 6</div>
                <div class="metric-delta">{"✓ Majority thriving" if above_avg >= 3 else "⚠ Below majority"}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card-green">
                <div class="metric-label">Highest Score</div>
                <div class="metric-value">{top_score:.1f}</div>
                <div class="metric-delta">🏆 {top_name.split()[0]}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            card_class = "metric-card-green" if avg_score >= 100 else "metric-card-red"
            delta_text = f"↑ {avg_score - 100:.1f} above avg" if avg_score >= 100 else f"↓ {100 - avg_score:.1f} below avg"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="metric-label">Average Score</div>
                <div class="metric-value">{avg_score:.1f}</div>
                <div class="metric-delta">{delta_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card-blue">
                <div class="metric-label">Lowest Score</div>
                <div class="metric-value">{lowest_score:.1f}</div>
                <div class="metric-delta">📍 {lowest_region['virginia_region_name'].split()[0]}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

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

        Select a Virginia region from the dropdown. Regions are colored by their Thriving Index score:
        - 🟢 **Green** = High scores (above peer average)
        - 🟡 **Yellow** = Average scores (near peer average)
        - 🔴 **Red** = Low scores (below peer average)
        - **Bold outline** = Selected region and its peer matches

        *Hover over regions for details. Use mouse to zoom and pan.*
        """)

        # Load geographic data
        try:
            regions_gdf, states_gdf = load_geographic_data()

            # Get list of VA regions
            va_regions = overall_df[['virginia_region_key', 'virginia_region_name']].drop_duplicates()
            va_region_options = {row['virginia_region_name']: row['virginia_region_key']
                                for _, row in va_regions.iterrows()}

            # Selection dropdown
            selected_name = st.selectbox(
                "Select Virginia Region:",
                options=list(va_region_options.keys()),
                index=0
            )
            selected_va_region = va_region_options[selected_name]

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

            # Create figure
            fig = go.Figure()

            # Add regions colored by score
            # First add non-selected/non-peer regions (lower opacity)
            for idx, row in regions_with_scores.iterrows():
                is_selected = row['region_key'] == selected_va_region
                is_peer = row['region_key'] in peer_region_keys

                # Get region boundary coordinates
                if row.geometry.geom_type == 'Polygon':
                    coords = list(row.geometry.exterior.coords)
                else:  # MultiPolygon - use largest polygon
                    geoms = list(row.geometry.geoms)
                    largest = max(geoms, key=lambda g: g.area)
                    coords = list(largest.exterior.coords)

                lons = [coord[0] for coord in coords]
                lats = [coord[1] for coord in coords]

                # Get score-based color
                fill_color = score_to_color(row['overall_score'], selected=is_selected, is_peer=is_peer)

                # Bold outline for selected and peer regions
                if is_selected:
                    line_width = 3
                    line_color = 'rgba(0, 0, 150, 0.9)'
                elif is_peer:
                    line_width = 2
                    line_color = 'rgba(0, 0, 100, 0.7)'
                else:
                    line_width = 0.5
                    line_color = 'rgba(0, 0, 0, 0.3)'

                hover_text = f"<b>{row['region_name']}</b><br>{row['state_name']}"
                if pd.notna(row['overall_score']):
                    hover_text += f"<br>Score: {row['overall_score']:.1f}"
                if is_selected:
                    hover_text += "<br><b>(Selected)</b>"
                elif is_peer:
                    hover_text += "<br><i>(Peer Region)</i>"

                fig.add_trace(go.Scattergeo(
                    lon=lons,
                    lat=lats,
                    mode='lines',
                    fill='toself',
                    fillcolor=fill_color,
                    line=dict(width=line_width, color=line_color),
                    showlegend=False,
                    text=hover_text,
                    hoverinfo='text'
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
                        line=dict(width=2.5, color='rgba(30,30,30,0.85)'),
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
                    center=dict(lat=36, lon=-82),
                    projection_scale=2.8  # Zoomed out to see all states
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
                ),
                uirevision='constant'  # Preserve zoom/pan when switching regions
            )

            st.plotly_chart(fig, use_container_width=True, key='regional_map')

            # Radar chart and comparison table
            st.subheader("Component Score Analysis")

            # Create columns for radar chart and key metrics
            radar_col, metrics_col = st.columns([1, 1])

            with radar_col:
                # Create radar chart for selected region vs peer average
                component_cols = [col for col in components_df.columns if col.startswith('Component')]
                component_names = [col.split(':')[1].strip() for col in component_cols]

                # Get selected region scores
                va_scores_row = components_df[components_df['virginia_region_key'] == selected_va_region]
                if len(va_scores_row) > 0:
                    va_values = [va_scores_row.iloc[0][col] for col in component_cols]

                    # Get peer average scores
                    peer_data = components_df[components_df['virginia_region_key'].isin(peer_region_keys)]
                    peer_avg = [peer_data[col].mean() for col in component_cols]

                    radar_fig = go.Figure()

                    # Add peer average
                    radar_fig.add_trace(go.Scatterpolar(
                        r=peer_avg + [peer_avg[0]],
                        theta=component_names + [component_names[0]],
                        fill='toself',
                        fillcolor='rgba(255, 127, 14, 0.2)',
                        line=dict(color='#ff7f0e', width=2),
                        name='Peer Average'
                    ))

                    # Add selected region
                    radar_fig.add_trace(go.Scatterpolar(
                        r=va_values + [va_values[0]],
                        theta=component_names + [component_names[0]],
                        fill='toself',
                        fillcolor='rgba(31, 119, 180, 0.3)',
                        line=dict(color='#1f77b4', width=3),
                        name=selected_name
                    ))

                    # Add reference line at 100
                    radar_fig.add_trace(go.Scatterpolar(
                        r=[100] * (len(component_names) + 1),
                        theta=component_names + [component_names[0]],
                        mode='lines',
                        line=dict(color='gray', width=1, dash='dash'),
                        name='Peer Benchmark (100)'
                    ))

                    radar_fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, max(max(va_values), max(peer_avg)) * 1.1])
                        ),
                        showlegend=True,
                        legend=dict(orientation='h', yanchor='bottom', y=-0.2),
                        height=400,
                        margin=dict(t=30, b=80)
                    )

                    st.plotly_chart(radar_fig, use_container_width=True)

            with metrics_col:
                # Show key metrics for the selected region
                if len(va_scores_row) > 0:
                    st.markdown(f"### {selected_name}")

                    # Calculate metrics
                    overall_score = sum(va_values) / len(va_values)
                    above_peer = sum(1 for v in va_values if v >= 100)
                    strongest = component_names[va_values.index(max(va_values))]
                    weakest = component_names[va_values.index(min(va_values))]

                    # Display styled metrics
                    score_color = "metric-card-green" if overall_score >= 100 else "metric-card-red"
                    st.markdown(f"""
                    <div class="{score_color}" style="margin-bottom: 1rem;">
                        <div class="metric-label">Overall Thriving Score</div>
                        <div class="metric-value">{overall_score:.1f}</div>
                        <div class="metric-delta">{above_peer} of 8 components above peer average</div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"""
                        <div class="metric-card-green" style="padding: 1rem;">
                            <div class="metric-label">💪 Strongest</div>
                            <div style="font-size: 1.1rem; font-weight: bold;">{strongest}</div>
                            <div style="font-size: 1.5rem;">{max(va_values):.1f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"""
                        <div class="metric-card-red" style="padding: 1rem;">
                            <div class="metric-label">🎯 Area for Growth</div>
                            <div style="font-size: 1.1rem; font-weight: bold;">{weakest}</div>
                            <div style="font-size: 1.5rem;">{min(va_values):.1f}</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Detailed Peer Comparison")

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
        
    # Research Lab (Combined Researcher Features)
    elif page == "Research Lab":
        st.markdown('<p class="main-header">Research & Analytics Lab</p>', unsafe_allow_html=True)
        st.info("🔬 Advanced analytics for researchers: Explore distributions, correlations, and methodology.")
        
        # Load extra raw data needed for research
        raw_data = load_regional_raw_data()
        
        if raw_data is None:
            st.error("Could not load regional raw data files. Please ensure `data/regional/*.csv` files exist.")
            st.stop()
            
        # Merge scores for correlation analysis
        master_df = overall_df.merge(components_df, on=['virginia_region_key', 'virginia_region_name'])
        
        # Tabs for different research modules
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Measure Explorer", "🔗 Correlations", "🧪 Peer Lab", "🗺️ Spatial Analysis"])
        
        with tab1:
            st.subheader("Deep Dive: Measure Explorer")
            st.markdown("Explore the raw values (not scores) across all 94 regions to understand distributions and identify outliers.")
            
            # Drop non-numeric cols for selection
            numeric_cols = raw_data.select_dtypes(include=np.number).columns.tolist()
            # Filter out IDs
            exclude = ['fips', 'code', 'id']
            numeric_cols = [c for c in numeric_cols if not any(ex in c.lower() for ex in exclude)]
            
            col1, col2 = st.columns([1, 3])
            with col1:
                selected_measure = st.selectbox("Select Measure:", numeric_cols, index=0)
                
                # Optional: Highlight a region. Need name mapping from raw data if possible
                # Raw data has region_name? Let's check columns or fallback to key
                region_opts = raw_data['region_key'].unique()
                if 'region_name' in raw_data.columns:
                     region_opts = raw_data['region_name'].unique()
                
                highlight_region = st.selectbox("Highlight Region:", region_opts)
                
                # Get key for highlighting
                if 'region_name' in raw_data.columns:
                    highlight_key = raw_data[raw_data['region_name'] == highlight_region]['region_key'].values[0]
                else:
                    highlight_key = highlight_region
                
            with col2:
                # Statistics
                desc = raw_data[selected_measure].describe()
                st.write(desc.to_frame().T)
                
                # Distribution Plot
                st.plotly_chart(create_distribution_plot(raw_data, selected_measure, highlight_key), use_container_width=True)
                
            # Top/Bottom lists
            c1, c2 = st.columns(2)
            cols_to_show = ['region_key', selected_measure]
            if 'region_name' in raw_data.columns: cols_to_show.insert(1, 'region_name')
            if 'state_name' in raw_data.columns: cols_to_show.insert(2, 'state_name')
                
            with c1:
                st.markdown("**Top 10 Regions**")
                st.dataframe(raw_data[cols_to_show].nlargest(10, selected_measure), hide_index=True)
            with c2:
                st.markdown("**Bottom 10 Regions**")
                st.dataframe(raw_data[cols_to_show].nsmallest(10, selected_measure), hide_index=True)

        with tab2:
            st.subheader("Correlation Analysis")
            st.markdown("Identify relationships between different components or raw measures.")
            
            mode = st.radio("Level of Analysis:", ["Component Scores", "Raw Measures"])
            
            if mode == "Component Scores":
                cols = [c for c in master_df.columns if "Component" in c]
                df_corr = master_df
            else:
                cols = numeric_cols # From tab 1
                df_corr = raw_data
                
            selected_corr_vars = st.multiselect("Select Variables to Correlate:", cols, default=cols[:5])
            
            if len(selected_corr_vars) > 1:
                st.plotly_chart(create_correlation_matrix(df_corr, selected_corr_vars), use_container_width=True)
                
                # Scatter driller
                st.markdown("#### Bivariate Analysis")
                sc1, sc2 = st.columns(2)
                x_axis = sc1.selectbox("X Axis", selected_corr_vars, index=0)
                y_axis = sc2.selectbox("Y Axis", selected_corr_vars, index=1)
                
                hover = 'region_name' if 'region_name' in df_corr.columns else 'region_key'
                st.plotly_chart(create_scatter_explorer(df_corr, x_axis, y_axis, hover_name=hover), use_container_width=True)
            else:
                st.warning("Please select at least 2 variables.")

        with tab3:
            st.subheader("Peer Matching Methodology Lab")
            st.markdown("Visualizing the 7-dimensional space used to select peer regions.")
            
            try:
                # Load matching variables
                match_vars = pd.read_csv('data/peer_matching_variables.csv')
                
                # Get VA regions available in the matching file
                va_regions = [r for r in match_vars['region_name'].unique() 
                             if "Virginia" in str(match_vars[match_vars['region_name']==r]['state_name'].values)]
                
                target_region_name = st.selectbox("Select Target Virginia Region:", va_regions)
                target_row = match_vars[match_vars['region_name'] == target_region_name].iloc[0]
                target_key = target_row['region_key']
                
                # Get peers for this target from the loaded peers_df
                my_peers = peers_df[peers_df['virginia_region_key'] == target_key]['region_key'].tolist()
                
                # Create a column in match_vars for color coding
                def get_status(row):
                    if row['region_key'] == target_key:
                        return "Target"
                    elif row['region_key'] in my_peers:
                        return "Selected Peer"
                    else:
                        return "Other Region"
                
                match_vars['Status'] = match_vars.apply(get_status, axis=1)
                
                # Select dimensions
                dims = [c for c in match_vars.columns if c not in ['region_key', 'region_name', 'state_name', 'Status']]
                
                c1, c2 = st.columns(2)
                x_dim = c1.selectbox("X Dimension (Matching Variable)", dims, index=0)
                y_dim = c2.selectbox("Y Dimension (Matching Variable)", dims, index=1)
                
                fig = px.scatter(
                    match_vars, 
                    x=x_dim, 
                    y=y_dim, 
                    color='Status',
                    color_discrete_map={"Target": "red", "Selected Peer": "blue", "Other Region": "lightgray"},
                    hover_name='region_name',
                    size='Status',
                    size_max=15, 
                    category_orders={"Status": ["Target", "Selected Peer", "Other Region"]}
                )
                fig.update_traces(marker=dict(opacity=0.7))
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### Peer Data Table")
                st.dataframe(match_vars[match_vars['Status'] != "Other Region"].sort_values('Status', ascending=False), hide_index=True)
                
            except Exception as e:
                st.error(f"Could not load peer matching data: {e}")

        with tab4:
            st.subheader("Spatial Analysis (Raw Data)")
            st.markdown("Map any raw variable across all 94 regions.")
            try:
                gdf, _ = load_geographic_data()
                # Merge with raw data
                gdf_data = gdf.merge(raw_data, on='region_key')
                
                map_var = st.selectbox("Select Variable to Map:", numeric_cols, key='map_var')
                
                fig = px.choropleth(
                    gdf_data,
                    geojson=gdf_data.geometry,
                    locations=gdf_data.index,
                    color=map_var,
                    hover_name='region_name' if 'region_name' in gdf_data.columns else 'region_key',
                    projection="mercator", 
                )
                fig.update_geos(fitbounds="locations", visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.warning(f"Could not load spatial tools: {e}")


if __name__ == "__main__":
    main()