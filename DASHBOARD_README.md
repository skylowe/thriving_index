# Virginia Rural Thriving Index - Interactive Dashboard

An interactive Streamlit dashboard for exploring thriving index scores across 6 Virginia rural regions.

## Quick Start

### Windows
```bash
run_dashboard.bat
```

### Linux/Mac
```bash
./run_dashboard.sh
```

Or manually:
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## Dashboard Features

### 1. Overview Page
- **Overall Rankings**: Interactive bar chart showing all 6 regions ranked by Thriving Index score
- **Key Metrics**: Summary statistics (regions above average, highest score, etc.)
- **Component Heatmap**: Visual comparison of all 8 components across all regions
- **Top Performers**: List of highest-scoring regions for each component

### 2. Component Analysis
- **Radar Chart**: Compare multiple regions across all 8 components
- **Region Selector**: Choose specific regions to compare or view all
- **Component Scores Table**: Detailed numeric breakdown

### 3. Regional Deep Dive
- **Single Region Focus**: Deep dive into any Virginia region
- **Overall Score & Rank**: Quick summary metrics
- **Measure-by-Measure Breakdown**: See scores for individual measures
- **Component Filtering**: Focus on specific components
- **Strengths & Challenges**: Top 5 highest and lowest scoring measures

### 4. Peer Comparison
- **Peer Distance Visualization**: See how closely matched peer regions are
- **Peer Details Table**: Complete information on all 8 peer regions
- **Matching Variables**: Population, employment, demographics used for matching

### 5. Data Explorer
- **Full Dataset Access**: Browse all underlying data
- **Download Capability**: Export any dataset as CSV
- **Multiple Views**: Overall index, components, detailed measures, peer regions

## Score Interpretation

- **100** = Peer average performance
- **>100** = Above peer average (better performance)
- **<100** = Below peer average (needs improvement)
- **0** = One standard deviation below peer average
- **200** = One standard deviation above peer average

## Data Sources

The dashboard loads data from:
- `data/results/thriving_index_overall.csv` - Overall scores
- `data/results/thriving_index_by_component.csv` - Component scores
- `data/results/thriving_index_detailed_scores.csv` - Measure-level scores
- `data/peer_regions_selected.csv` - Peer region information

## Troubleshooting

### Module not found errors
If you see "ModuleNotFoundError", install dependencies:
```bash
pip install -r requirements.txt
```

### Dashboard won't start
Make sure you're in the project root directory:
```bash
cd /path/to/thriving_index
streamlit run dashboard.py
```

### Port already in use
If port 8501 is busy, specify a different port:
```bash
streamlit run dashboard.py --server.port 8502
```

## Deployment Options

### Local Development
The dashboard runs locally by default. Perfect for exploration and analysis.

### Streamlit Cloud (Free Hosting)
1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py"]
```

## Customization

### Adding New Visualizations
Edit `dashboard.py` and add new functions following the existing patterns.

### Changing Colors
Modify the color schemes in the `create_*_chart()` functions:
- Green/Red theme: `#28a745` / `#dc3545`
- Plotly color scales: `RdYlGn`, `Viridis`, etc.

### Adding Pages
Add new page options in the sidebar radio button and corresponding logic.

## Technical Details

- **Framework**: Streamlit 1.28+
- **Visualizations**: Plotly Express & Graph Objects
- **Data**: Pandas DataFrames
- **Caching**: `@st.cache_data` for performance
- **Responsive**: Works on desktop, tablet, mobile

## Support

For issues or questions:
1. Check this README
2. Review the main PROJECT_PLAN.md
3. Examine the dashboard.py code comments
