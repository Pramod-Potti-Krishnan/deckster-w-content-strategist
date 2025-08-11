"""
Mermaid Diagram Agent - Code-Driven Diagram Generation
=====================================================

This agent generates diagrams using Mermaid.js syntax and renders
them to SVG using MCP Python server for execution.

Supports flowcharts, sequence diagrams, Gantt charts, and more.

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import logging
import json
from typing import Dict, Any, List, Optional
import asyncio
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from src.utils.model_utils import create_model_with_fallback
from .models import DiagramSpec, MermaidOutput, MermaidSpec

logger = logging.getLogger(__name__)


class MermaidContext(BaseModel):
    """Context for Mermaid generation."""
    spec: DiagramSpec
    diagram_type: str
    theme_colors: Dict[str, str]
    font_family: str = "Inter, system-ui, sans-serif"


class MermaidSyntaxBuilder(BaseModel):
    """Output from Mermaid syntax generation."""
    mermaid_code: str = Field(description="Generated Mermaid code")
    diagram_type: str = Field(description="Type of Mermaid diagram")
    node_count: int = Field(description="Number of nodes in diagram")
    has_subgraphs: bool = Field(default=False)
    custom_styling: Optional[str] = Field(default=None)


class MermaidDiagramAgent:
    """
    Agent for generating diagrams using Mermaid.js.
    Uses pydantic_ai for code generation and MCP for rendering.
    """
    
    def __init__(self):
        """Initialize the Mermaid diagram agent."""
        self.syntax_agent = self._create_syntax_agent()
        self.render_agent = self._create_render_agent()
        
        # Tools are registered as methods below
    
    def _create_syntax_agent(self) -> Agent:
        """Create agent for Mermaid syntax generation."""
        return Agent(
            create_model_with_fallback("gemini-2.5-pro"),
            result_type=MermaidSyntaxBuilder,
            system_prompt="""You are a Mermaid.js syntax expert. Generate clean, valid Mermaid code for diagrams.
            
            Rules:
            1. Use appropriate Mermaid diagram type for the data
            2. Escape special characters properly
            3. Keep node IDs simple and meaningful
            4. Add clear labels and relationships
            5. Use subgraphs for grouping when appropriate
            6. Apply consistent styling"""
        )
    
    def _create_render_agent(self) -> Agent:
        """Create agent for rendering Mermaid to SVG."""
        return Agent(
            create_model_with_fallback("gemini-2.5-flash"),
            result_type=MermaidOutput,
            system_prompt="Render Mermaid diagrams to SVG with proper theming."
        )
    
    async def generate(self, spec: DiagramSpec) -> MermaidOutput:
        """
        Generate a Mermaid diagram from specification.
        
        Args:
            spec: Diagram specification
            
        Returns:
            MermaidOutput with rendered SVG
        """
        logger.info(f"Generating Mermaid diagram of type: {spec.diagram_type}")
        
        # Determine Mermaid diagram type
        mermaid_type = self._map_to_mermaid_type(spec.diagram_type)
        
        # Extract theme colors
        theme_colors = self._extract_theme_colors(spec.theme)
        
        # Create context
        context = MermaidContext(
            spec=spec,
            diagram_type=mermaid_type,
            theme_colors=theme_colors
        )
        
        # Generate Mermaid syntax
        syntax_result = await self._generate_mermaid_syntax(context)
        
        # Apply theming
        themed_code = self._apply_theme_to_mermaid(
            syntax_result.mermaid_code,
            theme_colors
        )
        
        # Render to SVG
        svg_output = await self._render_mermaid_to_svg(themed_code)
        
        return MermaidOutput(
            mermaid_code=syntax_result.mermaid_code,
            svg_output=svg_output,
            diagram_type=mermaid_type,
            render_time_ms=100  # Placeholder
        )
    
    def _map_to_mermaid_type(self, diagram_type: str) -> str:
        """Map diagram type to Mermaid diagram type."""
        mapping = {
            "flowchart": "flowchart",
            "sequence": "sequenceDiagram",
            "gantt": "gantt",
            "pie_chart": "pie",
            "mind_map": "mindmap",
            "timeline": "timeline",
            "journey_map": "journey",
            "architecture": "flowchart",
            "network": "flowchart",
            "process_flow": "flowchart",
            "quadrant": "quadrantChart"
        }
        
        return mapping.get(diagram_type, "flowchart")
    
    def _extract_theme_colors(self, theme: Any) -> Dict[str, str]:
        """Extract colors from theme."""
        colors = {}
        
        if hasattr(theme, 'colors'):
            for key, value in theme.colors.items():
                colors[key] = value
        elif isinstance(theme, dict) and 'colors' in theme:
            colors = theme['colors']
        
        # Defaults
        colors.setdefault("primary", "#2563eb")
        colors.setdefault("secondary", "#64748b")
        colors.setdefault("background", "#ffffff")
        colors.setdefault("text", "#1e293b")
        colors.setdefault("border", "#e2e8f0")
        
        return colors
    
    async def _generate_mermaid_syntax(self, context: MermaidContext) -> MermaidSyntaxBuilder:
        """Generate Mermaid syntax using the agent."""
        prompt = f"""Generate Mermaid {context.diagram_type} diagram for:
        
        Content: {json.dumps(context.spec.content)}
        
        Create clean, professional Mermaid code that clearly represents the data."""
        
        result = await self.syntax_agent.run(prompt, deps=context)
        return result.data
    
    def _apply_theme_to_mermaid(self, mermaid_code: str, theme_colors: Dict[str, str]) -> str:
        """Apply theme colors to Mermaid code."""
        # Add theme configuration
        theme_config = f"""
%%{{init: {{
    'theme': 'base',
    'themeVariables': {{
        'primaryColor': '{theme_colors.get("primary", "#2563eb")}',
        'primaryTextColor': '{theme_colors.get("text", "#1e293b")}',
        'primaryBorderColor': '{theme_colors.get("border", "#e2e8f0")}',
        'lineColor': '{theme_colors.get("border", "#e2e8f0")}',
        'secondaryColor': '{theme_colors.get("secondary", "#64748b")}',
        'tertiaryColor': '{theme_colors.get("background", "#ffffff")}',
        'background': '{theme_colors.get("background", "#ffffff")}',
        'mainBkg': '{theme_colors.get("primary", "#2563eb")}',
        'secondBkg': '{theme_colors.get("secondary", "#64748b")}',
        'tertiaryBkg': '{theme_colors.get("background", "#ffffff")}',
        'fontFamily': 'Inter, system-ui, sans-serif',
        'fontSize': '14px'
    }}
}}}}%%
"""
        
        return theme_config + mermaid_code
    
    async def _render_mermaid_to_svg(self, mermaid_code: str) -> str:
        """
        Render Mermaid code to SVG using mermaid-py.
        
        This uses the mermaid.ink API to render diagrams.
        """
        try:
            import mermaid
            
            logger.info("Rendering Mermaid to SVG via mermaid-py")
            
            # Create Mermaid object with the code
            mermaid_obj = mermaid.Mermaid(mermaid_code)
            
            # Get SVG string from the response
            svg = mermaid_obj.svg_response.text
            
            # Clean up the SVG (remove any script tags for safety)
            if '<script' in svg:
                import re
                svg = re.sub(r'<script[^>]*>.*?</script>', '', svg, flags=re.DOTALL)
            
            logger.info("Successfully rendered Mermaid diagram to SVG")
            return svg
            
        except Exception as e:
            logger.error(f"Failed to render Mermaid to SVG: {e}")
            
            # Fallback to placeholder
            svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <rect width="800" height="600" fill="#f8f9fa"/>
    <text x="400" y="300" text-anchor="middle" font-family="Inter" font-size="16" fill="#6c757d">
        [Mermaid Rendering Failed: {str(e)[:50]}]
    </text>
    <!-- Error: {str(e)} -->
</svg>
"""
            return svg
    
    # Tool definitions for different diagram types
    async def build_flowchart(
        ctx: RunContext[MermaidContext],
        nodes: List[Dict[str, str]],
        edges: List[Dict[str, str]]
    ) -> str:
        """Build a flowchart in Mermaid syntax."""
        lines = ["flowchart TD"]
        
        # Add nodes
        for node in nodes:
            node_id = node.get("id", "")
            label = node.get("label", "")
            shape = node.get("shape", "rectangle")
            
            if shape == "rectangle":
                lines.append(f'    {node_id}["{label}"]')
            elif shape == "diamond":
                lines.append(f'    {node_id}{{"{label}"}}')
            elif shape == "circle":
                lines.append(f'    {node_id}(("{label}"))')
        
        # Add edges
        for edge in edges:
            from_node = edge.get("from", "")
            to_node = edge.get("to", "")
            label = edge.get("label", "")
            
            if label:
                lines.append(f'    {from_node} -->|{label}| {to_node}')
            else:
                lines.append(f'    {from_node} --> {to_node}')
        
        return "\n".join(lines)
    
    async def build_sequence(
        ctx: RunContext[MermaidContext],
        participants: List[str],
        messages: List[Dict[str, str]]
    ) -> str:
        """Build a sequence diagram in Mermaid syntax."""
        lines = ["sequenceDiagram"]
        
        # Add participants
        for p in participants:
            lines.append(f"    participant {p}")
        
        # Add messages
        for msg in messages:
            from_p = msg.get("from", "")
            to_p = msg.get("to", "")
            text = msg.get("text", "")
            msg_type = msg.get("type", "sync")  # sync, async, return
            
            if msg_type == "async":
                lines.append(f"    {from_p}->>{to_p}: {text}")
            elif msg_type == "return":
                lines.append(f"    {to_p}-->{from_p}: {text}")
            else:
                lines.append(f"    {from_p}->{to_p}: {text}")
        
        return "\n".join(lines)
    
    async def build_gantt(
        ctx: RunContext[MermaidContext],
        tasks: List[Dict[str, Any]]
    ) -> str:
        """Build a Gantt chart in Mermaid syntax."""
        lines = [
            "gantt",
            "    title Project Timeline",
            "    dateFormat YYYY-MM-DD"
        ]
        
        # Add sections and tasks
        current_section = None
        for task in tasks:
            section = task.get("section")
            if section and section != current_section:
                lines.append(f"    section {section}")
                current_section = section
            
            name = task.get("name", "")
            start = task.get("start", "")
            duration = task.get("duration", "")
            
            lines.append(f"    {name} : {start}, {duration}")
        
        return "\n".join(lines)
    
    async def build_pie(
        ctx: RunContext[MermaidContext],
        data: List[Dict[str, Any]]
    ) -> str:
        """Build a pie chart in Mermaid syntax."""
        lines = ["pie title Distribution"]
        
        for item in data:
            label = item.get("label", "")
            value = item.get("value", 0)
            lines.append(f'    "{label}" : {value}')
        
        return "\n".join(lines)
    
    async def build_mindmap(
        ctx: RunContext[MermaidContext],
        root: str,
        branches: Dict[str, List[str]]
    ) -> str:
        """Build a mindmap in Mermaid syntax."""
        lines = ["mindmap", f"  root(({root}))"]
        
        for branch, items in branches.items():
            lines.append(f"    {branch}")
            for item in items:
                lines.append(f"      {item}")
        
        return "\n".join(lines)
    
    async def execute_mermaid_cli(
        ctx: RunContext[MermaidContext],
        mermaid_code: str,
        output_format: str = "svg"
    ) -> str:
        """
        Execute Mermaid CLI via MCP to render diagram.
        
        In production, this would use MCP's executeCode to run:
        - mermaid-cli (mmdc) command
        - Or a Python Mermaid rendering library
        """
        # This is where MCP integration would happen
        # For now, return placeholder
        return f"<svg><!-- Rendered from: {mermaid_code[:50]}... --></svg>"
    
    async def apply_theme_css(
        ctx: RunContext[MermaidContext],
        svg_content: str,
        css_styles: str
    ) -> str:
        """Apply CSS styling to rendered SVG."""
        # Insert CSS into SVG
        style_tag = f"<style>{css_styles}</style>"
        
        # Find </defs> or <svg> tag and insert after
        if "</defs>" in svg_content:
            svg_content = svg_content.replace("</defs>", f"</defs>{style_tag}")
        else:
            svg_content = svg_content.replace("<svg", f"<svg>{style_tag}<svg", 1)
            svg_content = svg_content.replace("<svg><svg", "<svg")
        
        return svg_content


class MermaidTemplates:
    """
    Pre-built Mermaid templates for common diagrams.
    """
    
    DECISION_FLOW = """flowchart TD
    Start([Start]) --> Decision{Make Decision}
    Decision -->|Option A| ActionA[Take Action A]
    Decision -->|Option B| ActionB[Take Action B]
    ActionA --> Result1[Result 1]
    ActionB --> Result2[Result 2]
    Result1 --> End([End])
    Result2 --> End"""
    
    USER_JOURNEY = """journey
    title User Journey
    section Discovery
      Visit Website: 5: User
      Read Content: 3: User
      Watch Demo: 4: User
    section Evaluation
      Sign Up Trial: 3: User
      Test Features: 4: User
      Compare Options: 2: User
    section Purchase
      Select Plan: 3: User
      Complete Payment: 4: User
      Onboarding: 5: User"""
    
    QUADRANT_CHART = """quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]"""