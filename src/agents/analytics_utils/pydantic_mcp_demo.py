"""
Pydantic MCP Server Demo
========================

Complete working example demonstrating chart generation with real image output
using the pydantic MCP server integration.

This demo shows:
1. Server initialization and health check
2. Basic Python code execution
3. Chart generation with multiple chart types
4. Base64 image output handling
5. Real PNG file creation
6. Error handling and logging
7. Performance testing

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import asyncio
import base64
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PydanticMCPDemo:
    """
    Comprehensive demonstration of the pydantic MCP server capabilities.
    """
    
    def __init__(self, output_dir: str = "mcp_demo_output"):
        """
        Initialize the demo.
        
        Args:
            output_dir: Directory to save demo outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Import our MCP integration
        try:
            from .mcp_integration import get_mcp_integration
            from .pydantic_mcp_server import get_server, create_chart_with_mcp, execute_python_with_mcp
            
            self.mcp_integration = get_mcp_integration()
            self.server = get_server()
            
            # Import convenience functions
            self.create_chart_with_mcp = create_chart_with_mcp
            self.execute_python_with_mcp = execute_python_with_mcp
            
            logger.info("MCP integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP integration: {e}")
            raise
    
    def save_base64_image(self, base64_data: str, filename: str) -> str:
        """
        Save base64 image data to a PNG file.
        
        Args:
            base64_data: Base64 encoded image
            filename: Output filename
            
        Returns:
            Full path to saved file
        """
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_data)
            
            # Save to file
            output_path = self.output_dir / filename
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"Saved image: {output_path} ({len(image_bytes)} bytes)")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save image {filename}: {e}")
            raise
    
    async def test_server_health(self) -> Dict[str, Any]:
        """
        Test server health and capabilities.
        
        Returns:
            Health check results
        """
        print("\n" + "="*50)
        print("🔬 TESTING SERVER HEALTH")
        print("="*50)
        
        try:
            # Test MCP integration backend info
            backend_info = self.mcp_integration.get_backend_info()
            print(f"Backend Type: {backend_info['backend_type']}")
            print(f"Available: {backend_info['is_available']}")
            print(f"Capabilities: {backend_info['capabilities']}")
            
            # Test availability
            available = await self.mcp_integration.test_availability()
            print(f"Availability Test: {'✅ PASSED' if available else '❌ FAILED'}")
            
            # Server-specific health check
            if self.mcp_integration.backend_type == "pydantic_server":
                health = await self.server.health_check()
                print(f"Server Health: {health['status']}")
                print(f"Python Version: {health['python_version'].split()[0]}")
                print(f"Plotting Enabled: {health['plotting_enabled']}")
                
                if 'test_execution' in health:
                    print(f"Execution Test: {'✅' if health['test_execution']['success'] else '❌'}")
                
                if 'test_plotting' in health:
                    print(f"Plotting Test: {'✅' if health['test_plotting']['success'] else '❌'}")
                    if health['test_plotting'].get('plots_generated', 0) > 0:
                        print(f"Test Charts: {health['test_plotting']['plots_generated']} generated")
                
                return health
            
            else:
                print("Using external MCP backend")
                return {"status": "healthy", "backend": backend_info['backend_type']}
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            print(f"❌ Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def demo_basic_execution(self) -> bool:
        """
        Demonstrate basic Python code execution.
        
        Returns:
            True if successful
        """
        print("\n" + "="*50)
        print("🐍 TESTING BASIC PYTHON EXECUTION")
        print("="*50)
        
        test_cases = [
            {
                "name": "Simple Math",
                "code": """
result = 2 + 2
print(f"2 + 2 = {result}")
"""
            },
            {
                "name": "NumPy Operations",
                "code": """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
mean = np.mean(arr)
std = np.std(arr)
print(f"Array: {arr}")
print(f"Mean: {mean:.2f}")
print(f"Std Dev: {std:.2f}")
"""
            },
            {
                "name": "Data Processing",
                "code": """
import json
import datetime

data = {
    "timestamp": datetime.datetime.now().isoformat(),
    "values": [10, 20, 30, 40, 50],
    "metadata": {"version": "1.0", "source": "demo"}
}

total = sum(data["values"])
average = total / len(data["values"])

print(f"Total: {total}")
print(f"Average: {average}")
print(f"Data: {json.dumps(data, indent=2)}")
"""
            }
        ]
        
        all_successful = True
        
        for test_case in test_cases:
            print(f"\n📋 Running: {test_case['name']}")
            try:
                result = await self.execute_python_with_mcp(test_case['code'])
                
                if result.success:
                    print(f"✅ Success (Time: {result.execution_time:.2f}s)")
                    if result.stdout:
                        print(f"Output:\n{result.stdout}")
                else:
                    print(f"❌ Failed: {result.error_message}")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                    all_successful = False
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                all_successful = False
        
        return all_successful
    
    async def demo_chart_generation(self) -> Dict[str, str]:
        """
        Demonstrate comprehensive chart generation.
        
        Returns:
            Dictionary mapping chart types to saved file paths
        """
        print("\n" + "="*50)
        print("📊 TESTING CHART GENERATION")
        print("="*50)
        
        chart_demos = [
            {
                "type": "bar",
                "title": "Quarterly Revenue",
                "data": {
                    "labels": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
                    "values": [120000, 135000, 142000, 158000]
                }
            },
            {
                "type": "line",
                "title": "Monthly Growth Rate",
                "data": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "values": [5.2, 6.1, 4.8, 7.3, 8.1, 6.9]
                }
            },
            {
                "type": "pie",
                "title": "Market Share Distribution",
                "data": {
                    "labels": ["Product A", "Product B", "Product C", "Product D"],
                    "values": [35, 28, 22, 15]
                }
            },
            {
                "type": "scatter",
                "title": "Sales vs Marketing Spend",
                "data": {
                    "labels": ["Data Points"],
                    "values": [100, 150, 200, 250, 300, 120, 180, 220, 280, 350]  # x, y pairs
                }
            },
            {
                "type": "histogram",
                "title": "Customer Age Distribution",
                "data": {
                    "labels": ["Ages"],
                    "values": [25, 32, 28, 45, 38, 29, 33, 41, 37, 26, 31, 44, 39, 27, 35, 42, 30, 36, 43, 34]
                }
            }
        ]
        
        saved_files = {}
        
        for demo in chart_demos:
            print(f"\n📈 Generating: {demo['title']} ({demo['type']})")
            
            try:
                result = await self.create_chart_with_mcp(
                    chart_type=demo['type'],
                    data=demo['data'],
                    title=demo['title']
                )
                
                if result.success and result.plots:
                    # Save the chart
                    filename = f"chart_{demo['type']}_{datetime.now().strftime('%H%M%S')}.png"
                    saved_path = self.save_base64_image(result.plots[0], filename)
                    saved_files[demo['type']] = saved_path
                    
                    print(f"✅ Generated and saved: {filename}")
                    print(f"   Execution time: {result.execution_time:.2f}s")
                    print(f"   Image size: {len(result.plots[0])} base64 chars")
                    
                else:
                    print(f"❌ Failed: {result.error_message if not result.success else 'No plots generated'}")
                    if result.stderr:
                        print(f"   Error: {result.stderr}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")
        
        return saved_files
    
    async def demo_custom_chart_code(self) -> str:
        """
        Demonstrate custom chart generation with advanced Python code.
        
        Returns:
            Path to saved chart file
        """
        print("\n" + "="*50)
        print("🎨 TESTING CUSTOM CHART CODE")
        print("="*50)
        
        # Advanced custom chart with multiple subplots
        custom_code = """
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta

# Set style
plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
sns.set_palette("husl")

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Advanced Analytics Dashboard - Generated by Pydantic MCP Server', fontsize=16, fontweight='bold')

# 1. Sales Trend with Confidence Band
dates = [datetime(2024, 1, 1) + timedelta(days=i*30) for i in range(12)]
sales = np.array([100, 105, 110, 108, 115, 120, 125, 130, 128, 135, 140, 145])
noise = np.random.normal(0, 5, len(sales))
upper_bound = sales + np.abs(noise) + 10
lower_bound = sales - np.abs(noise) - 5

ax1.plot(dates, sales, 'b-', linewidth=2, label='Actual Sales')
ax1.fill_between(dates, lower_bound, upper_bound, alpha=0.3, color='blue', label='Confidence Band')
ax1.set_title('Sales Trend with Confidence Band')
ax1.set_ylabel('Sales (K$)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Market Share Donut Chart
categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Others']
sizes = [30, 25, 20, 15, 10]
colors = plt.cm.Set3(np.linspace(0, 1, len(sizes)))
wedges, texts, autotexts = ax2.pie(sizes, labels=categories, autopct='%1.1f%%', 
                                  colors=colors, startangle=90, pctdistance=0.85)
centre_circle = plt.Circle((0,0), 0.70, fc='white')
ax2.add_artist(centre_circle)
ax2.set_title('Market Share Distribution')

# 3. Performance Heatmap
departments = ['Sales', 'Marketing', 'Engineering', 'Support', 'Finance']
metrics = ['Q1', 'Q2', 'Q3', 'Q4']
performance = np.random.rand(len(departments), len(metrics)) * 100
im = ax3.imshow(performance, cmap='RdYlGn', aspect='auto')
ax3.set_xticks(np.arange(len(metrics)))
ax3.set_yticks(np.arange(len(departments)))
ax3.set_xticklabels(metrics)
ax3.set_yticklabels(departments)
ax3.set_title('Department Performance Heatmap (%)')

# Add text annotations
for i in range(len(departments)):
    for j in range(len(metrics)):
        text = ax3.text(j, i, f'{performance[i, j]:.0f}', 
                       ha="center", va="center", color="black", fontweight='bold')

# 4. Multi-series Line Chart
x = np.linspace(0, 10, 100)
y1 = np.sin(x) * np.exp(-x/10) * 50 + 100
y2 = np.cos(x) * np.exp(-x/15) * 30 + 80
y3 = np.sin(x*2) * np.exp(-x/8) * 25 + 90

ax4.plot(x, y1, 'r-', linewidth=2, label='Revenue', alpha=0.8)
ax4.plot(x, y2, 'g-', linewidth=2, label='Profit', alpha=0.8)
ax4.plot(x, y3, 'b-', linewidth=2, label='Growth Rate', alpha=0.8)
ax4.fill_between(x, y1, alpha=0.3, color='red')
ax4.fill_between(x, y2, alpha=0.3, color='green')
ax4.set_title('Multi-Metric Trend Analysis')
ax4.set_xlabel('Time Period')
ax4.set_ylabel('Value')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Improve layout
plt.tight_layout()
plt.subplots_adjust(top=0.93)

# Add footer
fig.text(0.5, 0.02, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by Pydantic MCP Server', 
         ha='center', fontsize=10, style='italic')

print("Advanced dashboard chart generated successfully!")
"""
        
        print("🎯 Generating advanced analytics dashboard...")
        
        try:
            result = await self.execute_python_with_mcp(custom_code)
            
            if result.success:
                print(f"✅ Custom code executed successfully")
                print(f"   Execution time: {result.execution_time:.2f}s")
                
                if result.plots:
                    filename = f"advanced_dashboard_{datetime.now().strftime('%H%M%S')}.png"
                    saved_path = self.save_base64_image(result.plots[0], filename)
                    print(f"   Advanced dashboard saved: {filename}")
                    return saved_path
                else:
                    print("⚠️  Code executed but no plots captured")
                    
                if result.stdout:
                    print(f"Output: {result.stdout}")
            
            else:
                print(f"❌ Custom code execution failed: {result.error_message}")
                if result.stderr:
                    print(f"Error details: {result.stderr}")
                    
        except Exception as e:
            print(f"❌ Exception in custom code: {e}")
        
        return ""
    
    async def demo_performance_test(self) -> Dict[str, float]:
        """
        Test performance with multiple concurrent operations.
        
        Returns:
            Performance metrics
        """
        print("\n" + "="*50)
        print("⚡ TESTING PERFORMANCE")
        print("="*50)
        
        # Simple performance test codes
        perf_tests = [
            "result = sum(range(10000))\nprint(f'Sum: {result}')",
            "import numpy as np\narr = np.random.rand(1000, 1000)\nresult = np.mean(arr)\nprint(f'Mean: {result:.4f}')",
            "import matplotlib.pyplot as plt\nplt.figure(figsize=(8,6))\nplt.plot([1,2,3,4], [1,4,2,3])\nplt.title('Perf Test')\nplt.show()",
            "data = list(range(1000))\nfiltered = [x for x in data if x % 2 == 0]\nprint(f'Filtered: {len(filtered)} items')",
            "import json\ndata = {'test': list(range(100))}\njson_str = json.dumps(data)\nprint(f'JSON length: {len(json_str)}')"
        ]
        
        print(f"🏃 Running {len(perf_tests)} concurrent performance tests...")
        
        start_time = datetime.now()
        
        # Run tests concurrently
        tasks = [self.execute_python_with_mcp(code) for code in perf_tests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Analyze results
        successful = 0
        failed = 0
        total_execution_time = 0
        charts_generated = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Test {i+1}: Exception - {result}")
                failed += 1
            else:
                if result.success:
                    print(f"✅ Test {i+1}: Success ({result.execution_time:.2f}s)")
                    successful += 1
                    total_execution_time += result.execution_time
                    if result.plots:
                        charts_generated += len(result.plots)
                else:
                    print(f"❌ Test {i+1}: Failed - {result.error_message}")
                    failed += 1
        
        metrics = {
            "total_wall_time": total_time,
            "total_execution_time": total_execution_time,
            "successful_tests": successful,
            "failed_tests": failed,
            "charts_generated": charts_generated,
            "average_execution_time": total_execution_time / max(successful, 1),
            "tests_per_second": len(perf_tests) / total_time
        }
        
        print(f"\n📊 Performance Results:")
        print(f"   Total wall time: {metrics['total_wall_time']:.2f}s")
        print(f"   Total execution time: {metrics['total_execution_time']:.2f}s")
        print(f"   Successful tests: {metrics['successful_tests']}/{len(perf_tests)}")
        print(f"   Charts generated: {metrics['charts_generated']}")
        print(f"   Average execution time: {metrics['average_execution_time']:.2f}s")
        print(f"   Tests per second: {metrics['tests_per_second']:.2f}")
        
        return metrics
    
    def generate_report(self, 
                       health_results: Dict,
                       basic_execution_success: bool,
                       chart_files: Dict[str, str],
                       custom_chart_file: str,
                       performance_metrics: Dict) -> str:
        """
        Generate a comprehensive demo report.
        
        Args:
            health_results: Server health check results
            basic_execution_success: Whether basic execution tests passed
            chart_files: Generated chart file paths
            custom_chart_file: Advanced dashboard file path
            performance_metrics: Performance test results
            
        Returns:
            Path to the generated report file
        """
        report = {
            "demo_metadata": {
                "timestamp": datetime.now().isoformat(),
                "output_directory": str(self.output_dir),
                "python_version": sys.version,
            },
            "server_health": health_results,
            "basic_execution": {
                "success": basic_execution_success,
                "tests_run": 3
            },
            "chart_generation": {
                "charts_generated": len(chart_files),
                "chart_types": list(chart_files.keys()),
                "files": chart_files
            },
            "custom_chart": {
                "generated": bool(custom_chart_file),
                "file": custom_chart_file
            },
            "performance": performance_metrics,
            "summary": {
                "overall_success": (
                    health_results.get("status") == "healthy" and
                    basic_execution_success and
                    len(chart_files) > 0 and
                    performance_metrics.get("successful_tests", 0) > 0
                ),
                "total_charts": len(chart_files) + (1 if custom_chart_file else 0),
                "total_files_created": len(chart_files) + (1 if custom_chart_file else 0) + 1  # +1 for report
            }
        }
        
        # Save report
        report_file = self.output_dir / f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Demo report saved: {report_file}")
        return str(report_file)
    
    async def run_complete_demo(self) -> bool:
        """
        Run the complete demonstration suite.
        
        Returns:
            True if overall demo was successful
        """
        print("🚀 Starting Pydantic MCP Server Complete Demo")
        print("=" * 80)
        
        try:
            # 1. Health check
            health_results = await self.test_server_health()
            
            # 2. Basic execution tests
            basic_success = await self.demo_basic_execution()
            
            # 3. Chart generation demos
            chart_files = await self.demo_chart_generation()
            
            # 4. Custom advanced chart
            custom_chart = await self.demo_custom_chart_code()
            
            # 5. Performance testing
            performance = await self.demo_performance_test()
            
            # 6. Generate report
            report_file = self.generate_report(
                health_results, basic_success, chart_files, custom_chart, performance
            )
            
            # Summary
            print("\n" + "="*80)
            print("📊 DEMO SUMMARY")
            print("="*80)
            
            overall_success = (
                health_results.get("status") == "healthy" and
                basic_success and
                len(chart_files) > 0
            )
            
            print(f"Overall Status: {'✅ SUCCESS' if overall_success else '❌ PARTIAL SUCCESS'}")
            print(f"Server Health: {'✅' if health_results.get('status') == 'healthy' else '❌'}")
            print(f"Basic Execution: {'✅' if basic_success else '❌'}")
            print(f"Charts Generated: {len(chart_files)}")
            print(f"Custom Dashboard: {'✅' if custom_chart else '❌'}")
            print(f"Performance Tests: {performance.get('successful_tests', 0)}/{performance.get('successful_tests', 0) + performance.get('failed_tests', 0)}")
            print(f"Output Directory: {self.output_dir}")
            print(f"Report File: {Path(report_file).name}")
            
            if chart_files:
                print("\nGenerated Charts:")
                for chart_type, file_path in chart_files.items():
                    print(f"  📈 {chart_type}: {Path(file_path).name}")
            
            if custom_chart:
                print(f"  🎨 Advanced Dashboard: {Path(custom_chart).name}")
            
            return overall_success
            
        except Exception as e:
            logger.error(f"Demo failed with exception: {e}")
            print(f"\n❌ Demo failed with exception: {e}")
            return False


async def main():
    """Main demo function."""
    print("🎯 Pydantic MCP Server Demo Starting...")
    
    # Create demo instance
    demo = PydanticMCPDemo()
    
    # Run complete demo
    success = await demo.run_complete_demo()
    
    # Exit with appropriate code
    exit_code = 0 if success else 1
    print(f"\n🏁 Demo completed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    # Run the demo
    exit_code = asyncio.run(main())
    sys.exit(exit_code)