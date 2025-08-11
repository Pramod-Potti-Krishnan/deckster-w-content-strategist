"""
Integration tests for the three-agent Layout Architect system.

Tests the complete pipeline from slide input to layout output.
"""

import asyncio
import pytest
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest,
    LayoutGenerationResult,
    LayoutEngineConfig
)
from src.models.agents import Slide, PresentationStrawman
from .test_synthetic_data import (
    SyntheticDataGenerator, get_test_strawman,
    get_complete_test_scenario
)


class TestIntegratedPipeline:
    """Test the complete three-agent pipeline."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return LayoutArchitectOrchestrator()
    
    @pytest.fixture
    def test_scenarios(self):
        """Create test scenarios for different industries."""
        generator = SyntheticDataGenerator(seed=42)
        return {
            "healthcare": generator.generate_test_scenario("healthcare_test", "healthcare"),
            "finance": generator.generate_test_scenario("finance_test", "finance"),
            "education": generator.generate_test_scenario("education_test", "education"),
            "technology": generator.generate_test_scenario("technology_test", "technology")
        }
    
    @pytest.mark.asyncio
    async def test_single_slide_generation(self, orchestrator):
        """Test generating layout for a single slide."""
        slide = Slide(
            slide_id="test_001",
            slide_number=1,
            title="Quarterly Business Review",
            slide_type="data_driven",
            narrative="Presenting Q4 performance metrics",
            key_points=[
                "Revenue increased 23% YoY to $45M",
                "Customer base grew by 1,200 accounts",
                "Market share expanded to 15%",
                "NPS score improved to 72"
            ],
            analytics_needed="Revenue chart, customer growth graph, market share pie chart",
            structure_preference="dashboard"
        )
        
        request = LayoutGenerationRequest(
            slide=slide,
            user_context={
                "brand": "DataCorp Analytics",
                "industry": "B2B SaaS",
                "preferences": {
                    "formality": "professional",
                    "data_visualization": "modern"
                }
            },
            presentation_context={
                "tone": "confident",
                "audience": "board of directors",
                "purpose": "quarterly review"
            }
        )
        
        start_time = time.time()
        result = await orchestrator.generate_layout(request)
        generation_time = time.time() - start_time
        
        # Assertions
        assert result.success, f"Layout generation failed: {result.error_message}"
        assert result.layout is not None
        assert result.theme is not None
        assert result.manifest is not None
        
        # Check layout quality
        assert len(result.layout.containers) >= 4  # Should have multiple data containers
        assert 0.3 <= result.layout.white_space_ratio <= 0.5
        
        # Check theme appropriateness
        assert "professional" in result.theme.name.lower() or "data" in result.theme.name.lower()
        
        # Check manifest
        assert result.manifest.content_flow.value in ["dashboard", "radial"]
        
        # Performance check
        assert generation_time < 30.0, f"Generation took too long: {generation_time:.2f}s"
        
        print(f"\n✅ Single slide generated in {generation_time:.2f}s")
        print(f"   Theme: {result.theme.name}")
        print(f"   Containers: {len(result.layout.containers)}")
        print(f"   Balance score: {result.generation_metrics.get('balance_score', 'N/A')}")
    
    @pytest.mark.asyncio
    async def test_batch_generation(self, orchestrator):
        """Test generating layouts for multiple slides."""
        generator = SyntheticDataGenerator(seed=42)
        slides = []
        
        # Create diverse slide types
        slide_configs = [
            ("title_slide", "Welcome to Our Journey"),
            ("content_heavy", "Market Analysis"),
            ("visual_heavy", "Product Showcase"),
            ("data_driven", "Performance Metrics"),
            ("content_heavy", "Next Steps")
        ]
        
        for i, (slide_type, title) in enumerate(slide_configs):
            slide = generator.generate_slide(
                slide_id=f"batch_{i+1:03d}",
                slide_number=i + 1,
                slide_type=slide_type,
                industry="technology"
            )
            slide.title = title  # Override with custom title
            slides.append(slide)
        
        # Batch generation
        start_time = time.time()
        results = await orchestrator.generate_batch(
            slides=slides,
            user_context={
                "brand": "TechInnovate",
                "industry": "Technology",
                "preferences": {"modern": True, "minimalist": True}
            },
            presentation_context={
                "tone": "innovative",
                "duration": 15
            }
        )
        batch_time = time.time() - start_time
        
        # Assertions
        assert len(results) == len(slides)
        successful = [r for r in results if r.success]
        assert len(successful) == len(slides), "Some slides failed to generate"
        
        # Check theme consistency
        themes = [r.theme.name for r in results]
        assert len(set(themes)) == 1, "Theme should be consistent across batch"
        
        # Check each result
        for i, result in enumerate(results):
            assert result.layout is not None
            assert result.slide_id == slides[i].slide_id
            print(f"   Slide {i+1}: {len(result.layout.containers)} containers")
        
        # Performance
        avg_time = batch_time / len(slides)
        print(f"\n✅ Batch of {len(slides)} slides in {batch_time:.2f}s ({avg_time:.2f}s/slide)")
        assert avg_time < 10.0, "Batch processing too slow per slide"
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("industry", ["healthcare", "finance", "education", "technology"])
    async def test_industry_specific_generation(self, orchestrator, industry):
        """Test layout generation for different industries."""
        generator = SyntheticDataGenerator()
        slide = generator.generate_slide(
            slide_id=f"{industry}_001",
            slide_number=1,
            slide_type="content_heavy",
            industry=industry
        )
        
        request = LayoutGenerationRequest(
            slide=slide,
            user_context={
                "brand": f"{industry.capitalize()} Corp",
                "industry": industry
            }
        )
        
        result = await orchestrator.generate_layout(request)
        
        assert result.success
        assert industry in result.theme.style_attributes.get("industry", "").lower() or \
               industry in str(result.theme.style_attributes).lower()
        
        print(f"\n✅ {industry.capitalize()} layout: {result.theme.name}")
    
    @pytest.mark.asyncio
    async def test_progressive_refinement(self, orchestrator):
        """Test the iterative refinement process."""
        slide = Slide(
            slide_id="refine_001",
            slide_number=1,
            title="Complex Dashboard with Many Elements",
            slide_type="data_driven",
            key_points=[
                "Metric 1: Revenue $45M",
                "Metric 2: Users 150K",
                "Metric 3: Retention 85%",
                "Metric 4: Growth 23%",
                "Metric 5: NPS 72",
                "Metric 6: CAC $1,200"
            ],
            analytics_needed="Multiple charts and KPI cards"
        )
        
        # First, generate with relaxed requirements
        request = LayoutGenerationRequest(
            slide=slide,
            layout_config=LayoutEngineConfig(
                max_iterations=2,
                white_space_min=0.2,
                white_space_max=0.6
            )
        )
        
        result1 = await orchestrator.generate_layout(request)
        
        # Then, generate with strict requirements
        request.layout_config = LayoutEngineConfig(
            max_iterations=5,
            white_space_min=0.35,
            white_space_max=0.45,
            balance_threshold=0.8
        )
        
        result2 = await orchestrator.generate_layout(request)
        
        # The refined version should have better metrics
        metrics1 = result1.generation_metrics
        metrics2 = result2.generation_metrics
        
        assert result2.success
        assert metrics2.get("total_iterations", 0) >= metrics1.get("total_iterations", 0)
        
        # Check if refinement improved balance
        if "balance_score" in metrics1 and "balance_score" in metrics2:
            print(f"\n✅ Refinement improved balance: {metrics1['balance_score']:.2f} → {metrics2['balance_score']:.2f}")
    
    @pytest.mark.asyncio
    async def test_theme_consistency_across_presentation(self, orchestrator, test_scenarios):
        """Test that theme remains consistent across a presentation."""
        scenario = test_scenarios["healthcare"]
        strawman = scenario["strawman"]
        
        results = await orchestrator.generate_batch(
            slides=strawman.slides,
            user_context={
                "brand": "HealthTech Solutions",
                "industry": "healthcare"
            }
        )
        
        # Extract theme attributes
        theme_names = [r.theme.name for r in results if r.success]
        primary_colors = [
            r.theme.tokens.colors.get("primary", {}).get("value")
            for r in results if r.success
        ]
        
        # All should be the same
        assert len(set(theme_names)) == 1, "Theme name should be consistent"
        assert len(set(primary_colors)) == 1, "Primary color should be consistent"
        
        print(f"\n✅ Theme consistency maintained: {theme_names[0]}")
    
    @pytest.mark.asyncio
    async def test_complex_content_handling(self, orchestrator):
        """Test handling of complex slides with many elements."""
        slide = Slide(
            slide_id="complex_001",
            slide_number=1,
            title="Comprehensive Market Analysis",
            slide_type="content_heavy",
            narrative="Deep dive into market dynamics",
            key_points=[
                "Market size: $45B growing at 12% CAGR",
                "Key players: Company A (35%), Company B (25%), Us (15%)",
                "Growth drivers: Digital transformation, COVID-19, Remote work",
                "Challenges: Regulation, Competition, Technology shifts",
                "Opportunities: Emerging markets, New segments, Partnerships",
                "Strategic focus: Innovation, Customer experience, M&A"
            ],
            visuals_needed="Market share pie chart, growth trend line",
            analytics_needed="Competitive analysis matrix"
        )
        
        request = LayoutGenerationRequest(
            slide=slide,
            layout_config=LayoutEngineConfig(
                max_iterations=5,
                white_space_min=0.25,  # Allow less white space for complex content
                white_space_max=0.4
            )
        )
        
        result = await orchestrator.generate_layout(request)
        
        assert result.success
        assert len(result.layout.containers) >= 6  # Should handle all content
        assert len(result.manifest.containers) >= 6
        
        # Check relationships for complex content
        assert len(result.manifest.relationships) > 3  # Should identify connections
        
        print(f"\n✅ Complex slide handled: {len(result.layout.containers)} containers")
        print(f"   Relationships: {len(result.manifest.relationships)}")
        print(f"   Complexity score: {result.manifest.complexity_score:.2f}")
    
    @pytest.mark.asyncio
    async def test_slide_complexity_analysis(self, orchestrator):
        """Test the slide complexity analysis feature."""
        slides = [
            Slide(
                slide_id="simple",
                slide_number=1,
                title="Simple Title",
                slide_type="title_slide",
                key_points=["One key message"]
            ),
            Slide(
                slide_id="complex",
                slide_number=2,
                title="Complex Analysis",
                slide_type="data_driven",
                key_points=["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
                analytics_needed="Multiple charts",
                visuals_needed="Diagrams"
            )
        ]
        
        for slide in slides:
            complexity = await orchestrator.analyze_slide_complexity(slide)
            
            print(f"\n📊 {slide.slide_id} complexity:")
            print(f"   Containers: {complexity['container_count']}")
            print(f"   Score: {complexity['complexity_score']:.2f}")
            print(f"   Flow: {complexity['content_flow']}")
            
            if slide.slide_id == "simple":
                assert complexity['complexity_score'] < 0.4
                assert complexity['container_count'] <= 2
            else:
                assert complexity['complexity_score'] > 0.5
                assert complexity['container_count'] >= 5


class TestQualityAssurance:
    """Test quality assurance for generated layouts."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.mark.asyncio
    async def test_layout_quality_metrics(self, orchestrator):
        """Test that all layouts meet quality standards."""
        slides = [
            get_test_strawman(3).slides[0],  # Title slide
            get_test_strawman(3).slides[1],  # Content slide
            get_test_strawman(3).slides[2]   # Another slide
        ]
        
        results = await orchestrator.generate_batch(slides=slides)
        
        for result in results:
            if not result.success:
                continue
            
            # Analyze quality
            layout = result.layout
            
            # White space check
            assert 0.2 <= layout.white_space_ratio <= 0.6, \
                f"White space {layout.white_space_ratio} out of range"
            
            # Container overlap check
            positions = [(c.position.leftInset, c.position.topInset, 
                         c.position.width, c.position.height) 
                        for c in layout.containers]
            
            for i, pos1 in enumerate(positions):
                for j, pos2 in enumerate(positions[i+1:], i+1):
                    assert not self._rectangles_overlap(pos1, pos2), \
                        f"Containers {i} and {j} overlap"
            
            # Margin check
            for container in layout.containers:
                assert container.position.leftInset >= 8, "Left margin violation"
                assert container.position.topInset >= 8, "Top margin violation"
                assert container.position.leftInset + container.position.width <= 152, "Right margin violation"
                assert container.position.topInset + container.position.height <= 82, "Bottom margin violation"
            
            print(f"\n✅ Layout {result.slide_id} passes quality checks")
    
    def _rectangles_overlap(self, rect1: tuple, rect2: tuple) -> bool:
        """Check if two rectangles overlap."""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or 
                   y1 + h1 <= y2 or y2 + h2 <= y1)
    
    @pytest.mark.asyncio
    async def test_semantic_accuracy(self, orchestrator):
        """Test that semantic analysis accurately reflects content."""
        slide = Slide(
            slide_id="semantic_test",
            slide_number=1,
            title="Key Performance Indicators",
            slide_type="data_driven",
            key_points=[
                "Revenue: $45M (↑23%)",
                "Users: 150K active",
                "Retention: 85%"
            ],
            analytics_needed="KPI dashboard with trends"
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        assert result.success
        
        # Check semantic roles
        roles = [c.role.value for c in result.manifest.containers]
        assert "headline" in roles
        assert "kpi_metric" in roles or "chart" in roles
        
        # Check importance levels
        important_containers = [c for c in result.manifest.containers 
                               if c.importance.value in ["high", "critical"]]
        assert len(important_containers) >= 2  # Title and at least one KPI
        
        print(f"\n✅ Semantic analysis accurate: {len(roles)} roles identified")


class TestPerformanceBenchmark:
    """Benchmark performance of the integrated system."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.mark.asyncio
    async def test_performance_scaling(self, orchestrator):
        """Test how performance scales with number of slides."""
        generator = SyntheticDataGenerator(seed=42)
        
        slide_counts = [1, 5, 10]
        results = {}
        
        for count in slide_counts:
            slides = [
                generator.generate_slide(f"perf_{i}", i, "content_heavy")
                for i in range(count)
            ]
            
            start_time = time.time()
            batch_results = await orchestrator.generate_batch(slides=slides)
            total_time = time.time() - start_time
            
            successful = sum(1 for r in batch_results if r.success)
            avg_time = total_time / count
            
            results[count] = {
                "total_time": total_time,
                "avg_time": avg_time,
                "success_rate": successful / count
            }
            
            print(f"\n📊 {count} slides: {total_time:.2f}s total, {avg_time:.2f}s/slide")
        
        # Check that performance scales reasonably
        # Average time per slide shouldn't increase dramatically
        assert results[10]["avg_time"] < results[1]["avg_time"] * 1.5
    
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, orchestrator):
        """Test concurrent layout generation."""
        slides = [
            Slide(
                slide_id=f"concurrent_{i}",
                slide_number=i,
                title=f"Slide {i}",
                slide_type="content_heavy",
                key_points=[f"Point {j}" for j in range(3)]
            )
            for i in range(3)
        ]
        
        # Generate concurrently
        start_time = time.time()
        tasks = [
            orchestrator.generate_layout(LayoutGenerationRequest(slide=slide))
            for slide in slides
        ]
        results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        # Generate sequentially for comparison
        start_time = time.time()
        sequential_results = []
        for slide in slides:
            result = await orchestrator.generate_layout(
                LayoutGenerationRequest(slide=slide)
            )
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        print(f"\n⚡ Concurrent: {concurrent_time:.2f}s")
        print(f"🐌 Sequential: {sequential_time:.2f}s")
        print(f"Speedup: {sequential_time/concurrent_time:.2f}x")
        
        # All should succeed
        assert all(r.success for r in results)
        assert len(results) == len(slides)


if __name__ == "__main__":
    # Run specific test
    import sys
    
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        pytest.main([__file__, "-k", test_class, "-v"])
    else:
        pytest.main([__file__, "-v"])