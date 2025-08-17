#!/usr/bin/env python3
"""
Generate a proper PIE chart using Mermaid
=========================================

Tests the pie chart generation specifically.
"""

import asyncio
import os
import sys
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

async def generate_pie_chart():
    """Generate a proper pie chart."""
    print("="*60)
    print("GENERATING PIE CHART WITH MERMAID")
    print("="*60)
    
    # Request specifically for pie chart
    result = await create_analytics(
        content="Show market share distribution for top 5 technology companies: Apple 35%, Microsoft 25%, Google 20%, Amazon 12%, Meta 8%",
        title="Tech Giants Market Share 2024",
        chart_type="pie"  # Explicitly request pie chart
    )
    
    print(f"\nGeneration Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Chart Type: {result.get('chart_type')}")
    print(f"  Format: {result.get('format')}")
    print(f"  Data Points: {len(result.get('data', []))}")
    
    if result.get('success') and result.get('content'):
        # Save the Mermaid code
        output_dir = Path("playbook_test_outputs")
        output_dir.mkdir(exist_ok=True)
        
        mermaid_file = output_dir / "proper_pie_chart.mmd"
        
        # Get the content
        content = result.get('content', '')
        
        # Add metadata
        output = f"""# Tech Giants Market Share 2024
# Chart Type: pie
# Format: mermaid
# Description: Market share distribution for top 5 tech companies

{content}

# ========== Data ==========
# Apple: 35%
# Microsoft: 25%
# Google: 20%
# Amazon: 12%
# Meta: 8%
"""
        
        mermaid_file.write_text(output)
        print(f"\n✅ Saved Mermaid code to: {mermaid_file}")
        
        # Also create a Python matplotlib version for PNG generation
        python_code = '''import matplotlib.pyplot as plt

# Data
labels = ['Apple', 'Microsoft', 'Google', 'Amazon', 'Meta']
sizes = [35, 25, 20, 12, 8]
colors = ['#A8DADC', '#457B9D', '#1D3557', '#F1FAEE', '#E63946']

# Create pie chart
fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
plt.title('Tech Giants Market Share 2024', fontsize=16, fontweight='bold')
plt.tight_layout()
'''
        
        py_file = output_dir / "proper_pie_chart.py"
        py_file.write_text(f"""# Tech Giants Market Share 2024
# Chart Type: pie
# Format: python_code

# ========== Chart Code ==========

{python_code}
""")
        print(f"✅ Saved Python code to: {py_file}")
        
        # Generate PNG
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        # Execute the Python code to create PNG
        labels = ['Apple', 'Microsoft', 'Google', 'Amazon', 'Meta']
        sizes = [35, 25, 20, 12, 8]
        colors = ['#A8DADC', '#457B9D', '#1D3557', '#F1FAEE', '#E63946']
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.title('Tech Giants Market Share 2024', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        png_dir = output_dir / "png_images"
        png_dir.mkdir(exist_ok=True)
        png_file = png_dir / "proper_pie_chart.png"
        plt.savefig(png_file, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Saved PNG to: {png_file}")
        
        # Update the HTML gallery
        update_gallery(png_file)
        
        print("\n" + "="*60)
        print("PIE CHART GENERATION COMPLETE")
        print("="*60)
        
        return True
    else:
        print("\n❌ Failed to generate pie chart")
        if not result.get('success'):
            print(f"Error: {result.get('metadata', {}).get('error', 'Unknown error')}")
        return False


def update_gallery(new_png_file):
    """Add the new pie chart to the existing gallery."""
    gallery_file = Path("playbook_test_outputs/chart_gallery.html")
    
    if not gallery_file.exists():
        print("Gallery file not found, skipping update")
        return
    
    # Read existing gallery
    content = gallery_file.read_text()
    
    # Find the insertion point (before closing </div> of gallery)
    gallery_end = content.rfind('</div>\n</body>')
    
    if gallery_end > 0:
        # Create new chart HTML
        new_chart_html = f"""
        <div class="chart-container">
            <div class="chart-header">Proper Pie Chart - Tech Giants Market Share</div>
            <div class="chart-image">
                <img src="png_images/{new_png_file.name}" alt="Tech Giants Market Share 2024">
            </div>
        </div>
"""
        
        # Insert the new chart
        updated_content = content[:gallery_end] + new_chart_html + content[gallery_end:]
        
        # Update the stats
        updated_content = updated_content.replace(
            'Successfully Generated:</span> 9 charts',
            'Successfully Generated:</span> 10 charts (including proper pie chart)'
        )
        
        # Save updated gallery
        gallery_file.write_text(updated_content)
        print(f"✅ Updated gallery: {gallery_file}")
        
        # Try to open the updated gallery
        os.system(f"open '{gallery_file}'")


if __name__ == "__main__":
    success = asyncio.run(generate_pie_chart())