"""
Root-level pytest configuration for the Deckster project.

This file contains shared configuration and fixtures for all tests.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure pytest-asyncio plugin
pytest_plugins = ('pytest_asyncio',)

# Optional: Add common fixtures or configuration here
import pytest

@pytest.fixture(scope="session")
def project_root_dir():
    """Return the project root directory."""
    return project_root

# Configure asyncio for all tests
import asyncio

@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for the test session."""
    if sys.platform == "win32":
        # Windows requires special handling
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.get_event_loop_policy()