# Layout Architect v2 Phase 2 Test Run Guide

## Environment Setup

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Ensure environment variables are set**:
   - The tests require `GOOGLE_API_KEY` in your `.env` file
   - Tests automatically convert this to `GEMINI_API_KEY` for the agents

## Running Tests

### All Tests
```bash
pytest test/layout_architect_v2_phase2/ -v
```

### Individual Test Categories

1. **Theme Agent Tests**:
   ```bash
   pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent -v
   ```

2. **Structure Agent Tests**:
   ```bash
   pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestStructureAgent -v
   ```

3. **Layout Engine Tests**:
   ```bash
   pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestLayoutEngine -v
   ```

4. **Tool Tests Only** (faster):
   ```bash
   pytest test/layout_architect_v2_phase2/test_agents_individual.py -v -k "tool"
   ```

5. **Synthetic Data Tests**:
   ```bash
   pytest test/layout_architect_v2_phase2/test_synthetic_data.py -v
   ```

6. **Integration Tests**:
   ```bash
   pytest test/layout_architect_v2_phase2/test_integration.py -v
   ```

## Known Issues and Solutions

### 1. Test Timeouts
Some tests may timeout when using gemini-2.5-flash model due to API response times.

**Solution**: Run individual tests or increase timeout:
```bash
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v --timeout=120
```

### 2. API Key Issues
If you see "Set the GEMINI_API_KEY environment variable":
- Ensure `GOOGLE_API_KEY` is set in your `.env` file
- The tests automatically convert this to `GEMINI_API_KEY`

### 3. Import Errors
If you encounter import errors:
- Ensure you're in the project root directory
- Activate the virtual environment
- The tests add the project root to sys.path automatically

### 4. Slow Test Execution
The gemini-2.5-flash model can be slower than previous versions.

**Solutions**:
- Run specific tests instead of the full suite
- Use the diagnostic tools to check API connectivity:
  ```bash
  python test/layout_architect_v2_phase2/test_api_connectivity.py
  python test/layout_architect_v2_phase2/test_model_fallback.py
  ```

## Test Structure

### Individual Agent Tests (`test_agents_individual.py`)
- Tests each agent in isolation with synthetic inputs
- Includes tool tests that run without AI calls (faster)
- Tests different scenarios (professional, casual, industries)

### Synthetic Data Tests (`test_synthetic_data.py`)
- Tests the synthetic data generation utilities
- Validates data structures and enums
- Quick to run, no AI calls

### Integration Tests (`test_integration.py`)
- Tests the full three-agent pipeline
- Requires all agents to work together
- Slowest tests due to multiple AI calls

### Diagnostic Tools
- `test_api_connectivity.py`: Tests Gemini API connectivity
- `test_model_fallback.py`: Checks available models
- `test_structure_diagnostic.py`: Diagnoses structure agent issues

## Performance Tips

1. **Run tool tests first** - they're fastest and don't require AI:
   ```bash
   pytest test/layout_architect_v2_phase2/ -v -k "tool"
   ```

2. **Use verbose output** to see progress:
   ```bash
   pytest test/layout_architect_v2_phase2/ -v -s
   ```

3. **Run in parallel** (if pytest-xdist is installed):
   ```bash
   pytest test/layout_architect_v2_phase2/ -n auto
   ```

## Expected Test Results

As of the latest update:
- Theme Agent tests: All passing
- Structure Agent tests: Tool tests pass, agent tests may timeout
- Layout Engine tests: May timeout due to iterative workflow
- Synthetic data tests: All passing
- Integration tests: May timeout due to multiple AI calls

## Debugging Failed Tests

1. **Check API connectivity**:
   ```bash
   python test/layout_architect_v2_phase2/test_api_connectivity.py
   ```

2. **Run with debug output**:
   ```bash
   pytest test/layout_architect_v2_phase2/failing_test.py -v -s --log-cli-level=DEBUG
   ```

3. **Check for Dict[str, Any] warnings**:
   - These indicate fields that Gemini can't process properly
   - The agents have been updated to use structured types instead