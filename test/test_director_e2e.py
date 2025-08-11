#!/usr/bin/env python3
"""
End-to-end automated testing tool for the Director agent.
Tests complete conversation flows through all states with predefined scenarios.
Supports both legacy and streamlined WebSocket protocols.
"""
import asyncio
import json
import argparse
import sys
import os
import warnings
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

# Suppress the PydanticAI warning about additionalProperties
warnings.filterwarnings("ignore", message=".*additionalProperties.*is not supported by Gemini.*")

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.director import DirectorAgent
from src.agents.intent_router import IntentRouter
from src.models.agents import StateContext, UserIntent
from src.workflows.state_machine import WorkflowOrchestrator
from src.utils.streamlined_packager import StreamlinedMessagePackager
from src.utils.message_packager import MessagePackager
from config.settings import get_settings

# Content Orchestrator imports
from src.agents.content_orchestrator import ContentOrchestrator
from src.agents.content_agent_v7 import ContentManifest, VisualSpec
from src.models.design_tokens import ThemeDefinition
from checkpoint_manager import CheckpointManager
from test_utils import (
    Colors, format_state, format_user_message, format_agent_message,
    format_error, format_success, print_separator,
    create_initial_context, add_to_history,
    format_clarifying_questions, format_confirmation_plan,
    format_strawman_summary, save_conversation, format_validation_results
)


class DirectorE2ETester:
    """Automated end-to-end tester for Director agent with protocol support."""
    
    def __init__(self, scenario_file: str = "test_scenarios.json", use_streaming: bool = False, 
                 slides_filter: str = None, generate_images: bool = True,
                 save_checkpoints: bool = False, start_stage: str = None,
                 checkpoint_file: str = None):
        """Initialize the tester with scenarios."""
        self.director = DirectorAgent()
        self.intent_router = IntentRouter()
        self.workflow = WorkflowOrchestrator()
        
        # Get settings and determine protocol
        self.settings = get_settings()
        self.use_streamlined = self.settings.USE_STREAMLINED_PROTOCOL
        
        # Content orchestrator settings
        self.use_streaming = use_streaming
        self.slides_filter = slides_filter
        self.generate_images = generate_images
        
        # Checkpoint settings
        self.save_checkpoints = save_checkpoints
        self.start_stage = start_stage
        self.checkpoint_file = checkpoint_file
        self.checkpoint_manager = CheckpointManager()
        
        # Initialize packagers for protocol handling
        self.streamlined_packager = StreamlinedMessagePackager()
        self.legacy_packager = MessagePackager()
        
        # Load test scenarios
        scenario_path = os.path.join(os.path.dirname(__file__), scenario_file)
        with open(scenario_path, 'r') as f:
            self.scenarios_data = json.load(f)
            self.scenarios = self.scenarios_data["scenarios"]
            self.validation_rules = self.scenarios_data["validation_rules"]
    
    def show_scenarios_menu(self):
        """Display available scenarios in a formatted menu."""
        print(f"\n{Colors.BOLD}🎯 Available Scenarios:{Colors.ENDC}")
        print("═" * 60)
        
        scenarios_list = [
            ("1", "default", "AI in Healthcare", "Standard presentation about AI applications in healthcare"),
            ("2", "executive", "Q3 Financial Results", "Board presentation on quarterly financial performance"),
            ("3", "technical", "Microservices Architecture", "Technical presentation for engineering team"),
            ("4", "educational", "Climate Change Basics", "Educational presentation for high school students"),
            ("5", "sales", "Product Launch", "Sales presentation for new SaaS product")
        ]
        
        for num, key, name, desc in scenarios_list:
            print(f"\n{Colors.BOLD}{num}️⃣  {name}{Colors.ENDC}")
            print(f"    {desc}")
    
    def format_streamlined_messages(self, messages: List[Any]) -> str:
        """Format streamlined messages for display."""
        output = []
        for msg in messages:
            if msg.type == "chat_message":
                if msg.payload.list_items:
                    output.append(f"{msg.payload.text}")
                    for item in msg.payload.list_items:
                        output.append(f"  • {item}")
                else:
                    output.append(msg.payload.text)
                    if msg.payload.sub_title:
                        output.append(f"\n{msg.payload.sub_title}")
            elif msg.type == "action_request":
                output.append(f"\n{msg.payload.prompt_text}")
                for action in msg.payload.actions:
                    marker = "►" if action.primary else "▷"
                    output.append(f"  {marker} {action.label}")
            elif msg.type == "slide_update":
                output.append(f"\n📊 Presentation ready: {msg.payload.metadata.main_title}")
                output.append(f"   {len(msg.payload.slides)} slides")
                output.append(f"   Theme: {msg.payload.metadata.overall_theme}")
                output.append(f"   Audience: {msg.payload.metadata.target_audience}")
                output.append(f"   Duration: {msg.payload.metadata.presentation_duration} minutes")
            elif msg.type == "status_update":
                output.append(f"⏳ {msg.payload.text}")
        return "\n".join(output)
    
    def format_slide_details(self, slide) -> str:
        """Format a single slide with all planning fields."""
        output = []
        output.append(f"\n{Colors.GREEN}Slide {slide.slide_number}: {slide.title}{Colors.ENDC}")
        output.append(f"  Type: {slide.slide_type}")
        output.append(f"  ID: {slide.slide_id}")
        output.append(f"  Narrative: {slide.narrative}")
        
        output.append(f"  Key Points:")
        for point in slide.key_points:
            output.append(f"    • {point}")
        
        # Display planning fields if present
        if hasattr(slide, 'analytics_needed') and slide.analytics_needed:
            output.append(f"  {Colors.CYAN}Analytics Needed:{Colors.ENDC}")
            output.append(f"    {slide.analytics_needed}")
            
        if hasattr(slide, 'visuals_needed') and slide.visuals_needed:
            output.append(f"  {Colors.HEADER}Visuals Needed:{Colors.ENDC}")
            output.append(f"    {slide.visuals_needed}")
            
        if hasattr(slide, 'diagrams_needed') and slide.diagrams_needed:
            output.append(f"  {Colors.YELLOW}Diagrams Needed:{Colors.ENDC}")
            output.append(f"    {slide.diagrams_needed}")
            
        if hasattr(slide, 'structure_preference') and slide.structure_preference:
            output.append(f"  {Colors.BLUE}Layout Preference:{Colors.ENDC} {slide.structure_preference}")
            
        return "\n".join(output)
    
    def _restore_context_from_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Restore context from checkpoint data."""
        from src.models.agents import StateContext, UserIntent
        
        # Restore context data
        context_data = checkpoint_data["context"]
        
        # Handle user intent restoration
        user_intent = None
        if context_data.get("user_intent"):
            # If it's a string (legacy format), map it to proper intent
            if isinstance(context_data["user_intent"], str):
                # Map old format to new intent types
                intent_map = {
                    "BUILD_PRESENTATION": "Submit_Initial_Topic",
                    "REFINE": "Submit_Refinement_Request"
                }
                intent_type = intent_map.get(context_data["user_intent"], "Submit_Initial_Topic")
                user_intent = UserIntent(intent_type=intent_type, confidence=1.0)
            else:
                # It's already a dict with proper structure
                user_intent = UserIntent(**context_data["user_intent"])
        
        # Map test states to valid StateContext states
        # For test purposes, we keep CONTENT_GENERATION state but map it for StateContext validation
        test_state = context_data["current_state"]
        state_mapping = {
            "CONTENT_GENERATION": "REFINE_STRAWMAN",  # Map to last valid state before content
            "THEME_GENERATION": "REFINE_STRAWMAN"
        }
        model_state = state_mapping.get(test_state, test_state)
        
        # Create context with required fields
        context = StateContext(
            current_state=model_state,
            conversation_history=context_data.get("conversation_history", []),
            session_data=context_data.get("session_data", {}),
            user_intent=user_intent
        )
        
        # Store the original test state for later use
        context.session_data["test_state"] = test_state
        
        return context
    
    def _is_v7_manifest(self, manifest: ContentManifest) -> bool:
        """Detect if this is a V7 ContentManifest based on structure."""
        # V7 has title as plain string (not TextContent object)
        if hasattr(manifest, 'title'):
            return isinstance(manifest.title, str)
        return False
    
    def format_content_manifest_complete(self, manifest: ContentManifest) -> str:
        """Display complete content manifest with all details - no truncation."""
        output = []
        is_v7 = self._is_v7_manifest(manifest)
        
        # Header
        output.append(f"\n{Colors.BOLD}📦 Content Manifest{Colors.ENDC}")
        output.append(f"  Content Density: {manifest.content_density}")
        # Handle both V1 and V2 manifest structures
        if hasattr(manifest, 'word_count_limit'):
            output.append(f"  Total Words: {manifest.total_word_count} / {manifest.word_count_limit}")
        else:
            output.append(f"  Total Words: {manifest.total_word_count}")
        
        # Theme integration
        if hasattr(manifest, 'deck_context_used') and manifest.deck_context_used:
            output.append(f"  {Colors.CYAN}✓ Deck context integrated{Colors.ENDC}")
        if hasattr(manifest, 'theme_elements_applied') and manifest.theme_elements_applied:
            output.append(f"  {Colors.CYAN}Theme elements: {', '.join(manifest.theme_elements_applied)}{Colors.ENDC}")
        
        # Text Content
        output.append(f"\n{Colors.GREEN}📝 Text Content:{Colors.ENDC}")
        
        # Handle both V1 (TextContent objects) and V7 (plain strings)
        if hasattr(manifest.title, 'text'):
            # V1 format
            output.append(f"  {Colors.BOLD}Title:{Colors.ENDC} {manifest.title.text}")
            output.append(f"    Word Count: {manifest.title.word_count}, Priority: {manifest.title.priority}")
            if hasattr(manifest.title, 'tone_keywords') and manifest.title.tone_keywords:
                output.append(f"    Tone Keywords: {', '.join(manifest.title.tone_keywords)}")
            if hasattr(manifest.title, 'sources') and manifest.title.sources:
                output.append(f"    Sources: {len(manifest.title.sources)} references")
        else:
            # V7 format (plain string) - Show the actual title content
            title_text = manifest.title if isinstance(manifest.title, str) else str(manifest.title)
            output.append(f"  {Colors.BOLD}Title:{Colors.ENDC} {title_text}")
        
        if manifest.main_points:
            output.append(f"\n  {Colors.BOLD}Main Points:{Colors.ENDC}")
            for i, point in enumerate(manifest.main_points, 1):
                if hasattr(point, 'text'):
                    # V1 format
                    output.append(f"    {i}. {point.text}")
                    output.append(f"       (Words: {point.word_count}, Priority: {point.priority})")
                else:
                    # V7 format (plain string) - Show the actual text content
                    point_text = point if isinstance(point, str) else str(point)
                    output.append(f"    {i}. {point_text}")
        
        if manifest.supporting_text:
            output.append(f"\n  {Colors.BOLD}Supporting Text:{Colors.ENDC}")
            if hasattr(manifest.supporting_text, 'text'):
                # V1 format
                output.append(f"    {manifest.supporting_text.text}")
                output.append(f"    (Words: {manifest.supporting_text.word_count}, Priority: {manifest.supporting_text.priority})")
            else:
                # V7 format (plain string) - Show the actual text content
                supporting_text = manifest.supporting_text if isinstance(manifest.supporting_text, str) else str(manifest.supporting_text)
                # Handle multiline supporting text
                for line in supporting_text.split('\n'):
                    output.append(f"    {line}")
        
        # Visual Specifications
        if manifest.primary_visual:
            output.append(self.format_visual_spec_complete(manifest.primary_visual, is_primary=True))
        
        if manifest.supporting_visuals:
            for i, visual in enumerate(manifest.supporting_visuals, 1):
                output.append(self.format_visual_spec_complete(visual, is_primary=False, index=i))
        
        # Content Organization (V1 only, not in V7)
        if not is_v7:
            output.append(f"\n{Colors.CYAN}📢 Content Organization:{Colors.ENDC}")
            if hasattr(manifest, 'preferred_reading_flow'):
                output.append(f"  Reading Flow: {manifest.preferred_reading_flow}")
            
            if hasattr(manifest, 'emphasis_areas') and manifest.emphasis_areas:
                output.append(f"  Emphasis Areas: {', '.join(manifest.emphasis_areas)}")
            
            if hasattr(manifest, 'grouping_suggestions') and manifest.grouping_suggestions:
                output.append(f"  Content Groupings:")
                for i, group in enumerate(manifest.grouping_suggestions, 1):
                    output.append(f"    Group {i}: {' + '.join(group)}")
        
        return "\n".join(output)
    
    def format_visual_spec_complete(self, visual, is_primary: bool = True, index: int = 1) -> str:
        """Display complete visual specification without any truncation."""
        output = []
        
        # Handle both dict and object formats
        def get_attr(obj, key, default=None):
            """Safely get attribute from dict or object"""
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)
        
        visual_type = get_attr(visual, 'visual_type', 'unknown')
        
        visual_label = "Primary Visual" if is_primary else f"Supporting Visual {index}"
        icon = {
            "chart": "📊",
            "image": "🎨",
            "diagram": "🔗",
            "icon": "🏦"
        }.get(visual_type, "🖼️")
        
        output.append(f"\n{Colors.HEADER}{icon} {visual_label} - {visual_type.upper()}{Colors.ENDC}")
        
        # Handle attributes that may not exist in V7
        priority = get_attr(visual, 'priority')
        if priority:
            output.append(f"  Priority: {priority}")
        space_req = get_attr(visual, 'space_requirement')
        if space_req:
            output.append(f"  Space Requirement: {space_req}")
        layout_pref = get_attr(visual, 'layout_preference')
        if layout_pref:
            output.append(f"  Layout Preference: {layout_pref}")
        handoff = get_attr(visual, 'handoff_ready')
        if handoff is not None:
            output.append(f"  Handoff Ready: {'✅' if handoff else '❌'}")
            
        description = get_attr(visual, 'description', 'No description')
        output.append(f"\n  Description: {description}")
        
        # Theme integration display
        theme_colors = get_attr(visual, 'theme_colors_used')
        if theme_colors:
            output.append(f"\n  {Colors.CYAN}Theme Colors Used:{Colors.ENDC}")
            for color in theme_colors:
                output.append(f"    • {color}")
        
        theme_style = get_attr(visual, 'theme_style_applied')
        if theme_style:
            output.append(f"  {Colors.CYAN}Theme Style Applied:{Colors.ENDC} {theme_style}")
        
        # Chart-specific details
        if visual_type == "chart" and get_attr(visual, 'chart_type'):
            output.append(f"\n  {Colors.CYAN}Chart Details:{Colors.ENDC}")
            chart_type = get_attr(visual, 'chart_type')
            output.append(f"    Type: {chart_type}")
            unit = get_attr(visual, 'unit')
            if unit:
                output.append(f"    Unit: {unit}")
            
            axes = get_attr(visual, 'axes')
            if axes:
                output.append(f"    Axes:")
                x_axis = get_attr(axes, 'x_axis') or get_attr(axes, 'x')
                if x_axis:
                    output.append(f"      X-axis: {x_axis}")
                y_axis = get_attr(axes, 'y_axis') or get_attr(axes, 'y')
                if y_axis:
                    output.append(f"      Y-axis: {y_axis}")
            
            data_points = get_attr(visual, 'data_points')
            if data_points:
                output.append(f"\n    {Colors.BOLD}Data Points ({len(data_points)}):{Colors.ENDC}")
                for dp in data_points:
                    if hasattr(dp, 'label') and hasattr(dp, 'value'):
                        output.append(f"      • {dp.label}: {dp.value}")
                    elif isinstance(dp, dict):
                        label = dp.get('label', dp.get('name', 'Unknown'))
                        value = dp.get('value', dp.get('y', dp.get('count', 'N/A')))
                        output.append(f"      • {label}: {value}")
                    if hasattr(dp, 'series_a') and hasattr(dp, 'series_b'):
                        if dp.series_a is not None or dp.series_b is not None:
                            series_parts = []
                            if dp.series_a is not None:
                                series_parts.append(f"Series A: {dp.series_a}")
                            if dp.series_b is not None:
                                series_parts.append(f"Series B: {dp.series_b}")
                            output.append(f"        ({', '.join(series_parts)})")
            
            data_insights = get_attr(visual, 'data_insights')
            if data_insights:
                output.append(f"\n    {Colors.BOLD}Data Insights:{Colors.ENDC}")
                output.append(f"    {data_insights}")
        
        # Image-specific details
        elif visual_type == "image":
            output.append(f"\n  {Colors.CYAN}Image Details:{Colors.ENDC}")
            image_style = get_attr(visual, 'image_style')
            if image_style:
                output.append(f"    Style: {image_style}")
            style_keywords = get_attr(visual, 'style_keywords')
            if style_keywords:
                output.append(f"    Keywords: {', '.join(style_keywords)}")
            composition = get_attr(visual, 'composition')
            if composition:
                output.append(f"    Composition: {composition}")
            lighting = get_attr(visual, 'lighting')
            if lighting:
                output.append(f"    Lighting: {lighting}")
            
            image_prompt = get_attr(visual, 'image_prompt')
            if image_prompt:
                output.append(f"\n    {Colors.BOLD}Full Image Prompt ({len(image_prompt)} chars):{Colors.ENDC}")
                # Display the ENTIRE prompt without truncation
                output.append(f"    {image_prompt}")
            
            negative_prompt = get_attr(visual, 'negative_prompt')
            if negative_prompt:
                output.append(f"\n    {Colors.BOLD}Negative Prompt:{Colors.ENDC}")
                output.append(f"    {negative_prompt}")
        
        # Diagram-specific details
        elif visual_type == "diagram" and get_attr(visual, 'diagram_type'):
            output.append(f"\n  {Colors.CYAN}Diagram Details:{Colors.ENDC}")
            diagram_type = get_attr(visual, 'diagram_type')
            output.append(f"    Type: {diagram_type}")
            layout_dir = get_attr(visual, 'layout_direction')
            if layout_dir:
                output.append(f"    Layout Direction: {layout_dir}")
            
            nodes = get_attr(visual, 'nodes')
            if nodes:
                output.append(f"\n    {Colors.BOLD}Nodes ({len(nodes)}):{Colors.ENDC}")
                for node in nodes:
                    if hasattr(node, 'id') and hasattr(node, 'label'):
                        output.append(f"      [{node.id}] {node.label}")
                        parts = []
                        if hasattr(node, 'type'):
                            parts.append(f"Type: {node.type}")
                        if hasattr(node, 'shape'):
                            parts.append(f"Shape: {node.shape}")
                        if hasattr(node, 'color'):
                            parts.append(f"Color: {node.color}")
                        if parts:
                            output.append(f"        {', '.join(parts)}")
                    elif isinstance(node, dict):
                        output.append(f"      [{node.get('id', 'unknown')}] {node.get('label', 'Unnamed')}")
                        parts = []
                        if 'type' in node:
                            parts.append(f"Type: {node['type']}")
                        if 'shape' in node:
                            parts.append(f"Shape: {node['shape']}")
                        if 'color' in node:
                            parts.append(f"Color: {node['color']}")
                        if parts:
                            output.append(f"        {', '.join(parts)}")
            
            connections = get_attr(visual, 'connections')
            if connections:
                output.append(f"\n    {Colors.BOLD}Connections ({len(connections)}):{Colors.ENDC}")
                for conn in connections:
                    if hasattr(conn, 'from_node') and hasattr(conn, 'to_node'):
                        label_text = f" '{conn.label}'" if hasattr(conn, 'label') and conn.label else ""
                        output.append(f"      {conn.from_node} → {conn.to_node}{label_text}")
                        parts = []
                        if hasattr(conn, 'type'):
                            parts.append(f"Type: {conn.type}")
                        if hasattr(conn, 'line_style'):
                            parts.append(f"Style: {conn.line_style}")
                        if parts:
                            output.append(f"        {', '.join(parts)}")
                    elif isinstance(conn, dict):
                        from_key = 'from' if 'from' in conn else 'from_node'
                        to_key = 'to' if 'to' in conn else 'to_node'
                        label_text = f" '{conn['label']}'" if 'label' in conn and conn['label'] else ""
                        output.append(f"      {conn.get(from_key, 'unknown')} → {conn.get(to_key, 'unknown')}{label_text}")
                        parts = []
                        if 'type' in conn:
                            parts.append(f"Type: {conn['type']}")
                        if 'style' in conn or 'line_style' in conn:
                            parts.append(f"Style: {conn.get('style', conn.get('line_style', 'solid'))}")
                        if parts:
                            output.append(f"        {', '.join(parts)}")
        
        return "\n".join(output)
    
    def format_theme_details(self, theme: ThemeDefinition) -> str:
        """Display comprehensive theme information without any limiting."""
        output = []
        
        output.append(f"\n{Colors.BOLD}🎨 Theme Definition: {theme.name}{Colors.ENDC}")
        output.append("═" * 80)
        
        # Formality and complexity from director
        output.append(f"\n{Colors.GREEN}📋 Director Context:{Colors.ENDC}")
        output.append(f"  Formality Level: {theme.formality_level}")
        output.append(f"  Complexity Allowance: {theme.complexity_allowance}")
        
        # Mood keywords if present (backward compatibility)
        if hasattr(theme, 'mood_keywords') and theme.mood_keywords:
            output.append(f"\n{Colors.GREEN}🎭 Mood & Tone:{Colors.ENDC}")
            output.append(f"  Keywords ({len(theme.mood_keywords)}): {', '.join(theme.mood_keywords)}")
        
        # Theme metadata if present
        if hasattr(theme, 'metadata') and theme.metadata:
            output.append(f"\n{Colors.HEADER}📋 Metadata:{Colors.ENDC}")
            for key, value in theme.metadata.items():
                output.append(f"  {key}: {value}")
        
        # Color palette - Show ALL colors
        output.append(f"\n{Colors.CYAN}🎨 Color Palette (Complete):{Colors.ENDC}")
        if hasattr(theme, 'design_tokens') and hasattr(theme.design_tokens, 'colors'):
            colors_dict = theme.design_tokens.colors
            if colors_dict:
                # Debug: Check what type colors_dict is
                if isinstance(colors_dict, dict):
                    for color_name, color_token in colors_dict.items():
                        # Handle both ColorToken objects and direct values
                        if hasattr(color_token, 'value'):
                            output.append(f"  {color_name}: {color_token.value}")
                            if hasattr(color_token, 'description') and color_token.description:
                                output.append(f"    Description: {color_token.description}")
                        elif isinstance(color_token, str):
                            # Direct hex value
                            output.append(f"  {color_name}: {color_token}")
                        else:
                            # Debug: Show what we got
                            output.append(f"  {color_name}: [Unknown type: {type(color_token)}]")
                else:
                    output.append(f"  [ERROR: colors is not a dict, it's {type(colors_dict)}]")
            else:
                output.append(f"  [No colors found in design_tokens]")
        else:
            output.append(f"  [No design_tokens.colors found]")
            # Debug: Show what attributes theme has
            if hasattr(theme, '__dict__'):
                output.append(f"  [DEBUG: Theme attributes: {list(theme.__dict__.keys())}]")
        
        # Typography - Show ALL font specifications with complete details
        output.append(f"\n{Colors.YELLOW}📝 Typography (Complete):{Colors.ENDC}")
        if hasattr(theme, 'design_tokens') and hasattr(theme.design_tokens, 'typography'):
            typography_dict = theme.design_tokens.typography
            if typography_dict:
                if isinstance(typography_dict, dict):
                    for font_role, font_spec in typography_dict.items():
                        output.append(f"  {font_role}:")
                        # Handle TypographyToken objects
                        if hasattr(font_spec, 'fontFamily'):
                            if hasattr(font_spec.fontFamily, 'value'):
                                output.append(f"    Font Family: {font_spec.fontFamily.value}")
                            if hasattr(font_spec, 'fontSize') and hasattr(font_spec.fontSize, 'value'):
                                output.append(f"    Font Size: {font_spec.fontSize.value}px")
                            if hasattr(font_spec, 'fontWeight') and font_spec.fontWeight and hasattr(font_spec.fontWeight, 'value'):
                                output.append(f"    Font Weight: {font_spec.fontWeight.value}")
                            if hasattr(font_spec, 'lineHeight') and font_spec.lineHeight and hasattr(font_spec.lineHeight, 'value'):
                                output.append(f"    Line Height: {font_spec.lineHeight.value}")
                            if hasattr(font_spec, 'letterSpacing') and font_spec.letterSpacing and hasattr(font_spec.letterSpacing, 'value'):
                                output.append(f"    Letter Spacing: {font_spec.letterSpacing.value}")
                        # Handle dict format (simplified)
                        elif isinstance(font_spec, dict):
                            if 'family' in font_spec:
                                output.append(f"    Font Family: {font_spec['family']}")
                            if 'size' in font_spec:
                                output.append(f"    Font Size: {font_spec['size']}px")
                            if 'weight' in font_spec:
                                output.append(f"    Font Weight: {font_spec['weight']}")
                            if 'lineHeight' in font_spec:
                                output.append(f"    Line Height: {font_spec['lineHeight']}")
                        else:
                            output.append(f"    [Unknown font spec type: {type(font_spec)}]")
                else:
                    output.append(f"  [ERROR: typography is not a dict, it's {type(typography_dict)}]")
            else:
                output.append(f"  [No typography found in design_tokens]")
        else:
            output.append(f"  [No design_tokens.typography found]")
        
        # Spacing scale - Show if present
        if hasattr(theme.design_tokens, 'spacing') and theme.design_tokens.spacing:
            output.append(f"\n{Colors.BLUE}📏 Spacing Scale:{Colors.ENDC}")
            for space_name, space_token in theme.design_tokens.spacing.items():
                if hasattr(space_token, 'value') and hasattr(space_token, 'unit'):
                    output.append(f"  {space_name}: {space_token.value}{space_token.unit}")
        
        # Sizing scale - Show if present
        if hasattr(theme.design_tokens, 'sizing') and theme.design_tokens.sizing:
            output.append(f"\n{Colors.BLUE}📐 Sizing Scale:{Colors.ENDC}")
            for size_name, size_token in theme.design_tokens.sizing.items():
                if hasattr(size_token, 'value') and hasattr(size_token, 'unit'):
                    output.append(f"  {size_name}: {size_token.value}{size_token.unit}")
        
        # Shadows - Show if present
        if hasattr(theme.design_tokens, 'shadows') and theme.design_tokens.shadows:
            output.append(f"\n{Colors.HEADER}🌑 Shadows:{Colors.ENDC}")
            for shadow_name, shadow_token in theme.design_tokens.shadows.items():
                if hasattr(shadow_token, 'value'):
                    output.append(f"  {shadow_name}: {shadow_token.value}")
        
        # Borders - Show if present
        if hasattr(theme.design_tokens, 'borders') and theme.design_tokens.borders:
            output.append(f"\n{Colors.HEADER}🔲 Borders:{Colors.ENDC}")
            for border_name, border_token in theme.design_tokens.borders.items():
                if hasattr(border_token, 'value'):
                    output.append(f"  {border_name}: {border_token.value}")
        
        # Visual guidelines - Show if present (backward compatibility)
        if hasattr(theme, 'visual_guidelines') and theme.visual_guidelines:
            output.append(f"\n{Colors.HEADER}🎯 Visual Guidelines:{Colors.ENDC}")
            for key, value in theme.visual_guidelines.items():
                if isinstance(value, list):
                    output.append(f"  {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
                else:
                    output.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Layout templates - Show if present (backward compatibility)
        if hasattr(theme, 'layout_templates') and theme.layout_templates and len(theme.layout_templates) > 0:
            output.append(f"\n{Colors.BLUE}📐 Layout Templates:{Colors.ENDC}")
            output.append(f"  Total Templates: {len(theme.layout_templates)}")
            for template_name, template in theme.layout_templates.items():
                output.append(f"\n  📄 {template_name}:")
                if hasattr(template, 'emphasis'):
                    output.append(f"    Emphasis: {template.emphasis}")
                if hasattr(template, 'reading_flow'):
                    output.append(f"    Reading Flow: {template.reading_flow}")
                if hasattr(template, 'description') and template.description:
                    output.append(f"    Description: {template.description}")
                
                # Show zones with dimensions
                if hasattr(template, 'zones') and template.zones:
                    output.append(f"    Zones ({len(template.zones)}):")
                    for zone_name, zone in template.zones.items():
                        if hasattr(zone, 'leftInset') and hasattr(zone, 'topInset') and hasattr(zone, 'width') and hasattr(zone, 'height'):
                            output.append(f"      • {zone_name}: [{zone.leftInset}, {zone.topInset}] {zone.width}x{zone.height} units")
                            if hasattr(zone, 'canExpand') and zone.canExpand:
                                output.append(f"        (expandable)")
        
        # Show strawman context if present
        if hasattr(theme, 'strawman_context') and theme.strawman_context:
            output.append(f"\n{Colors.YELLOW}📖 Strawman Context:{Colors.ENDC}")
            for key, value in theme.strawman_context.items():
                output.append(f"  {key}: {value}")
        
        # Add note about simplified theme
        output.append(f"\n{Colors.HEADER}💡 Note: This is a SIMPLIFIED theme focusing only on colors and fonts.{Colors.ENDC}")
        output.append(f"{Colors.HEADER}   Layout and visual guidelines are handled separately by other agents.{Colors.ENDC}")
        
        return "\n".join(output)
    
    def display_slide_content_realtime(self, slide_num: int, slide_id: str, manifest) -> str:
        """Display a single slide's content in real-time during generation."""
        output = []
        output.append(f"\n{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
        output.append(f"{Colors.GREEN}✅ Slide {slide_num} Generated: {slide_id}{Colors.ENDC}")
        output.append(f"{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
        
        # Display the actual content
        if hasattr(manifest, 'title') or isinstance(manifest, dict):
            title = manifest.title if hasattr(manifest, 'title') else manifest.get('title', 'No title')
            output.append(f"\n{Colors.BOLD}📌 Title:{Colors.ENDC} {title}")
        
        # Main points
        main_points = getattr(manifest, 'main_points', None) or (manifest.get('main_points') if isinstance(manifest, dict) else None)
        if main_points:
            output.append(f"\n{Colors.CYAN}📝 Main Points:{Colors.ENDC}")
            for i, point in enumerate(main_points, 1):
                output.append(f"  {i}. {point}")
        
        # Supporting text
        supporting = getattr(manifest, 'supporting_text', None) or (manifest.get('supporting_text') if isinstance(manifest, dict) else None)
        if supporting:
            output.append(f"\n{Colors.YELLOW}💬 Supporting Text:{Colors.ENDC}")
            for line in str(supporting).split('\n'):
                output.append(f"  {line}")
        
        # Visual information
        primary_visual = getattr(manifest, 'primary_visual', None) or (manifest.get('primary_visual') if isinstance(manifest, dict) else None)
        if primary_visual:
            visual_type = getattr(primary_visual, 'visual_type', None) or (primary_visual.get('visual_type') if isinstance(primary_visual, dict) else 'unknown')
            description = getattr(primary_visual, 'description', None) or (primary_visual.get('description') if isinstance(primary_visual, dict) else 'No description')
            output.append(f"\n{Colors.HEADER}🎨 Visual: {visual_type}{Colors.ENDC}")
            output.append(f"  Description: {description}")
        
        # Content metrics
        word_count = getattr(manifest, 'total_word_count', None) or (manifest.get('total_word_count') if isinstance(manifest, dict) else 0)
        density = getattr(manifest, 'content_density', None) or (manifest.get('content_density') if isinstance(manifest, dict) else 'unknown')
        output.append(f"\n{Colors.BLUE}📊 Metrics:{Colors.ENDC}")
        output.append(f"  Word Count: {word_count}")
        output.append(f"  Content Density: {density}")
        
        return "\n".join(output)
    
    def format_content_orchestrator_result(self, result: Dict[str, Any]) -> str:
        """Format the complete ContentOrchestrator result with theme, content, and images."""
        output = []
        
        # Theme section
        if 'theme' in result:
            theme_data = result['theme']
            if isinstance(theme_data, dict):
                # Create ThemeDefinition from dict for display
                theme = ThemeDefinition(**theme_data)
            else:
                theme = theme_data
            output.append(self.format_theme_details(theme))
        
        # Content section
        output.append(f"\n{Colors.BOLD}📝 Generated Content:{Colors.ENDC}")
        output.append("═" * 80)
        
        if 'content' in result:
            for i, content_item in enumerate(result['content']):
                slide_id = content_item['slide_id']
                manifest_data = content_item['content_manifest']
                
                # Create ContentManifest from dict if needed
                if isinstance(manifest_data, dict):
                    # For dict format, title is already a string in V7
                    manifest = type('ContentManifest', (), manifest_data)()
                else:
                    manifest = manifest_data
                
                output.append(f"\n{Colors.BOLD}Slide {i+1} ({slide_id}):{Colors.ENDC}")
                output.append(self.format_content_manifest_complete(manifest))
                
                # Show generated images or indicate if skipped
                if content_item.get('generated_images'):
                    output.append(f"\n{Colors.GREEN}🖼️  Generated Images:{Colors.ENDC}")
                    for img_type, img_data in content_item['generated_images'].items():
                        if img_data:
                            # Show image name/ID instead of base64 data
                            output.append(f"  • {img_type}: Image generated successfully")
                            if isinstance(img_data, str) and len(img_data) > 100:
                                output.append(f"    Size: ~{len(img_data) // 1000}KB (base64)")
                            else:
                                output.append(f"    Data: {img_data}")
                elif manifest and (manifest.primary_visual or manifest.supporting_visuals):
                    # Visual specs exist but no images generated
                    if not self.generate_images:
                        output.append(f"\n{Colors.YELLOW}🖼️  Images: Skipped (--no-images flag){Colors.ENDC}")
                    else:
                        output.append(f"\n{Colors.YELLOW}🖼️  Images: No images generated{Colors.ENDC}")
                
                if i < len(result['content']) - 1:
                    output.append(f"\n{Colors.CYAN}{'─' * 60}{Colors.ENDC}")
        
        # Metadata section
        if 'metadata' in result:
            output.append(f"\n\n{Colors.BOLD}📊 Generation Metadata:{Colors.ENDC}")
            meta = result['metadata']
            output.append(f"  Total slides: {meta.get('total_slides', 'N/A')}")
            output.append(f"  Main title: {meta.get('main_title', 'N/A')}")
            output.append(f"  Target audience: {meta.get('target_audience', 'N/A')}")
            output.append(f"  Duration: {meta.get('presentation_duration', 'N/A')} minutes")
            output.append(f"  Generated at: {meta.get('generated_at', 'N/A')}")
        
        return "\n".join(output)
    
    def filter_slides(self, slides: List) -> List:
        """Filter slides based on the slides_filter parameter."""
        if not self.slides_filter:
            return slides
            
        # Parse the filter
        if '-' in self.slides_filter:
            # Range format: "1-3" means slides 1, 2, 3
            start, end = self.slides_filter.split('-')
            start_idx = int(start) - 1  # Convert to 0-based index
            end_idx = int(end)  # Keep as 1-based for slicing
            filtered = slides[start_idx:end_idx]
            print(f"{Colors.CYAN}Limiting to slides {start}-{end} ({len(filtered)} slides){Colors.ENDC}")
            return filtered
        elif ',' in self.slides_filter:
            # List format: "1,3,5" means slides 1, 3, and 5
            indices = [int(x.strip()) - 1 for x in self.slides_filter.split(',')]
            filtered = [slides[i] for i in indices if i < len(slides)]
            print(f"{Colors.CYAN}Selecting slides: {self.slides_filter} ({len(filtered)} slides){Colors.ENDC}")
            return filtered
        else:
            # Single slide: "2" means only slide 2
            idx = int(self.slides_filter) - 1
            if idx < len(slides):
                filtered = [slides[idx]]
                print(f"{Colors.CYAN}Selecting only slide {self.slides_filter}{Colors.ENDC}")
                return filtered
            else:
                print(f"{Colors.YELLOW}Warning: Slide {self.slides_filter} not found, using all slides{Colors.ENDC}")
                return slides
    
    def show_interactive_menu(self) -> str:
        """Show interactive menu and get user choice."""
        protocol_status = f"{'Streamlined' if self.use_streamlined else 'Legacy'} Protocol"
        print(f"\n{Colors.BOLD}🎯 Deckster E2E Test Suite ({protocol_status}){Colors.ENDC}")
        print("═" * 60)
        
        self.show_scenarios_menu()
        
        print(f"\n{Colors.YELLOW}Please select a scenario (1-5) or 'q' to quit:{Colors.ENDC} ", end="")
        
        scenario_map = {
            "1": "default",
            "2": "executive", 
            "3": "technical",
            "4": "educational",
            "5": "sales"
        }
        
        while True:
            choice = input().strip().lower()
            if choice == 'q':
                print(f"{Colors.YELLOW}Exiting...{Colors.ENDC}")
                return None
            elif choice in scenario_map:
                return scenario_map[choice]
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1-5 or 'q':{Colors.ENDC} ", end="")
    
    async def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a complete test scenario."""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.scenarios[scenario_name]
        print(f"\n{Colors.BOLD}🎬 Running Scenario: {scenario['name']}{Colors.ENDC}")
        print(f"📖 Description: {scenario['description']}")
        
        # Show checkpoint info if applicable
        if self.start_stage or self.checkpoint_file:
            print(f"{Colors.CYAN}🔄 Using checkpoint to start from: {self.start_stage or 'loaded stage'}{Colors.ENDC}")
        if self.save_checkpoints:
            print(f"{Colors.YELLOW}💾 Checkpoints will be saved at each stage{Colors.ENDC}")
        
        print_separator()
        
        # Check debug mode
        debug_mode = os.getenv('DEBUG', '').lower() == 'true'
        
        results = {
            "scenario": scenario_name,
            "name": scenario["name"],
            "passed": True,
            "errors": [],
            "states_completed": [],
            "outputs": {}
        }
        
        # Initialize context and load checkpoint if specified
        context = None
        checkpoint_data = None
        skip_to_stage = None
        
        if self.checkpoint_file:
            # Load from specific checkpoint file
            try:
                checkpoint_data = self.checkpoint_manager.load_checkpoint_file(self.checkpoint_file)
                skip_to_stage = checkpoint_data["stage"]
                context = self._restore_context_from_checkpoint(checkpoint_data)
                results["outputs"] = checkpoint_data.get("stage_outputs", {})
                print(f"{Colors.GREEN}✅ Loaded checkpoint from: {self.checkpoint_file}{Colors.ENDC}")
                print(f"   Resuming from stage: {skip_to_stage}")
            except Exception as e:
                print(format_error(f"Failed to load checkpoint: {e}"))
                return results
        elif self.start_stage:
            # Load checkpoint for specified stage
            try:
                checkpoint_data = self.checkpoint_manager.load_checkpoint(scenario_name, self.start_stage)
                skip_to_stage = self.start_stage
                context = self._restore_context_from_checkpoint(checkpoint_data)
                results["outputs"] = checkpoint_data.get("stage_outputs", {})
                print(f"{Colors.GREEN}✅ Loaded checkpoint for stage: {self.start_stage}{Colors.ENDC}")
            except FileNotFoundError:
                print(format_error(f"No checkpoint found for {scenario_name}/{self.start_stage}"))
                print("Run with --save-checkpoints first to generate checkpoints")
                return results
            except Exception as e:
                print(format_error(f"Failed to load checkpoint: {e}"))
                return results
        
        if not context:
            # Initialize fresh context
            context = create_initial_context()
        
        try:
            # Define stage execution flags based on skip_to_stage
            should_skip = {
                "PROVIDE_GREETING": False,
                "ASK_CLARIFYING_QUESTIONS": False,
                "CREATE_CONFIRMATION_PLAN": False,
                "GENERATE_STRAWMAN": False,
                "REFINE_STRAWMAN": False,
                "CONTENT_GENERATION": False
            }
            
            if skip_to_stage:
                # Skip all stages before the target stage
                stage_index = self.checkpoint_manager.get_stage_index(skip_to_stage)
                for i, stage in enumerate(self.checkpoint_manager.STAGES):
                    if i < stage_index:
                        should_skip[stage] = True
                        results["states_completed"].append(stage)  # Mark as completed from checkpoint
            
            # State 1: PROVIDE_GREETING
            if not should_skip["PROVIDE_GREETING"]:
                print(f"\n{format_state('PROVIDE_GREETING')}")
                print("─" * 60)
                greeting = await self.director.process(context)
                
                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="PROVIDE_GREETING",
                        agent_output=greeting,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                else:
                    print(format_agent_message(greeting))
                    
                add_to_history(context, "assistant", greeting)
                results["states_completed"].append("PROVIDE_GREETING")
                results["outputs"]["greeting"] = greeting
                
                # Simulate user providing initial topic
                user_topic = scenario["responses"]["initial_topic"]
                print(format_user_message(user_topic))
                add_to_history(context, "user", user_topic)
                
                # Classify intent and transition to next state
                intent = await self.intent_router.classify(
                    user_topic, 
                    {
                        'current_state': context.current_state,
                        'recent_history': context.conversation_history[-3:] if context.conversation_history else []
                    }
                )
                context.user_intent = intent
                
                # Save initial topic to session data (simulating what websocket handler does)
                context.session_data['user_initial_request'] = user_topic
                context.current_state = "ASK_CLARIFYING_QUESTIONS"
                
                # Save checkpoint if enabled
                if self.save_checkpoints:
                    self.checkpoint_manager.save_checkpoint(
                        scenario_name,
                        "ASK_CLARIFYING_QUESTIONS",
                        context,
                        results["outputs"]
                    )
            
            # State 2: ASK_CLARIFYING_QUESTIONS
            if not should_skip["ASK_CLARIFYING_QUESTIONS"]:
                print(f"\n{format_state('ASK_CLARIFYING_QUESTIONS')}")
                print("─" * 60)
                questions = await self.director.process(context)
                
                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="ASK_CLARIFYING_QUESTIONS",
                        agent_output=questions,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                else:
                    print(format_agent_message(format_clarifying_questions(questions)))
                    
                add_to_history(context, "assistant", questions)
                results["states_completed"].append("ASK_CLARIFYING_QUESTIONS")
                results["outputs"]["questions"] = questions
                
                # Validate questions
                if not self._validate_questions(questions, results):
                    return results
                
                # Simulate user answering questions
                user_answers = "\n".join(scenario["responses"]["clarifying_answers"])
                print(format_user_message(user_answers))
                add_to_history(context, "user", user_answers)
                
                # Save clarifying answers to session data
                context.session_data['clarifying_answers'] = {
                    "raw_answers": user_answers,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Transition to CREATE_CONFIRMATION_PLAN
                context.current_state = "CREATE_CONFIRMATION_PLAN"
            
            # State 3: CREATE_CONFIRMATION_PLAN
            if not should_skip["CREATE_CONFIRMATION_PLAN"]:
                print(f"\n{format_state('CREATE_CONFIRMATION_PLAN')}")
                print("─" * 60)
                plan = await self.director.process(context)
                
                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="CREATE_CONFIRMATION_PLAN",
                        agent_output=plan,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                    print(f"{Colors.CYAN}[Streamlined: {len(messages)} messages]{Colors.ENDC}")
                else:
                    print(format_agent_message(format_confirmation_plan(plan)))
                    
                add_to_history(context, "assistant", plan)
                results["states_completed"].append("CREATE_CONFIRMATION_PLAN")
                results["outputs"]["plan"] = plan
                
                # Validate plan
                if not self._validate_plan(plan, scenario, results):
                    return results
                
                # Simulate user accepting plan
                user_response = scenario["responses"]["plan_response"]
                print(format_user_message(user_response))
                add_to_history(context, "user", user_response)
                
                # Save confirmation plan to session data
                context.session_data['confirmation_plan'] = plan.model_dump() if hasattr(plan, 'model_dump') else plan
                
                # Transition to GENERATE_STRAWMAN
                context.current_state = "GENERATE_STRAWMAN"
            
            # State 4: GENERATE_STRAWMAN
            strawman = None
            if should_skip["GENERATE_STRAWMAN"] and "strawman" in results["outputs"]:
                # Get strawman from checkpoint
                strawman = results["outputs"]["strawman"]
            elif not should_skip["GENERATE_STRAWMAN"]:
                print(f"\n{format_state('GENERATE_STRAWMAN')}")
                print("─" * 60)
            
                # For streamlined, show status update first
                if self.use_streamlined:
                    status_msg = self.streamlined_packager.create_pre_generation_status(
                        session_id=f"test_{scenario_name}",
                        state="GENERATE_STRAWMAN"
                    )
                    print(format_agent_message(f"⏳ {status_msg.payload.text}"))
                
                strawman = await self.director.process(context)
                
                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="GENERATE_STRAWMAN",
                        agent_output=strawman,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                    print(f"{Colors.CYAN}[Streamlined: {len(messages)} messages with structured JSON data]{Colors.ENDC}")
                    
                    # Show detailed slide content from the slide_update message
                    slide_update_msg = next((msg for msg in messages if msg.type == "slide_update"), None)
                    if slide_update_msg:
                        print(f"\n{Colors.BOLD}📄 Detailed Slide Content:{Colors.ENDC}")
                        for slide_data in slide_update_msg.payload.slides:
                            print(self.format_slide_details(slide_data))
                else:
                    print(format_agent_message(format_strawman_summary(strawman)))
                    # Also show slide details for legacy protocol
                    print(f"\n{Colors.BOLD}📄 Slide Content Details:{Colors.ENDC}")
                    for slide in strawman.slides:
                        print(self.format_slide_details(slide))
                    
                add_to_history(context, "assistant", strawman)
                results["states_completed"].append("GENERATE_STRAWMAN")
                results["outputs"]["strawman"] = strawman
                
                # Validate strawman
                if not self._validate_strawman(strawman, scenario, results):
                    return results
                
                # Simulate user requesting refinement
                refinement_request = scenario["responses"]["refinement_request"]
                print(format_user_message(refinement_request))
                add_to_history(context, "user", refinement_request)
                
                # Save strawman to session data
                context.session_data['presentation_strawman'] = strawman.model_dump() if hasattr(strawman, 'model_dump') else strawman
                
                # Transition to REFINE_STRAWMAN
                context.current_state = "REFINE_STRAWMAN"
            
            # State 5: REFINE_STRAWMAN
            refined_strawman = None
            if should_skip["REFINE_STRAWMAN"] and "refined_strawman" in results["outputs"]:
                # Get refined strawman from checkpoint
                refined_strawman = results["outputs"]["refined_strawman"]
            elif not should_skip["REFINE_STRAWMAN"]:
                print(f"\n{format_state('REFINE_STRAWMAN')}")
                print("─" * 60)
                
                # For streamlined, show status update first
                if self.use_streamlined:
                    status_msg = self.streamlined_packager.create_pre_generation_status(
                        session_id=f"test_{scenario_name}",
                        state="REFINE_STRAWMAN"
                    )
                    print(format_agent_message(f"⏳ {status_msg.payload.text}"))
                
                refined_strawman = await self.director.process(context)
                
                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="REFINE_STRAWMAN",
                        agent_output=refined_strawman,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                    print(f"{Colors.CYAN}[Streamlined: {len(messages)} messages with refined JSON data]{Colors.ENDC}")
                    
                    # Show detailed slide content from the slide_update message
                    slide_update_msg = next((msg for msg in messages if msg.type == "slide_update"), None)
                    if slide_update_msg:
                        print(f"\n{Colors.BOLD}📄 Refined Slide Content:{Colors.ENDC}")
                        # Show only the affected slides
                        if slide_update_msg.payload.affected_slides:
                            print(f"{Colors.YELLOW}Affected slides: {', '.join(slide_update_msg.payload.affected_slides)}{Colors.ENDC}")
                        for slide_data in slide_update_msg.payload.slides:
                            print(self.format_slide_details(slide_data))
                else:
                    print(format_agent_message("Strawman refined based on your feedback."))
                    # Also show refined slide details for legacy protocol
                    print(f"\n{Colors.BOLD}📄 Refined Slide Content:{Colors.ENDC}")
                    for slide in refined_strawman.slides:
                        print(self.format_slide_details(slide))
                
                # Validate refinement
                if 'strawman' in results["outputs"] and hasattr(refined_strawman, 'slides'):
                    original_strawman = results["outputs"]["strawman"]
                    if hasattr(original_strawman, 'slides'):
                        original_count = len(original_strawman.slides)
                        refined_count = len(refined_strawman.slides)
                        if refined_count != original_count:
                            print(format_error(f"Refinement changed slide count: {original_count} → {refined_count}"))
                            results["errors"].append(f"Refinement changed slide count from {original_count} to {refined_count}")
                        else:
                            print(format_success(f"Refinement preserved slide count: {refined_count} slides"))
                            
                add_to_history(context, "assistant", refined_strawman)
                results["states_completed"].append("REFINE_STRAWMAN")
                results["outputs"]["refined_strawman"] = refined_strawman
            
            # Content Generation Phase
            if not should_skip["CONTENT_GENERATION"]:
                # Simulate user accepting the strawman
                print(format_user_message("Looks good! Let's see the detailed content for each slide."))
                add_to_history(context, "user", "Looks good! Let's see the detailed content for each slide.")
                
                # Save refined strawman to session data (if not already there from checkpoint)
                if 'presentation_strawman' not in context.session_data and refined_strawman is not None:
                    context.session_data['presentation_strawman'] = refined_strawman.model_dump() if hasattr(refined_strawman, 'model_dump') else refined_strawman
                    
                    # Store strawman metadata for content generation (if not already there)
                    if hasattr(refined_strawman, 'main_title'):
                        context.session_data['strawman_metadata'] = {
                            'main_title': refined_strawman.main_title,
                            'overall_theme': getattr(refined_strawman, 'overall_theme', 'Professional'),
                            'target_audience': refined_strawman.target_audience,
                            'design_suggestions': getattr(refined_strawman, 'design_suggestions', 'Modern and professional')
                        }
                    elif isinstance(refined_strawman, dict):
                        context.session_data['strawman_metadata'] = {
                            'main_title': refined_strawman.get('main_title', 'Presentation'),
                            'overall_theme': refined_strawman.get('overall_theme', 'Professional'),
                            'target_audience': refined_strawman.get('target_audience', 'General audience'),
                            'design_suggestions': refined_strawman.get('design_suggestions', 'Modern and professional')
                        }
                
                # Transition to CONTENT_GENERATION (ContentOrchestrator handles theme generation internally)
                context.current_state = "CONTENT_GENERATION"
            
            # State 6 & 7: CONTENT_GENERATION (includes theme generation)
            if not should_skip["CONTENT_GENERATION"]:
                print(f"\n{format_state('CONTENT_GENERATION')}")
                print("─" * 60)
                print(f"{Colors.CYAN}Using ContentOrchestrator for complete content pipeline...{Colors.ENDC}")
                print(f"  🎨 Theme Generation")
                print(f"  📝 Content Creation") 
                if self.generate_images:
                    print(f"  🖼️  Image Generation")
                else:
                    print(f"  🖼️  Image Generation: {Colors.YELLOW}SKIPPED (--no-images flag){Colors.ENDC}")
            
            # Process CONTENT_GENERATION if not skipped
            if not should_skip["CONTENT_GENERATION"]:
                # Get strawman from session data or from previous stage
                strawman_data = context.session_data.get('presentation_strawman')
                if not strawman_data:
                    # If we don't have strawman data, we can't proceed
                    print(format_error("No strawman data available for content generation"))
                    results["errors"].append("No strawman data available")
                    return results
                    
                # Convert strawman data to object if needed
                from src.models.agents import PresentationStrawman
                if isinstance(strawman_data, dict):
                    refined_strawman = PresentationStrawman(**strawman_data)
                else:
                    refined_strawman = strawman_data
                
                # Extract director metadata
                director_metadata = {
                    "formality_level": "medium",  # Default
                    "complexity_allowance": "detailed"  # Default
                }
                
                # Determine formality from audience
                if any(word in refined_strawman.target_audience.lower() for word in ["executive", "board", "investor"]):
                    director_metadata["formality_level"] = "high"
                elif any(word in refined_strawman.target_audience.lower() for word in ["student", "general", "public"]):
                    director_metadata["formality_level"] = "casual"
                
                # Apply slide filter if specified
                if self.slides_filter:
                    original_slide_count = len(refined_strawman.slides)
                    refined_strawman.slides = self.filter_slides(refined_strawman.slides)
                    print(f"{Colors.CYAN}Processing {len(refined_strawman.slides)} of {original_slide_count} slides{Colors.ENDC}")
                
                # Initialize ContentOrchestrator
                content_orchestrator = ContentOrchestrator(
                    theme_model="gemini-2.5-flash",
                    content_model="gemini-2.5-pro",
                    use_tool_free_theme=True  # Use simpler theme agent
                )
                
                try:
                            if self.use_streaming:
                                # Streaming mode
                                print(f"\n{Colors.CYAN}Using STREAMING mode for real-time updates...{Colors.ENDC}")
                                
                                orchestration_result = {
                                    'theme': None,
                                    'content': [],
                                    'metadata': {}
                                }
                                
                                async for update in content_orchestrator.generate_content_streaming(
                                    strawman=refined_strawman,
                                    session_id=f"test_{scenario_name}",
                                    director_metadata=director_metadata,
                                    generate_images=self.generate_images
                                ):
                                    if update['type'] == 'theme_ready':
                                        print(f"\n{Colors.GREEN}✅ Theme generated successfully!{Colors.ENDC}")
                                        orchestration_result['theme'] = update['theme']
                                        # Display theme inline
                                        print(self.format_theme_details(update['theme']))
                                        
                                    elif update['type'] == 'content_ready':
                                        slide_index = update['slide_index']
                                        # Display the content immediately
                                        print(self.display_slide_content_realtime(
                                            slide_index + 1,
                                            update['slide_id'],
                                            update['content_manifest']
                                        ))
                                        
                                        # Add to results
                                        orchestration_result['content'].append({
                                            'slide_id': update['slide_id'],
                                            'content_manifest': update['content_manifest'].dict(),
                                            'generated_images': {}
                                        })
                                        
                                    elif update['type'] == 'image_ready':
                                        print(f"{Colors.MAGENTA}🖼️  Image generated for {update['slide_id']}{Colors.ENDC}")
                                        # Update the content item with image
                                        for item in orchestration_result['content']:
                                            if item['slide_id'] == update['slide_id']:
                                                item['generated_images']['primary'] = update.get('image_url', 'generated')
                                                break
                                                
                                    elif update['type'] == 'image_error':
                                        print(f"{Colors.YELLOW}⚠️  Image generation failed for {update['slide_id']}: {update['error']}{Colors.ENDC}")
                                        
                                    elif update['type'] == 'complete':
                                        orchestration_result['metadata'] = {
                                            'total_slides': update['total_slides'],
                                            'timestamp': update['timestamp']
                                        }
                                        print(f"\n{Colors.GREEN}✨ Content pipeline complete!{Colors.ENDC}")
                                        
                                    elif update['type'] == 'error':
                                        print(f"{Colors.RED}❌ Error: {update['error']}{Colors.ENDC}")
                                        results["errors"].append(f"Streaming error: {update['error']}")
                                        
                            else:
                                # Regular mode
                                print(f"\n{Colors.CYAN}Running complete content generation pipeline...{Colors.ENDC}")
                                
                                # Define callback for real-time display
                                async def progress_callback(update):
                                    if update['type'] == 'slide_content_ready':
                                        slide_num = update['slide_index'] + 1
                                        print(self.display_slide_content_realtime(
                                            slide_num,
                                            update['slide_id'],
                                            update['content_manifest']
                                        ))
                                
                                orchestration_result = await content_orchestrator.generate_content(
                                    strawman=refined_strawman,
                                    session_id=f"test_{scenario_name}",
                                    director_metadata=director_metadata,
                                    generate_images=self.generate_images,
                                    progress_callback=progress_callback
                                )
                            
                            # Display complete results
                            print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
                            print(f"{Colors.BOLD}COMPLETE CONTENT GENERATION RESULTS{Colors.ENDC}")
                            print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
                            
                            # Use the new format method to display everything
                            print(self.format_content_orchestrator_result(orchestration_result))
                            
                            # Store results
                            results["states_completed"].append("THEME_GENERATION")
                            results["states_completed"].append("CONTENT_GENERATION")
                            results["outputs"]["orchestration_result"] = orchestration_result
                            
                            # Extract theme and content manifests for validation
                            theme = None
                            content_manifests = []
                            
                            if 'theme' in orchestration_result:
                                theme_data = orchestration_result['theme']
                                if isinstance(theme_data, dict):
                                    theme = ThemeDefinition(**theme_data)
                                else:
                                    theme = theme_data
                                results["outputs"]["theme"] = theme
                            
                            if 'content' in orchestration_result:
                                for content_item in orchestration_result['content']:
                                    manifest_data = content_item['content_manifest']
                                    # Create a simple object that has the required attributes
                                    manifest = type('ContentManifest', (), manifest_data)()
                                    content_manifests.append(manifest)
                                results["outputs"]["content_manifests"] = content_manifests
                            
                            # Validate theme
                            if theme and not self._validate_simplified_theme(theme, results):
                                print(format_error("Theme validation failed"))
                            else:
                                print(format_success("Theme validation passed"))
                            
                            # Validate content
                            if content_manifests and not self._validate_content_manifests(content_manifests, refined_strawman, results):
                                print(format_error("Content validation failed"))
                            else:
                                print(format_success("Content validation passed"))
                            
                            # Summary statistics
                            print(f"\n{Colors.BOLD}📊 Generation Summary:{Colors.ENDC}")
                            print(f"  Total slides processed: {len(content_manifests)}")
                            
                            # Count visuals and images
                            visual_counts = {'chart': 0, 'image': 0, 'diagram': 0, 'text_only': 0}
                            image_count = 0
                            
                            for i, content_item in enumerate(orchestration_result.get('content', [])):
                                manifest_data = content_item['content_manifest']
                                if 'primary_visual' in manifest_data and manifest_data['primary_visual']:
                                    visual_type = manifest_data['primary_visual'].get('visual_type', 'unknown')
                                    visual_counts[visual_type] = visual_counts.get(visual_type, 0) + 1
                                else:
                                    visual_counts['text_only'] += 1
                                
                                if content_item.get('generated_images'):
                                    image_count += len(content_item['generated_images'])
                            
                            print(f"\n  Content Types:")
                            print(f"    📊 Charts: {visual_counts.get('chart', 0)}")
                            print(f"    🎨 Images: {visual_counts.get('image', 0)}")
                            print(f"    🔗 Diagrams: {visual_counts.get('diagram', 0)}")
                            print(f"    📝 Text-only: {visual_counts.get('text_only', 0)}")
                            print(f"\n  🖼️  Images Generated: {image_count}")
                                
                except Exception as e:
                    print(format_error(f"Content orchestration failed: {str(e)}"))
                    results["errors"].append(f"Content orchestration error: {str(e)}")
                    results["passed"] = False
                    if debug_mode:
                        import traceback
                        print(f"{Colors.YELLOW}[DEBUG] Traceback:{Colors.ENDC}")
                        print(traceback.format_exc())
            
            
            
            # Save conversation for analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"test_results_{scenario_name}_{timestamp}.json"
            save_conversation(context, save_path)
            results["conversation_saved"] = save_path
            
        except Exception as e:
            results["passed"] = False
            results["errors"].append(f"Exception: {str(e)}")
            print(format_error(f"Test failed with exception: {str(e)}"))
            if debug_mode:
                import traceback
                print(f"{Colors.YELLOW}[DEBUG] Traceback:{Colors.ENDC}")
                print(traceback.format_exc())
        
        return results
    
    def _validate_questions(self, questions, results: Dict) -> bool:
        """Validate clarifying questions output."""
        try:
            if len(questions.questions) < self.validation_rules["min_questions"]:
                results["passed"] = False
                results["errors"].append(f"Too few questions: {len(questions.questions)}")
                return False
            
            if len(questions.questions) > self.validation_rules["max_questions"]:
                results["passed"] = False
                results["errors"].append(f"Too many questions: {len(questions.questions)}")
                return False
            
            print(format_success(f"Questions validation passed ({len(questions.questions)} questions)"))
            return True
            
        except Exception as e:
            results["passed"] = False
            results["errors"].append(f"Questions validation error: {str(e)}")
            return False
    
    def _validate_plan(self, plan, scenario: Dict, results: Dict) -> bool:
        """Validate confirmation plan output."""
        try:
            if plan.proposed_slide_count < self.validation_rules["min_slides"]:
                results["passed"] = False
                results["errors"].append(f"Too few slides: {plan.proposed_slide_count}")
                return False
            
            if plan.proposed_slide_count > self.validation_rules["max_slides"]:
                results["passed"] = False
                results["errors"].append(f"Too many slides: {plan.proposed_slide_count}")
                return False
            
            # Check if slide count is reasonable for scenario
            expected_slides = scenario.get("expected_slides", 0)
            if expected_slides > 0:
                diff = abs(plan.proposed_slide_count - expected_slides)
                if diff > 2:  # Allow some variance
                    print(f"{Colors.YELLOW}Warning: Slide count {plan.proposed_slide_count} differs from expected {expected_slides}{Colors.ENDC}")
            
            print(format_success(f"Plan validation passed ({plan.proposed_slide_count} slides)"))
            return True
            
        except Exception as e:
            results["passed"] = False
            results["errors"].append(f"Plan validation error: {str(e)}")
            return False
    
    def _validate_theme(self, theme: ThemeDefinition, results: Dict) -> bool:
        """Validate theme definition has all required components."""
        try:
            all_valid = True
            
            # Check mood keywords
            if not theme.mood_keywords or len(theme.mood_keywords) < 3:
                results["errors"].append("Theme missing adequate mood keywords")
                all_valid = False
            
            # Check design tokens
            if not hasattr(theme, 'design_tokens'):
                results["errors"].append("Theme missing design tokens")
                all_valid = False
            else:
                # Check colors
                if not hasattr(theme.design_tokens, 'colors') or len(theme.design_tokens.colors) < 4:
                    results["errors"].append("Theme missing adequate color palette")
                    all_valid = False
                
                # Check typography
                if not hasattr(theme.design_tokens, 'typography') or len(theme.design_tokens.typography) < 2:
                    results["errors"].append("Theme missing typography definitions")
                    all_valid = False
            
            # Check visual guidelines
            if not theme.visual_guidelines:
                results["errors"].append("Theme missing visual guidelines")
                all_valid = False
            
            # Check layout templates
            if not theme.layout_templates or len(theme.layout_templates) < 3:
                results["errors"].append("Theme missing adequate layout templates")
                all_valid = False
            
            return all_valid
            
        except Exception as e:
            results["errors"].append(f"Theme validation error: {str(e)}")
            results["passed"] = False
            return False
    
    def _validate_simplified_theme(self, theme: ThemeDefinition, results: Dict) -> bool:
        """Validate simplified theme definition (colors and fonts only)."""
        try:
            all_valid = True
            
            # Debug: Show what we're validating
            print(f"\n{Colors.CYAN}🔍 Validating Theme Structure:{Colors.ENDC}")
            print(f"  Theme type: {type(theme)}")
            print(f"  Has design_tokens: {hasattr(theme, 'design_tokens')}")
            
            # Check design tokens
            if not hasattr(theme, 'design_tokens'):
                results["errors"].append("Theme missing design tokens")
                all_valid = False
            else:
                dt = theme.design_tokens
                print(f"  Design tokens type: {type(dt)}")
                print(f"  Has colors: {hasattr(dt, 'colors')}")
                print(f"  Has typography: {hasattr(dt, 'typography')}")
                
                # Check colors (at least primary, secondary, accent, background, text)
                if hasattr(dt, 'colors'):
                    color_count = len(dt.colors) if dt.colors else 0
                    print(f"  Color count: {color_count}")
                    if dt.colors:
                        print(f"  Color names: {list(dt.colors.keys())}")
                    if color_count < 5:
                        results["errors"].append(f"Theme has only {color_count} colors, need at least 5 (primary, secondary, accent, background, text)")
                        all_valid = False
                else:
                    results["errors"].append("Theme design_tokens missing colors attribute")
                    all_valid = False
                
                # Check typography (at least heading and body)
                if hasattr(dt, 'typography'):
                    typo_count = len(dt.typography) if dt.typography else 0
                    print(f"  Typography count: {typo_count}")
                    if dt.typography:
                        print(f"  Typography roles: {list(dt.typography.keys())}")
                    if typo_count < 2:
                        results["errors"].append(f"Theme has only {typo_count} typography entries, need at least 2 (heading, body)")
                        all_valid = False
                else:
                    results["errors"].append("Theme design_tokens missing typography attribute")
                    all_valid = False
            
            # Check formality and complexity from director
            print(f"  Has formality_level: {hasattr(theme, 'formality_level')}")
            print(f"  Formality value: {theme.formality_level if hasattr(theme, 'formality_level') else 'N/A'}")
            if not hasattr(theme, 'formality_level') or not theme.formality_level:
                results["errors"].append("Theme missing formality level from director")
                all_valid = False
            
            print(f"  Has complexity_allowance: {hasattr(theme, 'complexity_allowance')}")
            print(f"  Complexity value: {theme.complexity_allowance if hasattr(theme, 'complexity_allowance') else 'N/A'}")
            if not hasattr(theme, 'complexity_allowance') or not theme.complexity_allowance:
                results["errors"].append("Theme missing complexity allowance from director")
                all_valid = False
            
            # Check metadata for generation tracking
            if hasattr(theme, 'metadata') and theme.metadata:
                if 'generation_method' not in theme.metadata:
                    print(f"{Colors.YELLOW}Warning: Theme missing generation_method in metadata{Colors.ENDC}")
            
            print(f"\n  Validation result: {'PASS' if all_valid else 'FAIL'}")
            
            return all_valid
            
        except Exception as e:
            results["errors"].append(f"Simplified theme validation error: {str(e)}")
            results["passed"] = False
            print(f"{Colors.RED}Validation exception: {str(e)}{Colors.ENDC}")
            return False
    
    def _validate_content_manifests(self, manifests: List[ContentManifest], strawman, results: Dict) -> bool:
        """Validate content manifests."""
        try:
            if not manifests:
                results["errors"].append("No content manifests generated")
                results["passed"] = False
                return False
            
            if len(manifests) != len(strawman.slides):
                results["errors"].append(f"Manifest count mismatch: {len(manifests)} manifests for {len(strawman.slides)} slides")
                results["passed"] = False
                return False
            
            # Validate each manifest
            all_valid = True
            theme_integration_count = 0
            
            for i, manifest in enumerate(manifests):
                # Check word count compliance if limit exists
                if hasattr(manifest, 'word_count_limit') and hasattr(manifest, 'total_word_count'):
                    if manifest.total_word_count > manifest.word_count_limit:
                        print(f"  ⚠️ Slide {i+1} exceeds word limit: {manifest.total_word_count}/{manifest.word_count_limit}")
                        all_valid = False
                
                # Check theme integration (V1 style)
                if hasattr(manifest, 'theme_elements_applied') and manifest.theme_elements_applied:
                    theme_integration_count += 1
                
                # Check if visual specs are complete when needed
                slide = strawman.slides[i]
                
                # Handle both object and dict access for primary_visual
                primary_visual = None
                if hasattr(manifest, 'primary_visual'):
                    primary_visual = manifest.primary_visual
                elif isinstance(manifest, dict) and 'primary_visual' in manifest:
                    primary_visual = manifest['primary_visual']
                
                if primary_visual and (slide.analytics_needed or slide.slide_type == "data_driven"):
                    visual_type = getattr(primary_visual, 'visual_type', None) or (primary_visual.get('visual_type') if isinstance(primary_visual, dict) else None)
                    
                    if visual_type == "chart":
                        has_data = False
                        has_axes = False
                        
                        if hasattr(primary_visual, 'data_points'):
                            has_data = bool(primary_visual.data_points)
                        elif isinstance(primary_visual, dict):
                            has_data = bool(primary_visual.get('data_points'))
                            
                        if hasattr(primary_visual, 'axes'):
                            has_axes = bool(primary_visual.axes)
                        elif isinstance(primary_visual, dict):
                            has_axes = bool(primary_visual.get('axes'))
                            
                        if not has_data or not has_axes:
                            print(f"  ❌ Slide {i+1} chart missing data or axes")
                            all_valid = False
                
                if primary_visual and (slide.diagrams_needed or slide.slide_type == "diagram_focused"):
                    visual_type = getattr(primary_visual, 'visual_type', None) or (primary_visual.get('visual_type') if isinstance(primary_visual, dict) else None)
                    
                    if visual_type == "diagram":
                        has_nodes = False
                        has_connections = False
                        
                        if hasattr(primary_visual, 'nodes'):
                            has_nodes = bool(primary_visual.nodes)
                        elif isinstance(primary_visual, dict):
                            has_nodes = bool(primary_visual.get('nodes'))
                            
                        if hasattr(primary_visual, 'connections'):
                            has_connections = bool(primary_visual.connections)
                        elif isinstance(primary_visual, dict):
                            has_connections = bool(primary_visual.get('connections'))
                            
                        if not has_nodes or not has_connections:
                            print(f"  ❌ Slide {i+1} diagram missing nodes or connections")
                            all_valid = False
            
            # Report theme integration
            if theme_integration_count > 0:
                print(f"  ✅ Theme integrated in {theme_integration_count}/{len(manifests)} slides")
            
            return all_valid
            
        except Exception as e:
            results["errors"].append(f"Content validation error: {str(e)}")
            results["passed"] = False
            return False
    
    def _validate_strawman(self, strawman, scenario: Dict, results: Dict) -> bool:
        """Validate strawman output with detailed field checking."""
        try:
            # Check slide count
            if len(strawman.slides) < self.validation_rules["min_slides"]:
                results["passed"] = False
                results["errors"].append(f"Too few slides in strawman: {len(strawman.slides)}")
                return False
            
            print(f"\n{Colors.BOLD}🔍 Validating Strawman Structure:{Colors.ENDC}")
            all_valid = True
            
            # Validate each slide
            for i, slide in enumerate(strawman.slides):
                slide_valid = True
                
                # Print validation results for this slide
                print(format_validation_results(slide, self.validation_rules))
                
                # Check required fields
                for field in self.validation_rules["required_slide_fields"]:
                    if not hasattr(slide, field) or getattr(slide, field) is None:
                        results["passed"] = False
                        results["errors"].append(f"Slide {slide.slide_id} missing required field: {field}")
                        slide_valid = False
                        all_valid = False
                
                # Check important optional fields
                missing_important = []
                for field in self.validation_rules.get("important_slide_fields", []):
                    if not hasattr(slide, field) or getattr(slide, field) is None:
                        missing_important.append(field)
                
                if missing_important:
                    print(f"  ⚠️  Note: Missing optional fields: {', '.join(missing_important)}")
                
                if slide_valid:
                    print(f"  {Colors.GREEN}✓ Slide {i+1} validation passed{Colors.ENDC}")
                else:
                    print(f"  {Colors.RED}✗ Slide {i+1} validation failed{Colors.ENDC}")
            
            # Check slide types match expected structure if provided
            if "expected_structure" in scenario:
                slide_types = [slide.slide_type for slide in strawman.slides]
                if slide_types != scenario["expected_structure"]:
                    print(f"\n{Colors.YELLOW}⚠️  Warning: Slide structure differs from expected{Colors.ENDC}")
                    print(f"  Expected: {scenario['expected_structure']}")
                    print(f"  Actual:   {slide_types}")
            
            if all_valid:
                print(f"\n{format_success(f'Strawman validation passed ({len(strawman.slides)} slides)')}")
            else:
                print(f"\n{format_error(f'Strawman validation failed')}")
            
            return all_valid
            
        except Exception as e:
            results["passed"] = False
            results["errors"].append(f"Strawman validation error: {str(e)}")
            return False
    
    
    
    async def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """Run all available test scenarios."""
        results = []
        
        for scenario_name in self.scenarios.keys():
            print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
            result = await self.run_scenario(scenario_name)
            results.append(result)
            
            if result["passed"]:
                print(f"\n{format_success(f'Scenario {scenario_name} PASSED')}")
            else:
                print(f"\n{format_error(f'Scenario {scenario_name} FAILED')}")
                for error in result["errors"]:
                    print(f"  • {error}")
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        """Print test summary with enhanced formatting."""
        print(f"\n{Colors.BOLD}{'═'*60}{Colors.ENDC}")
        protocol_info = f"{'Streamlined' if self.use_streamlined else 'Legacy'} Protocol"
        print(f"{Colors.BOLD}📊 TEST SUMMARY ({protocol_info}){Colors.ENDC}")
        print(f"{Colors.BOLD}{'═'*60}{Colors.ENDC}\n")
        
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        
        print(f"🎯 Total Scenarios: {total}")
        print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.ENDC}")
        print(f"{Colors.RED}❌ Failed: {failed}{Colors.ENDC}")
        
        if failed > 0:
            print(f"\n{Colors.BOLD}📝 Failed Scenarios:{Colors.ENDC}")
            for result in results:
                if not result["passed"]:
                    print(f"\n❌ {result['name']} ({result['scenario']})")
                    for error in result["errors"]:
                        print(f"  • {error}")
        
        print(f"\n{Colors.BOLD}📊 States Coverage:{Colors.ENDC}")
        all_states = ["PROVIDE_GREETING", "ASK_CLARIFYING_QUESTIONS", 
                      "CREATE_CONFIRMATION_PLAN", "GENERATE_STRAWMAN", "REFINE_STRAWMAN",
                      "THEME_GENERATION", "CONTENT_GENERATION"]
        
        state_icons = {
            "PROVIDE_GREETING": "👋",
            "ASK_CLARIFYING_QUESTIONS": "❓",
            "CREATE_CONFIRMATION_PLAN": "📋",
            "GENERATE_STRAWMAN": "📊",
            "REFINE_STRAWMAN": "🔧",
            "THEME_GENERATION": "🎨",
            "CONTENT_GENERATION": "📝"
        }
        
        for state in all_states:
            completed = sum(1 for r in results if state in r["states_completed"])
            icon = state_icons.get(state, "📍")
            status = "✅" if completed == total else "🔄" if completed > 0 else "❌"
            print(f"{icon} {state}: {completed}/{total} {status}")
        
        # Show protocol benefits if using streamlined
        if self.use_streamlined:
            print(f"\n{Colors.BOLD}✨ Streamlined Protocol Benefits:{Colors.ENDC}")
            print("  • Multiple focused messages per state")
            print("  • Complete slide data with all planning fields")
            print("  • Real-time status updates")
            print("  • Clean separation of data and presentation")


async def main():
    """Main function to run the E2E tests."""
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('GOOGLE_API_KEY'):
        print(format_error("No AI API key found!"))
        print("Please ensure your .env file contains one of:")
        print("- GOOGLE_API_KEY=...")
        print("- OPENAI_API_KEY=sk-...")
        print("- ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="End-to-end testing for Director agent",
        epilog="Example: python test_director_e2e.py --scenario technical"
    )
    parser.add_argument(
        "--scenario", 
        type=str, 
        choices=["default", "executive", "technical", "educational", "sales"],
        help="Run specific scenario (default, executive, technical, educational, sales)"
    )
    parser.add_argument("--list", action="store_true", help="List available scenarios")
    parser.add_argument(
        "--streaming", 
        action="store_true", 
        help="Use streaming mode for real-time content generation updates"
    )
    parser.add_argument(
        "--slides",
        type=str,
        help="Limit slides to process (e.g., '1-2' for first 2 slides, '1,3,5' for specific slides)"
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image generation (useful for faster testing)"
    )
    parser.add_argument(
        "--save-checkpoints",
        action="store_true",
        help="Save checkpoints at each stage for later use"
    )
    parser.add_argument(
        "--start-stage",
        type=str,
        choices=["ASK_CLARIFYING_QUESTIONS", "CREATE_CONFIRMATION_PLAN", 
                 "GENERATE_STRAWMAN", "REFINE_STRAWMAN", "CONTENT_GENERATION"],
        help="Start testing from a specific stage using checkpoint data"
    )
    parser.add_argument(
        "--checkpoint-file",
        type=str,
        help="Load from a specific checkpoint file"
    )
    parser.add_argument(
        "--list-checkpoints",
        action="store_true",
        help="List available checkpoints and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize tester with all settings
    tester = DirectorE2ETester(
        use_streaming=args.streaming, 
        slides_filter=args.slides,
        generate_images=not args.no_images,
        save_checkpoints=args.save_checkpoints,
        start_stage=args.start_stage,
        checkpoint_file=args.checkpoint_file
    )
    
    # Handle list checkpoints command
    if args.list_checkpoints:
        print(f"\n{Colors.BOLD}📋 Available Checkpoints:{Colors.ENDC}")
        checkpoints = tester.checkpoint_manager.list_checkpoints()
        if checkpoints:
            for cp in checkpoints:
                print(f"  • {cp['scenario']}/{cp['stage']}: {cp['file']}")
        else:
            print("  No checkpoints found.")
        return
    
    if args.list:
        tester.show_scenarios_menu()
        return
    
    if args.scenario:
        # Run specific scenario from command line
        print(f"\n{Colors.BOLD}🎯 Running scenario: {args.scenario}{Colors.ENDC}")
        if args.streaming:
            print(f"{Colors.GREEN}Using streaming mode for real-time updates{Colors.ENDC}")
        if args.no_images:
            print(f"{Colors.YELLOW}Image generation disabled (--no-images flag){Colors.ENDC}")
        result = await tester.run_scenario(args.scenario)
        tester.print_summary([result])
    else:
        # Show interactive menu
        scenario_choice = tester.show_interactive_menu()
        if scenario_choice:
            result = await tester.run_scenario(scenario_choice)
            tester.print_summary([result])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(format_error(f"Fatal error: {str(e)}"))
