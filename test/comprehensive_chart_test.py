#!/usr/bin/env python
"""
Comprehensive Chart Test Suite
===============================

Tests all supported chart types and generates an HTML report with embedded images.
"""

import os
import sys
import asyncio
import base64
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor


class ChartTestSuite:
    """Comprehensive test suite for all chart types."""
    
    def __init__(self):
        self.test_dir = Path("test/chart_outputs")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Define all test cases for different chart types."""
        return [
            # Mermaid Charts (Simple)
            {
                "category": "Mermaid Charts",
                "title": "📈 Line Chart - Monthly Sales Trend",
                "description": "Monthly sales data: Jan $45K, Feb $52K, Mar $48K, Apr $61K, May $58K, Jun $72K, Jul $69K, Aug $75K, Sep $82K, Oct $79K, Nov $88K, Dec $95K",
                "chart_type": "line",
                "expected_format": "mermaid"
            },
            {
                "category": "Mermaid Charts",
                "title": "📊 Bar Chart - Product Categories",
                "description": "Sales by category: Electronics $450K, Clothing $320K, Home & Garden $280K, Sports $195K, Books $155K, Toys $210K",
                "chart_type": "bar",
                "expected_format": "mermaid"
            },
            {
                "category": "Mermaid Charts",
                "title": "🥧 Pie Chart - Market Share",
                "description": "Market share distribution: Apple 31%, Samsung 23%, Google 18%, Microsoft 15%, Others 13%",
                "chart_type": "pie",
                "expected_format": "mermaid"
            },
            {
                "category": "Mermaid Charts",
                "title": "🎯 Radar Chart - Skills Assessment",
                "description": "Employee skills: Technical 85, Communication 75, Leadership 80, Problem Solving 90, Teamwork 88, Creativity 72",
                "chart_type": "radar",
                "expected_format": "mermaid"
            },
            
            # Python/Matplotlib Charts (Complex)
            {
                "category": "Statistical Charts",
                "title": "🔵 Scatter Plot - Sales vs Marketing Spend",
                "description": "Marketing spend (thousands) vs sales (thousands): (10, 45), (15, 58), (20, 72), (25, 85), (30, 98), (35, 112), (40, 125), (45, 138), (50, 145), (55, 155)",
                "chart_type": "scatter",
                "expected_format": "base64"
            },
            {
                "category": "Statistical Charts",
                "title": "📊 Histogram - Customer Age Distribution",
                "description": "Generate age distribution for 1000 customers with mean age 38 and standard deviation 12, ranging from 18 to 65 years",
                "chart_type": "histogram",
                "expected_format": "base64"
            },
            {
                "category": "Statistical Charts",
                "title": "📦 Box Plot - Department Performance",
                "description": "Quarterly performance scores by department: Sales [78, 82, 85, 88, 91], Marketing [72, 75, 78, 80, 83], IT [85, 87, 89, 91, 93], HR [70, 73, 75, 77, 80], Finance [80, 82, 84, 86, 88]",
                "chart_type": "box",
                "expected_format": "base64"
            },
            
            # Advanced Visualizations
            {
                "category": "Advanced Charts",
                "title": "🔥 Heatmap - Correlation Matrix",
                "description": "Create a 6x6 correlation heatmap for metrics: Revenue, Costs, Profit, Customers, Satisfaction, Retention with realistic correlation values",
                "chart_type": "heatmap",
                "expected_format": "base64"
            },
            {
                "category": "Advanced Charts",
                "title": "🏔️ Area Chart - Website Traffic",
                "description": "Daily website traffic (thousands): Mon 12, Tue 15, Wed 18, Thu 22, Fri 28, Sat 35, Sun 30",
                "chart_type": "area",
                "expected_format": "base64"
            },
            {
                "category": "Advanced Charts",
                "title": "⚫ Bubble Chart - Project Analysis",
                "description": "Project data (budget in $K, duration in months, team size): Project A (100, 6, 5), Project B (150, 9, 8), Project C (200, 12, 10), Project D (80, 4, 3), Project E (120, 7, 6)",
                "chart_type": "bubble",
                "expected_format": "base64"
            },
            {
                "category": "Advanced Charts",
                "title": "💧 Waterfall Chart - Profit Breakdown",
                "description": "Profit waterfall: Starting Revenue $500K, Product Sales +$200K, Services +$150K, Operating Costs -$180K, Marketing -$50K, R&D -$70K, Final Profit $550K",
                "chart_type": "waterfall",
                "expected_format": "base64"
            },
            {
                "category": "Advanced Charts",
                "title": "🌳 Treemap - Budget Allocation",
                "description": "Department budgets: Engineering $2.5M, Sales $1.8M, Marketing $1.2M, Operations $900K, HR $600K, Legal $400K, Finance $500K",
                "chart_type": "treemap",
                "expected_format": "base64"
            },
            
            # Special Cases
            {
                "category": "Data Parsing Tests",
                "title": "💰 Quarterly Revenue with Exact Values",
                "description": "Q1 2024 revenue was exactly $2,456,789. Q2 reached $2,891,234. Q3 hit $3,123,456. Q4 closed at $3,567,890. Show the growth trend.",
                "chart_type": "line",
                "expected_format": "mermaid"
            },
            {
                "category": "Data Parsing Tests",
                "title": "📈 Percentage Growth Analysis",
                "description": "Year-over-year growth rates: 2019: 12.5%, 2020: -8.3%, 2021: 15.7%, 2022: 22.4%, 2023: 18.9%, 2024: 25.6%",
                "chart_type": "bar",
                "expected_format": "mermaid"
            },
            {
                "category": "Complex Visualizations",
                "title": "🌐 Multi-Series Line Chart",
                "description": "Compare three product lines over 6 months. Product A: [100, 110, 125, 140, 155, 170]. Product B: [80, 85, 92, 98, 105, 115]. Product C: [120, 118, 122, 130, 138, 145]",
                "chart_type": "line",
                "expected_format": "mermaid"
            }
        ]
    
    async def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case."""
        print(f"\n  Testing: {test_case['title']}")
        print(f"    Type: {test_case['chart_type']}")
        
        start_time = datetime.now()
        
        try:
            result = await create_analytics(
                test_case['description'],
                title=test_case['title'].split(' - ')[1] if ' - ' in test_case['title'] else test_case['title'],
                chart_type=test_case['chart_type'],
                mcp_tool=pydantic_mcp_executor
            )
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                "test_case": test_case,
                "success": result['success'],
                "format": result['format'],
                "elapsed_time": elapsed_time,
                "expected_format": test_case['expected_format'],
                "format_match": result['format'] == test_case['expected_format'],
                "content": result.get('content', ''),
                "insights": result.get('insights', []),
                "data_points": len(result.get('data', [])),
                "metadata": result.get('metadata', {})
            }
            
            # Save chart content
            if result['format'] == 'base64':
                # Save PNG image
                img_data = base64.b64decode(result['content'])
                filename = f"{test_case['chart_type']}_{self.timestamp}_{len(self.results)}.png"
                filepath = self.test_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(img_data)
                test_result['image_file'] = str(filepath)
                test_result['image_size'] = len(img_data)
                print(f"    ✅ Generated {len(img_data):,} byte image")
            elif result['format'] == 'mermaid':
                # Save Mermaid code
                filename = f"{test_case['chart_type']}_{self.timestamp}_{len(self.results)}.mmd"
                filepath = self.test_dir / filename
                with open(filepath, 'w') as f:
                    f.write(result['content'])
                test_result['mermaid_file'] = str(filepath)
                print(f"    ✅ Generated Mermaid chart")
            
            return test_result
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return {
                "test_case": test_case,
                "success": False,
                "error": str(e),
                "elapsed_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def run_all_tests(self):
        """Run all test cases."""
        print("\n" + "="*80)
        print("COMPREHENSIVE CHART TEST SUITE")
        print("="*80)
        
        test_cases = self.get_test_cases()
        print(f"\n📊 Running {len(test_cases)} chart tests...")
        
        for test_case in test_cases:
            result = await self.run_test(test_case)
            self.results.append(result)
        
        self.generate_summary()
        self.generate_html_report()
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        format_matches = sum(1 for r in self.results if r.get('format_match', False))
        
        print(f"\n📊 Total Tests: {total}")
        print(f"✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")
        print(f"🎯 Format Matches: {format_matches}/{total} ({format_matches/total*100:.1f}%)")
        
        # By category
        categories = {}
        for result in self.results:
            cat = result['test_case']['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'success': 0}
            categories[cat]['total'] += 1
            if result.get('success', False):
                categories[cat]['success'] += 1
        
        print("\n📂 By Category:")
        for cat, stats in categories.items():
            print(f"  {cat}: {stats['success']}/{stats['total']} successful")
        
        # By chart type
        chart_types = {}
        for result in self.results:
            ct = result['test_case']['chart_type']
            if ct not in chart_types:
                chart_types[ct] = {'total': 0, 'success': 0, 'base64': 0, 'mermaid': 0}
            chart_types[ct]['total'] += 1
            if result.get('success', False):
                chart_types[ct]['success'] += 1
                if result.get('format') == 'base64':
                    chart_types[ct]['base64'] += 1
                elif result.get('format') == 'mermaid':
                    chart_types[ct]['mermaid'] += 1
        
        print("\n📈 By Chart Type:")
        for ct, stats in chart_types.items():
            print(f"  {ct}: {stats['success']}/{stats['total']} (Images: {stats['base64']}, Mermaid: {stats['mermaid']})")
        
        # Timing
        avg_time = sum(r.get('elapsed_time', 0) for r in self.results) / len(self.results)
        print(f"\n⏱️ Average Generation Time: {avg_time:.2f} seconds")
    
    def generate_html_report(self):
        """Generate an HTML report with all charts."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Chart Test Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .category-section {
            margin-bottom: 40px;
        }
        
        .category-header {
            background: white;
            padding: 20px 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .category-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 5px;
        }
        
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }
        
        .chart-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .chart-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .chart-header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .chart-title {
            font-size: 1.3em;
            margin-bottom: 8px;
        }
        
        .chart-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .badge {
            background: rgba(255,255,255,0.2);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        
        .chart-content {
            padding: 30px;
            background: #f8f9fa;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chart-content img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .mermaid {
            max-width: 100%;
        }
        
        .insights {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .insights-title {
            font-weight: bold;
            color: #666;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .insight-item {
            color: #333;
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
            font-size: 0.95em;
            line-height: 1.5;
        }
        
        .insight-item:before {
            content: "💡";
            position: absolute;
            left: 0;
        }
        
        .error-card {
            background: #fee;
            border: 2px solid #fcc;
        }
        
        .error-message {
            color: #c00;
            padding: 20px;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .success-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .success-true {
            background: #4caf50;
        }
        
        .success-false {
            background: #f44336;
        }
        
        footer {
            text-align: center;
            padding: 40px;
            color: white;
            margin-top: 50px;
        }
        
        .description {
            padding: 15px 20px;
            background: white;
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Analytics Chart Test Report</h1>
            <p class="subtitle">Comprehensive test of all supported chart types with pydantic MCP execution</p>
            <p class="subtitle" style="margin-top: 10px; color: #999;">Generated: {timestamp}</p>
            
            <div class="summary">
                <div class="stat-card">
                    <div class="stat-value">{total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #4caf50, #45a049);">
                    <div class="stat-value">{successful_tests}</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #ff6b6b, #ff5252);">
                    <div class="stat-value">{failed_tests}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #4ecdc4, #44a8a0);">
                    <div class="stat-value">{success_rate}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
                    <div class="stat-value">{png_count}</div>
                    <div class="stat-label">PNG Images</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #fa709a, #fee140);">
                    <div class="stat-value">{mermaid_count}</div>
                    <div class="stat-label">Mermaid Charts</div>
                </div>
            </div>
        </header>
        
        {category_sections}
        
        <footer>
            <p>🚀 Powered by Pydantic MCP Server</p>
            <p style="margin-top: 10px; opacity: 0.8;">Analytics Agent with Real Python Execution</p>
        </footer>
    </div>
    
    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#667eea',
                primaryTextColor: '#fff',
                primaryBorderColor: '#7c3aed',
                lineColor: '#5a67d8',
                secondaryColor: '#764ba2',
                tertiaryColor: '#f3f4f6'
            }
        });
    </script>
</body>
</html>
"""
        
        # Group results by category
        categories = {}
        for result in self.results:
            cat = result['test_case']['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        # Generate category sections
        category_sections = []
        for category, results in categories.items():
            section_html = f"""
        <div class="category-section">
            <div class="category-header">
                <h2 class="category-title">{category}</h2>
                <p style="color: #666;">{len(results)} charts in this category</p>
            </div>
            <div class="chart-grid">
"""
            
            for result in results:
                test_case = result['test_case']
                success_class = "success-true" if result.get('success', False) else "success-false"
                
                if result.get('success', False):
                    if result['format'] == 'base64':
                        # Embed PNG image
                        with open(result['image_file'], 'rb') as f:
                            img_base64 = base64.b64encode(f.read()).decode()
                        chart_content = f'<img src="data:image/png;base64,{img_base64}" alt="{test_case["title"]}">'
                    elif result['format'] == 'mermaid':
                        # Embed Mermaid diagram
                        chart_content = f'<div class="mermaid">{result["content"]}</div>'
                    else:
                        chart_content = '<p>Unknown format</p>'
                    
                    # Format insights
                    insights_html = ""
                    if result.get('insights'):
                        insights_html = """
                <div class="insights">
                    <div class="insights-title">Key Insights</div>
"""
                        for insight in result['insights'][:3]:
                            insights_html += f'                    <div class="insight-item">{insight}</div>\n'
                        insights_html += "                </div>"
                else:
                    chart_content = f'<div class="error-message">Error: {result.get("error", "Unknown error")}</div>'
                    insights_html = ""
                
                section_html += f"""
                <div class="chart-card {'error-card' if not result.get('success', False) else ''}">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span class="success-indicator {success_class}"></span>
                            {test_case['title']}
                        </div>
                        <div class="chart-meta">
                            <span class="badge">Type: {test_case['chart_type']}</span>
                            <span class="badge">Format: {result.get('format', 'N/A')}</span>
                            <span class="badge">Time: {result.get('elapsed_time', 0):.1f}s</span>
                        </div>
                    </div>
                    <div class="description">{test_case['description']}</div>
                    <div class="chart-content">
                        {chart_content}
                    </div>
                    {insights_html}
                </div>
"""
            
            section_html += """
            </div>
        </div>
"""
            category_sections.append(section_html)
        
        # Calculate statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        success_rate = int(successful_tests / total_tests * 100) if total_tests > 0 else 0
        png_count = sum(1 for r in self.results if r.get('format') == 'base64')
        mermaid_count = sum(1 for r in self.results if r.get('format') == 'mermaid')
        
        # Fill in the template
        html_content = html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            png_count=png_count,
            mermaid_count=mermaid_count,
            category_sections='\n'.join(category_sections)
        )
        
        # Save HTML report
        report_path = self.test_dir / f"chart_test_report_{self.timestamp}.html"
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        print(f"\n📄 HTML Report saved to: {report_path}")
        print(f"   Open in browser: file://{report_path.absolute()}")
        
        # Also save a simple index.html for easy access
        index_path = self.test_dir / "index.html"
        with open(index_path, 'w') as f:
            f.write(html_content)
        print(f"   Quick access: file://{index_path.absolute()}")


async def main():
    """Run the comprehensive test suite."""
    print("\n🚀 Starting Comprehensive Chart Test Suite...")
    print("   This will test all supported chart types")
    print("   and generate an HTML report with embedded visualizations")
    
    test_suite = ChartTestSuite()
    await test_suite.run_all_tests()
    
    print("\n✅ Test Suite Complete!")
    print("   Check the HTML report for visual results")


if __name__ == "__main__":
    asyncio.run(main())