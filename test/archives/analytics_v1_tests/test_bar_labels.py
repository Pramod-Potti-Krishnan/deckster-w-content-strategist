#!/usr/bin/env python
"""
Test Bar Chart Label Parsing
============================
Debug why bar chart labels aren't being parsed correctly.
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

from src.agents.analytics_utils.data_parser import DataParser
from src.agents.analytics_utils.data_synthesizer import DataSynthesizer


async def test_label_parsing():
    """Test how labels are being parsed from descriptions."""
    
    print("\n" + "="*60)
    print("TESTING LABEL PARSING FOR BAR CHARTS")
    print("="*60)
    
    parser = DataParser()
    
    test_cases = [
        "Sales by category: Electronics $450K, Clothing $320K, Home $280K, Sports $195K, Books $155K",
        "Regional sales: North $1.2M, South $980K, East $1.1M, West $1.3M, Central $750K"
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}] Test: {test}")
        print("-" * 40)
        
        parsed = parser.parse_data_points(test)
        
        if parsed:
            print(f"Found {len(parsed)} data points:")
            for dp in parsed:
                print(f"  Label: '{dp.label}' | Value: {dp.value}")
        else:
            print("No data points parsed!")
            
        # Also test the synthesizer
        from src.agents.analytics_utils.models import AnalyticsRequest, SyntheticDataConfig, ChartType
        
        request = AnalyticsRequest(
            title="Test Chart",
            description=test,
            data_context=test
        )
        
        config = SyntheticDataConfig()
        
        synthesizer = DataSynthesizer()
        data_points, desc, insights = await synthesizer.generate_synthetic_data(
            request, config, ChartType.BAR
        )
        
        print(f"\nSynthesized {len(data_points)} points:")
        for dp in data_points:
            print(f"  Label: '{dp.label}' | Value: {dp.value}")


if __name__ == "__main__":
    asyncio.run(test_label_parsing())