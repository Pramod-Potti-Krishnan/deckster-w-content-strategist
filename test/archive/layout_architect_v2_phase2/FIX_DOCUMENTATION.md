# Layout Architect Test Suite Fix Documentation

## Overview
This document describes all the fixes applied to the Layout Architect test suite to resolve test failures and match the current agent implementations.

## Issues Identified and Fixed

### 1. TypographyToken Validation Errors

**Problem:**
```python
# Incorrect - causing validation errors
TypographyToken(
    fontFamily="Inter",  # String instead of TokenValue
    fontSize=16,         # Integer instead of TokenValue
)
```

**Solution:**
```python
# Correct - using TokenValue objects
TypographyToken(
    fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
    fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE),
    fontWeight=TokenValue(value=400, type=TokenType.FONT_WEIGHT),
    lineHeight=TokenValue(value=1.6, type=TokenType.LINE_HEIGHT)
)
```

**Files Fixed:**
- `test_synthetic_data.py`: Updated `generate_theme()` method to use proper TokenValue objects

### 2. Agent API Mismatches

**Problem:**
Tests were calling agent methods with incorrect parameters:
```python
# Incorrect
theme = await theme_agent.generate_theme(
    slide_type="content_heavy",
    user_context={...}
)
```

**Solution:**
```python
# Correct
theme = await theme_agent.generate_theme(
    strawman=strawman,  # PresentationStrawman object
    session_id="test_session_001",
    brand_guidelines={...}
)
```

**Files Fixed:**
- `test_agents_individual.py`: Updated all agent method calls to match actual signatures

### 3. Tool Method Call Issues

**Problem:**
Tests were trying to call tools as async functions with dictionaries:
```python
# Incorrect
result = await font_pairing_tool({"context": "professional"})
```

**Solution:**
For testing, we need to directly instantiate and call the tool classes:
```python
# Correct
finder = FontPairingFinder()
result = finder.find_pairing(
    FontPairingInput(
        context="professional",
        industry="finance",
        preferences={"serif": True}
    )
)
```

**Files Fixed:**
- `test_agents_individual.py`: Updated all tool tests to use direct class instantiation

### 4. Enum Value Access Issues

**Problem:**
Tests were using string values instead of proper enum members:
```python
# Incorrect
assert "headline" in roles
assert manifest.content_flow.value == "linear"
```

**Solution:**
```python
# Correct
assert ContainerRole.HEADLINE in roles
assert manifest.content_flow == ContentFlow.LINEAR
```

**Files Fixed:**
- `test_agents_individual.py`: Updated all enum comparisons

### 5. Missing Imports

**Problem:**
Required enums and types were not imported.

**Solution:**
Added necessary imports:
```python
from src.agents.layout_architect import (
    ContainerRole, ContentImportance, ContentFlow
)
```

### 6. ThemeDefinition Structure Updates

**Problem:**
ThemeDefinition structure changed from using `tokens` to `design_tokens`.

**Solution:**
Updated all references:
```python
# Old
theme.tokens.colors["primary"]

# New
theme.design_tokens.colors["primary"]
```

### 7. Invalid Enum Values

**Problem:**
Tests were checking for enum values that don't exist (e.g., "dashboard" for ContentFlow).

**Solution:**
Updated to use valid enum values:
```python
# Changed from
assert manifest.content_flow in ["dashboard", "radial"]

# To
assert manifest.content_flow in [ContentFlow.MATRIX, ContentFlow.RADIAL]
```

## Summary of Changes

### test_synthetic_data.py
1. Added TokenValue and TokenType imports
2. Updated all token creation to use TokenValue objects
3. Fixed ThemeDefinition structure to use design_tokens
4. Updated layout templates to use proper dictionary structure

### test_agents_individual.py
1. Added necessary enum imports
2. Fixed all agent method calls to use correct signatures
3. Updated tool tests to use direct class instantiation
4. Fixed all enum value comparisons
5. Removed calls to non-existent methods
6. Updated assertions to match actual return types

## Running the Tests

With all fixes applied, you can now run the tests:

```bash
# Run all Layout Architect tests
pytest test/layout_architect_v2_phase2/ -v

# Run individual agent tests
pytest test/layout_architect_v2_phase2/test_agents_individual.py -v

# Run specific test
pytest test/layout_architect_v2_phase2/test_agents_individual.py::TestThemeAgent::test_theme_generation_professional -v
```

## Key Learnings

1. **Always verify API signatures**: The test suite was written for an older version of the agents. Always check the actual implementation.

2. **Understand tool wrapping**: PydanticAI tools are wrapped with Tool() and return dictionaries when called through the agent, but for direct testing, use the underlying classes.

3. **Use proper type objects**: W3C Design Tokens require specific type objects (TokenValue) rather than plain values.

4. **Check enum values**: Always verify that enum values exist before using them in tests.

5. **Environment variables**: Ensure GEMINI_API_KEY is set from GOOGLE_API_KEY if needed.

## Next Steps

If you encounter any remaining test failures:

1. Check the error message carefully
2. Verify the actual implementation of the method/class being tested
3. Ensure all required imports are present
4. Check that test data matches expected formats
5. Verify environment variables are loaded correctly