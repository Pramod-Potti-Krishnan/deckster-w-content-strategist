# Layout Architect v2 Phase 2 Test Suite

Comprehensive testing framework for the three-agent Layout Architect system.

## Overview

This test suite provides thorough testing for:
- Individual agent functionality (Theme, Structure, Layout Engine)
- Integrated pipeline testing
- Director_IN integration and handoff
- Quality metrics and performance
- Edge cases and error handling
- Visual output generation

## Prerequisites

### Server Requirements
**No server needed!** These tests run independently without requiring the main.py server to be running. The tests directly instantiate and test the Layout Architect agents.

### Environment Setup

**IMPORTANT**: See `TEST_RUN_GUIDE.md` for detailed instructions on running tests and handling known issues.

1. **Create and activate a virtual environment** (recommended):
```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

2. **Install dependencies**:
```bash
# Install main project dependencies
pip install -r requirements.txt

# Install test dependencies (option 1: individual)
pip install pytest pytest-asyncio pytest-cov pytest-html

# OR install test dependencies (option 2: from file)
pip install -r test/layout_architect_v2_phase2/requirements-test.txt
```

3. **Set up environment variables**:
```bash
# Create .env file or export directly
export GOOGLE_API_KEY="your-api-key"
# or
export GEMINI_API_KEY="your-api-key"
```

## Test Structure

```
test/layout_architect_v2_phase2/
├── __init__.py                    # Package initialization and utilities
├── conftest.py                    # Pytest configuration and fixtures
├── test_synthetic_data.py         # Synthetic data generators
├── test_agents_individual.py      # Individual agent tests
├── test_agents_integrated.py      # Full pipeline integration tests
├── test_director_integration.py   # Director_IN handoff tests
├── test_quality_metrics.py        # Quality and performance metrics
├── test_edge_cases.py            # Edge case and error handling
├── test_visual_output.py         # HTML preview generation
└── fixtures/                     # Test fixtures and sample data
```

## Running Tests

### Run All Tests
```bash
pytest test/layout_architect_v2_phase2/
```

### Run Specific Test Categories

#### Individual Agent Tests
```bash
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v
```

#### Integration Tests
```bash
pytest test/layout_architect_v2_phase2/test_agents_integrated.py -v
```

#### Director Integration
```bash
pytest test/layout_architect_v2_phase2/test_director_integration.py -v
```

#### Quality Metrics
```bash
pytest test/layout_architect_v2_phase2/test_quality_metrics.py -v
```

#### Edge Cases
```bash
pytest test/layout_architect_v2_phase2/test_edge_cases.py -v
```

### Run with Markers

```bash
# Skip slow tests
pytest test/layout_architect_v2_phase2/ -m "not slow"

# Only integration tests
pytest test/layout_architect_v2_phase2/ -m integration

# Tests requiring API access
pytest test/layout_architect_v2_phase2/ -m requires_api
```

### Generate Reports

#### Coverage Report
```bash
pytest --cov=src.agents.layout_architect test/layout_architect_v2_phase2/ --cov-report=html
```

#### HTML Test Report
```bash
pytest test/layout_architect_v2_phase2/ --html=test_report.html --self-contained-html
```

## Test Modules

### 1. test_synthetic_data.py
Generates realistic test data:
- Industry-specific presentations (healthcare, finance, education, tech)
- Various slide types (title, content-heavy, visual-heavy, data-driven)
- Complete test scenarios with themes and manifests

### 2. test_agents_individual.py
Tests each agent in isolation:
- **Theme Agent**: Color palettes, font pairings, accessibility
- **Structure Agent**: Semantic analysis, relationship detection
- **Layout Engine**: Pattern generation, positioning, validation

### 3. test_agents_integrated.py
Tests the complete pipeline:
- Single slide generation
- Batch processing
- Industry-specific layouts
- Theme consistency
- Performance benchmarking

### 4. test_director_integration.py
Tests integration with Director_IN:
- Strawman approval handoff
- WebSocket message flow
- Session state management
- Real-world presentation scenarios

### 5. test_quality_metrics.py
Measures layout quality:
- Visual balance scoring
- Alignment quality
- Spacing consistency
- Readability scores
- Performance profiling

### 6. test_edge_cases.py
Tests error handling:
- Empty slides
- Overloaded content
- Missing API keys
- Invalid configurations
- Unicode and special characters

### 7. test_visual_output.py
Generates visual previews:
- HTML layout previews
- Side-by-side comparisons
- Visual regression testing

## Visual Output

Generate HTML previews of layouts:

```python
python test/layout_architect_v2_phase2/test_visual_output.py
```

Output files will be in `test/layout_architect_v2_phase2/output/`

## Performance Benchmarks

Expected performance targets:
- Single slide: < 10 seconds
- Batch of 10 slides: < 60 seconds
- Theme generation: < 5 seconds
- Structure analysis: < 5 seconds
- Layout generation: < 10 seconds

## Quality Targets

Minimum quality scores:
- Visual balance: > 0.6
- Alignment score: > 0.7
- White space: 30-50%
- Readability: > 0.6

## Quick Start

```bash
# 1. Set up environment (one-time setup)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-html

# 2. Set API key
export GOOGLE_API_KEY="your-api-key"  # or GEMINI_API_KEY

# 3. Run tests
pytest test/layout_architect_v2_phase2/ -v

# No need to start the server!
```

## Environment Requirements

```bash
# Required environment variables (at least one)
export GOOGLE_API_KEY="your-api-key"
# or
export GEMINI_API_KEY="your-api-key"

# Optional configuration
export LAYOUT_ARCHITECT_MODEL="gemini-2.5-flash"  # Default model
export LAYOUT_ARCHITECT_TEMPERATURE="0.7"

# Load from .env file (alternative)
# Create a .env file in project root with:
# GOOGLE_API_KEY=your-api-key
```

## Debugging

### Verbose Output
```bash
pytest test/layout_architect_v2_phase2/ -v -s
```

### Run Specific Test
```bash
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v
```

### Debug with PDB
```bash
pytest test/layout_architect_v2_phase2/ --pdb
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're running from the project root directory
```bash
cd /path/to/deckster
pytest test/layout_architect_v2_phase2/

# Test imports first
python test/layout_architect_v2_phase2/test_imports.py
```

If you see circular import errors, ensure the virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. **API key errors**: Verify your API key is set
```bash
echo $GOOGLE_API_KEY  # Should show your key (partially)
```

3. **Missing dependencies**: Install all requirements
```bash
pip install -r requirements.txt
pip install -r test/layout_architect_v2_phase2/requirements-test.txt
```

4. **Async errors**: Ensure pytest-asyncio is installed
```bash
pip install pytest-asyncio
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'

- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install -r test/layout_architect_v2_phase2/requirements-test.txt

- name: Run Layout Architect Tests
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    pytest test/layout_architect_v2_phase2/ \
      --cov=src.agents.layout_architect \
      --cov-report=xml \
      --junit-xml=test-results.xml
```

## FAQ

**Q: Do I need to run the main.py server?**
A: No, the tests run independently without the server.

**Q: Can I run tests without API keys?**
A: No, at least one API key (GOOGLE_API_KEY or GEMINI_API_KEY) is required for the AI agents.

**Q: How do I run a single test?**
A: Use pytest's -k flag: `pytest test/layout_architect_v2_phase2/ -k "test_theme_generation"`

**Q: Why are some tests slow?**
A: Tests marked with @pytest.mark.slow make real API calls. Skip them with `-m "not slow"`

## Contributing

When adding new tests:
1. Use appropriate fixtures from `conftest.py`
2. Add docstrings explaining test purpose
3. Use meaningful assertions with messages
4. Mark slow tests with `@pytest.mark.slow`
5. Generate synthetic data using provided generators