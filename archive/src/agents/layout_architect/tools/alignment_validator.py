"""
Grid alignment validation tool.

Ensures containers align to rows and columns with consistent dimensions
for related elements.
"""

from typing import List, Tuple, Dict, Set
from collections import defaultdict
from ..models import MVPContainer, GridPosition, AlignmentInfo


class AlignmentValidator:
    """Validator for grid alignment and dimension consistency."""
    
    def __init__(self, tolerance: int = 0):
        """Initialize with alignment tolerance (0 for exact alignment)."""
        self.tolerance = tolerance
    
    def validate_alignment(
        self,
        containers: List[MVPContainer]
    ) -> Tuple[bool, float, List[str]]:
        """
        Validate container alignment and return score with issues.
        
        Returns:
            - is_valid: Whether alignment meets requirements
            - score: Alignment score (0-1)
            - issues: List of alignment issues found
        """
        if not containers:
            return True, 1.0, []
        
        alignment_info = self._analyze_alignment(containers)
        issues = []
        
        # Check row alignment
        row_issues = self._validate_row_alignment(alignment_info)
        issues.extend(row_issues)
        
        # Check column alignment
        col_issues = self._validate_column_alignment(alignment_info)
        issues.extend(col_issues)
        
        # Check dimension consistency
        dim_issues = self._validate_dimensions(containers)
        issues.extend(dim_issues)
        
        # Check integer positions
        int_issues = self._validate_integer_positions(containers)
        issues.extend(int_issues)
        
        # Calculate alignment score
        score = self._calculate_alignment_score(alignment_info, len(containers))
        
        return len(issues) == 0, score, issues
    
    def _analyze_alignment(
        self,
        containers: List[MVPContainer]
    ) -> AlignmentInfo:
        """Analyze container alignment patterns."""
        info = AlignmentInfo()
        
        for container in containers:
            if container.position and container.position != "from_theme":
                pos = container.position
                
                # Group by Y coordinate (rows)
                info.add_to_row(pos.topInset, container.name)
                
                # Group by X coordinate (columns)
                info.add_to_column(pos.leftInset, container.name)
                
                # Group by dimensions
                dim_key = f"{pos.width}x{pos.height}"
                info.add_to_dimension_group(dim_key, container.name)
        
        return info
    
    def _validate_row_alignment(
        self,
        alignment_info: AlignmentInfo
    ) -> List[str]:
        """Validate that containers in same row have exact Y alignment."""
        issues = []
        
        for y_coord, containers in alignment_info.row_groups.items():
            if len(containers) > 1:
                # All containers in this group should have exact same Y
                # (Already grouped by Y, so this validates the grouping logic)
                pass
        
        # Check for near-misses (containers that should be aligned but aren't)
        y_coords = sorted(alignment_info.row_groups.keys())
        for i, y1 in enumerate(y_coords):
            for y2 in y_coords[i+1:]:
                if 0 < abs(y2 - y1) <= 2:  # Within 2 units
                    issues.append(
                        f"Containers at Y={y1} and Y={y2} should be aligned to same row"
                    )
        
        return issues
    
    def _validate_column_alignment(
        self,
        alignment_info: AlignmentInfo
    ) -> List[str]:
        """Validate that containers in same column have exact X alignment."""
        issues = []
        
        # Check for near-misses
        x_coords = sorted(alignment_info.column_groups.keys())
        for i, x1 in enumerate(x_coords):
            for x2 in x_coords[i+1:]:
                if 0 < abs(x2 - x1) <= 2:  # Within 2 units
                    issues.append(
                        f"Containers at X={x1} and X={x2} should be aligned to same column"
                    )
        
        return issues
    
    def _validate_dimensions(
        self,
        containers: List[MVPContainer]
    ) -> List[str]:
        """Validate that similar containers have consistent dimensions."""
        issues = []
        
        # Group containers by type/role
        type_groups = defaultdict(list)
        for container in containers:
            if container.position and container.position != "from_theme":
                # Extract container type from name
                container_type = container.name.split('_')[0]
                type_groups[container_type].append(container)
        
        # Check dimension consistency within groups
        for container_type, group in type_groups.items():
            if len(group) > 1:
                # Get all unique dimensions
                dimensions = set()
                for container in group:
                    pos = container.position
                    dimensions.add((pos.width, pos.height))
                
                if len(dimensions) > 1:
                    dim_list = [f"{w}x{h}" for w, h in dimensions]
                    issues.append(
                        f"{container_type} containers have inconsistent dimensions: {dim_list}"
                    )
        
        return issues
    
    def _validate_integer_positions(
        self,
        containers: List[MVPContainer]
    ) -> List[str]:
        """Validate all positions use integer values."""
        issues = []
        
        for container in containers:
            if container.position and container.position != "from_theme":
                pos = container.position
                
                if not isinstance(pos.leftInset, int):
                    issues.append(f"{container.name}: X position {pos.leftInset} is not integer")
                
                if not isinstance(pos.topInset, int):
                    issues.append(f"{container.name}: Y position {pos.topInset} is not integer")
                
                if not isinstance(pos.width, int):
                    issues.append(f"{container.name}: width {pos.width} is not integer")
                
                if not isinstance(pos.height, int):
                    issues.append(f"{container.name}: height {pos.height} is not integer")
        
        return issues
    
    def _calculate_alignment_score(
        self,
        alignment_info: AlignmentInfo,
        total_containers: int
    ) -> float:
        """Calculate overall alignment score (0-1)."""
        if total_containers == 0:
            return 1.0
        
        # Score based on how many containers are in aligned groups
        aligned_containers = 0
        
        # Count containers in row groups of 2+
        for containers in alignment_info.row_groups.values():
            if len(containers) >= 2:
                aligned_containers += len(containers)
        
        # Count containers in column groups of 2+ (avoid double counting)
        counted = set()
        for containers in alignment_info.column_groups.values():
            if len(containers) >= 2:
                for c in containers:
                    if c not in counted:
                        aligned_containers += 1
                        counted.add(c)
        
        # Normalize to avoid counting same container multiple times
        aligned_containers = min(aligned_containers, total_containers)
        
        return aligned_containers / total_containers
    
    def suggest_alignment_fixes(
        self,
        containers: List[MVPContainer]
    ) -> List[Dict[str, any]]:
        """Suggest fixes for alignment issues."""
        suggestions = []
        alignment_info = self._analyze_alignment(containers)
        
        # Find containers that could be aligned
        y_coords = sorted(alignment_info.row_groups.keys())
        for i, y1 in enumerate(y_coords):
            for y2 in y_coords[i+1:]:
                if 0 < abs(y2 - y1) <= 4:
                    # Suggest aligning to the coordinate with more containers
                    count1 = len(alignment_info.row_groups[y1])
                    count2 = len(alignment_info.row_groups[y2])
                    
                    if count1 >= count2:
                        target_y = y1
                        containers_to_move = alignment_info.row_groups[y2]
                    else:
                        target_y = y2
                        containers_to_move = alignment_info.row_groups[y1]
                    
                    suggestions.append({
                        "type": "align_row",
                        "containers": containers_to_move,
                        "target_y": target_y,
                        "message": f"Align {containers_to_move} to Y={target_y}"
                    })
        
        return suggestions
    
    def is_grid_aligned(
        self,
        containers: List[MVPContainer]
    ) -> bool:
        """Quick check if all containers are properly grid aligned."""
        valid, score, _ = self.validate_alignment(containers)
        return valid and score >= 0.9