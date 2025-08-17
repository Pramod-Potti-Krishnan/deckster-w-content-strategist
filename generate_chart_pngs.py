#!/usr/bin/env python3
"""
Generate PNG files from chart code
===================================

Executes Python chart code and converts Mermaid to images.
"""

import os
import sys
import re
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Setup paths
output_dir = Path("playbook_test_outputs")
png_dir = output_dir / "png_images"
png_dir.mkdir(exist_ok=True)

def execute_python_chart(py_file, png_file):
    """Execute Python chart code and save as PNG."""
    print(f"Processing {py_file.name}...")
    
    try:
        # Read the file
        content = py_file.read_text()
        
        # Extract just the code part (after "Chart Code" marker)
        code_match = re.search(r'# =+ Chart Code =+\n\n(.*?)(?:\n# =+|$)', content, re.DOTALL)
        if not code_match:
            print(f"  ⚠️  Could not find chart code in {py_file.name}")
            return False
        
        chart_code = code_match.group(1)
        
        # Fix the code - replace plt.show() with plt.savefig()
        chart_code = chart_code.replace('plt.show()', '')
        chart_code = chart_code.replace('plt.tight_layout()', 'plt.tight_layout()')
        # Fix seaborn style issue
        chart_code = chart_code.replace("plt.style.use('seaborn')", "plt.style.use('seaborn-v0_8')")
        
        # Create a clean namespace for execution
        namespace = {
            'plt': plt,
            'np': np,
            'sns': sns,
            'matplotlib': matplotlib
        }
        
        # Execute the code
        exec(chart_code, namespace)
        
        # Save the figure
        plt.savefig(png_file, dpi=100, bbox_inches='tight')
        plt.close('all')  # Close all figures to free memory
        
        print(f"  ✅ Saved: {png_file.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        plt.close('all')  # Ensure figures are closed even on error
        return False


def convert_mermaid_to_png(mmd_file, png_file):
    """Convert Mermaid chart to PNG using matplotlib fallback."""
    print(f"Processing {mmd_file.name}...")
    
    try:
        content = mmd_file.read_text()
        
        # Extract data from mermaid chart
        # Look for bar chart data
        bar_match = re.search(r'bar \[([\d., ]+)\]', content)
        labels_match = re.search(r'x-axis \[(.*?)\]', content)
        title_match = re.search(r'title "(.*?)"', content)
        
        if bar_match and labels_match:
            # Parse the data
            values_str = bar_match.group(1)
            values = [float(v.strip()) for v in values_str.split(',')]
            
            labels_str = labels_match.group(1)
            # Remove quotes and split
            labels = [l.strip().strip('"').replace('Category ', 'Cat ') for l in labels_str.split(',')]
            
            title = title_match.group(1) if title_match else mmd_file.stem
            
            # Create bar chart with matplotlib
            plt.figure(figsize=(10, 6))
            plt.bar(range(len(values)), values, color='skyblue', edgecolor='navy', alpha=0.7)
            plt.xticks(range(len(values)), labels, rotation=45, ha='right')
            plt.title(title)
            plt.ylabel('Value')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            plt.savefig(png_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            print(f"  ✅ Saved: {png_file.name}")
            return True
        else:
            print(f"  ⚠️  Could not parse Mermaid data from {mmd_file.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        plt.close('all')
        return False


def create_html_gallery():
    """Create HTML gallery with PNG images."""
    png_files = sorted(png_dir.glob("*.png"))
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Playbook Charts - PNG Gallery</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .chart-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chart-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            font-weight: bold;
        }
        .chart-image {
            padding: 20px;
            text-align: center;
            background: white;
        }
        .chart-image img {
            max-width: 100%;
            height: auto;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success { color: #4CAF50; }
        .warning { color: #FF9800; }
        .error { color: #f44336; }
    </style>
</head>
<body>
    <h1>📊 Playbook System - Chart Gallery</h1>
    
    <div class="stats">
        <h2>Generation Statistics</h2>
        <p><span class="success">✅ Successfully Generated:</span> """ + str(len(png_files)) + """ charts</p>
        <p>All charts have been converted to PNG format for easy viewing.</p>
    </div>
    
    <div class="gallery">
"""
    
    for png_file in png_files:
        # Extract chart name from filename
        chart_name = png_file.stem.replace('_', ' ').title()
        
        html += f"""
        <div class="chart-container">
            <div class="chart-header">{chart_name}</div>
            <div class="chart-image">
                <img src="png_images/{png_file.name}" alt="{chart_name}">
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>"""
    
    gallery_file = output_dir / "chart_gallery.html"
    gallery_file.write_text(html)
    print(f"\n✅ Created gallery: {gallery_file}")
    return gallery_file


def main():
    """Main execution."""
    print("="*60)
    print("GENERATING PNG FILES FROM CHARTS")
    print("="*60)
    
    # Process Python charts
    py_files = list(output_dir.glob("*.py"))
    print(f"\nFound {len(py_files)} Python chart files")
    
    py_success = 0
    for py_file in py_files:
        png_file = png_dir / f"{py_file.stem}.png"
        if execute_python_chart(py_file, png_file):
            py_success += 1
    
    # Process Mermaid charts
    mmd_files = list(output_dir.glob("*.mmd"))
    print(f"\nFound {len(mmd_files)} Mermaid chart files")
    
    mmd_success = 0
    for mmd_file in mmd_files:
        png_file = png_dir / f"{mmd_file.stem}.png"
        if convert_mermaid_to_png(mmd_file, png_file):
            mmd_success += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Python charts converted: {py_success}/{len(py_files)}")
    print(f"Mermaid charts converted: {mmd_success}/{len(mmd_files)}")
    print(f"Total PNGs created: {py_success + mmd_success}")
    
    # Create HTML gallery
    gallery_path = create_html_gallery()
    
    print("\n✅ PNG generation complete!")
    print(f"📁 Images saved to: {png_dir.absolute()}")
    print(f"🌐 View gallery at: {gallery_path.absolute()}")
    
    return gallery_path


if __name__ == "__main__":
    gallery = main()
    # Try to open the gallery
    os.system(f"open '{gallery}'")