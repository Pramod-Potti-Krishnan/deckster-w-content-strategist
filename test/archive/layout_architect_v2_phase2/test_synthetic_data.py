"""
Synthetic data generators for testing the three-agent Layout Architect system.

Provides realistic test data that mimics outputs from each stage of the pipeline.
"""

import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.models.agents import Slide, PresentationStrawman
from src.agents.layout_architect import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken,
    DimensionToken, GridZone, LayoutTemplate,
    SemanticContainer, ContainerManifest, ContainerRole,
    ContentImportance, ContentFlow, ContainerRelationship,
    RelationshipType
)
from src.agents.layout_architect.model_types.design_tokens import TokenValue, TokenType


class SyntheticDataGenerator:
    """Generate synthetic data for testing Layout Architect agents."""
    
    # Industry templates
    INDUSTRIES = {
        "healthcare": {
            "colors": ["#0066CC", "#4A90E2", "#E8F0FE"],
            "tone": "professional",
            "fonts": ["Arial", "Helvetica"],
            "keywords": ["patient", "care", "treatment", "diagnosis", "health"]
        },
        "finance": {
            "colors": ["#003366", "#2E7D32", "#F5F5F5"],
            "tone": "formal",
            "fonts": ["Georgia", "Times New Roman"],
            "keywords": ["revenue", "growth", "ROI", "investment", "portfolio"]
        },
        "education": {
            "colors": ["#1976D2", "#FFC107", "#FFFFFF"],
            "tone": "friendly",
            "fonts": ["Open Sans", "Roboto"],
            "keywords": ["learning", "students", "curriculum", "achievement", "knowledge"]
        },
        "technology": {
            "colors": ["#212121", "#00ACC1", "#F5F5F5"],
            "tone": "modern",
            "fonts": ["SF Pro", "Inter"],
            "keywords": ["innovation", "AI", "platform", "solution", "digital"]
        }
    }
    
    # Slide type templates
    SLIDE_TEMPLATES = {
        "title_slide": {
            "key_points_range": (1, 2),
            "container_roles": [ContainerRole.HEADLINE, ContainerRole.KEY_TAKEAWAY],
            "complexity": 0.2
        },
        "content_heavy": {
            "key_points_range": (3, 5),
            "container_roles": [ContainerRole.HEADLINE, ContainerRole.MAIN_POINT, 
                              ContainerRole.SUPPORTING_EVIDENCE_TEXT],
            "complexity": 0.6
        },
        "visual_heavy": {
            "key_points_range": (2, 4),
            "container_roles": [ContainerRole.HEADLINE, ContainerRole.IMAGE_CONCEPTUAL,
                              ContainerRole.KEY_TAKEAWAY],
            "complexity": 0.5
        },
        "data_driven": {
            "key_points_range": (3, 6),
            "container_roles": [ContainerRole.HEADLINE, ContainerRole.KPI_METRIC,
                              ContainerRole.SUPPORTING_EVIDENCE_CHART, ContainerRole.DATA_POINT],
            "complexity": 0.8
        }
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
    
    def generate_slide(
        self,
        slide_id: str,
        slide_number: int,
        slide_type: str = "content_heavy",
        industry: str = "technology"
    ) -> Slide:
        """Generate a synthetic slide with realistic content."""
        template = self.SLIDE_TEMPLATES.get(slide_type, self.SLIDE_TEMPLATES["content_heavy"])
        industry_data = self.INDUSTRIES.get(industry, self.INDUSTRIES["technology"])
        
        # Generate title
        title_templates = [
            f"{random.choice(industry_data['keywords']).capitalize()} Strategy Overview",
            f"Transforming {random.choice(industry_data['keywords']).capitalize()}",
            f"The Future of {random.choice(industry_data['keywords']).capitalize()}",
            f"{random.choice(industry_data['keywords']).capitalize()} Excellence"
        ]
        title = random.choice(title_templates)
        
        # Generate key points
        num_points = random.randint(*template["key_points_range"])
        key_points = []
        
        point_templates = [
            f"Achieve {random.randint(20, 50)}% improvement in {random.choice(industry_data['keywords'])}",
            f"Industry-leading {random.choice(industry_data['keywords'])} solutions",
            f"Transform your {random.choice(industry_data['keywords'])} with AI",
            f"Reduce costs by ${random.randint(1, 10)}M annually",
            f"Increase {random.choice(industry_data['keywords'])} efficiency by {random.randint(30, 70)}%",
            f"Best-in-class {random.choice(industry_data['keywords'])} platform"
        ]
        
        for _ in range(num_points):
            key_points.append(random.choice(point_templates))
        
        # Generate narrative
        narrative = f"This slide demonstrates our approach to {random.choice(industry_data['keywords'])}"
        
        # Add visual/analytics needs for appropriate types
        visuals_needed = None
        analytics_needed = None
        
        if slide_type == "visual_heavy":
            visuals_needed = f"Infographic showing {random.choice(industry_data['keywords'])} process"
        elif slide_type == "data_driven":
            analytics_needed = f"Chart comparing {random.choice(industry_data['keywords'])} metrics over time"
        
        return Slide(
            slide_id=slide_id,
            slide_number=slide_number,
            title=title,
            slide_type=slide_type,
            narrative=narrative,
            key_points=key_points,
            visuals_needed=visuals_needed,
            analytics_needed=analytics_needed,
            structure_preference=random.choice(["hierarchical", "visual_left", "centered", "dashboard"])
        )
    
    def generate_strawman(
        self,
        num_slides: int = 5,
        industry: str = "technology",
        presentation_title: Optional[str] = None
    ) -> PresentationStrawman:
        """Generate a complete presentation strawman."""
        if presentation_title is None:
            industry_data = self.INDUSTRIES.get(industry, self.INDUSTRIES["technology"])
            presentation_title = f"{random.choice(industry_data['keywords']).capitalize()} Transformation Journey"
        
        # Generate slides with varied types
        slide_types = ["title_slide"] + random.choices(
            ["content_heavy", "visual_heavy", "data_driven"],
            weights=[0.5, 0.3, 0.2],
            k=num_slides - 1
        )
        
        slides = []
        for i, slide_type in enumerate(slide_types):
            slide = self.generate_slide(
                slide_id=f"slide_{i+1:03d}",
                slide_number=i + 1,
                slide_type=slide_type,
                industry=industry
            )
            slides.append(slide)
        
        return PresentationStrawman(
            main_title=presentation_title,
            overall_theme=f"{industry.capitalize()} {self.INDUSTRIES[industry]['tone']}",
            slides=slides,
            design_suggestions=f"Modern {industry} style with {self.INDUSTRIES[industry]['colors'][0]} accent",
            target_audience=f"{industry.capitalize()} professionals and decision makers",
            presentation_duration=len(slides) * 3  # 3 minutes per slide average
        )
    
    def generate_theme(self, industry: str = "technology") -> ThemeDefinition:
        """Generate a synthetic theme definition."""
        industry_data = self.INDUSTRIES.get(industry, self.INDUSTRIES["technology"])
        
        # Create design tokens
        tokens = DesignTokens(
            name=f"{industry}_theme",
            colors={
                "primary": ColorToken(
                    value=industry_data["colors"][0],
                    type=TokenType.COLOR,
                    description="Primary brand color"
                ),
                "secondary": ColorToken(
                    value=industry_data["colors"][1],
                    type=TokenType.COLOR,
                    description="Secondary accent color"
                ),
                "background": ColorToken(
                    value=industry_data["colors"][2],
                    type=TokenType.COLOR,
                    description="Background color"
                ),
                "text": ColorToken(
                    value="#212121",
                    type=TokenType.COLOR,
                    description="Primary text color"
                )
            },
            typography={
                "heading": TypographyToken(
                    fontFamily=TokenValue(value=industry_data["fonts"][0], type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=40, type=TokenType.FONT_SIZE),
                    fontWeight=TokenValue(value=700, type=TokenType.FONT_WEIGHT),
                    lineHeight=TokenValue(value=1.2, type=TokenType.LINE_HEIGHT)
                ),
                "body": TypographyToken(
                    fontFamily=TokenValue(value=industry_data["fonts"][-1], type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=18, type=TokenType.FONT_SIZE),
                    fontWeight=TokenValue(value=400, type=TokenType.FONT_WEIGHT),
                    lineHeight=TokenValue(value=1.6, type=TokenType.LINE_HEIGHT)
                )
            },
            spacing={
                "small": DimensionToken(value=8, type=TokenType.DIMENSION),
                "medium": DimensionToken(value=16, type=TokenType.DIMENSION),
                "large": DimensionToken(value=24, type=TokenType.DIMENSION)
            },
            sizing={
                "container-max": DimensionToken(value=144, type=TokenType.DIMENSION),
                "container-min": DimensionToken(value=40, type=TokenType.DIMENSION)
            }
        )
        
        # Create layout templates
        templates = {
            "standard": LayoutTemplate(
                name="standard",
                description="Standard layout for content",
                zones={
                    "header": GridZone(
                        name="header",
                        leftInset=8,
                        topInset=8,
                        width=144,
                        height=20
                    ),
                    "content": GridZone(
                        name="content",
                        leftInset=8,
                        topInset=32,
                        width=144,
                        height=50
                    )
                }
            )
        }
        
        return ThemeDefinition(
            name=f"{industry}_{industry_data['tone']}",
            design_tokens=tokens,
            layout_templates=templates,
            metadata={
                "industry": industry,
                "formality": industry_data["tone"],
                "primary_color": industry_data["colors"][0]
            }
        )
    
    def generate_semantic_container(
        self,
        container_id: str,
        role: ContainerRole,
        slide: Slide,
        hierarchy_level: int = 2
    ) -> SemanticContainer:
        """Generate a semantic container based on slide content."""
        # Extract content based on role
        if role == ContainerRole.HEADLINE:
            content = slide.title
            importance = ContentImportance.HIGH
            visual_weight = 0.8
        elif role == ContainerRole.KEY_TAKEAWAY and slide.key_points:
            content = slide.key_points[0]
            importance = ContentImportance.HIGH
            visual_weight = 0.7
        elif role == ContainerRole.MAIN_POINT and slide.key_points:
            content = random.choice(slide.key_points)
            importance = ContentImportance.MEDIUM
            visual_weight = 0.5
        elif role == ContainerRole.SUPPORTING_EVIDENCE_TEXT:
            content = f"Evidence: {slide.narrative}"
            importance = ContentImportance.MEDIUM
            visual_weight = 0.4
        elif role == ContainerRole.IMAGE_CONCEPTUAL:
            content = slide.visuals_needed or "Visual placeholder"
            importance = ContentImportance.HIGH
            visual_weight = 0.6
        elif role == ContainerRole.KPI_METRIC:
            content = f"KPI: {random.randint(20, 80)}% improvement"
            importance = ContentImportance.HIGH
            visual_weight = 0.6
        else:
            content = "Content placeholder"
            importance = ContentImportance.MEDIUM
            visual_weight = 0.5
        
        return SemanticContainer(
            id=container_id,
            role=role,
            content=content,
            hierarchy_level=hierarchy_level,
            importance=importance,
            visual_weight=visual_weight,
            requires_visual=role in [ContainerRole.IMAGE_CONCEPTUAL, ContainerRole.SUPPORTING_EVIDENCE_CHART],
            tags=[slide.slide_type, role.value]
        )
    
    def generate_manifest(
        self,
        slide: Slide,
        theme: Optional[ThemeDefinition] = None
    ) -> ContainerManifest:
        """Generate a container manifest for a slide."""
        template = self.SLIDE_TEMPLATES.get(slide.slide_type, self.SLIDE_TEMPLATES["content_heavy"])
        
        # Generate containers based on slide type
        containers = []
        for i, role in enumerate(template["container_roles"]):
            container = self.generate_semantic_container(
                container_id=f"{slide.slide_id}_container_{i+1}",
                role=role,
                slide=slide,
                hierarchy_level=min(i + 1, 5)
            )
            containers.append(container)
        
        # Generate relationships
        relationships = []
        if len(containers) > 1:
            # Headline supports everything
            for i in range(1, len(containers)):
                relationships.append(ContainerRelationship(
                    from_container=containers[0].id,
                    to_container=containers[i].id,
                    relationship_type=RelationshipType.SUPPORTS,
                    strength=0.8
                ))
        
        # Determine content flow
        if slide.slide_type == "data_driven":
            content_flow = ContentFlow.DASHBOARD
        elif slide.slide_type == "visual_heavy":
            content_flow = ContentFlow.RADIAL
        else:
            content_flow = ContentFlow.LINEAR
        
        return ContainerManifest(
            slide_id=slide.slide_id,
            slide_type=slide.slide_type,
            containers=containers,
            relationships=relationships,
            primary_message=slide.title,
            content_flow=content_flow,
            visual_hierarchy=[c.id for c in containers],
            groupings=[],
            content_density=template["complexity"],
            complexity_score=template["complexity"]
        )
    
    def generate_test_scenario(
        self,
        scenario_name: str = "default",
        industry: str = "technology"
    ) -> Dict[str, Any]:
        """Generate a complete test scenario with all components."""
        # Generate strawman
        strawman = self.generate_strawman(
            num_slides=4,
            industry=industry
        )
        
        # Generate theme
        theme = self.generate_theme(industry=industry)
        
        # Generate manifests for each slide
        manifests = []
        for slide in strawman.slides:
            manifest = self.generate_manifest(slide, theme)
            manifests.append(manifest)
        
        return {
            "scenario_name": scenario_name,
            "industry": industry,
            "strawman": strawman,
            "theme": theme,
            "manifests": manifests,
            "timestamp": datetime.now().isoformat()
        }


# Utility functions for quick test data generation
def get_test_slide(slide_type: str = "content_heavy", industry: str = "technology") -> Slide:
    """Get a single test slide."""
    generator = SyntheticDataGenerator()
    return generator.generate_slide("test_001", 1, slide_type, industry)


def get_test_strawman(num_slides: int = 5, industry: str = "technology") -> PresentationStrawman:
    """Get a test strawman presentation."""
    generator = SyntheticDataGenerator()
    return generator.generate_strawman(num_slides, industry)


def get_test_theme(industry: str = "technology") -> ThemeDefinition:
    """Get a test theme."""
    generator = SyntheticDataGenerator()
    return generator.generate_theme(industry)


def get_test_manifest(slide: Optional[Slide] = None) -> ContainerManifest:
    """Get a test container manifest."""
    generator = SyntheticDataGenerator()
    if slide is None:
        slide = get_test_slide()
    return generator.generate_manifest(slide)


def get_complete_test_scenario(scenario_name: str = "default") -> Dict[str, Any]:
    """Get a complete test scenario."""
    generator = SyntheticDataGenerator()
    return generator.generate_test_scenario(scenario_name)


if __name__ == "__main__":
    # Example usage
    print("Generating synthetic test data...")
    
    # Generate a complete scenario
    scenario = get_complete_test_scenario("healthcare_demo")
    
    print(f"\nGenerated scenario: {scenario['scenario_name']}")
    print(f"Industry: {scenario['industry']}")
    print(f"Slides: {len(scenario['strawman'].slides)}")
    print(f"Theme: {scenario['theme'].name}")
    
    # Show first slide details
    first_slide = scenario['strawman'].slides[0]
    print(f"\nFirst slide:")
    print(f"  Title: {first_slide.title}")
    print(f"  Type: {first_slide.slide_type}")
    print(f"  Key points: {len(first_slide.key_points)}")
    
    # Show first manifest
    first_manifest = scenario['manifests'][0]
    print(f"\nFirst manifest:")
    print(f"  Containers: {len(first_manifest.containers)}")
    print(f"  Content flow: {first_manifest.content_flow.value}")
    print(f"  Complexity: {first_manifest.complexity_score:.2f}")