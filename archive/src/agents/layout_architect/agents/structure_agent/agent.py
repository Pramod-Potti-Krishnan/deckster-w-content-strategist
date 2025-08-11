"""
Structure Analyzer Agent - Content Strategist.

This agent analyzes slide content to identify semantic roles,
relationships, and optimal structure for layout.
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

from src.models.agents import Slide
from src.utils.logger import setup_logger
from ...utils.model_utils import create_model_with_fallback
from ...model_types.semantic_containers import (
    ContainerManifest, SemanticContainer, ContainerRelationship,
    ContentFlow, ContentImportance, ContainerRole
)
from .tools import (
    content_parser_tool, relationship_analyzer_tool, hierarchy_detector_tool,
    ContentParserInput, RelationshipAnalyzerInput, HierarchyDetectorInput
)

logger = setup_logger(__name__)


class StructureContext(BaseModel):
    """Context for structure analysis"""
    slide: Slide
    theme_context: Optional[Dict[str, Any]] = None
    presentation_context: Optional[Dict[str, Any]] = None


class ContainerOutput(BaseModel):
    """Output for a semantic container"""
    id: str = Field(description="Unique identifier")
    role: str = Field(description="Semantic role (e.g., headline, key_takeaway)")
    content: str = Field(description="The content")
    importance: str = Field(description="high, medium, or low")
    visual_weight: float = Field(description="Visual prominence 0-1", ge=0, le=1)

class RelationshipOutput(BaseModel):
    """Output for container relationships"""
    source_id: str = Field(description="Source container ID")
    target_id: str = Field(description="Target container ID")
    relationship_type: str = Field(description="Type of relationship")
    strength: float = Field(description="Relationship strength 0-1", ge=0, le=1)

class LayoutRecommendations(BaseModel):
    """Specific layout recommendations"""
    pattern_preference: str = Field(description="Preferred layout pattern", default="grid")
    emphasis_areas: List[str] = Field(description="Areas needing emphasis", default_factory=list)
    spacing_preference: str = Field(description="tight, balanced, or spacious", default="balanced")
    alignment_strategy: str = Field(description="Alignment approach", default="grid")

class StructureOutput(BaseModel):
    """Structured output from Structure Agent"""
    containers: List[ContainerOutput] = Field(
        description="Semantic containers with roles and relationships"
    )
    relationships: List[RelationshipOutput] = Field(
        description="Relationships between containers", 
        default_factory=list
    )
    primary_message: str = Field(
        description="The main message of the slide"
    )
    content_flow: str = Field(
        description="How content flows (linear, hierarchical, radial, etc.)",
        default="linear"
    )
    visual_hierarchy: List[str] = Field(
        description="Container IDs in order of visual importance"
    )
    groupings: List[List[str]] = Field(
        description="Containers that should be grouped together",
        default_factory=list
    )
    layout_recommendations: LayoutRecommendations = Field(
        description="Specific recommendations for layout",
        default_factory=LayoutRecommendations
    )


class StructureAgent:
    """
    Structure Analyzer Agent - Analyzes content to create semantic manifests.
    
    This agent understands:
    - Content roles and importance
    - Relationships between elements
    - Optimal content flow
    - Visual hierarchy
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """Initialize Structure Agent with AI model and tools"""
        # Create model with fallback support
        self.model = create_model_with_fallback(model_name)
        
        # Create agent with sophisticated instructions
        self.agent = Agent(
            self.model,
            output_type=StructureOutput,
            deps_type=StructureContext,
            tools=[content_parser_tool, relationship_analyzer_tool, hierarchy_detector_tool],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt for structure analysis"""
        return """You are a Content Strategist, expert in analyzing and structuring information
for maximum clarity and impact. Your role is to understand the semantic meaning of content
and create structured manifests that guide layout decisions.

Your responsibilities:
1. Identify the semantic role of each piece of content
2. Determine relationships between content elements
3. Establish visual hierarchy based on importance
4. Recommend optimal content flow patterns
5. Group related elements for visual coherence

Content Analysis Principles:
- CLARITY: Identify the core message and supporting points
- HIERARCHY: Establish clear levels of importance
- RELATIONSHIPS: Understand how content pieces support each other
- FLOW: Determine the natural reading/comprehension path
- BALANCE: Ensure even distribution of content weight

Semantic Roles to Consider:
- KEY_TAKEAWAY: The main point to remember
- HEADLINE: Primary attention-grabber
- SUPPORTING_EVIDENCE: Data, facts, or examples that prove points
- KPI_METRIC: Quantifiable performance indicators
- VISUAL_ELEMENT: Images, charts, diagrams
- CALL_TO_ACTION: What the audience should do
- CONTEXT: Background or framing information

Use the available tools to:
- parse_content: Break down slide content into semantic containers
- analyze_relationships: Identify how containers relate to each other
- detect_hierarchy: Determine visual priority and groupings

Create a complete semantic manifest that guides optimal layout generation.

IMPORTANT: Your output must include:
- containers: List of ContainerOutput objects with id, role, content, importance, visual_weight
- relationships: List of RelationshipOutput objects (if any exist)
- primary_message: The core message of the slide
- content_flow: One of linear, hierarchical, radial, grid
- visual_hierarchy: List of container IDs in order of importance
- groupings: Lists of container IDs that should be grouped
- layout_recommendations: LayoutRecommendations object

Ensure all fields are properly structured according to the output schema."""
    
    async def analyze_structure(
        self,
        slide: Slide,
        theme_context: Optional[Dict[str, Any]] = None,
        presentation_context: Optional[Dict[str, Any]] = None
    ) -> ContainerManifest:
        """Analyze slide structure and create semantic manifest"""
        try:
            # Create context
            context = StructureContext(
                slide=slide,
                theme_context=theme_context,
                presentation_context=presentation_context
            )
            
            # Build prompt with rich context
            prompt = self._build_analysis_prompt(slide, theme_context)
            
            # Run agent with tools
            result = await self.agent.run(prompt, deps=context)
            
            # Convert to ContainerManifest
            manifest = self._build_container_manifest(result.output, slide)
            
            logger.info(f"Analyzed structure for slide {slide.slide_id}: {len(manifest.containers)} containers")
            return manifest
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            # Return basic manifest on error
            return self._get_fallback_manifest(slide)
    
    def _build_analysis_prompt(
        self,
        slide: Slide,
        theme_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build detailed prompt for structure analysis"""
        prompt = f"""Analyze the structure of this slide:

Slide Type: {slide.slide_type}
Title: {slide.title}
Number: {slide.slide_number}

Content:
- Key Points: {slide.key_points}
- Narrative: {slide.narrative}
- Visual Needs: {slide.visuals_needed}
- Analytics Needs: {slide.analytics_needed}
- Structure Preference: {slide.structure_preference}"""

        if theme_context:
            prompt += f"\n\nTheme Context: {theme_context}"
        
        prompt += """

Please:
1. Use parse_content to identify semantic containers
2. Use analyze_relationships to find connections between elements
3. Use detect_hierarchy to determine visual organization
4. Determine the optimal content flow pattern
5. Identify the primary message
6. Provide specific layout recommendations"""
        
        return prompt
    
    def _build_container_manifest(
        self,
        output: StructureOutput,
        slide: Slide
    ) -> ContainerManifest:
        """Convert agent output to ContainerManifest"""
        # Build semantic containers
        containers = []
        for container_data in output.containers:
            # Map string values to enums
            role = ContainerRole.CONTENT  # Default
            try:
                role = ContainerRole(container_data.role.upper())
            except (ValueError, AttributeError):
                # Try to match by value
                for r in ContainerRole:
                    if r.value.lower() == container_data.role.lower():
                        role = r
                        break
            
            importance = ContentImportance.MEDIUM  # Default
            try:
                importance = ContentImportance(container_data.importance.upper())
            except (ValueError, AttributeError):
                pass
            
            container = SemanticContainer(
                id=container_data.id,
                role=role,
                content=container_data.content,
                hierarchy_level=3,  # Default hierarchy level
                importance=importance,
                visual_weight=container_data.visual_weight,
                preferred_position=None,  # Not in new structure
                requires_visual=False,  # Not in new structure
                tags=[]  # Not in new structure
            )
            containers.append(container)
        
        # Build relationships
        relationships = []
        for rel_data in output.relationships:
            relationship = ContainerRelationship(
                from_container=rel_data.source_id,
                to_container=rel_data.target_id,
                relationship_type=rel_data.relationship_type,
                strength=rel_data.strength,
                bidirectional=False  # Not in new structure, default to False
            )
            relationships.append(relationship)
        
        # Determine content flow
        content_flow = ContentFlow.LINEAR  # Default
        try:
            # Try to match by name first
            content_flow = ContentFlow[output.content_flow.upper()]
        except (KeyError, AttributeError):
            # Try to match by value
            for cf in ContentFlow:
                if cf.value.lower() == output.content_flow.lower():
                    content_flow = cf
                    break
        
        # Calculate metrics
        content_density = self._calculate_content_density(containers)
        complexity_score = self._calculate_complexity(containers, relationships)
        
        # Build manifest
        manifest = ContainerManifest(
            slide_id=slide.slide_id,
            slide_type=slide.slide_type,
            containers=containers,
            relationships=relationships,
            primary_message=output.primary_message,
            content_flow=content_flow,
            visual_hierarchy=output.visual_hierarchy,
            groupings=output.groupings,
            content_density=content_density,
            complexity_score=complexity_score,
            layout_constraints=None,  # Can be set based on recommendations
            accessibility_notes=None  # Can be set based on recommendations
        )
        
        return manifest
    
    def _calculate_content_density(self, containers: List[SemanticContainer]) -> float:
        """Calculate content density score"""
        if not containers:
            return 0.0
        
        # Consider number of containers and total content length
        total_content = sum(c.content_length or len(c.content) for c in containers)
        container_count = len(containers)
        
        # Normalize (heuristic)
        # Assume ~500 chars and ~5 containers is "medium" density (0.5)
        density = min(1.0, (total_content / 1000 + container_count / 10) / 2)
        
        return density
    
    def _calculate_complexity(
        self,
        containers: List[SemanticContainer],
        relationships: List[ContainerRelationship]
    ) -> float:
        """Calculate content complexity score"""
        if not containers:
            return 0.0
        
        # Factors for complexity
        hierarchy_depth = max(c.hierarchy_level for c in containers) if containers else 1
        relationship_density = len(relationships) / max(len(containers) - 1, 1)
        role_diversity = len(set(c.role for c in containers)) / len(containers)
        
        # Weight factors
        complexity = (
            (hierarchy_depth - 1) / 4 * 0.3 +  # Normalize to 0-1, weight 30%
            relationship_density * 0.4 +         # Weight 40%
            role_diversity * 0.3                 # Weight 30%
        )
        
        return min(1.0, max(0.0, complexity))
    
    def _get_fallback_manifest(self, slide: Slide) -> ContainerManifest:
        """Create basic manifest as fallback"""
        containers = []
        
        # Add title
        if slide.title:
            containers.append(SemanticContainer(
                id=f"{slide.slide_id}_title",
                role=ContainerRole.HEADLINE,
                content=slide.title,
                hierarchy_level=1,
                importance=ContentImportance.HIGH,
                visual_weight=0.7
            ))
        
        # Add key points
        if slide.key_points:
            for i, point in enumerate(slide.key_points):
                containers.append(SemanticContainer(
                    id=f"{slide.slide_id}_point_{i+1}",
                    role=ContainerRole.MAIN_POINT,
                    content=point,
                    hierarchy_level=2,
                    importance=ContentImportance.MEDIUM,
                    visual_weight=0.5
                ))
        
        # Create basic manifest
        return ContainerManifest(
            slide_id=slide.slide_id,
            slide_type=slide.slide_type,
            containers=containers,
            relationships=[],
            primary_message=slide.title or "Content",
            content_flow=ContentFlow.LINEAR,
            visual_hierarchy=[c.id for c in containers],
            groupings=[],
            content_density=0.5,
            complexity_score=0.3
        )
    
    async def analyze_batch(
        self,
        slides: List[Slide],
        theme_context: Optional[Dict[str, Any]] = None
    ) -> List[ContainerManifest]:
        """Analyze multiple slides in batch"""
        manifests = []
        
        for slide in slides:
            manifest = await self.analyze_structure(
                slide,
                theme_context=theme_context
            )
            manifests.append(manifest)
        
        return manifests