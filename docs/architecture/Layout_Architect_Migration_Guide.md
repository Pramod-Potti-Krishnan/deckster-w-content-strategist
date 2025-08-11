# Layout Architect Migration Guide: MVP to Three-Agent Architecture

## Overview

This guide helps migrate from the original Layout Architect MVP to the new three-agent architecture. The new system provides more intelligent, flexible, and higher-quality layout generation.

## Key Differences

### Old MVP Architecture
- Single monolithic agent (`LayoutArchitectMVP`)
- Rule-based layout decisions
- Hard-coded patterns and positions
- Limited adaptability

### New Three-Agent Architecture
- Three specialized agents (Theme, Structure, Layout Engine)
- AI-powered decision making
- Iterative refinement with validation
- Highly adaptable to content types

## Migration Steps

### 1. Update Imports

**Old:**
```python
from src.agents.layout_architect import LayoutArchitectMVP
from src.agents.layout_architect.models import LayoutConfig
```

**New:**
```python
from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest,
    LayoutGenerationResult
)
```

### 2. Replace Agent Initialization

**Old:**
```python
layout_architect = LayoutArchitectMVP(
    config=LayoutConfig(),
    session_manager=session_manager
)
```

**New:**
```python
orchestrator = LayoutArchitectOrchestrator(
    theme_model="gemini-1.5-pro",
    structure_model="gemini-1.5-pro",
    layout_model="gemini-1.5-pro"
)
```

### 3. Update Layout Generation Calls

**Old:**
```python
result = await layout_architect.process_approved_strawman(
    session_id=session_id,
    user_id=user_id,
    strawman=strawman
)

theme = result['theme']
layouts = result['layouts']
```

**New:**
```python
request = LayoutGenerationRequest(
    slide=slide,
    user_context={
        "brand": "YourBrand",
        "industry": "YourIndustry"
    },
    presentation_context={
        "tone": "professional",
        "audience": "executives"
    }
)

result = await orchestrator.generate_layout(request)

theme = result.theme
layout = result.layout
manifest = result.manifest  # New: semantic analysis
```

### 4. Handle Batch Processing

**Old:**
```python
# Process strawman with multiple slides
result = await layout_architect.process_approved_strawman(
    session_id=session_id,
    user_id=user_id,
    strawman=strawman_with_slides
)
```

**New:**
```python
# Process multiple slides
results = await orchestrator.generate_batch(
    slides=slides,
    user_context=user_context,
    presentation_context=presentation_context
)

for result in results:
    if result.success:
        process_layout(result.layout)
```

### 5. Update WebSocket Integration

**Old:**
```python
# Direct integration in LayoutArchitectMVP
await self._send_theme_update(theme_result)
await self._send_slide_update(slide_layouts)
```

**New:**
```python
# Handle in your WebSocket layer
if result.success:
    await websocket_handler.send_message({
        "type": "theme_update",
        "payload": {
            "theme_name": result.theme.name,
            "theme_config": result.theme.tokens.model_dump()
        }
    })
    
    await websocket_handler.send_message({
        "type": "slide_update",
        "payload": {
            "slides": [{
                "slide_id": result.layout.slide_id,
                "layout": result.layout.model_dump()
            }]
        }
    })
```

### 6. Configuration Updates

**Old:**
```python
config = LayoutConfig(
    enable_ai_structure=True,
    max_containers_per_slide=8
)
```

**New:**
```python
from src.agents.layout_architect import LayoutEngineConfig

config = LayoutEngineConfig(
    enable_ai_refinement=True,
    max_iterations=5,
    white_space_min=0.3,
    white_space_max=0.5,
    balance_threshold=0.7
)

request = LayoutGenerationRequest(
    slide=slide,
    layout_config=config
)
```

## New Features Available

### 1. Semantic Analysis
```python
# Access semantic understanding of content
manifest = result.manifest
print(f"Primary message: {manifest.primary_message}")
print(f"Content flow: {manifest.content_flow}")
print(f"Complexity: {manifest.complexity_score}")
```

### 2. Design Tokens
```python
# Access W3C format design tokens
tokens = result.theme.tokens
primary_color = tokens.colors['primary']['value']
heading_font = tokens.typography['heading']['fontFamily']
```

### 3. Layout Quality Metrics
```python
# Analyze layout quality
quality = await orchestrator.layout_engine.analyze_layout_quality(
    result.layout
)
print(f"Balance score: {quality['balance_score']}")
print(f"Center of mass: {quality['center_of_mass']}")
```

### 4. Refinement Capability
```python
# Refine existing layout based on feedback
refined_result = await orchestrator.refine_layout(
    slide_id=slide_id,
    current_layout=current_layout,
    feedback={
        "requirements": {
            "white_space_min": 0.4,
            "emphasis": "visual"
        }
    }
)
```

## Backward Compatibility

The old `LayoutArchitectMVP` is still available for backward compatibility:

```python
# Still works but deprecated
from src.agents.layout_architect import LayoutArchitectMVP
```

However, we strongly recommend migrating to the new architecture for:
- Better layout quality
- More intelligent decisions
- Greater flexibility
- Ongoing support and improvements

## Testing Your Migration

Use the provided test suite to verify your migration:

```bash
# Run new integration tests
python test/test_layout_architect_three_agents.py

# Compare old vs new output
python test/compare_layout_outputs.py
```

## Common Issues and Solutions

### Issue 1: Different Output Format
**Problem**: New architecture returns different model structure
**Solution**: Update your code to use the new model fields (see examples above)

### Issue 2: API Key Requirements
**Problem**: New agents require Gemini API access
**Solution**: Ensure `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set in environment

### Issue 3: Increased Latency
**Problem**: Three agents may take longer than single MVP
**Solution**: Use batch processing and consider caching themes

## Support

For migration assistance:
1. Check the integration tests for examples
2. Review the architecture documentation
3. Use the fallback mechanisms for critical paths

## Conclusion

The new three-agent architecture provides significant improvements in layout quality and flexibility. While migration requires some code changes, the benefits include:

- More intelligent layout decisions
- Better visual balance and aesthetics
- Semantic understanding of content
- Iterative refinement capabilities
- Standards-based design tokens

We recommend migrating incrementally, starting with non-critical slides and expanding as you verify the improvements.