"""
Layout Engine Agent - Master Artisan for layout generation.

This agent uses iterative refinement with LangGraph to generate
optimal layouts based on theme and semantic structure.
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

from src.utils.logger import setup_logger
from ...utils.model_utils import create_model_with_fallback
from ...model_types.design_tokens import ThemeDefinition
from ...model_types.semantic_containers import ContainerManifest
from ...model_types.layout_state import LayoutState, LayoutEngineConfig, LayoutStatus
from ... import models as mvp_models
MVPLayout = mvp_models.MVPLayout
from .state_machine import LayoutEngineWorkflow
from .tools import (
    layout_pattern_tool, grid_position_tool,
    layout_validator_tool, visual_balance_tool
)

logger = setup_logger(__name__)


class LayoutContext(BaseModel):
    """Context for layout generation"""
    theme: ThemeDefinition
    manifest: ContainerManifest
    config: LayoutEngineConfig = Field(default_factory=LayoutEngineConfig)
    iteration_context: Optional[Dict[str, Any]] = None


class LayoutOutput(BaseModel):
    """Structured output from Layout Engine"""
    layout: Dict[str, Any] = Field(description="The generated layout")
    pattern_used: str = Field(description="Layout pattern applied")
    white_space_ratio: float = Field(description="Calculated white space ratio")
    balance_score: float = Field(description="Visual balance score")
    validation_passed: bool = Field(description="Whether layout passed validation")
    iterations_used: int = Field(description="Number of iterations needed")
    generation_notes: List[str] = Field(
        description="Notes about the generation process"
    )


class LayoutEngineAgent:
    """
    Layout Engine Agent - Generates optimal layouts through iterative refinement.
    
    This agent:
    - Uses the LangGraph state machine for iterative workflow
    - Applies sophisticated layout patterns
    - Validates and refines layouts
    - Ensures visual balance and proper spacing
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """Initialize Layout Engine with AI model and workflow"""
        # Create model with fallback support
        self.model = create_model_with_fallback(model_name)
        
        # Create workflow
        self.workflow = LayoutEngineWorkflow()
        
        # Create agent for AI-powered refinement
        self.agent = Agent(
            self.model,
            output_type=LayoutOutput,
            deps_type=LayoutContext,
            tools=[
                layout_pattern_tool,
                grid_position_tool,
                layout_validator_tool,
                visual_balance_tool
            ],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt for layout generation"""
        return """You are the Layout Engine - a Master Artisan of visual composition.
Your role is to create optimal layouts that balance aesthetics, functionality, and clarity.

Core Responsibilities:
1. Apply sophisticated layout patterns (golden ratio, rule of thirds, etc.)
2. Calculate precise grid positions for all containers
3. Ensure proper visual balance and white space
4. Validate layouts against constraints
5. Iteratively refine based on feedback

Layout Principles:
- HIERARCHY: Establish clear visual priority through size and position
- BALANCE: Distribute visual weight evenly across the canvas
- ALIGNMENT: Maintain precise grid alignment for professional appearance
- SPACING: Use white space effectively (30-50% is ideal)
- FLOW: Guide the eye naturally through content

Grid System:
- 160×90 integer-based grid
- Minimum 8-unit margins
- 4-unit gutters between elements
- All positions must be integers

Available Tools:
- generate_layout_pattern: Select optimal pattern for content
- calculate_grid_positions: Determine precise container positions
- validate_layout: Check layout against all constraints
- score_visual_balance: Analyze and improve visual balance

Iteration Strategy:
- Start with pattern selection based on content characteristics
- Position containers according to pattern zones
- Validate and identify issues
- Refine positions to address validation feedback
- Repeat until optimal or max iterations reached

Remember: You are crafting visual experiences, not just arranging boxes.
Every layout should feel intentional, balanced, and beautiful."""
    
    async def generate_layout(
        self,
        theme: ThemeDefinition,
        manifest: ContainerManifest,
        config: Optional[LayoutEngineConfig] = None
    ) -> MVPLayout:
        """Generate layout using iterative refinement workflow"""
        try:
            # Use default config if not provided
            if config is None:
                config = LayoutEngineConfig()
            
            # Create initial state
            initial_state = LayoutState(
                theme=theme,
                manifest=manifest,
                max_iterations=config.max_iterations,
                target_white_space_min=config.white_space_min,
                target_white_space_max=config.white_space_max
            )
            
            logger.info(
                f"Starting layout generation for slide {manifest.slide_id} "
                f"with {len(manifest.containers)} containers"
            )
            
            # Run the workflow
            final_state = await self.workflow.run(initial_state)
            
            # Check results
            if final_state.status == LayoutStatus.FINALIZED and final_state.final_layout:
                logger.info(
                    f"Layout generation successful - "
                    f"Iterations: {final_state.iteration}, "
                    f"Balance: {final_state.generation_metrics.get('final_balance_score', 0):.2f}"
                )
                # Reconstruct MVPLayout from dict
                return mvp_models.MVPLayout(**final_state.final_layout)
            else:
                logger.error(f"Layout generation failed: {final_state.status}")
                # Return best attempt if available
                if final_state.proposal_history:
                    best_proposal = max(
                        final_state.proposal_history,
                        key=lambda p: p.confidence
                    )
                    logger.info("Returning best attempt from history")
                    # Reconstruct MVPLayout from dict
                    return mvp_models.MVPLayout(**best_proposal.layout)
                else:
                    # Create fallback layout
                    return self._create_fallback_layout(manifest)
        
        except Exception as e:
            logger.error(f"Layout generation error: {e}")
            return self._create_fallback_layout(manifest)
    
    async def refine_layout(
        self,
        layout: MVPLayout,
        feedback: Dict[str, Any]
    ) -> MVPLayout:
        """Refine an existing layout based on feedback"""
        # This method allows external refinement requests
        # For now, we'll use the validation tools to analyze and improve
        
        try:
            # Validate current layout
            validation_input = {
                "layout": {
                    "containers": [
                        {
                            "id": c.id,
                            "position": c.position.model_dump(),
                            "visual_weight": 0.5  # Default weight
                        }
                        for c in layout.containers
                    ],
                    "white_space_ratio": layout.white_space_ratio
                },
                "theme": {"name": "current"},
                "requirements": feedback.get("requirements", {})
            }
            
            validation_report = await layout_validator_tool.function(
                LayoutValidationInput(**validation_input)
            )
            
            if validation_report.is_valid:
                logger.info("Layout already valid, no refinement needed")
                return layout
            
            # Use AI to suggest improvements
            context = LayoutContext(
                theme=ThemeDefinition(name="refinement"),
                manifest=ContainerManifest(
                    slide_id=layout.slide_id,
                    slide_type="generic",
                    containers=[],  # Would need actual manifest
                    relationships=[],
                    primary_message="Refinement",
                    content_flow="linear"
                ),
                iteration_context={
                    "current_layout": layout.model_dump(),
                    "validation_issues": [i.model_dump() for i in validation_report.issues],
                    "feedback": feedback
                }
            )
            
            prompt = f"""The current layout has validation issues:
{validation_report.issues}

User feedback: {feedback}

Please suggest specific position adjustments to fix these issues while maintaining visual balance."""
            
            result = await self.agent.run(prompt, deps=context)
            
            # Apply suggested changes (would need to parse and apply)
            # For now, return original
            return layout
            
        except Exception as e:
            logger.error(f"Layout refinement error: {e}")
            return layout
    
    def _create_fallback_layout(self, manifest: ContainerManifest) -> MVPLayout:
        """Create a simple fallback layout"""
        MVPContainer = mvp_models.MVPContainer
        GridPosition = mvp_models.GridPosition
        ContainerContent = mvp_models.ContainerContent
        
        containers = []
        y_offset = 8
        
        for i, container in enumerate(manifest.containers):
            # Simple vertical stacking
            mvp_container = MVPContainer(
                name=container.id,  # MVPContainer uses 'name' not 'id'
                position=GridPosition(
                    leftInset=8,
                    topInset=y_offset,
                    width=144,  # 160 - 2*8 margins
                    height=20
                ),
                content=ContainerContent(
                    type="text",
                    text=container.content,
                    style="body"
                )
            )
            containers.append(mvp_container)
            y_offset += 24  # Height + spacing
        
        # Determine slide number from slide_id
        slide_number = 1
        try:
            # Extract number from slide_id like "slide_001" or "test_001"
            parts = manifest.slide_id.split('_')
            if len(parts) > 1:
                slide_number = int(parts[-1])
        except:
            pass
        
        # Map slide type to layout name
        layout_mapping = {
            "title_slide": "titleSlide",
            "content_heavy": "contentSlide",
            "visual_heavy": "visualSlide",
            "data_driven": "dataSlide"
        }
        layout_name = layout_mapping.get(manifest.slide_type, "contentSlide")
        
        # Import required models
        LayoutSpec = mvp_models.LayoutSpec
        LayoutHints = mvp_models.LayoutHints
        ContentState = mvp_models.ContentState
        
        return MVPLayout(
            slide_id=manifest.slide_id,
            slide_number=slide_number,
            slide_type=manifest.slide_type,
            layout=layout_name,
            layout_spec=LayoutSpec(
                source="theme",
                layout_hints=LayoutHints()
            ),
            containers=containers,
            content_state=ContentState(),
            white_space_ratio=0.4,
            alignment_score=0.9
        )
    
    async def analyze_layout_quality(self, layout: MVPLayout) -> Dict[str, Any]:
        """Analyze the quality of a layout"""
        # Use visual balance tool
        balance_input = {
            "containers": [
                {
                    "id": c.id,
                    "position": c.position.model_dump()
                }
                for c in layout.containers
            ]
        }
        
        balance_result = await visual_balance_tool.function(
            VisualBalanceInput(**balance_input)
        )
        
        # Use validation tool
        validation_input = {
            "layout": {
                "containers": [
                    {
                        "id": c.id,
                        "position": c.position.model_dump(),
                        "visual_weight": 0.5
                    }
                    for c in layout.containers
                ],
                "white_space_ratio": layout.white_space_ratio
            },
            "theme": {"name": "analysis"},
            "requirements": {}
        }
        
        validation_report = await layout_validator_tool.function(
            LayoutValidationInput(**validation_input)
        )
        
        return {
            "balance_score": balance_result.balance_score,
            "center_of_mass": balance_result.center_of_mass,
            "quadrant_distribution": balance_result.quadrant_distribution,
            "is_valid": validation_report.is_valid,
            "white_space_ratio": validation_report.white_space_ratio,
            "alignment_score": validation_report.alignment_score,
            "issues": [i.model_dump() for i in validation_report.issues],
            "recommendations": balance_result.recommendations
        }
    
    async def generate_batch(
        self,
        themes_and_manifests: List[tuple[ThemeDefinition, ContainerManifest]],
        config: Optional[LayoutEngineConfig] = None
    ) -> List[MVPLayout]:
        """Generate layouts for multiple slides in batch"""
        layouts = []
        
        for theme, manifest in themes_and_manifests:
            layout = await self.generate_layout(theme, manifest, config)
            layouts.append(layout)
        
        return layouts