"""
Semantic Container models for Structure Analyzer Agent.

These models define the semantic roles and relationships
of content within presentation slides.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class ContainerRole(str, Enum):
    """Semantic roles for containers"""
    # Primary content
    KEY_TAKEAWAY = "key_takeaway"
    HEADLINE = "headline"
    MAIN_POINT = "main_point"
    
    # Supporting evidence
    SUPPORTING_EVIDENCE_CHART = "supporting_evidence_chart"
    SUPPORTING_EVIDENCE_TEXT = "supporting_evidence_text"
    SUPPORTING_EVIDENCE_IMAGE = "supporting_evidence_image"
    
    # Data and metrics
    KPI_METRIC = "kpi_metric"
    DATA_POINT = "data_point"
    STATISTIC = "statistic"
    
    # Visual elements
    IMAGE_CONCEPTUAL = "image_conceptual"
    IMAGE_PRODUCT_SHOT = "image_product_shot"
    DIAGRAM = "diagram"
    ICON = "icon"
    
    # Text elements
    QUOTE = "quote"
    DEFINITION = "definition"
    EXAMPLE = "example"
    LIST_ITEM = "list_item"
    
    # Metadata
    FOOTNOTE = "footnote"
    DISCLAIMER = "disclaimer"
    SOURCE_CITATION = "source_citation"
    
    # Interactive
    CALL_TO_ACTION = "call_to_action"
    QUESTION = "question"
    
    # Structural
    SECTION_HEADER = "section_header"
    TRANSITION = "transition"


class RelationshipType(str, Enum):
    """Types of relationships between containers"""
    SUPPORTS = "supports"  # B supports/proves A
    ELABORATES = "elaborates"  # B provides more detail about A
    CONTRASTS = "contrasts"  # B contrasts with A
    FOLLOWS = "follows"  # B follows A in sequence
    GROUPS_WITH = "groups_with"  # A and B are part of same group
    ANNOTATES = "annotates"  # B annotates/explains A
    RESPONDS_TO = "responds_to"  # B responds to A (e.g., answer to question)
    VISUALIZES = "visualizes"  # B visualizes data from A


class ContentImportance(str, Enum):
    """Importance levels for content"""
    CRITICAL = "critical"  # Must be prominently displayed
    HIGH = "high"  # Important, should be easily visible
    MEDIUM = "medium"  # Standard importance
    LOW = "low"  # Supporting information
    OPTIONAL = "optional"  # Can be omitted if space constrained


class ContainerRelationship(BaseModel):
    """Relationship between two containers"""
    from_container: str = Field(description="ID of the source container")
    to_container: str = Field(description="ID of the target container")
    relationship_type: RelationshipType
    strength: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Strength of the relationship"
    )
    bidirectional: bool = Field(
        default=False,
        description="Whether relationship goes both ways"
    )


class SemanticContainer(BaseModel):
    """
    A semantic container representing a logical content unit.
    
    This goes beyond visual representation to capture the
    meaning and purpose of content.
    """
    id: str = Field(description="Unique identifier for the container")
    role: ContainerRole = Field(description="Semantic role of the content")
    content: str = Field(description="The actual content or description")
    
    # Hierarchy and importance
    hierarchy_level: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Hierarchy level (1=highest)"
    )
    importance: ContentImportance = Field(
        default=ContentImportance.MEDIUM,
        description="Importance level for layout decisions"
    )
    
    # Visual hints
    visual_weight: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Suggested visual weight (0=minimal, 1=dominant)"
    )
    preferred_position: Optional[str] = Field(
        default=None,
        description="Preferred position hint (e.g., 'top', 'center', 'left')"
    )
    
    # Content characteristics
    content_length: Optional[int] = Field(
        default=None,
        description="Approximate content length in characters"
    )
    requires_visual: bool = Field(
        default=False,
        description="Whether this content requires visual support"
    )
    is_interactive: bool = Field(
        default=False,
        description="Whether this is interactive content"
    )
    
    # Metadata
    data_source: Optional[str] = Field(
        default=None,
        description="Source of the content/data"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Additional tags for categorization"
    )
    
    @field_validator('content_length', mode='after')
    @classmethod
    def set_content_length(cls, v, info):
        """Auto-calculate content length if not provided"""
        if v is None and info.data.get('content'):
            return len(info.data.get('content'))
        return v
    
    def get_layout_hints(self) -> Dict[str, Any]:
        """Get layout hints based on semantic properties"""
        hints = {
            "min_size": self._calculate_min_size(),
            "can_be_grouped": self._can_be_grouped(),
            "requires_emphasis": self.importance in [ContentImportance.CRITICAL, ContentImportance.HIGH],
            "can_be_minimized": self.importance in [ContentImportance.LOW, ContentImportance.OPTIONAL]
        }
        
        if self.preferred_position:
            hints["preferred_position"] = self.preferred_position
        
        return hints
    
    def _calculate_min_size(self) -> str:
        """Calculate minimum size based on content"""
        if self.role in [ContainerRole.HEADLINE, ContainerRole.KEY_TAKEAWAY]:
            return "large"
        elif self.role in [ContainerRole.FOOTNOTE, ContainerRole.DISCLAIMER]:
            return "small"
        elif self.content_length and self.content_length > 200:
            return "medium"
        else:
            return "flexible"
    
    def _can_be_grouped(self) -> bool:
        """Determine if this container can be grouped with others"""
        groupable_roles = [
            ContainerRole.LIST_ITEM,
            ContainerRole.DATA_POINT,
            ContainerRole.KPI_METRIC,
            ContainerRole.ICON
        ]
        return self.role in groupable_roles


class ContentFlow(str, Enum):
    """How content flows through the slide"""
    LINEAR = "linear"  # Sequential, top to bottom
    HIERARCHICAL = "hierarchical"  # Tree-like structure
    RADIAL = "radial"  # Central concept with radiating points
    COMPARATIVE = "comparative"  # Side-by-side comparison
    CYCLICAL = "cyclical"  # Circular flow
    MATRIX = "matrix"  # Grid-based organization


class ContainerManifest(BaseModel):
    """
    Complete manifest of semantic containers for a slide.
    
    This is the output of the Structure Analyzer Agent,
    providing a complete semantic understanding of slide content.
    """
    slide_id: str = Field(description="ID of the slide being analyzed")
    slide_type: str = Field(description="Type of slide")
    
    # Core content structure
    containers: List[SemanticContainer] = Field(
        description="All semantic containers in the slide"
    )
    relationships: List[ContainerRelationship] = Field(
        default_factory=list,
        description="Relationships between containers"
    )
    
    # Content analysis
    primary_message: str = Field(
        description="The main message of the slide"
    )
    content_flow: ContentFlow = Field(
        description="How content flows through the slide"
    )
    
    # Layout hints
    visual_hierarchy: List[str] = Field(
        description="Container IDs in order of visual importance"
    )
    groupings: List[List[str]] = Field(
        default_factory=list,
        description="Containers that should be grouped together"
    )
    
    # Metrics
    content_density: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall content density (0=sparse, 1=dense)"
    )
    complexity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Content complexity (0=simple, 1=complex)"
    )
    
    # Additional guidance
    layout_constraints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Specific constraints for layout"
    )
    accessibility_notes: Optional[List[str]] = Field(
        default=None,
        description="Accessibility considerations"
    )
    
    def get_container_by_role(self, role: ContainerRole) -> List[SemanticContainer]:
        """Get all containers with a specific role"""
        return [c for c in self.containers if c.role == role]
    
    def get_critical_containers(self) -> List[SemanticContainer]:
        """Get containers marked as critical importance"""
        return [c for c in self.containers if c.importance == ContentImportance.CRITICAL]
    
    def get_container_relationships(self, container_id: str) -> List[ContainerRelationship]:
        """Get all relationships involving a specific container"""
        return [
            r for r in self.relationships
            if r.from_container == container_id or r.to_container == container_id
        ]
    
    def get_hierarchy_tree(self) -> Dict[int, List[SemanticContainer]]:
        """Get containers organized by hierarchy level"""
        tree = {}
        for container in self.containers:
            level = container.hierarchy_level
            if level not in tree:
                tree[level] = []
            tree[level].append(container)
        return dict(sorted(tree.items()))
    
    def calculate_balance_score(self) -> float:
        """Calculate visual balance score based on container distribution"""
        if not self.containers:
            return 1.0
        
        # Calculate weight distribution
        total_weight = sum(c.visual_weight for c in self.containers)
        if total_weight == 0:
            return 1.0
        
        # Calculate variance in weights
        avg_weight = total_weight / len(self.containers)
        variance = sum((c.visual_weight - avg_weight) ** 2 for c in self.containers)
        
        # Lower variance = better balance
        max_variance = len(self.containers) * (1.0 ** 2)  # Worst case
        balance = 1.0 - (variance / max_variance) if max_variance > 0 else 1.0
        
        return min(1.0, max(0.0, balance))
    
    @model_validator(mode='after')
    def ensure_visual_hierarchy(self):
        """Ensure visual hierarchy includes all containers"""
        if not self.visual_hierarchy and self.containers:
            # Auto-generate based on importance and hierarchy
            sorted_containers = sorted(
                self.containers,
                key=lambda c: (
                    -c.importance.value if hasattr(c.importance, 'value') else 0,
                    c.hierarchy_level,
                    -c.visual_weight
                )
            )
            self.visual_hierarchy = [c.id for c in sorted_containers]
        return self
    
    @field_validator('content_density', mode='after')
    @classmethod
    def calculate_content_density(cls, v, info):
        """Auto-calculate content density if not provided"""
        if v == 0.0 and info.data.get('containers'):
            containers = info.data.get('containers')
            if not containers:
                return 0.0
            
            # Calculate based on content length and container count
            total_content = sum(c.content_length or 0 for c in containers)
            container_count = len(containers)
            
            # Normalize (rough heuristic)
            density = min(1.0, (total_content / 500 + container_count / 10) / 2)
            return density
        return v


class StructureAnalysis(BaseModel):
    """
    Complete structure analysis output from the Structure Analyzer Agent.
    
    This includes the manifest plus analysis metadata.
    """
    manifest: ContainerManifest
    analysis_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the analysis"
    )
    alternative_structures: Optional[List[ContentFlow]] = Field(
        default=None,
        description="Alternative structure suggestions"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings or issues found"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )