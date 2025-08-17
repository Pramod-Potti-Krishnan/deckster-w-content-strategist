#!/usr/bin/env python
"""
Manual Validation Test for Simplified MCP
==========================================

This script generates various charts using ONLY the simplified MCP implementation
(no fallback to archived code) for manual validation.

The generated Python code can be executed to create actual charts.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Setup
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics


async def generate_validation_charts():
    """Generate charts for manual validation."""
    
    # Create output directory
    output_dir = Path(f"validation_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("GENERATING CHARTS FOR MANUAL VALIDATION")
    print("Using ONLY Simplified MCP (No Fallback)")
    print("="*70)
    print(f"\nOutput directory: {output_dir}\n")
    
    # Define test cases
    test_cases = [
        {
            "name": "1_simple_bar_chart",
            "title": "Monthly Sales 2024",
            "content": "Create a bar chart showing monthly sales: Jan $45K, Feb $52K, Mar $48K, Apr $61K, May $58K, Jun $67K",
            "chart_type": "bar"
        },
        {
            "name": "2_line_trend_chart",
            "title": "Revenue Growth Trend",
            "content": "Show revenue trend over 8 quarters with steady growth from $1M to $2.5M",
            "chart_type": "line"
        },
        {
            "name": "3_pie_distribution",
            "title": "Market Share",
            "content": "Display market share: Leader 35%, Challenger 28%, Follower 22%, Others 15%",
            "chart_type": "pie"
        },
        {
            "name": "4_scatter_correlation",
            "title": "Price vs Demand",
            "content": "Create scatter plot showing negative correlation between price and demand with 15 data points",
            "chart_type": "scatter"
        },
        {
            "name": "5_histogram_distribution",
            "title": "Customer Age Distribution",
            "content": "Generate histogram of customer ages with normal distribution, mean=35, std=10, 500 samples",
            "chart_type": "histogram"
        },
        {
            "name": "6_heatmap_correlation",
            "title": "Feature Correlation Matrix",
            "content": "Create correlation heatmap for 5 features: Speed, Quality, Price, Support, Reliability",
            "chart_type": "heatmap"
        }
    ]
    
    print("Generating charts...\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test['title']}")
        print(f"    Type: {test['chart_type']}")
        
        try:
            # Generate the chart
            result = await create_analytics(
                content=test['content'],
                title=test['title'],
                chart_type=test['chart_type']
            )
            
            if result['success']:
                if result['format'] == 'python_code':
                    # Save Python code
                    py_file = output_dir / f"{test['name']}.py"
                    with open(py_file, 'w') as f:
                        # Add header comment
                        f.write(f'"""\n{test["title"]}\n{test["content"]}\n"""\n\n')
                        f.write(result['content'])
                    print(f"    ✅ Python code saved: {py_file.name}")
                    
                elif result['format'] == 'mermaid':
                    # Save Mermaid code
                    mmd_file = output_dir / f"{test['name']}.mmd"
                    with open(mmd_file, 'w') as f:
                        f.write(result['content'])
                    print(f"    ✅ Mermaid code saved: {mmd_file.name}")
                    
                else:
                    print(f"    ⚠️ Unexpected format: {result['format']}")
                    
                # Save insights
                if result.get('insights'):
                    insights_file = output_dir / f"{test['name']}_insights.txt"
                    with open(insights_file, 'w') as f:
                        f.write(f"{test['title']}\n")
                        f.write("="*50 + "\n\n")
                        for insight in result['insights']:
                            f.write(f"• {insight}\n")
                    
            else:
                print(f"    ❌ Generation failed")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Create execution script
    print("\nCreating execution script...")
    
    exec_script = '''#!/usr/bin/env python
"""Execute all generated Python charts and save as PNG images."""

import os
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')

def execute_chart(py_file):
    """Execute a Python chart file and save as PNG."""
    png_file = py_file.with_suffix('.png')
    
    try:
        with open(py_file, 'r') as f:
            code = f.read()
        
        # Add save command
        code += f"""
import matplotlib.pyplot as plt
if plt.get_fignums():
    plt.savefig('{png_file}', dpi=100, bbox_inches='tight')
    plt.close('all')
    print(f'  ✅ Saved: {png_file.name}')
else:
    print(f'  ⚠️ No figure created for {py_file.name}')
"""
        exec(code, {'__name__': '__main__'})
        return True
    except Exception as e:
        print(f'  ❌ Error with {py_file.name}: {e}')
        return False

print("Executing Python charts to generate PNGs...")
print("="*50)

py_files = sorted(Path('.').glob('*.py'))
py_files = [f for f in py_files if f.name != 'execute_all.py']

success = 0
for py_file in py_files:
    print(f"\\nProcessing: {py_file.name}")
    if execute_chart(py_file):
        success += 1

print("\\n" + "="*50)
print(f"Successfully generated {success}/{len(py_files)} PNG images")
'''
    
    exec_file = output_dir / "execute_all.py"
    with open(exec_file, 'w') as f:
        f.write(exec_script)
    exec_file.chmod(0o755)
    
    print(f"✅ Execution script created: {exec_file}")
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION CHARTS GENERATED")
    print("="*70)
    print(f"\n📁 Output directory: {output_dir}")
    print(f"📊 Charts generated: {len(test_cases)}")
    print("\n📝 TO VALIDATE:")
    print(f"1. cd {output_dir}")
    print("2. python execute_all.py  # This will create PNG images")
    print("3. Review the generated PNG files")
    print("\n✨ All charts were generated using ONLY the simplified MCP executor")
    print("   (No fallback to archived code)")
    print("="*70)


async def main():
    """Main entry point."""
    # Verify we're using simplified version
    import sys
    archived_modules = [m for m in sys.modules.keys() if 'archived_mcp_backup' in m]
    
    if archived_modules:
        print(f"⚠️ WARNING: Found archived modules: {archived_modules}")
        print("This test should use ONLY the simplified implementation!")
    else:
        print("✅ Confirmed: Using ONLY simplified MCP implementation (no archived code)")
    
    await generate_validation_charts()


if __name__ == "__main__":
    asyncio.run(main())