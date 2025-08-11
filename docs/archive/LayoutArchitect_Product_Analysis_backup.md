# Layout Architect Product Analysis & Functional Specification

## Executive Summary
- **Purpose**: The Layout Architect is the first specialist agent in Deckster's parallel agent architecture, responsible for transforming content strategy into visual layouts. It processes presentation strawman content and generates intelligent, varied layout specifications for each slide, ensuring visual appeal while maintaining content clarity.
- **Key Capabilities**: 
  - Presentation theme generation with layouts and typography
  - Theme-based layout mapping
  - Custom container generation for complex content
  - Content-aware layout selection
  - Progressive slide-by-slide delivery
  - Layout variety management
- **Integration Context**: Works in parallel with other specialist agents after strawman approval, feeding processed layouts to the Director OUT assembler for progressive frontend delivery
- **Multiple Agents**: No - this analysis focuses solely on the Layout Architect agent

## Product Concept Analysis
### Original Requirements
The Phase 2 plan establishes the Layout Architect as the inaugural parallel agent, introducing:
- Parallel execution after strawman approval (State 5)
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
     - Step 4: **Typography System Design**:
       - **Hierarchy Definition**: Create comprehensive font stack:
         - **Headers**: h1, h2, h3, h4, h5, h6 (hierarchical structure)
         - **Body Variants**: body, lead (intro text), small (fine print)
         - **Special Purpose**: caption, footer, quote, code (monospace)
         - **Data Display**: metric (large numbers), label (chart labels), overline (small caps)
       - **Font Properties**: Specify for each level:
         - Typeface family (primary and fallback)
         - Size (base and responsive scaling)
         - Weight (100-900 scale)
         - Line height (1.2-1.8 based on use)
         - Letter spacing (tracking adjustments)
         - Text transform (uppercase, lowercase, capitalize)
       - **Color Variants**: Define for each text level:
         - Default color (standard use)
         - Emphasized color (highlighted state)
         - Muted color (secondary information)
         - Interactive color (links, clickable elements)
       - **Contextual Sizing**: 
         - Title slides: h1 at 48-72pt, h2 at 36-48pt
         - Content slides: h1 at 32-40pt, h2 at 24-32pt
         - Data slides: metric at 60-96pt for KPIs
         - Mobile/responsive: 85% of desktop sizes
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
       - Break down content into logical containers by type:
         - **Text Elements**: Headers, subheaders, body paragraphs, bullet lists, quotes
         - **Data Elements**: 
           - **Tables**: First-class objects with structured rows/columns, header styling, cell padding
           - **Charts**: Bar, line, pie, scatter with dedicated label/legend space
           - **Metrics**: KPI displays, gauges, counters
           - **Timelines**: Temporal data visualization
           - **Maps**: Geographic data display
         - **Code Elements**:
           - **Code Blocks**: Syntax-highlighted code with theme support (Monokai, Solarized, etc.)
           - **Inline Code**: Monospace snippets within text
         - **Media Elements**: 
           - **Images**: Raster images (JPG, PNG)
           - **Icons**: Vector-based (SVG) with theme-controlled colors
           - **Videos**: With playback controls
           - **GIFs/Animations**: Motion graphics
         - **Interactive Elements**: Buttons/CTAs, QR codes, clickable areas
         - **Structural Elements**: 
           - **Shapes**: Rectangles, circles, lines with theme-controlled fills/strokes
           - **Dividers**: Horizontal/vertical separators
           - **Progress Indicators**: Navigation/completion status
         - **Decorative Elements**: Background patterns, watermarks, badges
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
       - **Semantic Content-to-Visual Mapping**:
         | Strawman Content | Semantic Type | Visual Treatment | Layout Pattern |
         |-----------------|---------------|------------------|----------------|
         | Main point of slide | KeyTakeaway | Wide container at top, h2 typography, bottom border | 120×8 GU |
         | List of items | BulletedList | Standard text box, body font, themed bullets | 60×30 GU |
         | Direct quote | Quote | Large left padding, accent background, italic | 80×20 GU |
         | Competing ideas | ComparisonFramework | 2+ tall narrow containers, side-by-side | 40×50 GU each |
         | Process/flow | ProcessFlow | Horizontal sequence with arrow shapes between | Variable |
         | Key number/stat | KeyMetric | Large metric font, small caption below | 30×25 GU |
         | Clarification | Footnote | Small container, caption font, bottom placement | 40×8 GU |
         | Data request | DataViz | Large primary block, flagged for chart agent | 80×50 GU |
         | Code snippet | CodeBlock | Monospace font, syntax highlighting, dark bg | 100×40 GU |
         | Structured data | Table | Row/column grid, header emphasis, cell padding | Variable |
         
       - **Slide Type Specific Strategies**:
         
         **title_slide Layouts**:
         - Full-Bleed: Background image (160×90), title overlay (100×20) with scrim
         - Single Focal: Centered title (60×20), subtitle (40×10), logo (20×20)
         
         **content_heavy Layouts**:
         - Columnar Text: 2-3 columns (45×50 each), pull quotes between
         - Two-Column: Main content (90×60), sidebar points (50×60)
         - Single Focal: Large text block (120×50), highlighted key sentence
         
         **data_driven Layouts**:
         - Grid: 2×2 charts (45×35 each), central insight callout
         - Two-Column: Primary chart (80×50), metrics list (55×50)
         - Single Focal: Major visualization (100×60), key insight below
         
         **visual_heavy Layouts**:
         - Full-Bleed: Edge-to-edge image, minimal text overlay
         - Grid: Gallery 3×3 (45×25 each), hover captions
         - Two-Column: Large image (95×65), description (55×65)
         
         **diagram_focused Layouts**:
         - Single Focal: Central diagram (120×55), legend below
         - Two-Column: Diagram (85×60), step explanation (65×60)
         - Full-Bleed: Full-screen flow, floating annotations
         
         **mixed_content Layouts**:
         - Grid: Flexible 2×2, mix of text/image/chart/icon
         - Two-Column: Balanced 60/40 or 50/50 split
         - Single Focal: Hero element with supporting ring
         
         **conclusion_slide Layouts**:
         - Single Focal: CTA button (60×15), message, contact info
         - Two-Column: Summary (70×50), next steps (70×50)
         - Full-Bleed: Inspirational image, CTA overlay
         
       - **Container Sizing by Content Type**:
         - Headlines: 8-15 GU height
         - Body paragraphs: 20-40 GU height
         - Bullet lists: 5-8 GU per item
         - Hero images: 80×50 GU minimum
         - Thumbnails: 30×20 GU
         - Icons: 8×8 or 12×12 GU
         - Charts: Bar (50×35), Pie (40×40), Line (60×35)
         - Tables: 10 GU height per row
         - CTAs: 50×12 GU
         - QR codes: 20×20 GU
         
       - **Typography Assignment**:
         - Main titles: h1 or h2 depending on hierarchy
         - Section headers: h3 or h4
         - Key takeaways: h2 or lead typography
         - Body content: body typography
         - Data labels: label typography
         - Large numbers: metric typography
         - Quotes: quote typography with styling
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

     **Stage 4: Grid Positioning with Z-Index Management**
     - **Input**: Enhanced container manifest with visual treatments and theme body zone coordinates
     - **Process**:
       - **Body Zone Calculation**: 
         - Subtract header/footer zones from total grid (160×90)
         - Account for slide margins (typically 8 GU on all sides)
         - Result: Available body area (e.g., 144×65 GU)
       - **Container Positioning Algorithm**:
         - Start with background/lowest z-index elements
         - Apply positioning best practices:
           - **Rule of Thirds**: Position focal points at x=53, x=107, y=30, y=60 for dynamic composition
           - **Standardized Gutters**: Enforce minimum 4 GU between sibling containers
           - **Alignment Rules**: Align edges of different containers to common lines
           - **Optical Centering**: Position vertically centered items slightly above true center (y - height*0.05)
           - **Visual Weight Balance**: Balance large/dark elements with equivalent text/whitespace
         - Position primary content using these principles
         - Add supporting elements maintaining consistent spacing
         - Validate all positions against grid constraints
       - **Z-Index Layering**:
         - Background images/shapes: z-index 1
         - Main content: z-index 2-5
         - Callouts/overlays: z-index 6-10
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

     **Stage 6: Layout Variety Analysis and Optimization**
     - **Input**: Complete layout specification and history of previous slides
     - **Process**:
       - **Similarity Calculation**:
         - Compare container arrangements with last 5-7 slides
         - Calculate position similarity, visual weight distribution
         - Generate variety score (0-100)
       - **Variety Enhancement** (if score <80):
         - Alternate container arrangements (left/right flip)
         - Adjust spacing and proportions (±10%)
         - Rotate between alignment strategies
       - **Coherence Check**: Ensure changes maintain readability
     - **Output**: Variety-optimized layout with score:
       ```json
       {
         "layoutId": "content-slide-7",
         "varietyScore": 85,
         "adjustmentsApplied": ["flipped-horizontal", "increased-spacing"]
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

#### 2. **Typography Hierarchy Generation**
   - Purpose: Create a complete typography system for the presentation
   - Trigger: During theme generation
   - Input Requirements:
     - Data: Theme style parameters
     - Format: Style configuration
     - Validation: Valid style selection
   - Processing Steps:
     - Step 1: Select appropriate font families
     - Step 2: Define size hierarchy (h1, h2, h3, body, caption)
     - Step 3: Set font weights and line heights
     - Step 4: Configure text alignment defaults
   - Output Specification:
     - Data: Typography specification
     - Format: JSON with font properties
   - Success Criteria: Readable, hierarchical typography
   - Error Scenarios: Font availability issues
   - Dependencies: Font library, readability guidelines

#### 3. **Content Density Analysis**
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

#### 4. **Visual Hierarchy Determination**
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

#### 5. **Layout Hint Generation**
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

## Memory Requirements

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

## Integration Requirements

### System Integration Points
- **Director Agent**: Receives strawman after State 5 completion
- **Director OUT Assembler**: Sends completed layouts via message queue
- **Theme Generation**: Creates custom theme based on presentation context
- **Frontend Renderer**: Provides theme and layout specs compatible with rendering engine

### Data Flow
```markdown
## Data Flow Analysis

### Input Sources
1. **Presentation Strawman**: Complete slide structure from Director
2. **User Preferences**: Visual and style preferences from session
3. **Presentation Metadata**: Type, audience, formality level

### Processing Pipeline
1. **Strawman Reception**: Validate and parse presentation structure
2. **Context Analysis**: Extract metadata and preferences
3. **Theme Generation**: Create complete theme with layouts, typography, colors
4. **Concurrent Processing**: Process slides in parallel using generated theme
5. **Layout Generation**: Create specifications per slide
6. **Quality Validation**: Ensure grid constraints and variety
7. **Progressive Delivery**: Send completed layouts immediately

### Output Destinations
1. **Message Queue**: AgentMessage objects to Director OUT
2. **Session Storage**: Layout history for variety tracking
3. **Pattern Database**: Successful layouts for learning
```

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

## Memory Architecture Analysis

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

### Proposed Schema Changes
```sql
-- Add layout-specific columns to sessions table
ALTER TABLE sessions ADD COLUMN layout_architect_state JSONB DEFAULT '{
  "layout_history": [],
  "processing_queue": [],
  "variety_score": 0,
  "generated_theme": null
}'::JSONB;

-- Create layout patterns table
CREATE TABLE layout_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name TEXT NOT NULL,
    content_type TEXT NOT NULL,
    layout_spec JSONB NOT NULL,
    effectiveness_score FLOAT DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create layout templates table  
CREATE TABLE layout_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name TEXT NOT NULL,
    container_spec JSONB NOT NULL,
    content_characteristics JSONB NOT NULL,
    theme_compatibility TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create presentation themes table
CREATE TABLE presentation_themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT REFERENCES sessions(id),
    theme_name TEXT NOT NULL,
    theme_spec JSONB NOT NULL, -- Complete theme with layouts, typography, colors
    presentation_type TEXT,
    audience_type TEXT,
    formality_level TEXT,
    effectiveness_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_layout_patterns_content_type ON layout_patterns(content_type);
CREATE INDEX idx_layout_patterns_score ON layout_patterns(effectiveness_score DESC);
CREATE INDEX idx_layout_templates_name ON layout_templates(template_name);
```

## Technical Requirements

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

## Success Metrics

### Functional Metrics
- **Layout Generation**: 100% of slides receive valid layouts
- **Theme Mapping**: 95% success rate for standard slides
- **Custom Generation**: <5% failure rate for complex content
- **Variety Score**: >80% unique layouts in 20-slide deck

### Performance Metrics
- **Response Time**: 95th percentile <2s per slide
- **Error Rate**: <1% layout generation failures
- **Queue Performance**: 99.9% message delivery success
- **Memory Efficiency**: <50MB peak usage per session

### User Experience Metrics
- **Visual Appeal**: Measurable improvement in presentation ratings
- **Layout Satisfaction**: <10% manual layout adjustments
- **Time to Completion**: 30% faster presentation creation
- **Variety Perception**: Users report "less repetitive" layouts

## Implementation Considerations

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

### D: Container Type Reference

#### Text Containers
| Type | Typical Size (GU) | Typography | Use Case |
|------|------------------|------------|----------|
| Main Title | 100×15 | h1 | Title slides |
| Section Title | 80×12 | h2 | Section headers |
| Subtitle | 60×8 | h3 | Supporting titles |
| Body Text | 60-120×20-40 | body | Main content |
| Bullet List | 60×5-8 per item | body | Listed items |
| Quote Block | 60×20 | quote | Testimonials |
| Key Takeaway | 120×8 | h2/lead | Single insight |
| Caption | 40×5 | caption | Image descriptions |
| Code Block | 100×40 | code | Code snippets |
| Inline Code | Variable | code | Code in text |
| Footnote | 40×8 | small | Annotations |

#### Data Visualization Containers
| Type | Minimum Size (GU) | Optimal Size (GU) | Notes |
|------|------------------|-------------------|-------|
| Bar Chart | 40×30 | 50×35 | Needs label space |
| Line Chart | 50×30 | 60×35 | Wide for trends |
| Pie Chart | 35×35 | 40×40 | Square aspect |
| Table | 60×10/row | 80×10/row | First-class object with styled headers |
| Gauge | 30×30 | 35×35 | Circular |
| Timeline | 100×15 | 140×20 | Horizontal |
| Map | 60×40 | 80×50 | Geographic data |

#### Media Containers
| Type | Standard Sizes (GU) | Aspect Ratio | Z-Index |
|------|-------------------|--------------|----------|
| Hero Image | 80×50, 100×60 | 16:9 or 4:3 | 2-3 |
| Thumbnail | 30×20, 45×25 | Variable | 2-3 |
| Video | 80×45, 120×67 | 16:9 | 3-4 |
| Icon | 8×8, 12×12, 16×16 | 1:1 | 3-4 |
| Logo | 20×10, 30×15 | Variable | 2-3 |
| QR Code | 20×20 | 1:1 | 4-5 |

#### Interactive Elements
| Type | Size (GU) | Typography | Prominence |
|------|-----------|------------|------------|
| Primary CTA | 50×12 | h3/button | High |
| Secondary CTA | 40×10 | body/button | Medium |
| Link | Inline | body | Low |
| Progress Bar | 100×4 | caption | Low |
| Navigation | 140×8 | small | Medium |

#### Structural Elements
| Type | Typical Size (GU) | Purpose | Properties |
|------|------------------|----------|------------|
| Divider Line | 120×1 | Section separation | Theme stroke color |
| Background Pattern | 160×90 | Visual texture | Low opacity |
| Watermark | 40×20 | Branding | z-index 1 |
| Rectangle | Variable | Container/emphasis | Fill, stroke, opacity |
| Circle | 20×20 to 40×40 | Focal points | Theme colors |
| Arrow | 20×10 | Flow direction | Between process steps |
| Badge | 20×20 | Status/emphasis | Accent colors |
| Sidebar | 40×70 | Secondary content | Background tint |