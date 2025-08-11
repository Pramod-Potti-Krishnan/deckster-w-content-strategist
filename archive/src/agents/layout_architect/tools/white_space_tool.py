"""
White space validation tool for ensuring proper spacing.

Validates that layouts maintain 30-50% white space ratio
and proper margins/gutters.
"""

from typing import List, Tuple, Dict
from ..models import MVPContainer, GridPosition


class WhiteSpaceTool:
    """Tool for calculating and validating white space in layouts."""
    
    def __init__(
        self,
        grid_width: int = 160,
        grid_height: int = 90,
        min_ratio: float = 0.3,
        max_ratio: float = 0.5
    ):
        """Initialize with grid dimensions and target ratios."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.total_area = grid_width * grid_height
    
    def calculate_white_space_ratio(
        self,
        containers: List[MVPContainer]
    ) -> float:
        """Calculate the white space ratio for a layout."""
        used_area = 0
        
        for container in containers:
            if container.position and container.position != "from_theme":
                pos = container.position
                used_area += pos.width * pos.height
        
        white_space_area = self.total_area - used_area
        return white_space_area / self.total_area
    
    def validate_white_space_ratio(
        self,
        ratio: float
    ) -> Tuple[bool, str]:
        """Validate if white space ratio is within acceptable range."""
        if ratio < self.min_ratio:
            return False, f"White space ratio {ratio:.2f} is below minimum {self.min_ratio}"
        elif ratio > self.max_ratio:
            return False, f"White space ratio {ratio:.2f} is above maximum {self.max_ratio}"
        else:
            return True, f"White space ratio {ratio:.2f} is optimal"
    
    def validate_margins(
        self,
        containers: List[MVPContainer],
        min_margin: int = 8
    ) -> Tuple[bool, List[str]]:
        """Validate that all containers respect minimum margins."""
        violations = []
        
        for container in containers:
            if container.position and container.position != "from_theme":
                pos = container.position
                
                # Check left margin
                if pos.leftInset < min_margin:
                    violations.append(
                        f"{container.name}: left margin {pos.leftInset} < {min_margin}"
                    )
                
                # Check top margin
                if pos.topInset < min_margin:
                    violations.append(
                        f"{container.name}: top margin {pos.topInset} < {min_margin}"
                    )
                
                # Check right margin
                right_edge = pos.leftInset + pos.width
                if right_edge > self.grid_width - min_margin:
                    violations.append(
                        f"{container.name}: right margin violation at {right_edge}"
                    )
                
                # Check bottom margin
                bottom_edge = pos.topInset + pos.height
                if bottom_edge > self.grid_height - min_margin:
                    violations.append(
                        f"{container.name}: bottom margin violation at {bottom_edge}"
                    )
        
        return len(violations) == 0, violations
    
    def validate_gutters(
        self,
        containers: List[MVPContainer],
        min_gutter: int = 4
    ) -> Tuple[bool, List[str]]:
        """Validate minimum spacing between containers."""
        violations = []
        
        # Check all pairs of containers
        for i, c1 in enumerate(containers):
            if not c1.position or c1.position == "from_theme":
                continue
                
            for j, c2 in enumerate(containers[i+1:], i+1):
                if not c2.position or c2.position == "from_theme":
                    continue
                
                distance = self._calculate_container_distance(
                    c1.position, c2.position
                )
                
                if distance < min_gutter and distance >= 0:
                    violations.append(
                        f"{c1.name} and {c2.name}: spacing {distance} < {min_gutter}"
                    )
        
        return len(violations) == 0, violations
    
    def _calculate_container_distance(
        self,
        pos1: GridPosition,
        pos2: GridPosition
    ) -> int:
        """Calculate minimum distance between two containers."""
        # Check if containers overlap
        if self._containers_overlap(pos1, pos2):
            return -1
        
        # Calculate horizontal distance
        h_distance = 0
        if pos1.leftInset + pos1.width <= pos2.leftInset:
            h_distance = pos2.leftInset - (pos1.leftInset + pos1.width)
        elif pos2.leftInset + pos2.width <= pos1.leftInset:
            h_distance = pos1.leftInset - (pos2.leftInset + pos2.width)
        
        # Calculate vertical distance
        v_distance = 0
        if pos1.topInset + pos1.height <= pos2.topInset:
            v_distance = pos2.topInset - (pos1.topInset + pos1.height)
        elif pos2.topInset + pos2.height <= pos1.topInset:
            v_distance = pos1.topInset - (pos2.topInset + pos2.height)
        
        # Return minimum non-zero distance
        if h_distance > 0 and v_distance > 0:
            return min(h_distance, v_distance)
        elif h_distance > 0:
            return h_distance
        elif v_distance > 0:
            return v_distance
        else:
            return 0
    
    def _containers_overlap(
        self,
        pos1: GridPosition,
        pos2: GridPosition
    ) -> bool:
        """Check if two containers overlap."""
        # Check horizontal overlap
        h_overlap = not (
            pos1.leftInset + pos1.width <= pos2.leftInset or
            pos2.leftInset + pos2.width <= pos1.leftInset
        )
        
        # Check vertical overlap
        v_overlap = not (
            pos1.topInset + pos1.height <= pos2.topInset or
            pos2.topInset + pos2.height <= pos1.topInset
        )
        
        return h_overlap and v_overlap
    
    def suggest_white_space_adjustment(
        self,
        current_ratio: float,
        containers: List[MVPContainer]
    ) -> Dict[str, any]:
        """Suggest adjustments to achieve target white space ratio."""
        target_ratio = (self.min_ratio + self.max_ratio) / 2
        
        if abs(current_ratio - target_ratio) < 0.05:
            return {"action": "none", "message": "White space is optimal"}
        
        if current_ratio < self.min_ratio:
            # Need more white space - reduce container sizes
            scale_factor = 0.9
            return {
                "action": "reduce_sizes",
                "scale_factor": scale_factor,
                "message": f"Reduce container sizes by {(1-scale_factor)*100:.0f}%"
            }
        else:
            # Too much white space - increase container sizes
            scale_factor = 1.1
            return {
                "action": "increase_sizes",
                "scale_factor": scale_factor,
                "message": f"Increase container sizes by {(scale_factor-1)*100:.0f}%"
            }
    
    def calculate_breathing_room(
        self,
        containers: List[MVPContainer]
    ) -> Dict[str, float]:
        """Calculate breathing room metrics for the layout."""
        if not containers:
            return {"average": 0, "min": 0, "max": 0}
        
        distances = []
        
        for i, c1 in enumerate(containers):
            if not c1.position or c1.position == "from_theme":
                continue
                
            for j, c2 in enumerate(containers[i+1:], i+1):
                if not c2.position or c2.position == "from_theme":
                    continue
                
                distance = self._calculate_container_distance(
                    c1.position, c2.position
                )
                if distance >= 0:
                    distances.append(distance)
        
        if not distances:
            return {"average": 0, "min": 0, "max": 0}
        
        return {
            "average": sum(distances) / len(distances),
            "min": min(distances),
            "max": max(distances)
        }