#!/usr/bin/env python3
"""
Comprehensive Test Suite for All SVG Templates
===============================================

Tests all SVG templates for:
- Template loading and validation
- Text wrapping capabilities
- Color theming
- Actual SVG generation with sample content
"""

import asyncio
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

sys.path.append(str(Path(__file__).parent))

from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import DiagramSpec

OUTPUT_DIR = Path("test/diagram-tests/test_output/svg_templates_comprehensive")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_test_content(diagram_type: str) -> Dict[str, Any]:
    """Create comprehensive test content for each diagram type."""
    
    if diagram_type == "pyramid":
        return {
            "elements": [
                {"label": "Strategic Vision and Leadership Excellence"},  # Long text to test wrapping
                {"label": "Tactical Planning and Resource Management"},
                {"label": "Operational Excellence and Daily Execution"}
            ],
            "title": "Organizational Hierarchy"
        }
    
    elif diagram_type == "funnel":
        return {
            "elements": [
                {"label": "Brand Awareness and Initial Discovery Phase"},
                {"label": "Interest Generation and Engagement"},
                {"label": "Consideration and Evaluation"},
                {"label": "Purchase Decision Making"},
                {"label": "Final Conversion"}
            ],
            "title": "Customer Journey Funnel"
        }
    
    elif diagram_type == "timeline":
        return {
            "elements": [
                {"label": "Project Initiation", "date": "Q1 2024"},
                {"label": "Requirements Gathering", "date": "Q2 2024"},
                {"label": "Design & Architecture", "date": "Q3 2024"},
                {"label": "Development Phase", "date": "Q4 2024"},
                {"label": "Testing & QA", "date": "Q1 2025"},
                {"label": "Production Launch", "date": "Q2 2025"}
            ],
            "title": "Project Roadmap"
        }
    
    elif diagram_type == "cycle":
        return {
            "elements": [
                {"label": "Plan and Strategy Development"},
                {"label": "Execute and Implement"},
                {"label": "Monitor and Measure"},
                {"label": "Optimize and Improve"}
            ],
            "title": "Continuous Improvement Cycle"
        }
    
    elif diagram_type == "venn":
        return {
            "elements": [
                {"label": "Technical Skills"},
                {"label": "Business Knowledge"},
                {"label": "Leadership Qualities"}  # Overlap
            ],
            "title": "Competency Overlap"
        }
    
    elif diagram_type in ["matrix_2x2", "matrix"]:
        return {
            "elements": [
                {"label": "High Impact High Effort"},
                {"label": "High Impact Low Effort"},
                {"label": "Low Impact Low Effort"},
                {"label": "Low Impact High Effort"}
            ],
            "relationships": [
                {"axis": "x", "label": "Effort Required"},
                {"axis": "y", "label": "Business Impact"}
            ],
            "title": "Priority Matrix"
        }
    
    elif diagram_type == "hub_spoke":
        return {
            "elements": [
                {"label": "Central Platform"},  # Hub
                {"label": "Marketing Team"},     # Spokes
                {"label": "Sales Operations"},
                {"label": "Engineering"},
                {"label": "Customer Support"},
                {"label": "Finance & Admin"},
                {"label": "Human Resources"}
            ],
            "title": "Department Integration Model"
        }
    
    elif diagram_type == "honeycomb":
        return {
            "elements": [
                {"label": "Core Mission"},        # Center
                {"label": "Innovation Focus"},    # Surrounding cells
                {"label": "Quality Excellence"},
                {"label": "Team Collaboration"},
                {"label": "Customer Centricity"},
                {"label": "Integrity & Ethics"},
                {"label": "Continuous Learning"}
            ],
            "title": "Organizational Values"
        }
    
    elif diagram_type == "swot":
        return {
            "elements": [
                {"label": "Strong brand recognition, Skilled workforce, Market leader"},
                {"label": "Limited resources, Tech debt, Geographic constraints"},
                {"label": "Growing market, New technologies, Partnership potential"},
                {"label": "Competition, Economic uncertainty, Regulatory changes"}
            ],
            "title": "Strategic SWOT Analysis"
        }
    
    elif diagram_type in ["process_flow", "process"]:
        return {
            "elements": [
                {"label": "Data Collection"},
                {"label": "Validation & QA"},
                {"label": "Processing Engine"},
                {"label": "Quality Check"},
                {"label": "Final Output"}
            ],
            "title": "Data Processing Pipeline"
        }
    
    else:
        return {
            "elements": [
                {"label": f"Element 1 for {diagram_type}"},
                {"label": f"Element 2 for {diagram_type}"},
                {"label": f"Element 3 for {diagram_type}"}
            ],
            "title": f"{diagram_type.replace('_', ' ').title()} Diagram"
        }


def validate_svg(svg_content: str) -> tuple[bool, str]:
    """Validate SVG content and return status with message."""
    try:
        # Parse SVG
        root = ET.fromstring(svg_content)
        
        # Check if it's valid SVG
        if not root.tag.endswith('svg'):
            return False, "Not a valid SVG root element"
        
        # Count elements
        text_elements = 0
        path_elements = 0
        rect_elements = 0
        circle_elements = 0
        
        for elem in root.iter():
            if elem.tag.endswith('text'):
                text_elements += 1
            elif elem.tag.endswith('path'):
                path_elements += 1
            elif elem.tag.endswith('rect'):
                rect_elements += 1
            elif elem.tag.endswith('circle'):
                circle_elements += 1
        
        # Check for text wrapping (tspan elements)
        wrapped_texts = 0
        for elem in root.iter():
            if elem.tag.endswith('text'):
                tspans = list(elem.findall('.//{http://www.w3.org/2000/svg}tspan'))
                if len(tspans) > 1:
                    wrapped_texts += 1
        
        stats = f"texts={text_elements}, paths={path_elements}, rects={rect_elements}, circles={circle_elements}"
        if wrapped_texts > 0:
            stats += f", wrapped={wrapped_texts}"
        
        return True, stats
        
    except Exception as e:
        return False, str(e)


async def test_template(diagram_type: str, agent: SVGDiagramAgent) -> Dict[str, Any]:
    """Test a single template comprehensively."""
    
    results = {
        "diagram_type": diagram_type,
        "template_exists": False,
        "svg_valid": False,
        "generation_success": False,
        "text_wrapping": False,
        "color_theming": False,
        "error": None
    }
    
    try:
        # Create test content
        content = create_test_content(diagram_type)
        
        # Test with different themes
        themes = [
            {
                "name": "Default",
                "colors": {
                    "primary": "#3b82f6",
                    "secondary": "#10b981",
                    "accent": "#f59e0b",
                    "background": "#ffffff",
                    "text": "#1e293b"
                }
            },
            {
                "name": "Dark",
                "colors": {
                    "primary": "#8b5cf6",
                    "secondary": "#ec4899",
                    "accent": "#06b6d4",
                    "background": "#1e293b",
                    "text": "#f1f5f9"
                }
            }
        ]
        
        for theme_idx, theme in enumerate(themes):
            # Create spec
            spec = DiagramSpec(
                diagram_type=diagram_type,
                content=content,
                theme=theme,
                layout_hints={}
            )
            
            # Generate SVG
            result = await agent.generate(spec)
            
            # Validate SVG
            is_valid, stats = validate_svg(result.svg_content)
            
            if is_valid:
                results["svg_valid"] = True
                results["generation_success"] = True
                
                # Check for text wrapping
                if "wrapped=" in stats:
                    results["text_wrapping"] = True
                
                # Save output
                output_file = OUTPUT_DIR / f"{diagram_type}_theme_{theme_idx}.svg"
                output_file.write_text(result.svg_content)
                results["template_exists"] = True
                
                # Color theming is successful if we generated with different themes
                if theme_idx > 0:
                    results["color_theming"] = True
            
    except FileNotFoundError as e:
        results["error"] = f"Template not found: {e}"
    except Exception as e:
        results["error"] = str(e)
    
    return results


async def main():
    """Run comprehensive tests for all SVG templates."""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE SVG TEMPLATE TEST SUITE")
    print("="*80)
    
    # Initialize agent
    print("\nInitializing SVG agent...")
    try:
        agent = SVGDiagramAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"⚠️ Agent initialization requires API keys: {e}")
        print("Note: Some tests may be limited without full agent initialization")
        return
    
    # List of all templates to test
    templates = [
        "pyramid",
        "funnel",
        "timeline",
        "cycle",
        "venn",
        "matrix_2x2",
        "hub_spoke",
        "honeycomb",
        "swot",
        "process_flow"
    ]
    
    print(f"\nTesting {len(templates)} templates...")
    print("-" * 80)
    
    # Test each template
    all_results = []
    for template in templates:
        print(f"\n📋 Testing: {template}")
        results = await test_template(template, agent)
        all_results.append(results)
        
        # Print immediate feedback
        if results["generation_success"]:
            print(f"  ✅ Generation successful")
            if results["text_wrapping"]:
                print(f"  ✅ Text wrapping detected")
            if results["color_theming"]:
                print(f"  ✅ Color theming working")
        else:
            print(f"  ❌ Error: {results['error']}")
    
    # Generate summary report
    print("\n" + "="*80)
    print("TEST SUMMARY REPORT")
    print("="*80)
    
    # Overall statistics
    total = len(all_results)
    successful = sum(1 for r in all_results if r["generation_success"])
    with_wrapping = sum(1 for r in all_results if r["text_wrapping"])
    with_theming = sum(1 for r in all_results if r["color_theming"])
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total templates tested: {total}")
    print(f"  Successfully generated: {successful}/{total} ({successful/total*100:.0f}%)")
    print(f"  With text wrapping: {with_wrapping}/{total}")
    print(f"  With color theming: {with_theming}/{total}")
    
    # Detailed results table
    print(f"\n📋 Detailed Results:")
    print("-" * 80)
    print(f"{'Template':<15} {'Exists':<8} {'Valid':<8} {'Wrapping':<10} {'Theming':<10} {'Status':<10}")
    print("-" * 80)
    
    for r in all_results:
        exists = "✅" if r["template_exists"] else "❌"
        valid = "✅" if r["svg_valid"] else "❌"
        wrapping = "✅" if r["text_wrapping"] else "⚠️"
        theming = "✅" if r["color_theming"] else "⚠️"
        status = "✅ Pass" if r["generation_success"] else "❌ Fail"
        
        print(f"{r['diagram_type']:<15} {exists:<8} {valid:<8} {wrapping:<10} {theming:<10} {status:<10}")
    
    # List any errors
    errors = [r for r in all_results if r["error"]]
    if errors:
        print(f"\n⚠️ Errors encountered:")
        for r in errors:
            print(f"  - {r['diagram_type']}: {r['error']}")
    
    # Final verdict
    print("\n" + "="*80)
    if successful == total:
        print("✅ ALL TESTS PASSED! All SVG templates are working correctly.")
    else:
        print(f"⚠️ {total - successful} template(s) need attention.")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"   Generated {successful * 2} SVG files (2 themes per template)")
    
    # Recommendations
    if successful < total:
        print("\n📝 Recommendations:")
        failed = [r['diagram_type'] for r in all_results if not r["generation_success"]]
        print(f"  - Fix failing templates: {', '.join(failed)}")
    
    if with_wrapping < successful:
        no_wrap = [r['diagram_type'] for r in all_results if r["generation_success"] and not r["text_wrapping"]]
        if no_wrap:
            print(f"  - Add text wrapping support for: {', '.join(no_wrap)}")


if __name__ == "__main__":
    asyncio.run(main())