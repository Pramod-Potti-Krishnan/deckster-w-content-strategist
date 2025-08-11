"""
Layout Architect - Three-agent system for intelligent layout generation.

This module provides a sophisticated layout generation system using three
specialized agents:
- Theme Agent: Brand & Style Director
- Content Agent: Content Strategist
- Layout Architect Agent: Layout Designer

The orchestrator coordinates these agents to generate optimal layouts.
"""

# Import phase2b orchestrators
from .orchestrator_phase2b import LayoutArchitectOrchestratorPhase2B
from .orchestrator_phase2b_streaming import LayoutArchitectOrchestratorPhase2BStreaming

# Import agents from their specific modules
from .agents.theme_agent import ThemeAgent
from .agents.content_agent import ContentAgentV5, ContentManifest
from .agents.layout_architect_agent import LayoutArchitectAgent

# Import models from model_types subdirectory
from src.models.design_tokens import (
    DesignTokens, ThemeDefinition, GridZone, LayoutTemplate,
    ColorToken, TypographyToken, DimensionToken
)
from .model_types.semantic_containers import (
    SemanticContainer, ContainerManifest, ContainerRole,
    ContentImportance, ContentFlow, ContainerRelationship,
    RelationshipType
)
from .model_types.layout_state import (
    LayoutState, LayoutStatus, ValidationReport,
    LayoutEngineConfig
)

# Import MVP models from models.py file (not the models/ directory)
from .models import MVPLayout, MVPContainer, GridPosition, ContainerContent

__all__ = [
    # Orchestrators
    'LayoutArchitectOrchestratorPhase2B',
    'LayoutArchitectOrchestratorPhase2BStreaming',
    
    # Agents
    'ThemeAgent',
    'ContentAgentV5',
    'ContentManifest',
    'LayoutArchitectAgent',
    
    # Core Models
    'DesignTokens',
    'ThemeDefinition',
    'SemanticContainer',
    'ContainerManifest',
    'MVPLayout',
    'MVPContainer',
    'LayoutState',
    'LayoutEngineConfig',
    
    # Token Types
    'ColorToken',
    'TypographyToken', 
    'DimensionToken',
    
    # Layout Components
    'GridZone',
    'LayoutTemplate',
    'GridPosition',
    'ContainerContent',
    
    # Relationships
    'ContainerRelationship',
    
    # Enums
    'ContainerRole',
    'ContentImportance',
    'ContentFlow',
    'LayoutStatus',
    'RelationshipType',
]

# Version
__version__ = "2.0.0"