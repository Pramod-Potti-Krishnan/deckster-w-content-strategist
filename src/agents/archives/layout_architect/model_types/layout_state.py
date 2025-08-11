"""
State models for Layout Engine Agent's iterative workflow.

These models define the state that flows through the LangGraph
state machine for layout generation.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field
from enum import Enum

from .design_tokens import ThemeDefinition
from .semantic_containers import ContainerManifest

# Avoid circular import - only import for type checking
if TYPE_CHECKING:
    from ..models import MVPLayout, MVPContainer


class LayoutStatus(str, Enum):
    """Status of layout generation"""
    INITIALIZING = "initializing"
    PROPOSING = "proposing"
    VALIDATING = "validating"
    REFINING = "refining"
    FINALIZED = "finalized"
    FAILED = "failed"


class ValidationIssue(BaseModel):
    """Individual validation issue"""
    issue_type: str = Field(description="Type of validation issue")
    severity: str = Field(description="Severity: error, warning, info")
    message: str = Field(description="Human-readable description")
    affected_containers: List[str] = Field(
        default_factory=list,
        description="IDs of affected containers"
    )
    suggestion: Optional[str] = Field(
        default=None,
        description="Suggested fix"
    )


class ValidationReport(BaseModel):
    """Complete validation report for a layout"""
    is_valid: bool = Field(description="Whether layout passes all validations")
    white_space_ratio: float = Field(description="Calculated white space ratio")
    alignment_score: float = Field(description="Grid alignment score (0-1)")
    balance_score: float = Field(description="Visual balance score (0-1)")
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="List of validation issues"
    )
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get only error-level issues"""
        return [i for i in self.issues if i.severity == "error"]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues"""
        return [i for i in self.issues if i.severity == "warning"]


class LayoutProposal(BaseModel):
    """Proposed layout with metadata"""
    layout: Dict[str, Any] = Field(description="The proposed layout as dict")
    pattern_used: str = Field(description="Layout pattern applied")
    decisions_made: List[str] = Field(
        default_factory=list,
        description="Key decisions made during generation"
    )
    confidence: float = Field(
        ge=0, le=1,
        description="Confidence in the proposal"
    )


class LayoutState(BaseModel):
    """
    State for iterative layout generation workflow.
    
    This state flows through the LangGraph nodes during
    the layout generation process.
    """
    # Input data
    theme: ThemeDefinition = Field(description="Theme definition with tokens and templates")
    manifest: ContainerManifest = Field(description="Semantic container manifest")
    
    # Current state
    status: LayoutStatus = Field(
        default=LayoutStatus.INITIALIZING,
        description="Current status of layout generation"
    )
    iteration: int = Field(
        default=0,
        description="Current iteration number"
    )
    
    # Layout data
    current_proposal: Optional[LayoutProposal] = Field(
        default=None,
        description="Current layout proposal"
    )
    validation_report: Optional[ValidationReport] = Field(
        default=None,
        description="Validation results for current proposal"
    )
    
    # History
    proposal_history: List[LayoutProposal] = Field(
        default_factory=list,
        description="History of all proposals"
    )
    refinement_attempts: int = Field(
        default=0,
        description="Number of refinement attempts"
    )
    
    # Configuration
    max_iterations: int = Field(
        default=5,
        description="Maximum iterations before giving up"
    )
    target_white_space_min: float = Field(
        default=0.3,
        description="Minimum white space ratio"
    )
    target_white_space_max: float = Field(
        default=0.5,
        description="Maximum white space ratio"
    )
    
    # Results
    final_layout: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Final validated layout as dict"
    )
    generation_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metrics about the generation process"
    )
    
    def should_continue(self) -> bool:
        """Check if workflow should continue"""
        if self.status == LayoutStatus.FINALIZED:
            return False
        if self.status == LayoutStatus.FAILED:
            return False
        if self.iteration >= self.max_iterations:
            return False
        return True
    
    def is_valid(self) -> bool:
        """Check if current proposal is valid"""
        return (
            self.validation_report is not None and
            self.validation_report.is_valid
        )
    
    def get_refinement_context(self) -> Dict[str, Any]:
        """Get context for refinement based on validation"""
        if not self.validation_report:
            return {}
        
        context = {
            "errors": [i.dict() for i in self.validation_report.get_errors()],
            "warnings": [i.dict() for i in self.validation_report.get_warnings()],
            "white_space_ratio": self.validation_report.white_space_ratio,
            "alignment_score": self.validation_report.alignment_score,
            "balance_score": self.validation_report.balance_score
        }
        
        # Add specific guidance
        if self.validation_report.white_space_ratio < self.target_white_space_min:
            context["guidance"] = "Increase spacing between containers or reduce container sizes"
        elif self.validation_report.white_space_ratio > self.target_white_space_max:
            context["guidance"] = "Decrease spacing or increase container sizes"
        
        return context


class LayoutEngineConfig(BaseModel):
    """Configuration for Layout Engine"""
    enable_ai_refinement: bool = Field(
        default=True,
        description="Use AI for intelligent refinement"
    )
    max_iterations: int = Field(
        default=5,
        description="Maximum refinement iterations"
    )
    white_space_min: float = Field(
        default=0.3,
        description="Minimum white space ratio"
    )
    white_space_max: float = Field(
        default=0.5,
        description="Maximum white space ratio"
    )
    alignment_tolerance: int = Field(
        default=0,
        description="Grid alignment tolerance"
    )
    balance_threshold: float = Field(
        default=0.7,
        description="Minimum balance score"
    )