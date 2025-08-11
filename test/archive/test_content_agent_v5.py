#!/usr/bin/env python3
"""
Test Content Agent V5 - Clean Architecture Test Suite
====================================================

This test suite demonstrates the V5 clean architecture that combines:
- V3's elegant 2-step component planning
- V4's proven strategic briefing and specialist execution

Features:
- All 5 stages of content generation with timing
- Strategic briefing and playbook visibility
- Icon enrichment post-processing
- Multiple test modes and themes
- Export capabilities (HTML, JSON)
- Real-time content display options

Usage:
    python test_content_agent_v5.py                    # Basic test
    python test_content_agent_v5.py --verbose          # Show all details
    python test_content_agent_v5.py --real-time        # Display content as generated
    python test_content_agent_v5.py --test-mode full   # Run full deck test

Author: AI Assistant
Date: 2024
Version: 1.0 (Clean)
"""

import asyncio
import argparse
import sys
import os
import warnings
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required models and agents
from src.models.agents import PresentationStrawman, Slide
from src.agents.layout_architect.agents.content_agent.content_agent_v5 import ContentAgentV5
from src.agents.layout_architect.agents.content_agent.content_agent_v2 import ContentManifest
from src.agents.layout_architect.model_types.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType, LayoutTemplate, GridZone
)

# Import test utilities (or define colors inline if not available)
try:
    from test_utils import Colors, format_success, format_error, print_separator
except ImportError:
    # Define colors inline if test_utils not available
    class Colors:
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        ENDC = '\033[0m'
        END = '\033[0m'  # Alias for compatibility
        BOLD = '\033[1m'
    
    def format_success(msg):
        return f"{Colors.GREEN}✓ {msg}{Colors.ENDCC}"
    
    def format_error(msg):
        return f"{Colors.RED}✗ {msg}{Colors.ENDCC}"
    
    def print_separator():
        print("=" * 80)

# ============================================================================
# TEST DATA CREATION
# ============================================================================

def create_healthcare_slides() -> List[Slide]:
    """Create healthcare-themed test slides."""
    return [
        Slide(
            slide_id="health_001",
            slide_number=1,
            slide_type="title_slide",
            title="Digital Health Revolution",
            narrative="Set the stage for how AI is transforming healthcare delivery",
            key_points=[
                "AI-powered diagnostics reducing error rates by 40%",
                "Telemedicine adoption increased 300% post-2020",
                "Predictive analytics preventing 1M hospitalizations annually"
            ],
            visuals_needed="Futuristic medical technology imagery",
            structure_preference="hero_visual"
        ),
        Slide(
            slide_id="health_002",
            slide_number=2,
            slide_type="data_driven",
            title="Clinical Outcomes Improvement",
            narrative="Show quantitative impact of digital health initiatives",
            key_points=[
                "30% reduction in readmission rates",
                "Average diagnosis time cut from 5 days to 24 hours",
                "Patient satisfaction scores up 45%"
            ],
            analytics_needed="Bar chart comparing traditional vs AI-assisted outcomes",
            structure_preference="two-column"
        ),
        Slide(
            slide_id="health_003",
            slide_number=3,
            slide_type="mixed_content",
            title="Our Integrated Platform Approach",
            narrative="Explain how our solution addresses key healthcare challenges",
            key_points=[
                "Unified patient data across all touchpoints",
                "Real-time clinical decision support",
                "Automated compliance and reporting"
            ],
            diagrams_needed="System architecture showing data flow between components",
            structure_preference="mixed_content"
        )
    ]

def create_finance_slides() -> List[Slide]:
    """Create finance-themed test slides."""
    return [
        Slide(
            slide_id="fin_001",
            slide_number=1,
            slide_type="data_driven",
            title="Q3 2024 Financial Performance",
            narrative="Highlight exceptional growth and profitability",
            key_points=[
                "Revenue: $2.4B (+25% YoY)",
                "EBITDA margin expanded to 32%",
                "Free cash flow reached $800M"
            ],
            analytics_needed="Trend chart showing quarterly revenue growth",
            structure_preference="data_focused"
        ),
        Slide(
            slide_id="fin_002",
            slide_number=2,
            slide_type="mixed_content",
            title="Market Expansion Strategy",
            narrative="Show geographic and sector diversification progress",
            key_points=[
                "Entered 5 new international markets",
                "Enterprise segment grew 45%",
                "Strategic partnerships with Fortune 500 companies"
            ],
            visuals_needed="World map showing market presence",
            diagrams_needed="Growth strategy framework",
            structure_preference="visual_heavy"
        )
    ]

def create_theme(mood: str = "professional") -> ThemeDefinition:
    """Create a theme based on mood."""
    mood_configs = {
        "professional": {
            "keywords": ["professional", "trustworthy", "innovative"],
            "primary_color": "#003366",
            "font": "Arial"
        },
        "modern": {
            "keywords": ["modern", "dynamic", "tech-forward"],
            "primary_color": "#00A86B",
            "font": "Inter"
        },
        "bold": {
            "keywords": ["bold", "impactful", "confident"],
            "primary_color": "#FF6B35",
            "font": "Montserrat"
        }
    }
    
    config = mood_configs.get(mood, mood_configs["professional"])
    
    return ThemeDefinition(
        name=f"{mood.capitalize()} Theme",
        mood_keywords=config["keywords"],
        visual_guidelines={
            "color_scheme": "corporate",
            "icon_style": "minimal",
            "chart_style": "clean"
        },
        formality_level="high",
        design_tokens=DesignTokens(
            name=mood,
            colors={
                "primary": ColorToken(value=config["primary_color"]),
                "secondary": ColorToken(value="#F0F0F0"),
                "accent": ColorToken(value="#007ACC")
            },
            typography={
                "heading": TypographyToken(
                    fontFamily=TokenValue(value=config["font"], type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=32, type=TokenType.FONT_SIZE)
                ),
                "body": TypographyToken(
                    fontFamily=TokenValue(value=config["font"], type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE)
                )
            },
            spacing={
                "small": DimensionToken(value=8, type=TokenType.DIMENSION),
                "medium": DimensionToken(value=16, type=TokenType.DIMENSION),
                "large": DimensionToken(value=32, type=TokenType.DIMENSION)
            },
            sizing={
                "icon": DimensionToken(value=24, type=TokenType.DIMENSION),
                "button": DimensionToken(value=48, type=TokenType.DIMENSION)
            }
        ),
        layout_templates={
            "contentSlide": LayoutTemplate(
                name="contentSlide",
                zones={
                    "header": GridZone(name="header", leftInset=10, topInset=10, width=140, height=20),
                    "content": GridZone(name="content", leftInset=10, topInset=35, width=140, height=60),
                    "footer": GridZone(name="footer", leftInset=10, topInset=100, width=140, height=10)
                }
            )
        }
    )

def create_strawman(theme_type: str = "healthcare") -> PresentationStrawman:
    """Create a strawman based on theme."""
    if theme_type == "healthcare":
        return PresentationStrawman(
            main_title="The Future of Digital Healthcare",
            overall_theme="Transforming patient care through AI and digital innovation",
            target_audience="Healthcare executives and investors",
            design_suggestions="Modern, clean, with medical imagery",
            presentation_duration=20,
            slides=create_healthcare_slides()
        )
    elif theme_type == "finance":
        return PresentationStrawman(
            main_title="2024 Financial Results & Strategy",
            overall_theme="Record growth and strategic market expansion",
            target_audience="Investors and financial analysts",
            design_suggestions="Professional, data-rich, corporate",
            presentation_duration=15,
            slides=create_finance_slides()
        )
    else:
        # Default to healthcare
        return create_strawman("healthcare")

# ============================================================================
# OUTPUT FORMATTER
# ============================================================================

class V5OutputFormatter:
    """Format V5 output for human readability."""
    
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.verbose = options.get('verbose', False)
    
    def format_manifest(self, manifest: ContentManifest) -> str:
        """Format content manifest for display."""
        lines = []
        
        # Title and supporting text
        lines.append(f"\n{Colors.BOLD}📄 Content Generated:{Colors.ENDC}")
        lines.append(f"   Title: {Colors.CYAN}{manifest.title}{Colors.ENDC}")
        if manifest.supporting_text:
            # Show first line of supporting text
            first_line = manifest.supporting_text.split('\n')[0]
            if len(first_line) > 60:
                first_line = first_line[:57] + "..."
            lines.append(f"   Supporting: {first_line}")
        
        # Main points
        if manifest.main_points:
            lines.append(f"\n   {Colors.YELLOW}Key Messages:{Colors.ENDC}")
            for point in manifest.main_points:
                lines.append(f"   • {point}")
        
        # Primary visual
        if manifest.primary_visual:
            lines.append(f"\n   {Colors.MAGENTA}Primary Visual:{Colors.ENDC}")
            lines.append(f"   • {manifest.primary_visual.visual_type}: {manifest.primary_visual.description}")
        
        # Supporting visuals
        if manifest.supporting_visuals:
            lines.append(f"\n   {Colors.BLUE}Supporting Visuals ({len(manifest.supporting_visuals)}):{Colors.ENDC}")
            for spec in manifest.supporting_visuals:
                lines.append(f"   • {spec.visual_type}: {spec.description}")
        
        # Stats
        lines.append(f"\n   {Colors.GREEN}Stats:{Colors.ENDC}")
        lines.append(f"   • Word count: {manifest.total_word_count}")
        lines.append(f"   • Visual count: {manifest.visual_count}")
        lines.append(f"   • Layout: {manifest.structure_preference or 'default'}")
        lines.append(f"   • Content density: {manifest.content_density}")
        
        return "\n".join(lines)
    
    def format_timing(self, start_time: float, end_time: float) -> str:
        """Format timing information."""
        duration = end_time - start_time
        return f"{Colors.GREEN}✓ Completed in {duration:.2f}s{Colors.ENDC}"

# ============================================================================
# TEST RUNNER
# ============================================================================

class V5TestRunner:
    """Run tests with Content Agent V5."""
    
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.formatter = V5OutputFormatter(options)
        self.agent = ContentAgentV5()
    
    async def run_test(self, strawman: PresentationStrawman, theme: ThemeDefinition) -> List[ContentManifest]:
        """Run the test based on options."""
        slides = strawman.slides
        
        # Determine which slides to process
        if self.options['test_mode'] == 'single':
            slides = slides[:1]
        elif self.options['test_mode'] == 'multi':
            slides = slides[:3]
        # 'full' uses all slides
        
        print(f"\n{Colors.BOLD}🚀 Testing Content Agent V5 - Clean Architecture{Colors.ENDC}")
        print(f"   Processing {len(slides)} slides with theme: {theme.name}")
        print_separator()
        
        # Process slides
        if self.options.get('show_icons', True) and len(slides) > 1:
            # Use process_all_slides for icon enrichment
            print(f"\n{Colors.CYAN}Running dual-phase orchestration...{Colors.ENDC}")
            start_time = time.time()
            manifests = await self.agent.process_all_slides(slides, theme, strawman)
            end_time = time.time()
            print(self.formatter.format_timing(start_time, end_time))
        else:
            # Process slides individually
            manifests = []
            for i, slide in enumerate(slides):
                print(f"\n{Colors.BOLD}Slide {slide.slide_number}: {slide.title}{Colors.ENDC}")
                
                start_time = time.time()
                manifest = await self.agent.run(slide, theme, strawman, manifests.copy())
                end_time = time.time()
                
                manifests.append(manifest)
                
                # Display results
                if self.options.get('real_time', False) or self.options.get('verbose', False):
                    print(self.formatter.format_manifest(manifest))
                
                print(self.formatter.format_timing(start_time, end_time))
                
                if self.options.get('pause', False) and i < len(slides) - 1:
                    input("\nPress Enter to continue...")
        
        # Export if requested
        if self.options.get('export_json', False):
            self.export_json(manifests)
        
        if self.options.get('export_html', False):
            self.export_html(manifests, strawman)
        
        return manifests
    
    def export_json(self, manifests: List[ContentManifest]):
        """Export results to JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"v5_test_results_{timestamp}.json"
        
        data = {
            "test_time": datetime.now().isoformat(),
            "options": self.options,
            "results": [
                {
                    "slide_id": m.slide_id,
                    "title": m.title,
                    "word_count": m.total_word_count,
                    "visual_count": m.visual_count,
                    "main_points": m.main_points,
                    "layout": m.layout_preference
                }
                for m in manifests
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n{format_success(f'Exported JSON to {filename}')}")
    
    def export_html(self, manifests: List[ContentManifest], strawman: PresentationStrawman):
        """Export results to HTML."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"v5_test_results_{timestamp}.html"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Content Agent V5 Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: #003366; color: white; padding: 20px; border-radius: 8px; }}
        .slide {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .title {{ color: #003366; font-size: 24px; font-weight: bold; }}
        .stats {{ background: #f0f0f0; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .points {{ margin: 10px 0; }}
        .points li {{ margin: 5px 0; }}
        .visual {{ background: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{strawman.main_title}</h1>
        <p>{strawman.overall_theme}</p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
"""
        
        for manifest in manifests:
            html += f"""
    <div class="slide">
        <div class="title">{manifest.title}</div>
        {f'<div class="subtitle">{manifest.supporting_text.split(chr(10))[0] if manifest.supporting_text else ""}</div>' if manifest.supporting_text else ''}
        
        <div class="stats">
            Words: {manifest.total_word_count} | Visuals: {manifest.visual_count} | 
            Layout: {manifest.structure_preference or 'default'} | Density: {manifest.content_density}
        </div>
        
        <div class="points">
            <strong>Key Points:</strong>
            <ul>
                {''.join(f'<li>{point}</li>' for point in manifest.main_points)}
            </ul>
        </div>
        
        {self._format_visuals_html(manifest)}
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filename, 'w') as f:
            f.write(html)
        
        print(f"\n{format_success(f'Exported HTML to {filename}')}")
    
    def _format_visuals_html(self, manifest: ContentManifest) -> str:
        """Format visuals for HTML export."""
        if not manifest.primary_visual and not manifest.supporting_visuals:
            return ""
        
        html = '<div class="visuals"><strong>Visual Elements:</strong>'
        
        if manifest.primary_visual:
            html += f'<div class="visual">🌟 Primary: {manifest.primary_visual.visual_type} - {manifest.primary_visual.description}</div>'
        
        for spec in manifest.supporting_visuals:
            icon = "🎨" if spec.visual_type == "image" else "📊" if spec.visual_type == "chart" else "📋" if spec.visual_type == "table" else "🔷"
            html += f'<div class="visual">{icon} {spec.visual_type}: {spec.description}</div>'
        
        html += '</div>'
        return html

# ============================================================================
# MAIN
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Test Content Agent V5 with clean architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Basic test with defaults
  %(prog)s --verbose                 # Show all details
  %(prog)s --real-time               # Display content as generated
  %(prog)s --test-mode full          # Run full deck test
  %(prog)s --theme finance           # Use finance theme
  %(prog)s --export-html --export-json  # Export results
        """
    )
    
    # Display options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed process information"
    )
    parser.add_argument(
        "--real-time",
        action="store_true",
        help="Display content as it's generated"
    )
    parser.add_argument(
        "--show-icons",
        action="store_true",
        default=True,
        help="Use icon enrichment when processing multiple slides (default: True)"
    )
    
    # Test options
    parser.add_argument(
        "--test-mode",
        choices=["single", "multi", "full"],
        default="multi",
        help="Test mode: single (1 slide), multi (3 slides), full (all slides)"
    )
    parser.add_argument(
        "--theme",
        choices=["healthcare", "finance"],
        default="healthcare",
        help="Theme for test content"
    )
    parser.add_argument(
        "--mood",
        choices=["professional", "modern", "bold"],
        default="professional",
        help="Visual mood for theme"
    )
    
    # Export options
    parser.add_argument(
        "--export-html",
        action="store_true",
        help="Export results to HTML file"
    )
    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Export results to JSON file"
    )
    
    # Other options
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause between slides"
    )
    
    args = parser.parse_args()
    
    # Convert to options dict
    options = {
        'verbose': args.verbose,
        'real_time': args.real_time,
        'show_icons': args.show_icons,
        'test_mode': args.test_mode,
        'theme': args.theme,
        'mood': args.mood,
        'export_html': args.export_html,
        'export_json': args.export_json,
        'pause': args.pause
    }
    
    # Create test data
    strawman = create_strawman(args.theme)
    theme = create_theme(args.mood)
    
    # Run test
    runner = V5TestRunner(options)
    try:
        results = await runner.run_test(strawman, theme)
        print(f"\n{format_success(f'Test completed successfully with {len(results)} slides')}")
    except Exception as e:
        print(f"\n{format_error(f'Test failed: {e}')}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())