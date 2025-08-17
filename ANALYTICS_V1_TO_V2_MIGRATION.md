# Analytics V1 to V2 Migration Guide

## Overview
This document describes the migration from Analytics V1 to Analytics V2 and the archival of V1 components.

**Migration Date:** August 11, 2025  
**Reason:** Analytics V2 provides a more robust, feature-rich implementation with better chart rendering, theme support, and data generation.

## What Was Archived

### 1. Core Analytics V1 Files
**Moved to:** `src/agents/archives/analytics_v1/`

- `analytics_agent.py` - Original analytics agent implementation
- `analytics_utils/` - Complete utilities directory including:
  - `conductor.py` - Chart selection logic
  - `data_synthesizer.py` - Synthetic data generation
  - `mermaid_chart_agent.py` - Mermaid chart generation
  - `python_chart_agent.py` - Python/matplotlib chart generation
  - `models.py` - Data models for V1
  - Various MCP and backup implementations

### 2. Test Files
**Moved to:** `test/archives/analytics_v1_tests/`

All V1-related test files including:
- Root directory test files (test_all_charts.py, test_playbook_*.py, etc.)
- Test directory analytics tests
- Diagram analytics tests

### 3. Active V2 Components
**Location:** `src/agents/`

- `analytics_agent_v2.py` - New analytics agent
- `analytics_utils_v2/` - New utilities with enhanced features

## Key Differences: V1 vs V2

### Architecture Improvements
| Feature | V1 | V2 |
|---------|----|----|
| Chart Types | 23 types (some broken) | 23 types (all working) |
| Theme Support | Basic | Advanced with gradients |
| Data Generation | Simple | LLM-enhanced with context |
| Error Handling | Basic | Comprehensive with fallbacks |
| File Output | Limited | PNG + JSON with metadata |

### Fixed Issues in V2
1. ✅ **Horizontal Bar Chart** - Now correctly uses `barh()`
2. ✅ **Violin Plot** - Properly shows violin shapes with bimodal distributions
3. ✅ **Stacked Area Chart** - Fixed label sorting (Period_1, Period_2... instead of Period_1, Period_10...)
4. ✅ **Histogram** - Uses raw values instead of frequency counts
5. ✅ **Theme Validation** - Proper ThemeConfig with defaults

## How to Use V2

### Basic Usage
```python
from src.agents.analytics_agent_v2 import create_analytics_v2

# Generate a chart with synthetic data
response = await create_analytics_v2(
    content="Show monthly revenue trend",
    title="Revenue Trend 2024",
    chart_type="line_chart",  # Optional - will auto-select if not provided
    use_synthetic_data=True,
    theme={
        "primary": "#2563EB",
        "secondary": "#EC4899",
        "tertiary": "#06B6D4"
    },
    save_files=True,
    output_dir="charts_output"
)
```

### With User Data
```python
# Provide your own data
user_data = [
    {"label": "Q1", "value": 100000},
    {"label": "Q2", "value": 120000},
    {"label": "Q3", "value": 115000},
    {"label": "Q4", "value": 140000}
]

response = await create_analytics_v2(
    content="Quarterly sales performance",
    title="Sales by Quarter",
    data=user_data,
    use_synthetic_data=False
)
```

## API Changes

### Import Changes
```python
# Old (V1)
from src.agents.analytics_agent import create_analytics_chart

# New (V2)
from src.agents.analytics_agent_v2 import create_analytics_v2
```

### Function Signature Changes
```python
# V1
create_analytics_chart(
    content: str,
    title: Optional[str] = None,
    data: Optional[List[Dict]] = None
) -> ChartOutput

# V2
create_analytics_v2(
    content: str,
    title: Optional[str] = None,
    data: Optional[List[Dict[str, Any]]] = None,
    use_synthetic_data: bool = True,
    theme: Optional[Dict[str, Any]] = None,
    chart_type: Optional[str] = None,
    enhance_labels: bool = True,
    mcp_tool=None,
    save_files: bool = False,
    output_dir: str = "analytics_output"
) -> Dict[str, Any]
```

## Response Format Changes

### V1 Response
```python
{
    "status": "success",
    "chart_type": "bar_chart",
    "format": "mermaid",
    "content": "chart code..."
}
```

### V2 Response
```python
{
    "success": true,
    "chart": "base64_encoded_png",
    "data": {
        "labels": [...],
        "values": [...],
        "statistics": {...}
    },
    "metadata": {
        "chart_type": "bar_chart_vertical",
        "generation_method": "python_mcp",
        "data_source": "synthetic",
        "theme_applied": {...},
        "insights": [...],
        "timestamp": "2025-08-11T22:00:00"
    }
}
```

## Archive Structure
```
src/agents/archives/analytics_v1/
├── analytics_agent.py
└── analytics_utils/
    ├── conductor.py
    ├── data_synthesizer.py
    ├── mermaid_chart_agent.py
    ├── python_chart_agent.py
    ├── models.py
    └── [other v1 files]

test/archives/analytics_v1_tests/
├── test_all_charts.py
├── test_playbook_*.py
├── diagram_analytics_tests/
└── [other v1 test files]
```

## Rollback Instructions
If you need to rollback to V1:
1. Move files back from `src/agents/archives/analytics_v1/` to `src/agents/`
2. Move test files back from `test/archives/analytics_v1_tests/` to their original locations
3. Update imports in your code

## Support
For questions about the migration or V2 features, refer to:
- `ANALYTICS_AGENT_REBUILD_STRATEGY.md` - V2 design documentation
- `src/agents/analytics_utils_v2/` - V2 implementation code
- Test files: `test_8_charts_v2.py`, `test_all_23_charts_comprehensive.py`

## Benefits of V2
- ✅ All 23 chart types working correctly
- ✅ Advanced theme customization with gradients
- ✅ LLM-enhanced data generation
- ✅ Better error handling and fallbacks
- ✅ PNG and JSON output for API transmission
- ✅ Comprehensive metadata and insights
- ✅ Rate limiting support for API calls
- ✅ Local execution fallback when MCP unavailable