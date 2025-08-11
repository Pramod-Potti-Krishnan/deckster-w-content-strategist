#!/usr/bin/env python3
"""
Beautiful CLI Test for Content Orchestrator End-to-End Flow
===========================================================

This test demonstrates the complete content generation pipeline using the ContentOrchestrator:
1. Theme Agent - Generates design theme
2. Content Agent V7 - Generates all content and image specifications  
3. Image Build Agent - Generates actual images
4. Assembly - Final content package

The test uses the same mock_strawman.json but goes through the full orchestration flow.

Usage:
    python test_content_orchestrator_beautiful.py              # Run full flow
    python test_content_orchestrator_beautiful.py --pause      # Pause between slides
    python test_content_orchestrator_beautiful.py --export     # Save results
    python test_content_orchestrator_beautiful.py --quiet      # Minimal output
    python test_content_orchestrator_beautiful.py --no-images  # Skip image generation
    python test_content_orchestrator_beautiful.py --streaming  # Use streaming mode

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import asyncio
import json
import sys
import os
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import warnings
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Rich imports for beautiful terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.columns import Columns
    from rich.markdown import Markdown
    from rich.rule import Rule
    from rich import box
    from rich.markup import escape
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not installed. Install with: pip install rich")
    print("Falling back to basic output.")

# Import required modules
from src.models.agents import PresentationStrawman, Slide
from src.agents.content_orchestrator import ContentOrchestrator
from src.models.design_tokens import ThemeDefinition

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# ============================================================================
# DISPLAY MANAGER
# ============================================================================

class BeautifulDisplay:
    """Handles all the beautiful terminal output"""
    
    def __init__(self, console: Console, options: Dict[str, Any]):
        self.console = console
        self.options = options
        self.quiet = options.get('quiet', False)
        self.no_icons = options.get('no_icons', False)
    
    def icon(self, icon_name: str) -> str:
        """Get icon or empty string if disabled"""
        if self.no_icons:
            return ""
        
        icons = {
            'rocket': '🚀',
            'theme': '🎨',
            'content': '📝',
            'image': '🖼️',
            'check': '✅',
            'error': '❌',
            'time': '⏱️',
            'package': '📦',
            'sparkles': '✨',
            'gear': '⚙️',
            'chart': '📊',
            'stream': '🌊'
        }
        return icons.get(icon_name, '')
    
    def show_banner(self):
        """Show the application banner"""
        if self.quiet:
            return
            
        banner = Panel.fit(
            f"""[bold cyan]Content Orchestrator Test[/bold cyan]
[dim]End-to-End Content Generation Pipeline[/dim]

{self.icon('theme')} Theme Generation → {self.icon('content')} Content Creation → {self.icon('image')} Image Generation → {self.icon('package')} Assembly

[bold yellow]Pipeline:[/bold yellow]
1. Theme Agent - Design system generation
2. Content Agent V7 - Content and specifications
3. Image Build Agent - Visual generation
4. Final Assembly - Complete package""",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(banner)
        self.console.print()
    
    def show_strawman_overview(self, strawman: PresentationStrawman):
        """Display strawman overview"""
        if self.quiet:
            return
            
        table = Table(title=f"{self.icon('rocket')} Presentation Overview", box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Title", strawman.main_title)
        table.add_row("Theme", strawman.overall_theme)
        table.add_row("Duration", f"{strawman.presentation_duration} minutes")
        table.add_row("Audience", strawman.target_audience)
        table.add_row("Total Slides", str(len(strawman.slides)))
        
        self.console.print(table)
        self.console.print()
    
    def show_theme_progress(self):
        """Show theme generation progress"""
        if not self.quiet:
            self.console.print(f"\n{self.icon('theme')} [bold cyan]STAGE 1: Theme Generation[/bold cyan]")
            self.console.print("[dim]Generating design system with Theme Agent...[/dim]")
    
    def show_theme_result(self, theme: ThemeDefinition):
        """Display generated theme"""
        if self.quiet:
            return
            
        # Create theme info panel
        theme_info = f"""[bold yellow]Theme Name:[/bold yellow] {theme.name}
[bold yellow]Formality:[/bold yellow] {theme.formality_level}
[bold yellow]Complexity:[/bold yellow] {theme.complexity_allowance}"""
        
        # Add colors if available
        if hasattr(theme, 'design_tokens') and theme.design_tokens.colors:
            theme_info += "\n\n[bold yellow]Color Palette:[/bold yellow]"
            for name, color in list(theme.design_tokens.colors.items())[:5]:
                theme_info += f"\n  {name}: {color.value}"
        
        # Add typography if available
        if hasattr(theme, 'design_tokens') and theme.design_tokens.typography:
            theme_info += "\n\n[bold yellow]Typography:[/bold yellow]"
            for name, typo in list(theme.design_tokens.typography.items())[:3]:
                font = typo.fontFamily.value if hasattr(typo, 'fontFamily') else 'N/A'
                theme_info += f"\n  {name}: {font}"
        
        self.console.print(Panel(
            theme_info,
            title=f"{self.icon('theme')} Generated Theme",
            border_style="green",
            padding=(1, 2)
        ))
        self.console.print()
    
    def show_content_progress(self, slide_num: int, total: int):
        """Show content generation progress"""
        if not self.quiet:
            self.console.print(f"\n{self.icon('content')} [bold cyan]STAGE 2: Content Generation - Slide {slide_num}/{total}[/bold cyan]")
    
    def show_image_progress(self, slide_id: str):
        """Show image generation progress"""
        if not self.quiet:
            self.console.print(f"  {self.icon('image')} Generating image for {slide_id}...")
    
    def show_streaming_update(self, update: Dict[str, Any]):
        """Display streaming update"""
        if self.quiet:
            return
            
        update_type = update.get('type', 'unknown')
        
        if update_type == 'theme_ready':
            self.console.print(f"{self.icon('check')} [bold green]Theme generated successfully![/bold green]")
        elif update_type == 'content_ready':
            slide_id = update.get('slide_id', 'unknown')
            progress = update.get('progress', 0)
            self.console.print(f"{self.icon('check')} [green]Content ready for {slide_id}[/green] - Progress: {progress}%")
        elif update_type == 'image_ready':
            slide_id = update.get('slide_id', 'unknown')
            self.console.print(f"{self.icon('check')} [magenta]Image ready for {slide_id}[/magenta]")
        elif update_type == 'error':
            error = update.get('error', 'Unknown error')
            self.console.print(f"{self.icon('error')} [red]Error: {error}[/red]")
        elif update_type == 'complete':
            total_slides = update.get('total_slides', 0)
            self.console.print(f"\n{self.icon('sparkles')} [bold green]Pipeline complete! Generated content for {total_slides} slides.[/bold green]")
    
    def show_final_results(self, result: Dict[str, Any], processing_time: float):
        """Display final results summary"""
        if self.quiet:
            self.console.print(f"✓ Complete in {processing_time:.2f}s")
            return
        
        self.console.rule(f"{self.icon('package')} [bold green]RESULTS SUMMARY[/bold green]", style="green")
        
        # Create summary table
        table = Table(box=box.ROUNDED)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Processing Time", f"{processing_time:.2f}s")
        table.add_row("Theme", result['theme']['name'] if isinstance(result['theme'], dict) else result['theme'].name)
        table.add_row("Slides Generated", str(len(result['content'])))
        
        # Count images
        image_count = sum(1 for item in result['content'] if item.get('generated_images'))
        table.add_row("Images Generated", str(image_count))
        
        self.console.print(table)
        self.console.print()
        
        # Show content breakdown
        self.console.print(f"{self.icon('chart')} [bold yellow]Content Breakdown:[/bold yellow]")
        for i, content_item in enumerate(result['content'], 1):
            manifest = content_item['content_manifest']
            # Handle both dict and object formats
            if isinstance(manifest, dict):
                # In dict format, title is a direct string
                title_text = manifest.get('title', 'Untitled')
                word_count = manifest.get('total_word_count', 0)
            else:
                # It's a ContentManifest object
                title_text = manifest.title
                word_count = manifest.total_word_count
            
            self.console.print(f"  Slide {i}: {title_text} ({word_count} words)")
            if content_item.get('generated_images'):
                self.console.print(f"    └─ {self.icon('image')} Image generated")
        
        self.console.print()

# ============================================================================
# TEST RUNNER
# ============================================================================

class ContentOrchestratorTest:
    """Main test runner for Content Orchestrator"""
    
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.console = Console() if RICH_AVAILABLE else None
        self.display = BeautifulDisplay(self.console, options) if self.console else None
        self.orchestrator = None
    
    async def run_test(self):
        """Run the complete test"""
        start_time = time.time()
        
        # Load mock strawman
        mock_path = Path(__file__).parent / "mock_strawman.json"
        if not mock_path.exists():
            self.console.print(f"{self.display.icon('error')} [red]Error: mock_strawman.json not found![/red]")
            self.console.print(f"[dim]Expected at: {mock_path}[/dim]")
            return
        
        with open(mock_path, 'r') as f:
            strawman_data = json.load(f)
        
        strawman = PresentationStrawman(**strawman_data)
        
        # For testing, limit to first 2 slides
        if len(strawman.slides) > 2:
            strawman.slides = strawman.slides[:2]
        
        # Show banner and overview
        if self.display:
            self.display.show_banner()
            self.display.show_strawman_overview(strawman)
        
        # Initialize orchestrator
        self.orchestrator = ContentOrchestrator(
            theme_model="gemini-2.5-flash",
            content_model="gemini-2.5-pro",
            use_tool_free_theme=True  # Use simpler theme agent
        )
        
        # Director metadata (could be extracted from strawman in real use)
        director_metadata = {
            'formality_level': 'high',  # Healthcare is formal
            'complexity_allowance': 'detailed'
        }
        
        try:
            if self.options.get('streaming', False):
                # Streaming mode
                if self.display:
                    self.console.print(f"\n{self.display.icon('stream')} [bold cyan]Using STREAMING mode[/bold cyan]\n")
                
                result = await self._run_streaming(strawman, director_metadata)
            else:
                # Regular mode
                result = await self._run_regular(strawman, director_metadata)
            
            processing_time = time.time() - start_time
            
            # Show final results
            if self.display and result:
                self.display.show_final_results(result, processing_time)
            
            # Export if requested
            if self.options.get('export', False) and result:
                self._export_results(result, strawman, processing_time)
            
        except Exception as e:
            if self.display:
                self.console.print(f"\n{self.display.icon('error')} [red]Error: {e}[/red]")
                if not self.options.get('quiet', False):
                    import traceback
                    self.console.print("[dim]" + traceback.format_exc() + "[/dim]")
    
    async def _run_regular(self, strawman: PresentationStrawman, director_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run in regular (non-streaming) mode"""
        if self.display:
            self.display.show_theme_progress()
        
        # Generate everything
        result = await self.orchestrator.generate_content(
            strawman=strawman,
            session_id="test_session",
            director_metadata=director_metadata,
            generate_images=not self.options.get('no_images', False)
        )
        
        # Display theme result
        if self.display and 'theme' in result:
            theme = result['theme']
            if isinstance(theme, dict):
                # Convert dict to ThemeDefinition for display
                from src.models.design_tokens import ThemeDefinition
                theme_obj = ThemeDefinition(**theme)
                self.display.show_theme_result(theme_obj)
            else:
                self.display.show_theme_result(theme)
        
        return result
    
    async def _run_streaming(self, strawman: PresentationStrawman, director_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run in streaming mode"""
        # Collect results as we stream
        result = {
            'theme': None,
            'content': [],
            'metadata': {}
        }
        
        async for update in self.orchestrator.generate_content_streaming(
            strawman=strawman,
            session_id="test_session_streaming",
            director_metadata=director_metadata,
            generate_images=not self.options.get('no_images', False)
        ):
            if self.display:
                self.display.show_streaming_update(update)
            
            # Collect data
            if update['type'] == 'theme_ready':
                result['theme'] = update['theme']
                if self.display:
                    self.display.show_theme_result(update['theme'])
            
            elif update['type'] == 'content_ready':
                # Store content
                result['content'].append({
                    'slide_id': update['slide_id'],
                    'content_manifest': update['content_manifest'].dict(),
                    'generated_images': {}
                })
            
            elif update['type'] == 'image_ready':
                # Find and update the slide with image URL
                for item in result['content']:
                    if item['slide_id'] == update['slide_id']:
                        item['generated_images']['primary'] = update.get('image_url', '')
                        break
            
            elif update['type'] == 'complete':
                result['metadata'] = {
                    'total_slides': update['total_slides'],
                    'timestamp': update['timestamp']
                }
            
            # Pause if requested
            if self.options.get('pause', False) and update['type'] in ['content_ready', 'theme_ready']:
                if self.display and not self.options.get('quiet', False):
                    self.console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
        
        return result
    
    def _export_results(self, result: Dict[str, Any], strawman: PresentationStrawman, processing_time: float):
        """Export results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = Path(__file__).parent / f"content_orchestrator_results_{timestamp}.json"
        
        # Prepare export data
        export_data = {
            "test_info": {
                "timestamp": timestamp,
                "processing_time": processing_time,
                "strawman_title": strawman.main_title,
                "total_slides": len(strawman.slides),
                "mode": "streaming" if self.options.get('streaming', False) else "regular"
            },
            "theme": result['theme'].dict() if hasattr(result['theme'], 'dict') else result['theme'],
            "content": result['content'],
            "metadata": result.get('metadata', {})
        }
        
        # Write to file
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        if self.display:
            self.console.print(f"\n{self.display.icon('check')} Results exported to: [cyan]{export_path}[/cyan]")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Beautiful CLI test for Content Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Run full pipeline
  %(prog)s --streaming            # Use streaming mode
  %(prog)s --no-images            # Skip image generation
  %(prog)s --pause                # Pause between major steps
  %(prog)s --export               # Export results to JSON
  %(prog)s --quiet                # Minimal output
  %(prog)s --no-icons             # Disable emoji icons
        """
    )
    
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Use streaming mode for real-time updates"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image generation (content only)"
    )
    
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause between major steps for review"
    )
    
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to JSON file"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (progress only)"
    )
    
    parser.add_argument(
        "--no-icons",
        action="store_true",
        help="Disable emoji icons in output"
    )
    
    args = parser.parse_args()
    
    # Convert args to options dict
    options = {
        'streaming': args.streaming,
        'no_images': args.no_images,
        'pause': args.pause,
        'export': args.export,
        'quiet': args.quiet,
        'no_icons': args.no_icons
    }
    
    # Run test
    test = ContentOrchestratorTest(options)
    await test.run_test()

if __name__ == "__main__":
    asyncio.run(main())