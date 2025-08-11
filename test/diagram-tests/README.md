# Diagram Agent Testing Guide

## Overview
The diagram agent system has been reorganized with a comprehensive test suite. The system supports two generation strategies (after removing AI Visual):
1. **SVG Templates** - Fast, deterministic diagram generation with multiple templates
2. **Mermaid** - Code-driven, flexible diagrams

## Test Directory Structure

```
test/diagram-tests/
├── README.md                       # This file
├── run_all_tests.sh               # Master test runner
├── test_output/                   # All test outputs
├── integration/                   # Integration tests (require API keys)
│   ├── test_diagram_integration.py
│   └── test_svg_from_content.py
├── unit/                         # Unit tests (no API keys required)
│   ├── test_diagram_simple.py
│   ├── test_svg_simple.py
│   └── test_svg_templates_simple.py
├── pyramid/                      # Pyramid template specific tests
│   ├── test_pyramid_colors.py
│   ├── test_pyramid_comprehensive.py
│   ├── test_pyramid_direct.py
│   └── test_pyramid_updated.py
└── templates/                    # SVG template tests
    ├── test_all_svg_templates.py
    ├── test_all_svg_templates_comprehensive.py
    ├── test_svg_agent_wrapping.py
    ├── test_svg_color_theming.py
    └── test_swot_fixes.py
```

## Test Categories

### Unit Tests (No API Keys Required)
Located in `unit/` - Test basic functionality without API calls:
- `test_diagram_simple.py` - Basic diagram agent functionality
- `test_svg_simple.py` - SVG generation basics
- `test_svg_templates_simple.py` - Template loading and validation

### Integration Tests (Require API Keys)
Located in `integration/` - Full pipeline testing:
- `test_diagram_integration.py` - Main integration test with all strategies
- `test_svg_from_content.py` - SVG template testing with content

### Template Tests
Located in `templates/` - Comprehensive SVG template testing:
- `test_all_svg_templates_comprehensive.py` - Tests all 10 SVG templates with theming
- `test_svg_agent_wrapping.py` - Text wrapping functionality
- `test_svg_color_theming.py` - Color theme application
- `test_swot_fixes.py` - SWOT matrix specific improvements

### Pyramid Tests
Located in `pyramid/` - Pyramid template specific testing:
- `test_pyramid_comprehensive.py` - Full pyramid testing with all features
- `test_pyramid_colors.py` - Color scheme testing
- `test_pyramid_updated.py` - Tests latest pyramid improvements
- `test_pyramid_direct.py` - Direct template manipulation

## Running Tests

### Quick Start (No API Keys)
```bash
cd test/diagram-tests
python3 unit/test_diagram_simple.py
```

### Run All Tests
```bash
cd test/diagram-tests
./run_all_tests.sh
```

### Run Category-Specific Tests
```bash
# Unit tests only
cd test/diagram-tests
for test in unit/test_*.py; do python3 "$test"; done

# Template tests only
for test in templates/test_*.py; do python3 "$test"; done

# Pyramid tests only
for test in pyramid/test_*.py; do python3 "$test"; done
```

### With API Keys
For integration tests, set your environment variables first:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

Then run integration tests:
```bash
cd test/diagram-tests
python3 integration/test_diagram_integration.py
```

## Test Output Structure

All test outputs are saved in `test_output/` with the following structure:
```
test_output/
├── svg_templates_comprehensive/   # Comprehensive template test outputs
│   ├── pyramid_theme_0.svg
│   ├── pyramid_theme_1.svg
│   ├── funnel_theme_0.svg
│   └── ...
├── diagrams/                     # General diagram outputs
├── mermaid_diagrams/             # Mermaid diagram outputs
└── ...
```

## Available SVG Templates

The system currently supports 10 SVG templates:
1. **pyramid_3_level** - Hierarchical pyramid with light colors
2. **funnel_5_stage** - Sales/conversion funnel
3. **matrix_2x2** - 2x2 decision matrix
4. **timeline_horizontal** - Horizontal timeline
5. **cycle_4_step** - Circular process cycle
6. **venn_2_circle** - Venn diagram
7. **hub_spoke_6** - Hub and spoke model
8. **honeycomb_7** - Honeycomb structure
9. **swot_matrix** - SWOT analysis matrix
10. **process_flow_5** - Process flow diagram

## Recent Improvements

### Pyramid Template
- 25% proportionally larger while maintaining triangular shape
- Light background colors (#fef3c7, #d1fae5, #dbeafe)
- All text in black for consistency
- Improved text wrapping with 18px font size

### SWOT Matrix
- Much lighter background colors for better readability
- Items displayed on separate lines
- Support for up to 4 lines per quadrant

### General Improvements
- Text wrapping with ellipsis for overflow
- Smart color contrast calculation
- Consistent theming across all templates
```

## Key Integration Points

The tests use the exact `DiagramContentV4` format from content_agent_v7:

```python
DiagramContentV4(
    pattern="process_flow",           # From DIAGRAM_PLAYBOOK
    core_elements=[                   # Diagram elements
        {"id": "...", "label": "...", "type": "..."}
    ],
    relationships=[                    # Connections
        {"from": "...", "to": "...", "label": "..."}
    ],
    flow_direction="horizontal",      # Layout direction
    visual_hierarchy=["id1", "id2"]   # Emphasis order
)
```

## Current Status

✅ **Working Without API Keys:**
- Model definitions and validation
- SVG template loading and structure
- Mermaid syntax generation
- Enum types and basic functionality

⚠️ **Requires API Keys:**
- Full integration testing
- Actual diagram generation
- AI visual creation with Imagen 3
- Gemini-based text zone extraction

## Dependencies

### Required for Basic Functionality
- pydantic
- pydantic_ai

### Optional (for Full Features)
- Pillow (PIL) - Image processing
- rembg - Background removal
- google-genai - Imagen 3 generation
- google.generativeai - Gemini Vision

## Next Steps

1. **To run full tests:**
   - Set up API keys for Gemini and Google AI
   - Install optional dependencies: `pip install Pillow google-genai`

2. **To integrate with content_agent_v7:**
   ```python
   from src.agents.diagram_agent import DiagramBuildAgent
   
   diagram_agent = DiagramBuildAgent()
   result = await diagram_agent.build_diagram_from_spec(
       diagram_spec={...},
       theme={...}
   )
   ```

3. **To add more templates:**
   - Create SVG files in `src/agents/diagram_utils/templates/`
   - Update SVGTemplateLibrary in `svg_agent.py`

## Troubleshooting

### "Failed to create any model" Error
- Set `GEMINI_API_KEY` environment variable
- Or use mock/test mode without actual API calls

### "Pillow not installed" Warning
- Install with: `pip install Pillow`
- Only needed for image processing features

### "rembg not installed" Warning
- Install with: `pip install rembg`
- Only needed for background removal features