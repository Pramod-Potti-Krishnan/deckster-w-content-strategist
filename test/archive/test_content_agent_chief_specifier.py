#!/usr/bin/env python3
"""
Test script for enhanced Content Agent with Chief Specifier role.
Tests all four expert modes with different slide types.
"""
import asyncio
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent import ContentAgent, ContentManifest
from src.models.agents import Slide


def create_test_slide(slide_type: str, slide_id: str, analytics: str = None, 
                     visuals: str = None, diagrams: str = None) -> Slide:
    """Create a test slide with Phase 1 format data"""
    
    slide_configs = {
        "data_driven": {
            "title": "Revenue Growth Analysis",
            "narrative": "This slide demonstrates our impressive revenue growth trajectory",
            "key_points": ["37% YoY growth", "Record Q4 performance", "Expanding market share"],
            "analytics_needed": "**Goal:** Show revenue growth trend **Content:** Quarterly revenue data for last 2 years **Style:** Professional bar chart with trend line",
            "structure_preference": "Single focal point layout"
        },
        "visual_heavy": {
            "title": "The Future of Healthcare AI",
            "narrative": "A vision of how AI will transform patient care",
            "key_points": ["AI-assisted diagnostics", "Personalized treatment", "Predictive healthcare"],
            "visuals_needed": "**Goal:** Create immediate visual impact **Content:** Modern hospital with AI elements overlaid, doctors using advanced technology **Style:** Futuristic, professional, blue tones",
            "structure_preference": "Hero Image / Full-Bleed"
        },
        "diagram_focused": {
            "title": "Implementation Roadmap",
            "narrative": "Our phased approach to digital transformation",
            "key_points": ["Phase 1: Foundation", "Phase 2: Integration", "Phase 3: Optimization", "Phase 4: Innovation"],
            "diagrams_needed": "**Goal:** Show clear progression **Content:** Four phases connected by arrows showing dependencies **Style:** Clean flowchart with timeline",
            "structure_preference": "Timeline / Process Flow"
        },
        "content_heavy": {
            "title": "Key Benefits Overview",
            "narrative": "Comprehensive overview of solution benefits",
            "key_points": [
                "Reduced operational costs by 25%",
                "Improved customer satisfaction scores",
                "Faster time to market",
                "Enhanced team productivity"
            ],
            "structure_preference": "Two-column layout"
        }
    }
    
    config = slide_configs.get(slide_type, slide_configs["content_heavy"])
    
    return Slide(
        slide_id=slide_id,
        slide_number=1,
        slide_type=slide_type,
        title=config["title"],
        narrative=config["narrative"],
        key_points=config["key_points"],
        analytics_needed=analytics or config.get("analytics_needed"),
        visuals_needed=visuals or config.get("visuals_needed"),
        diagrams_needed=diagrams or config.get("diagrams_needed"),
        structure_preference=config["structure_preference"]
    )


async def test_content_agent_mode(slide_type: str, expected_mode: str):
    """Test Content Agent with a specific slide type"""
    print(f"\n{'='*60}")
    print(f"Testing {expected_mode.upper()} Mode with {slide_type} slide")
    print('='*60)
    
    # Create test slide
    slide = create_test_slide(slide_type, f"test_{slide_type}_001")
    
    # Create strawman metadata
    strawman_metadata = {
        "main_title": "AI Innovation Showcase",
        "overall_theme": "Data-driven and forward-looking",
        "target_audience": "executives",
        "design_suggestions": "Modern professional with blue color scheme"
    }
    
    # Initialize Content Agent
    agent = ContentAgent()
    
    # Prepare content
    print(f"\nProcessing slide: {slide.title}")
    manifest = await agent.prepare_content(
        slide=slide,
        strawman_metadata=strawman_metadata,
        theme=None,
        session_id="test_session"
    )
    
    # Display results
    print(f"\n📊 Content Manifest Results:")
    print(f"  - Slide Type: {manifest.slide_type}")
    print(f"  - Total Words: {manifest.total_word_count}/{manifest.word_count_limit}")
    print(f"  - Content Density: {manifest.content_density}")
    print(f"  - Target Audience: {manifest.target_audience}")
    
    print(f"\n📝 Text Content:")
    print(f"  Title: {manifest.title.text} (P{manifest.title.priority[-1]})")
    for i, point in enumerate(manifest.main_points, 1):
        print(f"  Point {i}: {point.text[:60]}... (P{point.priority[-1]})")
    
    if manifest.primary_visual:
        print(f"\n🎨 Visual Specification:")
        print(f"  - Type: {manifest.primary_visual.visual_type}")
        print(f"  - Handoff Ready: {manifest.primary_visual.handoff_ready}")
        print(f"  - Priority: {manifest.primary_visual.priority}")
        
        if manifest.primary_visual.visual_type == "chart":
            print(f"  - Chart Type: {manifest.primary_visual.chart_type}")
            if manifest.primary_visual.data_points:
                print(f"  - Data Points: {len(manifest.primary_visual.data_points)}")
                # Show first few data points
                for dp in manifest.primary_visual.data_points[:3]:
                    print(f"    • {dp}")
                if len(manifest.primary_visual.data_points) > 3:
                    print(f"    • ... and {len(manifest.primary_visual.data_points) - 3} more")
            print(f"  - Axes: {manifest.primary_visual.axes}")
            if manifest.primary_visual.data_insights:
                print(f"  - Insights: {manifest.primary_visual.data_insights[:100]}...")
        
        elif manifest.primary_visual.visual_type == "image":
            print(f"  - Style: {manifest.primary_visual.image_style}")
            print(f"  - Keywords: {', '.join(manifest.primary_visual.style_keywords or [])}")
            if manifest.primary_visual.image_prompt:
                print(f"  - Prompt ({len(manifest.primary_visual.image_prompt)} chars):")
                print(f"    {manifest.primary_visual.image_prompt[:200]}...")
            if manifest.primary_visual.negative_prompt:
                print(f"  - Avoid: {manifest.primary_visual.negative_prompt}")
        
        elif manifest.primary_visual.visual_type == "diagram":
            print(f"  - Diagram Type: {manifest.primary_visual.diagram_type}")
            print(f"  - Layout Direction: {manifest.primary_visual.layout_direction}")
            if manifest.primary_visual.nodes:
                print(f"  - Nodes ({len(manifest.primary_visual.nodes)}):")
                for node in manifest.primary_visual.nodes[:4]:
                    print(f"    • {node.id}: {node.label}")
                if len(manifest.primary_visual.nodes) > 4:
                    print(f"    • ... and {len(manifest.primary_visual.nodes) - 4} more")
            if manifest.primary_visual.connections:
                print(f"  - Connections: {len(manifest.primary_visual.connections)}")
    
    # Save full manifest for inspection
    output_file = f"content_manifest_{slide_type}.json"
    with open(output_file, 'w') as f:
        # Convert to dict for JSON serialization
        manifest_dict = manifest.model_dump()
        json.dump(manifest_dict, f, indent=2)
    print(f"\n💾 Full manifest saved to: {output_file}")
    
    return manifest


async def main():
    """Test all four expert modes"""
    print("🚀 Testing Enhanced Content Agent - Chief Specifier Role")
    print("=" * 80)
    
    # Test configurations
    test_cases = [
        ("data_driven", "data_storyteller"),
        ("visual_heavy", "visual_briefer"),
        ("diagram_focused", "diagram_architect"),
        ("content_heavy", "content_writer")
    ]
    
    results = {}
    
    for slide_type, expected_mode in test_cases:
        try:
            manifest = await test_content_agent_mode(slide_type, expected_mode)
            results[slide_type] = {
                "status": "success",
                "visual_type": manifest.primary_visual.visual_type if manifest.primary_visual else None,
                "handoff_ready": manifest.primary_visual.handoff_ready if manifest.primary_visual else None,
                "word_count": f"{manifest.total_word_count}/{manifest.word_count_limit}"
            }
        except Exception as e:
            print(f"\n❌ Error testing {slide_type}: {e}")
            import traceback
            traceback.print_exc()
            results[slide_type] = {"status": "error", "error": str(e)}
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for slide_type, result in results.items():
        if result["status"] == "success":
            print(f"✅ {slide_type:15} - Visual: {result['visual_type'] or 'None':10} - Ready: {result['handoff_ready']} - Words: {result['word_count']}")
        else:
            print(f"❌ {slide_type:15} - Error: {result['error']}")
    
    # Overall success
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"\n🏁 Overall: {success_count}/{len(test_cases)} tests passed")


if __name__ == "__main__":
    asyncio.run(main())