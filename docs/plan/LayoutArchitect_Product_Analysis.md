# Layout Architect Product Analysis & Functional Specification

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Product Concept Analysis](#product-concept-analysis)
3. [Phase 1 Integration](#phase-1-integration)
4. [Phase 3 Agent Guidance](#phase-3-agent-guidance)
5. [Detailed Functional Specification](#detailed-functional-specification)
   - [Primary Functions](#primary-functions)
   - [Supporting Functions](#supporting-functions)
   - [User Interaction Flows](#user-interaction-flows)
6. [System Architecture](#system-architecture)
   - [Memory Requirements](#memory-requirements)
   - [Integration Requirements](#integration-requirements)
   - [Data Flow Analysis](#data-flow-analysis)
7. [Technical Specifications](#technical-specifications)
   - [WebSocket Messages](#new-websocket-messages)
   - [Database Schema](#database-schema-extensions)
   - [Performance Requirements](#performance)
   - [Success Metrics](#success-metrics)
8. [Implementation Guidelines](#implementation-guidelines)
   - [Modular Prompt System](#modular-prompt-system)
   - [Concurrency Model](#concurrency-model)
   - [Frontend Compatibility](#frontend-compatibility)
9. [Appendices](#appendices)
   - A: Glossary
   - B: Referenced Documents
   - C: Open Questions
   - D: Container Type Reference
   - E: Typography Specification
   - F: Content Type Registry
   - G: Slide Type Strategy Matrix

## Executive Summary
- **Purpose**: The Layout Architect is the first specialist agent in Deckster's multi-agent architecture, responsible for transforming content strategy into professional visual layouts. It processes the approved presentation strawman from Phase 1 and generates sophisticated layout specifications for each slide, applying proven design principles to ensure professional quality, readability, and visual impact.
- **Key Capabilities**: 
  - Presentation theme generation with layouts and typography
  - Professional design principle enforcement (white space, alignment, balance)
  - Strategic component highlighting for key insights
  - Functional minimalism for clarity and impact
  - Grid-based precision positioning
  - Progressive slide-by-slide delivery
- **Integration Context**: Acts as the bridge between Phase 1 (Director IN) and Phase 3 (specialist agents). Receives the approved strawman from State 5 and provides layout guidance to all Phase 3 agents (Researcher, Analyst, Visualizer, Diagrammer) before they begin their work.
- **Multiple Agents**: No - this analysis focuses solely on the Layout Architect agent

### Quick Reference Tables

#### Core Functions Overview
| Function | Purpose | Trigger | Output |
|----------|---------|---------|--------|
| Strawman Analysis | Understand presentation structure | Receives approved strawman | Layout strategy context |
| Theme Generation | Create visual design system | After strawman analysis | Complete theme spec |
| Layout Generation | Design individual slides | After theme generation | SlideLayoutSpec per slide |
| Message Delivery | Send layouts to Director OUT | Per slide completion | AgentMessage |

#### Performance Targets
| Metric | Target | Measurement |
|--------|--------|-------------|
| Layout Generation Speed | <2s per slide | 95th percentile |
| Concurrent Slides | Up to 30 | Simultaneous processing |
| Memory Usage | <50MB per session | Peak usage |
| White Space Ratio | 30-50% | Professional standard |
| Grid Alignment | 100% | All elements aligned |
| Balance Score | >90% | Visual equilibrium |
| Error Rate | <1% | Layout generation failures |

#### Slide Types & Strategies
| Slide Type | Structure Options | Primary Use Case |
|------------|------------------|------------------|
| title_slide | Full-Bleed, Single Focal, Two-Column | Opening/section starts |
| content_heavy | Columnar, Two-Column, Single Focal | Text-focused content |
| data_driven | Grid, Two-Column, Single Focal | Charts and metrics |
| visual_heavy | Full-Bleed, Grid Gallery, Two-Column | Image-focused |
| diagram_focused | Single Focal, Two-Column, Full-Bleed | Process flows |
| mixed_content | Grid, Two-Column, Single Focal | Balanced content |
| conclusion_slide | Single Focal, Two-Column, Full-Bleed | CTAs and summaries |

## Product Concept Analysis
### Original Requirements
The Phase 2 plan establishes the Layout Architect as the inaugural specialist agent, introducing:
- Sequential execution after strawman approval (State 5) from Phase 1
- Acts as prerequisite for all Phase 3 agents to begin their work
- Slide-by-slide content processing and delivery
- Integration with existing theme system
- Custom container generation for complex layouts
- Layout variety tracking to avoid repetition
- Progressive enhancement model where slides improve as more agents contribute

### Assumptions Made
1. The existing theme system provides a set of predefined layouts (e.g., titleSlide, contentSlide, dataSlide)
2. Grid-based positioning system uses 160x90 units for responsive design
3. Frontend can handle progressive updates to individual slides
4. Layout decisions should consider content density and visual hierarchy
5. The agent needs to maintain context awareness across the entire presentation for consistency
6. Phase 1 delivers a complete, user-approved strawman with all slide content and metadata
7. Phase 3 agents depend on Layout Architect's output to guide their content generation

## Phase 1 Integration

### Workflow Continuation from Director IN

The Layout Architect represents the seamless transition from Phase 1's strategic planning to Phase 2's visual execution. This integration ensures continuity in the presentation development process.

#### State 5 Handoff Mechanism
- **Trigger Point**: User approves the strawman in State 5 (REFINE_STRAWMAN)
- **Handoff Data**: Complete PresentationStrawman object containing:
  - Main title and overall theme
  - Target audience and presentation duration
  - Complete slide array with:
    - Slide IDs, titles, and types
    - Content briefs (key_points, analytics_needed, visuals_needed, diagrams_needed)
    - Structure preferences from Director
    - Narrative flow and speaker notes
- **Validation**: Layout Architect verifies strawman completeness before processing
- **Acknowledgment**: Sends confirmation to Director IN that handoff is complete

#### Data Transformation Pipeline
1. **Strawman Reception**: 
   - Receives the approved PresentationStrawman via standardized message protocol
   - Validates all required fields are present
   - Extracts presentation metadata for theme generation

2. **Context Preservation**:
   - Maintains all strategic decisions from Director IN
   - Preserves content briefs for Phase 3 agent guidance
   - Retains audience and formality specifications

3. **Enhancement Layer**:
   - Adds visual specifications without altering content strategy
   - Augments each slide with layout and container definitions
   - Preserves original briefs for downstream agents

#### Session State Management
- **Phase Transition**: Session state updates from "strawman_approved" to "layout_processing"
- **Data Persistence**: Original strawman stored for reference by Phase 3 agents
- **Progress Tracking**: Layout Architect updates session with processing status per slide

## Phase 3 Agent Guidance

### Layout as Foundation for Specialist Agents

The Layout Architect's output serves as the visual framework that guides all Phase 3 agents in their content generation. Each agent receives both the original content briefs from the strawman AND the layout specifications to ensure their outputs fit perfectly within the designed containers.

#### Researcher Agent Guidance
- **Container Specifications**: Provides exact dimensions and capacity for text content
- **Typography Directives**: Specifies font hierarchy for different content types
- **Content Volume Limits**: Character counts based on container sizes
- **Layout Context**: Indicates whether content is primary, secondary, or supporting

Example guidance:
```json
{
  "slide_id": "slide_003",
  "research_containers": [
    {
      "container_id": "main-point-1",
      "max_characters": 120,
      "typography": "h2",
      "role": "key_takeaway"
    },
    {
      "container_id": "supporting-text",
      "max_characters": 300,
      "typography": "body",
      "role": "explanation"
    }
  ]
}
```

#### Data Analyst Agent Guidance
- **Chart Containers**: Exact dimensions for data visualizations
- **Aspect Ratios**: Optimal proportions for different chart types
- **Label Space**: Reserved areas for titles, legends, and annotations
- **Color Palette**: Theme colors for consistent visualization

Example guidance:
```json
{
  "slide_id": "slide_005",
  "data_containers": [
    {
      "container_id": "main-chart",
      "dimensions": { "width": 80, "height": 50 },
      "chart_type_hint": "bar_chart",
      "color_sequence": ["#0066cc", "#00aa44", "#ff6600"],
      "label_zones": {
        "title": { "height": 5 },
        "legend": { "width": 20 },
        "axis": { "bottom": 5, "left": 10 }
      }
    }
  ]
}
```

#### Visual Designer Agent Guidance
- **Image Containers**: Precise dimensions and aspect ratios
- **Visual Hierarchy**: Z-index and prominence indicators
- **Style Consistency**: Theme-based visual treatments
- **Placement Context**: Relationship to other elements

Example guidance:
```json
{
  "slide_id": "slide_007",
  "visual_containers": [
    {
      "container_id": "hero-image",
      "dimensions": { "width": 100, "height": 60 },
      "aspect_ratio": "16:9",
      "visual_style": "full-bleed",
      "z_index": 2,
      "overlay_safe_zones": [
        { "x": 10, "y": 10, "width": 40, "height": 20 }
      ]
    }
  ]
}
```

#### UX Analyst (Diagrammer) Agent Guidance
- **Diagram Space**: Container dimensions for process flows and frameworks
- **Connection Zones**: Areas reserved for arrows and relationships
- **Node Sizing**: Consistent dimensions for diagram elements
- **Flow Direction**: Horizontal vs vertical layout preferences

Example guidance:
```json
{
  "slide_id": "slide_009",
  "diagram_containers": [
    {
      "container_id": "process-flow",
      "dimensions": { "width": 120, "height": 55 },
      "flow_direction": "horizontal",
      "node_size": { "width": 25, "height": 15 },
      "connection_style": "arrows",
      "max_nodes": 4
    }
  ]
}
```

### Coordination Protocol

#### Message Format for Agent Coordination
```typescript
interface LayoutGuidanceMessage {
  source: "layout_architect";
  target_agent: "researcher" | "analyst" | "visualizer" | "diagrammer";
  slide_id: string;
  layout_name: string;
  containers: Array<{
    id: string;
    type: string;
    dimensions: { width: number; height: number; };
    position: { x: number; y: number; };
    constraints: Record<string, any>;
    content_ref: string; // References original strawman brief
  }>;
  theme_context: {
    typography: Record<string, TypographySpec>;
    colors: Record<string, string>;
    style_guidelines: string[];
  };
}
```

#### Synchronization Points
1. **Layout Completion**: Layout Architect signals completion for each slide
2. **Agent Activation**: Phase 3 agents receive activation signal with layout guidance
3. **Content Fitting**: Agents validate their content fits within provided containers
4. **Error Handling**: Agents can request layout adjustments if content doesn't fit

## Professional Design Principles

The Layout Architect implements five critical design principles that ensure every presentation meets the highest professional standards. These principles are applied systematically throughout the layout generation process.

### 1. White Space (Negative Space)

**What it is**: White space is the empty, unmarked space on a slide - including margins, gutters between elements, and spacing between lines. It's an active design element, not "empty" space.

**Why it matters**:
- **Reduces Cognitive Load**: Prevents visual overwhelm, making content easier to scan and digest
- **Creates Focus**: Isolates important elements to naturally draw the viewer's eye
- **Improves Readability**: Proper spacing between text lines and paragraphs enhances legibility
- **Signals Professionalism**: Spacious layouts convey confidence, clarity, and authority

**Implementation**:
- **Generous Margins**: Minimum 8 grid units on all edges, no content touches slide boundaries
- **Consistent Gutters**: 4 grid units between columns, charts, and text boxes
- **Deliberate Spacing**: Consistent distances between title/body (6 GU) and body/footer (4 GU)
- **White Space Ratio**: Target 30-50% of slide area as white space

### 2. Alignment to Grids

**What it is**: The practice of placing every element precisely on the 160×90 integer grid unit system, ensuring all positions and dimensions use whole numbers only.

**Why it matters**:
- **Creates Order**: Brings immediate sense of structure and intentionality
- **Enhances Readability**: Eyes follow clean, predictable paths through information
- **Ensures Professionalism**: Perfect alignment is a hallmark of professional design
- **Frontend Compatibility**: Integer-only positioning ensures pixel-perfect rendering

**Implementation**:
- **160×90 Grid System**: All elements positioned using integer grid units only (no fractional values)
- **Row/Column Alignment**: Similar elements align to the same rows and columns
  - Example: Three text columns with subheadings all start at the same Y position
  - All subheadings have identical widths and heights
  - Content below each subheading matches the width of its heading
- **Consistent Dimensions**: Related elements share the same dimensions
  - All columns in a set have equal widths
  - Similar content blocks maintain consistent heights
- **Grid Snapping**: All X and Y coordinates must be integers (0-160 for X, 0-90 for Y)
- **Edge Alignment**: Elements sharing a logical relationship must share edge coordinates
  - Left edges of related elements align to the same X coordinate
  - Top edges of elements in the same row share the same Y coordinate

### 3. Balance

**What it is**: The deliberate distribution of visual weight to create stability and equilibrium. Visual weight is determined by size, color darkness, and content density.

**Why it matters**:
- **Visual Harmony**: Balanced slides feel calm and pleasing
- **Effortless Processing**: Well-balanced layouts function efficiently
- **Professional Appearance**: Prevents amateur-looking lopsided designs

**Implementation**:
- **Asymmetrical Balance**: Large elements (charts) balanced by smaller elements plus white space
- **Symmetrical Balance**: For formal slides - mirrored elements across central axis
- **Visual Weight Calculation**: Algorithm considers size, color intensity, and density
- **White Space as Balance**: Empty areas act as counterweight to heavy elements

### 4. Highlighting Important Components

**What it is**: Strategic use of visual contrast to guide attention to the most important information - the key insight that proves the slide's action title.

**Why it matters**:
- **Directs Focus Instantly**: Executives immediately see key evidence
- **Tells the Story Faster**: Transforms neutral data into clear evidence
- **Supports Decision Making**: Makes critical information unmissable

**Implementation**:
- **Call-Out Color**: Muted colors (greys) for context, bright accent color for key data
- **Weight and Size**: Bold or larger formatting for critical numbers
- **Isolation**: Extra white space frames important components
- **Simple Annotations**: Minimal arrows/circles with short labels (e.g., "+15%")

### 5. Functional Minimalism

**What it is**: A philosophy where every element must serve a clear functional purpose. If an element is purely decorative, it's removed.

**Why it matters**:
- **Maximizes Signal-to-Noise**: Removes visual noise, strengthens core message
- **Respects the Audience**: Assumes intelligent viewers who value clarity over decoration
- **Increases Impact**: Clean designs have more authority and credibility

**Implementation**:
- **No Chartjunk**: Remove unnecessary gridlines, 3D effects, shadows, heavy borders
- **No Decorative Images**: Only use images that ARE the data (e.g., product photos)
- **Concise Language**: Edit text to essential meaning only
- **Simple Forms**: Basic shapes, clean lines, standard sans-serif fonts

### Design Principle Integration

These principles work together throughout the layout generation pipeline:

1. **Theme Generation**: Establishes white space standards and grid system
2. **Container Analysis**: Applies functional minimalism to identify essential elements
3. **Layout Selection**: Chooses arrangements that ensure balance
4. **Grid Positioning**: Enforces strict alignment and optimal white space
5. **Visual Treatment**: Implements highlighting for key components
6. **Validation**: Verifies all principles are satisfied

The Layout Architect's success is measured not by variety, but by consistent application of these professional design principles across every slide.

## Detailed Functional Specification

### Primary Functions

#### 1. **Strawman Layout Analysis**
   - Purpose: Analyze the entire presentation strawman to understand content structure and flow
   - Trigger: Receives approved strawman from State 5 (REFINE_STRAWMAN)
   - Input Requirements:
     - Data: PresentationStrawman object with all slides
     - Format: JSON structure with slide array
     - Validation: Must contain valid slide IDs and content
   - Processing Steps:
     - Step 1: Parse strawman structure and extract metadata
     - Step 2: Analyze presentation type and target audience
     - Step 3: Identify content patterns across slides
     - Step 4: Create presentation-wide layout strategy
   - Output Specification:
     - Data: Layout strategy context for consistent processing
     - Format: Internal state object
   - Success Criteria: Complete analysis within 2 seconds
   - Error Scenarios: Invalid strawman structure, missing required fields
   - Dependencies: Valid strawman from Director agent

#### 2. **Presentation Theme Generation**
   - Purpose: Generate a comprehensive presentation theme including layouts, typography system, and color palette based on the analyzed strawman content and user preferences
   - Trigger: After strawman layout analysis completes
   - Input Requirements:
     - Data: Analyzed presentation context, metadata, and content patterns
     - Format: Layout strategy and insights from strawman analysis
     - Validation: Valid analysis results, user preferences, and any brand guidelines
   - Processing Steps:
     - Step 1: **Context Application** - Leverage analyzed presentation purpose, audience profile, and content requirements
     - Step 2: **Style Determination** - Establish appropriate formality level, visual tone, and design language based on context
     - Step 3: **Layout Generation** - Create distinct layouts for each slide type:
       - **Title Slide**: Complete layout with all containers fully specified
       - **Section Divider Slides**: Full transitional layouts for chapter breaks
       - **Content Slides**: Define only header and footer zones, leaving body area flexible for dynamic content
     - Step 4: **Typography System Design**: Create comprehensive typography hierarchy (see Typography Specification Table in Appendix E)
     - Step 5: **Color Palette Creation**:
       - **Text Colors**: Primary text, secondary text, accent text, muted text
       - **Background Colors**: Main background, alternate background, overlay backgrounds
       - **UI Elements**: Border colors, divider lines, shadows, highlights
       - **Data Visualization**: Chart colors (6-8 color sequence), gradients for emphasis
       - **Semantic Colors**: Success (#green), warning (#yellow), error (#red), info (#blue)
       - **Brand Integration**: Incorporate brand colors if provided
     - Step 6: **Container Specifications**:
       - **Content Slide Framework**:
         - Header Zone: Grid coordinates for title, subtitle, logos (maximize elegance, minimize height)
         - Footer Zone: Coordinates for slide numbers, date, presentation name, branding elements
         - Body Zone: Maximum available space (x, y, width, height) optimized for content flexibility
       - **Title Slide Layout**:
         - Title Container: Centered or aligned positioning with prominent sizing
         - Subtitle Container: Supporting text placement
         - Author/Organization Containers: Attribution zones
         - Visual Element Zones: Logo placement, decorative elements
         - All with precise grid coordinates, dimensions, z-index layering
       - **Section Divider Layout**:
         - Section Title Container: Prominent positioning for chapter names
         - Section Number Container: Optional numbering display
         - Progress Indicator Zone: Visual progress representation
         - Decorative Element Zones: Separators or visual breaks
   - Output Specification:
     - Data: Complete theme specification package
     - Format: Structured JSON containing:
       ```json
       {
         "themeName": "string",
         "layouts": {
           "titleSlide": { /* complete layout spec */ },
           "contentSlide": { /* header/footer/body zones */ },
           "sectionDivider": { /* complete layout spec */ }
         },
         "typography": { /* complete font hierarchy */ },
         "colors": { /* comprehensive color system */ },
         "gridSpecifications": { /* container coordinates */ }
       }
       ```
   - Success Criteria: 
     - All slide types have appropriate layouts
     - Typography hierarchy is readable and balanced
     - Color palette is cohesive and accessible (WCAG AA compliant)
     - Content zones maximize available space while maintaining elegance
   - Error Scenarios: 
     - Style conflicts between formality and brand requirements
     - Insufficient contrast in color selections
     - Font availability issues
     - Grid constraint violations
   - Dependencies: Completed strawman analysis, user preferences, grid system (160x90)

#### 3. **Slide-by-Slide Layout Generation**
   - Purpose: Generate optimal layout specifications for individual slides through intelligent content analysis and adaptive container positioning
   - Trigger: Concurrent processing after theme generation completes
   - Input Requirements:
     - Data: Individual slide content, metadata, and generated theme
     - Format: Slide object with type, content structure, and contextual purpose
     - Validation: Valid slide type, content structure, and theme availability
   - Processing Steps:

     **Stage 1: Initial Layout Type Determination**
     - **Input**: Slide object with type indicator (titleSlide, sectionDivider, contentSlide)
     - **Process**: 
       - For title slides and section dividers: Apply complete pre-defined theme layouts
       - For content slides: Use only header/footer from theme, proceed to container generation
     - **Output**: Layout strategy decision (theme-complete or custom-body-required)

     **Stage 2: Content Decomposition and Analysis**
     - **Input**: Slide content object with all text, data, and visual elements
     - **Process**:
       - Break down content into logical containers using the Content Type Registry (see Appendix F)
       - Identify container types: Text, Data, Code, Media, Interactive, Structural, and Decorative elements
       - Identify special content requirements:
         - **Tables**: Preserve row/column structure, apply theme-based cell styling, header emphasis
         - **Code Blocks**: Require monospace font, syntax highlighting, adequate line height
         - **Icons**: Scale based on importance, apply theme colors dynamically
         - **Shapes**: Support fill/stroke/opacity from theme, proper layering
         - **Charts**: Adequate space for labels, legends, and axis titles
         - **Videos**: Control overlay space, aspect ratio preservation
         - **CTAs**: Prominence through size, color, and spacing
       - Determine container relationships and hierarchies
       - Consider z-index requirements early:
         - Background elements (patterns, watermarks): z-index 1
         - Main content layers: z-index 2-5
         - Interactive overlays: z-index 6-8
         - Modal/popup elements: z-index 9-10
     - **Output**: Container manifest JSON:
       ```json
       {
         "containers": [
           {
             "id": "main-point-1",
             "type": "text",
             "content": "...",
             "hierarchy": "primary",
             "zIndex": 2,
             "estimatedSize": "large"
           }
         ]
       }
       ```
     
     **Stage 3: Content Representation Strategy**
     - **Input**: Container manifest from Stage 2 + slide type/structure from strawman
     - **Process**:
       - Apply semantic mapping based on content type and slide context
       - Select appropriate layout pattern from Slide Type Strategy Matrix (see Appendix G)
       - Assign typography levels and visual treatments
       - Determine container sizing based on content volume and importance
     - **Output**: Enhanced container manifest with visual treatments:
       ```json
       {
         "containers": [
           {
             "id": "main-point-1",
             "visualTreatment": "keyTakeaway",
             "typography": "h2",
             "spaceAllocation": 0.4,
             "priority": 1
           }
         ]
       }
       ```

     **Stage 4: Grid Positioning with Professional Design Principles**
     - **Input**: Enhanced container manifest with visual treatments and theme body zone coordinates
     - **Process**:
       - **White Space Implementation**: 
         - Calculate total slide area: 160×90 = 14,400 GU²
         - Target white space: 30-50% (4,320-7,200 GU²)
         - Enforce generous margins: 8 GU minimum on all edges
         - Apply consistent gutters: 4 GU between all sibling containers
         - Create breathing room: 6 GU between title and body, 4 GU between body and footer
       - **Grid Alignment Enforcement**:
         - Use 160×90 integer grid system directly
         - All positions must be whole numbers (no decimals)
         - Group similar elements into aligned rows and columns
         - Ensure consistent dimensions for related elements:
           - Same width for all columns in a set
           - Same height for all subheadings in a row
           - Content width matches its heading width
         - Snap all edges to integer coordinates
         - Validate no fractional positions exist
       - **Balance Calculation**:
         - Calculate visual weight: size × color_intensity × content_density
         - For asymmetrical layouts: balance chart (weight=high) with text (weight=medium) + white space
         - For symmetrical layouts: mirror elements across vertical center (x=80)
         - Include white space as active balancing element
         - Validate balance score: must exceed 90% threshold
       - **Component Highlighting**:
         - Identify key insight container from content hierarchy
         - Apply isolation: add +2 GU white space around key element
         - Reserve accent color for single most important data point
         - Size emphasis: key metric 1.2-1.5x larger than supporting data
         - Position prominence: place key insight at optical center or Rule of Thirds intersection
       - **Functional Minimalism Validation**:
         - Remove any purely decorative containers
         - Simplify complex shapes to basic forms
         - Eliminate redundant visual elements
         - Ensure every container serves clear functional purpose
         - Verify clean, uncluttered final layout
       - **Z-Index Layering** (simplified for minimalism):
         - Background (if functional): z-index 1
         - Main content: z-index 2-3
         - Key highlights: z-index 4
         - Critical callouts only: z-index 5
     - **Output**: Positioned container specifications:
       ```json
       {
         "containers": [
           {
             "id": "main-point-1",
             "position": { "x": 12, "y": 20, "width": 136, "height": 8 },
             "zIndex": 3
           }
         ]
       }
       ```

     **Stage 5: Precise Sizing and Capacity Validation**
     - **Input**: Positioned containers with dimensions
     - **Process**:
       - **Text Capacity Calculation**:
         - Characters per line = (width - padding) × chars_per_grid_unit
         - Total lines = (height - padding) / line_height
         - Total capacity = characters_per_line × total_lines
       - **Visual Element Validation**:
         - Charts: Minimum 40×25 GU for readability
         - Images: Aspect ratio preservation within bounds
         - Icons: Standard sizes (4×4, 6×6, 8×8 GU)
       - **Overflow Detection**: Flag containers needing content adjustment
     - **Output**: Validated container specifications with capacity limits:
       ```json
       {
         "containers": [
           {
             "id": "main-point-1",
             "maxCharacters": 120,
             "currentCharacters": 95,
             "overflowStatus": "ok"
           }
         ]
       }
       ```

     **Stage 6: Design Principle Validation and Optimization**
     - **Input**: Complete layout specification with positioned containers
     - **Process**:
       - **White Space Validation**:
         - Calculate actual white space ratio
         - Verify minimum margins (8 GU) maintained
         - Check gutter consistency (4 GU)
         - Ensure 30-50% white space target achieved
       - **Alignment Verification**:
         - Confirm all positions use integer coordinates
         - Validate similar elements share row/column positions
         - Check width/height consistency for related elements
         - Verify content aligns with its headers
         - Flag any fractional coordinates
       - **Balance Assessment**:
         - Calculate final visual weight distribution
         - Verify balance score exceeds 90% threshold
         - Check symmetry for formal slides
         - Validate white space as active balance element
       - **Highlighting Effectiveness**:
         - Confirm single focal point identified
         - Verify isolation spacing applied
         - Check accent color limited to key insight
         - Validate size/position prominence
       - **Minimalism Compliance**:
         - Ensure no decorative elements remain
         - Verify all containers have functional purpose
         - Check for clean, simple forms
         - Validate removal of visual clutter
     - **Output**: Design principle validation report:
       ```json
       {
         "layoutId": "content-slide-7",
         "principleScores": {
           "whiteSpace": 0.95,
           "gridAlignment": 1.0,
           "balance": 0.92,
           "highlighting": 0.88,
           "minimalism": 0.96
         },
         "overallScore": 0.94,
         "violations": []
       }
       ```

     **Stage 7: Final Layout Assembly and Validation**
     - **Input**: All container specifications and theme references
     - **Process**:
       - Merge theme header/footer with custom body containers
       - Apply final visual polish (shadows, borders)
       - Validate all grid constraints
       - Generate rendering hints for frontend
     - **Output**: Complete SlideLayoutSpec ready for delivery

   - Output Specification:
     - Data: Complete SlideLayoutSpec with all container definitions
     - Format: 
       ```json
       {
         "slideId": "string",
         "layoutSource": "theme|custom",
         "layoutName": "string",
         "containers": [
           {
             "id": "string",
             "type": "text|image|chart|shape",
             "position": { "x": 0, "y": 0, "width": 0, "height": 0 },
             "content": { /* content spec */ },
             "styling": { /* visual properties */ },
             "zIndex": 1
           }
         ],
         "layoutHints": { /* rendering guidance */ },
         "varietyScore": 0.85
       }
       ```
   - Success Criteria: 
     - Layout generation <2s per slide
     - All containers fit within grid bounds
     - Text capacity accurately calculated
     - Variety score >80% across presentation
   - Error Scenarios: 
     - Content overflow beyond grid capacity
     - Irreconcilable positioning conflicts
     - No viable layout solution found
     - Text truncation required
   - Dependencies: 
     - Generated theme configuration
     - Layout history for variety tracking
     - Grid system constraints
     - Typography specifications

#### 4. **Progressive Message Delivery**
   - Purpose: Send completed layouts to Director OUT immediately
   - Trigger: Completion of each slide's layout processing
   - Input Requirements:
     - Data: Completed SlideLayoutSpec
     - Format: AgentMessage protocol
     - Validation: Valid slide ID and layout data
   - Processing Steps:
     - Step 1: Package layout data in AgentMessage
     - Step 2: Set completion status
     - Step 3: Add timestamp
     - Step 4: Send to message queue
   - Output Specification:
     - Data: AgentMessage with layout payload
     - Format: Standardized message format
   - Success Criteria: Immediate delivery upon completion
   - Error Scenarios: Message queue unavailable
   - Dependencies: Message queue infrastructure

### Supporting Functions

#### 1. **Theme Style Determination**
   - Purpose: Determine appropriate theme style based on presentation context
   - Trigger: Part of theme generation process
   - Input Requirements:
     - Data: Presentation type, audience, formality level
     - Format: Metadata from strawman
     - Validation: Valid presentation metadata
   - Processing Steps:
     - Step 1: Map presentation type to style categories
     - Step 2: Adjust for audience expectations
     - Step 3: Apply formality constraints
     - Step 4: Select base theme template
   - Output Specification:
     - Data: Theme style parameters
     - Format: Style configuration object
   - Success Criteria: Coherent style selection
   - Error Scenarios: Conflicting style requirements
   - Dependencies: Style templates library

#### 2. **Content Density Analysis**
   - Purpose: Evaluate the amount and complexity of slide content
   - Trigger: Part of layout generation process
   - Input Requirements:
     - Data: Slide content object
     - Format: Structured content with text, data, lists
     - Validation: Non-empty content
   - Processing Steps:
     - Step 1: Count content elements
     - Step 2: Calculate text volume
     - Step 3: Assess data complexity
     - Step 4: Determine density score
   - Output Specification:
     - Data: Content density metric
     - Format: Enum (high, medium, low)
   - Success Criteria: Accurate density assessment
   - Error Scenarios: Unrecognized content types
   - Dependencies: Content parsing utilities

#### 3. **Visual Hierarchy Determination**
   - Purpose: Establish the visual importance of content elements
   - Trigger: During layout specification
   - Input Requirements:
     - Data: Content structure and emphasis markers
     - Format: Hierarchical content tree
     - Validation: Valid content relationships
   - Processing Steps:
     - Step 1: Identify primary vs secondary content
     - Step 2: Determine reading flow
     - Step 3: Assign visual weights
     - Step 4: Map to layout positions
   - Output Specification:
     - Data: Hierarchy specification
     - Format: Weighted content map
   - Success Criteria: Clear visual priorities
   - Error Scenarios: Ambiguous content hierarchy
   - Dependencies: Content analysis

#### 4. **Layout Hint Generation**
   - Purpose: Provide rendering guidance to frontend
   - Trigger: Final step of layout specification
   - Input Requirements:
     - Data: Layout choice and content characteristics
     - Format: Layout context
     - Validation: Complete layout specification
   - Processing Steps:
     - Step 1: Analyze layout requirements
     - Step 2: Set visual emphasis level
     - Step 3: Determine spacing preferences
     - Step 4: Configure color intensity
   - Output Specification:
     - Data: LayoutHints object
     - Format: JSON with rendering preferences
   - Success Criteria: Actionable hints for frontend
   - Error Scenarios: Conflicting hint requirements
   - Dependencies: Frontend rendering capabilities

### User Interaction Flows

#### 1. **Standard Strawman Processing Flow**
   - Entry Point: Strawman approved by user in State 5
   - Steps: 
     1. Receive complete strawman
     2. Analyze presentation context
     3. Generate presentation theme (layouts, typography, colors)
     4. Process slides concurrently using generated theme
     5. Send layouts progressively
   - Decision Points: Theme layout vs custom container generation per slide
   - Exit Points: All slides processed and sent

#### 2. **Layout Refinement Flow**
   - Entry Point: User requests layout changes
   - Steps:
     1. Receive specific slide feedback
     2. Re-analyze slide requirements
     3. Generate alternative layout
     4. Send updated specification
   - Decision Points: Constraint satisfaction
   - Exit Points: User accepts new layout

#### 3. **Error Recovery Flow**
   - Entry Point: Layout generation failure
   - Steps:
     1. Log error details
     2. Apply fallback layout
     3. Send error message
     4. Continue with next slide
   - Decision Points: Fallback appropriateness
   - Exit Points: Error handled gracefully

## System Architecture

### Memory Requirements

### Working Memory (Session-based)
- **Presentation Context**: Theme preferences, target audience, formality level - needed throughout processing
- **Layout History**: Array of previous slide layouts - maintained for variety tracking
- **Processing State**: Current slide being processed, completion status - temporary during execution
- **Error Log**: Failed layout attempts - kept for session debugging

### Persistent Memory (Database)
- **Successful Layout Patterns**: Effective layout choices by content type - stored in layout_patterns table
- **Layout Templates**: Custom container configurations that worked well - stored in layout_templates table
- **Performance Metrics**: Processing times and success rates - stored for optimization

### Context Requirements
- **Strawman Analysis**: Full presentation context including metadata
- **Theme Configuration**: Available layouts and their specifications
- **User Preferences**: Visual density, formality, color preferences
- **Previous Layouts**: Last 5-10 slide layouts for variety

### Integration Requirements

### System Integration Points
- **Director IN (Phase 1)**: Receives approved strawman after State 5 completion
- **Director OUT Assembler**: Sends completed layouts via message queue
- **Theme Generation**: Creates custom theme based on presentation context
- **Frontend Renderer**: Provides theme and layout specs compatible with rendering engine
- **Phase 3 Agents**: Provides layout guidance and container specifications to:
  - **Researcher**: Text container capacities and typography specs
  - **Data Analyst**: Chart dimensions and visualization constraints
  - **Visual Designer**: Image containers and visual hierarchy
  - **UX Analyst (Diagrammer)**: Diagram space and flow specifications

### Data Flow
```markdown
### Data Flow Analysis

### Input Sources
1. **Presentation Strawman**: Complete slide structure from Director IN (Phase 1)
2. **User Preferences**: Visual and style preferences from session
3. **Presentation Metadata**: Type, audience, formality level
4. **Phase 1 Context**: Strategic decisions and content briefs from States 1-5

### Processing Pipeline
1. **Phase 1 Handoff**: Receive approved strawman from State 5
2. **Strawman Reception**: Validate and parse presentation structure
3. **Context Analysis**: Extract metadata and preferences
4. **Theme Generation**: Create complete theme with layouts, typography, colors
5. **Concurrent Processing**: Process slides in parallel using generated theme
6. **Layout Generation**: Create specifications per slide
7. **Quality Validation**: Ensure grid constraints and variety
8. **Progressive Delivery**: Send completed layouts immediately
9. **Phase 3 Preparation**: Package layout guidance for specialist agents

### Output Destinations
1. **Message Queue**: AgentMessage objects to Director OUT
2. **Session Storage**: Layout history for variety tracking
3. **Pattern Database**: Successful layouts for learning
4. **Phase 3 Agents**: Layout guidance messages containing:
   - Container specifications and dimensions
   - Typography and color directives
   - Content capacity limits
   - Visual hierarchy guidelines
```

## Technical Specifications

### New WebSocket Messages
```typescript
// Theme generation complete message
interface ThemeGenerated {
  type: "theme_generated";
  session_id: string;
  theme: {
    name: string;
    layouts: {
      titleSlide: LayoutDefinition;
      contentSlide: LayoutDefinition;
      sectionHeader: LayoutDefinition;
      dataSlide: LayoutDefinition;
      [key: string]: LayoutDefinition;
    };
    typography: {
      h1: TypographySpec;
      h2: TypographySpec;
      h3: TypographySpec;
      body: TypographySpec;
      caption: TypographySpec;
    };
    colors: {
      background: string;
      primary: string;
      secondary: string;
      accent: string;
      [key: string]: string;
    };
  };
  timestamp: string;
}

// Layout-specific update message
interface LayoutUpdate {
  type: "layout_update";
  session_id: string;
  slide_id: string;
  layout: string;
  layout_spec: {
    source: "theme" | "custom";
    theme_layout?: string;
    custom_containers?: ContainerSpec[];
    layout_hints: LayoutHints;
  };
  processing_status: "complete" | "error";
  timestamp: string;
}
```

### Memory Architecture Analysis

### Current Supabase Schema
The current schema includes:
- **sessions table**: Stores user sessions with conversation history and state
- **presentations table**: Stores completed presentations with embeddings
- **visual_assets table**: Stores generated images and graphics
- **agent_outputs table**: Tracks all agent responses with timing and status

### Agent Memory Requirements
The Layout Architect needs:
1. **Working Memory**: 
   - Current strawman being processed
   - Layout history for variety tracking
   - Processing queue for concurrent slides
   - Theme configuration cache

2. **Persistent Memory**:
   - Successful layout patterns by content type
   - Custom container templates
   - Performance metrics

### Database Schema Extensions

```sql
-- Session state extension
ALTER TABLE sessions ADD COLUMN layout_architect_state JSONB DEFAULT '{
  "layout_history": [],
  "processing_queue": [],
  "variety_score": 0,
  "generated_theme": null
}'::JSONB;

-- Layout patterns for learning
CREATE TABLE layout_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name TEXT NOT NULL,
    content_type TEXT NOT NULL,
    layout_spec JSONB NOT NULL,
    effectiveness_score FLOAT DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Custom layout templates
CREATE TABLE layout_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name TEXT NOT NULL,
    container_spec JSONB NOT NULL,
    content_characteristics JSONB NOT NULL,
    theme_compatibility TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated themes storage
CREATE TABLE presentation_themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT REFERENCES sessions(id),
    theme_name TEXT NOT NULL,
    theme_spec JSONB NOT NULL,
    presentation_type TEXT,
    audience_type TEXT,
    formality_level TEXT,
    effectiveness_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_layout_patterns_content_type ON layout_patterns(content_type);
CREATE INDEX idx_layout_patterns_score ON layout_patterns(effectiveness_score DESC);
CREATE INDEX idx_layout_templates_name ON layout_templates(template_name);
CREATE INDEX idx_themes_session ON presentation_themes(session_id);
```

### Technical Requirements

### Performance
- **Layout Generation Speed**: <2 seconds per slide
- **Concurrent Processing**: Handle up to 30 slides simultaneously  
- **Memory Usage**: <50MB per session
- **Message Queue Latency**: <100ms per message

### Scalability
- **Expected Load**: 100+ concurrent sessions
- **Growth Projections**: 10x growth in 6 months
- **Resource Constraints**: Single process per session
- **Caching Strategy**: Theme layouts cached in memory

### Security
- **Data Sensitivity**: Low - layout specs are non-sensitive
- **Access Controls**: User can only access own session layouts
- **Validation**: All grid positions must be within bounds
- **Sanitization**: Container names and IDs sanitized

### Success Metrics

### Functional Metrics
- **Layout Generation**: 100% of slides receive valid layouts
- **Theme Mapping**: 95% success rate for standard slides
- **Custom Generation**: <5% failure rate for complex content
- **Design Principle Adherence**: >90% compliance across all 5 principles

### Performance Metrics
- **Response Time**: 95th percentile <2s per slide
- **Error Rate**: <1% layout generation failures
- **Queue Performance**: 99.9% message delivery success
- **Memory Efficiency**: <50MB peak usage per session

### Design Quality Metrics
- **White Space Ratio**: 30-50% achieved on 95% of slides
- **Grid Alignment**: 100% of elements properly aligned
- **Visual Balance**: >90% balance score on all layouts
- **Highlighting Effectiveness**: Key insights identified on 100% of data slides
- **Minimalism Score**: Zero decorative elements, 100% functional

### User Experience Metrics
- **Professional Quality**: Presentations rated "boardroom-ready"
- **Readability Score**: >95% content easily scannable
- **Time to Insight**: 50% faster identification of key messages
- **Executive Satisfaction**: Meets C-suite presentation standards

## Implementation Guidelines

### Modular Prompt System
The Layout Architect uses the ENHANCE_LAYOUT modular prompt which should:
- Understand theme constraints
- Balance variety with consistency  
- Consider content hierarchy
- Optimize for readability

### Concurrency Model
- Use asyncio for parallel slide processing
- Implement proper error isolation
- Maintain order for variety tracking
- Handle partial failures gracefully

### Frontend Compatibility
- Ensure layout specs match frontend grid system
- Provide clear rendering hints
- Support progressive enhancement
- Handle missing layout gracefully

### Learning System
- Track successful layout patterns
- Build content-to-layout mappings
- Improve selection over time
- A/B test layout effectiveness

## Next Steps
- Use this document as input for `/build-agent-architecture`
- Review theme layout compatibility
- Define custom container constraints
- Establish performance benchmarks

## Appendices

### A: Glossary
- **Container**: A positioned region on a slide that holds content
- **Grid Unit**: 1/160th of width or 1/90th of height
- **Layout Hints**: Rendering suggestions for the frontend
- **Theme Layout**: Predefined layout from the theme system
- **Variety Score**: Measure of layout diversity across slides
- **Typography Levels**: Hierarchical text styles (h1-h6, body, lead, metric, etc.)
- **Z-Index**: Layering order for overlapping elements (1-10 scale)
- **Gutter Space**: Minimum spacing between containers (standardized at 4 GU)
- **Content Density**: Measure of information volume per slide (high/medium/low)
- **Rule of Thirds**: Grid lines at x=53, x=107, y=30, y=60 for dynamic composition
- **Optical Center**: Slightly above geometric center for visual balance
- **Visual Weight**: Estimated prominence based on size, color, and content density
- **First-Class Object**: Content type with dedicated styling and behavior (e.g., tables, code blocks)
- **Semantic Type**: The meaning/purpose of content (e.g., KeyTakeaway, Quote, ProcessFlow)

### B: Referenced Documents
- Phase 2 Updated Plan
- WebSocket Protocol Specification
- Theme System Documentation
- Grid System Reference

### C: Open Questions
1. Should layout history persist across sessions for better personalization?
2. How many concurrent slides can we process without overwhelming the system?
3. What's the optimal variety score threshold?
4. Should we pre-generate common custom containers?

### D: Quick Reference - Container Sizing Guidelines

#### Standard Container Dimensions
| Content Volume | Width Range (GU) | Height Range (GU) | Example Use |
|---------------|------------------|------------------|-------------|
| Minimal | 20-40 | 5-10 | Labels, captions |
| Small | 40-60 | 10-20 | Bullet points, small charts |
| Medium | 60-80 | 20-40 | Body text, images |
| Large | 80-120 | 40-60 | Main content, hero visuals |
| Full Width | 140-160 | Variable | Headers, dividers |

#### Aspect Ratio Guidelines
| Content Type | Preferred Ratio | Alternative Ratios |
|--------------|-----------------|-------------------|
| Images | 16:9 | 4:3, 1:1, 3:2 |
| Charts | 4:3 | 16:9, 1:1 |
| Icons | 1:1 | N/A |
| Text Blocks | Golden (1.618:1) | 2:1, 3:2 |

**Note**: For detailed content type specifications, see:
- Appendix E: Typography Specification
- Appendix F: Content Type Registry
- Appendix G: Slide Type Strategy Matrix

### E: Typography Specification

#### Complete Typography Hierarchy

| Level | Purpose | Font Size | Weight | Line Height | Use Cases |
|-------|---------|-----------|--------|-------------|------------|
| **h1** | Main titles | 48-72pt (title) / 32-40pt (content) | 700-800 | 1.2 | Title slides, major sections |
| **h2** | Section headers | 36-48pt (title) / 24-32pt (content) | 600-700 | 1.3 | Section dividers, key points |
| **h3** | Subsection headers | 24-32pt | 600 | 1.4 | Slide titles, major content headers |
| **h4** | Minor headers | 20-24pt | 500-600 | 1.4 | Content sections, list headers |
| **h5** | Sub-subsections | 18-20pt | 500 | 1.5 | Tertiary headers |
| **h6** | Minor headers | 16-18pt | 500 | 1.5 | Small section breaks |
| **body** | Main content | 16-18pt | 400 | 1.6 | Paragraphs, descriptions |
| **lead** | Intro text | 20-22pt | 400 | 1.5 | Opening statements |
| **small** | Fine print | 12-14pt | 400 | 1.4 | Disclaimers, footnotes |
| **caption** | Image/chart labels | 14pt | 400 | 1.4 | Descriptions, sources |
| **footer** | Slide footers | 12pt | 400 | 1.3 | Page numbers, dates |
| **quote** | Quotations | 18-24pt | 400 italic | 1.6 | Testimonials, citations |
| **code** | Code snippets | 14-16pt | 400 mono | 1.4 | Technical content |
| **metric** | Large numbers | 60-96pt | 700 | 1.1 | KPIs, statistics |
| **label** | UI labels | 12-14pt | 500 | 1.3 | Chart labels, form fields |
| **overline** | Above headers | 12pt | 600 caps | 1.3 | Category labels |

#### Typography Properties

**Font Families**:
- Primary: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
- Monospace: "Fira Code", "Consolas", "Monaco", monospace
- Display: "Playfair Display" (optional for elegant themes)

**Color Variants per Level**:
- Default: Base color from theme
- Emphasized: 10% darker or accent color
- Muted: 40% opacity of base
- Interactive: Primary accent color with hover states

**Responsive Scaling**:
- Desktop: 100% of defined sizes
- Tablet: 90% of defined sizes
- Mobile: 85% of defined sizes
- Minimum sizes enforced for readability

### F: Content Type Registry

#### Text Elements
| Type | Description | Container Requirements | Typography |
|------|-------------|----------------------|------------|
| Headers | Section titles | Full width, prominent | h1-h6 based on level |
| Body Text | Main content | Variable width blocks | body |
| Bullet Lists | Itemized content | Indented, consistent spacing | body |
| Quotes | Testimonials/citations | Accent styling, padding | quote |
| Key Takeaways | Main insights | Wide, prominent | h2/lead |
| Footnotes | Annotations | Small, bottom placement | small |

#### Data Elements
| Type | Description | Special Requirements | Min Size (GU) |
|------|-------------|---------------------|---------------|
| Tables | Structured data | Row/column preservation, header styling | 60×10/row |
| Bar Charts | Comparative data | Label space, axis titles | 40×30 |
| Line Charts | Trends over time | Wide aspect for clarity | 50×30 |
| Pie Charts | Part-to-whole | Square aspect, legend | 35×35 |
| Metrics/KPIs | Key numbers | Large display font | 30×25 |
| Gauges | Progress/status | Circular layout | 30×30 |
| Timelines | Temporal data | Horizontal layout | 100×15 |
| Maps | Geographic data | Aspect ratio preservation | 60×40 |

#### Code Elements
| Type | Description | Styling Requirements | Typography |
|------|-------------|---------------------|------------|
| Code Blocks | Multi-line code | Syntax highlighting, dark background | code (mono) |
| Inline Code | Code in text | Background highlight | code (mono) |

#### Media Elements
| Type | Description | Format Support | Z-Index |
|------|-------------|---------------|----------|
| Images | Photos/graphics | JPG, PNG, WebP | 2-3 |
| Icons | UI elements | SVG with theme colors | 3-4 |
| Videos | Motion content | MP4, WebM with controls | 3-4 |
| GIFs | Animations | Looping animations | 3-4 |

#### Interactive Elements
| Type | Description | Behavior | Prominence |
|------|-------------|----------|------------|
| Primary CTA | Main actions | Hover states, prominent | High |
| Secondary CTA | Supporting actions | Subtle styling | Medium |
| Links | Text links | Underline/color | Low |
| QR Codes | External links | Static image | Medium |

#### Structural Elements
| Type | Description | Properties | Purpose |
|------|-------------|------------|----------|
| Shapes | Geometric elements | Fill, stroke, opacity | Emphasis/decoration |
| Dividers | Separators | Line style, color | Section breaks |
| Progress Bars | Status indicators | Fill percentage | Navigation |
| Containers | Layout boxes | Border, background | Organization |

#### Decorative Elements
| Type | Description | Z-Index | Opacity |
|------|-------------|---------|----------|
| Backgrounds | Patterns/gradients | 1 | 10-30% |
| Watermarks | Branding | 1 | 20-40% |
| Badges | Status/labels | 5-6 | 100% |
| Shadows | Depth effects | N/A | Variable |

### G: Slide Type Strategy Matrix

#### Semantic Content Mapping
| Content Purpose | Semantic Type | Visual Treatment | Default Size (GU) | Typography |
|----------------|---------------|------------------|-------------------|------------|
| Main point | KeyTakeaway | Wide, prominent, top position | 120×8 | h2/lead |
| Listed items | BulletedList | Standard box, consistent spacing | 60×30 | body |
| Quotation | Quote | Accent background, left padding | 80×20 | quote |
| Comparison | ComparisonFramework | Side-by-side tall containers | 40×50 each | body |
| Process | ProcessFlow | Horizontal with arrows | Variable | body |
| Statistics | KeyMetric | Large number, small label | 30×25 | metric |
| Clarification | Footnote | Small, bottom placement | 40×8 | small |
| Visualization | DataViz | Primary content block | 80×50 | label |
| Code | CodeBlock | Dark background, mono font | 100×40 | code |
| Data table | Table | Structured grid | Variable | body |

#### Slide Type Layout Strategies

**title_slide**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Full-Bleed Visual | Background image (160×90) + overlay | Title (100×20), subtitle (60×10) centered | Opening with impact |
| Single Focal Point | Centered elements | Title (60×20), subtitle (40×10), logo (20×20) | Clean, professional |
| Two-Column | Split visual/text | Left visual (80×70), right text (70×70) | Balanced introduction |

**content_heavy**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Columnar Text | 2-3 text columns | Columns (45×50 each) with 4 GU gutters | Dense information |
| Two-Column | Main + sidebar | Primary (90×60), secondary (50×60) | Key points + details |
| Single Focal | Large text block | Main content (120×50) centered | Single message focus |

**data_driven**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Grid Layout | 2×2 or 2×3 charts | Charts (45×35 each), insight callout center | Multiple metrics |
| Two-Column | Chart + analysis | Visualization (80×50), insights (55×50) | Data + interpretation |
| Single Focal | One major chart | Large viz (100×60), caption below | Single data story |

**visual_heavy**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Full-Bleed | Edge-to-edge image | Image (160×90), minimal text overlay | Maximum impact |
| Grid Gallery | Image grid | 3×3 grid (45×25 each) or 2×3 (70×35 each) | Multiple visuals |
| Two-Column | Image + description | Visual (95×65), text (55×65) | Visual storytelling |

**diagram_focused**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Single Focal | Central diagram | Diagram (120×55), legend/key below | Complex process |
| Two-Column | Diagram + steps | Visual (85×60), explanation (65×60) | Step-by-step guide |
| Full-Bleed | Full-screen flow | Diagram (140×70), floating annotations | Immersive explanation |

**mixed_content**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Grid Layout | Flexible 2×2 | Mixed containers (70×35 each) | Varied content types |
| Two-Column | Balanced split | 50/50 or 60/40 division | Equal importance |
| Single Focal | Hero + support | Main element (80×50), supporting ring | Clear hierarchy |

**conclusion_slide**
| Structure | Layout Pattern | Container Arrangement | Use When |
|-----------|---------------|---------------------|----------|
| Single Focal | CTA centered | Button (60×15), message above, contact below | Clear action |
| Two-Column | Summary + next | Summary (70×50), action items (70×50) | Recap + direction |
| Full-Bleed | Inspirational | Background image, CTA overlay (80×20) | Emotional close |

#### Container Sizing Guidelines
- **Minimum readable sizes**: Text (40×15), Charts (40×30), Images (30×20)
- **Optimal proportions**: Golden ratio (1.618:1) for rectangular containers
- **Gutter standards**: 4 GU minimum between siblings, 8 GU from slide edges
- **Z-index layers**: Background (1), Content (2-5), Overlays (6-8), Modals (9-10)

### H: Professional Design Principles Reference

#### Design Principle Application Matrix

| Principle | Measurement | Target | Implementation | Validation |
|-----------|------------|--------|----------------|------------|
| **White Space** | Area ratio | 30-50% | Margins (8 GU), Gutters (4 GU) | Calculate unused GU² |
| **Grid Alignment** | Integer positioning | 100% | 160×90 grid, whole numbers only | Coordinate validation |
| **Balance** | Weight distribution | >90% | Asymmetric/Symmetric options | Visual weight algorithm |
| **Highlighting** | Focus clarity | 1 per slide | Isolation, color, size | Single accent validation |
| **Minimalism** | Functional ratio | 100% | Remove decoration | Purpose verification |

#### White Space Calculation Formula
```
White Space Ratio = (Total Slide Area - Sum of Container Areas) / Total Slide Area
Total Slide Area = 160 × 90 = 14,400 GU²
Target White Space = 4,320 - 7,200 GU² (30-50%)
```

#### Visual Weight Algorithm
```
Visual Weight = Container Area × Color Intensity × Content Density
Where:
- Container Area = width × height (in GU²)
- Color Intensity = 0.1 (light) to 1.0 (dark/saturated)
- Content Density = 0.3 (sparse) to 1.0 (dense)

Balance Score = 1 - (|Left Weight - Right Weight| / Total Weight)
```

#### Grid Alignment Rules
1. **Integer Coordinates**: All X positions ∈ {0, 1, 2, ..., 159, 160}, all Y positions ∈ {0, 1, 2, ..., 89, 90}
2. **No Fractional Values**: Positions and dimensions must be whole numbers only
3. **Row/Column Alignment**: 
   - Similar elements (e.g., column headers) must share the same Y coordinate
   - Elements in the same column must share the same X coordinate
   - Related elements must have consistent widths and heights
4. **Content-Header Alignment**: Content containers must match the width of their headers
5. **Edge Consistency**: Related containers must share aligned edges (same X or Y values)
6. **Gutter Consistency**: Exactly 4 GU between adjacent containers (integer spacing)

#### Highlighting Priority Hierarchy
1. **Position**: Optical center (x=80, y=43) or Rule of Thirds intersections (integer positions)
2. **Size**: 1.2-1.5× larger than supporting elements
3. **Color**: Single accent color from theme palette
4. **Isolation**: +2 GU additional white space on all sides
5. **Weight**: Bold or increased font weight for text

#### Minimalism Checklist
- [ ] No gradient backgrounds without data purpose
- [ ] No drop shadows except for essential depth
- [ ] No decorative borders or frames
- [ ] No stock photos or clip art
- [ ] No 3D effects on charts
- [ ] No excessive colors (max 4-5 including greys)
- [ ] No redundant labels or legends
- [ ] No ornamental fonts or text effects

#### Professional Layout Patterns

**Executive Summary Layout**
- White space: 40-45%
- Key metric: Optical center, 2× size
- Supporting data: Corners, muted colors
- Clean typography: Sans-serif only

**Data Insight Layout**
- White space: 35-40%
- Chart: Left 2/3, full height
- Insight: Right 1/3, highlighted
- Callout: Single annotation on chart

**Strategic Framework Layout**
- White space: 45-50%
- Central diagram: 60% of body area
- Labels: Aligned to grid
- Balance: Symmetric for formality

## Conclusion

The Layout Architect represents a sophisticated visual intelligence layer in Deckster's architecture, transforming raw content into professionally designed presentations. By consolidating theme generation, layout selection, and container positioning into a single coherent system, it ensures every presentation is both visually appealing and effectively structured.

### Key Innovations
1. **Professional Design Principles**: Systematic application of white space, alignment, balance, highlighting, and minimalism
2. **Intelligent Layout Selection**: Content-aware mapping with design principle enforcement
3. **Progressive Delivery**: Slide-by-slide processing enables real-time preview
4. **Mathematical Precision**: Grid-based positioning with algorithmic validation
5. **Executive Standards**: Boardroom-ready presentations through proven design principles

### Implementation Priorities
1. Build core theme generation engine with professional design standards
2. Implement design principle validation and scoring algorithms
3. Create precision grid positioning with white space optimization
4. Develop highlighting and balance calculation systems
5. Integrate functional minimalism checks throughout pipeline

### Success Indicators
- All five design principles score >90% compliance
- White space ratio achieves 30-50% on every slide
- 100% grid alignment accuracy with zero manual positioning
- Key insights highlighted effectively on all data slides
- Presentations consistently rated "executive-ready"

This specification provides the foundation for building a Layout Architect that elevates Deckster's presentation quality to professional standards while maintaining the speed and reliability users expect.