# Mermaid Diagrams Playbook - Enhanced Version 2.0

## Overview

The Mermaid Diagrams Playbook provides comprehensive specifications for all 9 Mermaid diagram types with **enhanced syntax patterns** designed for effective LLM usage. This playbook serves as the authoritative reference for Mermaid diagram generation within the system.

## Supported Diagram Types

### 1. **Flowchart** (Process Category)
- **Use Cases**: Process flows, decision trees, system architectures, algorithms
- **Key Features**: Multiple node shapes, various edge types, subgraph support
- **Orientations**: TD, TB, BT, LR, RL

### 2. **Class Diagram** (Structural Category)
- **Use Cases**: OOP design, system architecture, data models, API structures
- **Key Features**: Inheritance, composition, interfaces, visibility modifiers
- **Relationships**: Inheritance, composition, aggregation, association

### 3. **Entity Relationship Diagram** (Data Category)
- **Use Cases**: Database schemas, data relationships, domain models
- **Key Features**: Cardinality notation, primary/foreign keys, attributes
- **Relationship Types**: One-to-one, one-to-many, many-to-many

### 4. **User Journey Map** (Experience Category)
- **Use Cases**: User experience visualization, customer journeys, workflow satisfaction
- **Key Features**: Sections, tasks with scores (0-5), actor assignment
- **Score Meaning**: 0 (Very negative) to 5 (Very positive)

### 5. **Gantt Chart** (Project Category)
- **Use Cases**: Project timelines, task scheduling, milestone tracking
- **Key Features**: Dependencies, critical paths, date exclusion, sections
- **Task States**: active, done, crit, milestone

### 6. **Quadrant Chart** (Analysis Category)
- **Use Cases**: 2x2 matrix analysis, priority mapping, effort vs impact
- **Key Features**: Custom quadrant labels, data points with [x,y] coordinates
- **Coordinate Range**: 0 to 1 for both axes

### 7. **Timeline** (Chronological Category)
- **Use Cases**: Historical events, project milestones, roadmaps
- **Key Features**: Sections, multiple events per period, automatic coloring
- **Format**: Single or multiple events per time period

### 8. **Kanban Board** (Workflow Category)
- **Use Cases**: Task management, workflow visualization, WIP limits
- **Key Features**: Columns, task metadata, priority levels, ticket linking
- **Metadata**: Assigned person, ticket ID, priority level

### 9. **Architecture Diagram** (Technical Category) - Beta
- **Use Cases**: Cloud architecture, service relationships, deployment infrastructure
- **Key Features**: Groups, services, directional connections, 200k+ icons
- **Default Icons**: cloud, database, disk, internet, server

## Enhanced Playbook Structure (v2.0)

Each diagram type specification now includes:

1. **Basic Metadata**
   - Name and category
   - Mermaid type identifier
   
2. **When to Use**
   - Clear use cases and scenarios
   - Best fit situations
   
3. **Syntax Patterns** ✨ NEW
   - Complete statement templates with `<placeholders>`
   - Node/element definition patterns
   - Edge/relationship patterns
   - Ready-to-use syntax templates
   
4. **Construction Rules** ✨ NEW
   - Step-by-step building instructions
   - Exact ordering requirements
   - Format specifications
   - Clear examples for each step
   
5. **Escape Rules** ✨ NEW
   - Special character handling
   - Reserved words to avoid
   - Quote usage guidelines
   - Unicode and emoji support
   
6. **Configuration Options**
   - Layout settings
   - Spacing and padding
   - Renderer options
   
7. **Best Practices**
   - Maximum element counts
   - Naming conventions
   - Organization guidelines
   
8. **Examples**
   - Basic example
   - Advanced examples
   - Complete real-world examples

## Key Improvements for LLM Usage

### Enhanced Syntax Patterns
The v2.0 playbook provides concrete syntax patterns with clear placeholders that LLMs can directly use:

**Example - Flowchart Node Definition:**
```
Pattern: <nodeId>[\"<label>\"]
Usage: Start[\"Begin Process\"]
```

**Example - ER Relationship:**
```
Pattern: <ENTITY1> <cardinality1><line><cardinality2> <ENTITY2> : <verb>
Usage: CUSTOMER ||--o{ ORDER : places
```

### Step-by-Step Construction Rules
Each diagram type includes numbered steps for building valid Mermaid syntax:
1. Start with diagram type declaration
2. Define elements with specific syntax
3. Connect elements using patterns
4. Add metadata and styling

### Comprehensive Escape Rules
Clear guidance on handling special characters:
- Use `&quot;` for quotes in labels
- Use `&lt;` and `&gt;` for angle brackets  
- Wrap labels in quotes when containing special chars
- List of reserved words to avoid

## Helper Functions

The playbook provides enhanced utility functions:

- `get_diagram_spec(diagram_type)` - Get full specification for a diagram type
- `get_diagrams_by_category(category)` - List diagrams in a category
- `get_diagram_when_to_use(diagram_type)` - Get use cases for a diagram
- `get_syntax_patterns(diagram_type)` - Get detailed syntax patterns ✨ NEW
- `get_construction_rules(diagram_type)` - Get step-by-step rules ✨ NEW
- `get_escape_rules(diagram_type)` - Get escape sequences ✨ NEW
- `get_diagram_examples(diagram_type)` - Get example code
- `find_diagrams_for_intent(intent)` - Find suitable diagrams for an intent
- `get_all_diagram_types()` - List all supported types
- `get_diagram_categories()` - List all categories
- `validate_mermaid_syntax(diagram_type, code)` - Basic syntax validation
- `get_best_diagram_for_data(data)` - Recommend diagram based on data
- `get_template(template_name)` - Get pre-built templates
- `list_available_templates()` - List available templates

## Templates

Pre-built templates are available for common use cases:
- `flowchart_decision` - Decision flow template
- `class_hierarchy` - Class inheritance template
- `er_database` - Database schema template
- `journey_template` - User journey template
- `gantt_project` - Project timeline template
- `quadrant_analysis` - Priority matrix template

## Integration

The playbook integrates seamlessly with the existing `mermaid_agent.py` to provide:
- Intelligent diagram type selection
- Proper syntax generation
- Theme application
- Validation support

## Usage Example

```python
from src.agents.diagram_utils.mermaid_playbook import (
    get_diagram_spec,
    find_diagrams_for_intent,
    get_template
)

# Get specification for flowchart
flowchart_spec = get_diagram_spec("flowchart")

# Find suitable diagrams for a use case
diagrams = find_diagrams_for_intent("project timeline")
# Returns: ['gantt']

# Get a template
template = get_template("gantt_project")
```

## Testing

A comprehensive test suite (`test_mermaid_playbook.py`) validates:
- Playbook structure integrity
- All diagram specifications
- Helper function operations
- Syntax validation
- Template availability

Run tests with:
```bash
python3 src/agents/diagram_utils/test_mermaid_playbook.py
```

## Version History

### Version 2.0 (Current)
- **Date**: 2024
- **Major Changes**: 
  - Added detailed syntax patterns with `<placeholder>` format
  - Added step-by-step construction rules
  - Added comprehensive escape rules
  - Enhanced for LLM usage with concrete patterns
  - Replaced abstract syntax_requirements with actionable patterns
- **Based on**: Official Mermaid.js documentation

### Version 1.0
- **Date**: 2024
- **Initial Release**: Basic playbook structure with syntax requirements