# FCC Broadband API - Placeholder Implementation Design

**Date**: 2025-11-14
**Status**: Design Specification
**Measure**: 6.1 - Broadband Access (% with access to broadband)

---

## Context

The FCC (Federal Communications Commission) Broadband Map API provides data on broadband availability across the United States. This data is needed for **Measure 6.1** (Broadband Access) in **Component Index 6** (Infrastructure & Cost of Doing Business).

**Current Status**: FCC API key is not yet available.

**User Requirement**: Create placeholder implementation that can be fully integrated once the FCC API key is obtained.

---

## Design Goals

1. **Future-Ready**: Structure code to easily integrate real FCC API when key is available
2. **Graceful Degradation**: System continues to work without broadband data
3. **Clear Documentation**: Make it obvious where API key should be added
4. **Testable**: Allow testing of data flow even without real API
5. **No Silent Failures**: Log clearly when broadband data is unavailable

---

## Implementation Strategy

### Approach: **Conditional Inclusion with Logging**

The broadband measure will be **conditionally included** based on API key availability:
- If API key present: Fetch and use real data
- If API key absent: Skip measure, log warning, exclude from index calculation

---

## Code Architecture

### 1. Configuration Module

**File**: `src/utils/config.py`

```python
import os
import logging

logger = logging.getLogger(__name__)

class APIConfig:
    """Central configuration for all API keys"""

    # Essential APIs (always required)
    CENSUS_KEY = os.getenv('CENSUS_KEY')
    BEA_API_KEY = os.getenv('BEA_API_KEY')
    BLS_API_KEY = os.getenv('BLS_API_KEY')

    # Optional APIs (graceful degradation)
    FCC_API_KEY = os.getenv('FCC_API_KEY', None)
    FBI_UCR_KEY = os.getenv('FBI_UCR_KEY', None)
    NASSQS_TOKEN = os.getenv('NASSQS_TOKEN', None)

    # Feature flags
    FCC_ENABLED = FCC_API_KEY is not None
    FBI_ENABLED = FBI_UCR_KEY is not None
    NASS_ENABLED = NASSQS_TOKEN is not None

    @classmethod
    def validate_essential_keys(cls):
        """Raise error if essential keys are missing"""
        missing = []
        if not cls.CENSUS_KEY:
            missing.append('CENSUS_KEY')
        if not cls.BEA_API_KEY:
            missing.append('BEA_API_KEY')
        if not cls.BLS_API_KEY:
            missing.append('BLS_API_KEY')

        if missing:
            raise ValueError(f"Missing essential API keys: {', '.join(missing)}")

    @classmethod
    def log_api_status(cls):
        """Log which APIs are available"""
        logger.info("=== API Configuration ===")
        logger.info(f"Census API: {'✓ Available' if cls.CENSUS_KEY else '✗ Missing'}")
        logger.info(f"BEA API: {'✓ Available' if cls.BEA_API_KEY else '✗ Missing'}")
        logger.info(f"BLS API: {'✓ Available' if cls.BLS_API_KEY else '✗ Missing'}")
        logger.info(f"FCC API: {'✓ Available' if cls.FCC_ENABLED else '⏳ Pending (placeholder mode)'}")
        logger.info(f"FBI UCR API: {'✓ Available' if cls.FBI_ENABLED else '✗ Missing'}")
        logger.info(f"USDA NASS API: {'✓ Available' if cls.NASS_ENABLED else '✗ Missing'}")
        logger.info("========================")
```

### 2. FCC API Client (Placeholder)

**File**: `src/api_clients/fcc_api.py`

```python
import logging
from typing import Optional, Dict, Any
from .base_api import BaseAPIClient
from ..utils.config import APIConfig

logger = logging.getLogger(__name__)

class FCCBroadbandAPI(BaseAPIClient):
    """
    FCC Broadband Map API Client

    PLACEHOLDER IMPLEMENTATION: This client is designed to integrate with the
    FCC Broadband Map API once an API key is obtained. Until then, all methods
    return None and log warnings.

    To enable:
    1. Obtain FCC API key from [URL to be determined]
    2. Set environment variable: export FCC_API_KEY="your_key_here"
    3. Restart application

    API Documentation: https://broadbandmap.fcc.gov/
    """

    BASE_URL = "https://broadbandmap.fcc.gov/api"  # Placeholder URL

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FCC API client

        Args:
            api_key: FCC API key. If None, uses environment variable FCC_API_KEY
        """
        api_key = api_key or APIConfig.FCC_API_KEY
        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            cache_dir="cache/fcc",
            rate_limit=None  # Unknown until API docs available
        )

        if not self.api_key:
            logger.warning(
                "FCC API key not configured. Broadband data will not be available. "
                "Set FCC_API_KEY environment variable to enable."
            )

    def get_broadband_access(
        self,
        state: str,
        county: Optional[str] = None,
        year: int = 2022
    ) -> Optional[Dict[str, Any]]:
        """
        Get broadband access data for a county

        PLACEHOLDER: Returns None until API key is configured.

        Args:
            state: Two-letter state code (e.g., 'VA')
            county: County name (e.g., 'Fairfax County')
            year: Data year

        Returns:
            Dictionary with broadband access data, or None if API unavailable
            Expected structure when implemented:
            {
                'state': 'VA',
                'county': 'Fairfax County',
                'year': 2022,
                'pct_broadband_access': 95.5,
                'pct_25_3_mbps': 93.2,  # 25 Mbps down / 3 Mbps up
                'pct_100_20_mbps': 85.0,  # 100 Mbps down / 20 Mbps up
                'data_source': 'FCC Broadband Map'
            }
        """
        if not self.api_key:
            logger.debug(
                f"Skipping broadband data for {county}, {state} - FCC API key not available"
            )
            return None

        # TODO: Implement actual API call when key is available
        # Example endpoint (to be verified):
        # endpoint = f"/broadband/county/{state}/{county}/{year}"
        # params = {'api_key': self.api_key}
        # return self.fetch(endpoint, params, cache_expiry=86400)

        logger.warning(
            "FCC API implementation pending. API key is configured but endpoint "
            "implementation is not yet complete."
        )
        return None

    def get_broadband_access_bulk(
        self,
        state: str,
        year: int = 2022
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get broadband access data for all counties in a state

        PLACEHOLDER: Returns None until API key is configured.

        Args:
            state: Two-letter state code (e.g., 'VA')
            year: Data year

        Returns:
            Dictionary mapping county names to broadband data, or None if API unavailable
        """
        if not self.api_key:
            logger.debug(
                f"Skipping bulk broadband data for {state} - FCC API key not available"
            )
            return None

        # TODO: Implement bulk query when API is available
        # This may be more efficient than individual county queries

        logger.warning("FCC bulk API implementation pending")
        return None

    def is_available(self) -> bool:
        """Check if FCC API is available and configured"""
        return self.api_key is not None
```

### 3. Data Collection Module

**File**: `src/data_collection/fetch_infrastructure.py`

```python
import logging
import pandas as pd
from typing import List, Dict, Any
from ..api_clients.fcc_api import FCCBroadbandAPI
from ..utils.config import APIConfig

logger = logging.getLogger(__name__)

class InfrastructureDataCollector:
    """Collect infrastructure and cost of doing business measures"""

    def __init__(self):
        self.fcc_api = FCCBroadbandAPI()

    def collect_broadband_data(
        self,
        regions: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Collect broadband access data for all regions

        Args:
            regions: List of region dictionaries with 'state', 'counties', etc.

        Returns:
            DataFrame with broadband access by region
            Columns: region_id, pct_broadband_access

        Note:
            If FCC API is not available, returns DataFrame with NaN values
            and logs warnings. The measure will be excluded from index calculation.
        """
        if not self.fcc_api.is_available():
            logger.warning(
                "FCC API not available. Broadband access measure will be excluded "
                "from Infrastructure & Cost index. To enable, set FCC_API_KEY "
                "environment variable."
            )
            # Return DataFrame with NaN values
            return pd.DataFrame({
                'region_id': [r['region_id'] for r in regions],
                'pct_broadband_access': [None] * len(regions),
                'broadband_data_available': [False] * len(regions)
            })

        logger.info(f"Collecting broadband access data for {len(regions)} regions...")

        results = []
        for region in regions:
            try:
                # For multi-county regions, may need to aggregate
                # Placeholder: fetch for first county or aggregate across all
                broadband_data = self._get_region_broadband(region)

                results.append({
                    'region_id': region['region_id'],
                    'pct_broadband_access': broadband_data.get('pct_broadband_access') if broadband_data else None,
                    'broadband_data_available': broadband_data is not None
                })
            except Exception as e:
                logger.error(f"Error fetching broadband data for {region['region_id']}: {e}")
                results.append({
                    'region_id': region['region_id'],
                    'pct_broadband_access': None,
                    'broadband_data_available': False
                })

        df = pd.DataFrame(results)
        available_count = df['broadband_data_available'].sum()
        logger.info(f"Broadband data collected: {available_count}/{len(regions)} regions")

        return df

    def _get_region_broadband(self, region: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get broadband data for a region (may aggregate multiple counties)"""
        # Implementation depends on whether region is single county or multi-county
        # For now, placeholder
        return self.fcc_api.get_broadband_access(
            state=region['state'],
            county=region.get('counties', [None])[0] if region.get('counties') else None
        )
```

### 4. Index Calculation Module

**File**: `src/scoring/component_index.py`

```python
import logging
import pandas as pd
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

class ComponentIndexCalculator:
    """Calculate component indexes from measures"""

    # Component definitions
    COMPONENTS = {
        'infrastructure_cost': {
            'name': 'Infrastructure & Cost of Doing Business',
            'measures': [
                'broadband_access',  # May be missing
                'housing_affordability',
                'pct_housing_recent',
                'property_crime_rate',
                'violent_crime_rate',
                # highway_accessibility excluded (no API)
            ]
        },
        # ... other components
    }

    def calculate_component_index(
        self,
        component_id: str,
        measures_df: pd.DataFrame,
        inverse_measures: Optional[List[str]] = None
    ) -> pd.Series:
        """
        Calculate component index from constituent measures

        Args:
            component_id: Component identifier (e.g., 'infrastructure_cost')
            measures_df: DataFrame with standardized measure indexes
            inverse_measures: List of measures where lower is better

        Returns:
            Series with component index scores by region

        Note:
            If any measures are missing (NaN), they are excluded from the average.
            Component index is calculated as the mean of available measures.
            If no measures are available, component index is NaN.
        """
        component = self.COMPONENTS[component_id]
        measure_columns = component['measures']

        # Check which measures are available
        available_measures = [m for m in measure_columns if m in measures_df.columns]
        missing_measures = [m for m in measure_columns if m not in measures_df.columns]

        if missing_measures:
            logger.warning(
                f"Component '{component['name']}': Missing measures: {', '.join(missing_measures)}"
            )

        if not available_measures:
            logger.error(
                f"Component '{component['name']}': No measures available! "
                f"Cannot calculate component index."
            )
            return pd.Series(np.nan, index=measures_df.index)

        # Calculate mean of available measures, ignoring NaN
        component_index = measures_df[available_measures].mean(axis=1, skipna=True)

        # Count how many measures contributed to each region's score
        measure_counts = measures_df[available_measures].notna().sum(axis=1)

        # Log summary
        logger.info(
            f"Component '{component['name']}': "
            f"{len(available_measures)}/{len(measure_columns)} measures available. "
            f"Avg measures per region: {measure_counts.mean():.1f}"
        )

        # Warn if some regions have very few measures
        min_measures = measure_counts.min()
        if min_measures < len(available_measures) * 0.5:
            logger.warning(
                f"Some regions have < 50% of available measures for '{component['name']}'"
            )

        return component_index
```

### 5. Dashboard Display

**File**: `dashboard/components/infrastructure_view.py`

```python
import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from typing import Optional

def render_infrastructure_component(region_data: pd.Series) -> html.Div:
    """
    Render Infrastructure & Cost component view for a region

    Args:
        region_data: Series with all measure values for a region

    Returns:
        Dash HTML component
    """
    measures = [
        {
            'id': 'broadband_access',
            'name': 'Broadband Access',
            'value': region_data.get('broadband_access'),
            'status': region_data.get('broadband_data_available', False)
        },
        {
            'id': 'housing_affordability',
            'name': 'Housing Affordability',
            'value': region_data.get('housing_affordability'),
            'status': True
        },
        # ... other measures
    ]

    measure_cards = []
    for measure in measures:
        if measure['status'] and pd.notna(measure['value']):
            # Data available - show value
            card = html.Div([
                html.H5(measure['name']),
                html.P(f"Index Score: {measure['value']:.1f}", className='score'),
            ], className='measure-card available')
        else:
            # Data not available - show placeholder
            card = html.Div([
                html.H5(measure['name']),
                html.P("Data pending", className='pending'),
                html.Small(
                    "This measure requires FCC API access. "
                    "It will be included once the API key is configured.",
                    className='help-text'
                )
            ], className='measure-card pending')

        measure_cards.append(card)

    return html.Div([
        html.H3("Infrastructure & Cost of Doing Business"),
        html.Div(measure_cards, className='measures-grid')
    ])
```

### 6. Testing Support

**File**: `tests/test_fcc_placeholder.py`

```python
import pytest
import os
from src.api_clients.fcc_api import FCCBroadbandAPI
from src.utils.config import APIConfig

class TestFCCPlaceholder:
    """Test FCC API placeholder behavior"""

    def test_no_api_key_returns_none(self):
        """Test that API returns None when key is not configured"""
        # Ensure API key is not set
        old_key = os.environ.get('FCC_API_KEY')
        if 'FCC_API_KEY' in os.environ:
            del os.environ['FCC_API_KEY']

        api = FCCBroadbandAPI()
        result = api.get_broadband_access('VA', 'Fairfax County')

        assert result is None
        assert not api.is_available()

        # Restore original key if it existed
        if old_key:
            os.environ['FCC_API_KEY'] = old_key

    def test_api_key_present_returns_data_or_warning(self):
        """Test that API acknowledges key when present"""
        # Set a dummy API key
        os.environ['FCC_API_KEY'] = 'test_key_placeholder'

        api = FCCBroadbandAPI()

        assert api.is_available()
        assert api.api_key == 'test_key_placeholder'

        # Should return None but log that implementation is pending
        result = api.get_broadband_access('VA', 'Fairfax County')
        # For now, still returns None until actual implementation
        assert result is None

        # Cleanup
        del os.environ['FCC_API_KEY']

    def test_component_calculation_handles_missing_broadband(self):
        """Test that component index calculation handles missing broadband data"""
        # Create test data with missing broadband
        import pandas as pd
        measures_df = pd.DataFrame({
            'region_id': ['R1', 'R2', 'R3'],
            'broadband_access': [None, None, None],  # Missing
            'housing_affordability': [120, 100, 80],
            'property_crime_rate': [90, 110, 100],
        })

        from src.scoring.component_index import ComponentIndexCalculator
        calculator = ComponentIndexCalculator()

        # Should calculate index from available measures only
        component_index = calculator.calculate_component_index(
            'infrastructure_cost',
            measures_df
        )

        assert len(component_index) == 3
        assert all(pd.notna(component_index))  # Should have values despite missing broadband
```

---

## Usage Instructions

### For Developers

**During Development (no API key)**:
1. Code will log warnings about missing FCC API key
2. Broadband measure will be excluded from index calculations
3. Dashboard will show "Data pending" for broadband measure
4. All other functionality works normally

**When API Key Obtained**:
1. Add API key to environment: `export FCC_API_KEY="your_key_here"`
2. Research FCC API documentation to determine exact endpoints
3. Update `FCCBroadbandAPI` class with real implementation:
   - Replace placeholder `BASE_URL` with actual FCC API URL
   - Implement `get_broadband_access()` with real API calls
   - Add rate limiting if required
   - Update data structure to match FCC response format
4. Test with sample requests
5. Re-run data collection to fetch broadband data
6. Recalculate Infrastructure component index
7. Update dashboard to display broadband data

### For Users/Analysts

**Current State**:
- Infrastructure & Cost index includes 4 measures (out of 5 possible)
- Broadband access is excluded pending API access
- Index scores are still valid and comparable

**Future State** (when API key available):
- Infrastructure & Cost index will include 5 measures
- Index scores will be recalculated (scores will change slightly)
- Historical comparability: may need to provide both "with" and "without" broadband versions

---

## Documentation Requirements

### 1. In-Code Documentation

All FCC-related code includes:
- ✅ Class/function docstrings explaining placeholder status
- ✅ TODO comments indicating where real implementation goes
- ✅ Instructions for enabling FCC API

### 2. README Section

Add to main `README.md`:

```markdown
## Optional Data Sources

### FCC Broadband Data

The FCC Broadband Map provides data on broadband access, used for the
Infrastructure & Cost component index.

**Status**: ⏳ API key pending

**To enable**:
1. Obtain FCC API key from [URL]
2. Set environment variable: `export FCC_API_KEY="your_key"`
3. Update `src/api_clients/fcc_api.py` with API endpoints
4. Re-run data collection: `python scripts/collect_data.py`

**Impact if disabled**: Infrastructure index calculated from 4 measures instead of 5.
```

### 3. Configuration File

**File**: `.env.example`

```bash
# Essential API Keys (Required)
CENSUS_KEY=your_census_key_here
BEA_API_KEY=your_bea_key_here
BLS_API_KEY=your_bls_key_here

# Optional API Keys (Graceful degradation if missing)
FCC_API_KEY=pending  # Set to your key when obtained
FBI_UCR_KEY=your_fbi_key_here
NASSQS_TOKEN=your_nass_key_here
```

### 4. Logging Messages

**Log Levels**:
- `INFO`: FCC API status at startup (available/pending)
- `WARNING`: When broadband data is skipped due to missing API key
- `DEBUG`: Individual county skips (verbose)

**Example Logs**:
```
INFO: === API Configuration ===
INFO: Census API: ✓ Available
INFO: BEA API: ✓ Available
INFO: BLS API: ✓ Available
INFO: FCC API: ⏳ Pending (placeholder mode)
WARNING: FCC API not available. Broadband access measure will be excluded from Infrastructure & Cost index.
INFO: Component 'Infrastructure & Cost': 4/5 measures available.
```

---

## Testing Strategy

### 1. Unit Tests
- ✅ Test FCC client returns None when key missing
- ✅ Test FCC client acknowledges key when present
- ✅ Test component calculation with missing measures
- ✅ Test dashboard renders "pending" state correctly

### 2. Integration Tests
- ✅ Test full data collection pipeline with FCC disabled
- ✅ Test index calculation produces valid scores without broadband
- ✅ Test dashboard loads without errors

### 3. Manual Testing Checklist
- [ ] Run data collection without FCC key - should complete successfully
- [ ] Check logs for appropriate warnings
- [ ] View dashboard - Infrastructure index should show 4/5 measures
- [ ] Export data - broadband column should be empty
- [ ] Add dummy FCC key - system should acknowledge but still return None
- [ ] Remove FCC key - system should revert to placeholder mode

---

## Future Implementation Checklist

When FCC API key is obtained:

- [ ] Research FCC Broadband Map API documentation
- [ ] Identify exact endpoint URLs
- [ ] Determine authentication method (API key in header? Query param?)
- [ ] Understand response format
- [ ] Update `BASE_URL` in `FCCBroadbandAPI`
- [ ] Implement `get_broadband_access()` with real API call
- [ ] Implement `get_broadband_access_bulk()` if bulk endpoint available
- [ ] Add rate limiting if required
- [ ] Test API connection with sample requests
- [ ] Update data collection to use real FCC data
- [ ] Recalculate all index scores
- [ ] Update dashboard to show real broadband data
- [ ] Document API access in `API_INVESTIGATION_REPORT.md`
- [ ] Update `API_MAPPING.md`: Broadband (MEDIUM → HIGH)
- [ ] Update `API_KEYS_STATUS.md`
- [ ] Remove "placeholder" notices from code comments
- [ ] Update tests to expect real data structure

---

## Summary

This design ensures that:
1. ✅ System works without FCC API key (graceful degradation)
2. ✅ Clear logging indicates when broadband data is unavailable
3. ✅ Code structure makes it easy to add real implementation later
4. ✅ Dashboard displays "pending" state for broadband measure
5. ✅ Index calculations handle missing data appropriately
6. ✅ No silent failures or confusing errors

**When API key is obtained**, implementation should be straightforward:
- Update API endpoints in `fcc_api.py`
- Re-run data collection
- Recalculate indexes
- Update dashboard

**Until then**, the system provides a complete, working thriving index with 29-30 measures across 7.5 component indexes (Infrastructure index at 4/5 measures instead of 5/5).

---

*This placeholder implementation will be replaced with real FCC API integration when the API key is obtained.*
