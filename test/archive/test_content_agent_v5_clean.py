#!/usr/bin/env python3
"""
Test Content Agent V5 - Clean Output Version
===========================================

This test provides clean, readable output for Content Agent V5 with:
- Suppressed library warnings and logs
- Stage-by-stage content display
- Full strategic briefs in Stage 2
- All generated content in Stage 3
- Clean summary in Stage 4

Usage:
    python test_content_agent_v5_clean.py              # Basic test
    python test_content_agent_v5_clean.py --real-time  # Show all content
    python test_content_agent_v5_clean.py --quiet      # Minimal output

Author: AI Assistant
Date: 2024
Version: 1.0 (Clean Output)
"""

import asyncio
import argparse
import sys
import os
import warnings
import json
import time
import logging
import textwrap
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# LOGGING CONFIGURATION - MUST BE FIRST
# ============================================================================

# Suppress all warnings
warnings.filterwarnings("ignore")

# Configure logging to suppress library output
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)

# Suppress specific loggers
for logger_name in ['httpx', 'pydantic_ai', 'src.agents', 'src.agents.layout_architect']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required models and agents
from src.models.agents import PresentationStrawman, Slide
from src.agents.layout_architect.agents.content_agent.content_agent_v5 import ContentAgentV5
from src.agents.layout_architect.agents.content_agent import content_agent_v5
from src.agents.layout_architect.agents.content_agent.content_agent_v2 import ContentManifest
from src.agents.layout_architect.agents.content_agent.playbooks_v4 import PlaybookSession
from src.agents.layout_architect.model_types.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType, LayoutTemplate, GridZone
)

# ============================================================================
# COLORS AND FORMATTING
# ============================================================================

class Colors:
    # Main colors
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Reset
    ENDC = '\033[0m'

def print_separator(char="━", length=60, color=Colors.DIM):
    """Print a separator line."""
    print(f"{color}{char * length}{Colors.ENDC}")

def wrap_text(text: str, width: int = 70, indent: str = "   ") -> str:
    """Wrap text for readability."""
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)

# ============================================================================
# STAGE DISPLAY
# ============================================================================

class StageDisplay:
    """Handle stage-by-stage content display."""
    
    def __init__(self, options: Dict[str, Any]):
        self.real_time = options.get('real_time', False)
        self.show_briefs = options.get('show_briefs', False) or self.real_time
        self.show_content = options.get('show_content', False) or self.real_time
        self.quiet = options.get('quiet', False)
        self.verbose = options.get('verbose', False)
    
    def stage_header(self, stage_num: int, title: str):
        """Display stage header."""
        if self.quiet:
            return
        icons = ["🎯", "📋", "🎨", "🔧", "✨"]
        icon = icons[stage_num - 1] if stage_num <= len(icons) else "📌"
        print(f"\n{icon} {Colors.BOLD}Stage {stage_num}: {title}{Colors.ENDC}")
    
    def stage_1_output(self, components: List[str], playbooks: Dict[str, str]):
        """Display Stage 1 output."""
        if self.quiet:
            return
            
        print(f"   {Colors.GREEN}✓{Colors.ENDC} Components identified: {', '.join(components)}")
        
        if self.show_content or self.verbose:
            print(f"   {Colors.GREEN}✓{Colors.ENDC} Playbook strategies selected:")
            for comp, playbook in playbooks.items():
                print(f"     {Colors.DIM}•{Colors.ENDC} {comp} → {Colors.CYAN}{playbook}{Colors.ENDC}")
    
    def stage_2_briefs(self, briefs):
        """Display Stage 2 strategic briefs."""
        if not self.show_briefs:
            if not self.quiet:
                print(f"   {Colors.GREEN}✓{Colors.ENDC} Created {len(briefs.briefs)} strategic briefs")
            return
        
        for i, brief in enumerate(briefs.briefs, 1):
            playbook_display = brief.playbook_key if brief.playbook_key else f"{Colors.RED}NOT SET{Colors.ENDC}"
            print(f"\n   {Colors.YELLOW}Brief {i}:{Colors.ENDC} {brief.component_type.upper()} Component")
            print(f"   {Colors.GREEN}Playbook:{Colors.ENDC} {playbook_display}")
            print(f"   {'─' * 50}")
            
            # Show if required_elements contains playbook data
            if brief.required_elements and 'containers' in brief.required_elements:
                print(f"   {Colors.BOLD}Containers from Playbook:{Colors.ENDC}")
                for container in brief.required_elements.get('containers', []):
                    tag = container.get('tag', 'unknown')
                    role = container.get('role', 'unknown')
                    word_limit = container.get('word_limit', 'N/A')
                    print(f"   • {tag} - {role} ({word_limit} words)")
            
            # Detailed instructions
            print(f"\n   {Colors.BOLD}Detailed Instructions:{Colors.ENDC}")
            print(wrap_text(brief.detailed_instruction, indent="   "))
            
            # Required elements
            if brief.required_elements:
                print(f"\n   {Colors.BOLD}Required Elements:{Colors.ENDC}")
                for key, value in brief.required_elements.items():
                    if key == 'containers':  # Already shown above
                        continue
                    if isinstance(value, list):
                        print(f"   • {key}:")
                        for item in value:
                            if isinstance(item, dict):
                                print(f"     - {json.dumps(item, indent=0).replace(chr(10), ' ')}")
                            else:
                                print(f"     - {item}")
                    else:
                        print(f"   • {key}: {value}")
            
            # Style guidelines
            if brief.style_guidelines:
                print(f"\n   {Colors.BOLD}Style Guidelines:{Colors.ENDC}")
                for key, value in brief.style_guidelines.items():
                    print(f"   • {key}: {value}")
            
            # Constraints
            if brief.constraints:
                print(f"\n   {Colors.BOLD}Constraints:{Colors.ENDC}")
                for constraint in brief.constraints:
                    print(f"   • {constraint}")
    
    def stage_3_content(self, component_type: str, output: Any):
        """Display Stage 3 generated content."""
        # Always show Stage 3 content - it's the core output of the test
        if self.quiet:
            return
        
        print(f"\n   {Colors.MAGENTA}{component_type.upper()} Output:{Colors.ENDC}")
        print(f"   {'═' * 30}")
        
        if component_type == "text" and isinstance(output, content_agent_v5.TextContentV4):
            self._display_text_content(output)
        elif component_type == "analytics" and isinstance(output, content_agent_v5.AnalyticsContentV4):
            self._display_analytics_content(output)
        elif component_type == "image" and isinstance(output, content_agent_v5.ImageContentV4):
            self._display_image_content(output)
        elif component_type == "diagram" and isinstance(output, content_agent_v5.DiagramContentV4):
            self._display_diagram_content(output)
        elif component_type == "table" and isinstance(output, content_agent_v5.TableContentV4):
            self._display_table_content(output)
    
    def _display_text_content(self, content):
        """Display text content with HTML."""
        print(f"   {Colors.BOLD}Title:{Colors.ENDC} {content.title}")
        print(f"   {Colors.BOLD}Narrative Flow:{Colors.ENDC} {content.narrative_flow}")
        print(f"   {Colors.BOLD}Tone:{Colors.ENDC} {', '.join(content.tone_markers)}")
        
        print(f"\n   {Colors.BOLD}HTML Content:{Colors.ENDC}")
        for block in content.content_blocks:
            if block.content_html:
                # Format HTML for readability
                html = block.content_html.replace("><", ">\n   <")
                print(f"   {html}")
    
    def _display_analytics_content(self, content):
        """Display analytics content."""
        print(f"   {Colors.BOLD}Chart Type:{Colors.ENDC} {content.chart_type}")
        print(f"   {Colors.BOLD}Title:{Colors.ENDC} {content.title}")
        
        print(f"\n   {Colors.BOLD}Data Points:{Colors.ENDC}")
        for dp in content.data_points[:3]:  # Show first 3
            print(f"   • {json.dumps(dp, indent=0).replace(chr(10), ' ')}")
        if len(content.data_points) > 3:
            print(f"   • ... and {len(content.data_points) - 3} more")
        
        print(f"\n   {Colors.BOLD}Visual Encoding:{Colors.ENDC}")
        for key, value in content.visual_encoding.items():
            print(f"   • {key}: {value}")
        
        print(f"\n   {Colors.BOLD}Insights:{Colors.ENDC}")
        for insight in content.insights:
            print(f"   • {insight}")
    
    def _display_image_content(self, content):
        """Display image content."""
        print(f"   {Colors.BOLD}Archetype:{Colors.ENDC} {content.archetype}")
        print(f"   {Colors.BOLD}Subject:{Colors.ENDC} {content.primary_subject}")
        print(f"   {Colors.BOLD}Composition:{Colors.ENDC} {content.composition_notes}")
        
        print(f"\n   {Colors.BOLD}Art Direction:{Colors.ENDC}")
        for key, value in content.art_direction.items():
            print(f"   • {key}: {value}")
        
        print(f"\n   {Colors.BOLD}Mood:{Colors.ENDC} {', '.join(content.mood_keywords)}")
    
    def _display_diagram_content(self, content):
        """Display diagram content."""
        print(f"   {Colors.BOLD}Pattern:{Colors.ENDC} {content.pattern}")
        print(f"   {Colors.BOLD}Flow Direction:{Colors.ENDC} {content.flow_direction}")
        
        print(f"\n   {Colors.BOLD}Core Elements:{Colors.ENDC}")
        for elem in content.core_elements[:3]:
            print(f"   • {elem}")
        
        print(f"\n   {Colors.BOLD}Visual Hierarchy:{Colors.ENDC}")
        for level in content.visual_hierarchy:
            print(f"   • {level}")
    
    def _display_table_content(self, content):
        """Display table content."""
        print(f"   {Colors.BOLD}Structure:{Colors.ENDC} {content.structure_type}")
        print(f"   {Colors.BOLD}Headers:{Colors.ENDC} {' | '.join(content.headers)}")
        print(f"   {Colors.BOLD}Rows:{Colors.ENDC} {len(content.rows)}")
        print(f"   {Colors.BOLD}Summary:{Colors.ENDC} {content.summary_insight}")
    
    def stage_4_summary(self, manifest: ContentManifest):
        """Display Stage 4 assembly summary."""
        if self.quiet:
            return
            
        print(f"   {Colors.GREEN}✓{Colors.ENDC} Total word count: {manifest.total_word_count}")
        print(f"   {Colors.GREEN}✓{Colors.ENDC} Visual elements: {manifest.visual_count}")
        print(f"   {Colors.GREEN}✓{Colors.ENDC} Content density: {manifest.content_density}")
        print(f"   {Colors.GREEN}✓{Colors.ENDC} Layout: {manifest.structure_preference or 'default'}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_slide_selection(slides_arg: str, total_slides: int) -> List[int]:
    """Parse slide selection argument into list of slide indices."""
    if not slides_arg:
        return list(range(total_slides))
    
    slide_indices = []
    
    # Handle range (e.g., "1-3")
    if '-' in slides_arg and ',' not in slides_arg:
        start, end = slides_arg.split('-')
        start_idx = int(start) - 1  # Convert to 0-based
        end_idx = int(end) - 1
        slide_indices = list(range(start_idx, end_idx + 1))
    
    # Handle list (e.g., "1,3,5")
    elif ',' in slides_arg:
        for num in slides_arg.split(','):
            slide_indices.append(int(num.strip()) - 1)
    
    # Handle single slide
    else:
        slide_indices = [int(slides_arg) - 1]
    
    # Filter valid indices
    valid_indices = [i for i in slide_indices if 0 <= i < total_slides]
    return valid_indices

# ============================================================================
# CLEAN TEST RUNNER
# ============================================================================

class CleanV5TestRunner:
    """Run tests with clean output."""
    
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.display = StageDisplay(options)
        self.playbook_session = PlaybookSession()
    
    async def run_single_slide_detailed(
        self, 
        slide: Slide, 
        theme: ThemeDefinition,
        deck_summary: str,
        strawman: PresentationStrawman,
        completed_slides: Optional[List[ContentManifest]] = None
    ) -> ContentManifest:
        """Run single slide with detailed stage output."""
        
        # Stage 1: Component Planning
        self.display.stage_header(1, "Component Planning")
        start_time = time.time()
        
        components = await content_agent_v5.identify_required_components(slide)
        component_playbooks = await content_agent_v5.select_playbook_strategies(slide, components)
        
        stage1_time = time.time() - start_time
        self.display.stage_1_output(components, component_playbooks)
        if not self.options.get('quiet'):
            print(f"   {Colors.DIM}Completed in {stage1_time:.1f}s{Colors.ENDC}")
        
        # Convert to PlannedComponent format
        planned_components = []
        for comp_type, playbook_key in component_playbooks.items():
            planned = content_agent_v5.PlannedComponent(
                component_type=comp_type,
                selected_playbook_key=playbook_key,
                rationale=f"Selected for {slide.slide_type} slide"
            )
            planned_components.append(planned)
        
        # Stage 2: Strategic Briefing
        self.display.stage_header(2, "Strategic Briefing")
        start_time = time.time()
        
        strategic_briefs = await content_agent_v5.run_strategic_briefing_agent_v2(
            planned_components,
            slide,
            theme,
            self.playbook_session
        )
        
        stage2_time = time.time() - start_time
        self.display.stage_2_briefs(strategic_briefs)
        if not self.options.get('quiet'):
            print(f"\n   {Colors.DIM}Completed in {stage2_time:.1f}s{Colors.ENDC}")
        
        # Stage 3: Content Generation
        self.display.stage_header(3, "Content Generation")
        start_time = time.time()
        
        # Run specialists in parallel
        specialist_tasks = []
        component_types = []
        
        for brief in strategic_briefs.briefs:
            if brief.component_type == "text":
                task = content_agent_v5.run_text_specialist_v4(brief, slide, theme, deck_summary, completed_slides)
                specialist_tasks.append(task)
                component_types.append("text")
            elif brief.component_type == "analytics":
                task = content_agent_v5.run_analytics_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("analytics")
            elif brief.component_type == "image":
                task = content_agent_v5.run_image_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("image")
            elif brief.component_type == "diagram":
                task = content_agent_v5.run_diagram_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("diagram")
            elif brief.component_type == "table":
                task = content_agent_v5.run_table_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("table")
        
        # Execute and display results
        specialist_results = await asyncio.gather(*specialist_tasks)
        
        component_outputs = {}
        for comp_type, result in zip(component_types, specialist_results):
            component_outputs[comp_type] = result
            self.display.stage_3_content(comp_type, result)
        
        stage3_time = time.time() - start_time
        if not self.options.get('quiet'):
            print(f"\n   {Colors.DIM}Completed in {stage3_time:.1f}s{Colors.ENDC}")
        
        # Stage 4: Assembly
        self.display.stage_header(4, "Content Assembly")
        start_time = time.time()
        
        manifest = content_agent_v5.assemble_content_manifest_v4(
            slide,
            component_outputs,
            self.playbook_session
        )
        
        stage4_time = time.time() - start_time
        self.display.stage_4_summary(manifest)
        if not self.options.get('quiet'):
            print(f"   {Colors.DIM}Completed in {stage4_time:.1f}s{Colors.ENDC}")
        
        return manifest
    
    async def run_test(self, strawman: PresentationStrawman, theme: ThemeDefinition) -> List[ContentManifest]:
        """Run the test."""
        all_slides = strawman.slides
        
        # Determine which slides to process
        if self.options.get('slides'):
            # Use custom slide selection
            slide_indices = parse_slide_selection(self.options['slides'], len(all_slides))
            slides = [all_slides[i] for i in slide_indices]
        elif self.options['test_mode'] == 'single':
            slides = all_slides[:1]
        elif self.options['test_mode'] == 'multi':
            slides = all_slides[:3]
        else:
            slides = all_slides
        
        if not self.options.get('quiet'):
            print(f"\n{Colors.BOLD}🚀 Content Agent V5 - Clean Output Test{Colors.ENDC}")
            print(f"Processing {len(slides)} slide{'s' if len(slides) > 1 else ''} with {theme.name}")
            print_separator()
        
        deck_summary = f"{strawman.main_title}: {strawman.overall_theme}"
        manifests = []
        
        # Process slides
        for i, slide in enumerate(slides):
            if not self.options.get('quiet'):
                print(f"\n{Colors.BOLD}{Colors.CYAN}📄 Slide {slide.slide_number}: {slide.title}{Colors.ENDC}")
                print_separator(char="─", length=50, color=Colors.DIM)
            
            total_start = time.time()
            
            if self.options.get('real_time') or self.options.get('show_briefs') or self.options.get('show_content'):
                # Detailed stage-by-stage processing
                manifest = await self.run_single_slide_detailed(
                    slide, theme, deck_summary, strawman, manifests.copy()
                )
            else:
                # Simple processing with ContentAgentV5
                agent = ContentAgentV5()
                manifest = await agent.run(slide, theme, strawman, manifests.copy())
                
                if not self.options.get('quiet'):
                    print(f"   {Colors.GREEN}✓{Colors.ENDC} Generated: {manifest.title}")
                    print(f"   {Colors.GREEN}✓{Colors.ENDC} Word count: {manifest.total_word_count}")
                    print(f"   {Colors.GREEN}✓{Colors.ENDC} Visuals: {manifest.visual_count}")
            
            manifests.append(manifest)
            
            total_time = time.time() - total_start
            if not self.options.get('quiet'):
                print(f"\n   {Colors.GREEN}{Colors.BOLD}✓ Total time: {total_time:.1f}s{Colors.ENDC}")
            
            if self.options.get('pause') and i < len(slides) - 1:
                input("\nPress Enter to continue...")
        
        return manifests

# ============================================================================
# TEST DATA
# ============================================================================

def create_test_slide() -> Slide:
    """Create a test slide."""
    return Slide(
        slide_id="test_001",
        slide_number=1,
        slide_type="mixed_content",
        title="Digital Health Revolution",
        narrative="Show how AI is transforming healthcare delivery",
        key_points=[
            "AI diagnostics reducing errors by 40%",
            "Telemedicine adoption up 300%",
            "Predictive analytics preventing hospitalizations"
        ],
        analytics_needed="Comparison chart of traditional vs AI-assisted outcomes",
        visuals_needed="Futuristic medical technology imagery",
        structure_preference="two-column"
    )

def create_test_theme() -> ThemeDefinition:
    """Create a test theme."""
    return ThemeDefinition(
        name="Professional Modern",
        mood_keywords=["professional", "innovative", "trustworthy"],
        visual_guidelines={
            "color_scheme": "blues and whites",
            "icon_style": "minimal line icons",
            "chart_style": "clean and modern"
        },
        formality_level="high",
        design_tokens=DesignTokens(
            name="professional",
            colors={
                "primary": ColorToken(value="#003366"),
                "secondary": ColorToken(value="#0066CC"),
                "accent": ColorToken(value="#00A86B")
            },
            typography={
                "heading": TypographyToken(
                    fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=32, type=TokenType.FONT_SIZE)
                ),
                "body": TypographyToken(
                    fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE)
                )
            },
            spacing={
                "small": DimensionToken(value=8, type=TokenType.DIMENSION),
                "medium": DimensionToken(value=16, type=TokenType.DIMENSION)
            },
            sizing={
                "icon": DimensionToken(value=24, type=TokenType.DIMENSION)
            }
        ),
        layout_templates={}
    )

def create_test_strawman() -> PresentationStrawman:
    """Create a test strawman."""
    # Try to load mock_strawman.json if it exists
    mock_path = Path(__file__).parent / "mock_strawman.json"
    if mock_path.exists():
        with open(mock_path, 'r') as f:
            data = json.load(f)
        return PresentationStrawman(**data)
    
    # Fallback to simple test strawman
    return PresentationStrawman(
        main_title="The Future of Digital Healthcare",
        overall_theme="Transforming patient care through AI and digital innovation",
        target_audience="Healthcare executives and investors",
        design_suggestions="Modern, clean, professional with medical imagery",
        presentation_duration=20,
        slides=[create_test_slide()]
    )

# ============================================================================
# MAIN
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Test Content Agent V5 with clean, readable output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Basic test with clean output
  %(prog)s --real-time            # Show all stages and content
  %(prog)s --slides 1-3           # Process slides 1 through 3
  %(prog)s --slides 2,4,6        # Process specific slides
  %(prog)s --slides 5            # Process only slide 5
  %(prog)s --show-briefs          # Show strategic briefs
  %(prog)s --quiet                # Minimal output only
        """
    )
    
    # Display options
    parser.add_argument(
        "--real-time",
        action="store_true",
        help="Display all stages and content as generated (implies --show-briefs and --show-content)"
    )
    parser.add_argument(
        "--show-briefs",
        action="store_true",
        help="Display full strategic briefs in Stage 2"
    )
    parser.add_argument(
        "--show-content",
        action="store_true",
        help="Display all generated content in Stage 3"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all but essential output"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show additional details"
    )
    
    # Test options
    parser.add_argument(
        "--test-mode",
        choices=["single", "multi", "full"],
        default="single",
        help="Test mode: single (1 slide), multi (3 slides), full (all slides)"
    )
    parser.add_argument(
        "--slides",
        type=str,
        help="Specify slides to process: single (5), range (1-3), or list (1,3,5)"
    )
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause between slides"
    )
    
    args = parser.parse_args()
    
    # Convert to options dict
    options = {
        'real_time': args.real_time,
        'show_briefs': args.show_briefs,
        'show_content': args.show_content,
        'quiet': args.quiet,
        'verbose': args.verbose,
        'test_mode': args.test_mode,
        'slides': args.slides,
        'pause': args.pause
    }
    
    # Create test data
    strawman = create_test_strawman()
    theme = create_test_theme()
    
    # Run test
    runner = CleanV5TestRunner(options)
    try:
        results = await runner.run_test(strawman, theme)
        if not args.quiet:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Test completed successfully{Colors.ENDC}")
            print(f"Generated content for {len(results)} slide{'s' if len(results) > 1 else ''}")
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Test failed: {e}{Colors.ENDC}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())