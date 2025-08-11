#!/usr/bin/env python
"""
Test Histogram Generation
=========================
Debug histogram data and plotting issues.
"""

import os
import sys
import asyncio
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor
from src.agents.analytics_utils.data_parser import DataParser
from src.agents.analytics_utils.data_synthesizer import DataSynthesizer
from src.agents.analytics_utils.models import AnalyticsRequest, SyntheticDataConfig, ChartType


async def test_histogram():
    """Test histogram generation."""
    
    print("\n" + "="*60)
    print("TESTING HISTOGRAM GENERATION")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "title": "Age Distribution",
            "description": "Customer age distribution: 500 customers with mean age 38, std deviation 12",
            "chart_type": "histogram"
        },
        {
            "title": "Response Time Analysis",
            "description": "Response times in milliseconds: mean 250ms, std 50ms, 1000 samples",
            "chart_type": "histogram"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] Testing: {test_case['title']}")
        print(f"Description: {test_case['description']}")
        print("-" * 40)
        
        # First test data parsing
        parser = DataParser()
        parsed = parser.parse_data_points(test_case['description'])
        
        if parsed:
            print(f"Parsed {len(parsed)} data points:")
            for j, dp in enumerate(parsed[:10]):  # Show first 10
                print(f"  {j+1}. Label: '{dp.label}' | Value: {dp.value}")
            if len(parsed) > 10:
                print(f"  ... and {len(parsed)-10} more")
        else:
            print("No data points parsed from description")
            
        # Test data synthesis
        request = AnalyticsRequest(
            title=test_case['title'],
            description=test_case['description'],
            data_context=test_case['description']
        )
        
        config = SyntheticDataConfig()
        synthesizer = DataSynthesizer()
        
        data_points, desc, insights = await synthesizer.generate_synthetic_data(
            request, config, ChartType.HISTOGRAM
        )
        
        print(f"\nSynthesized {len(data_points)} data points:")
        for j, dp in enumerate(data_points[:10]):
            print(f"  {j+1}. Label: '{dp.label}' | Value: {dp.value:.2f}")
        if len(data_points) > 10:
            print(f"  ... and {len(data_points)-10} more")
            
        # Check if this is actual distribution data
        values = [dp.value for dp in data_points]
        if len(values) > 0:
            import numpy as np
            print(f"\nData statistics:")
            print(f"  Count: {len(values)}")
            print(f"  Mean: {np.mean(values):.2f}")
            print(f"  Std: {np.std(values):.2f}")
            print(f"  Min: {np.min(values):.2f}")
            print(f"  Max: {np.max(values):.2f}")
            print(f"  Unique values: {len(set(values))}")


if __name__ == "__main__":
    asyncio.run(test_histogram())