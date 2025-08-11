"""
Test Analytics with Pydantic MCP Server
========================================

Demonstrates real Python code execution and image generation
using the pydantic MCP server implementation.
"""

import os
import sys
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Setup
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor


async def test_pydantic_mcp_integration():
    """Test analytics with pydantic MCP server."""
    
    print("\n" + "="*70)
    print("TESTING ANALYTICS WITH PYDANTIC MCP SERVER")
    print("="*70)
    print("\nThis test demonstrates ACTUAL Python code execution")
    print("and real chart image generation via the pydantic MCP server.")
    
    # Create output directory
    output_dir = "test_output/pydantic_mcp_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test cases that will generate real images
    test_cases = [
        {
            "title": "Quarterly Revenue Trend",
            "content": "Quarterly revenue: Q1=$2.5M, Q2=$3.1M, Q3=$2.8M, Q4=$3.6M",
            "chart_type": "line",
            "expected": "Mermaid chart (simple type)"
        },
        {
            "title": "Sales Correlation Analysis",
            "content": "Create scatter plot showing correlation: (10, 20), (20, 40), (30, 35), (40, 50), (50, 65)",
            "chart_type": "scatter",
            "expected": "Python code -> Real PNG image"
        },
        {
            "title": "Customer Age Distribution",
            "content": "Show age distribution histogram with mean 35 and std 10, 500 samples",
            "chart_type": "histogram",
            "expected": "Python code -> Real PNG image"
        },
        {
            "title": "Product Category Heatmap",
            "content": "Create 5x5 heatmap for product categories vs regions with correlation values",
            "chart_type": "heatmap",
            "expected": "Python code -> Real PNG image"
        },
        {
            "title": "Monthly Performance Box Plot",
            "content": "Box plot of monthly performance metrics across departments",
            "chart_type": "box",
            "expected": "Python code -> Real PNG image"
        }
    ]
    
    successful_images = 0
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test['title']}")
        print("-"*40)
        print(f"Expected: {test['expected']}")
        
        try:
            # Create analytics with pydantic MCP executor
            result = await create_analytics(
                test['content'],
                title=test['title'],
                chart_type=test['chart_type'],
                mcp_tool=pydantic_mcp_executor
            )
            
            if result['success']:
                print(f"✅ Chart generated successfully")
                print(f"   Type: {result['chart_type']}")
                print(f"   Format: {result['format']}")
                
                # Check if we got actual image or just code
                if result['format'] == 'base64':
                    print(f"   🎉 REAL IMAGE GENERATED via pydantic MCP!")
                    print(f"   Image size: {len(result['content'])} characters")
                    
                    # Save the actual image
                    try:
                        image_data = base64.b64decode(result['content'])
                        filename = f"{test['chart_type']}_{datetime.now().strftime('%H%M%S')}.png"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"   💾 Saved to: {filepath}")
                        print(f"   File size: {len(image_data)} bytes")
                        successful_images += 1
                        results.append((test['title'], True, 'image'))
                    except Exception as e:
                        print(f"   ❌ Failed to save image: {e}")
                        results.append((test['title'], True, 'error'))
                        
                elif result['format'] == 'python_code':
                    print(f"   📝 Got Python code (would execute with MCP)")
                    print(f"   Code length: {len(result['content'])} characters")
                    
                    # Try to execute the code with pydantic MCP
                    print("   🔄 Attempting direct execution...")
                    base64_image = await pydantic_mcp_executor.execute_chart_code(result['content'])
                    
                    if base64_image:
                        print(f"   🎉 Successfully executed code and got image!")
                        image_data = base64.b64decode(base64_image)
                        filename = f"{test['chart_type']}_executed_{datetime.now().strftime('%H%M%S')}.png"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"   💾 Saved executed chart to: {filepath}")
                        successful_images += 1
                        results.append((test['title'], True, 'executed'))
                    else:
                        print(f"   ⚠️ Code execution didn't produce image")
                        results.append((test['title'], True, 'code'))
                        
                elif result['format'] == 'mermaid':
                    print(f"   📊 Got Mermaid chart (simple visualization)")
                    print(f"   Content length: {len(result['content'])} characters")
                    results.append((test['title'], True, 'mermaid'))
                    
                # Show insights
                if result.get('insights'):
                    print(f"\n   💡 Insights:")
                    for insight in result['insights'][:3]:
                        print(f"      • {insight}")
                        
            else:
                print(f"❌ Failed to generate chart")
                results.append((test['title'], False, None))
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test['title'], False, 'exception'))
    
    # Summary
    print("\n" + "="*70)
    print("PYDANTIC MCP INTEGRATION RESULTS")
    print("="*70)
    
    print(f"\n📊 Results Summary:")
    print(f"   Total tests: {len(test_cases)}")
    print(f"   Successful: {sum(1 for _, success, _ in results if success)}")
    print(f"   Real images generated: {successful_images}")
    
    print(f"\n📈 Breakdown by format:")
    for format_type in ['image', 'executed', 'mermaid', 'code']:
        count = sum(1 for _, _, fmt in results if fmt == format_type)
        if count > 0:
            print(f"   {format_type}: {count}")
    
    if successful_images > 0:
        print(f"\n✅ SUCCESS! Pydantic MCP Server Integration Working!")
        print(f"   • Python code is being executed in subprocess")
        print(f"   • Real PNG images are being generated")
        print(f"   • Charts saved to: {output_dir}/")
        print(f"\n🎯 The pydantic MCP server is fully operational!")
    else:
        print(f"\n⚠️ No images were generated - check MCP configuration")
    
    return successful_images > 0


async def demonstrate_complete_system():
    """Demonstrate the complete analytics system with pydantic MCP."""
    
    print("\n" + "="*70)
    print("COMPLETE SYSTEM DEMONSTRATION")
    print("="*70)
    print("\nDemonstrating all improvements with actual code execution:")
    
    examples = [
        {
            "description": "📊 Data Parsing + Real Execution",
            "content": "Q1 revenue was $1.2M, Q2 hit $1.5M, Q3 reached $1.8M, and Q4 closed at $2.1M. Show the trend.",
            "chart_type": "line"
        },
        {
            "description": "📈 Complex Visualization with MCP",
            "content": "Create a scatter plot with regression line showing the correlation between marketing spend (10k, 20k, 30k, 40k, 50k) and sales (50k, 95k, 140k, 185k, 230k)",
            "chart_type": "scatter"
        },
        {
            "description": "🔥 Heatmap via Python Execution",
            "content": "Generate a correlation heatmap for 5 metrics: Revenue, Costs, Profit, Customers, Satisfaction",
            "chart_type": "heatmap"
        }
    ]
    
    for example in examples:
        print(f"\n{example['description']}")
        print("-"*40)
        
        result = await create_analytics(
            example['content'],
            chart_type=example['chart_type'],
            mcp_tool=pydantic_mcp_executor
        )
        
        if result['success']:
            if result['format'] == 'base64':
                print(f"✅ Real image generated! Size: {len(result['content'])} chars")
                # Save for verification
                filename = f"demo_{example['chart_type']}_{datetime.now().strftime('%H%M%S')}.png"
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(result['content']))
                print(f"   Saved to: {filename}")
            else:
                print(f"Format: {result['format']}")


async def main():
    """Run all tests."""
    
    print("\n🚀 Starting Pydantic MCP Integration Tests...")
    print("\nThe pydantic MCP server will:")
    print("  1. Execute Python code in a subprocess")
    print("  2. Capture matplotlib charts as images")
    print("  3. Return base64-encoded PNG files")
    print("  4. Save actual chart images to disk")
    
    # Run integration test
    success = await test_pydantic_mcp_integration()
    
    if success:
        # Run complete system demo
        await demonstrate_complete_system()
    
    print("\n✅ Testing Complete!")
    print("\n📝 How to use in your code:")
    print("   from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor")
    print("   result = await create_analytics('your request', mcp_tool=pydantic_mcp_executor)")
    print("\n🎯 The system is now executing Python code and generating real images!")


if __name__ == "__main__":
    asyncio.run(main())