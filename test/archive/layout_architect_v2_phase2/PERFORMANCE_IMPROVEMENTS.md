# Layout Architect Performance Improvements

## Summary of Changes

This document outlines the performance improvements made to the Layout Architect testing framework to address hanging tests and improve overall test execution speed.

## Key Issues Addressed

1. **Hanging Tests**: The `test_theme_generation_by_industry` test was hanging indefinitely
2. **Model Availability**: `gemini-2.5-flash` was not available, causing failures
3. **No Timeouts**: Tests could run forever without proper timeout controls
4. **No Performance Tracking**: No visibility into which tests were slow

## Implemented Solutions

### 1. Timeout Wrapper Implementation
- Added `async_timeout` decorator to problematic tests
- Added `call_agent_with_timeout` helper for agent method calls
- Set 120-second timeout for industry-specific theme generation tests
- Individual agent calls have 60-second timeouts

### 2. Model Configuration Updates
- Changed default model from `gemini-2.5-flash` to `gemini-1.5-flash`
- Implemented automatic model fallback mechanism
- Added support for `LAYOUT_ARCHITECT_MODEL` environment variable
- Fallback order: `gemini-1.5-flash` → `gemini-1.5-pro` → `gemini-1.0-pro` → `gemini-pro`

### 3. Test Performance Markers
- Added `@pytest.mark.slow` to tests that typically take > 30 seconds
- Marked tests: theme generation, layout generation, iterative refinement, e2e tests
- Can now run quick tests only: `pytest -m "not slow"`

### 4. Enhanced pytest.ini Configuration
- Default timeout: 30 seconds
- Slow tests: 120 seconds
- E2E tests: 180 seconds
- Added `--durations=10` to show slowest tests
- Test profiles for different scenarios

### 5. Diagnostic Tools
- Pre-test checks for API keys and model availability
- Performance monitoring with automatic baseline saving
- Diagnostic output before test session starts
- Automatic slow test detection (> 10 seconds)

### 6. Model Utilities
- `create_model_with_fallback()`: Automatically tries multiple models
- `check_model_availability()`: Verifies model access
- `get_available_models()`: Lists all accessible models
- Environment variable support for model override

## How to Use

### Running Tests Efficiently

```bash
# Run all tests except slow ones (fastest)
pytest -m "not slow"

# Run only quick tests
pytest -m "quick"

# Run with specific timeout
pytest --timeout=60

# Run and see performance report
pytest --durations=10

# Run diagnostics only
python test_diagnostics.py
```

### Environment Variables

```bash
# Override default model
export LAYOUT_ARCHITECT_MODEL=gemini-1.5-pro

# Use either API key
export GOOGLE_API_KEY=your-key
# or
export GEMINI_API_KEY=your-key
```

### Debugging Hanging Tests

1. Check model availability:
   ```python
   python test_diagnostics.py
   ```

2. Run specific test with timeout:
   ```bash
   pytest test_agents_individual.py::TestThemeAgent::test_theme_generation_by_industry -v --timeout=30
   ```

3. View performance baseline:
   ```bash
   ls performance_baseline_*.json
   ```

## Performance Guidelines

1. **Agent Calls**: Always use timeout wrappers for external API calls
2. **Test Duration**: 
   - Unit tests: < 10 seconds
   - Integration tests: < 30 seconds
   - E2E tests: < 180 seconds
3. **Model Selection**: Use fastest available model for tests
4. **Parallel Execution**: Tests are independent and can run in parallel

## Next Steps for Further Optimization

1. **Caching**: Implement response caching for repeated API calls
2. **Mock Mode**: Add mock responses for faster unit testing
3. **Parallel Execution**: Use `pytest-xdist` for parallel test runs
4. **Batch Processing**: Group similar API calls to reduce overhead
5. **Local Models**: Consider using local models for CI/CD pipelines

## Monitoring Test Performance

After each test run, a performance baseline is saved with:
- Test names and durations
- Min/max/average times
- Timestamp of the run

Use this data to:
- Identify performance regressions
- Track improvements over time
- Set realistic timeout values