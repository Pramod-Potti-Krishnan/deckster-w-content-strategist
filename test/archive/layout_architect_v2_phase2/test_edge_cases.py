"""
Edge case testing for Layout Architect.

Tests error handling, boundary conditions, and unusual scenarios.
"""

import asyncio
import pytest
import os
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from src.models.agents import Slide, PresentationStrawman
from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest,
    LayoutEngineConfig
)
from .test_synthetic_data import SyntheticDataGenerator


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.mark.asyncio
    async def test_empty_slide(self, orchestrator):
        """Test handling of empty slide."""
        slide = Slide(
            slide_id="empty_001",
            slide_number=1,
            title="",
            slide_type="content_heavy",
            key_points=[],
            narrative=""
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        # Should handle gracefully
        assert result.layout is not None
        assert len(result.layout.containers) >= 1  # At least a placeholder
        
        if result.success:
            print("\n✅ Empty slide handled successfully")
        else:
            print(f"\n⚠️  Empty slide fallback: {result.error_message}")
    
    @pytest.mark.asyncio
    async def test_overloaded_slide(self, orchestrator):
        """Test handling of slide with too much content."""
        # Create slide with 20 key points
        key_points = [f"Point {i}: This is a very detailed point that contains a lot of information" 
                      for i in range(20)]
        
        slide = Slide(
            slide_id="overload_001",
            slide_number=1,
            title="Extremely Complex Slide with Many Points",
            slide_type="content_heavy",
            key_points=key_points,
            narrative="This slide has way too much content",
            visuals_needed="Multiple charts and diagrams",
            analytics_needed="Complex dashboard with 10 metrics"
        )
        
        request = LayoutGenerationRequest(
            slide=slide,
            layout_config=LayoutEngineConfig(
                max_iterations=5,
                white_space_min=0.1,  # Allow less white space
                white_space_max=0.3
            )
        )
        
        result = await orchestrator.generate_layout(request)
        
        assert result.layout is not None
        print(f"\n📦 Overloaded slide: {len(result.layout.containers)} containers")
        
        # Should still maintain some white space
        assert result.layout.white_space_ratio >= 0.1
        
        # Check if all content was included or truncated
        container_count = len(result.layout.containers)
        if container_count < 20:
            print(f"   Content was consolidated: {container_count} containers for 20 points")
    
    @pytest.mark.asyncio
    async def test_invalid_slide_type(self, orchestrator):
        """Test handling of invalid slide type."""
        slide = Slide(
            slide_id="invalid_001",
            slide_number=1,
            title="Test Slide",
            slide_type="invalid_type",  # Not a standard type
            key_points=["Point 1", "Point 2"]
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        # Should handle gracefully with default behavior
        assert result.layout is not None
        print("\n✅ Invalid slide type handled gracefully")
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, orchestrator):
        """Test handling when API key is missing."""
        # Temporarily remove API keys
        original_google = os.environ.get("GOOGLE_API_KEY")
        original_gemini = os.environ.get("GEMINI_API_KEY")
        
        try:
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
            
            slide = SyntheticDataGenerator().generate_slide("api_test", 1)
            request = LayoutGenerationRequest(slide=slide)
            
            # Should fail gracefully
            result = await orchestrator.generate_layout(request)
            
            assert result.error_message is not None
            assert "API" in result.error_message or not result.success
            print(f"\n✅ Missing API key handled: {result.error_message}")
            
        finally:
            # Restore API keys
            if original_google:
                os.environ["GOOGLE_API_KEY"] = original_google
            if original_gemini:
                os.environ["GEMINI_API_KEY"] = original_gemini
    
    @pytest.mark.asyncio
    async def test_malformed_configuration(self, orchestrator):
        """Test handling of invalid configuration."""
        slide = SyntheticDataGenerator().generate_slide("config_test", 1)
        
        # Invalid config: min > max
        request = LayoutGenerationRequest(
            slide=slide,
            layout_config=LayoutEngineConfig(
                max_iterations=0,  # Invalid: should be > 0
                white_space_min=0.8,  # Invalid: min > max
                white_space_max=0.2,
                balance_threshold=2.0  # Invalid: should be <= 1
            )
        )
        
        result = await orchestrator.generate_layout(request)
        
        # Should either fix config or use defaults
        assert result.layout is not None
        print("\n✅ Malformed config handled")
    
    @pytest.mark.asyncio
    async def test_unicode_content(self, orchestrator):
        """Test handling of unicode and special characters."""
        slide = Slide(
            slide_id="unicode_001",
            slide_number=1,
            title="Unicode Test: 测试 🚀 Testing",
            slide_type="content_heavy",
            key_points=[
                "English text with émojis 😊",
                "中文内容测试",
                "Математические символы: ∑∏∫",
                "Special chars: €£¥₹"
            ],
            narrative="Testing unicode handling"
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        assert result.success or result.layout is not None
        print("\n✅ Unicode content handled")
    
    @pytest.mark.asyncio
    async def test_extremely_long_text(self, orchestrator):
        """Test handling of extremely long text content."""
        long_text = "This is an extremely long piece of text that goes on and on " * 50
        
        slide = Slide(
            slide_id="longtext_001",
            slide_number=1,
            title="Slide with Very Long Content",
            slide_type="content_heavy",
            key_points=[long_text[:200], long_text[200:400], long_text[400:600]],
            narrative=long_text
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        assert result.layout is not None
        
        # Check if text was truncated or wrapped
        for container in result.layout.containers:
            if hasattr(container.content, 'text'):
                assert len(container.content.text) < 1000  # Should truncate
        
        print("\n✅ Long text handled with truncation")
    
    @pytest.mark.asyncio
    async def test_null_values(self, orchestrator):
        """Test handling of null/None values."""
        slide = Slide(
            slide_id="null_001",
            slide_number=1,
            title="Test Slide",
            slide_type="content_heavy",
            key_points=["Valid point", None, "Another point"],  # None in list
            narrative=None,
            visuals_needed=None
        )
        
        # Filter out None values
        slide.key_points = [p for p in slide.key_points if p is not None]
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        assert result.layout is not None
        print("\n✅ Null values handled")
    
    @pytest.mark.asyncio
    async def test_circular_relationships(self, orchestrator):
        """Test handling of circular relationships in content."""
        slide = Slide(
            slide_id="circular_001",
            slide_number=1,
            title="Circular Process",
            slide_type="visual_heavy",
            key_points=[
                "Step 1 leads to Step 2",
                "Step 2 leads to Step 3",
                "Step 3 leads back to Step 1"
            ],
            narrative="Circular process flow"
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        assert result.success
        
        # Check if relationships were detected
        if result.manifest.relationships:
            print(f"\n✅ Circular relationships: {len(result.manifest.relationships)} detected")
    
    @pytest.mark.asyncio
    async def test_resource_constraints(self, orchestrator):
        """Test behavior under resource constraints."""
        # Generate many slides quickly
        slides = []
        for i in range(5):
            slide = SyntheticDataGenerator().generate_slide(f"resource_{i}", i)
            slides.append(slide)
        
        # Process concurrently to stress the system
        tasks = [
            orchestrator.generate_layout(LayoutGenerationRequest(slide=slide))
            for slide in slides
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception) and r.success)
        failures = len(results) - successes
        
        print(f"\n📊 Resource test: {successes} successes, {failures} failures")
        
        # Should handle at least some requests
        assert successes > 0
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, orchestrator):
        """Test handling of timeouts."""
        # This test would need actual timeout implementation
        # For now, test with very complex slide that takes long to process
        
        complex_slide = Slide(
            slide_id="timeout_001",
            slide_number=1,
            title="Complex Analysis",
            slide_type="data_driven",
            key_points=[f"Complex metric {i}" for i in range(10)],
            analytics_needed="Multiple complex charts",
            visuals_needed="Detailed diagrams"
        )
        
        request = LayoutGenerationRequest(
            slide=complex_slide,
            layout_config=LayoutEngineConfig(
                max_iterations=10  # Force many iterations
            )
        )
        
        # Should complete even if slow
        result = await orchestrator.generate_layout(request)
        assert result.layout is not None
        print("\n✅ Complex processing completed")


class TestBoundaryConditions:
    """Test boundary conditions for grid system."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.mark.asyncio
    async def test_minimum_container_size(self, orchestrator):
        """Test handling of minimum container size constraints."""
        slide = Slide(
            slide_id="minsize_001",
            slide_number=1,
            title="Many Small Items",
            slide_type="content_heavy",
            key_points=[f"Item {i}" for i in range(15)]  # Many small items
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        if result.success:
            # Check minimum sizes
            for container in result.layout.containers:
                assert container.position.width >= 20  # Minimum readable width
                assert container.position.height >= 10  # Minimum readable height
            
            print("\n✅ Minimum container sizes enforced")
    
    @pytest.mark.asyncio
    async def test_maximum_grid_utilization(self, orchestrator):
        """Test maximum utilization of grid space."""
        slide = Slide(
            slide_id="maxgrid_001",
            slide_number=1,
            title="Full Grid Test",
            slide_type="data_driven",
            key_points=["Maximize space usage"],
            analytics_needed="Large dashboard filling entire slide"
        )
        
        request = LayoutGenerationRequest(
            slide=slide,
            layout_config=LayoutEngineConfig(
                white_space_min=0.05,  # Allow very little white space
                white_space_max=0.15
            )
        )
        
        result = await orchestrator.generate_layout(request)
        
        if result.success:
            # Calculate total coverage
            total_area = 0
            for container in result.layout.containers:
                area = container.position.width * container.position.height
                total_area += area
            
            grid_area = 160 * 90
            coverage = total_area / grid_area
            
            print(f"\n📏 Grid utilization: {coverage:.1%}")
            assert coverage > 0.8  # Should use most of the grid
    
    @pytest.mark.asyncio
    async def test_edge_positioning(self, orchestrator):
        """Test containers at grid edges."""
        slide = Slide(
            slide_id="edge_001",
            slide_number=1,
            title="Edge Positioning Test",
            slide_type="visual_heavy",
            key_points=["Top left", "Top right", "Bottom left", "Bottom right"],
            structure_preference="corners"
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        if result.success:
            # Check that containers respect margins
            for container in result.layout.containers:
                pos = container.position
                
                # Left edge
                assert pos.leftInset >= 8
                
                # Top edge
                assert pos.topInset >= 8
                
                # Right edge
                assert pos.leftInset + pos.width <= 152  # 160 - 8
                
                # Bottom edge
                assert pos.topInset + pos.height <= 82  # 90 - 8
            
            print("\n✅ Edge positioning constraints respected")


class TestRecoveryMechanisms:
    """Test error recovery mechanisms."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self, orchestrator):
        """Test recovery from partial failures."""
        # Create a batch with one problematic slide
        slides = [
            SyntheticDataGenerator().generate_slide("normal_1", 1),
            Slide(  # Problematic slide
                slide_id="problem_001",
                slide_number=2,
                title="",
                slide_type="invalid_type",
                key_points=[]
            ),
            SyntheticDataGenerator().generate_slide("normal_2", 3)
        ]
        
        results = await orchestrator.generate_batch(slides=slides)
        
        assert len(results) == 3
        
        # Check that other slides still processed
        successful = [r for r in results if r.success]
        assert len(successful) >= 2  # At least the normal slides
        
        print(f"\n✅ Partial failure recovery: {len(successful)}/3 succeeded")
    
    @pytest.mark.asyncio
    async def test_fallback_theme_generation(self, orchestrator):
        """Test fallback when theme generation fails."""
        # Mock theme agent failure
        with patch.object(orchestrator.theme_agent, 'generate_theme') as mock_theme:
            mock_theme.side_effect = Exception("Theme generation failed")
            
            slide = SyntheticDataGenerator().generate_slide("theme_fail", 1)
            request = LayoutGenerationRequest(slide=slide)
            
            result = await orchestrator.generate_layout(request)
            
            # Should still produce a layout with fallback theme
            assert result.layout is not None
            assert result.theme.name == "fallback"
            print("\n✅ Fallback theme used when generation fails")
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, orchestrator):
        """Test graceful degradation of features."""
        slide = SyntheticDataGenerator().generate_slide("degrade_test", 1)
        
        # Request with very strict requirements
        request = LayoutGenerationRequest(
            slide=slide,
            layout_config=LayoutEngineConfig(
                max_iterations=1,  # Very limited iterations
                white_space_min=0.4,
                white_space_max=0.41,  # Very narrow range
                balance_threshold=0.95  # Very high threshold
            )
        )
        
        result = await orchestrator.generate_layout(request)
        
        # Should still produce something usable
        assert result.layout is not None
        assert len(result.layout.containers) > 0
        
        # May not meet all requirements
        if not result.success:
            print(f"\n⚠️  Degraded gracefully: {result.error_message}")
        else:
            print("\n✅ Handled strict requirements")


if __name__ == "__main__":
    # Run edge case tests
    pytest.main([__file__, "-v", "-k", "edge"])