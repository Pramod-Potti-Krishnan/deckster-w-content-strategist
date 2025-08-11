# Agent Context Management System

## Overview

The Agent Context Management System provides a centralized way to manage context and state across all agents in the Deckster presentation generation pipeline. It enables:

- **Incremental Processing**: Agents can store and retrieve intermediate results
- **Context Sharing**: Downstream agents can access outputs from upstream agents
- **State Tracking**: Monitor the processing state of each agent
- **Error Recovery**: Track failures and enable reruns of specific agents
- **Performance Monitoring**: Measure processing times and identify bottlenecks

## Architecture

### Core Components

1. **AgentContextManager**: Central manager for all agent contexts in a session
2. **AgentContext**: Individual context data for each agent
3. **ContextAwareAgent**: Base class for agents that use the context system
4. **AgentType**: Enum defining all agent types in the system
5. **AgentState**: Enum tracking processing states

### Agent Dependencies

```
DIRECTOR
    ↓
THEME ←─────┐
    ↓       │
CONTENT ────┘
    ↓
LAYOUT
    ↓
REFINEMENT
```

## Usage Guide

### 1. Initialize Context Manager

```python
from src.utils.agent_context_manager import AgentContextManager

# Create context manager for a session
context_manager = AgentContextManager(
    session_id="unique_session_id",
    supabase_client=supabase  # Optional for persistence
)

# Load existing context if available
await context_manager.load_from_storage()
```

### 2. Create Context-Aware Agent

```python
from src.utils.agent_context_manager import ContextAwareAgent, AgentType

class SimplifiedThemeAgent(ContextAwareAgent):
    def __init__(self, context_manager: AgentContextManager):
        super().__init__(AgentType.THEME, context_manager)
        # Initialize agent-specific components
```

### 3. Track Agent Processing

```python
async def generate_theme(self, strawman, session_id):
    # Start processing
    input_data = {
        "strawman": strawman.dict(),
        "session_id": session_id
    }
    self.start_processing(input_data)
    
    try:
        # Perform agent work
        theme = await self._generate_theme_internal(strawman)
        
        # Mark as completed
        output_data = {
            "theme_definition": theme.dict(),
            "generation_method": "ai_generated"
        }
        self.complete_processing(output_data)
        
        # Save to storage
        await self.context_manager.save_to_storage()
        
        return theme
        
    except Exception as e:
        # Mark as failed
        self.fail_processing(str(e))
        raise
```

### 4. Access Upstream Context

```python
# In Content Agent, access Theme Agent's output
upstream_context = self.get_upstream_context()

if "theme" in upstream_context:
    theme_data = upstream_context["theme"]
    # Use theme data for content generation
```

### 5. Check Processing Status

```python
# Get overall processing summary
summary = context_manager.get_processing_summary()
print(f"Completed agents: {summary['completed_count']}")
print(f"Failed agents: {summary['failed_count']}")
print(f"Total time: {summary['total_time_ms']}ms")

# Check specific agent status
theme_status = summary['agents']['theme']
print(f"Theme agent state: {theme_status['state']}")
print(f"Theme processing time: {theme_status['processing_time_ms']}ms")
```

## Integration with Simplified Theme Agent

The Simplified Theme Agent demonstrates best practices for context management:

```python
class SimplifiedThemeAgent(ContextAwareAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash", 
                 context_manager: Optional[AgentContextManager] = None):
        if context_manager:
            super().__init__(AgentType.THEME, context_manager)
        else:
            self.context_manager = None
            
    async def generate_theme(self, strawman, session_id, 
                           director_metadata=None, brand_guidelines=None):
        # Track processing start if context manager available
        if self.context_manager:
            upstream_context = self.get_upstream_context()
            input_data = {
                "strawman": strawman.dict(),
                "director_metadata": director_metadata,
                "upstream_context": upstream_context
            }
            self.start_processing(input_data)
        
        try:
            # Generate theme...
            theme = await self._generate_theme_internal(...)
            
            # Track completion
            if self.context_manager:
                output_data = {
                    "theme_definition": theme.dict(),
                    "generation_method": "ai_generated",
                    "generation_time_ms": generation_time
                }
                self.complete_processing(output_data)
                await self.context_manager.save_to_storage()
                
            return theme
            
        except Exception as e:
            if self.context_manager:
                self.fail_processing(str(e))
            raise
```

## Benefits

### 1. Incremental Updates
- Agents can be rerun independently without losing previous work
- Failed agents can be retried without reprocessing successful ones

### 2. Performance Optimization
- Identify slow agents through timing data
- Cache results to avoid redundant processing

### 3. Debugging and Monitoring
- Track exactly where failures occur
- Understand data flow between agents
- Monitor processing times

### 4. Flexibility
- Easy to add new agents to the pipeline
- Dependencies are clearly defined
- Context can be persisted for session resumption

## Best Practices

1. **Always check for context manager**: Make agents work with or without context management
2. **Store meaningful output**: Include all data downstream agents might need
3. **Track metadata**: Include generation methods, confidence scores, timing
4. **Handle failures gracefully**: Use fail_processing to track errors
5. **Save incrementally**: Call save_to_storage after important operations

## Example: End-to-End Test Integration

```python
# In test_director_e2e.py
# Initialize context manager for test session
agent_context_manager = AgentContextManager(
    session_id=f"test_{scenario_name}",
    supabase_client=None  # No persistence for tests
)

# Create theme agent with context management
theme_agent = SimplifiedThemeAgent(
    context_manager=agent_context_manager
)

# Generate theme
theme = await theme_agent.generate_theme(
    strawman=refined_strawman,
    session_id=f"test_{scenario_name}_theme",
    director_metadata=director_metadata
)

# Check generation method
if theme.metadata.get('generation_method') == 'ai_generated':
    print("✅ Theme was AI-generated")
else:
    print("⚠️ Using fallback theme")

# Get processing summary
summary = agent_context_manager.get_processing_summary()
print(f"Theme processing time: {summary['agents']['theme']['processing_time_ms']}ms")
```

## Future Enhancements

1. **Parallel Processing**: Run independent agents concurrently
2. **Partial Results**: Store intermediate results during long operations
3. **Versioning**: Track multiple versions of agent outputs
4. **Metrics Collection**: Integration with monitoring systems
5. **Advanced Caching**: Smart invalidation based on input changes