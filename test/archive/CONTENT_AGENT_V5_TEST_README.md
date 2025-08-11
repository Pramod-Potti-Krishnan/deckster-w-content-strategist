# Content Agent V5 Beautiful Test Suite

A visually rich CLI test for Content Agent V5 that processes the mock healthcare presentation strawman.

## Prerequisites

```bash
# Install rich library for beautiful terminal output
pip install rich
```

## Running the Test

### Basic Run (Default - Verbose with all stages)
```bash
python test_content_agent_v5_beautiful.py
```

### Run with Pause Between Slides
```bash
python test_content_agent_v5_beautiful.py --pause
```

### Export Results to JSON
```bash
python test_content_agent_v5_beautiful.py --export
```

### Quiet Mode (Minimal Output)
```bash
python test_content_agent_v5_beautiful.py --quiet
```

### Disable Emoji Icons (For Terminal Compatibility)
```bash
python test_content_agent_v5_beautiful.py --no-icons
```

## Features

1. **Beautiful Terminal UI**
   - Healthcare-themed colors (blues, greens, whites)
   - Progress bars for each slide
   - Tables for structured data
   - Tree views for hierarchical information
   - Emoji indicators for content types

2. **Real-Time Stage Display**
   - Stage 1: Component Planning - Shows identified components and selected playbooks
   - Stage 2: Strategic Briefing - Displays detailed briefs for each component
   - Stage 3: Content Generation - Progress bars for parallel specialist execution
   - Stage 4: Assembly - Final manifest summary

3. **Comprehensive Output**
   - Strawman overview table
   - Theme information display
   - Slide-by-slide processing with headers
   - Generated content previews
   - Final summary dashboard with statistics

4. **Export Capability**
   - Saves results to timestamped JSON file
   - Includes processing times and metrics

## Test Data

The test uses `mock_strawman.json` which contains a 10-slide presentation about "Digital Transformation in Healthcare" with diverse slide types:
- Title slide
- Section dividers
- Content heavy slides
- Data driven slides
- Visual heavy slides
- Diagram focused slides
- Mixed content slides
- Conclusion slide

## Troubleshooting

If you see "Warning: 'rich' library not installed", install it with:
```bash
pip install rich
```

The test will fall back to basic output if rich is not available, but the experience is much better with rich installed.