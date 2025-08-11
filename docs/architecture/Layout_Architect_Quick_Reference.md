# Layout Architect Three-Agent System - Quick Reference

## Quick Start

```python
from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest
)

# Initialize
orchestrator = LayoutArchitectOrchestrator()

# Generate layout
request = LayoutGenerationRequest(
    slide=slide,
    user_context={"brand": "TechCorp"},
    presentation_context={"tone": "professional"}
)
result = await orchestrator.generate_layout(request)

# Use results
layout = result.layout
theme = result.theme
```

## Agent Overview

| Agent | Role | Key Tools |
|-------|------|-----------|
| **Theme Agent** | Brand & Style Director | ColorPaletteGenerator, FontPairingFinder, LayoutZoneDefiner |
| **Structure Agent** | Content Strategist | ContentParser, RelationshipAnalyzer, HierarchyDetector |
| **Layout Engine** | Master Artisan | LayoutPatternGenerator, GridPositionCalculator, LayoutValidator |

## Key Models

### Input
```python
class LayoutGenerationRequest:
    slide: Slide                          # Slide content
    user_context: Dict[str, Any]          # Brand, industry, preferences
    presentation_context: Dict[str, Any]  # Tone, audience, duration
    layout_config: LayoutEngineConfig     # Optional configuration
```

### Output
```python
class LayoutGenerationResult:
    slide_id: str                    # Slide identifier
    layout: MVPLayout                # Container positions
    theme: ThemeDefinition           # Design tokens
    manifest: ContainerManifest      # Semantic analysis
    generation_metrics: Dict         # Performance metrics
    success: bool                    # Success status
    error_message: Optional[str]     # Error details if failed
```

### Core Components
```python
# Design tokens (W3C format)
class DesignTokens:
    colors: Dict[str, ColorToken]
    typography: Dict[str, TypographyToken]
    spacing: Dict[str, DimensionToken]

# Semantic container
class SemanticContainer:
    id: str
    role: ContainerRole              # HEADLINE, KEY_TAKEAWAY, etc.
    content: str
    importance: ContentImportance    # CRITICAL, HIGH, MEDIUM, LOW
    hierarchy_level: int            # 1-5

# Layout container
class MVPContainer:
    id: str
    type: str                       # text, image, chart, etc.
    position: GridPosition          # leftInset, topInset, width, height
    content: ContainerContent       # text, style, metadata
```

## Common Operations

### Generate Single Layout
```python
result = await orchestrator.generate_layout(request)
if result.success:
    print(f"Generated layout with {len(result.layout.containers)} containers")
```

### Batch Generation
```python
results = await orchestrator.generate_batch(
    slides=slides,
    user_context=context,
    presentation_context=pres_context
)
```

### Analyze Layout Quality
```python
quality = await orchestrator.layout_engine.analyze_layout_quality(layout)
print(f"Balance: {quality['balance_score']:.2f}")
print(f"Valid: {quality['is_valid']}")
```

### Refine Layout
```python
refined = await orchestrator.refine_layout(
    slide_id=slide_id,
    current_layout=layout,
    feedback={"white_space_min": 0.4}
)
```

## Grid System Rules

- **Grid**: 160×90 units
- **Margins**: Minimum 8 units
- **Gutters**: 4 units between containers
- **Positions**: All integers
- **White Space**: 30-50% target

## Container Roles

| Role | Description | Visual Weight |
|------|-------------|---------------|
| HEADLINE | Main title | High (0.8-1.0) |
| KEY_TAKEAWAY | Primary message | High (0.7-0.9) |
| MAIN_POINT | Core content | Medium (0.5-0.7) |
| SUPPORTING_EVIDENCE | Data, examples | Medium (0.4-0.6) |
| VISUAL_ELEMENT | Images, charts | High (0.6-0.8) |
| CONTEXT | Background info | Low (0.2-0.4) |

## Layout Patterns

| Pattern | Best For | Description |
|---------|----------|-------------|
| golden_ratio | 2-3 containers, visual emphasis | 61.8% / 38.2% split |
| rule_of_thirds | 3 containers, balanced | Equal thirds division |
| f_pattern | Text-heavy, hierarchical | Natural reading flow |
| z_pattern | 4 containers, balanced | Diagonal visual flow |
| symmetrical | Formal presentations | Centered alignment |

## Configuration Options

```python
class LayoutEngineConfig:
    max_iterations: int = 5          # Refinement attempts
    white_space_min: float = 0.3     # Minimum white space
    white_space_max: float = 0.5     # Maximum white space
    balance_threshold: float = 0.7   # Minimum balance score
    enable_ai_refinement: bool = True
```

## Error Handling

```python
try:
    result = await orchestrator.generate_layout(request)
    if not result.success:
        # Use fallback
        print(f"Generation failed: {result.error_message}")
        layout = result.layout  # Still contains fallback
except Exception as e:
    print(f"Critical error: {e}")
```

## Best Practices

1. **Provide Context**: Include brand and audience info for better themes
2. **Use Batch Mode**: Process multiple slides together for consistency
3. **Check Metrics**: Monitor balance scores and white space ratios
4. **Handle Failures**: Always check `result.success` before using
5. **Cache Themes**: Reuse themes across similar presentations

## Common Issues

| Issue | Solution |
|-------|----------|
| No API key | Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` |
| Layout too dense | Increase `white_space_min` in config |
| Poor balance | Check container visual weights |
| Slow generation | Reduce `max_iterations` or use cache |

## Testing

```bash
# Run integration tests
python test/test_layout_architect_three_agents.py

# Test specific slide
python -c "
from test_utils import test_slide
asyncio.run(test_slide('path/to/slide.json'))
"
```