"""
Test 3 Random Charts with Synthetic Data
=========================================

Generate 3 different chart types with synthetic data to demonstrate the system.
"""

import asyncio
from dotenv import load_dotenv
import os
import random

# Load environment variables
load_dotenv()

from src.agents.analytics_agent_v2 import create_analytics_v2


async def generate_three_random_charts():
    """Generate 3 random charts with synthetic data."""
    
    print("=" * 70)
    print("🎨 Generating 3 Random Charts with Synthetic Data")
    print("=" * 70)
    
    # Chart configurations
    chart_configs = [
        {
            "name": "Sales Trend Analysis",
            "content": "Show monthly sales trend over the last 12 months with growth pattern",
            "chart_type": "line_chart",
            "theme": {
                "primary": "#2563EB",    # Blue
                "secondary": "#10B981",  # Green
                "tertiary": "#F59E0B"    # Orange
            }
        },
        {
            "name": "Department Performance",
            "content": "Compare performance metrics across different departments in the company",
            "chart_type": "bar_chart_vertical",
            "theme": {
                "primary": "#7C3AED",    # Purple
                "secondary": "#EC4899",  # Pink
                "tertiary": "#06B6D4"    # Cyan
            }
        },
        {
            "name": "Budget Distribution",
            "content": "Show budget allocation across different business units as percentages",
            "chart_type": "pie_chart",
            "theme": {
                "primary": "#059669",    # Green
                "secondary": "#DC2626",  # Red
                "tertiary": "#7C3AED"    # Purple
            }
        }
    ]
    
    # Generate each chart
    for i, config in enumerate(chart_configs, 1):
        print(f"\n📊 Chart {i}: {config['name']}")
        print("-" * 50)
        
        try:
            result = await create_analytics_v2(
                content=config["content"],
                title=config["name"],
                theme=config["theme"],
                chart_type=config["chart_type"],
                enhance_labels=False,  # Disable LLM enhancement for faster testing
                save_files=True,
                output_dir=f"test_output/chart_{i}_{config['chart_type']}"
            )
            
            if result['success']:
                print(f"✅ Success!")
                print(f"   Chart Type: {result['metadata']['chart_type']}")
                print(f"   Data Source: {result['metadata']['data_source']}")
                print(f"   Generation Time: {result['metadata']['generation_time_ms']:.0f}ms")
                
                if result.get('saved_files'):
                    print(f"   📁 Files saved:")
                    for file_type, path in result['saved_files'].items():
                        print(f"      - {file_type}: {os.path.basename(path)}")
                
                # Show data summary
                if result.get('data'):
                    data = result['data']
                    if data.get('statistics'):
                        stats = data['statistics']
                        print(f"   📈 Data Statistics:")
                        print(f"      - Count: {stats['count']} data points")
                        print(f"      - Range: {stats['min']:.2f} to {stats['max']:.2f}")
                        print(f"      - Mean: {stats['mean']:.2f}")
                    
                    # Show first few labels
                    if data.get('labels'):
                        labels_preview = data['labels'][:3]
                        print(f"   🏷️  Labels: {', '.join(str(l) for l in labels_preview)}...")
                    
                    # Show insights
                    if result['metadata'].get('insights'):
                        print(f"   💡 Insights:")
                        for insight in result['metadata']['insights'][:2]:
                            print(f"      - {insight}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)[:100]}")
    
    print("\n" + "=" * 70)
    print("✨ Chart Generation Complete!")
    print("=" * 70)
    print("\n📂 Output Directory Structure:")
    print("test_output/")
    print("├── chart_1_line_chart/")
    print("│   ├── *.png          (Chart image)")
    print("│   ├── *_data.json    (Underlying data)")
    print("│   └── *_metadata.json (Chart metadata)")
    print("├── chart_2_bar_chart_vertical/")
    print("│   └── ... (same structure)")
    print("└── chart_3_pie_chart/")
    print("    └── ... (same structure)")
    
    print("\n💡 The system generates both:")
    print("   1. PNG files - Ready for display or API transmission")
    print("   2. JSON data - Complete underlying data for further processing")


if __name__ == "__main__":
    # Run the test
    asyncio.run(generate_three_random_charts())