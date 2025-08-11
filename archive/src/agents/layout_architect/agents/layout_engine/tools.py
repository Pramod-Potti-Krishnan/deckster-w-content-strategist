"""
Tools for Layout Engine Agent - Pattern generation, positioning, and validation.

These tools provide sophisticated layout capabilities including
pattern suggestions, precise positioning, and comprehensive validation.
"""

from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field, validator
from pydantic_ai import Tool
import math

from ...model_types.design_tokens import GridZone, LayoutTemplate
from ...model_types.semantic_containers import SemanticContainer, ContainerManifest
from ...model_types.layout_state import ValidationIssue, ValidationReport
from ... import models as mvp_models
MVPContainer = mvp_models.MVPContainer
GridPosition = mvp_models.GridPosition
ContainerContent = mvp_models.ContainerContent


class LayoutPatternInput(BaseModel):
    """Input for layout pattern generation"""
    container_count: int = Field(description="Number of containers to layout")
    content_flow: str = Field(description="Content flow type (linear, hierarchical, etc.)")
    visual_emphasis: float = Field(
        ge=0, le=1,
        description="Visual vs text emphasis"
    )
    container_roles: List[str] = Field(
        description="Roles of containers to consider"
    )


class LayoutPatternOutput(BaseModel):
    """Output from layout pattern generation"""
    pattern_name: str = Field(description="Name of the recommended pattern")
    pattern_description: str = Field(description="Description of the pattern")
    layout_zones: Dict[str, Dict[str, int]] = Field(
        description="Suggested zones for the pattern"
    )
    rationale: str = Field(description="Why this pattern was chosen")
    alternatives: List[str] = Field(
        description="Alternative patterns that could work"
    )


class LayoutPatternGenerator:
    """Generate layout patterns based on content characteristics"""
    
    # Pattern definitions
    PATTERNS = {
        "golden_ratio": {
            "description": "Uses golden ratio for visual harmony",
            "best_for": ["visual_emphasis", "2-3 containers"],
            "zones": {
                "primary": {"ratio": 0.618, "position": "left"},
                "secondary": {"ratio": 0.382, "position": "right"}
            }
        },
        "f_pattern": {
            "description": "Follows natural F-shaped reading pattern",
            "best_for": ["text_heavy", "hierarchical"],
            "zones": {
                "header": {"height": 0.2, "position": "top"},
                "main": {"height": 0.6, "position": "middle"},
                "sidebar": {"width": 0.3, "position": "right"}
            }
        },
        "z_pattern": {
            "description": "Z-shaped visual flow for balanced content",
            "best_for": ["balanced", "4 containers"],
            "zones": {
                "top_left": {"quadrant": 1},
                "top_right": {"quadrant": 2},
                "bottom_left": {"quadrant": 3},
                "bottom_right": {"quadrant": 4}
            }
        },
        "rule_of_thirds": {
            "description": "Divides space into thirds for balance",
            "best_for": ["visual_heavy", "3 containers"],
            "zones": {
                "left": {"column": 1},
                "center": {"column": 2},
                "right": {"column": 3}
            }
        },
        "symmetrical": {
            "description": "Perfect symmetry for formal presentations",
            "best_for": ["formal", "even containers"],
            "zones": {
                "center": {"align": "center", "width": 0.8}
            }
        },
        "asymmetrical": {
            "description": "Dynamic asymmetry for modern feel",
            "best_for": ["modern", "visual_emphasis"],
            "zones": {
                "focal": {"size": "large", "offset": True},
                "supporting": {"size": "small", "balance": True}
            }
        }
    }
    
    def generate_pattern(self, input_data: LayoutPatternInput) -> LayoutPatternOutput:
        """Generate appropriate layout pattern"""
        # Score patterns
        scores = {}
        for pattern_name, pattern_info in self.PATTERNS.items():
            score = self._score_pattern(pattern_info, input_data)
            scores[pattern_name] = score
        
        # Select best pattern
        best_pattern = max(scores, key=scores.get)
        pattern_info = self.PATTERNS[best_pattern]
        
        # Generate zones based on pattern
        zones = self._generate_zones(best_pattern, input_data)
        
        # Generate rationale
        rationale = self._generate_rationale(best_pattern, input_data, scores[best_pattern])
        
        # Get alternatives
        sorted_patterns = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [p[0] for p in sorted_patterns[1:4]]  # Top 3 alternatives
        
        return LayoutPatternOutput(
            pattern_name=best_pattern,
            pattern_description=pattern_info["description"],
            layout_zones=zones,
            rationale=rationale,
            alternatives=alternatives
        )
    
    def _score_pattern(self, pattern_info: Dict, input_data: LayoutPatternInput) -> float:
        """Score a pattern based on input characteristics"""
        score = 0.0
        
        # Check container count compatibility
        if input_data.container_count <= 3 and "2-3 containers" in str(pattern_info.get("best_for", [])):
            score += 2.0
        elif input_data.container_count == 4 and "4 containers" in str(pattern_info.get("best_for", [])):
            score += 2.0
        
        # Check visual emphasis
        if input_data.visual_emphasis > 0.7 and "visual" in str(pattern_info.get("best_for", [])):
            score += 1.5
        elif input_data.visual_emphasis < 0.3 and "text" in str(pattern_info.get("best_for", [])):
            score += 1.5
        
        # Check content flow
        if input_data.content_flow in str(pattern_info.get("best_for", [])):
            score += 1.0
        
        return score
    
    def _generate_zones(self, pattern_name: str, input_data: LayoutPatternInput) -> Dict[str, Dict[str, int]]:
        """Generate specific zones for the pattern"""
        # Grid dimensions
        GRID_WIDTH = 160
        GRID_HEIGHT = 90
        MARGIN = 8
        
        work_width = GRID_WIDTH - (2 * MARGIN)
        work_height = GRID_HEIGHT - (2 * MARGIN)
        
        zones = {}
        
        if pattern_name == "golden_ratio":
            golden = 0.618
            zones["primary"] = {
                "leftInset": MARGIN,
                "topInset": MARGIN,
                "width": int(work_width * golden),
                "height": work_height
            }
            zones["secondary"] = {
                "leftInset": MARGIN + zones["primary"]["width"] + 4,
                "topInset": MARGIN,
                "width": work_width - zones["primary"]["width"] - 4,
                "height": work_height
            }
        
        elif pattern_name == "rule_of_thirds":
            third_width = work_width // 3
            for i, zone_name in enumerate(["left", "center", "right"]):
                zones[zone_name] = {
                    "leftInset": MARGIN + (i * (third_width + 2)),
                    "topInset": MARGIN,
                    "width": third_width - 2 if i < 2 else third_width,
                    "height": work_height
                }
        
        elif pattern_name == "z_pattern":
            half_width = (work_width - 4) // 2
            half_height = (work_height - 4) // 2
            zones["top_left"] = {
                "leftInset": MARGIN,
                "topInset": MARGIN,
                "width": half_width,
                "height": half_height
            }
            zones["top_right"] = {
                "leftInset": MARGIN + half_width + 4,
                "topInset": MARGIN,
                "width": half_width,
                "height": half_height
            }
            zones["bottom_left"] = {
                "leftInset": MARGIN,
                "topInset": MARGIN + half_height + 4,
                "width": half_width,
                "height": half_height
            }
            zones["bottom_right"] = {
                "leftInset": MARGIN + half_width + 4,
                "topInset": MARGIN + half_height + 4,
                "width": half_width,
                "height": half_height
            }
        
        else:
            # Default centered layout
            zones["main"] = {
                "leftInset": MARGIN,
                "topInset": MARGIN,
                "width": work_width,
                "height": work_height
            }
        
        return zones
    
    def _generate_rationale(self, pattern: str, input_data: LayoutPatternInput, score: float) -> str:
        """Generate explanation for pattern choice"""
        rationale_parts = []
        
        if pattern == "golden_ratio":
            rationale_parts.append("Golden ratio creates natural visual harmony")
        elif pattern == "rule_of_thirds":
            rationale_parts.append("Rule of thirds provides balanced composition")
        elif pattern == "z_pattern":
            rationale_parts.append("Z-pattern follows natural eye movement")
        
        if input_data.visual_emphasis > 0.7:
            rationale_parts.append("High visual emphasis requires prominent image placement")
        elif input_data.visual_emphasis < 0.3:
            rationale_parts.append("Text-heavy content benefits from clear reading hierarchy")
        
        rationale_parts.append(f"Pattern scored {score:.1f} for your content characteristics")
        
        return ". ".join(rationale_parts)


class GridPositionInput(BaseModel):
    """Input for grid position calculation"""
    containers: List[Dict[str, Any]] = Field(
        description="Containers with semantic information"
    )
    layout_zones: Dict[str, Dict[str, int]] = Field(
        description="Available zones from pattern"
    )
    groupings: List[List[str]] = Field(
        default_factory=list,
        description="Containers that should be grouped"
    )
    alignment_rules: Dict[str, str] = Field(
        default_factory=dict,
        description="Specific alignment requirements"
    )


class GridPositionOutput(BaseModel):
    """Output from grid position calculation"""
    positions: Dict[str, Dict[str, int]] = Field(
        description="Container ID to grid position mapping"
    )
    space_utilization: float = Field(
        description="Percentage of available space used"
    )
    alignment_score: float = Field(
        description="How well positions align to grid"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Any positioning warnings"
    )


class GridPositionCalculator:
    """Calculate precise grid positions for containers"""
    
    GRID_WIDTH = 160
    GRID_HEIGHT = 90
    MARGIN = 8
    GUTTER = 4
    
    def calculate_positions(self, input_data: GridPositionInput) -> GridPositionOutput:
        """Calculate optimal positions for all containers"""
        containers = input_data.containers
        zones = input_data.layout_zones
        groupings = input_data.groupings
        
        positions = {}
        warnings = []
        used_area = 0
        
        # Sort containers by visual priority
        sorted_containers = sorted(
            containers,
            key=lambda c: (
                -c.get('importance_score', 0),
                c.get('hierarchy_level', 3),
                -c.get('visual_weight', 0.5)
            )
        )
        
        # Place containers in zones
        zone_assignments = self._assign_to_zones(sorted_containers, zones, groupings)
        
        # Calculate specific positions within zones
        for container_id, zone_name in zone_assignments.items():
            if zone_name in zones:
                zone = zones[zone_name]
                position = self._position_in_zone(
                    container_id,
                    zone,
                    zone_assignments,
                    containers
                )
                positions[container_id] = position
                
                # Calculate used area
                used_area += position["width"] * position["height"]
            else:
                warnings.append(f"Container {container_id} could not be placed")
        
        # Calculate metrics
        total_area = (self.GRID_WIDTH - 2 * self.MARGIN) * (self.GRID_HEIGHT - 2 * self.MARGIN)
        space_utilization = used_area / total_area if total_area > 0 else 0
        alignment_score = self._calculate_alignment_score(positions)
        
        return GridPositionOutput(
            positions=positions,
            space_utilization=space_utilization,
            alignment_score=alignment_score,
            warnings=warnings
        )
    
    def _assign_to_zones(
        self,
        containers: List[Dict],
        zones: Dict[str, Dict],
        groupings: List[List[str]]
    ) -> Dict[str, str]:
        """Assign containers to zones"""
        assignments = {}
        zone_list = list(zones.keys())
        zone_index = 0
        
        # Handle grouped containers first
        for group in groupings:
            if zone_index < len(zone_list):
                zone_name = zone_list[zone_index]
                for container_id in group:
                    assignments[container_id] = zone_name
                zone_index += 1
        
        # Assign remaining containers
        for container in containers:
            container_id = container.get('id')
            if container_id and container_id not in assignments:
                if zone_index < len(zone_list):
                    assignments[container_id] = zone_list[zone_index]
                    zone_index += 1
                else:
                    # Reuse zones if necessary
                    assignments[container_id] = zone_list[0]
        
        return assignments
    
    def _position_in_zone(
        self,
        container_id: str,
        zone: Dict[str, int],
        assignments: Dict[str, str],
        containers: List[Dict]
    ) -> Dict[str, int]:
        """Calculate position within a zone"""
        # Count containers in same zone
        zone_containers = [
            cid for cid, z in assignments.items()
            if z == assignments[container_id]
        ]
        
        if len(zone_containers) == 1:
            # Single container fills zone
            return {
                "leftInset": zone["leftInset"],
                "topInset": zone["topInset"],
                "width": zone["width"],
                "height": zone["height"]
            }
        else:
            # Multiple containers - divide zone
            index = zone_containers.index(container_id)
            
            # Vertical stacking by default
            container_height = (zone["height"] - (len(zone_containers) - 1) * self.GUTTER) // len(zone_containers)
            
            return {
                "leftInset": zone["leftInset"],
                "topInset": zone["topInset"] + index * (container_height + self.GUTTER),
                "width": zone["width"],
                "height": container_height
            }
    
    def _calculate_alignment_score(self, positions: Dict[str, Dict[str, int]]) -> float:
        """Calculate how well positions align to grid"""
        if not positions:
            return 1.0
        
        misalignments = 0
        total_checks = 0
        
        for pos in positions.values():
            # Check if all values are integers (already aligned)
            for value in pos.values():
                total_checks += 1
                if not isinstance(value, int) or value % 1 != 0:
                    misalignments += 1
        
        return 1.0 - (misalignments / total_checks) if total_checks > 0 else 1.0


class LayoutValidationInput(BaseModel):
    """Input for layout validation"""
    layout: Dict[str, Any] = Field(description="Layout to validate")
    theme: Dict[str, Any] = Field(description="Theme constraints")
    requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Specific requirements to validate"
    )


class LayoutValidator:
    """Comprehensive layout validation"""
    
    def validate(self, input_data: LayoutValidationInput) -> ValidationReport:
        """Validate layout against all requirements"""
        layout = input_data.layout
        theme = input_data.theme
        requirements = input_data.requirements
        
        issues = []
        
        # Extract layout data
        containers = layout.get('containers', [])
        white_space_ratio = layout.get('white_space_ratio', 0)
        
        # Validate white space
        ws_min = requirements.get('white_space_min', 0.3)
        ws_max = requirements.get('white_space_max', 0.5)
        
        if white_space_ratio < ws_min:
            issues.append(ValidationIssue(
                issue_type="white_space_low",
                severity="error",
                message=f"White space {white_space_ratio:.2f} below minimum {ws_min}",
                suggestion="Increase spacing or reduce container sizes"
            ))
        elif white_space_ratio > ws_max:
            issues.append(ValidationIssue(
                issue_type="white_space_high",
                severity="warning",
                message=f"White space {white_space_ratio:.2f} above maximum {ws_max}",
                suggestion="Reduce spacing or increase container sizes"
            ))
        
        # Validate margins
        margin_issues = self._validate_margins(containers, requirements.get('margin', 8))
        issues.extend(margin_issues)
        
        # Validate overlaps
        overlap_issues = self._validate_overlaps(containers)
        issues.extend(overlap_issues)
        
        # Validate alignment
        alignment_issues = self._validate_alignment(containers)
        issues.extend(alignment_issues)
        
        # Calculate scores
        alignment_score = 1.0 - (len(alignment_issues) / max(len(containers), 1))
        balance_score = self._calculate_balance_score(containers)
        
        # Determine validity
        has_errors = any(i.severity == "error" for i in issues)
        
        return ValidationReport(
            is_valid=not has_errors,
            white_space_ratio=white_space_ratio,
            alignment_score=alignment_score,
            balance_score=balance_score,
            issues=issues
        )
    
    def _validate_margins(self, containers: List[Dict], min_margin: int) -> List[ValidationIssue]:
        """Validate margin constraints"""
        issues = []
        
        for container in containers:
            pos = container.get('position', {})
            if not pos:
                continue
            
            # Check margins
            if pos.get('leftInset', 0) < min_margin:
                issues.append(ValidationIssue(
                    issue_type="margin_violation",
                    severity="error",
                    message=f"Left margin {pos.get('leftInset')} below minimum {min_margin}",
                    affected_containers=[container.get('id', 'unknown')]
                ))
            
            if pos.get('topInset', 0) < min_margin:
                issues.append(ValidationIssue(
                    issue_type="margin_violation",
                    severity="error",
                    message=f"Top margin {pos.get('topInset')} below minimum {min_margin}",
                    affected_containers=[container.get('id', 'unknown')]
                ))
        
        return issues
    
    def _validate_overlaps(self, containers: List[Dict]) -> List[ValidationIssue]:
        """Check for container overlaps"""
        issues = []
        
        for i, c1 in enumerate(containers):
            pos1 = c1.get('position', {})
            if not pos1:
                continue
            
            for c2 in containers[i+1:]:
                pos2 = c2.get('position', {})
                if not pos2:
                    continue
                
                if self._rectangles_overlap(pos1, pos2):
                    issues.append(ValidationIssue(
                        issue_type="container_overlap",
                        severity="error",
                        message="Containers overlap",
                        affected_containers=[
                            c1.get('id', 'unknown'),
                            c2.get('id', 'unknown')
                        ]
                    ))
        
        return issues
    
    def _validate_alignment(self, containers: List[Dict]) -> List[ValidationIssue]:
        """Check grid alignment"""
        issues = []
        
        for container in containers:
            pos = container.get('position', {})
            if not pos:
                continue
            
            # Check if positions are integers
            for key, value in pos.items():
                if not isinstance(value, int):
                    issues.append(ValidationIssue(
                        issue_type="alignment_error",
                        severity="warning",
                        message=f"{key} not aligned to grid: {value}",
                        affected_containers=[container.get('id', 'unknown')]
                    ))
        
        return issues
    
    def _rectangles_overlap(self, pos1: Dict, pos2: Dict) -> bool:
        """Check if two rectangles overlap"""
        return not (
            pos1['leftInset'] + pos1['width'] <= pos2['leftInset'] or
            pos2['leftInset'] + pos2['width'] <= pos1['leftInset'] or
            pos1['topInset'] + pos1['height'] <= pos2['topInset'] or
            pos2['topInset'] + pos2['height'] <= pos1['topInset']
        )
    
    def _calculate_balance_score(self, containers: List[Dict]) -> float:
        """Calculate visual balance score"""
        if not containers:
            return 1.0
        
        # Calculate center of mass
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for container in containers:
            pos = container.get('position', {})
            if not pos:
                continue
            
            weight = container.get('visual_weight', 0.5)
            center_x = pos.get('leftInset', 0) + pos.get('width', 0) / 2
            center_y = pos.get('topInset', 0) + pos.get('height', 0) / 2
            
            weighted_x += center_x * weight
            weighted_y += center_y * weight
            total_weight += weight
        
        if total_weight == 0:
            return 1.0
        
        # Calculate center of mass
        com_x = weighted_x / total_weight
        com_y = weighted_y / total_weight
        
        # Calculate distance from ideal center
        ideal_x = 80  # Center of 160 grid
        ideal_y = 45  # Center of 90 grid
        
        distance = math.sqrt((com_x - ideal_x)**2 + (com_y - ideal_y)**2)
        max_distance = math.sqrt(80**2 + 45**2)  # Maximum possible distance
        
        # Convert to score (closer to center = higher score)
        balance = 1.0 - (distance / max_distance)
        
        return max(0.0, min(1.0, balance))


class VisualBalanceInput(BaseModel):
    """Input for visual balance scoring"""
    containers: List[Dict[str, Any]] = Field(description="Positioned containers")
    visual_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Visual weight overrides"
    )


class VisualBalanceOutput(BaseModel):
    """Output from visual balance scoring"""
    balance_score: float = Field(description="Overall balance score (0-1)")
    center_of_mass: Tuple[float, float] = Field(description="Visual center of mass")
    quadrant_distribution: Dict[str, float] = Field(
        description="Weight distribution by quadrant"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Balance improvement suggestions"
    )


class VisualBalanceScorer:
    """Analyze and score visual balance of layouts"""
    
    def score_balance(self, input_data: VisualBalanceInput) -> VisualBalanceOutput:
        """Score visual balance of a layout"""
        containers = input_data.containers
        weight_overrides = input_data.visual_weights
        
        # Calculate visual weights
        weights = {}
        positions = {}
        
        for container in containers:
            container_id = container.get('id')
            if not container_id:
                continue
            
            # Get weight (override or calculated)
            if container_id in weight_overrides:
                weight = weight_overrides[container_id]
            else:
                weight = self._calculate_visual_weight(container)
            
            weights[container_id] = weight
            positions[container_id] = container.get('position', {})
        
        # Calculate center of mass
        com_x, com_y = self._calculate_center_of_mass(weights, positions)
        
        # Calculate quadrant distribution
        quadrant_dist = self._calculate_quadrant_distribution(weights, positions)
        
        # Calculate balance score
        balance_score = self._calculate_balance_score(com_x, com_y, quadrant_dist)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            com_x, com_y, quadrant_dist, balance_score
        )
        
        return VisualBalanceOutput(
            balance_score=balance_score,
            center_of_mass=(com_x, com_y),
            quadrant_distribution=quadrant_dist,
            recommendations=recommendations
        )
    
    def _calculate_visual_weight(self, container: Dict) -> float:
        """Calculate visual weight of a container"""
        # Base weight from importance
        importance_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3,
            'optional': 0.1
        }
        base_weight = importance_weights.get(container.get('importance', 'medium'), 0.5)
        
        # Adjust for size
        pos = container.get('position', {})
        if pos:
            area = pos.get('width', 0) * pos.get('height', 0)
            size_factor = min(area / 5000, 1.0)  # Normalize to max expected area
            base_weight *= (0.5 + 0.5 * size_factor)
        
        # Adjust for content type
        if container.get('role') in ['image', 'chart', 'diagram']:
            base_weight *= 1.2  # Visuals have more weight
        
        return min(1.0, base_weight)
    
    def _calculate_center_of_mass(
        self,
        weights: Dict[str, float],
        positions: Dict[str, Dict]
    ) -> Tuple[float, float]:
        """Calculate the visual center of mass"""
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for container_id, weight in weights.items():
            pos = positions.get(container_id, {})
            if not pos:
                continue
            
            # Calculate center point
            center_x = pos.get('leftInset', 0) + pos.get('width', 0) / 2
            center_y = pos.get('topInset', 0) + pos.get('height', 0) / 2
            
            weighted_x += center_x * weight
            weighted_y += center_y * weight
            total_weight += weight
        
        if total_weight == 0:
            return (80, 45)  # Default to center
        
        return (weighted_x / total_weight, weighted_y / total_weight)
    
    def _calculate_quadrant_distribution(
        self,
        weights: Dict[str, float],
        positions: Dict[str, Dict]
    ) -> Dict[str, float]:
        """Calculate weight distribution by quadrant"""
        quadrants = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
        
        for container_id, weight in weights.items():
            pos = positions.get(container_id, {})
            if not pos:
                continue
            
            # Determine quadrant
            center_x = pos.get('leftInset', 0) + pos.get('width', 0) / 2
            center_y = pos.get('topInset', 0) + pos.get('height', 0) / 2
            
            if center_x < 80:
                if center_y < 45:
                    quadrants["Q1"] += weight
                else:
                    quadrants["Q3"] += weight
            else:
                if center_y < 45:
                    quadrants["Q2"] += weight
                else:
                    quadrants["Q4"] += weight
        
        # Normalize
        total = sum(quadrants.values())
        if total > 0:
            for q in quadrants:
                quadrants[q] /= total
        
        return quadrants
    
    def _calculate_balance_score(
        self,
        com_x: float,
        com_y: float,
        quadrant_dist: Dict[str, float]
    ) -> float:
        """Calculate overall balance score"""
        # Distance from center score
        center_distance = math.sqrt((com_x - 80)**2 + (com_y - 45)**2)
        max_distance = math.sqrt(80**2 + 45**2)
        center_score = 1.0 - (center_distance / max_distance)
        
        # Quadrant distribution score
        ideal_dist = 0.25  # Perfect balance
        quad_variance = sum((v - ideal_dist)**2 for v in quadrant_dist.values())
        max_variance = 0.75  # Worst case: all weight in one quadrant
        quad_score = 1.0 - (quad_variance / max_variance)
        
        # Combined score
        return (center_score * 0.6 + quad_score * 0.4)
    
    def _generate_recommendations(
        self,
        com_x: float,
        com_y: float,
        quadrant_dist: Dict[str, float],
        balance_score: float
    ) -> List[str]:
        """Generate balance improvement recommendations"""
        recommendations = []
        
        if balance_score >= 0.8:
            recommendations.append("Layout has excellent visual balance")
            return recommendations
        
        # Center of mass recommendations
        if com_x < 70:
            recommendations.append("Consider moving visual weight rightward")
        elif com_x > 90:
            recommendations.append("Consider moving visual weight leftward")
        
        if com_y < 35:
            recommendations.append("Consider moving visual weight downward")
        elif com_y > 55:
            recommendations.append("Consider moving visual weight upward")
        
        # Quadrant recommendations
        heavy_quadrants = [q for q, w in quadrant_dist.items() if w > 0.35]
        light_quadrants = [q for q, w in quadrant_dist.items() if w < 0.15]
        
        if heavy_quadrants:
            recommendations.append(f"Redistribute weight from {', '.join(heavy_quadrants)}")
        if light_quadrants:
            recommendations.append(f"Add visual elements to {', '.join(light_quadrants)}")
        
        return recommendations


# Create PydanticAI tools
layout_pattern_tool = Tool(
    function=LayoutPatternGenerator().generate_pattern,
    name="generate_layout_pattern",
    description="Generate appropriate layout pattern based on content"
)

grid_position_tool = Tool(
    function=GridPositionCalculator().calculate_positions,
    name="calculate_grid_positions",
    description="Calculate precise grid positions for containers"
)

layout_validator_tool = Tool(
    function=LayoutValidator().validate,
    name="validate_layout",
    description="Comprehensively validate a layout proposal"
)

visual_balance_tool = Tool(
    function=VisualBalanceScorer().score_balance,
    name="score_visual_balance",
    description="Analyze and score visual balance of layout"
)