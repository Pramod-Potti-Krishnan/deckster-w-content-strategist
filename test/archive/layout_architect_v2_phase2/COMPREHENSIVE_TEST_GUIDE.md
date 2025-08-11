# Comprehensive Test Guide for Layout Architect v2 Phase 2

## Current Test Suite Status

### Working Tests ✅
1. **Tool Tests** - These run without AI calls and are very fast:
   - `test_font_pairing_tool` (Theme Agent)
   - `test_color_palette_generation` (Theme Agent)
   - `test_content_parsing_tool` (Structure Agent)
   - `test_relationship_detection` (Structure Agent)
   - `test_layout_patterns` (Layout Engine)
   - `test_visual_balance_scoring` (Layout Engine)
   - `test_layout_validation` (Layout Engine)

2. **Synthetic Data Tests** - Quick validation tests:
   - All tests in `test_synthetic_data.py`
   - These validate data structures and enums

3. **Import Tests** - Basic sanity checks:
   - `test_imports.py` - Verifies all modules can be imported

### Tests with Known Issues ⚠️
1. **Agent Integration Tests** - May timeout due to multiple AI calls:
   - Theme generation tests (10-20s typical)
   - Structure analysis tests (10-15s typical)
   - Layout generation tests (15-30s due to iterative refinement)
   - Full pipeline tests (30-60s)

2. **Common Timeout Scenarios**:
   - `test_iterative_refinement` - Layout Engine's multiple iterations
   - `test_end_to_end_performance` - Full pipeline with all agents
   - Integration tests in `test_agents_integrated.py`

## Recommended Test Running Order

### 1. Quick Verification (< 1 minute)
```bash
# Start with imports and setup verification
pytest test/layout_architect_v2_phase2/test_imports.py -v
pytest test/layout_architect_v2_phase2/test_setup_verification.py -v

# Run synthetic data tests
pytest test/layout_architect_v2_phase2/test_synthetic_data.py -v
```

### 2. Tool Tests Only (< 2 minutes)
```bash
# Run all tool tests - these are fast and don't use AI
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v -k "tool"
```

### 3. Individual Agent Tests (5-10 minutes each)
```bash
# Theme Agent tests
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent -v -s

# Structure Agent tests
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestStructureAgent -v -s

# Layout Engine tests
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestLayoutEngine -v -s
```

### 4. Performance Tests (with extended timeout)
```bash
# Run with custom timeout
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestPerformanceMetrics -v --timeout=120
```

### 5. Full Test Suite (30-60 minutes)
```bash
# Run everything with extended timeout
pytest test/layout_architect_v2_phase2/ -v --timeout=120
```

## Specific Test Commands

### API Connectivity Check
```bash
# Verify Gemini API is working
python test/layout_architect_v2_phase2/test_api_connectivity.py
```

### Model Availability Check
```bash
# Check which models are available
python test/layout_architect_v2_phase2/test_model_fallback.py
```

### Structure Agent Diagnostics
```bash
# Diagnose structure agent issues
python test/layout_architect_v2_phase2/test_structure_diagnostic.py
```

### Run Specific Test by Name
```bash
# Run tests matching a pattern
pytest test/layout_architect_v2_phase2/ -v -k "professional"
pytest test/layout_architect_v2_phase2/ -v -k "title_slide"
```

### Run with Debug Output
```bash
# See detailed output including print statements
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v -s --log-cli-level=DEBUG
```

## Expected Outcomes

### Successful Test Output
- Tool tests: All should pass within 1-2 seconds each
- Agent tests: May take 10-30 seconds each depending on AI response time
- You'll see output like:
  ```
  ✅ Professional theme generated in 12.34s
  ✅ Title slide analyzed in 8.56s
  ✅ Layout generated in 15.78s
  ```

### Known Timeouts
These tests commonly timeout with gemini-2.0-flash:
1. `test_iterative_refinement` - Multiple layout iterations
2. `test_end_to_end_performance` - Full pipeline test
3. `test_theme_generation_by_industry` - Parameterized tests with multiple runs

## Quick Troubleshooting

### 1. API Key Issues
```bash
# Check if GOOGLE_API_KEY is set
echo $GOOGLE_API_KEY

# The tests automatically convert to GEMINI_API_KEY
# If still issues, try setting both:
export GEMINI_API_KEY=$GOOGLE_API_KEY
```

### 2. Import Errors
```bash
# Ensure you're in project root
pwd  # Should show /home/gmk/Software/deckster.xyz/deckster

# Activate virtual environment
source venv/bin/activate

# Verify Python path
python -c "import sys; print(sys.path)"
```

### 3. Timeout Issues
```bash
# For specific slow tests, run individually with custom timeout
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v --timeout=60

# Or use the timeout wrapper in code
from test_timeout_wrapper import async_timeout
```

### 4. Memory Issues
```bash
# Run tests one at a time if memory is limited
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v -x
```

### 5. Debugging Failed Tests
```bash
# Get more verbose output
pytest test/layout_architect_v2_phase2/failing_test.py -vvv -s

# Run with pdb on failure
pytest test/layout_architect_v2_phase2/failing_test.py --pdb
```

## Performance Tips

### 1. Parallel Execution (if pytest-xdist installed)
```bash
# Run tests in parallel (be careful with API rate limits)
pytest test/layout_architect_v2_phase2/ -n 2
```

### 2. Run Only Changed Tests
```bash
# If using pytest-watch
ptw test/layout_architect_v2_phase2/ -- -v
```

### 3. Skip Slow Tests
```bash
# Mark slow tests with @pytest.mark.slow and skip them
pytest test/layout_architect_v2_phase2/ -v -m "not slow"
```

### 4. Use Test Fixtures Efficiently
The test files use fixtures for agent creation - these are cached per test class, reducing setup time.

## Understanding Test Results

### Tool Test Results
- Should always pass quickly
- Failures indicate code issues, not AI/API issues
- Check for:
  - Correct input/output formats
  - Pattern matching logic
  - Mathematical calculations

### Agent Test Results
- May vary slightly due to AI non-determinism
- Check for:
  - Valid theme generation (fallback themes are OK)
  - Proper container detection (counts may vary)
  - Layout constraints met (white space, margins)

### Integration Test Results
- Most complex, most likely to timeout
- Success criteria:
  - All agents communicate properly
  - Output formats are correct
  - No exceptions raised

## Common Patterns in Test Failures

1. **"Set the GEMINI_API_KEY environment variable"**
   - Solution: Ensure GOOGLE_API_KEY is in .env file

2. **"AttributeError: 'Dict' object has no attribute 'model_dump'"**
   - Solution: Check that objects are proper Pydantic models

3. **"Timeout after X seconds"**
   - Solution: Run test individually with longer timeout

4. **"KeyError" in agent responses**
   - Solution: AI response format may have changed; check tool outputs

5. **Empty or None responses from agents**
   - Solution: Check API connectivity; model may be overloaded

## Quick Test Health Check

Run this sequence to quickly assess test suite health:

```bash
# 1. Check setup (< 10s)
pytest test/layout_architect_v2_phase2/test_imports.py -v

# 2. Check tools (< 30s)
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v -k "tool"

# 3. Check one agent (< 60s)
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v

# If all pass, the test suite is healthy!
```

## Summary

- **Start simple**: Run tool tests first
- **Be patient**: AI tests take time
- **Run individually**: If timeouts occur
- **Check diagnostics**: Use the diagnostic scripts
- **Watch for patterns**: Most failures have known solutions

The test suite is comprehensive but requires patience due to AI response times. Focus on tool tests for quick feedback during development, and run full agent tests before commits.