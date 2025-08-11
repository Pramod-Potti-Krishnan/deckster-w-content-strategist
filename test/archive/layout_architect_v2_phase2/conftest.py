"""
Pytest configuration for Layout Architect v2 Phase 2 tests.

Provides shared fixtures and configuration for all test modules.
"""

import pytest
import asyncio
import os
import sys
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import diagnostics
try:
    from .test_diagnostics import diagnostics, run_pre_test_checks
except ImportError:
    # Fallback if running from different directory
    import os
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from test_diagnostics import diagnostics, run_pre_test_checks

# Load environment variables from .env file
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")

# Also set GEMINI_API_KEY from GOOGLE_API_KEY if needed
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    print("Set GEMINI_API_KEY from GOOGLE_API_KEY")

# Check if API key exists
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("⚠️  WARNING: No API key found! Tests will fail.")
else:
    print(f"✅ API key found (starts with: {api_key[:10]}...)")

# pytest-asyncio is configured in root conftest.py

# Set default timeout for async operations
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy() if sys.platform == 'win32' else None)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_output_dir():
    """Create and return test output directory."""
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "output",
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


@pytest.fixture
def api_keys_available():
    """Check if API keys are available."""
    google_key = os.getenv("GOOGLE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    return bool(google_key or gemini_key)


@pytest.fixture
def skip_without_api_keys(api_keys_available):
    """Skip test if API keys are not available."""
    if not api_keys_available:
        pytest.skip("API keys not available")


# Test configuration
@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "api_timeout": 30,
        "max_retries": 3,
        "enable_visual_output": True,
        "industries": ["healthcare", "finance", "education", "technology"],
        "slide_types": ["title_slide", "content_heavy", "visual_heavy", "data_driven"],
        "model_fallback": ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]  # Fallback models
    }


# Shared test data
@pytest.fixture
def sample_slide_data():
    """Provide sample slide data for testing."""
    return {
        "title_slide": {
            "slide_id": "test_title_001",
            "slide_number": 1,
            "title": "Test Presentation",
            "slide_type": "title_slide",
            "key_points": ["Welcome to the test"],
            "narrative": "Opening slide"
        },
        "content_slide": {
            "slide_id": "test_content_001",
            "slide_number": 2,
            "title": "Key Information",
            "slide_type": "content_heavy",
            "key_points": [
                "First important point",
                "Second important point",
                "Third important point"
            ],
            "narrative": "Detailed content explanation"
        },
        "visual_slide": {
            "slide_id": "test_visual_001",
            "slide_number": 3,
            "title": "Visual Overview",
            "slide_type": "visual_heavy",
            "key_points": ["Visual representation of data"],
            "visuals_needed": "Infographic showing process flow",
            "narrative": "Visual explanation"
        },
        "data_slide": {
            "slide_id": "test_data_001",
            "slide_number": 4,
            "title": "Performance Metrics",
            "slide_type": "data_driven",
            "key_points": [
                "Revenue: $10M",
                "Growth: 25%",
                "Users: 50K"
            ],
            "analytics_needed": "Charts and KPIs",
            "narrative": "Data analysis"
        }
    }


# Hook to run diagnostics before test session
def pytest_sessionstart(session):
    """Run diagnostics before test session starts."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(run_pre_test_checks())
        if not results.get('any_api_key'):
            pytest.exit("No API keys found. Please set GOOGLE_API_KEY or GEMINI_API_KEY")
    finally:
        loop.close()

# Performance tracking
@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    # Use the global diagnostics instance
    return diagnostics
    
@pytest.fixture
def performance_tracker_legacy():
    """Legacy performance tracker for compatibility."""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
        
        def start(self, operation: str):
            """Start timing an operation."""
            self.start_times[operation] = datetime.now()
        
        def end(self, operation: str) -> float:
            """End timing and return duration."""
            if operation in self.start_times:
                duration = (datetime.now() - self.start_times[operation]).total_seconds()
                if operation not in self.metrics:
                    self.metrics[operation] = []
                self.metrics[operation].append(duration)
                del self.start_times[operation]
                return duration
            return 0.0
        
        def get_average(self, operation: str) -> float:
            """Get average duration for an operation."""
            if operation in self.metrics and self.metrics[operation]:
                return sum(self.metrics[operation]) / len(self.metrics[operation])
            return 0.0
        
        def get_report(self) -> Dict[str, Any]:
            """Get performance report."""
            report = {}
            for operation, durations in self.metrics.items():
                report[operation] = {
                    "count": len(durations),
                    "total": sum(durations),
                    "average": sum(durations) / len(durations) if durations else 0,
                    "min": min(durations) if durations else 0,
                    "max": max(durations) if durations else 0
                }
            return report
    
    return PerformanceTracker()


# Pytest marks
def pytest_configure(config):
    """Configure custom pytest marks."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require API access"
    )


# Test result formatting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add custom test result formatting."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        if hasattr(item, "performance_metrics"):
            # Add performance metrics to report
            report.performance = item.performance_metrics


# Performance monitoring hooks
@pytest.fixture(autouse=True)
def monitor_test_performance(request, performance_tracker):
    """Automatically monitor test performance."""
    test_name = request.node.name
    performance_tracker.start_timing(test_name)
    
    yield
    
    duration = performance_tracker.end_timing(test_name)
    if duration > 10:  # Log slow tests
        print(f"\n⚠️  Slow test: {test_name} took {duration:.2f}s")

# Hook to save performance baseline after session
def pytest_sessionfinish(session, exitstatus):
    """Save performance baseline after test session."""
    if hasattr(diagnostics, 'performance_data') and diagnostics.performance_data:
        diagnostics.save_performance_baseline()
        print("\n📊 Performance baseline saved")

# Cleanup
@pytest.fixture(autouse=True)
def cleanup_test_files(request, test_output_dir):
    """Clean up test files after each test."""
    def cleanup():
        # Only clean up if requested
        if hasattr(request.node, "cleanup_files") and request.node.cleanup_files:
            import shutil
            shutil.rmtree(test_output_dir, ignore_errors=True)
    
    request.addfinalizer(cleanup)