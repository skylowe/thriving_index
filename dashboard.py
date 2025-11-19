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
        ["Overview", "Component Analysis", "Regional Deep Dive", "Peer Comparison", "Data Explorer"]
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
