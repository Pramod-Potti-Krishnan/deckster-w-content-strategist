#!/usr/bin/env python3
"""
Basic test to check imports and initialization.
"""

import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("✓ Dotenv loaded")

# Import analytics
from src.agents.analytics_agent_v2 import create_analytics_v2
print("✓ Analytics imported")

# Import models
from src.agents.analytics_utils_v2.models import ChartType, AnalyticsRequest
print("✓ Models imported")

# Import conductor
from src.agents.analytics_utils_v2.conductor import AnalyticsConductor
print("✓ Conductor imported")

async def test_basic():
    """Test basic initialization."""
    print("\nTesting basic initialization...")
    
    try:
        # Create conductor
        conductor = AnalyticsConductor()
        print("✓ Conductor created")
        
        # Create a simple request
        request = AnalyticsRequest(
            content="Test bar chart",
            use_synthetic_data=True
        )
        print("✓ Request created")
        
        # Try to select a chart (this might hang)
        print("Attempting chart selection...")
        plan = await conductor.select_chart(request)
        print(f"✓ Chart selected: {plan.chart_type}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting basic test...")
    asyncio.run(test_basic())
    print("Test complete!")