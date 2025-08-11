# Diagnosing Test Hanging Issues

## Quick Diagnostics

Run these commands to diagnose the issue:

### 1. Test API Connectivity
```bash
python test/layout_architect_v2_phase2/test_api_connectivity.py
```

This will test different Gemini models and show which ones work with your API key.

### 2. Check Model Availability
```bash
python test/layout_architect_v2_phase2/test_model_fallback.py
```

This will show which models are available.

### 3. Run Tests with Timeout
```bash
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v --timeout=30
```

This will timeout after 30 seconds if the test hangs.

### 4. Run with Debug Output
```bash
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v -s --log-cli-level=DEBUG
```

This will show more detailed output.

## Common Issues and Solutions

### 1. **API Key Issues**
- Check if `GOOGLE_API_KEY` or `GEMINI_API_KEY` is set in `.env`
- Verify the key is valid and has access to the models

### 2. **Model Availability**
- `gemini-2.5-flash` might not be available in all regions or for all accounts
- Try falling back to `gemini-1.5-flash` or `gemini-1.5-pro`

### 3. **Rate Limiting**
- If running many tests quickly, you might hit rate limits
- Add delays between tests or reduce parallel execution

### 4. **Network Issues**
- Check internet connectivity
- Try using a VPN if there are regional restrictions

## Temporary Fix

If `gemini-2.5-flash` is not available, update the agents to use a fallback:

```python
# In each agent's __init__ method:
def __init__(self, model_name: str = "gemini-1.5-flash"):  # Fallback to 1.5
```

## Running Individual Tests

To isolate the issue, run tests one by one:

```bash
# Test 1
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v

# Test 2
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_casual -v

# Test 3 (the one that hangs)
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_by_industry -v -k healthcare
```

## Check for Errors in Agent Implementation

The hanging might be due to:
1. Infinite loops in agent tools
2. Synchronous blocking calls in async functions
3. Missing error handling in API calls

## Environment Variables

Make sure these are set:
- `GOOGLE_API_KEY` or `GEMINI_API_KEY`
- `LOG_LEVEL=DEBUG` (for more output)

## Next Steps

1. Run the diagnostic scripts
2. Check which model works
3. Update the agent default models if needed
4. Add proper timeouts to prevent hanging