#!/usr/bin/env python3
"""
Integration test for Content Agent with Director IN data format.
Tests edge cases and integration scenarios.
"""
import asyncio
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent import ContentAgent, ContentManifest
from src.models.agents import Slide


async def test_edge_cases():
    """Test edge cases for content agent"""
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)
    
    agent = ContentAgent()
    results = []
    
    # Test 1: Empty content
    print("\n1. Testing empty content slide...")
    empty_slide = Slide(
        slide_id="test_empty",
        slide_number=1,
        slide_type="content_heavy",
        title="",
        narrative="",  # Empty string instead of None
        key_points=[],
        structure_preference="Single focal point"
    )
    
    try:
        manifest = await agent.prepare_content(
            slide=empty_slide,
            strawman_metadata={"target_audience": "general_public"},
            theme=None,
            session_id="test_empty"
        )
        print(f"   ✅ Handled empty content: {manifest.total_word_count} words")
        results.append(("Empty content", "Success"))
    except Exception as e:
        print(f"   ❌ Failed on empty content: {e}")
        results.append(("Empty content", f"Failed: {e}"))
    
    # Test 2: Very long content
    print("\n2. Testing very long content...")
    long_points = [f"This is a very long point number {i} that contains a lot of text to test word count limits and see how the agent handles content that exceeds normal boundaries." for i in range(10)]
    long_slide = Slide(
        slide_id="test_long",
        slide_number=2,
        slide_type="content_heavy",
        title="Extremely Detailed Analysis",
        narrative="This slide contains an enormous amount of information that needs to be condensed.",
        key_points=long_points,
        structure_preference="Two-column layout"
    )
    
    try:
        manifest = await agent.prepare_content(
            slide=long_slide,
            strawman_metadata={"target_audience": "executives"},
            theme=None,
            session_id="test_long"
        )
        print(f"   ✅ Handled long content: {manifest.total_word_count}/{manifest.word_count_limit} words")
        within_limit = manifest.total_word_count <= manifest.word_count_limit
        print(f"   {'✅' if within_limit else '❌'} Word count within limit: {within_limit}")
        results.append(("Long content", "Success" if within_limit else "Over limit"))
    except Exception as e:
        print(f"   ❌ Failed on long content: {e}")
        results.append(("Long content", f"Failed: {e}"))
    
    # Test 3: Mixed visual needs
    print("\n3. Testing multiple visual needs...")
    mixed_slide = Slide(
        slide_id="test_mixed",
        slide_number=3,
        slide_type="mixed_content",
        title="Multi-Visual Slide",
        narrative="This slide needs multiple types of visuals",
        key_points=["Data point 1", "Visual point 2"],
        analytics_needed="**Goal:** Show growth **Content:** Sales data **Style:** Modern chart",
        visuals_needed="**Goal:** Illustrate concept **Content:** Abstract representation **Style:** Minimalist",
        diagrams_needed="**Goal:** Show process **Content:** Three steps **Style:** Simple flow"
    )
    
    try:
        manifest = await agent.prepare_content(
            slide=mixed_slide,
            strawman_metadata={"target_audience": "technical"},
            theme=None,
            session_id="test_mixed"
        )
        visual_count = len([v for v in [manifest.primary_visual] + manifest.supporting_visuals if v])
        print(f"   ✅ Created {visual_count} visual specifications")
        if manifest.primary_visual:
            print(f"   Primary visual: {manifest.primary_visual.visual_type} (Ready: {manifest.primary_visual.handoff_ready})")
        results.append(("Mixed visuals", f"{visual_count} visuals"))
    except Exception as e:
        print(f"   ❌ Failed on mixed visuals: {e}")
        results.append(("Mixed visuals", f"Failed: {e}"))
    
    # Test 4: Special characters and formatting
    print("\n4. Testing special characters...")
    special_slide = Slide(
        slide_id="test_special",
        slide_number=4,
        slide_type="data_driven",
        title="Revenue: $1M → $5M (400% ↑)",
        narrative="Testing © symbols, ™ marks, and other special chars: €£¥",
        key_points=["Point with \"quotes\"", "Point with 'apostrophes'", "Point with & ampersand"],
        analytics_needed="**Goal:** Show € currency data **Content:** European sales **Style:** Professional"
    )
    
    try:
        manifest = await agent.prepare_content(
            slide=special_slide,
            strawman_metadata={"target_audience": "investors"},
            theme=None,
            session_id="test_special"
        )
        print(f"   ✅ Handled special characters")
        print(f"   Title preserved: {manifest.title.text}")
        results.append(("Special chars", "Success"))
    except Exception as e:
        print(f"   ❌ Failed on special characters: {e}")
        results.append(("Special chars", f"Failed: {e}"))
    
    # Summary
    print("\n" + "="*60)
    print("EDGE CASE TEST SUMMARY")
    print("="*60)
    for test_name, result in results:
        status = "✅" if "Success" in result or "visuals" in result else "❌"
        print(f"{status} {test_name:20} - {result}")
    
    return results


async def test_director_integration():
    """Test integration with Director IN output format"""
    print("\n" + "="*60)
    print("TESTING DIRECTOR IN INTEGRATION")
    print("="*60)
    
    # Simulate Director IN strawman output
    director_strawman = {
        "main_title": "AI-Powered Healthcare Revolution",
        "executive_summary": "Comprehensive overview of AI applications in healthcare",
        "target_audience": "healthcare_professionals",
        "presentation_duration": "20 minutes",
        "theme": "Innovation and Trust",
        "narrative_flow": "Problem → Solution → Benefits → Call to Action",
        "structure_preference": "Visual-heavy with data support"
    }
    
    # Simulate slides from Director IN
    director_slides = [
        Slide(
            slide_id="dir_001",
            slide_number=1,
            slide_type="title_slide",
            title="AI-Powered Healthcare Revolution",
            narrative="Setting the stage for transformation",
            key_points=["Transforming Patient Care", "Powered by Advanced AI"],
            structure_preference="Hero Image"
        ),
        Slide(
            slide_id="dir_002", 
            slide_number=2,
            slide_type="data_driven",
            title="The Healthcare Crisis",
            narrative="Current challenges in healthcare delivery",
            key_points=["Rising costs", "Staff shortages", "Patient outcomes"],
            analytics_needed="**Goal:** Show healthcare cost trends **Content:** 5-year cost increase data **Style:** Impactful chart",
            structure_preference="Single focal point"
        ),
        Slide(
            slide_id="dir_003",
            slide_number=3,
            slide_type="diagram_focused",
            title="Our AI Solution Architecture",
            narrative="How our AI system integrates with existing healthcare infrastructure",
            key_points=["Data ingestion", "AI processing", "Clinical integration", "Patient interface"],
            diagrams_needed="**Goal:** Show system architecture **Content:** Four main components connected **Style:** Technical but clear",
            structure_preference="Timeline / Process Flow"
        )
    ]
    
    agent = ContentAgent()
    results = []
    
    for slide in director_slides:
        print(f"\nProcessing Director slide: {slide.title}")
        try:
            manifest = await agent.prepare_content(
                slide=slide,
                strawman_metadata=director_strawman,
                theme=None,
                session_id=f"director_{slide.slide_id}"
            )
            
            print(f"✅ Generated manifest:")
            print(f"   - Type: {manifest.slide_type}")
            print(f"   - Words: {manifest.total_word_count}/{manifest.word_count_limit}")
            print(f"   - Density: {manifest.content_density}")
            
            if manifest.primary_visual:
                print(f"   - Visual: {manifest.primary_visual.visual_type} (Ready: {manifest.primary_visual.handoff_ready})")
                
                # Verify visual has required data
                if manifest.primary_visual.visual_type == "chart":
                    has_data = bool(manifest.primary_visual.data_points and manifest.primary_visual.axes)
                    print(f"   - Chart data complete: {has_data}")
                elif manifest.primary_visual.visual_type == "diagram":
                    has_structure = bool(manifest.primary_visual.nodes and manifest.primary_visual.connections)
                    print(f"   - Diagram structure complete: {has_structure}")
            
            results.append((slide.title, "Success"))
            
            # Save manifest
            filename = f"director_manifest_{slide.slide_id}.json"
            with open(filename, 'w') as f:
                json.dump(manifest.model_dump(), f, indent=2)
            print(f"   💾 Saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append((slide.title, f"Failed: {e}"))
    
    # Summary
    print("\n" + "="*60)
    print("DIRECTOR INTEGRATION SUMMARY")
    print("="*60)
    success_count = sum(1 for _, result in results if result == "Success")
    print(f"✅ Success: {success_count}/{len(results)} slides processed")
    
    return results


async def test_performance():
    """Test performance with multiple slides"""
    print("\n" + "="*60)
    print("TESTING PERFORMANCE")
    print("="*60)
    
    import time
    
    agent = ContentAgent()
    
    # Create 10 test slides of different types
    slide_types = ["content_heavy", "data_driven", "visual_heavy", "diagram_focused", "mixed_content"]
    test_slides = []
    
    for i in range(10):
        slide_type = slide_types[i % len(slide_types)]
        slide = Slide(
            slide_id=f"perf_{i:03d}",
            slide_number=i+1,
            slide_type=slide_type,
            title=f"Performance Test Slide {i+1}",
            narrative=f"Testing performance with slide type {slide_type}",
            key_points=[f"Point {j}" for j in range(3)],
            analytics_needed="**Goal:** Test **Content:** Data **Style:** Chart" if "data" in slide_type else None,
            visuals_needed="**Goal:** Test **Content:** Visual **Style:** Modern" if "visual" in slide_type else None,
            diagrams_needed="**Goal:** Test **Content:** Flow **Style:** Simple" if "diagram" in slide_type else None
        )
        test_slides.append(slide)
    
    # Process slides and measure time
    start_time = time.time()
    results = []
    
    for slide in test_slides:
        slide_start = time.time()
        try:
            manifest = await agent.prepare_content(
                slide=slide,
                strawman_metadata={"target_audience": "general_public"},
                theme=None,
                session_id=f"perf_{slide.slide_id}"
            )
            slide_time = time.time() - slide_start
            results.append((slide.slide_type, slide_time, "Success"))
            print(f"✅ {slide.slide_id}: {slide_time:.2f}s")
        except Exception as e:
            slide_time = time.time() - slide_start
            results.append((slide.slide_type, slide_time, f"Failed: {e}"))
            print(f"❌ {slide.slide_id}: Failed after {slide_time:.2f}s")
    
    total_time = time.time() - start_time
    
    # Analysis
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    print(f"Total time: {total_time:.2f}s for {len(test_slides)} slides")
    print(f"Average time per slide: {total_time/len(test_slides):.2f}s")
    
    # Group by slide type
    from collections import defaultdict
    type_times = defaultdict(list)
    for slide_type, time_taken, status in results:
        if status == "Success":
            type_times[slide_type].append(time_taken)
    
    print("\nAverage time by slide type:")
    for slide_type, times in type_times.items():
        avg_time = sum(times) / len(times) if times else 0
        print(f"  {slide_type:15} - {avg_time:.2f}s")
    
    return results


async def main():
    """Run all integration tests"""
    print("🚀 Content Agent Integration Tests")
    print("=" * 80)
    
    all_results = {}
    
    # Run edge case tests
    edge_results = await test_edge_cases()
    all_results["edge_cases"] = edge_results
    
    # Run Director integration tests
    director_results = await test_director_integration()
    all_results["director_integration"] = director_results
    
    # Run performance tests
    perf_results = await test_performance()
    all_results["performance"] = perf_results
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 80)
    
    for test_suite, results in all_results.items():
        success_count = sum(1 for _, result in results if "Success" in str(result))
        total_count = len(results)
        print(f"{test_suite}: {success_count}/{total_count} passed")
    
    # Save complete test results
    with open("content_agent_test_results.json", 'w') as f:
        json.dump({
            "timestamp": str(asyncio.get_event_loop().time()),
            "results": {k: [{"test": t[0], "result": str(t[1])} for t in v] 
                       for k, v in all_results.items()}
        }, f, indent=2)
    
    print("\n💾 Complete test results saved to: content_agent_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())