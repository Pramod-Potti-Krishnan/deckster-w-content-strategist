# Diagram Generation System

## Overview
This system provides intelligent diagram generation with three strategies:
1. **SVG Templates** - Fast, deterministic, perfect quality
2. **Mermaid** - Code-driven, flexible, wide variety
3. **AI Visual** - Creative, artistic, unlimited possibilities

## Architecture

### Integration with Content Agent V7
The system is designed to consume `DiagramContentV4` output from content_agent_v7:

```python
DiagramContentV4:
  pattern: str              # From DIAGRAM_PLAYBOOK
  core_elements: List[Dict] # Diagram elements
  relationships: List[Dict] # Connections
  flow_direction: str       # Layout direction
  visual_hierarchy: List    # Emphasis order
```

### Three Generation Strategies

#### 1. SVG Templates (pydantic_ai)
- Uses pre-built SVG templates
- XML manipulation with pydantic_ai tools
- Best for: pyramids, matrices, funnels
- Speed: < 100ms

#### 2. Mermaid (pydantic_ai + MCP)
- Generates Mermaid.js code
- MCP for rendering (placeholder currently)
- Best for: flowcharts, sequences, Gantt
- Speed: ~500ms

#### 3. AI Visual (Traditional)
- Uses ImageBuildAgent + Imagen 3
- Gemini Vision for text zones
- Best for: honeycomb, networks, artistic
- Speed: 3-5 seconds

## Usage

### From Content Agent
```python
from src.agents.diagram_agent import DiagramBuildAgent

# Content agent output
diagram_content = DiagramContentV4(...)

# Generate diagram
agent = DiagramBuildAgent()
result = await agent.build_diagram_from_spec(
    diagram_spec={
        "pattern": diagram_content.pattern,
        "content": {...},
        "data_points": diagram_content.core_elements
    },
    theme=theme
)
```

### Direct Usage
```python
from src.agents.diagram_agent import DiagramAgent
from src.agents.diagram_utils.models import DiagramRequest

agent = DiagramAgent()
request = DiagramRequest(
    content="...",
    diagram_type="flowchart",
    data_points=[...],
    theme=theme
)
result = await agent.generate_diagram(request)
```

## Testing

Run all tests:
```bash
./run_all_diagram_tests.sh
```

Individual tests:
```bash
python test_diagram_integration.py  # Main integration
python test_svg_from_content.py     # SVG templates
python test_mermaid_from_content.py # Mermaid generation
python test_ai_visual_from_content.py # AI visual
```

## Templates

SVG templates are in `templates/`:
- `pyramid_3_level.svg` - 3-level pyramid
- `matrix_2x2.svg` - 2x2 matrix
- (Add more as needed)

## Key Design Decisions

1. **Hybrid Approach**: pydantic_ai for text/code, traditional for images
2. **Content Agent Integration**: Designed to consume DiagramContentV4
3. **Intelligent Routing**: Conductor agent selects optimal strategy
4. **Fallback Chain**: SVG → Mermaid → AI Visual

## Dependencies

- pydantic_ai: Agent framework
- lxml: SVG manipulation
- Pillow: Image processing
- google-genai: Imagen 3 generation
- google.generativeai: Gemini Vision

## Future Enhancements

1. Add more SVG templates
2. Implement actual MCP server for Mermaid
3. Add caching layer
4. Improve text zone extraction
5. Add more diagram types