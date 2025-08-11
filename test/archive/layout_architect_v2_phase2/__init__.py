"""
Test suite for the three-agent Layout Architect system.

This package contains comprehensive tests for:
- Individual agent testing with synthetic inputs
- Integrated three-agent workflow testing
- Director_IN integration testing
- Quality metrics and performance testing
- Edge case handling
- Visual output generation
"""

import os
import sys

# Add parent directories to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(test_dir))
sys.path.insert(0, project_root)

# Common test utilities
from typing import Dict, Any, List
from src.models.agents import Slide, PresentationStrawman
from src.agents.layout_architect import (
    ThemeDefinition, ContainerManifest, MVPLayout,
    SemanticContainer, ContainerRole, ContentImportance
)

def create_test_slide(
    slide_id: str = "test_001",
    slide_type: str = "content_heavy",
    title: str = "Test Slide",
    key_points: List[str] = None
) -> Slide:
    """Create a test slide with default values."""
    if key_points is None:
        key_points = ["Point 1", "Point 2", "Point 3"]
    
    return Slide(
        slide_id=slide_id,
        slide_number=1,
        title=title,
        slide_type=slide_type,
        narrative="Test narrative",
        key_points=key_points
    )

def create_test_theme() -> ThemeDefinition:
    """Create a test theme definition."""
    return ThemeDefinition(
        name="test_theme",
        style_attributes={
            "formality": "professional",
            "color_scheme": "blue",
            "typography": "modern"
        }
    )

def create_test_manifest(slide_id: str = "test_001") -> ContainerManifest:
    """Create a test container manifest."""
    containers = [
        SemanticContainer(
            id=f"{slide_id}_title",
            role=ContainerRole.HEADLINE,
            content="Test Title",
            hierarchy_level=1,
            importance=ContentImportance.HIGH,
            visual_weight=0.8
        ),
        SemanticContainer(
            id=f"{slide_id}_main",
            role=ContainerRole.MAIN_POINT,
            content="Main content here",
            hierarchy_level=2,
            importance=ContentImportance.MEDIUM,
            visual_weight=0.5
        )
    ]
    
    return ContainerManifest(
        slide_id=slide_id,
        slide_type="content_heavy",
        containers=containers,
        relationships=[],
        primary_message="Test message",
        content_flow="linear",
        visual_hierarchy=[c.id for c in containers],
        groupings=[],
        content_density=0.5,
        complexity_score=0.3
    )

# Test configuration
TEST_CONFIG = {
    "api_timeout": 30,
    "max_retries": 3,
    "enable_visual_output": True,
    "output_dir": os.path.join(test_dir, "output"),
    "fixtures_dir": os.path.join(test_dir, "fixtures")
}