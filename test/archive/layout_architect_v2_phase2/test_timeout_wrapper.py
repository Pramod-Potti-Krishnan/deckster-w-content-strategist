"""
Wrapper to add timeouts to async tests.
"""

import asyncio
import functools
from typing import Callable, Any

def async_timeout(seconds: int = 30):
    """
    Decorator to add timeout to async tests.
    
    Usage:
        @async_timeout(20)
        @pytest.mark.asyncio
        async def test_something():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                raise AssertionError(f"Test timed out after {seconds} seconds")
        return wrapper
    return decorator

# Helper function to add timeout to agent calls
async def call_agent_with_timeout(agent_method, *args, timeout=30, **kwargs):
    """Call an agent method with a timeout."""
    try:
        return await asyncio.wait_for(
            agent_method(*args, **kwargs),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise AssertionError(f"Agent call timed out after {timeout} seconds")