"""
Agent Context Manager - Manages incremental context for agents.

This system allows agents to:
1. Store their outputs for future agents
2. Access outputs from previous agents
3. Track processing state
4. Enable incremental updates
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentType(str, Enum):
    """Types of agents in the system"""
    DIRECTOR = "director"
    THEME = "theme"
    CONTENT = "content"
    LAYOUT = "layout"
    REFINEMENT = "refinement"


class AgentState(str, Enum):
    """Processing state of an agent"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentContext(BaseModel):
    """Context data for a single agent"""
    agent_type: AgentType
    state: AgentState = AgentState.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None


class AgentContextManager:
    """
    Manages context across all agents in a session.
    
    This allows agents to:
    - Store their outputs for downstream agents
    - Access outputs from upstream agents
    - Track processing state and metadata
    - Enable incremental updates and reruns
    """
    
    def __init__(self, session_id: str, supabase_client: Optional[Any] = None):
        """
        Initialize context manager.
        
        Args:
            session_id: Unique session identifier
            supabase_client: Optional Supabase client for persistence
        """
        self.session_id = session_id
        self.supabase = supabase_client
        self.contexts: Dict[AgentType, AgentContext] = {}
        self._initialize_contexts()
        
        logger.info(f"Initialized AgentContextManager for session {session_id}")
    
    def _initialize_contexts(self):
        """Initialize empty contexts for all agent types"""
        for agent_type in AgentType:
            self.contexts[agent_type] = AgentContext(agent_type=agent_type)
    
    async def load_from_storage(self) -> bool:
        """
        Load existing context from Supabase if available.
        
        Returns:
            True if context was loaded, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table("agent_contexts").select("*").eq(
                "session_id", self.session_id
            ).execute()
            
            if result.data:
                for record in result.data:
                    agent_type = AgentType(record["agent_type"])
                    self.contexts[agent_type] = AgentContext(**record["context_data"])
                logger.info(f"Loaded {len(result.data)} agent contexts from storage")
                return True
        except Exception as e:
            logger.error(f"Failed to load context from storage: {e}")
        
        return False
    
    async def save_to_storage(self) -> bool:
        """
        Save current context to Supabase.
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            for agent_type, context in self.contexts.items():
                data = {
                    "session_id": self.session_id,
                    "agent_type": agent_type.value,
                    "context_data": context.dict(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Upsert the context
                self.supabase.table("agent_contexts").upsert(data).execute()
            
            logger.info(f"Saved {len(self.contexts)} agent contexts to storage")
            return True
        except Exception as e:
            logger.error(f"Failed to save context to storage: {e}")
        
        return False
    
    def start_agent(
        self,
        agent_type: AgentType,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Mark an agent as started and store its input.
        
        Args:
            agent_type: Type of agent starting
            input_data: Input data for the agent
            metadata: Optional metadata
        """
        context = self.contexts[agent_type]
        context.state = AgentState.IN_PROGRESS
        context.input_data = input_data
        context.metadata = metadata or {}
        context.started_at = datetime.utcnow()
        
        logger.info(f"Started {agent_type.value} agent for session {self.session_id}")
    
    def complete_agent(
        self,
        agent_type: AgentType,
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Mark an agent as completed and store its output.
        
        Args:
            agent_type: Type of agent completing
            output_data: Output data from the agent
            metadata: Optional metadata to merge
        """
        context = self.contexts[agent_type]
        context.state = AgentState.COMPLETED
        context.output_data = output_data
        context.completed_at = datetime.utcnow()
        
        if context.started_at:
            context.processing_time_ms = int(
                (context.completed_at - context.started_at).total_seconds() * 1000
            )
        
        if metadata:
            context.metadata.update(metadata)
        
        logger.info(
            f"Completed {agent_type.value} agent for session {self.session_id} "
            f"in {context.processing_time_ms}ms"
        )
    
    def fail_agent(self, agent_type: AgentType, error_message: str):
        """
        Mark an agent as failed.
        
        Args:
            agent_type: Type of agent that failed
            error_message: Error message
        """
        context = self.contexts[agent_type]
        context.state = AgentState.FAILED
        context.error_message = error_message
        context.completed_at = datetime.utcnow()
        
        logger.error(f"Failed {agent_type.value} agent: {error_message}")
    
    def get_agent_output(self, agent_type: AgentType) -> Optional[Dict[str, Any]]:
        """
        Get output from a specific agent.
        
        Args:
            agent_type: Type of agent to get output from
            
        Returns:
            Output data if agent completed, None otherwise
        """
        context = self.contexts.get(agent_type)
        if context and context.state == AgentState.COMPLETED:
            return context.output_data
        return None
    
    def get_upstream_context(self, agent_type: AgentType) -> Dict[str, Any]:
        """
        Get all available context from agents that should run before this one.
        
        Args:
            agent_type: Current agent type
            
        Returns:
            Dictionary of upstream agent outputs
        """
        # Define agent dependencies
        dependencies = {
            AgentType.THEME: [AgentType.DIRECTOR],
            AgentType.CONTENT: [AgentType.DIRECTOR, AgentType.THEME],
            AgentType.LAYOUT: [AgentType.DIRECTOR, AgentType.THEME, AgentType.CONTENT],
            AgentType.REFINEMENT: [AgentType.DIRECTOR, AgentType.THEME, AgentType.CONTENT, AgentType.LAYOUT]
        }
        
        upstream_context = {}
        
        for dep in dependencies.get(agent_type, []):
            output = self.get_agent_output(dep)
            if output:
                upstream_context[dep.value] = output
        
        return upstream_context
    
    def can_run_agent(self, agent_type: AgentType) -> bool:
        """
        Check if an agent can run based on its dependencies.
        
        Args:
            agent_type: Type of agent to check
            
        Returns:
            True if all dependencies are satisfied
        """
        dependencies = {
            AgentType.THEME: [AgentType.DIRECTOR],
            AgentType.CONTENT: [AgentType.DIRECTOR],  # Theme is optional
            AgentType.LAYOUT: [AgentType.CONTENT],
            AgentType.REFINEMENT: [AgentType.CONTENT]
        }
        
        required_deps = dependencies.get(agent_type, [])
        
        for dep in required_deps:
            if self.contexts[dep].state != AgentState.COMPLETED:
                return False
        
        return True
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all agent processing states.
        
        Returns:
            Summary dictionary with agent states and timings
        """
        summary = {
            "session_id": self.session_id,
            "agents": {},
            "total_time_ms": 0,
            "completed_count": 0,
            "failed_count": 0
        }
        
        for agent_type, context in self.contexts.items():
            agent_summary = {
                "state": context.state.value,
                "processing_time_ms": context.processing_time_ms,
                "has_output": bool(context.output_data)
            }
            
            if context.error_message:
                agent_summary["error"] = context.error_message
            
            if context.metadata:
                agent_summary["metadata"] = context.metadata
            
            summary["agents"][agent_type.value] = agent_summary
            
            if context.state == AgentState.COMPLETED:
                summary["completed_count"] += 1
                if context.processing_time_ms:
                    summary["total_time_ms"] += context.processing_time_ms
            elif context.state == AgentState.FAILED:
                summary["failed_count"] += 1
        
        return summary
    
    def reset_agent(self, agent_type: AgentType):
        """
        Reset a specific agent's context.
        
        Args:
            agent_type: Type of agent to reset
        """
        self.contexts[agent_type] = AgentContext(agent_type=agent_type)
        logger.info(f"Reset {agent_type.value} agent context")
    
    def reset_downstream(self, agent_type: AgentType):
        """
        Reset an agent and all its downstream dependencies.
        
        Args:
            agent_type: Type of agent that changed
        """
        # Define downstream dependencies
        downstream_map = {
            AgentType.DIRECTOR: [AgentType.THEME, AgentType.CONTENT, AgentType.LAYOUT, AgentType.REFINEMENT],
            AgentType.THEME: [AgentType.CONTENT, AgentType.LAYOUT, AgentType.REFINEMENT],
            AgentType.CONTENT: [AgentType.LAYOUT, AgentType.REFINEMENT],
            AgentType.LAYOUT: [AgentType.REFINEMENT]
        }
        
        # Reset the agent itself
        self.reset_agent(agent_type)
        
        # Reset all downstream agents
        for downstream in downstream_map.get(agent_type, []):
            self.reset_agent(downstream)
        
        logger.info(f"Reset {agent_type.value} and all downstream agents")


class ContextAwareAgent:
    """
    Base class for agents that use the context management system.
    
    Provides helper methods for accessing and storing context.
    """
    
    def __init__(self, agent_type: AgentType, context_manager: AgentContextManager):
        """
        Initialize context-aware agent.
        
        Args:
            agent_type: Type of this agent
            context_manager: Context manager instance
        """
        self.agent_type = agent_type
        self.context_manager = context_manager
    
    def get_upstream_context(self) -> Dict[str, Any]:
        """Get context from upstream agents"""
        return self.context_manager.get_upstream_context(self.agent_type)
    
    def start_processing(self, input_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Mark agent as started"""
        self.context_manager.start_agent(self.agent_type, input_data, metadata)
    
    def complete_processing(self, output_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Mark agent as completed"""
        self.context_manager.complete_agent(self.agent_type, output_data, metadata)
    
    def fail_processing(self, error_message: str):
        """Mark agent as failed"""
        self.context_manager.fail_agent(self.agent_type, error_message)
    
    def can_run(self) -> bool:
        """Check if this agent can run"""
        return self.context_manager.can_run_agent(self.agent_type)