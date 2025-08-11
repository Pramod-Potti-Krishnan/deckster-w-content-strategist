"""
Structure analyzer for Layout Architect.

Uses AI to intelligently analyze slide content and determine optimal
structure, container arrangement, and content relationships.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from src.models.agents import Slide
from src.utils.logger import setup_logger
from .models import LayoutArrangement, MVPContainer

logger = setup_logger(__name__)


class ContainerElement(BaseModel):
    """Represents a single element within a container."""
    type: str = Field(description="Element type: heading, text, bullet, image, etc.")
    content: str = Field(description="Element content or description")
    level: Optional[int] = Field(default=None, description="Hierarchy level (e.g., h1=1, h2=2)")


class StructureAnalysis(BaseModel):
    """AI-generated structure analysis for a slide."""
    arrangement: LayoutArrangement = Field(description="Recommended layout arrangement")
    rationale: str = Field(description="Explanation of why this structure was chosen")
    container_count: int = Field(description="Optimal number of containers")
    container_breakdown: Dict[str, List[ContainerElement]] = Field(
        description="Breakdown of elements within each container"
    )
    container_priorities: Dict[str, int] = Field(
        description="Importance ranking for containers (1=highest)"
    )
    visual_balance: float = Field(
        ge=0, le=1, 
        description="Visual balance score (0-1)"
    )
    content_relationships: List[str] = Field(
        description="How content pieces relate to each other"
    )
    placeholder_suggestions: Optional[Dict[str, str]] = Field(
        default=None,
        description="Suggested placeholder content for containers"
    )


class StructureAnalyzer:
    """Analyzes slide content to determine optimal structure using AI."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """Initialize structure analyzer with AI model."""
        import os
        
        # Set GEMINI_API_KEY from GOOGLE_API_KEY if needed
        if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
            os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
        
        self.model = GeminiModel(model_name)
        self.agent = Agent(
            self.model,
            output_type=StructureAnalysis,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for structure analysis."""
        return """You are a presentation design expert specializing in slide structure and layout.

Analyze the given slide content and determine:

1. **Optimal Layout Arrangement**: Choose from vertical, horizontal, or grid
   - Vertical: Content flows top to bottom (best for lists, sequential info)
   - Horizontal: Side-by-side content (best for comparisons, before/after)
   - Grid: Matrix layout (best for multiple equal items, dashboards)

2. **Container Breakdown**: Break content into logical containers
   - Identify distinct content groups
   - Determine hierarchy (h1, h2, h3, body text)
   - Count actual elements needed

3. **Content Relationships**: How pieces relate
   - Sequential (step by step)
   - Comparative (side by side)
   - Hierarchical (parent-child)
   - Matrix (equal importance)

4. **Visual Balance**: Score 0-1 based on:
   - Content density
   - Symmetry
   - White space distribution
   - Reading flow

Example Analysis:
For "3 key benefits with descriptions":
- arrangement: "grid" (3 equal items)
- container_count: 4 (1 title + 3 benefit containers)
- container_breakdown: {
    "title": [{"type": "heading", "content": "Key Benefits", "level": 1}],
    "benefit_1": [
      {"type": "heading", "content": "Benefit 1", "level": 3},
      {"type": "text", "content": "Description of benefit 1"}
    ],
    ...
  }

Be specific about the number of elements and their types. If content mentions "3 columns", 
ensure you create 3 separate containers with appropriate elements in each."""
    
    async def analyze_structure(
        self, 
        slide: Slide,
        existing_structure_preference: Optional[str] = None
    ) -> StructureAnalysis:
        """Analyze slide content and determine optimal structure."""
        try:
            # Build context for analysis
            context = self._build_analysis_context(slide, existing_structure_preference)
            
            # Run AI analysis
            result = await self.agent.run(
                f"""Analyze this slide structure:
                
Title: {slide.title}
Content Type: {slide.slide_type}
Structure Hint: {existing_structure_preference or 'None provided'}

Key Points:
{self._format_key_points(slide.key_points)}

Narrative: {slide.narrative}

Visual/Analytics Needs:
- Analytics: {slide.analytics_needed or 'None'}
- Visuals: {slide.visuals_needed or 'None'}
- Diagrams: {slide.diagrams_needed or 'None'}

Determine the optimal structure for this content."""
            )
            
            return result.data
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            # Return fallback analysis
            return self._get_fallback_analysis(slide, existing_structure_preference)
    
    def _build_analysis_context(
        self, 
        slide: Slide,
        structure_preference: Optional[str]
    ) -> Dict:
        """Build context for structure analysis."""
        return {
            "slide_type": slide.slide_type,
            "has_title": bool(slide.title),
            "key_points_count": len(slide.key_points) if slide.key_points else 0,
            "has_visuals": bool(slide.visuals_needed or slide.diagrams_needed),
            "has_analytics": bool(slide.analytics_needed),
            "structure_hint": structure_preference,
            "content_density": self._estimate_content_density(slide)
        }
    
    def _format_key_points(self, key_points: Optional[List[str]]) -> str:
        """Format key points for prompt."""
        if not key_points:
            return "No key points provided"
        return "\n".join(f"- {point}" for point in key_points)
    
    def _estimate_content_density(self, slide: Slide) -> str:
        """Estimate content density level."""
        total_content = 0
        if slide.key_points:
            total_content += len(slide.key_points)
        if slide.analytics_needed:
            total_content += 2  # Analytics usually need more space
        if slide.visuals_needed or slide.diagrams_needed:
            total_content += 2  # Visuals need space
        
        if total_content <= 3:
            return "low"
        elif total_content <= 6:
            return "medium"
        else:
            return "high"
    
    def _get_fallback_analysis(
        self, 
        slide: Slide,
        structure_preference: Optional[str]
    ) -> StructureAnalysis:
        """Get fallback analysis when AI fails."""
        # Determine arrangement based on content
        if "grid" in (structure_preference or "").lower():
            arrangement = LayoutArrangement.GRID
        elif "horizontal" in (structure_preference or "").lower() or "column" in (structure_preference or "").lower():
            arrangement = LayoutArrangement.HORIZONTAL
        else:
            arrangement = LayoutArrangement.VERTICAL
        
        # Basic container breakdown
        containers = {"title": [ContainerElement(type="heading", content=slide.title or "Title", level=1)]}
        
        if slide.key_points:
            for i, point in enumerate(slide.key_points):
                containers[f"point_{i+1}"] = [
                    ContainerElement(type="text", content=point)
                ]
        
        return StructureAnalysis(
            arrangement=arrangement,
            rationale="Fallback analysis based on content type",
            container_count=len(containers),
            container_breakdown={k: [e.model_dump() for e in v] for k, v in containers.items()},
            container_priorities={k: i+1 for i, k in enumerate(containers.keys())},
            visual_balance=0.5,
            content_relationships=["sequential"],
            placeholder_suggestions=None
        )