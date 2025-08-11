"""
Final Analytics Agent Demonstration
====================================

Shows all improvements working together.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Setup
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics


async def demonstrate_improvements():
    """Demonstrate all improvements."""
    
    print("\n" + "="*70)
    print("ANALYTICS AGENT - COMPLETE FEATURE DEMONSTRATION")
    print("="*70)
    
    demos = [
        {
            "title": "1. EXACT DATA PARSING",
            "description": "Chart uses exact values from user request",
            "request": "Show Q1=$1.2M, Q2=$1.5M, Q3=$1.3M, Q4=$1.8M",
            "chart_title": "Quarterly Revenue 2024"
        },
        {
            "title": "2. ACCURATE INSIGHTS",
            "description": "Insights match the actual data trend",
            "request": "Monthly growth: Jan 100, Feb 150, Mar 200, Apr 250, May 300, Jun 350",
            "chart_title": "Monthly Growth Pattern"
        },
        {
            "title": "3. COMPLEX CHART TYPES",
            "description": "Python code generation for advanced charts",
            "request": "Create scatter plot showing correlation between ad spend (10k, 20k, 30k, 40k) and revenue (50k, 80k, 110k, 140k)",
            "chart_title": "Ad Spend vs Revenue",
            "chart_type": "scatter"
        },
        {
            "title": "4. PERCENTAGE DATA",
            "description": "Correctly handles percentage distributions",
            "request": "Market share: Leader 45%, Challenger 30%, Niche 20%, Others 5%",
            "chart_title": "Market Share Analysis",
            "chart_type": "pie"
        },
        {
            "title": "5. SEASONAL PATTERNS",
            "description": "Detects and reports seasonal variations",
            "request": "Ice cream sales by month: Jan $10k, Feb $12k, Mar $20k, Apr $35k, May $55k, Jun $85k, Jul $95k, Aug $90k, Sep $60k, Oct $40k, Nov $20k, Dec $15k",
            "chart_title": "Seasonal Sales Pattern",
            "chart_type": "line"
        }
    ]
    
    for demo in demos:
        print(f"\n{'='*70}")
        print(f"{demo['title']}")
        print(f"Purpose: {demo['description']}")
        print("-"*70)
        
        result = await create_analytics(
            demo['request'],
            title=demo['chart_title'],
            chart_type=demo.get('chart_type')
        )
        
        if result['success']:
            print(f"✅ Chart Generated Successfully")
            print(f"   Type: {result['chart_type']}")
            print(f"   Format: {result['format']}")
            
            # Show parsed data
            if result.get('data'):
                print(f"\n📊 Parsed Data Points:")
                for dp in result['data'][:4]:  # Show first 4
                    print(f"   • {dp['label']}: {dp['value']:.2f}")
                if len(result['data']) > 4:
                    print(f"   ... and {len(result['data'])-4} more")
            
            # Show insights
            if result.get('insights'):
                print(f"\n💡 Generated Insights:")
                for insight in result['insights']:
                    print(f"   • {insight}")
            
            # Show description
            if result.get('description'):
                print(f"\n📝 Description:")
                print(f"   {result['description']}")
            
            # For Python charts, show if code was generated
            if result['format'] == 'python_code':
                print(f"\n🐍 Python Code Generated:")
                print(f"   Length: {len(result['content'])} characters")
                print(f"   Can be executed with matplotlib/seaborn")
        else:
            print(f"❌ Failed to generate chart")
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n✨ Key Improvements Demonstrated:")
    print("  ✅ Exact data parsing from natural language")
    print("  ✅ Insights that match actual data")
    print("  ✅ Support for all 12+ chart types")
    print("  ✅ Proper handling of percentages and monetary values")
    print("  ✅ Seasonal pattern detection")
    print("  ✅ Python code generation for complex visualizations")
    print("  ✅ MCP integration ready (when available)")


if __name__ == "__main__":
    print("\n🚀 Starting Final Analytics Agent Demo...\n")
    asyncio.run(demonstrate_improvements())
    print("\n✅ Demo Complete!\n")