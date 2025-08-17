#!/usr/bin/env python3
"""
Analytics Playbook System Comparison Tests
==========================================

Tests to compare original rule-based system with new playbook-based system.
Ensures both implementations work correctly and produce valid results.

Usage:
    python test_playbook_comparison.py

Author: Analytics Agent System
Date: 2024
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.analytics_agent import create_analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlaybookComparisonTester:
    """Tests to compare original and playbook implementations."""
    
    def __init__(self):
        """Initialize the tester."""
        self.test_cases = self._create_test_cases()
        self.results = {
            "original": [],
            "playbook": [],
            "comparison": []
        }
        
    def _create_test_cases(self) -> List[Dict[str, Any]]:
        """Create test cases covering various chart types."""
        return [
            {
                "name": "Time Series Line Chart",
                "content": "Show monthly sales trend over the past year with seasonal patterns",
                "title": "Monthly Sales Trend",
                "chart_type": "line"
            },
            {
                "name": "Categorical Bar Chart",
                "content": "Compare revenue across our 5 product categories",
                "title": "Product Category Revenue",
                "chart_type": "bar"
            },
            {
                "name": "Proportional Pie Chart",
                "content": "Display market share breakdown for top 4 competitors",
                "title": "Market Share Distribution",
                "chart_type": "pie"
            },
            {
                "name": "Correlation Scatter Plot",
                "content": "Show relationship between price and customer satisfaction scores",
                "title": "Price vs Satisfaction",
                "chart_type": "scatter"
            },
            {
                "name": "Distribution Histogram",
                "content": "Analyze distribution of customer ages in our database",
                "title": "Customer Age Distribution",
                "chart_type": "histogram"
            },
            {
                "name": "Matrix Heatmap",
                "content": "Create heatmap of user activity by hour of day and day of week",
                "title": "Activity Heatmap",
                "chart_type": "heatmap"
            },
            {
                "name": "Multi-dimensional Radar",
                "content": "Compare performance across 6 key metrics for 3 products",
                "title": "Product Performance Radar",
                "chart_type": "radar"
            },
            {
                "name": "Complex Area Chart",
                "content": "Show cumulative revenue growth over time with confidence bands",
                "title": "Cumulative Revenue",
                "chart_type": "area"
            }
        ]
    
    async def run_with_original(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run test with original implementation."""
        # Set environment variable for original
        os.environ["USE_PLAYBOOK_SYSTEM"] = "false"
        
        # Import fresh to get correct implementation
        import importlib
        import src.agents.analytics_agent
        importlib.reload(src.agents.analytics_agent)
        from src.agents.analytics_agent import create_analytics
        
        try:
            result = await create_analytics(
                content=test_case["content"],
                title=test_case["title"],
                chart_type=test_case.get("chart_type")
            )
            return {
                "success": result.get("success", False),
                "chart_type": result.get("chart_type"),
                "format": result.get("format"),
                "has_content": bool(result.get("content")),
                "data_points": len(result.get("data", [])),
                "insights_count": len(result.get("insights", [])),
                "error": None
            }
        except Exception as e:
            logger.error(f"Original implementation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_with_playbook(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run test with playbook implementation."""
        # Set environment variable for playbook
        os.environ["USE_PLAYBOOK_SYSTEM"] = "true"
        
        # Import fresh to get correct implementation
        import importlib
        import src.agents.analytics_agent
        importlib.reload(src.agents.analytics_agent)
        from src.agents.analytics_agent import create_analytics
        
        try:
            result = await create_analytics(
                content=test_case["content"],
                title=test_case["title"],
                chart_type=test_case.get("chart_type")
            )
            return {
                "success": result.get("success", False),
                "chart_type": result.get("chart_type"),
                "format": result.get("format"),
                "has_content": bool(result.get("content")),
                "data_points": len(result.get("data", [])),
                "insights_count": len(result.get("insights", [])),
                "error": None
            }
        except Exception as e:
            logger.error(f"Playbook implementation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def compare_implementations(self):
        """Run all tests with both implementations and compare."""
        print("\n" + "="*80)
        print("ANALYTICS PLAYBOOK SYSTEM COMPARISON TEST")
        print("="*80)
        print(f"Running {len(self.test_cases)} test cases...")
        print("-"*80)
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"  Request: {test_case['content'][:60]}...")
            
            # Run with original
            print("  Running with ORIGINAL implementation...", end="")
            original_result = await self.run_with_original(test_case)
            self.results["original"].append(original_result)
            print(f" {'✓' if original_result['success'] else '✗'}")
            
            # Run with playbook
            print("  Running with PLAYBOOK implementation...", end="")
            playbook_result = await self.run_with_playbook(test_case)
            self.results["playbook"].append(playbook_result)
            print(f" {'✓' if playbook_result['success'] else '✗'}")
            
            # Compare results
            comparison = self._compare_results(original_result, playbook_result)
            self.results["comparison"].append(comparison)
            
            # Print comparison
            print(f"  Comparison:")
            print(f"    - Both successful: {comparison['both_successful']}")
            print(f"    - Same chart type: {comparison['same_chart_type']}")
            print(f"    - Same format: {comparison['same_format']}")
            print(f"    - Data points: Original={original_result.get('data_points', 0)}, "
                  f"Playbook={playbook_result.get('data_points', 0)}")
            
            if not comparison['both_successful']:
                if not original_result['success']:
                    print(f"    ⚠️  Original failed: {original_result.get('error', 'Unknown error')}")
                if not playbook_result['success']:
                    print(f"    ⚠️  Playbook failed: {playbook_result.get('error', 'Unknown error')}")
        
        # Print summary
        self._print_summary()
    
    def _compare_results(self, original: Dict, playbook: Dict) -> Dict:
        """Compare results from both implementations."""
        return {
            "both_successful": original["success"] and playbook["success"],
            "same_chart_type": original.get("chart_type") == playbook.get("chart_type"),
            "same_format": original.get("format") == playbook.get("format"),
            "both_have_content": original.get("has_content") and playbook.get("has_content"),
            "data_difference": abs(
                original.get("data_points", 0) - playbook.get("data_points", 0)
            )
        }
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        # Count successes
        original_success = sum(1 for r in self.results["original"] if r["success"])
        playbook_success = sum(1 for r in self.results["playbook"] if r["success"])
        both_success = sum(1 for c in self.results["comparison"] if c["both_successful"])
        
        print(f"\nSuccess Rates:")
        print(f"  Original: {original_success}/{len(self.test_cases)} "
              f"({(original_success/len(self.test_cases))*100:.1f}%)")
        print(f"  Playbook: {playbook_success}/{len(self.test_cases)} "
              f"({(playbook_success/len(self.test_cases))*100:.1f}%)")
        print(f"  Both:     {both_success}/{len(self.test_cases)} "
              f"({(both_success/len(self.test_cases))*100:.1f}%)")
        
        # Chart type consistency
        same_chart = sum(1 for c in self.results["comparison"] 
                        if c["same_chart_type"] and c["both_successful"])
        if both_success > 0:
            print(f"\nChart Type Consistency: {same_chart}/{both_success} "
                  f"({(same_chart/both_success)*100:.1f}%)")
        
        # Format consistency
        same_format = sum(1 for c in self.results["comparison"] 
                         if c["same_format"] and c["both_successful"])
        if both_success > 0:
            print(f"Format Consistency: {same_format}/{both_success} "
                  f"({(same_format/both_success)*100:.1f}%)")
        
        # Recommendations
        print("\n" + "-"*80)
        print("RECOMMENDATIONS:")
        
        if playbook_success >= original_success:
            print("✅ Playbook implementation is performing as well or better than original")
            if playbook_success == len(self.test_cases):
                print("✅ All tests passed with playbook implementation")
        else:
            print("⚠️  Playbook implementation has lower success rate than original")
            print("   Consider reviewing failed test cases before full deployment")
        
        if both_success == len(self.test_cases):
            print("✅ Both implementations successfully handle all test cases")
        elif both_success >= len(self.test_cases) * 0.8:
            print("✅ Both implementations handle most test cases successfully")
        else:
            print("⚠️  Some test cases fail in one or both implementations")
        
        print("\nTo enable playbook system in production:")
        print("  export USE_PLAYBOOK_SYSTEM=true")
        print("\nTo use original system:")
        print("  export USE_PLAYBOOK_SYSTEM=false")
        print("="*80)


async def main():
    """Main test runner."""
    tester = PlaybookComparisonTester()
    await tester.compare_implementations()


if __name__ == "__main__":
    # Ensure we start with original implementation
    os.environ["USE_PLAYBOOK_SYSTEM"] = "false"
    
    print(f"Starting comparison test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()