# Phase 2B: Content-Driven Layout Architecture

## Executive Summary

Phase 2B introduces a paradigm shift from "hope content fits layout" to "create layout that fits content." This architecture adds a Content Preparation Agent that works in parallel with the Theme Agent, providing the Layout Architect with actual content rather than guesses, enabling proper structure preference implementation.

## Problem Analysis

### Current Issues (Phase 2A)
1. **Layout Agent Guessing Game**: The StructureLayout Agent tries to analyze AND layout content simultaneously
2. **Structure Preference Mismatches**: 5/8 slides default to "verticalStack" instead of requested layouts
3. **Content Volume Unknown**: Agent doesn't know if "two-column layout" will fit unknown content
4. **Generic Fallbacks**: Without content awareness, agent defaults to safe, generic layouts

### Root Cause
The Layout Architect is making decisions without knowing:
- How much text content exists
- What visual elements are needed
- Content priorities and hierarchy
- Audience-appropriate detail level

## New Architecture: Three-Agent Parallel System

```
                    Strawman Data
                         |
         ┌───────────────┴───────────────┐
         ↓                               ↓
    Theme Agent                    Content Agent
  (Design Tokens)              (Prepared Content)
         ↓                               ↓
         └───────────────┬───────────────┘
                         ↓
                  Layout Architect
                 (Content-Aware Layout)
                         ↓
                   Final Layout
```

### Agent Responsibilities

#### 1. Theme Agent (Existing)
- Generates design tokens from strawman metadata
- Creates color palettes, typography, spacing
- Defines available layout templates
- **Unchanged from Phase 2A**

#### 2. Content Agent (NEW)
**Primary Responsibilities:**
- Expand strawman bullet points into presentation-ready text
- Generate detailed descriptions for visuals/charts/diagrams
- Enforce word count limits based on slide type
- Adjust content depth based on audience
- Mark content priorities for layout positioning

**Content Preparation Process:**
1. Receive slide data from strawman
2. Analyze slide type and structure preference
3. Determine word count budget
4. Expand content within constraints
5. Generate visual descriptions (not counted in word limit)
6. Tag content with priority levels
7. Output structured content manifest

#### 3. Layout Architect (Modified)
**Updated Responsibilities:**
- Receive prepared content + theme tokens
- Select appropriate layout based on actual content volume
- Position content based on priorities
- Honor structure preferences (now possible with known content)
- Generate final grid positions

## Content Constraints

### Word Count Limits by Slide Type

| Slide Type | Base Word Count | Description |
|------------|-----------------|-------------|
| title_slide | 10-20 words | Title, subtitle, presenter info only |
| section_divider | 15-30 words | Section title and brief description |
| content_heavy | 80-120 words | Detailed explanations, multiple points |
| data_driven | 40-60 words | Text + detailed chart description |
| visual_heavy | 30-50 words | Minimal text + comprehensive image description |
| mixed_content | 60-90 words | Balanced text and visual descriptions |
| diagram_focused | 40-70 words | Process explanation + diagram description |
| conclusion_slide | 50-80 words | Key takeaways and call to action |

### Audience Adjustments

| Audience Type | Word Count Adjustment | Content Style |
|---------------|----------------------|---------------|
| Executives | -30% | Focus on outcomes, ROI, strategic impact |
| Technical | +20% | Include methodology, technical details |
| General Public | Baseline | Avoid jargon, use simple language |
| Educational | +10% | Add definitions, examples |
| Healthcare Professionals | Baseline | Medical terminology acceptable |
| Investors | -20% | Focus on metrics, growth, market opportunity |

### Content Priority Levels

1. **Critical (P1)**: Must be prominently displayed
2. **Important (P2)**: Should be clearly visible
3. **Supporting (P3)**: Can be smaller or secondary
4. **Optional (P4)**: Include if space permits

## Visual Description Format

```json
{
  "visual_type": "chart|diagram|image|icon",
  "description": "Detailed description for visual generation",
  "visual_spec": {
    // For charts
    "chart_type": "bar|line|pie|scatter",
    "data_points": [
      {"label": "...", "value": 0}
    ],
    "axes": {"x": "label", "y": "label"},
    
    // For diagrams
    "diagram_type": "flowchart|mindmap|process|hierarchy",
    "nodes": [...],
    "connections": [...],
    
    // For images
    "image_style": "photo|illustration|abstract",
    "key_elements": ["element1", "element2"],
    "mood": "professional|inspirational|technical"
  },
  "space_requirement": "large|medium|small",
  "layout_preference": "left|right|center|full-width"
}
```

## Content Manifest Structure

```typescript
interface ContentManifest {
  slide_id: string;
  slide_type: string;
  structure_preference: string;
  target_audience: string;
  
  text_content: {
    title: {
      text: string;
      word_count: number;
      priority: Priority;
    };
    main_points: Array<{
      text: string;
      word_count: number;
      priority: Priority;
    }>;
    supporting_text?: {
      text: string;
      word_count: number;
      priority: Priority;
    };
  };
  
  visual_content?: {
    primary_visual?: VisualDescription;
    supporting_visuals?: VisualDescription[];
  };
  
  content_metrics: {
    total_word_count: number;
    word_count_limit: number;
    visual_count: number;
    content_density: "light|medium|heavy";
  };
  
  layout_hints: {
    preferred_reading_flow: "F-pattern|Z-pattern|linear|circular";
    emphasis_areas: string[];
    grouping_suggestions: string[][];
  };
}
```

## Implementation Benefits

### Immediate Improvements
1. **Structure Preferences Honored**: Layout decisions based on actual content
2. **No Content Overflow**: Pre-sized content fits slide constraints
3. **Better Visual Balance**: Real content weights, not estimates
4. **Audience Optimization**: Content depth tuned before layout

### New Capabilities
1. **Dynamic Layout Selection**: Choose optimal layout for actual content
2. **Priority-Based Positioning**: Most important content gets prime placement
3. **Content-Aware Spacing**: Adjust white space based on content density
4. **Responsive Design**: Layout adapts to content, not vice versa

## Migration Path

### Phase 1: Content Agent Implementation
1. Create content agent structure
2. Implement content expansion logic
3. Add word count enforcement
4. Create visual description generator

### Phase 2: Orchestrator Update
1. Add parallel execution for Theme + Content
2. Modify Layout Architect input interface
3. Update content flow pipeline

### Phase 3: Layout Architect Enhancement
1. Remove content analysis logic
2. Add content manifest consumption
3. Implement priority-based positioning
4. Update structure preference mapping

### Phase 4: Testing & Validation
1. Test structure preference compliance
2. Validate content fit within limits
3. Verify audience adaptations
4. Performance benchmarking

## Success Metrics

1. **Structure Preference Compliance**: >95% of requested layouts implemented
2. **Content Fit Rate**: 100% of content fits within slide bounds
3. **Visual Balance Score**: >0.8 average across all layouts
4. **Generation Time**: <30s for complete presentation (parallel execution)

## Risk Mitigation

1. **Content Generation Quality**: Use same high-quality models as other agents
2. **Word Count Accuracy**: Implement strict tokenization and counting
3. **Visual Description Clarity**: Provide detailed schemas and examples
4. **Backward Compatibility**: Maintain fallback to Phase 2A if needed

## Conclusion

Phase 2B represents a fundamental architectural improvement that addresses the root cause of layout issues. By separating content preparation from layout generation, we enable true content-driven design that honors user preferences while ensuring professional, balanced presentations.

The parallel execution of Theme and Content agents maintains performance while dramatically improving output quality. This architecture scales well and provides a foundation for future enhancements like real-time content adjustment and multi-language support.