#!/usr/bin/env python3
"""
Simple test to verify Layout Architect setup is working.
"""

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    ThemeAgent,
    StructureAgent,
    LayoutEngineAgent,
    MVPLayout,
    MVPContainer,
    ThemeDefinition,
    ContainerManifest
)
from src.models.agents import Slide


def test_imports_work():
    """Test that all imports are working correctly."""
    assert LayoutArchitectOrchestrator is not None
    assert ThemeAgent is not None
    assert StructureAgent is not None
    assert LayoutEngineAgent is not None
    assert MVPLayout is not None
    assert MVPContainer is not None
    assert ThemeDefinition is not None
    assert ContainerManifest is not None
    assert Slide is not None


def test_create_slide():
    """Test creating a simple slide."""
    slide = Slide(
        slide_id="test_001",
        slide_number=1,
        slide_type="content_heavy",
        title="Test Slide",
        key_points=["Point 1", "Point 2", "Point 3"],
        narrative="This is a test slide"
    )
    assert slide.slide_id == "test_001"
    assert slide.slide_type == "content_heavy"
    assert slide.title == "Test Slide"
    assert len(slide.key_points) == 3
    assert slide.narrative == "This is a test slide"


def test_create_mvp_layout():
    """Test creating an MVP layout."""
    from src.agents.layout_architect import GridPosition, ContainerContent
    
    container = MVPContainer(
        name="test_container",
        position=GridPosition(
            leftInset=10,
            topInset=10,
            width=100,
            height=50
        ),
        content=ContainerContent(
            type="text",
            text="Test content",
            style="body"
        )
    )
    
    layout = MVPLayout(
        slide_id="test_001",
        containers=[container],
        white_space_ratio=0.4
    )
    
    assert layout.slide_id == "test_001"
    assert len(layout.containers) == 1
    assert layout.containers[0].name == "test_container"
    assert layout.white_space_ratio == 0.4


def test_create_theme_definition():
    """Test creating a theme definition."""
    theme = ThemeDefinition(
        name="test_theme",
        style_attributes={
            "primaryColor": "#0066CC",
            "secondaryColor": "#E8F0FE",
            "fontFamily": "Arial"
        }
    )
    
    assert theme.name == "test_theme"
    assert theme.style_attributes["primaryColor"] == "#0066CC"
    assert theme.style_attributes["fontFamily"] == "Arial"


@pytest.mark.skip(reason="Requires API key")
def test_create_orchestrator_with_api():
    """Test creating orchestrator (requires API key)."""
    try:
        orchestrator = LayoutArchitectOrchestrator()
        assert orchestrator.theme_agent is not None
        assert orchestrator.structure_agent is not None
        assert orchestrator.layout_engine is not None
    except Exception as e:
        if "API_KEY" in str(e):
            pytest.skip("API key not configured")
        else:
            raise


if __name__ == "__main__":
    print("Running setup verification tests...")
    test_imports_work()
    print("✓ Imports working")
    
    test_create_slide()
    print("✓ Slide creation working")
    
    test_create_mvp_layout()
    print("✓ MVP Layout creation working")
    
    test_create_theme_definition()
    print("✓ Theme Definition creation working")
    
    print("\n✅ All basic tests passed! Layout Architect setup is working correctly.")
    print("\nTo run tests with API access, use: pytest test_setup_verification.py --with-api")