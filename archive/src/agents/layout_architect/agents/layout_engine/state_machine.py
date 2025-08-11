"""
LangGraph state machine for iterative layout generation.

This state machine implements the iterative refinement workflow
for the Layout Engine Agent, using validation feedback to improve layouts.
"""

from typing import Dict, Any, List, Optional, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from src.utils.logger import setup_logger
from ...model_types.layout_state import (
    LayoutState, LayoutStatus, LayoutProposal, ValidationReport
)
from ... import models as mvp_models
MVPLayout = mvp_models.MVPLayout
MVPContainer = mvp_models.MVPContainer
GridPosition = mvp_models.GridPosition
ContainerContent = mvp_models.ContainerContent
from .tools import (
    layout_pattern_tool, grid_position_tool,
    layout_validator_tool, visual_balance_tool,
    LayoutPatternInput, GridPositionInput,
    LayoutValidationInput, VisualBalanceInput
)

logger = setup_logger(__name__)


class LayoutEngineWorkflow:
    """
    LangGraph workflow for iterative layout generation.
    
    The workflow follows these steps:
    1. Initialize state from theme and manifest
    2. Generate layout proposal using pattern and positioning tools
    3. Validate the proposal
    4. Refine if needed based on validation feedback
    5. Finalize when valid or max iterations reached
    """
    
    def __init__(self):
        """Initialize the workflow graph"""
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        # Create graph with LayoutState
        workflow = StateGraph(LayoutState)
        
        # Add nodes
        workflow.add_node("initialize", self.initialize_node)
        workflow.add_node("propose_layout", self.propose_layout_node)
        workflow.add_node("validate_layout", self.validate_layout_node)
        workflow.add_node("refine_layout", self.refine_layout_node)
        workflow.add_node("finalize_layout", self.finalize_layout_node)
        
        # Add edges
        workflow.set_entry_point("initialize")
        
        # From initialize
        workflow.add_edge("initialize", "propose_layout")
        
        # From propose_layout
        workflow.add_edge("propose_layout", "validate_layout")
        
        # From validate_layout - conditional
        workflow.add_conditional_edges(
            "validate_layout",
            self.should_refine,
            {
                "refine": "refine_layout",
                "finalize": "finalize_layout",
                "fail": END
            }
        )
        
        # From refine_layout
        workflow.add_edge("refine_layout", "propose_layout")
        
        # From finalize_layout
        workflow.add_edge("finalize_layout", END)
        
        return workflow.compile()
    
    async def initialize_node(self, state: LayoutState) -> Dict[str, Any]:
        """Initialize the layout generation process"""
        logger.info(f"Initializing layout generation for slide {state.manifest.slide_id}")
        
        # Set initial status
        updates = {
            "status": LayoutStatus.PROPOSING,
            "iteration": 0,
            "refinement_attempts": 0,
            "generation_metrics": {
                "start_time": "now",
                "theme_name": state.theme.name,
                "container_count": len(state.manifest.containers)
            }
        }
        
        return updates
    
    async def propose_layout_node(self, state: LayoutState) -> Dict[str, Any]:
        """Generate a layout proposal using tools"""
        logger.info(f"Proposing layout - iteration {state.iteration + 1}")
        
        # Increment iteration
        iteration = state.iteration + 1
        
        try:
            # 1. Generate layout pattern
            pattern_input = LayoutPatternInput(
                container_count=len(state.manifest.containers),
                content_flow=state.manifest.content_flow.value,
                visual_emphasis=self._calculate_visual_emphasis(state.manifest),
                container_roles=[c.role.value for c in state.manifest.containers]
            )
            
            pattern_result = await layout_pattern_tool.function(pattern_input)
            
            # 2. Calculate grid positions
            container_data = [
                {
                    "id": c.id,
                    "importance_score": self._importance_to_score(c.importance),
                    "hierarchy_level": c.hierarchy_level,
                    "visual_weight": c.visual_weight
                }
                for c in state.manifest.containers
            ]
            
            position_input = GridPositionInput(
                containers=container_data,
                layout_zones=pattern_result.layout_zones,
                groupings=state.manifest.groupings or [],
                alignment_rules={}
            )
            
            position_result = await grid_position_tool.function(position_input)
            
            # 3. Build MVPLayout
            mvp_containers = []
            for container in state.manifest.containers:
                if container.id in position_result.positions:
                    pos_data = position_result.positions[container.id]
                    
                    mvp_container = MVPContainer(
                        id=container.id,
                        type=self._map_role_to_type(container.role),
                        position=GridPosition(**pos_data),
                        content=ContainerContent(
                            text=container.content,
                            style={
                                "fontSize": self._get_font_size(container.hierarchy_level),
                                "fontWeight": "bold" if container.importance.value in ["critical", "high"] else "normal"
                            }
                        )
                    )
                    mvp_containers.append(mvp_container)
            
            # Calculate white space
            white_space_ratio = self._calculate_white_space(mvp_containers)
            
            layout = MVPLayout(
                slide_id=state.manifest.slide_id,
                containers=mvp_containers,
                white_space_ratio=white_space_ratio
            )
            
            # Create proposal
            proposal = LayoutProposal(
                layout=layout.model_dump(),
                pattern_used=pattern_result.pattern_name,
                decisions_made=[
                    f"Applied {pattern_result.pattern_name} pattern",
                    f"Positioned {len(mvp_containers)} containers",
                    f"Space utilization: {position_result.space_utilization:.1%}"
                ],
                confidence=position_result.alignment_score * 0.8 + 0.2
            )
            
            # Update state
            updates = {
                "status": LayoutStatus.VALIDATING,
                "iteration": iteration,
                "current_proposal": proposal,
                "proposal_history": state.proposal_history + [proposal]
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Layout proposal failed: {e}")
            return {
                "status": LayoutStatus.FAILED,
                "iteration": iteration,
                "generation_metrics": {
                    **state.generation_metrics,
                    "error": str(e)
                }
            }
    
    async def validate_layout_node(self, state: LayoutState) -> Dict[str, Any]:
        """Validate the current layout proposal"""
        logger.info("Validating layout proposal")
        
        if not state.current_proposal:
            return {"status": LayoutStatus.FAILED}
        
        try:
            # Prepare validation input
            layout_dict = {
                "containers": [
                    {
                        "id": c.id,
                        "position": c.position.model_dump(),
                        "visual_weight": next(
                            (sc.visual_weight for sc in state.manifest.containers if sc.id == c.id),
                            0.5
                        )
                    }
                    for c in state.current_proposal.layout.containers
                ],
                "white_space_ratio": state.current_proposal.layout.white_space_ratio
            }
            
            validation_input = LayoutValidationInput(
                layout=layout_dict,
                theme={"name": state.theme.name},
                requirements={
                    "white_space_min": state.target_white_space_min,
                    "white_space_max": state.target_white_space_max,
                    "margin": 8
                }
            )
            
            # Run validation
            validation_report = await layout_validator_tool.function(validation_input)
            
            # Also check visual balance
            balance_input = VisualBalanceInput(
                containers=[
                    {
                        "id": c.id,
                        "position": c.position.model_dump(),
                        "importance": next(
                            (sc.importance.value for sc in state.manifest.containers if sc.id == c.id),
                            "medium"
                        ),
                        "role": c.type
                    }
                    for c in state.current_proposal.layout.containers
                ]
            )
            
            balance_result = await visual_balance_tool.function(balance_input)
            
            # Update validation report with balance score
            validation_report.balance_score = balance_result.balance_score
            
            # Log results
            logger.info(
                f"Validation results - Valid: {validation_report.is_valid}, "
                f"Balance: {balance_result.balance_score:.2f}, "
                f"Issues: {len(validation_report.issues)}"
            )
            
            updates = {
                "validation_report": validation_report,
                "generation_metrics": {
                    **state.generation_metrics,
                    f"iteration_{state.iteration}_valid": validation_report.is_valid,
                    f"iteration_{state.iteration}_balance": balance_result.balance_score
                }
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "status": LayoutStatus.FAILED,
                "generation_metrics": {
                    **state.generation_metrics,
                    "validation_error": str(e)
                }
            }
    
    def should_refine(self, state: LayoutState) -> Literal["refine", "finalize", "fail"]:
        """Decide whether to refine, finalize, or fail"""
        if state.status == LayoutStatus.FAILED:
            return "fail"
        
        if not state.validation_report:
            return "fail"
        
        # Check if valid
        if state.validation_report.is_valid:
            # Also check balance score
            if state.validation_report.balance_score >= 0.7:
                return "finalize"
            elif state.refinement_attempts < 2:
                # Try to improve balance even if valid
                logger.info("Layout valid but balance could be improved")
                return "refine"
            else:
                # Accept it after enough attempts
                return "finalize"
        
        # Check iteration limit
        if state.iteration >= state.max_iterations:
            logger.warning("Max iterations reached, finalizing best attempt")
            return "finalize"
        
        # Continue refining
        return "refine"
    
    async def refine_layout_node(self, state: LayoutState) -> Dict[str, Any]:
        """Refine layout based on validation feedback"""
        logger.info("Refining layout based on validation feedback")
        
        refinement_attempts = state.refinement_attempts + 1
        
        # Get refinement context
        context = state.get_refinement_context()
        
        # Log what we're trying to fix
        if context.get("errors"):
            logger.info(f"Addressing {len(context['errors'])} errors")
        if context.get("warnings"):
            logger.info(f"Addressing {len(context['warnings'])} warnings")
        
        # Update metrics
        updates = {
            "status": LayoutStatus.PROPOSING,
            "refinement_attempts": refinement_attempts,
            "generation_metrics": {
                **state.generation_metrics,
                f"refinement_{refinement_attempts}_reason": context.get("guidance", "General improvement")
            }
        }
        
        return updates
    
    async def finalize_layout_node(self, state: LayoutState) -> Dict[str, Any]:
        """Finalize the layout"""
        logger.info("Finalizing layout")
        
        if state.current_proposal and state.current_proposal.layout:
            final_layout = state.current_proposal.layout
            
            # Add final metrics
            metrics = {
                **state.generation_metrics,
                "total_iterations": state.iteration,
                "total_refinements": state.refinement_attempts,
                "final_valid": state.validation_report.is_valid if state.validation_report else False,
                "final_balance_score": state.validation_report.balance_score if state.validation_report else 0,
                "final_pattern": state.current_proposal.pattern_used
            }
            
            logger.info(
                f"Layout finalized - Iterations: {state.iteration}, "
                f"Valid: {metrics['final_valid']}, "
                f"Balance: {metrics['final_balance_score']:.2f}"
            )
            
            return {
                "status": LayoutStatus.FINALIZED,
                "final_layout": final_layout,
                "generation_metrics": metrics
            }
        else:
            logger.error("No valid layout to finalize")
            return {
                "status": LayoutStatus.FAILED,
                "generation_metrics": {
                    **state.generation_metrics,
                    "failure_reason": "No valid proposal"
                }
            }
    
    # Helper methods
    def _calculate_visual_emphasis(self, manifest) -> float:
        """Calculate visual emphasis from manifest"""
        visual_containers = sum(
            1 for c in manifest.containers 
            if c.requires_visual or c.role.value in ["image", "chart", "visual_element"]
        )
        total_containers = len(manifest.containers)
        
        return visual_containers / total_containers if total_containers > 0 else 0.0
    
    def _importance_to_score(self, importance) -> float:
        """Convert importance enum to numeric score"""
        scores = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3,
            "optional": 0.1
        }
        return scores.get(importance.value, 0.5)
    
    def _map_role_to_type(self, role) -> str:
        """Map semantic role to container type"""
        role_to_type = {
            "headline": "text",
            "key_takeaway": "text",
            "main_point": "text",
            "supporting_evidence": "text",
            "kpi_metric": "metric",
            "visual_element": "image",
            "image": "image",
            "chart": "chart",
            "call_to_action": "text",
            "context": "text",
            "navigation": "text"
        }
        return role_to_type.get(role.value, "text")
    
    def _get_font_size(self, hierarchy_level: int) -> str:
        """Get font size based on hierarchy level"""
        sizes = {
            1: "2.5rem",
            2: "1.5rem",
            3: "1.125rem",
            4: "1rem",
            5: "0.875rem"
        }
        return sizes.get(hierarchy_level, "1rem")
    
    def _calculate_white_space(self, containers: List[MVPContainer]) -> float:
        """Calculate white space ratio"""
        if not containers:
            return 1.0
        
        # Calculate total area used by containers
        total_area = 0
        for container in containers:
            pos = container.position
            total_area += pos.width * pos.height
        
        # Grid dimensions
        grid_area = 160 * 90
        
        # White space ratio
        white_space = 1.0 - (total_area / grid_area)
        
        return max(0.0, min(1.0, white_space))
    
    async def run(self, state: LayoutState) -> LayoutState:
        """Run the workflow with the given state"""
        result = await self.graph.ainvoke(state)
        return result