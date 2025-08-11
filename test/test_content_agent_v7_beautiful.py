#!/usr/bin/env python3
"""
Beautiful CLI Test for Content Agent V7 + Image Build Agent
===========================================================

A single test that demonstrates the split architecture:
1. Content Agent V7 - Generates all content and image specifications
2. Image Build Agent - Separate service that generates actual images

The test clearly shows the handoff between the two services, demonstrating
how Content V7 creates specifications that are then processed by the 
Image Build Agent as a separate microservice.

Usage:
    python test_content_agent_v7_beautiful.py                # Run both services
    python test_content_agent_v7_beautiful.py --pause        # Pause between slides
    python test_content_agent_v7_beautiful.py --export       # Save results
    python test_content_agent_v7_beautiful.py --quiet        # Minimal output
    python test_content_agent_v7_beautiful.py --no-icons     # Disable emojis
    python test_content_agent_v7_beautiful.py --no-images    # Only run Content V7

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
from typing import Dict, Any, List, Optional, Tuple
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
from src.agents.content_agent_v7 import ContentAgentV7, ContentManifest
from src.agents import content_agent_v7
from src.agents.image_build_agent import generate_image, ImageContentV4
from src.utils.playbooks_v4 import PlaybookSession
from src.models.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType
)

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# ============================================================================
# THEME AND STYLING
# ============================================================================

class HealthcareTheme:
    """Healthcare-themed colors and icons"""
    # Colors
    PRIMARY = "#0066CC"  # Medical blue
    SECONDARY = "#00A86B" # Medical green
    ACCENT = "#FF6B6B"   # Alert red
    BACKGROUND = "#F0F4F8" # Soft gray
    TEXT = "#2D3748"     # Dark gray
    
    # Icons (with fallback for --no-icons)
    ICONS = {
        'slide': '📊',
        'component': '🧩',
        'text': '📝',
        'analytics': '📈',
        'image': '🖼️',
        'diagram': '🔄',
        'table': '📋',
        'icon': '✨',
        'success': '✅',
        'progress': '🔄',
        'time': '⏱️',
        'stage': '🎯',
        'brief': '📋',
        'content': '📄',
        'assembly': '🔧',
        'complete': '🎉',
        'healthcare': '🏥',
        'ai': '🤖',
        'data': '💾',
        'user': '👤'
    }
    
    @classmethod
    def get_icon(cls, key: str, no_icons: bool = False) -> str:
        """Get icon with fallback for no-icons mode"""
        if no_icons:
            return ""
        return cls.ICONS.get(key, "•")

# ============================================================================
# BEAUTIFUL DISPLAY COMPONENTS
# ============================================================================

class BeautifulDisplay:
    """Handle beautiful terminal output with rich formatting"""
    
    def __init__(self, console: Console, options: Dict[str, Any]):
        self.console = console
        self.options = options
        self.no_icons = options.get('no_icons', False)
        self.theme = HealthcareTheme()
    
    def show_banner(self):
        """Display welcome banner"""
        if self.options.get('quiet'):
            return
            
        banner_text = """
╔═══════════════════════════════════════════════════════════════╗
║     CONTENT AGENT V7 + IMAGE BUILD AGENT - SPLIT TEST        ║
║                   Healthcare Digital Transformation           ║
╚═══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(
            Text(banner_text, style="bold cyan", justify="center"),
            border_style="bright_blue",
            padding=(1, 2)
        ))
        
        # Show test configuration
        config_table = Table(show_header=False, box=box.SIMPLE)
        config_table.add_column("Setting", style="dim")
        config_table.add_column("Value", style="bright_cyan")
        
        config_table.add_row("Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        config_table.add_row("Mode", "Verbose Real-time" if not self.options.get('quiet') else "Quiet")
        config_table.add_row("Icons", "Enabled" if not self.no_icons else "Disabled")
        config_table.add_row("Export", "Enabled" if self.options.get('export') else "Disabled")
        
        self.console.print(config_table)
        self.console.print()
    
    def show_strawman_overview(self, strawman: PresentationStrawman):
        """Display strawman overview in a beautiful table"""
        if self.options.get('quiet'):
            return
            
        # Main info panel
        info_text = f"""
[bold]{strawman.main_title}[/bold]
[dim]{strawman.overall_theme}[/dim]

[bold]Audience:[/bold] {strawman.target_audience}
[bold]Duration:[/bold] {strawman.presentation_duration} minutes
[bold]Design:[/bold] {strawman.design_suggestions}
[bold]Slides:[/bold] {len(strawman.slides)} slides
        """
        
        self.console.print(Panel(
            info_text.strip(),
            title=f"{self.theme.get_icon('healthcare', self.no_icons)} Presentation Overview",
            border_style="bright_blue",
            padding=(1, 2)
        ))
        
        # Slides table
        slides_table = Table(
            title="Slide Structure",
            box=box.ROUNDED,
            show_lines=True,
            header_style="bold cyan"
        )
        
        slides_table.add_column("#", style="dim", width=3)
        slides_table.add_column("Type", style="cyan", width=15)
        slides_table.add_column("Title", style="white", width=40)
        slides_table.add_column("Content", style="dim", width=20)
        
        for slide in strawman.slides:
            icon = self.theme.get_icon(slide.slide_type.split('_')[0], self.no_icons)
            content_info = []
            if slide.analytics_needed:
                content_info.append(f"{self.theme.get_icon('analytics', self.no_icons)} Analytics")
            if slide.visuals_needed:
                content_info.append(f"{self.theme.get_icon('image', self.no_icons)} Visuals")
            if slide.diagrams_needed:
                content_info.append(f"{self.theme.get_icon('diagram', self.no_icons)} Diagrams")
            
            slides_table.add_row(
                str(slide.slide_number),
                f"{icon} {slide.slide_type}",
                slide.title,
                ", ".join(content_info) or "Text only"
            )
        
        self.console.print(slides_table)
        self.console.print()
    
    def show_theme_info(self, theme: ThemeDefinition):
        """Display theme information"""
        if self.options.get('quiet'):
            return
            
        theme_tree = Tree(f"{self.theme.get_icon('ai', self.no_icons)} Theme: {theme.name}")
        
        mood_branch = theme_tree.add("Mood Keywords")
        for mood in theme.mood_keywords:
            mood_branch.add(f"[cyan]{mood}[/cyan]")
        
        visual_branch = theme_tree.add("Visual Guidelines")
        for key, value in theme.visual_guidelines.items():
            visual_branch.add(f"[dim]{key}:[/dim] {value}")
        
        self.console.print(Panel(theme_tree, border_style="green"))
        self.console.print()
    
    def show_slide_header(self, slide: Slide, index: int, total: int):
        """Display slide processing header"""
        progress_bar = self._create_progress_bar(index, total)
        
        header_text = f"""
{progress_bar}

[bold cyan]{escape(slide.title)}[/bold cyan]
[dim]Type: {slide.slide_type} | ID: {slide.slide_id}[/dim]
        """
        
        self.console.print(Panel(
            header_text.strip(),
            title=f"{self.theme.get_icon('slide', self.no_icons)} Slide {slide.slide_number}/{total}",
            border_style="bright_blue",
            padding=(0, 2)
        ))
    
    def _create_progress_bar(self, current: int, total: int) -> str:
        """Create a visual progress bar"""
        if self.no_icons:
            filled = "="
            empty = "-"
        else:
            filled = "█"
            empty = "░"
        
        bar_length = 40
        filled_length = int(bar_length * current / total)
        bar = filled * filled_length + empty * (bar_length - filled_length)
        percentage = (current / total) * 100
        
        return f"[bright_green]{bar}[/bright_green] {percentage:.0f}%"
    
    def show_stage_header(self, stage_num: int, stage_name: str):
        """Display stage header"""
        if self.options.get('quiet'):
            return
            
        stage_icons = ["🎯", "📋", "🎨", "🔧", "✨"]
        icon = stage_icons[stage_num - 1] if stage_num <= len(stage_icons) and not self.no_icons else ""
        
        self.console.print(Rule(
            f"{icon} Stage {stage_num}: {stage_name}",
            style="bright_yellow"
        ))
    
    def show_components_identified(self, components: List[str], playbooks: Dict[str, str]):
        """Display identified components and playbooks"""
        if self.options.get('quiet'):
            return
            
        # Components
        comp_table = Table(
            title="Identified Components",
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 1)
        )
        comp_table.add_column("Component", style="cyan")
        
        for comp in components:
            icon = self.theme.get_icon(comp, self.no_icons)
            comp_table.add_row(f"{icon} {comp.title()}")
        
        # Playbooks
        playbook_table = Table(
            title="Selected Playbooks",
            box=box.SIMPLE,
            header_style="bold"
        )
        playbook_table.add_column("Component", style="cyan", width=15)
        playbook_table.add_column("Playbook", style="green", width=25)
        
        for comp, playbook in playbooks.items():
            icon = self.theme.get_icon(comp, self.no_icons)
            playbook_table.add_row(f"{icon} {comp.title()}", playbook)
        
        # Display side by side
        self.console.print(Columns([comp_table, playbook_table], padding=2))
    
    def show_strategic_brief(self, brief):
        """Display a strategic brief beautifully"""
        if self.options.get('quiet'):
            return
            
        playbook_display = brief.playbook_key if brief.playbook_key else "NO PLAYBOOK KEY"
        brief_tree = Tree(
            f"{self.theme.get_icon(brief.component_type, self.no_icons)} "
            f"[bold cyan]{brief.component_type.upper()} - {playbook_display}[/bold cyan]"
        )
        
        # Instructions
        instr_branch = brief_tree.add("[bold]Instructions[/bold]")
        instr_branch.add(Text(brief.detailed_instruction, style="dim"))
        
        # Check if playbook elements were extracted
        if brief.required_elements:
            req_branch = brief_tree.add("[bold]Required Elements[/bold]")
            for key, value in brief.required_elements.items():
                if key == 'containers' and isinstance(value, list):
                    containers_branch = req_branch.add("[cyan]containers[/cyan] (from playbook)")
                    for container in value:
                        if isinstance(container, dict):
                            cont_text = f"• {container.get('tag', '?')} - {container.get('role', '?')} ({container.get('word_limit', '?')} words)"
                            containers_branch.add(cont_text)
                elif isinstance(value, list):
                    sub_branch = req_branch.add(f"[cyan]{key}[/cyan]")
                    for item in value:
                        sub_branch.add(f"• {item}")
                else:
                    req_branch.add(f"[cyan]{key}:[/cyan] {value}")
        else:
            brief_tree.add("[red]No Required Elements extracted from playbook[/red]")
        
        # Style guidelines
        if brief.style_guidelines:
            style_branch = brief_tree.add("[bold]Style Guidelines[/bold]")
            for key, value in brief.style_guidelines.items():
                style_branch.add(f"[cyan]{key}:[/cyan] {value}")
        else:
            brief_tree.add("[red]No Style Guidelines extracted from playbook[/red]")
        
        self.console.print(Panel(brief_tree, border_style="green", padding=(1, 2)))
    
    def show_content_generation_progress(self, component_types: List[str]):
        """Show progress bars for parallel content generation"""
        if self.options.get('quiet'):
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            tasks = {}
            for comp_type in component_types:
                icon = self.theme.get_icon(comp_type, self.no_icons)
                task_id = progress.add_task(
                    f"{icon} Generating {comp_type} content...",
                    total=100
                )
                tasks[comp_type] = task_id
            
            # Simulate progress
            for i in range(100):
                for comp_type, task_id in tasks.items():
                    progress.update(task_id, advance=1)
                time.sleep(0.01)
    
    async def show_content_generation_progress_async(self, component_types: List[str]):
        """Async version of progress display that can be cancelled"""
        if self.options.get('quiet'):
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            tasks = {}
            for comp_type in component_types:
                icon = self.theme.get_icon(comp_type, self.no_icons)
                task_id = progress.add_task(
                    f"{icon} Generating {comp_type} content...",
                    total=100
                )
                tasks[comp_type] = task_id
            
            # Simulate progress with async sleep
            try:
                for i in range(100):
                    for comp_type, task_id in tasks.items():
                        progress.update(task_id, advance=1)
                    await asyncio.sleep(0.02)  # Slightly slower for better visual effect
            except asyncio.CancelledError:
                # Complete all progress bars when cancelled
                for comp_type, task_id in tasks.items():
                    progress.update(task_id, completed=100)
    
    def show_raw_json_content(self, comp_type: str, content: Any, icon: str):
        """Display raw JSON content for debugging"""
        import json
        
        # Convert content to dict for JSON display
        if hasattr(content, 'model_dump'):
            content_dict = content.model_dump()
        elif hasattr(content, 'dict'):
            content_dict = content.dict()
        else:
            content_dict = str(content)
        
        # Pretty print JSON with syntax highlighting
        json_str = json.dumps(content_dict, indent=2)
        
        self.console.print(Panel(
            Syntax(json_str, "json", theme="monokai", line_numbers=False),
            title=f"{icon} {comp_type.upper()} Raw JSON Output",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def show_generated_content(self, comp_type: str, content: Any):
        """Display generated content preview"""
        # Always show Stage 3 content unless quiet mode
        if self.options.get('quiet'):
            return
            
        icon = self.theme.get_icon(comp_type, self.no_icons)
        
        # Check if raw JSON mode is enabled
        if self.options.get('raw', False):
            self.show_raw_json_content(comp_type, content, icon)
            return
        
        if comp_type == "text" and hasattr(content, 'title'):
            # Build full content display
            lines = [
                f"[bold cyan]{escape(content.title)}[/bold cyan]",
                f"[dim]Flow: {content.narrative_flow}[/dim]",
                f"[dim]Tone: {', '.join(content.tone_markers)}[/dim]",
                ""
            ]
            
            # Add HTML content blocks
            if hasattr(content, 'content_blocks'):
                for block in content.content_blocks:
                    if hasattr(block, 'role'):
                        lines.append(f"[bold yellow]{block.role.upper()}:[/bold yellow]")
                    if hasattr(block, 'content_html'):
                        
                        # Format HTML for display - escape first to prevent markup conflicts
                        html = escape(block.content_html)
                        html = html.replace('&lt;p&gt;', '  ').replace('&lt;/p&gt;', '\n')
                        html = html.replace('&lt;strong&gt;', '[bold]').replace('&lt;/strong&gt;', '[/bold]')
                        html = html.replace('&lt;em&gt;', '[italic]').replace('&lt;/em&gt;', '[/italic]')
                        html = html.replace('&lt;h3&gt;', '[bold]').replace('&lt;/h3&gt;', '[/bold]\n')
                        html = html.replace('&lt;h1&gt;', '[bold cyan]').replace('&lt;/h1&gt;', '[/bold cyan]\n')
                        html = html.replace('&lt;ul&gt;', '').replace('&lt;/ul&gt;', '')
                        html = html.replace('&lt;li&gt;', '  • ').replace('&lt;/li&gt;', '')
                        lines.append(html.strip())
                    lines.append("")
            
            # Always add debug section for HTML (no flag needed)
            lines.append("")
            lines.append("[bold red]DEBUG - Raw HTML Output:[/bold red]")
            lines.append("[dim]" + "-" * 50 + "[/dim]")
            if hasattr(content, 'content_blocks'):
                for block in content.content_blocks:
                    if hasattr(block, 'content_html') and block.content_html:
                        lines.append(f"[yellow]{escape(block.role)}:[/yellow] [cyan]{escape(block.content_html)}[/cyan]")
            lines.append("")
            
            self.console.print(Panel(
                "\n".join(lines).strip(),
                title=f"{icon} Text Content",
                border_style="cyan",
                padding=(1, 2)
            ))
        
        elif comp_type == "analytics" and hasattr(content, 'chart_type'):
            lines = [
                f"[bold green]{escape(content.title)}[/bold green]",
                f"[dim]Chart Type: {content.chart_type}[/dim]",
                ""
            ]
            
            # Add data points
            if hasattr(content, 'data_points') and content.data_points:
                lines.append("[bold yellow]Data Points:[/bold yellow]")
                for i, dp in enumerate(content.data_points[:5]):  # Show first 5
                    lines.append(f"  {i+1}. {json.dumps(dp, indent=0)}")
                if len(content.data_points) > 5:
                    lines.append(f"  ... and {len(content.data_points) - 5} more")
                lines.append("")
            
            # Add visual encoding
            if hasattr(content, 'visual_encoding'):
                lines.append("[bold yellow]Visual Encoding:[/bold yellow]")
                for key, value in content.visual_encoding.items():
                    lines.append(f"  • {key}: {value}")
                lines.append("")
            
            # Add insights
            if hasattr(content, 'insights') and content.insights:
                lines.append("[bold yellow]Key Insights:[/bold yellow]")
                for insight in content.insights:
                    lines.append(f"  → {escape(insight)}")
            
            self.console.print(Panel(
                "\n".join(lines).strip(),
                title=f"{icon} Analytics Content",
                border_style="green",
                padding=(1, 2)
            ))
        
        elif comp_type == "image" and hasattr(content, 'archetype'):
            lines = [
                f"[bold magenta]Archetype: {escape(content.archetype)}[/bold magenta]",
                f"[dim]Subject: {escape(content.primary_subject)}[/dim]",
                ""
            ]
            
            # Add composition details
            if hasattr(content, 'composition_notes'):
                lines.append(f"[bold yellow]Composition:[/bold yellow]")
                lines.append(f"  {escape(content.composition_notes)}")
                lines.append("")
            
            # Add art direction
            if hasattr(content, 'art_direction'):
                lines.append("[bold yellow]Art Direction:[/bold yellow]")
                for key, value in content.art_direction.items():
                    lines.append(f"  • {key}: {value}")
                lines.append("")
            
            # Add mood keywords
            if hasattr(content, 'mood_keywords'):
                lines.append(f"[bold yellow]Mood:[/bold yellow] {', '.join(content.mood_keywords)}")
            
            # Add alt text
            if hasattr(content, 'alt_text'):
                lines.append("")
                lines.append(f"[bold yellow]Alt Text:[/bold yellow]")
                lines.append(f"  {escape(content.alt_text)}")
            
            # Add Imagen prompt if present
            if hasattr(content, 'imagen_prompt') and content.imagen_prompt:
                lines.append("")
                lines.append("[bold cyan]Imagen 3 Prompt:[/bold cyan]")
                # Wrap long prompt
                prompt_words = content.imagen_prompt.split()
                current_line = []
                for word in prompt_words:
                    current_line.append(word)
                    if len(' '.join(current_line)) > 70:
                        lines.append(f"  {escape(' '.join(current_line[:-1]))}")
                        current_line = [word]
                if current_line:
                    lines.append(f"  {escape(' '.join(current_line))}")
            
            # Add Imagen config if present
            if hasattr(content, 'imagen_config') and content.imagen_config:
                lines.append("")
                lines.append(f"[bold cyan]Imagen Config:[/bold cyan]")
                lines.append(f"  Aspect Ratio: {content.imagen_config.get('aspectRatio', 'N/A')}")
            
            # Add generated image indicator
            if hasattr(content, 'generated_image_base64') and content.generated_image_base64:
                lines.append("")
                lines.append("[bold green]✓ Image Generated Successfully![/bold green]")
                lines.append(f"[dim]Base64 length: {len(content.generated_image_base64)} chars[/dim]")
                
                # Optionally save to file for viewing
                if self.options.get('save_images', False):
                    import base64
                    from pathlib import Path
                    
                    # Create output directory
                    output_dir = Path("test/generated_images")
                    output_dir.mkdir(exist_ok=True)
                    
                    # Save image
                    filename = f"slide_{getattr(content, 'slide_number', 'unknown')}_{content.archetype}.png"
                    filepath = output_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(content.generated_image_base64))
                    
                    lines.append(f"[dim]Saved to: {filepath}[/dim]")
            
            self.console.print(Panel(
                "\n".join(lines).strip(),
                title=f"{icon} Image Content",
                border_style="magenta",
                padding=(1, 2)
            ))
        
        elif comp_type == "diagram" and hasattr(content, 'pattern'):
            lines = [
                f"[bold blue]Pattern: {escape(content.pattern)}[/bold blue]",
                f"[dim]Flow Direction: {escape(content.flow_direction)}[/dim]",
                ""
            ]
            
            # Add core elements
            if hasattr(content, 'core_elements'):
                lines.append("[bold yellow]Core Elements:[/bold yellow]")
                for elem in content.core_elements:
                    lines.append(f"  • {escape(elem)}")
                lines.append("")
            
            # Add visual hierarchy
            if hasattr(content, 'visual_hierarchy'):
                lines.append("[bold yellow]Visual Hierarchy:[/bold yellow]")
                for i, level in enumerate(content.visual_hierarchy):
                    lines.append(f"  {i+1}. {escape(level)}")
                lines.append("")
            
            # Add annotations
            if hasattr(content, 'annotations'):
                lines.append("[bold yellow]Annotations:[/bold yellow]")
                for ann in content.annotations:
                    lines.append(f"  → {escape(ann)}")
            
            self.console.print(Panel(
                "\n".join(lines).strip(),
                title=f"{icon} Diagram Content",
                border_style="blue",
                padding=(1, 2)
            ))
        
        elif comp_type == "table" and hasattr(content, 'structure_type'):
            lines = [
                f"[bold yellow]Structure: {content.structure_type}[/bold yellow]",
                ""
            ]
            
            # Add summary
            if hasattr(content, 'summary_insight'):
                lines.append(f"[dim]{escape(content.summary_insight)}[/dim]")
                lines.append("")
            
            # Add headers and sample rows
            if hasattr(content, 'headers') and hasattr(content, 'rows'):
                # Create a simple table representation
                lines.append("[bold yellow]Table Data:[/bold yellow]")
                lines.append(f"  Headers: {' | '.join(escape(h) for h in content.headers)}")
                lines.append(f"  {'-' * 50}")
                
                # Show first few rows
                for i, row in enumerate(content.rows[:3]):
                    row_data = ' | '.join(escape(str(cell)) for cell in row)
                    lines.append(f"  {row_data}")
                
                if len(content.rows) > 3:
                    lines.append(f"  ... and {len(content.rows) - 3} more rows")
                lines.append("")
            
            # Add formatting hints
            if hasattr(content, 'formatting_hints'):
                lines.append("[bold yellow]Formatting:[/bold yellow]")
                for hint in content.formatting_hints:
                    lines.append(f"  • {escape(hint)}")
                lines.append("")
            
            # Add HTML table debug output
            if hasattr(content, 'html_table') and content.html_table:
                lines.append("[bold red]DEBUG - Raw HTML Table:[/bold red]")
                lines.append("[dim]" + "-" * 50 + "[/dim]")
                # Show first 500 chars of HTML
                html_preview = content.html_table[:500]
                if len(content.html_table) > 500:
                    html_preview += "..."
                lines.append(f"[cyan]{escape(html_preview)}[/cyan]")
                lines.append(f"[dim]Total HTML length: {len(content.html_table)} characters[/dim]")
                lines.append("")
            
            self.console.print(Panel(
                "\n".join(lines).strip(),
                title=f"{icon} Table Content",
                border_style="yellow",
                padding=(1, 2)
            ))
    
    def show_manifest_summary(self, manifest: ContentManifest):
        """Display content manifest summary"""
        if self.options.get('quiet'):
            return
            
        summary = f"""
[bold cyan]{escape(manifest.title)}[/bold cyan]

[bold]Metrics:[/bold]
• Total words: {manifest.total_word_count}
• Visual elements: {manifest.visual_count}
• Content density: {manifest.content_density}
• Layout: {manifest.structure_preference or 'default'}
        """
        
        self.console.print(Panel(
            summary.strip(),
            title=f"{self.theme.get_icon('complete', self.no_icons)} Content Assembly Complete",
            border_style="bright_green"
        ))
    
    def show_final_summary(self, total_slides: int, processing_time: float, manifests: List[ContentManifest]):
        """Display final summary dashboard"""
        # Main stats
        stats_table = Table(
            title="Processing Summary",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold cyan"
        )
        
        stats_table.add_column("Metric", style="cyan", width=30)
        stats_table.add_column("Value", style="bright_green", width=20)
        
        total_words = sum(m.total_word_count for m in manifests)
        total_visuals = sum(m.visual_count for m in manifests)
        
        # Count density distribution
        density_counts = {"light": 0, "medium": 0, "heavy": 0}
        for m in manifests:
            density_counts[m.content_density] = density_counts.get(m.content_density, 0) + 1
        density_summary = ", ".join([f"{k}: {v}" for k, v in density_counts.items() if v > 0])
        
        stats_table.add_row("Total Slides Processed", str(total_slides))
        stats_table.add_row("Total Processing Time", f"{processing_time:.2f} seconds")
        stats_table.add_row("Average Time per Slide", f"{processing_time/total_slides:.2f} seconds")
        stats_table.add_row("Total Words Generated", f"{total_words:,}")
        stats_table.add_row("Total Visual Elements", str(total_visuals))
        stats_table.add_row("Content Density Distribution", density_summary)
        
        self.console.print(stats_table)
        
        # Success message
        self.console.print(Panel(
            f"[bold green]{self.theme.get_icon('complete', self.no_icons)} "
            f"All slides processed successfully![/bold green]",
            border_style="bright_green",
            padding=(1, 2)
        ))

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
# TEST RUNNER
# ============================================================================

class BeautifulTestRunner:
    """Run the content agent test with beautiful output"""
    
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.console = Console() if RICH_AVAILABLE else None
        self.display = BeautifulDisplay(self.console, options) if RICH_AVAILABLE else None
        self.playbook_session = PlaybookSession()
    
    async def run_test(self):
        """Run the complete test"""
        # Load mock strawman
        mock_path = Path(__file__).parent / "mock_strawman.json"
        with open(mock_path, 'r') as f:
            strawman_data = json.load(f)
        
        strawman = PresentationStrawman(**strawman_data)
        
        # Create theme
        theme = self._create_test_theme()
        
        # Show banner and overview
        if self.display:
            self.display.show_banner()
            self.display.show_strawman_overview(strawman)
            self.display.show_theme_info(theme)
        
        # Determine which slides to process
        all_slides = strawman.slides
        if self.options.get('slides'):
            slide_indices = parse_slide_selection(self.options['slides'], len(all_slides))
            slides_to_process = [all_slides[i] for i in slide_indices]
        else:
            slides_to_process = all_slides
        
        # Process slides
        start_time = time.time()
        manifests = []
        
        # Create content agent
        agent = ContentAgentV7()
        
        for i, slide in enumerate(slides_to_process):
            if self.display:
                self.display.show_slide_header(slide, i + 1, len(slides_to_process))
            
            # Process slide with detailed output
            if self.options.get('verbose'):
                manifest = await self._process_slide_verbose(
                    slide, theme, strawman, manifests.copy(), i + 1
                )
            else:
                manifest = await agent.run(slide, theme, strawman, manifests.copy())
            
            manifests.append(manifest)
            
            if self.options.get('pause') and i < len(strawman.slides) - 1:
                input("\nPress Enter to continue to next slide...")
        
        # Show summary
        total_time = time.time() - start_time
        if self.display:
            self.display.show_final_summary(len(strawman.slides), total_time, manifests)
        
        # Export if requested
        if self.options.get('export'):
            self._export_results(manifests, strawman, total_time)
        
        return manifests
    
    async def _process_slide_verbose(
        self, 
        slide: Slide, 
        theme: ThemeDefinition,
        strawman: PresentationStrawman,
        completed_slides: List[ContentManifest],
        slide_index: int
    ) -> ContentManifest:
        """Process a single slide with verbose output"""
        deck_summary = f"{strawman.main_title}: {strawman.overall_theme}"
        
        # Stage 1: Component Planning
        if self.display:
            self.display.show_stage_header(1, "Component Planning")
        
        stage1_start = time.time()
        components = await content_agent_v7.identify_required_components(slide)
        component_playbooks = await content_agent_v7.select_playbook_strategies(slide, components)
        stage1_time = time.time() - stage1_start
        
        if self.display:
            self.display.show_components_identified(components, component_playbooks)
            self.console.print(f"[dim]Completed in {stage1_time:.2f}s[/dim]\n")
        
        # Convert to PlannedComponent format
        planned_components = []
        for comp_type, playbook_key in component_playbooks.items():
            planned = content_agent_v7.PlannedComponent(
                component_type=comp_type,
                selected_playbook_key=playbook_key,
                rationale=f"Selected for {slide.slide_type} slide"
            )
            planned_components.append(planned)
        
        # Stage 2: Strategic Briefing
        if self.display:
            self.display.show_stage_header(2, "Strategic Briefing")
            
            # Show what playbook content is being passed to Stage 2
            if not self.options.get('quiet'):
                self.console.print("\n[dim]Playbook content being used:[/dim]")
                for comp in planned_components:
                    playbook_data = None
                    if comp.component_type == "text":
                        playbook_data = content_agent_v7.TEXT_PLAYBOOK.get(comp.selected_playbook_key, {})
                    elif comp.component_type == "analytics":
                        playbook_data = content_agent_v7.ANALYTICS_PLAYBOOK.get(comp.selected_playbook_key, {})
                    elif comp.component_type == "image":
                        playbook_data = content_agent_v7.IMAGE_PLAYBOOK.get(comp.selected_playbook_key, {})
                    elif comp.component_type == "diagram":
                        playbook_data = content_agent_v7.DIAGRAM_PLAYBOOK.get(comp.selected_playbook_key, {})
                    elif comp.component_type == "table":
                        playbook_data = content_agent_v7.TABLE_PLAYBOOK.get(comp.selected_playbook_key, {})
                    
                    if playbook_data:
                        self.console.print(f"[cyan]{comp.component_type.upper()}[/cyan] → [green]{comp.selected_playbook_key}[/green]:")
                        if 'narrative_arc' in playbook_data:
                            self.console.print(f"  • Narrative Arc: {playbook_data['narrative_arc']}")
                        if 'html_containers' in playbook_data:
                            self.console.print(f"  • Containers: {len(playbook_data['html_containers'])} defined")
                        if 'purpose' in playbook_data:
                            self.console.print(f"  • Purpose: {playbook_data['purpose']}")
                self.console.print("")
        
        stage2_start = time.time()
        strategic_briefs = await content_agent_v7.run_strategic_briefing_agent_v2(
            planned_components,
            slide,
            theme,
            self.playbook_session
        )
        stage2_time = time.time() - stage2_start
        
        if self.display:
            for brief in strategic_briefs.briefs:
                self.display.show_strategic_brief(brief)
            self.console.print(f"[dim]Completed in {stage2_time:.2f}s[/dim]\n")
        
        # Stage 3: Content Generation
        if self.display:
            self.display.show_stage_header(3, "Content Generation")
        
        stage3_start = time.time()
        
        # Prepare specialist tasks
        specialist_tasks = []
        component_types = []
        
        for brief in strategic_briefs.briefs:
            if brief.component_type == "text":
                task = content_agent_v7.run_text_specialist_v4(
                    brief, slide, theme, deck_summary, completed_slides
                )
                specialist_tasks.append(task)
                component_types.append("text")
            elif brief.component_type == "analytics":
                task = content_agent_v7.run_analytics_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("analytics")
            elif brief.component_type == "image":
                task = content_agent_v7.run_image_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("image")
            elif brief.component_type == "diagram":
                task = content_agent_v7.run_diagram_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("diagram")
            elif brief.component_type == "table":
                task = content_agent_v7.run_table_specialist_v4(brief, slide, theme)
                specialist_tasks.append(task)
                component_types.append("table")
        
        # Show progress and run specialists
        if self.display and not self.options.get('quiet'):
            # Run progress display and actual tasks concurrently
            progress_task = asyncio.create_task(
                self.display.show_content_generation_progress_async(component_types)
            )
            
            # Run the actual specialist tasks
            specialist_results = await asyncio.gather(*specialist_tasks)
            
            # Cancel progress display once tasks are done
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
        else:
            specialist_results = await asyncio.gather(*specialist_tasks)
        
        stage3_time = time.time() - stage3_start
        
        # Map results
        component_outputs = {}
        for comp_type, result in zip(component_types, specialist_results):
            component_outputs[comp_type] = result
            if self.display:
                self.display.show_generated_content(comp_type, result)
        
        if self.display:
            self.console.print(f"[dim]Completed in {stage3_time:.2f}s[/dim]\n")
        
        # Stage 4: Assembly (optional)
        if self.options.get('raw_output', False):
            # Skip assembly - work with raw outputs
            if self.display:
                self.console.print("\n[bold yellow]📦 Raw Output Mode - Assembly Skipped[/bold yellow]")
                self.console.print("[dim]Working directly with component outputs[/dim]\n")
            
            # Create a minimal manifest for compatibility
            text_output = component_outputs.get('text')
            title = text_output.title if text_output and hasattr(text_output, 'title') else slide.title
            
            manifest = ContentManifest(
                slide_id=slide.slide_id,
                slide_type=slide.slide_type,
                structure_preference=slide.structure_preference,
                title=title,
                main_points=[],
                supporting_text=None,
                primary_visual=None,
                supporting_visuals=[],
                total_word_count=0,
                visual_count=len([k for k in component_outputs.keys() if k.startswith(('image', 'analytics', 'diagram', 'table'))]),
                content_density="medium",
                theme_elements_applied=[],
                deck_context_used=True
            )
        else:
            # Standard assembly
            if self.display:
                self.display.show_stage_header(4, "Content Assembly")
            
            stage4_start = time.time()
            # Import assembly utility
            from src.utils.content_assembly import assemble_content_manifest
            manifest = assemble_content_manifest(
                slide,
                component_outputs,
                self.playbook_session
            )
            stage4_time = time.time() - stage4_start
            
            if self.display:
                self.display.show_manifest_summary(manifest)
                self.console.print(f"[dim]Completed in {stage4_time:.2f}s[/dim]\n")
        
        # Mark completion of Content Agent V7 work
        if self.display:
            self.console.print("\n[bold green]✓ Content Agent V7 completed successfully![/bold green]")
            self.console.print("[dim]All text content and image specifications generated.[/dim]\n")
        
        # Stage 5: Image Generation (Separate Service)
        if not self.options.get('no_images', False):
            if self.display:
                # Show clear separation
                self.console.rule("[bold cyan]SWITCHING TO IMAGE BUILD AGENT SERVICE[/bold cyan]", style="cyan")
                self.console.print("\n[yellow]Note: This is a separate microservice that handles image generation[/yellow]")
                self.console.print("[yellow]Content Agent V7 has provided the image specifications[/yellow]\n")
                
                self.display.show_stage_header(5, "Image Generation Service")
            
            stage5_start = time.time()
            image_specs_to_process = []
            
            # Collect all image specifications from Content Agent V7
            for comp_type, output in component_outputs.items():
                if comp_type.startswith("image") and hasattr(output, 'imagen_prompt'):
                    image_specs_to_process.append((comp_type, output))
            
            if image_specs_to_process:
                if self.display:
                    self.console.print(f"[bold]Found {len(image_specs_to_process)} image specification(s) to process[/bold]\n")
                
                # Process each image specification through the Image Build Agent
                for comp_type, image_spec in image_specs_to_process:
                    try:
                        if self.display:
                            self.console.print(f"[bold cyan]Image Build Agent Processing:[/bold cyan]")
                            self.console.print(f"  📄 Received spec: {image_spec.archetype}")
                            self.console.print(f"  🎨 Subject: [dim]{image_spec.primary_subject[:50]}...[/dim]")
                            self.console.print(f"  📐 Aspect ratio: {image_spec.imagen_config.get('aspectRatio', '16:9')}")
                        
                        # Call the separate Image Build Agent service
                        if self.display:
                            self.console.print("  🔄 Calling Image Build Agent API...")
                        
                        image_result = await generate_image(image_spec)
                        
                        if image_result["success"]:
                            # Update the output with generated image
                            image_spec.generated_image_base64 = image_result["base64"]
                            if image_result.get("has_transparent", False):
                                image_spec.transparent_image_base64 = image_result.get("transparent_base64")
                                image_spec.has_transparent_version = True
                            
                            if self.display:
                                img_size = len(image_result['base64']) // 1024  # KB
                                self.console.print(f"  ✅ [bold green]Image generated successfully![/bold green]")
                                self.console.print(f"  📊 Size: ~{img_size}KB")
                                self.console.print(f"  🖼️  Model: {image_result['metadata']['model']}")
                                if image_result.get("has_transparent", False):
                                    self.console.print(f"  🎭 Transparent version also created")
                                self.console.print()
                        else:
                            if self.display:
                                self.console.print(f"  ❌ [red]Image generation failed: {image_result.get('error')}[/red]\n")
                    except Exception as e:
                        if self.display:
                            self.console.print(f"  ❌ [red]Image Build Agent error: {e}[/red]\n")
            
            stage5_time = time.time() - stage5_start
            if self.display:
                self.console.print(f"[bold green]✓ Image Build Agent completed[/bold green]")
                self.console.print(f"[dim]Image generation took {stage5_time:.2f}s[/dim]\n")
        else:
            if self.display:
                self.console.rule("[bold yellow]IMAGE GENERATION SKIPPED[/bold yellow]", style="yellow")
                self.console.print("\n[dim]Image Build Agent not called (--no-images flag)[/dim]")
                self.console.print("[dim]Content Agent V7 has generated image specifications only[/dim]\n")
        
        return manifest
    
    def _create_test_theme(self) -> ThemeDefinition:
        """Create healthcare theme"""
        return ThemeDefinition(
            name="Healthcare Professional",
            mood_keywords=["professional", "innovative", "trustworthy", "caring"],
            visual_guidelines={
                "color_scheme": "medical blues and whites with green accents",
                "icon_style": "modern healthcare icons",
                "chart_style": "clean data visualizations",
                "imagery": "professional medical settings and technology"
            },
            formality_level="high",
            design_tokens=DesignTokens(
                name="healthcare",
                colors={
                    "primary": ColorToken(value="#0066CC"),
                    "secondary": ColorToken(value="#00A86B"),
                    "accent": ColorToken(value="#FF6B6B"),
                    "background": ColorToken(value="#F0F4F8")
                },
                typography={
                    "heading": TypographyToken(
                        fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                        fontSize=TokenValue(value=36, type=TokenType.FONT_SIZE)
                    ),
                    "body": TypographyToken(
                        fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                        fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE)
                    )
                },
                spacing={
                    "small": DimensionToken(value=8, type=TokenType.DIMENSION),
                    "medium": DimensionToken(value=16, type=TokenType.DIMENSION),
                    "large": DimensionToken(value=32, type=TokenType.DIMENSION)
                },
                sizing={
                    "icon": DimensionToken(value=24, type=TokenType.DIMENSION)
                }
            ),
            layout_templates={}
        )
    
    def _export_results(self, manifests: List[ContentManifest], strawman: PresentationStrawman, processing_time: float):
        """Export results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = Path(__file__).parent / f"content_agent_v7_results_{timestamp}.json"
        
        results = {
            "test_info": {
                "timestamp": timestamp,
                "processing_time": processing_time,
                "strawman_title": strawman.main_title,
                "total_slides": len(strawman.slides)
            },
            "manifests": [
                {
                    "slide_number": i + 1,
                    "title": manifest.title,
                    "word_count": manifest.total_word_count,
                    "visual_count": manifest.visual_count,
                    "content_density": manifest.content_density,
                    "structure": manifest.structure_preference
                }
                for i, manifest in enumerate(manifests)
            ]
        }
        
        with open(export_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        if self.console:
            self.console.print(f"\n[green]Results exported to: {export_path}[/green]")

# ============================================================================
# MAIN
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Beautiful CLI test for Content Agent V7 with Split Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Default verbose run (all slides)
  %(prog)s --slides 1-3           # Process slides 1 through 3
  %(prog)s --slides 2,4,6        # Process specific slides
  %(prog)s --slides 5            # Process only slide 5
  %(prog)s --pause                # Pause between slides
  %(prog)s --export               # Export results to JSON
  %(prog)s --quiet                # Minimal output
  %(prog)s --no-icons             # Disable emoji icons
        """
    )
    
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause between slides for review"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to JSON file"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output mode"
    )
    parser.add_argument(
        "--no-icons",
        action="store_true",
        help="Disable emoji icons (for compatibility)"
    )
    parser.add_argument(
        "--raw", "--json",
        action="store_true",
        help="Show raw JSON output for Stage 3 content"
    )
    parser.add_argument(
        "--save-images",
        action="store_true",
        help="Save generated images to test/generated_images directory"
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image generation (only create specifications)"
    )
    parser.add_argument(
        "--raw-output",
        action="store_true",
        help="Return raw component outputs without assembly (shows more detail)"
    )
    parser.add_argument(
        "--slides",
        type=str,
        help="Specify slides to process: single (5), range (1-3), or list (1,3,5)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Verbose output (default: True)"
    )
    
    args = parser.parse_args()
    
    # Create options
    options = {
        'pause': args.pause,
        'export': args.export,
        'quiet': args.quiet,
        'no_icons': args.no_icons,
        'no_images': args.no_images,
        'raw_output': args.raw_output,
        'slides': args.slides,
        'verbose': args.verbose and not args.quiet,
        'raw': args.raw,
        'save_images': args.save_images
    }
    
    # Run test
    runner = BeautifulTestRunner(options)
    
    try:
        await runner.run_test()
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            runner.console.print("\n[yellow]Test interrupted by user[/yellow]")
        else:
            print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            runner.console.print(f"\n[red]Error: {escape(str(e))}[/red]")
            if options.get('verbose'):
                runner.console.print_exception()
        else:
            print(f"\nError: {e}")
            if options.get('verbose'):
                import traceback
                traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())