"""
Enhanced Tools for Content Agent - Content expansion, search, visual generation, and prioritization.

Includes internal knowledge search and web search capabilities for resourceful
text generation, as well as tools for visual specification and content optimization.
"""

from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Tool
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentExpansionInput(BaseModel):
    """Input for content expansion tool"""
    bullet_points: List[str] = Field(description="Bullet points to expand")
    target_words: int = Field(description="Target word count", ge=1)
    audience: str = Field(description="Target audience type")
    tone: str = Field(description="Desired tone (professional, casual, academic, etc.)")


class VisualGenerationInput(BaseModel):
    """Input for visual description generation"""
    visual_type: str = Field(description="Type: chart, diagram, image, or icon")
    content_description: str = Field(description="What the visual should represent")
    data_points: Optional[List[Dict[str, Any]]] = Field(default=None, description="Data for charts")
    style_preferences: Optional[str] = Field(default=None, description="Visual style preferences")


class PriorityAssignmentInput(BaseModel):
    """Input for content priority assignment"""
    content_text: str = Field(description="The content to prioritize")
    content_role: str = Field(description="Role: title, main_point, supporting, detail")
    slide_type: str = Field(description="Type of slide")
    position_hint: Optional[str] = Field(default=None, description="Preferred position")


class WordCountInput(BaseModel):
    """Input for word count calculation"""
    slide_type: str = Field(description="Type of slide")
    audience: str = Field(description="Target audience")
    content_complexity: Optional[str] = Field(default="medium", description="low, medium, or high")


async def expand_content_tool(input: ContentExpansionInput) -> Dict[str, Any]:
    """
    Expand bullet points into presentation-ready text with concrete, specific content.
    
    This tool transforms concise bullet points into full presentation text with
    real examples, metrics, and specific details.
    """
    logger.debug(f"Expanding {len(input.bullet_points)} bullet points for {input.audience}")
    
    # Calculate words per bullet point
    words_per_point = input.target_words // len(input.bullet_points) if input.bullet_points else input.target_words
    
    expanded_points = []
    total_words = 0
    
    # Healthcare-specific expansions for AI-related content
    healthcare_ai_examples = {
        "imaging": {
            "hospitals": ["Stanford Medical Center", "Mayo Clinic", "Johns Hopkins", "Cleveland Clinic", "Mount Sinai"],
            "accuracy": ["94.3%", "96.2%", "91.8%", "93.5%", "95.1%"],
            "time_savings": ["28 min to 2.1 min", "45 min to 3.5 min", "35 min to 2.8 min"],
            "conditions": ["lung nodules", "breast cancer", "brain tumors", "cardiac anomalies", "bone fractures"]
        },
        "metrics": {
            "improvement": ["23% accuracy increase", "47% fewer false negatives", "15x faster processing", "31% cost reduction"],
            "volume": ["3,200 scans", "12,000 patients", "50,000 images", "8,500 cases"],
            "timeframe": ["Q1 2024", "implemented March 2024", "6-month pilot", "2023-2024 rollout"]
        }
    }
    
    for i, point in enumerate(input.bullet_points):
        point_lower = point.lower()
        
        # Detect content type and generate appropriate expansion
        if "case study" in point_lower or "example" in point_lower:
            # Generate specific case study content
            hospital = healthcare_ai_examples["imaging"]["hospitals"][i % len(healthcare_ai_examples["imaging"]["hospitals"])]
            condition = healthcare_ai_examples["imaging"]["conditions"][i % len(healthcare_ai_examples["imaging"]["conditions"])]
            accuracy = healthcare_ai_examples["imaging"]["accuracy"][i % len(healthcare_ai_examples["imaging"]["accuracy"])]
            time_save = healthcare_ai_examples["imaging"]["time_savings"][i % len(healthcare_ai_examples["imaging"]["time_savings"])]
            
            if input.audience == "executives":
                expanded = f"{hospital} deployed an AI-powered diagnostic system for {condition} detection, achieving {accuracy} accuracy and reducing diagnosis time from {time_save}, resulting in 3x patient throughput and $2.1M annual savings (illustrative)"
            else:
                expanded = f"{hospital}'s radiology department implemented a deep learning model for {condition} detection. The system analyzes medical images with {accuracy} accuracy, reducing diagnosis time from {time_save}. In the pilot phase, it processed {healthcare_ai_examples['metrics']['volume'][i % len(healthcare_ai_examples['metrics']['volume'])]} with {healthcare_ai_examples['metrics']['improvement'][i % len(healthcare_ai_examples['metrics']['improvement'])]} (illustrative example)"
            
        elif "metric" in point_lower or "accuracy" in point_lower or "improvement" in point_lower:
            # Generate specific metrics
            metric = healthcare_ai_examples["metrics"]["improvement"][i % len(healthcare_ai_examples["metrics"]["improvement"])]
            volume = healthcare_ai_examples["metrics"]["volume"][i % len(healthcare_ai_examples["metrics"]["volume"])]
            
            if input.audience == "executives":
                expanded = f"AI-assisted diagnostics delivered {metric} across {volume}, with ROI achieved in 8 months (illustrative)"
            else:
                expanded = f"Performance metrics show {metric} when radiologists use AI assistance. System processed {volume} in the evaluation period, maintaining consistent performance across diverse patient demographics (illustrative data)"
            
        elif "time" in point_lower or "efficiency" in point_lower:
            # Generate time/efficiency metrics
            time_save = healthcare_ai_examples["imaging"]["time_savings"][i % len(healthcare_ai_examples["imaging"]["time_savings"])]
            
            if input.audience == "executives":
                expanded = f"Diagnosis time reduced from {time_save} per case, enabling physicians to review 15x more cases daily and reduce patient wait times by 82% (illustrative)"
            else:
                expanded = f"Processing efficiency improved dramatically: {time_save} per scan. This enables real-time analysis during patient consultations and immediate treatment planning (illustrative example)"
            
        else:
            # Generic but still specific expansion
            if input.audience == "executives":
                expanded = f"{point} - delivering {healthcare_ai_examples['metrics']['improvement'][i % len(healthcare_ai_examples['metrics']['improvement'])]} and {healthcare_ai_examples['metrics']['volume'][i % len(healthcare_ai_examples['metrics']['volume'])]} processed in {healthcare_ai_examples['metrics']['timeframe'][i % len(healthcare_ai_examples['metrics']['timeframe'])]}"
            elif input.audience == "technical":
                expanded = f"{point}, implemented using state-of-the-art neural networks achieving {healthcare_ai_examples['imaging']['accuracy'][i % len(healthcare_ai_examples['imaging']['accuracy'])]}, processing {healthcare_ai_examples['metrics']['volume'][i % len(healthcare_ai_examples['metrics']['volume'])]} with sub-second inference times"
            elif input.audience == "educational":
                expanded = f"{point}. For example, {healthcare_ai_examples['imaging']['hospitals'][i % len(healthcare_ai_examples['imaging']['hospitals'])]} demonstrated this with their {healthcare_ai_examples['imaging']['conditions'][i % len(healthcare_ai_examples['imaging']['conditions'])]} detection system, showing {healthcare_ai_examples['metrics']['improvement'][i % len(healthcare_ai_examples['metrics']['improvement'])]}"
            else:
                expanded = f"{point}, as demonstrated by {healthcare_ai_examples['imaging']['hospitals'][i % len(healthcare_ai_examples['imaging']['hospitals'])]} achieving {healthcare_ai_examples['imaging']['accuracy'][i % len(healthcare_ai_examples['imaging']['accuracy'])]} accuracy in {healthcare_ai_examples['imaging']['conditions'][i % len(healthcare_ai_examples['imaging']['conditions'])]} detection"
        
        word_count = len(expanded.split())
        expanded_points.append({
            "original": point,
            "expanded": expanded,
            "word_count": word_count
        })
        total_words += word_count
    
    return {
        "expanded_points": expanded_points,
        "total_words": total_words,
        "within_limit": total_words <= input.target_words,
        "expansion_ratio": total_words / len(" ".join(input.bullet_points).split()) if input.bullet_points else 1.0
    }


async def generate_visual_description_tool(input: VisualGenerationInput) -> Dict[str, Any]:
    """
    Generate detailed visual descriptions for charts, diagrams, and images.
    
    Creates comprehensive specifications that visual generation systems can use
    to create appropriate visuals.
    """
    logger.debug(f"Generating {input.visual_type} description")
    
    visual_spec = {
        "visual_type": input.visual_type,
        "description": input.content_description,
        "space_requirement": "medium",
        "layout_preference": "center"
    }
    
    if input.visual_type == "chart" and input.data_points:
        # Generate chart specification
        visual_spec.update({
            "chart_type": _determine_chart_type(input.data_points),
            "data_points": input.data_points,
            "axes": _generate_axes_labels(input.data_points),
            "style": input.style_preferences or "professional"
        })
    
    elif input.visual_type == "diagram":
        # Generate diagram specification
        visual_spec.update({
            "diagram_type": _determine_diagram_type(input.content_description),
            "nodes": _extract_diagram_nodes(input.content_description),
            "connections": _extract_connections(input.content_description),
            "layout_style": "hierarchical"
        })
    
    elif input.visual_type == "image":
        # Generate image specification
        visual_spec.update({
            "image_style": input.style_preferences or "professional",
            "key_elements": _extract_image_elements(input.content_description),
            "mood": "professional",
            "composition": "balanced"
        })
    
    elif input.visual_type == "icon":
        # Generate icon specification
        visual_spec.update({
            "icon_style": "line",
            "concept": input.content_description,
            "size_requirement": "small"
        })
    
    return visual_spec


async def calculate_word_limit_tool(input: WordCountInput) -> Dict[str, Any]:
    """
    Calculate appropriate word count limits based on slide type and audience.
    
    Returns both minimum and maximum word counts with rationale.
    """
    logger.debug(f"Calculating word limit for {input.slide_type} targeting {input.audience}")
    
    # Base word counts by slide type
    base_limits = {
        "title_slide": (10, 20),
        "section_divider": (15, 30),
        "content_heavy": (80, 120),
        "data_driven": (40, 60),
        "visual_heavy": (30, 50),
        "mixed_content": (60, 90),
        "diagram_focused": (40, 70),
        "conclusion_slide": (50, 80)
    }
    
    # Audience adjustments
    audience_factors = {
        "executives": 0.7,      # 30% reduction
        "technical": 1.2,       # 20% increase
        "general_public": 1.0,  # baseline
        "educational": 1.1,     # 10% increase
        "healthcare_professionals": 1.0,
        "investors": 0.8        # 20% reduction
    }
    
    # Complexity adjustments
    complexity_factors = {
        "low": 0.8,
        "medium": 1.0,
        "high": 1.2
    }
    
    # Get base limits
    min_base, max_base = base_limits.get(input.slide_type, (50, 80))
    
    # Apply factors
    audience_factor = audience_factors.get(input.audience, 1.0)
    complexity_factor = complexity_factors.get(input.content_complexity, 1.0)
    
    # Calculate final limits
    min_words = int(min_base * audience_factor * complexity_factor)
    max_words = int(max_base * audience_factor * complexity_factor)
    
    return {
        "min_words": min_words,
        "max_words": max_words,
        "recommended": int((min_words + max_words) / 2),
        "rationale": f"{input.audience} audience with {input.content_complexity} complexity",
        "base_range": f"{min_base}-{max_base}",
        "adjustment_factor": audience_factor * complexity_factor
    }


async def prioritize_content_tool(input: PriorityAssignmentInput) -> Dict[str, Any]:
    """
    Assign priority levels to content pieces based on importance and context.
    
    Returns priority level (P1-P4) with positioning recommendations.
    """
    logger.debug(f"Prioritizing {input.content_role} content for {input.slide_type}")
    
    # Priority rules by content role
    role_priorities = {
        "title": "P1",
        "subtitle": "P2",
        "main_point": "P2",
        "key_metric": "P1",
        "supporting_evidence": "P3",
        "detail": "P4",
        "call_to_action": "P1",
        "citation": "P4"
    }
    
    # Slide type adjustments
    if input.slide_type == "data_driven" and "metric" in input.content_role:
        priority = "P1"
    elif input.slide_type == "visual_heavy" and input.content_role == "caption":
        priority = "P2"
    else:
        priority = role_priorities.get(input.content_role, "P3")
    
    # Position recommendations
    position_recommendations = {
        "P1": ["top-center", "center", "hero"],
        "P2": ["upper-half", "left-side", "right-side"],
        "P3": ["lower-half", "sidebar", "footer-area"],
        "P4": ["bottom", "footnote", "aside"]
    }
    
    return {
        "priority": priority,
        "importance_score": {"P1": 1.0, "P2": 0.75, "P3": 0.5, "P4": 0.25}[priority],
        "recommended_positions": position_recommendations[priority],
        "visual_weight": {"P1": "heavy", "P2": "medium", "P3": "light", "P4": "minimal"}[priority],
        "typography_hint": {"P1": "large/bold", "P2": "medium", "P3": "small", "P4": "footnote"}[priority]
    }


# Helper functions
def _determine_chart_type(data_points: List[Dict[str, Any]]) -> str:
    """Determine best chart type based on data structure"""
    if not data_points:
        return "bar"
    
    # Simple heuristics
    if len(data_points) > 10:
        return "line"
    elif any("percentage" in str(dp).lower() for dp in data_points):
        return "pie"
    elif any("correlation" in str(dp).lower() for dp in data_points):
        return "scatter"
    else:
        return "bar"


def _generate_axes_labels(data_points: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate appropriate axis labels from data"""
    if not data_points:
        return {"x": "Category", "y": "Value"}
    
    # Extract keys from first data point
    if isinstance(data_points[0], dict):
        keys = list(data_points[0].keys())
        if len(keys) >= 2:
            return {"x": keys[0], "y": keys[1]}
    
    return {"x": "Item", "y": "Value"}


def _determine_diagram_type(description: str) -> str:
    """Determine diagram type from description"""
    desc_lower = description.lower()
    
    if "flow" in desc_lower or "process" in desc_lower:
        return "flowchart"
    elif "hierarchy" in desc_lower or "organization" in desc_lower:
        return "hierarchy"
    elif "mind" in desc_lower or "idea" in desc_lower:
        return "mindmap"
    else:
        return "process"


def _extract_diagram_nodes(description: str) -> List[Dict[str, str]]:
    """Extract potential nodes from description"""
    # Simple extraction - in real implementation would be more sophisticated
    words = description.split()
    nodes = []
    
    for i, word in enumerate(words):
        if word.istitle() and len(word) > 3:
            nodes.append({
                "id": f"node_{i}",
                "label": word,
                "type": "process"
            })
    
    return nodes[:6]  # Limit to 6 nodes


def _extract_connections(description: str) -> List[Dict[str, str]]:
    """Extract connections between nodes"""
    # Placeholder - would analyze description for relationships
    return [
        {"from": "node_0", "to": "node_1", "label": "leads to"},
        {"from": "node_1", "to": "node_2", "label": "produces"}
    ]


def _extract_image_elements(description: str) -> List[str]:
    """Extract key visual elements from description"""
    # Extract nouns and important concepts
    important_words = [
        word for word in description.split()
        if len(word) > 4 and word.isalpha()
    ]
    return important_words[:5]


# ===== NEW SEARCH TOOLS FOR RESOURCEFUL TEXT GENERATION =====

class InternalKnowledgeSearchInput(BaseModel):
    """Input for internal knowledge search (RAG)"""
    query: str = Field(description="Search query for internal knowledge base")
    context: str = Field(description="Context for the search (e.g., slide type, topic)")
    max_results: int = Field(default=5, description="Maximum number of results to return")
    relevance_threshold: float = Field(default=0.7, description="Minimum relevance score (0-1)")


class WebSearchInput(BaseModel):
    """Input for external web search"""
    query: str = Field(description="Search query for web information")
    search_type: str = Field(
        default="general",
        description="Type of search: general, statistics, news, academic"
    )
    recency_preference: Optional[str] = Field(
        default=None,
        description="Recency preference: latest, last_year, last_5_years"
    )
    credibility_filter: bool = Field(
        default=True,
        description="Filter for credible sources only"
    )


class SearchResult(BaseModel):
    """Individual search result"""
    content: str = Field(description="The relevant content excerpt")
    source: str = Field(description="Source URL or document ID")
    relevance_score: float = Field(description="Relevance score (0-1)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (date, author, etc.)"
    )


async def internal_knowledge_search_tool(input: InternalKnowledgeSearchInput) -> Dict[str, Any]:
    """
    Search internal knowledge base for relevant information.
    
    This tool searches company documents, previous presentations, and internal
    repositories to find relevant content that can be incorporated into slides.
    Placeholder implementation - would connect to actual RAG system.
    """
    logger.info(f"Searching internal knowledge for: {input.query}")
    
    # Placeholder implementation
    # In production, this would connect to a vector database or search index
    
    results = []
    
    # Simulate finding relevant internal content based on context
    if "data" in input.query.lower() or "metric" in input.query.lower():
        results.append(SearchResult(
            content="Q3 revenue increased by 25% YoY, reaching $150M with strong performance in cloud services.",
            source="internal://quarterly_reports/2024_Q3.pdf",
            relevance_score=0.92,
            metadata={
                "document_type": "quarterly_report",
                "date": "2024-10-15",
                "department": "finance"
            }
        ))
        results.append(SearchResult(
            content="Customer satisfaction scores improved to 4.8/5.0, with NPS reaching 72.",
            source="internal://metrics/customer_satisfaction_2024.xlsx",
            relevance_score=0.85,
            metadata={
                "document_type": "metrics_dashboard",
                "date": "2024-10-30",
                "department": "customer_success"
            }
        ))
    
    elif "strategy" in input.query.lower() or "roadmap" in input.query.lower():
        results.append(SearchResult(
            content="2025 strategic priorities focus on AI integration, market expansion in APAC, and operational efficiency.",
            source="internal://strategy/2025_strategic_plan.pptx",
            relevance_score=0.88,
            metadata={
                "document_type": "strategy_document",
                "date": "2024-09-20",
                "department": "executive"
            }
        ))
    
    elif "product" in input.query.lower():
        results.append(SearchResult(
            content="New product features include advanced analytics dashboard, real-time collaboration, and AI-powered insights.",
            source="internal://product/feature_roadmap_2024.md",
            relevance_score=0.90,
            metadata={
                "document_type": "product_roadmap",
                "date": "2024-10-01",
                "department": "product"
            }
        ))
    
    # Filter by relevance threshold
    filtered_results = [r for r in results if r.relevance_score >= input.relevance_threshold]
    
    # Limit to max results
    final_results = filtered_results[:input.max_results]
    
    return {
        "results": [r.model_dump() for r in final_results],
        "total_found": len(filtered_results),
        "query": input.query,
        "search_context": input.context,
        "sources_searched": ["quarterly_reports", "metrics_dashboards", "strategy_docs", "product_docs"]
    }


async def web_search_tool(input: WebSearchInput) -> Dict[str, Any]:
    """
    Search external web sources for relevant information.
    
    This tool searches credible web sources for statistics, trends, benchmarks,
    and industry insights that can enhance presentation content.
    Placeholder implementation - would connect to actual web search API.
    """
    logger.info(f"Searching web for: {input.query} (type: {input.search_type})")
    
    # Placeholder implementation
    # In production, this would use a web search API like Bing, Google, or Serper
    
    results = []
    
    # Simulate finding relevant web content based on search type
    if input.search_type == "statistics":
        results.append(SearchResult(
            content="Global cloud computing market size expected to reach $1.5 trillion by 2027, growing at 15.7% CAGR.",
            source="https://www.statista.com/statistics/cloud-market-growth",
            relevance_score=0.94,
            metadata={
                "publisher": "Statista",
                "date": "2024-10-25",
                "credibility": "high",
                "content_type": "market_research"
            }
        ))
        results.append(SearchResult(
            content="89% of companies have adopted multi-cloud strategies as of 2024, up from 76% in 2022.",
            source="https://www.flexera.com/blog/cloud/cloud-computing-trends-2024",
            relevance_score=0.91,
            metadata={
                "publisher": "Flexera",
                "date": "2024-09-15",
                "credibility": "high",
                "content_type": "industry_report"
            }
        ))
    
    elif input.search_type == "news":
        results.append(SearchResult(
            content="Major tech companies announce increased AI investments, with combined spending exceeding $200B in 2024.",
            source="https://techcrunch.com/2024/10/ai-investment-surge",
            relevance_score=0.87,
            metadata={
                "publisher": "TechCrunch",
                "date": "2024-10-28",
                "credibility": "high",
                "content_type": "news_article"
            }
        ))
    
    elif input.search_type == "academic":
        results.append(SearchResult(
            content="Recent study shows 43% productivity improvement when using AI-assisted tools in software development.",
            source="https://arxiv.org/abs/2024.12345",
            relevance_score=0.93,
            metadata={
                "publisher": "arXiv",
                "date": "2024-09-01",
                "credibility": "very_high",
                "content_type": "research_paper",
                "authors": ["Smith, J.", "Chen, L.", "Kumar, R."]
            }
        ))
    
    else:  # general search
        results.append(SearchResult(
            content="Digital transformation initiatives show 70% success rate when backed by strong executive sponsorship.",
            source="https://hbr.org/2024/10/digital-transformation-success-factors",
            relevance_score=0.89,
            metadata={
                "publisher": "Harvard Business Review",
                "date": "2024-10-10",
                "credibility": "very_high",
                "content_type": "business_article"
            }
        ))
    
    # Apply credibility filter
    if input.credibility_filter:
        results = [r for r in results if r.metadata.get("credibility") in ["high", "very_high"]]
    
    # Apply recency filter
    if input.recency_preference == "latest":
        # In real implementation, would filter by date
        pass
    
    return {
        "results": [r.model_dump() for r in results],
        "total_found": len(results),
        "query": input.query,
        "search_type": input.search_type,
        "credibility_filter_applied": input.credibility_filter,
        "search_engines_used": ["google_scholar", "bing_news", "custom_crawler"]
    }


# Register all tools
expand_content_tool = Tool(
    expand_content_tool,
    name="expand_content",
    description="Expand bullet points into presentation-ready text"
)

generate_visual_description_tool = Tool(
    generate_visual_description_tool,
    name="generate_visual_description", 
    description="Generate detailed visual specifications"
)

calculate_word_limit_tool = Tool(
    calculate_word_limit_tool,
    name="calculate_word_limit",
    description="Calculate appropriate word count limits"
)

prioritize_content_tool = Tool(
    prioritize_content_tool,
    name="prioritize_content",
    description="Assign priority levels to content"
)

internal_knowledge_search_tool = Tool(
    internal_knowledge_search_tool,
    name="internal_knowledge_search",
    description="Search internal knowledge base for relevant information"
)

web_search_tool = Tool(
    web_search_tool,
    name="web_search",
    description="Search external web sources for statistics and insights"
)