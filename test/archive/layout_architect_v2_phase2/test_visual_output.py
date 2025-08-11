"""
Visual output generation for Layout Architect tests.

Creates HTML previews of generated layouts for manual inspection.
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

from src.agents.layout_architect import MVPLayout, MVPContainer
from src.models.agents import Slide
from .test_synthetic_data import get_complete_test_scenario


class LayoutVisualizer:
    """Generate visual representations of layouts."""
    
    def __init__(self, output_dir: str):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html_preview(
        self,
        layout: MVPLayout,
        slide: Slide,
        theme_name: str = "default",
        output_file: str = None
    ) -> str:
        """Generate HTML preview of a layout."""
        if output_file is None:
            output_file = f"layout_{layout.slide_id}.html"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Layout Preview: {slide.title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }}
        .slide-info {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .slide-viewport {{
            position: relative;
            width: 1600px;
            height: 900px;
            background: white;
            border: 1px solid #ddd;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transform: scale(0.5);
            transform-origin: top left;
            margin-bottom: 20px;
        }}
        .container {{
            position: absolute;
            border: 2px solid #3498db;
            background: rgba(52, 152, 219, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            text-align: center;
            overflow: hidden;
        }}
        .container.text {{
            border-color: #2ecc71;
            background: rgba(46, 204, 113, 0.1);
        }}
        .container.image {{
            border-color: #e74c3c;
            background: rgba(231, 76, 60, 0.1);
        }}
        .container.chart {{
            border-color: #f39c12;
            background: rgba(243, 156, 18, 0.1);
        }}
        .container.metric {{
            border-color: #9b59b6;
            background: rgba(155, 89, 182, 0.1);
        }}
        .grid-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            opacity: 0.1;
        }}
        .metrics {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        .metric-item {{
            display: inline-block;
            margin-right: 30px;
            margin-bottom: 10px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            font-size: 1.2em;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="slide-info">
        <h1>{slide.title}</h1>
        <p><strong>Type:</strong> {slide.slide_type} | <strong>Theme:</strong> {theme_name}</p>
        <p><strong>Slide ID:</strong> {layout.slide_id} | <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="slide-viewport">
        <!-- Grid overlay -->
        <svg class="grid-overlay" width="1600" height="900">
            {self._generate_grid_svg()}
        </svg>
        
        <!-- Containers -->
        {self._generate_containers_html(layout.containers)}
    </div>
    
    <div class="metrics">
        <h2>Layout Metrics</h2>
        <div class="metric-item">
            <div class="metric-label">Containers</div>
            <div class="metric-value">{len(layout.containers)}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">White Space</div>
            <div class="metric-value">{layout.white_space_ratio:.1%}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Grid Size</div>
            <div class="metric-value">160×90</div>
        </div>
    </div>
    
    <div class="slide-info" style="margin-top: 20px;">
        <h3>Slide Content</h3>
        <p><strong>Narrative:</strong> {slide.narrative}</p>
        <h4>Key Points:</h4>
        <ul>
            {''.join(f'<li>{point}</li>' for point in slide.key_points)}
        </ul>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    def _generate_grid_svg(self) -> str:
        """Generate SVG grid overlay."""
        lines = []
        
        # Vertical lines every 10 units
        for x in range(0, 1600, 100):  # 10 units * 10 scale
            lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="900" stroke="#000" />')
        
        # Horizontal lines every 10 units
        for y in range(0, 900, 100):  # 10 units * 10 scale
            lines.append(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="#000" />')
        
        return '\n'.join(lines)
    
    def _generate_containers_html(self, containers: List[MVPContainer]) -> str:
        """Generate HTML for containers."""
        html_parts = []
        
        for container in containers:
            pos = container.position
            # Scale up by 10x for visualization (160x90 -> 1600x900)
            left = pos.leftInset * 10
            top = pos.topInset * 10
            width = pos.width * 10
            height = pos.height * 10
            
            container_class = f"container {container.type}"
            
            # Get text content
            text = ""
            if hasattr(container.content, 'text'):
                text = container.content.text
            else:
                text = f"{container.type.upper()}<br>{container.id}"
            
            html_parts.append(f"""
        <div class="{container_class}" style="
            left: {left}px;
            top: {top}px;
            width: {width}px;
            height: {height}px;
        ">
            {text}
        </div>""")
        
        return '\n'.join(html_parts)
    
    def generate_comparison_html(
        self,
        layouts: List[Dict[str, Any]],
        output_file: str = "comparison.html"
    ) -> str:
        """Generate comparison view of multiple layouts."""
        output_path = os.path.join(self.output_dir, output_file)
        
        # Generate comparison HTML
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Layout Comparison</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }
        .comparison-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .layout-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .slide-preview {
            position: relative;
            width: 100%;
            padding-top: 56.25%; /* 16:9 aspect ratio */
            background: #f9f9f9;
            border: 1px solid #ddd;
            overflow: hidden;
        }
        .slide-content {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }
        .mini-container {
            position: absolute;
            border: 1px solid #3498db;
            background: rgba(52, 152, 219, 0.2);
        }
        h2 {
            margin-top: 0;
            font-size: 1.2em;
        }
        .metrics {
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Layout Comparison</h1>
    <div class="comparison-grid">
"""
        
        for layout_data in layouts:
            layout = layout_data["layout"]
            slide = layout_data["slide"]
            theme = layout_data.get("theme", "default")
            
            html += f"""
        <div class="layout-item">
            <h2>{slide.title}</h2>
            <p><strong>Type:</strong> {slide.slide_type} | <strong>Theme:</strong> {theme}</p>
            <div class="slide-preview">
                <div class="slide-content">
                    {self._generate_mini_containers(layout.containers)}
                </div>
            </div>
            <div class="metrics">
                <strong>Containers:</strong> {len(layout.containers)} | 
                <strong>White Space:</strong> {layout.white_space_ratio:.1%}
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    def _generate_mini_containers(self, containers: List[MVPContainer]) -> str:
        """Generate mini container previews for comparison view."""
        html_parts = []
        
        for container in containers:
            pos = container.position
            # Scale to percentage for responsive layout
            left_pct = (pos.leftInset / 160) * 100
            top_pct = (pos.topInset / 90) * 100
            width_pct = (pos.width / 160) * 100
            height_pct = (pos.height / 90) * 100
            
            html_parts.append(f"""
                    <div class="mini-container" style="
                        left: {left_pct}%;
                        top: {top_pct}%;
                        width: {width_pct}%;
                        height: {height_pct}%;
                    "></div>""")
        
        return '\n'.join(html_parts)


def generate_test_visualizations():
    """Generate visualizations for test scenarios."""
    from src.agents.layout_architect import LayoutArchitectOrchestrator
    
    # Create output directory
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "output",
        "visual_test_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    visualizer = LayoutVisualizer(output_dir)
    
    print(f"Generating visualizations in: {output_dir}")
    
    # Generate test scenarios
    scenarios = ["healthcare", "finance", "education", "technology"]
    layouts_for_comparison = []
    
    for industry in scenarios:
        print(f"\nGenerating {industry} scenario...")
        
        # Get test scenario
        scenario = get_complete_test_scenario(f"{industry}_visual_test")
        
        # Create orchestrator
        orchestrator = LayoutArchitectOrchestrator()
        
        # Generate layouts
        try:
            results = asyncio.run(orchestrator.generate_batch(
                slides=scenario["strawman"].slides[:2],  # First 2 slides only
                user_context={"industry": industry}
            ))
            
            for i, result in enumerate(results):
                if result.success:
                    # Generate individual preview
                    slide = scenario["strawman"].slides[i]
                    html_path = visualizer.generate_html_preview(
                        layout=result.layout,
                        slide=slide,
                        theme_name=result.theme.name,
                        output_file=f"{industry}_slide_{i+1}.html"
                    )
                    print(f"  Generated: {os.path.basename(html_path)}")
                    
                    # Add to comparison
                    layouts_for_comparison.append({
                        "layout": result.layout,
                        "slide": slide,
                        "theme": result.theme.name
                    })
        except Exception as e:
            print(f"  Error generating {industry}: {e}")
    
    # Generate comparison view
    if layouts_for_comparison:
        comparison_path = visualizer.generate_comparison_html(layouts_for_comparison)
        print(f"\nGenerated comparison: {os.path.basename(comparison_path)}")
    
    print(f"\n✅ Visualizations complete! Open {output_dir} to view.")


if __name__ == "__main__":
    import asyncio
    generate_test_visualizations()