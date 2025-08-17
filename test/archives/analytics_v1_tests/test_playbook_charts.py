#!/usr/bin/env python3
"""
Test Playbook System Chart Generation
======================================

Generates various chart types using the playbook system for manual validation.
Saves outputs to files for review.

Author: Analytics Agent System
Date: 2024
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Map GOOGLE_API_KEY to GEMINI_API_KEY if needed
if os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Force playbook system
os.environ["USE_PLAYBOOK_SYSTEM"] = "true"

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.analytics_agent import create_analytics


class PlaybookChartTester:
    """Generate test charts using playbook system."""
    
    def __init__(self):
        """Initialize the tester."""
        self.output_dir = Path("playbook_test_outputs")
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        
    def get_test_cases(self):
        """Define test cases for various chart types."""
        return [
            {
                "id": "01_line_trend",
                "name": "Monthly Sales Trend",
                "content": "Show monthly sales trend over the past year with clear seasonal patterns and growth",
                "title": "Monthly Sales Performance 2024",
                "expected_type": "line"
            },
            {
                "id": "02_bar_comparison",
                "name": "Product Category Revenue",
                "content": "Compare revenue across our 8 product categories for Q4 2024",
                "title": "Q4 2024 Product Revenue",
                "expected_type": "bar"
            },
            {
                "id": "03_histogram_distribution",
                "name": "Customer Age Distribution",
                "content": "Analyze the distribution of customer ages in our database, showing any clustering",
                "title": "Customer Age Analysis",
                "expected_type": "histogram"
            },
            {
                "id": "04_scatter_correlation",
                "name": "Price vs Satisfaction",
                "content": "Show correlation between product price and customer satisfaction scores",
                "title": "Price-Satisfaction Correlation",
                "expected_type": "scatter"
            },
            {
                "id": "05_pie_proportion",
                "name": "Market Share",
                "content": "Display market share breakdown for top 5 companies in the industry",
                "title": "Market Share Distribution 2024",
                "expected_type": "pie"
            },
            {
                "id": "06_heatmap_matrix",
                "name": "Activity Heatmap",
                "content": "Create a heatmap showing user activity levels by hour of day and day of week",
                "title": "User Activity Patterns",
                "expected_type": "heatmap"
            },
            {
                "id": "07_radar_comparison",
                "name": "Product Performance",
                "content": "Compare 3 products across 6 performance metrics: speed, reliability, usability, features, support, value",
                "title": "Multi-Product Performance Radar",
                "expected_type": "radar"
            },
            {
                "id": "08_area_cumulative",
                "name": "Cumulative Revenue",
                "content": "Show cumulative revenue growth over the past 52 weeks with confidence bands",
                "title": "Weekly Revenue Accumulation",
                "expected_type": "area"
            },
            {
                "id": "09_waterfall_breakdown",
                "name": "Profit Waterfall",
                "content": "Create waterfall chart showing how we went from $1M starting revenue to $1.5M ending revenue through various factors",
                "title": "Revenue Bridge Analysis",
                "expected_type": "waterfall"
            },
            {
                "id": "10_box_plot_comparison",
                "name": "Regional Sales Distribution",
                "content": "Compare sales distributions across 4 regions using box plots to show medians and outliers",
                "title": "Regional Sales Comparison",
                "expected_type": "box_plot"
            },
            {
                "id": "11_bubble_3d",
                "name": "Market Analysis",
                "content": "Show market opportunity with revenue on x-axis, growth rate on y-axis, and market size as bubble size",
                "title": "Market Opportunity Matrix",
                "expected_type": "bubble"
            },
            {
                "id": "12_stacked_composition",
                "name": "Revenue Composition",
                "content": "Show how revenue composition changed over 12 months across 4 product lines using stacked area chart",
                "title": "Product Line Revenue Evolution",
                "expected_type": "area"
            }
        ]
    
    async def generate_chart(self, test_case):
        """Generate a single chart."""
        print(f"\n[{test_case['id']}] Generating: {test_case['name']}")
        print(f"  Request: {test_case['content'][:80]}...")
        
        try:
            result = await create_analytics(
                content=test_case['content'],
                title=test_case['title']
            )
            
            # Extract key information
            success = result.get('success', False)
            chart_type = result.get('chart_type', 'unknown')
            format_type = result.get('format', 'unknown')
            content = result.get('content', '')
            data = result.get('data', [])
            insights = result.get('insights', [])
            description = result.get('description', '')
            
            print(f"  ✓ Generated: {chart_type} ({format_type})")
            print(f"  ✓ Data points: {len(data)}")
            print(f"  ✓ Insights: {len(insights)}")
            
            if success and content:
                # Save chart content
                self._save_chart(test_case['id'], test_case['name'], 
                               chart_type, format_type, content, 
                               data, insights, description)
                
                # Record result
                self.results.append({
                    "id": test_case['id'],
                    "name": test_case['name'],
                    "success": True,
                    "expected": test_case['expected_type'],
                    "actual": chart_type,
                    "format": format_type,
                    "match": chart_type == test_case['expected_type']
                })
            else:
                print(f"  ✗ Failed to generate chart")
                self.results.append({
                    "id": test_case['id'],
                    "name": test_case['name'],
                    "success": False,
                    "error": result.get('metadata', {}).get('error', 'Unknown error')
                })
                
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            self.results.append({
                "id": test_case['id'],
                "name": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    def _save_chart(self, chart_id, name, chart_type, format_type, 
                   content, data, insights, description):
        """Save chart to file."""
        # Determine file extension
        if format_type == 'mermaid':
            ext = 'mmd'
        elif format_type == 'python_code':
            ext = 'py'
        else:
            ext = 'txt'
        
        # Create filename
        filename = f"{chart_id}_{chart_type}.{ext}"
        filepath = self.output_dir / filename
        
        # Prepare content with metadata
        output = f"""# {name}
# Chart Type: {chart_type}
# Format: {format_type}
# Generated: {datetime.now().isoformat()}
# Description: {description}

"""
        
        # Add insights as comments
        if insights:
            output += "# Insights:\n"
            for insight in insights:
                output += f"#   - {insight}\n"
            output += "\n"
        
        # Add the chart content
        if format_type == 'python_code':
            output += "# ========== Chart Code ==========\n\n"
        
        output += content
        
        # Add data summary
        if data and len(data) <= 20:  # Only include if small dataset
            output += f"\n\n# ========== Data ({len(data)} points) ==========\n"
            output += "# " + json.dumps(data[:5], indent=2).replace('\n', '\n# ')
            if len(data) > 5:
                output += "\n# ... (showing first 5 of {} points)".format(len(data))
        
        # Save to file
        filepath.write_text(output)
        print(f"  ✓ Saved: {filename}")
    
    def create_html_preview(self):
        """Create HTML file to preview Mermaid charts."""
        mermaid_files = list(self.output_dir.glob("*.mmd"))
        
        if not mermaid_files:
            print("\nNo Mermaid charts to preview")
            return
        
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Playbook Chart Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({ startOnLoad: true });</script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .chart-container { 
            background: white; 
            margin: 20px 0; 
            padding: 20px; 
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-title { 
            font-size: 18px; 
            font-weight: bold; 
            color: #2196F3;
            margin-bottom: 10px;
        }
        .mermaid { 
            text-align: center;
            min-height: 300px;
        }
        .metadata {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <h1>Playbook System Chart Preview</h1>
    <p>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
"""
        
        for mmd_file in sorted(mermaid_files):
            content = mmd_file.read_text()
            
            # Extract title and chart content
            lines = content.split('\n')
            title = lines[0].replace('# ', '') if lines[0].startswith('#') else mmd_file.stem
            
            # Find mermaid content (between %%{ and the end or next comment)
            mermaid_start = -1
            mermaid_lines = []
            for i, line in enumerate(lines):
                if '%%{' in line or 'graph' in line or 'pie' in line or 'xychart' in line:
                    mermaid_start = i
                elif mermaid_start >= 0 and not line.startswith('#'):
                    mermaid_lines.append(line)
                elif mermaid_start >= 0 and line.startswith('#'):
                    break
            
            mermaid_content = '\n'.join(mermaid_lines) if mermaid_lines else content
            
            # Extract metadata
            chart_type = "unknown"
            for line in lines[:10]:
                if "Chart Type:" in line:
                    chart_type = line.split("Chart Type:")[1].strip().replace('#', '')
                    break
            
            html_content += f"""
    <div class="chart-container">
        <div class="chart-title">{title}</div>
        <div class="mermaid">
{mermaid_content}
        </div>
        <div class="metadata">
            File: {mmd_file.name} | Type: {chart_type}
        </div>
    </div>
"""
        
        html_content += """
    <h2>Summary</h2>
    <div class="chart-container">
        <p>Total charts generated: """ + str(len(mermaid_files)) + """</p>
        <p>Preview shows only Mermaid charts. Check .py files for Python/matplotlib charts.</p>
    </div>
</body>
</html>"""
        
        preview_file = self.output_dir / "preview.html"
        preview_file.write_text(html_content)
        print(f"\n✓ Created HTML preview: {preview_file}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("PLAYBOOK CHART GENERATION SUMMARY")
        print("="*60)
        
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        
        print(f"\nTotal tests: {len(self.results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            print("\n✓ Successful Charts:")
            for r in successful:
                match_indicator = "✓" if r.get('match') else "≈"
                print(f"  [{r['id']}] {r['name']}")
                print(f"    Expected: {r.get('expected', 'N/A')} | Actual: {r['actual']} {match_indicator}")
                print(f"    Format: {r['format']}")
        
        if failed:
            print("\n✗ Failed Charts:")
            for r in failed:
                print(f"  [{r['id']}] {r['name']}")
                print(f"    Error: {r.get('error', 'Unknown')[:100]}")
        
        # Type matching statistics
        if successful:
            matches = [r for r in successful if r.get('match')]
            print(f"\nType Match Rate: {len(matches)}/{len(successful)} "
                  f"({(len(matches)/len(successful)*100):.1f}%)")
        
        print(f"\nOutputs saved to: {self.output_dir.absolute()}")
        print("="*60)
    
    async def run_all_tests(self):
        """Run all test cases."""
        print("="*60)
        print("PLAYBOOK SYSTEM CHART GENERATION TEST")
        print("="*60)
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Using playbook system: {os.getenv('USE_PLAYBOOK_SYSTEM')}")
        
        test_cases = self.get_test_cases()
        
        for test_case in test_cases:
            await self.generate_chart(test_case)
            # Small delay between requests
            await asyncio.sleep(1)
        
        # Create HTML preview
        self.create_html_preview()
        
        # Print summary
        self.print_summary()


async def main():
    """Main entry point."""
    tester = PlaybookChartTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        import traceback
        traceback.print_exc()