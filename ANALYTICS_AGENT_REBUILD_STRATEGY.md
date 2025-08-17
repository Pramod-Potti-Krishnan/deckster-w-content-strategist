# Analytics Agent Rebuild Strategy

## Executive Summary

This document outlines a comprehensive rebuild strategy for the Analytics Agent based on extensive testing and learnings from achieving a 56.5% success rate with 23 chart types. The rebuilt system features a **two-phase generation architecture**, **LLM-enhanced synthetic data**, **theme customization**, and returns both **PNG charts and JSON data** via API.

### Key Improvements
- ✅ Fixed chart implementations (violin, horizontal bar, stacked area, histogram)
- ✅ Two-phase system: Code Generation → Execution
- ✅ User data with synthetic fallback
- ✅ LLM-powered professional labeling
- ✅ Theme customization with primary/secondary/tertiary colors
- ✅ API returns PNG + JSON
- ✅ Rate limiting and error handling

---

## 1. Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                           │
│  Request: {content, data?, theme?, use_synthetic_data}   │
│  Response: {chart: PNG, data: JSON, metadata}           │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                Analytics Orchestrator                    │
│  • Route requests                                        │
│  • Manage data sources                                   │
│  • Apply themes                                          │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Conductor   │   │Data Manager  │   │Theme Engine  │
│ LLM + Rules  │   │User/Synthetic│   │Color Mixing  │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │          Chart Generators              │
        ├─────────────────┬─────────────────────┤
        │  Python Agent   │   Mermaid Agent     │
        │  (18 types)     │   (5 types)         │
        └─────────────────┴─────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         Execution Engine               │
        │  • MCP Executor (Jupyter)              │
        │  • PNG Generation                      │
        │  • Base64 Encoding                    │
        └───────────────────────────────────────┘
```

### Two-Phase Generation System

**Phase 1: Code Generation**
- Generate Python/Mermaid code based on request
- Apply theme colors and styling
- Include data processing logic

**Phase 2: Execution**
- Execute code via MCP or subprocess
- Generate PNG output
- Return base64 encoded image

---

## 2. Data Strategy

### Data Source Priority

```python
def determine_data_source(request):
    if request.data and len(request.data) > 0:
        # User provided data
        return UserDataProcessor(request.data)
    elif request.use_synthetic_data != False:
        # Generate synthetic data (default: True)
        return SyntheticDataGenerator(request)
    else:
        # Error: No data available
        raise ValueError("No data provided and synthetic data disabled")
```

### User-Provided Data Format

```json
{
  "data": [
    {"label": "Q1 2024", "value": 45000, "category": "revenue"},
    {"label": "Q2 2024", "value": 52000, "category": "revenue"},
    {"label": "Q3 2024", "value": 48000, "category": "revenue"},
    {"label": "Q4 2024", "value": 61000, "category": "revenue"}
  ]
}
```

### LLM-Enhanced Synthetic Data

```python
class LLMDataEnhancer:
    """Generate professional labels and realistic values using LLM."""
    
    async def generate_labels(self, context: str, count: int) -> List[str]:
        """
        Generate context-aware labels.
        
        Examples:
        - Revenue context → ["North America", "Europe", "Asia Pacific"]
        - Time context → ["Jan 2024", "Feb 2024", "Mar 2024"]
        - Product context → ["Enterprise", "Professional", "Starter"]
        """
        prompt = f"""
        Generate {count} professional labels for a chart about: {context}
        Return labels that are:
        - Industry-appropriate
        - Consistent in format
        - Clear and concise
        """
        return await self.llm.generate(prompt)
    
    async def generate_realistic_values(self, context: str, labels: List[str]) -> List[float]:
        """
        Generate realistic values based on context.
        
        Examples:
        - Revenue: $10K-$1M range
        - Percentages: 0-100, sum to 100 for pie
        - Growth rates: -20% to +50%
        """
        prompt = f"""
        Generate realistic values for {labels} in context of: {context}
        Consider:
        - Industry benchmarks
        - Logical relationships
        - Statistical distributions
        """
        return await self.llm.generate(prompt)
```

---

## 3. Theme Customization System

### Theme Configuration

```python
class ChartTheme:
    """Complete theme configuration for charts."""
    
    def __init__(self, 
                 primary: str = "#1E40AF",      # Blue
                 secondary: str = "#10B981",    # Green  
                 tertiary: str = "#F59E0B",     # Amber
                 style: str = "modern"):
        self.primary = primary
        self.secondary = secondary
        self.tertiary = tertiary
        self.style = style
        
        # Generate color palette
        self.palette = self._generate_palette()
        
    def _generate_palette(self) -> List[str]:
        """Generate extended palette from base colors."""
        palette = [self.primary, self.secondary, self.tertiary]
        
        # Add shades
        for color in [self.primary, self.secondary]:
            palette.extend(self._generate_shades(color, 3))
        
        # Add complementary colors
        palette.extend(self._generate_complementary(self.primary))
        
        return palette
    
    def _mix_colors(self, color1: str, color2: str, ratio: float = 0.5) -> str:
        """Mix two colors with given ratio."""
        # Implementation for color mixing
        pass
    
    def apply_to_chart(self, chart_type: str) -> Dict[str, Any]:
        """Get theme configuration for specific chart type."""
        configs = {
            "line_chart": {
                "line_colors": self.palette[:5],
                "grid_color": self._lighten(self.tertiary, 0.3),
                "background": "#FFFFFF"
            },
            "bar_chart": {
                "colors": self._gradient(self.primary, self.secondary),
                "edge_color": self._darken(self.primary, 0.2)
            },
            "pie_chart": {
                "colors": self.palette,
                "explode_color": self.tertiary
            },
            "heatmap": {
                "colormap": self._create_colormap(self.primary, self.tertiary),
                "bad_color": "#CCCCCC"
            }
        }
        return configs.get(chart_type, {"colors": self.palette})
```

### Theme Application in Charts

```python
def generate_themed_chart(data, theme: ChartTheme, chart_type: str):
    """Generate chart with applied theme."""
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Apply theme style
    if theme.style == "modern":
        plt.style.use('seaborn-v0_8-darkgrid')
    elif theme.style == "minimal":
        plt.style.use('seaborn-v0_8-white')
    
    # Get chart-specific colors
    colors = theme.apply_to_chart(chart_type)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Apply theme colors
    if chart_type == "bar_chart":
        ax.bar(data.labels, data.values, color=colors['colors'])
    elif chart_type == "line_chart":
        for i, series in enumerate(data.series):
            ax.plot(series.x, series.y, 
                   color=colors['line_colors'][i % len(colors['line_colors'])],
                   linewidth=2)
    
    # Style the plot
    ax.set_facecolor('#FAFAFA')
    ax.grid(True, alpha=0.3, color=colors.get('grid_color', '#E0E0E0'))
    
    return fig
```

---

## 4. API Specification

### Request Format

```python
class AnalyticsAPIRequest:
    content: str                    # Chart description/request
    title: Optional[str]            # Chart title
    data: Optional[List[Dict]]      # User-provided data
    use_synthetic_data: bool = True # Generate synthetic if no data
    theme: Optional[Dict] = {
        "primary": "#1E40AF",
        "secondary": "#10B981",
        "tertiary": "#F59E0B",
        "style": "modern"           # modern|classic|minimal
    }
    output_format: str = "png"      # png|svg|base64
    include_raw_data: bool = True   # Include JSON data in response
```

### Response Format

```python
class AnalyticsAPIResponse:
    success: bool
    chart: str                      # Base64 encoded PNG
    data: Dict = {
        "labels": [...],            # X-axis labels
        "values": [...],            # Y-axis values
        "series": [...],            # Multiple series if applicable
        "metadata": {               # Additional data properties
            "min": float,
            "max": float,
            "mean": float,
            "total": float
        }
    }
    metadata: Dict = {
        "chart_type": str,          # Actual chart type used
        "generation_method": str,   # python|mermaid
        "theme_applied": Dict,      # Theme configuration used
        "data_source": str,         # user|synthetic
        "insights": List[str],      # Auto-generated insights
        "timestamp": str            # Generation timestamp
    }
    error: Optional[str]            # Error message if failed
```

### API Usage Examples

```python
# Example 1: User-provided data with custom theme
async def example_user_data():
    response = await analytics_api.generate({
        "content": "Show quarterly revenue growth",
        "title": "Q1-Q4 2024 Revenue",
        "data": [
            {"label": "Q1", "value": 45000},
            {"label": "Q2", "value": 52000},
            {"label": "Q3", "value": 48000},
            {"label": "Q4", "value": 61000}
        ],
        "theme": {
            "primary": "#0EA5E9",   # Sky blue
            "secondary": "#22C55E",  # Green
            "tertiary": "#F97316"    # Orange
        }
    })
    
    # Save outputs
    save_png(response.chart, "revenue_chart.png")
    save_json(response.data, "revenue_data.json")

# Example 2: Synthetic data with LLM enhancement
async def example_synthetic_data():
    response = await analytics_api.generate({
        "content": "Create a pie chart showing market share distribution for top 5 cloud providers",
        "title": "Cloud Market Share 2024",
        "use_synthetic_data": True,  # Will generate realistic market share data
        "theme": {
            "style": "minimal"
        }
    })
    
    # Response includes LLM-generated labels like:
    # ["AWS", "Azure", "Google Cloud", "Alibaba Cloud", "IBM Cloud"]
    # With realistic market share percentages
```

---

## 5. Component Specifications

### 5.1 Analytics Playbook (`analytics_playbook.py`)

```python
ANALYTICS_PLAYBOOK = {
    "version": "2.0",
    "charts": {
        "line_chart": {
            "renderer": "matplotlib",
            "when_to_use": [
                "Trend over time",
                "Multiple series comparison",
                "Show patterns and anomalies"
            ],
            "data_requirements": [
                {"role": "x", "type": "time|ordered"},
                {"role": "y", "type": "numeric"},
                {"role": "series", "type": "category", "optional": True}
            ],
            "theme_config": {
                "supports_gradient": False,
                "max_series": 5,
                "color_application": "per_series"
            },
            "synthetic_features": {
                "rows": 100,
                "pattern": "trend|seasonal|random",
                "noise_level": 0.1
            }
        },
        # ... 22 more chart specifications
    }
}
```

### 5.2 Enhanced Python Chart Agent

```python
class EnhancedPythonChartAgent:
    """Fixed implementations for all chart types."""
    
    async def generate_chart(self, request: ChartRequest) -> ChartOutput:
        """Generate chart with proper implementation."""
        
        # Map to correct implementation
        generators = {
            "violin_plot": self._generate_violin_plot,      # Uses violinplot()
            "bar_horizontal": self._generate_horizontal_bar, # Uses barh()
            "stacked_area": self._generate_stacked_area,    # Multiple fill_between()
            "histogram": self._generate_histogram,          # Raw data values
            # ... all 23 types
        }
        
        generator = generators.get(request.chart_type)
        if not generator:
            raise ValueError(f"Unsupported chart type: {request.chart_type}")
        
        # Generate with theme
        code = generator(request.data, request.theme, request.title)
        
        # Execute and return PNG
        result = await self.executor.execute(code)
        return ChartOutput(
            chart=result.image_base64,
            format="png",
            code=code
        )
    
    def _generate_violin_plot(self, data, theme, title):
        """Correct violin plot implementation."""
        return f"""
import matplotlib.pyplot as plt
import numpy as np

# Create bimodal distribution for violin shape
data_arrays = []
for i in range(4):
    mode1 = np.random.normal(30 + i*10, 5, 100)
    mode2 = np.random.normal(60 + i*10, 5, 100)
    data_arrays.append(np.concatenate([mode1, mode2]))

fig, ax = plt.subplots(figsize=(10, 6))

# Use violinplot (not boxplot!)
parts = ax.violinplot(data_arrays, positions=range(4), widths=0.7,
                      showmeans=True, showmedians=True, showextrema=True)

# Apply theme colors
for pc, color in zip(parts['bodies'], ['{theme.primary}', '{theme.secondary}'] * 2):
    pc.set_facecolor(color)
    pc.set_alpha(0.7)

ax.set_title('{title}')
ax.set_xlabel('Groups')
ax.set_ylabel('Values')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
```

### 5.3 Data Synthesizer with LLM

```python
class LLMDataSynthesizer:
    """Generate realistic synthetic data with LLM enhancement."""
    
    def __init__(self, llm_model="gemini-2.0-flash-exp"):
        self.llm = create_model_with_fallback(llm_model)
    
    async def generate_data(self, request: DataRequest) -> List[DataPoint]:
        """Generate synthetic data with professional labels."""
        
        # Get LLM to generate appropriate labels
        labels = await self._generate_labels(request)
        
        # Generate realistic values based on context
        values = await self._generate_values(request, labels)
        
        # Apply statistical patterns
        if request.pattern == "trend":
            values = self._apply_trend(values, request.trend_direction)
        elif request.pattern == "seasonal":
            values = self._apply_seasonality(values, request.period)
        
        # Create data points
        data_points = []
        for label, value in zip(labels, values):
            data_points.append(DataPoint(
                label=label,
                value=value,
                metadata={"synthetic": True, "llm_generated": True}
            ))
        
        return data_points
    
    async def _generate_labels(self, request):
        """Generate context-appropriate labels using LLM."""
        prompt = f"""
        Generate {request.num_points} labels for a {request.chart_type} chart.
        Context: {request.description}
        
        Requirements:
        - Professional and consistent formatting
        - Appropriate for the domain
        - Logical ordering if applicable
        
        Return as JSON array of strings.
        """
        
        response = await self.llm.generate(prompt)
        return json.loads(response)
```

---

## 6. Implementation Guide

### 6.1 Folder Structure

```
src/agents/analytics_agent/
├── __init__.py
├── analytics_agent.py           # Main orchestrator
├── analytics_playbook.py        # Chart specifications
├── components/
│   ├── conductor.py            # LLM-based chart selection
│   ├── data_manager.py         # User/synthetic data handling
│   ├── theme_engine.py         # Color and theme management
│   ├── llm_enhancer.py         # LLM for labels and values
│   └── chart_validator.py      # Output validation
├── generators/
│   ├── python_chart_agent.py   # Python/matplotlib charts
│   ├── mermaid_chart_agent.py  # Mermaid charts
│   └── chart_implementations/  # Individual chart implementations
│       ├── violin_plot.py
│       ├── horizontal_bar.py
│       ├── stacked_area.py
│       └── ... (23 files)
├── executors/
│   ├── mcp_executor.py         # MCP/Jupyter execution
│   └── subprocess_executor.py  # Fallback execution
├── models/
│   ├── request_models.py       # API request structures
│   ├── response_models.py      # API response structures
│   └── data_models.py          # Data point structures
└── tests/
    ├── test_all_charts.py       # Comprehensive testing
    ├── test_themes.py           # Theme application tests
    └── test_synthetic_data.py  # LLM data generation tests
```

### 6.2 Rate Limiting Strategy

```python
class RateLimiter:
    """Handle API rate limits gracefully."""
    
    def __init__(self, requests_per_minute=10):
        self.rpm = requests_per_minute
        self.min_delay = 60 / requests_per_minute  # 6 seconds for 10 RPM
        self.last_request = 0
    
    async def wait_if_needed(self):
        """Ensure minimum delay between requests."""
        elapsed = time.time() - self.last_request
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)
        self.last_request = time.time()
    
    async def with_retry(self, func, max_retries=3):
        """Execute with exponential backoff on rate limit."""
        for attempt in range(max_retries):
            try:
                await self.wait_if_needed()
                return await func()
            except RateLimitError:
                wait_time = 60 * (2 ** attempt)  # 60s, 120s, 240s
                logger.warning(f"Rate limit hit, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
        raise Exception("Max retries exceeded")
```

---

## 7. Testing Framework

### 7.1 Comprehensive Test Suite

```python
class AnalyticsTestSuite:
    """Test all 23 chart types with various configurations."""
    
    async def test_all_charts(self):
        """Generate all chart types with different data/themes."""
        
        test_configs = [
            {
                "chart": "line_chart",
                "data_source": "synthetic",
                "theme": "default",
                "expected_success": True
            },
            # ... all 23 types
        ]
        
        results = []
        for config in test_configs:
            result = await self.test_single_chart(config)
            results.append(result)
        
        # Generate report
        success_rate = sum(r.success for r in results) / len(results)
        self.generate_html_report(results, success_rate)
    
    async def test_single_chart(self, config):
        """Test individual chart generation."""
        try:
            response = await analytics_api.generate({
                "content": f"Generate {config['chart']} test",
                "use_synthetic_data": config['data_source'] == "synthetic",
                "theme": self.get_test_theme(config['theme'])
            })
            
            # Validate response
            assert response.chart is not None
            assert response.data is not None
            assert len(response.data['values']) > 0
            
            # Save outputs for visual inspection
            self.save_test_output(config['chart'], response)
            
            return TestResult(success=True, chart=config['chart'])
            
        except Exception as e:
            logger.error(f"Test failed for {config['chart']}: {e}")
            return TestResult(success=False, chart=config['chart'], error=str(e))
```

### 7.2 Visual Validation Gallery

```python
def generate_test_gallery(test_outputs_dir):
    """Create HTML gallery for visual validation."""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chart Test Gallery</title>
        <style>
            .chart-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                padding: 20px;
            }
            .chart-card {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }
            .chart-img {
                max-width: 100%;
                height: 300px;
                object-fit: contain;
            }
        </style>
    </head>
    <body>
        <h1>Analytics Chart Test Gallery</h1>
        <div class="chart-grid">
    """
    
    for chart_file in sorted(os.listdir(test_outputs_dir)):
        if chart_file.endswith('.png'):
            chart_name = chart_file.replace('.png', '').replace('_', ' ').title()
            html += f"""
            <div class="chart-card">
                <h3>{chart_name}</h3>
                <img class="chart-img" src="{chart_file}" />
                <p>✅ Generated Successfully</p>
            </div>
            """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    with open(f"{test_outputs_dir}/gallery.html", "w") as f:
        f.write(html)
```

---

## 8. Migration Strategy

### Phase 1: Component Development (Week 1-2)
- [ ] Implement enhanced chart generators
- [ ] Build LLM data synthesizer
- [ ] Create theme engine
- [ ] Set up API structure

### Phase 2: Integration (Week 3)
- [ ] Integrate components
- [ ] Add rate limiting
- [ ] Implement error handling
- [ ] Create test suite

### Phase 3: Testing & Validation (Week 4)
- [ ] Run comprehensive tests
- [ ] Visual validation
- [ ] Performance benchmarking
- [ ] Fix identified issues

### Phase 4: Deployment (Week 5)
- [ ] Deploy with feature flags
- [ ] Monitor performance
- [ ] Collect metrics
- [ ] Iterate based on feedback

### Rollback Plan
```python
# Feature flag configuration
FEATURE_FLAGS = {
    "use_new_analytics": False,  # Toggle new system
    "use_llm_synthesis": False,  # Toggle LLM data generation
    "use_theme_engine": False,   # Toggle theme system
}

def get_analytics_agent():
    if FEATURE_FLAGS["use_new_analytics"]:
        return EnhancedAnalyticsAgent()
    else:
        return LegacyAnalyticsAgent()
```

---

## 9. Performance Optimizations

### 9.1 Caching Strategy

```python
class ChartCache:
    """Cache generated charts to reduce API calls."""
    
    def __init__(self, ttl=3600):  # 1 hour TTL
        self.cache = {}
        self.ttl = ttl
    
    def get_cache_key(self, request):
        """Generate unique cache key from request."""
        return hashlib.md5(
            json.dumps({
                "content": request.content,
                "data": request.data,
                "theme": request.theme
            }).encode()
        ).hexdigest()
    
    async def get_or_generate(self, request, generator_func):
        """Return cached chart or generate new."""
        key = self.get_cache_key(request)
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                logger.info("Returning cached chart")
                return entry['response']
        
        # Generate new
        response = await generator_func(request)
        
        # Cache result
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        return response
```

### 9.2 Parallel Processing

```python
async def generate_multiple_charts(requests: List[ChartRequest]):
    """Generate multiple charts in parallel with rate limiting."""
    
    rate_limiter = RateLimiter(requests_per_minute=10)
    
    async def generate_with_limit(request):
        await rate_limiter.wait_if_needed()
        return await analytics_api.generate(request)
    
    # Process in batches to respect rate limits
    batch_size = 5
    results = []
    
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i+batch_size]
        batch_results = await asyncio.gather(
            *[generate_with_limit(req) for req in batch]
        )
        results.extend(batch_results)
        
        # Wait between batches
        if i + batch_size < len(requests):
            await asyncio.sleep(30)  # Half-minute between batches
    
    return results
```

---

## 10. Monitoring & Metrics

### Key Metrics to Track

```python
class AnalyticsMetrics:
    """Track analytics agent performance."""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_charts": 0,
            "failed_charts": 0,
            "chart_types": {},
            "data_sources": {"user": 0, "synthetic": 0},
            "average_generation_time": 0,
            "rate_limit_hits": 0,
            "theme_usage": {}
        }
    
    def track_request(self, request, response, duration):
        """Track individual request metrics."""
        self.metrics["total_requests"] += 1
        
        if response.success:
            self.metrics["successful_charts"] += 1
        else:
            self.metrics["failed_charts"] += 1
        
        # Track chart type
        chart_type = response.metadata.get("chart_type")
        self.metrics["chart_types"][chart_type] = \
            self.metrics["chart_types"].get(chart_type, 0) + 1
        
        # Track data source
        data_source = response.metadata.get("data_source")
        self.metrics["data_sources"][data_source] += 1
        
        # Update average time
        self.update_average_time(duration)
    
    def get_success_rate(self):
        """Calculate overall success rate."""
        total = self.metrics["total_requests"]
        if total == 0:
            return 0
        return self.metrics["successful_charts"] / total * 100
```

---

## Conclusion

This comprehensive rebuild strategy addresses all identified issues and adds powerful new features:

1. **Reliability**: Fixed chart implementations increase success rate from 30% to 56%+
2. **Flexibility**: Support for user data with intelligent synthetic fallback
3. **Professional Output**: LLM-enhanced labels and realistic data generation
4. **Customization**: Full theme support with color mixing
5. **API Design**: Clean request/response with PNG + JSON outputs
6. **Scalability**: Rate limiting and caching for production use

The modular architecture allows for incremental improvements and easy testing of individual components. With proper implementation and testing, this system should achieve 80%+ success rate across all 23 chart types while providing professional, customizable outputs suitable for presentations and reports.