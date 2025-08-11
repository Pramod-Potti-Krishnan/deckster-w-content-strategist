"""
Grid calculator tool for integer-based positioning.

Ensures all positions and dimensions use integer values only,
following the 160x90 grid system.
"""

from typing import Tuple, Optional
from ..models import GridPosition


class GridCalculator:
    """Calculator for grid-based positioning with integer precision."""
    
    def __init__(self, grid_width: int = 160, grid_height: int = 90):
        """Initialize with grid dimensions."""
        self.grid_width = grid_width
        self.grid_height = grid_height
    
    def snap_to_grid(self, value: float) -> int:
        """Snap any value to nearest integer grid unit."""
        return round(value)
    
    def validate_position(self, position: GridPosition) -> bool:
        """Validate that position uses only integers and fits within grid."""
        # Check integer values
        if not position.validate_integers():
            return False
        
        # Check bounds
        if position.leftInset < 0 or position.topInset < 0:
            return False
        
        if position.leftInset + position.width > self.grid_width:
            return False
        
        if position.topInset + position.height > self.grid_height:
            return False
        
        return True
    
    def constrain_to_grid(self, position: GridPosition) -> GridPosition:
        """Constrain position to fit within grid bounds."""
        # Ensure integers
        x = self.snap_to_grid(position.leftInset)
        y = self.snap_to_grid(position.topInset)
        w = self.snap_to_grid(position.width)
        h = self.snap_to_grid(position.height)
        
        # Constrain to bounds
        x = max(0, min(x, self.grid_width - 1))
        y = max(0, min(y, self.grid_height - 1))
        w = max(1, min(w, self.grid_width - x))
        h = max(1, min(h, self.grid_height - y))
        
        return GridPosition(leftInset=x, topInset=y, width=w, height=h)
    
    def calculate_available_space(
        self,
        margin: int = 8
    ) -> Tuple[int, int, int, int]:
        """Calculate available space after margins."""
        x = margin
        y = margin
        width = self.grid_width - (2 * margin)
        height = self.grid_height - (2 * margin)
        return x, y, width, height
    
    def distribute_space(
        self,
        total_space: int,
        num_items: int,
        gutter: int = 4
    ) -> Tuple[int, int]:
        """Distribute space evenly among items with gutters."""
        if num_items == 0:
            return 0, 0
        
        total_gutters = (num_items - 1) * gutter
        available = total_space - total_gutters
        item_size = available // num_items
        remainder = available % num_items
        
        return item_size, remainder
    
    def calculate_grid_layout(
        self,
        num_items: int,
        available_width: int,
        available_height: int,
        gutter: int = 4,
        max_cols: int = 3
    ) -> Tuple[int, int, int, int]:
        """Calculate optimal grid layout dimensions."""
        if num_items == 0:
            return 0, 0, 0, 0
        
        # Determine columns and rows
        cols = min(num_items, max_cols)
        rows = (num_items + cols - 1) // cols
        
        # Calculate cell dimensions
        cell_width = (available_width - (cols - 1) * gutter) // cols
        cell_height = (available_height - (rows - 1) * gutter) // rows
        
        return cols, rows, cell_width, cell_height
    
    def align_to_baseline(
        self,
        positions: list[GridPosition],
        baseline: Optional[int] = None
    ) -> list[GridPosition]:
        """Align multiple positions to a common baseline."""
        if not positions:
            return positions
        
        # Use provided baseline or find the most common Y
        if baseline is None:
            y_values = [p.topInset for p in positions]
            baseline = max(set(y_values), key=y_values.count)
        
        aligned = []
        for pos in positions:
            aligned_pos = GridPosition(
                leftInset=pos.leftInset,
                topInset=baseline,
                width=pos.width,
                height=pos.height
            )
            aligned.append(aligned_pos)
        
        return aligned
    
    def center_in_area(
        self,
        content_width: int,
        content_height: int,
        area_x: int,
        area_y: int,
        area_width: int,
        area_height: int
    ) -> GridPosition:
        """Center content within an area."""
        x = area_x + (area_width - content_width) // 2
        y = area_y + (area_height - content_height) // 2
        
        return GridPosition(
            leftInset=x,
            topInset=y,
            width=content_width,
            height=content_height
        )