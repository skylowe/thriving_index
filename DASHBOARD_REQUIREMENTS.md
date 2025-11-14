# Virginia Thriving Index - Dashboard Requirements

**Date**: 2025-11-14
**Status**: Requirements Definition
**Technology**: Plotly Dash (Python-based)

---

## Executive Summary

This document defines the requirements for an interactive web dashboard displaying the Virginia Thriving Index and comparison regions across surrounding states (MD, WV, NC, TN, KY, DC). The dashboard will feature interactive maps, comparative charts, and detailed regional profiles.

**Primary Focus**: Virginia regions compared against similar regions in surrounding states
**Geographic Scope**: Virginia + MD, WV, NC, TN, KY, DC
**Methodology**: 8 component indexes based on 30+ individual measures

---

## User Requirements (from User)

From user specification:
1. **Interactive Map**: Display index scores across all regions and states
2. **Comparison Charts**: Allow users to see how regions compare within and across states
3. **Virginia Focus**: Virginia is the focal point of the analysis
4. **Cross-State Comparison**: Ability to compare similar regions across state boundaries

---

## Functional Requirements

### 1. Interactive Regional Map

**Primary View**: Multi-state choropleth map

**Features**:
- **Geographic Coverage**: Display all regions in VA, MD, WV, NC, TN, KY, and DC
- **Color Coding**: Color regions by Thriving Index score (or component indexes)
- **Interactivity**:
  - Hover: Display region name and index score
  - Click: Navigate to detailed regional profile
  - Zoom/Pan: Allow exploration of specific areas
- **Layer Selection**:
  - Overall Thriving Index (default)
  - Individual Component Indexes (8 options)
  - Individual Measures (30+ options)
- **State Highlighting**: Option to highlight Virginia regions
- **Comparison View**: Highlight peer regions for selected Virginia region

**Technical Approach**:
- Plotly Choropleth (mapbox or geo)
- GeoJSON boundaries for Planning District Commissions (Virginia) and counties (other states)
- Color scale: Diverging or sequential (e.g., RdYlGn, Viridis)
- Legend: Clear explanation of score ranges

**Map Layers**:
1. Base geography (state/region boundaries)
2. Index score coloring
3. Peer region highlighting (optional)
4. Virginia emphasis (optional border/hatching)

### 2. Regional Comparison Charts

**Purpose**: Allow users to compare regions within and across states

**Chart Types**:

#### 2.1 Peer Region Comparison (Primary Chart)
- **Type**: Horizontal bar chart or radar chart
- **X-axis**: Index score (0-200, centered at 100)
- **Y-axis**: Region names
- **Features**:
  - Show selected Virginia region vs its 10 peer regions
  - Color-code bars by state
  - Highlight Virginia region
  - Sort by index score (default) or state
  - Toggle between Overall Index and Component Indexes

#### 2.2 Component Index Breakdown
- **Type**: Grouped bar chart or spider/radar chart
- **Purpose**: Show all 8 component indexes for selected regions
- **Features**:
  - Compare selected region against peer average, state average, national average
  - Color-coded by component
  - Reference line at 100 (average)

#### 2.3 Measure-Level Detail
- **Type**: Grouped bar chart or dot plot
- **Purpose**: Show individual measures within a component
- **Features**:
  - Drill-down from component to constituent measures
  - Display raw values and standardized scores
  - Show peer region range (min/max) for context

#### 2.4 Cross-State Comparison Matrix
- **Type**: Heatmap
- **Purpose**: Compare all Virginia regions across component indexes
- **Features**:
  - Rows: Virginia regions (8-21 depending on consolidation)
  - Columns: 8 component indexes
  - Cell color: Index score
  - Click cell: Navigate to detailed view

### 3. Regional Profile Page

**Purpose**: Detailed information for a single region

**Components**:

#### 3.1 Header
- Region name
- State
- Overall Thriving Index score (prominent)
- Ranking among Virginia regions (if Virginia)
- Quick stats: Population, area, major localities

#### 3.2 Peer Regions
- List of 10 peer regions with scores
- Map showing geographic distribution of peer regions
- Rationale: Display matching variables used for peer selection
  - Total population
  - % in micropolitan area
  - % farm income
  - % manufacturing employment
  - Distance to small MSA
  - Distance to large MSA

#### 3.3 Component Index Scores
- Table or card layout showing 8 component indexes
- Score, rank among peers, visual indicator (above/below average)

#### 3.4 Measure Details
- Expandable/collapsible sections for each component
- Table showing:
  - Measure name
  - Raw value
  - Standardized index score
  - Peer average
  - State average (if applicable)
  - Percentile rank

#### 3.5 Trends (Future Enhancement)
- Historical data showing change over time
- Growth trajectories for key measures

### 4. Filters and Controls

**Global Controls** (apply to entire dashboard):
- **Index Selection**: Overall Thriving Index vs Component Indexes (dropdown)
- **Region Selection**: Multi-select for regions to compare
- **State Filter**: Show all states, or filter to specific states
- **Virginia Focus Toggle**: Highlight Virginia regions on map

**Chart-Specific Controls**:
- Sort order (by score, alphabetically, by state)
- Number of regions to display (top 10, 20, all)
- Peer comparison vs state comparison vs all regions

### 5. Data Export

**Features**:
- Export current view as PNG/SVG (maps and charts)
- Export data tables as CSV
- Export full regional profile as PDF (future)

**Data to Export**:
- Selected region data
- Peer region comparisons
- Full index scores and raw measures

---

## Non-Functional Requirements

### Performance
- **Load Time**: Initial page load < 3 seconds
- **Interaction Response**: Map/chart interactions < 500ms
- **Data Volume**: Support 600+ regions (VA + peer states) without performance degradation

### Usability
- **Responsive Design**: Work on desktop, tablet (mobile optional)
- **Accessibility**: WCAG 2.1 Level AA compliance (color contrast, keyboard navigation, screen reader support)
- **Browser Support**: Chrome, Firefox, Safari, Edge (latest 2 versions)

### Reliability
- **Uptime**: 99% availability (if hosted)
- **Error Handling**: Graceful degradation if data missing
- **Data Freshness**: Clear indication of data vintage (e.g., "Data as of 2022")

---

## Technical Architecture

### Technology Stack

**Framework**: Plotly Dash
- Reason: Python-native, excellent charting, good for data applications
- Alternative considered: Streamlit (faster development but less customization)

**Components**:
- **Dash Core Components**: Interactive charts (dcc.Graph)
- **Dash HTML Components**: Layout structure
- **Dash Bootstrap Components**: Styling and responsive layout
- **Plotly**: Charts and maps
- **Pandas**: Data manipulation

**Mapping Library**:
- Plotly Choropleth Maps (primary)
- Alternative: Folium (if more advanced mapping needed)

**Styling**:
- Dash Bootstrap Components (bootstrap theme)
- Custom CSS for branding
- Color palette: Accessible, colorblind-friendly

### Data Flow

```
Raw API Data → Processing/Scoring → Data Files (CSV/JSON) → Dashboard
                                            ↓
                                    Cache/Database (optional)
                                            ↓
                                     Dash Application
```

**Data Storage**:
- Option 1: Pre-processed CSV/JSON files loaded at startup
- Option 2: SQLite database for larger datasets
- Option 3: PostgreSQL for production deployment

**Caching**:
- Use Dash caching (@cache.memoize) for expensive calculations
- Pre-compute index scores; don't recalculate on each interaction

### Application Structure

```
dashboard/
  app.py                    # Main Dash application
  layouts/
    home_layout.py          # Landing page
    map_layout.py           # Interactive map view
    comparison_layout.py    # Comparison charts
    profile_layout.py       # Regional profile
  callbacks/
    map_callbacks.py        # Map interactivity
    chart_callbacks.py      # Chart updates
    filter_callbacks.py     # Filter logic
  components/
    map_component.py        # Reusable map component
    chart_components.py     # Reusable chart components
    filters.py              # Filter UI components
  data/
    regions.json            # Region metadata
    index_scores.csv        # Pre-calculated index scores
    peer_matches.json       # Peer region mappings
    boundaries.geojson      # Geographic boundaries
  assets/
    custom.css              # Custom styling
    logo.png                # Branding assets
  utils/
    data_loader.py          # Data loading utilities
    formatting.py           # Number/text formatting
```

---

## User Interface Design

### Navigation Structure

**Primary Navigation** (top bar):
- Home / Overview
- Interactive Map
- Comparison Tool
- Regional Profiles
- About / Methodology

**Secondary Navigation**:
- Index selector (dropdown)
- Filters panel (collapsible sidebar)

### Page Layouts

#### Home Page
- Welcome text
- Key findings summary
- Quick links to:
  - View Virginia regions on map
  - Compare specific regions
  - Learn about methodology

#### Map Page
- Full-screen map (80% of viewport)
- Sidebar with:
  - Layer selection
  - Legend
  - Selected region info
- Footer with data source/vintage

#### Comparison Page
- Region selector (multi-select dropdown)
- Chart type selector (tabs or dropdown)
- Main chart area
- Data table below chart
- Export button

#### Profile Page
- Breadcrumb navigation (Home > Region Name)
- Profile sections (as described in §3)
- Sticky sidebar with section navigation

---

## Specific Visualizations

### 1. Overall Thriving Index Map

**Visualization Type**: Choropleth map

**Design**:
- **Color Scale**:
  - Sequential: Higher score = darker green
  - Diverging: Below 100 = red, 100 = white, above 100 = green
  - Recommended: RdYlGn (red-yellow-green) diverging scale
- **Score Ranges**:
  - < 80: Dark red
  - 80-90: Light red
  - 90-110: Yellow (near average)
  - 110-120: Light green
  - > 120: Dark green
- **Virginia Emphasis**: Thicker borders or subtle hatching for Virginia regions

**Interactivity**:
- Hover: Tooltip showing region name, state, overall score, rank
- Click: Navigate to regional profile or open summary panel
- Selection: Highlight clicked region and its peers

### 2. Peer Region Bar Chart

**Visualization Type**: Horizontal bar chart

**Design**:
- **Bars**:
  - Length = index score
  - Reference line at 100 (average)
  - Color by state (discrete color palette)
  - Virginia region highlighted with border or different opacity
- **Sorting**: Default by score (highest to lowest)
- **Labels**: Region name on y-axis, score value on bar end

**Example**:
```
Northern Virginia PDC     ████████████████ 145  (VA)
Montgomery County         ███████████████  140  (MD)
Howard County             ██████████████   135  (MD)
Research Triangle         █████████████    130  (NC)
...
Central Appalachia PDC    ██████           85   (VA)
```

### 3. Component Index Radar Chart

**Visualization Type**: Radar/spider chart

**Design**:
- **Axes**: 8 component indexes (radial)
- **Scale**: 0-200 with 100 at middle
- **Lines**:
  - Selected region (solid, thick)
  - Peer average (dashed)
  - State average (dotted)
  - Virginia average (if comparing non-VA region)
- **Fill**: Semi-transparent fill for selected region

**Components** (8 axes):
1. Growth
2. Economic Opportunity & Diversity
3. Other Economic Prosperity (if included)
4. Demographic Growth & Renewal
5. Education & Skill
6. Infrastructure & Cost
7. Quality of Life
8. Social Capital

### 4. Cross-State Heatmap

**Visualization Type**: Heatmap matrix

**Design**:
- **Rows**: Virginia regions (8-21)
- **Columns**: 8 component indexes + Overall
- **Cells**: Color by index score (diverging scale)
- **Annotations**: Display score value in cell
- **Interactivity**: Click cell to see measure details

### 5. Measure Detail Comparison

**Visualization Type**: Dot plot with error bars

**Design**:
- **Y-axis**: Measure names
- **X-axis**: Standardized index score (0-200)
- **Dots**:
  - Selected region (large, colored)
  - Peer average (medium, grey)
  - Peer range (error bars showing min/max)
- **Reference line**: 100 (vertical line)

---

## Data Requirements for Dashboard

### Pre-Computed Data Files

1. **regions.json**: Region metadata
```json
{
  "region_id": "VA_NorthernVirginia",
  "region_name": "Northern Virginia PDC",
  "state": "VA",
  "counties": ["Arlington", "Fairfax", "Loudoun", ...],
  "population": 2500000,
  "area_sq_mi": 1000,
  "centroid_lat": 38.88,
  "centroid_lon": -77.11
}
```

2. **index_scores.csv**: All index scores
```csv
region_id,overall_index,growth_index,economic_opp_index,...,measure_1,measure_2,...
VA_NorthernVirginia,145,155,140,...,120,135,...
MD_MontgomeryCounty,140,150,138,...,118,132,...
```

3. **peer_matches.json**: Peer region relationships
```json
{
  "VA_NorthernVirginia": {
    "peers": ["MD_MontgomeryCounty", "MD_HowardCounty", ...],
    "matching_variables": {
      "population": 2500000,
      "pct_micropolitan": 0,
      "pct_farm_income": 0.001,
      "pct_manufacturing": 0.05,
      "dist_small_msa": 10,
      "dist_large_msa": 0
    },
    "distances": [0.5, 0.7, 0.9, ...]
  }
}
```

4. **boundaries.geojson**: Geographic boundaries
```geojson
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "VA_NorthernVirginia",
      "properties": {"name": "Northern Virginia PDC", "state": "VA"},
      "geometry": {"type": "Polygon", "coordinates": [...]}
    }
  ]
}
```

5. **measure_metadata.json**: Measure definitions
```json
{
  "measure_id": "population_growth",
  "measure_name": "Population Growth Rate (5-year)",
  "component": "Growth",
  "inverse": false,
  "units": "% annual",
  "description": "Annualized population growth over 5 years",
  "data_source": "Census Population Estimates"
}
```

---

## Implementation Phases

### Phase 1: Core Functionality (MVP)
- Overall Thriving Index map
- Basic region comparison chart
- Simple regional profile
- Virginia-only regions initially

**Deliverables**:
- Interactive map with Virginia regions
- Bar chart comparing Virginia regions
- Basic filters (index selection)

### Phase 2: Enhanced Interactivity
- Add peer regions from surrounding states
- Peer region comparison charts
- Component index drill-down
- Improved filters and controls

**Deliverables**:
- Multi-state map
- Peer region bar charts
- Component index radar charts
- Enhanced regional profiles

### Phase 3: Advanced Features
- Cross-state heatmap
- Measure-level detail views
- Data export functionality
- Advanced filtering

**Deliverables**:
- All visualization types complete
- Full export capabilities
- Polished UI/UX

### Phase 4: Polish & Deployment
- Performance optimization
- Accessibility improvements
- Responsive design
- Production deployment

**Deliverables**:
- Production-ready application
- Documentation
- User guide

---

## Key Metrics / Success Criteria

**Functionality**:
- ✅ Users can view Virginia regions on interactive map
- ✅ Users can compare regions within and across states
- ✅ Users can drill down from overall index to individual measures
- ✅ Users can identify peer regions for any Virginia region

**Performance**:
- ✅ Page load < 3 seconds
- ✅ Map interactions < 500ms
- ✅ Support 600+ regions without lag

**Usability**:
- ✅ Intuitive navigation (user testing)
- ✅ Clear visual hierarchy
- ✅ Accessible to screen readers
- ✅ Mobile-friendly (responsive)

---

## Open Questions

1. **Region Consolidation**: Use all 21 Virginia PDCs or consolidate to 8-12 regions?
   - Decision: To be determined based on data analysis

2. **Hosting**: Local/internal vs public web hosting?
   - Affects deployment strategy and security requirements

3. **Update Frequency**: How often will data be refreshed?
   - Annual? On-demand? Affects caching strategy

4. **Branding**: Official Virginia state branding or neutral design?
   - Color scheme, logo, styling

5. **User Authentication**: Public access or restricted?
   - May require login system if restricted

---

## References

- Plotly Dash: https://dash.plotly.com/
- Plotly Choropleth Maps: https://plotly.com/python/choropleth-maps/
- Dash Bootstrap Components: https://dash-bootstrap-components.opensource.faculty.ai/
- Nebraska Thriving Index Dashboard (reference): Review for design inspiration

---

*This document will be updated as requirements are refined and implementation progresses.*
