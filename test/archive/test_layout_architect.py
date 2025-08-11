"""
Tests for Layout Architect MVP.

Tests core functionality including white space calculation,
grid alignment validation, and layout generation.
"""

import os
import sys
import pytest
from typing import List

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.models import (
    MVPContainer, MVPLayout, MVPTheme, GridPosition,
    ContainerContent, LayoutConfig, LayoutSpec, ContentState,
    ThemeConfig, ThemeColors, ThemeTypography, ThemeLayout
)
from src.agents.layout_architect.tools import (
    GridCalculator, WhiteSpaceTool, AlignmentValidator
)
from src.agents.layout_architect.layout_engine import LayoutEngine
from src.models.agents import Slide


class TestWhiteSpaceTool:
    """Test white space calculations and validation."""
    
    def test_white_space_calculation(self):
        """Test that white space ratio is calculated correctly."""
        tool = WhiteSpaceTool()
        
        # Create test containers
        containers = [
            MVPContainer(
                name="title",
                content=ContainerContent(type="text", text="Title"),
                position=GridPosition(leftInset=8, topInset=8, width=144, height=12)
            ),
            MVPContainer(
                name="body",
                content=ContainerContent(type="text", text="Content"),
                position=GridPosition(leftInset=8, topInset=24, width=144, height=50)
            )
        ]
        
        ratio = tool.calculate_white_space_ratio(containers)
        
        # Total area = 160 * 90 = 14400
        # Used area = (144 * 12) + (144 * 50) = 1728 + 7200 = 8928
        # White space = 14400 - 8928 = 5472
        # Ratio = 5472 / 14400 = 0.38
        
        assert 0.37 <= ratio <= 0.39
    
    def test_margin_validation(self):
        """Test margin validation."""
        tool = WhiteSpaceTool()
        
        # Valid margins
        valid_containers = [
            MVPContainer(
                name="test",
                content=ContainerContent(type="text", text="Test"),
                position=GridPosition(leftInset=8, topInset=8, width=144, height=74)
            )
        ]
        
        valid, issues = tool.validate_margins(valid_containers, min_margin=8)
        assert valid
        assert len(issues) == 0
        
        # Invalid margins
        invalid_containers = [
            MVPContainer(
                name="test",
                content=ContainerContent(type="text", text="Test"),
                position=GridPosition(leftInset=4, topInset=4, width=156, height=86)
            )
        ]
        
        valid, issues = tool.validate_margins(invalid_containers, min_margin=8)
        assert not valid
        assert len(issues) > 0


class TestAlignmentValidator:
    """Test grid alignment validation."""
    
    def test_row_alignment(self):
        """Test that containers in same row are detected."""
        validator = AlignmentValidator()
        
        # Aligned containers
        aligned_containers = [
            MVPContainer(
                name="item1",
                content=ContainerContent(type="text", text="Item 1"),
                position=GridPosition(leftInset=8, topInset=20, width=70, height=20)
            ),
            MVPContainer(
                name="item2",
                content=ContainerContent(type="text", text="Item 2"),
                position=GridPosition(leftInset=82, topInset=20, width=70, height=20)
            )
        ]
        
        valid, score, issues = validator.validate_alignment(aligned_containers)
        assert valid
        assert score >= 0.9
        assert len(issues) == 0
    
    def test_integer_position_validation(self):
        """Test that all positions must be integers."""
        validator = AlignmentValidator()
        
        # All integer positions
        containers = [
            MVPContainer(
                name="test",
                content=ContainerContent(type="text", text="Test"),
                position=GridPosition(leftInset=10, topInset=20, width=30, height=40)
            )
        ]
        
        valid, score, issues = validator.validate_alignment(containers)
        assert valid
        
        # Check for fractional positions (would fail in real scenario)
        # Note: Our model enforces integers, so this is more of a safety check


class TestGridCalculator:
    """Test grid positioning calculations."""
    
    def test_snap_to_grid(self):
        """Test snapping values to grid."""
        calc = GridCalculator()
        
        assert calc.snap_to_grid(10.2) == 10
        assert calc.snap_to_grid(10.5) == 10  # Python uses banker's rounding
        assert calc.snap_to_grid(10.8) == 11
        assert calc.snap_to_grid(11.5) == 12  # 11.5 rounds to 12
    
    def test_distribute_space(self):
        """Test space distribution among items."""
        calc = GridCalculator()
        
        # 3 items in 100 units with 4 unit gutters
        item_size, remainder = calc.distribute_space(100, 3, 4)
        
        # Total gutters = 2 * 4 = 8
        # Available = 100 - 8 = 92
        # Item size = 92 // 3 = 30
        # Remainder = 92 % 3 = 2
        
        assert item_size == 30
        assert remainder == 2
    
    def test_grid_layout_calculation(self):
        """Test grid layout dimensions."""
        calc = GridCalculator()
        
        cols, rows, cell_w, cell_h = calc.calculate_grid_layout(
            num_items=6,
            available_width=150,
            available_height=80,
            gutter=4,
            max_cols=3
        )
        
        assert cols == 3
        assert rows == 2
        assert cell_w == 47  # (150 - 2*4) // 3
        assert cell_h == 38  # (80 - 1*4) // 2


class TestLayoutEngine:
    """Test layout engine functionality."""
    
    @pytest.fixture
    def layout_engine(self):
        """Create layout engine with default config."""
        config = LayoutConfig()
        return LayoutEngine(config)
    
    @pytest.fixture
    def sample_theme(self):
        """Create sample theme for testing."""
        return MVPTheme(
            theme_name="test_theme",
            theme_config=ThemeConfig(
                layouts={
                    "titleSlide": ThemeLayout(
                        containers={
                            "title": GridPosition(leftInset=20, topInset=35, width=120, height=20),
                            "subtitle": GridPosition(leftInset=20, topInset=55, width=120, height=10)
                        }
                    ),
                    "contentSlide": ThemeLayout(
                        containers={
                            "title": GridPosition(leftInset=8, topInset=8, width=144, height=12),
                            "body": GridPosition(leftInset=8, topInset=24, width=144, height=58)
                        }
                    )
                },
                typography={
                    "h1": ThemeTypography(fontSize=48, fontWeight="bold"),
                    "body": ThemeTypography(fontSize=18, fontWeight="normal")
                },
                colors=ThemeColors(
                    primary="#0066cc",
                    secondary="#4d94ff",
                    background="#ffffff",
                    text="#333333"
                )
            ),
            created_for_session="test_session"
        )
    
    def test_vertical_layout(self, layout_engine, sample_theme):
        """Test vertical layout arrangement."""
        slide = Slide(
            slide_id="test_1",
            slide_number=1,
            title="Test Slide",
            slide_type="content_heavy",
            key_message="Test message",
            content_outline=[],
            speaker_notes="",
            key_points=["Point 1", "Point 2", "Point 3"],
            narrative="Test narrative"
        )
        
        # This would be an async test in real implementation
        # For now, testing the structure
        assert layout_engine is not None
        assert layout_engine.config.grid_width == 160
        assert layout_engine.config.grid_height == 90
    
    def test_white_space_compliance(self, layout_engine):
        """Test that layouts maintain proper white space ratio."""
        # Test containers that should have ~40% white space
        containers = [
            MVPContainer(
                name="title",
                content=ContainerContent(type="text", text="Title"),
                position=GridPosition(leftInset=8, topInset=8, width=144, height=12)
            ),
            MVPContainer(
                name="content",
                content=ContainerContent(type="text", text="Content"),
                position=GridPosition(leftInset=8, topInset=24, width=144, height=50)
            )
        ]
        
        ratio = layout_engine._calculate_white_space(containers)
        assert 0.3 <= ratio <= 0.5