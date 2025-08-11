"""
Tools for Structure Analyzer Agent - Content analysis and relationship detection.

These tools help analyze content structure, identify relationships,
and determine content hierarchy.
"""

from typing import List, Dict, Tuple, Optional, Set, Any
from pydantic import BaseModel, Field
from pydantic_ai import Tool
import re
from collections import defaultdict

from ...model_types.semantic_containers import (
    ContainerRole, RelationshipType, ContentImportance,
    SemanticContainer, ContainerRelationship
)


class ContentParserInput(BaseModel):
    """Input for content parsing"""
    slide_content: Dict[str, Any] = Field(description="Raw slide content to parse")
    slide_type: str = Field(description="Type of slide for context")
    audience_level: str = Field(default="general", description="Audience knowledge level")


class ContentParserOutput(BaseModel):
    """Output from content parsing"""
    containers: List[Dict[str, Any]] = Field(
        description="Parsed semantic containers"
    )
    content_stats: Dict[str, int] = Field(
        description="Statistics about the content"
    )
    detected_patterns: List[str] = Field(
        description="Patterns detected in the content"
    )


class ContentParser:
    """Parse and analyze slide content to identify semantic containers"""
    
    # Pattern definitions for content detection
    PATTERNS = {
        "metric": re.compile(r'\b\d+(?:\.\d+)?%?\s*(?:increase|decrease|growth|reduction|YoY|QoQ|vs)', re.I),
        "comparison": re.compile(r'\b(?:versus|vs|compared to|against|better than|worse than)\b', re.I),
        "list": re.compile(r'^(?:\d+\.|[-•*])\s+', re.M),
        "question": re.compile(r'\?$', re.M),
        "action": re.compile(r'\b(?:click|download|sign up|register|contact|call|visit)\b', re.I),
        "definition": re.compile(r'\b(?:is defined as|means|refers to|:)\s+', re.I),
        "example": re.compile(r'\b(?:for example|e\.g\.|such as|including|like)\b', re.I),
        "key_phrase": re.compile(r'\b(?:key|important|critical|essential|must|vital)\b', re.I)
    }
    
    def parse_content(self, input_data: ContentParserInput) -> ContentParserOutput:
        """Parse slide content into semantic containers"""
        slide_content = input_data.slide_content
        containers = []
        content_stats = defaultdict(int)
        detected_patterns = []
        
        # Parse title
        if slide_content.get('title'):
            title_container = self._parse_title(slide_content['title'], slide_content.get('slide_id', 'unknown'))
            containers.append(title_container)
            content_stats['titles'] = 1
        
        # Parse key points
        if slide_content.get('key_points'):
            point_containers = self._parse_key_points(
                slide_content['key_points'],
                slide_content.get('slide_id', 'unknown')
            )
            containers.extend(point_containers)
            content_stats['key_points'] = len(point_containers)
        
        # Parse narrative/body text
        if slide_content.get('narrative'):
            narrative_containers = self._parse_narrative(
                slide_content['narrative'],
                slide_content.get('slide_id', 'unknown')
            )
            containers.extend(narrative_containers)
            content_stats['narrative_elements'] = len(narrative_containers)
        
        # Parse visual/diagram needs
        if slide_content.get('visuals_needed') or slide_content.get('diagrams_needed'):
            visual_containers = self._parse_visual_needs(
                slide_content.get('visuals_needed'),
                slide_content.get('diagrams_needed'),
                slide_content.get('slide_id', 'unknown')
            )
            containers.extend(visual_containers)
            content_stats['visuals'] = len(visual_containers)
        
        # Parse analytics/data needs
        if slide_content.get('analytics_needed'):
            data_containers = self._parse_analytics_needs(
                slide_content['analytics_needed'],
                slide_content.get('slide_id', 'unknown')
            )
            containers.extend(data_containers)
            content_stats['data_elements'] = len(data_containers)
        
        # Detect patterns
        all_text = ' '.join([
            str(slide_content.get('title', '')),
            ' '.join(slide_content.get('key_points', [])),
            str(slide_content.get('narrative', ''))
        ])
        
        for pattern_name, pattern_re in self.PATTERNS.items():
            if pattern_re.search(all_text):
                detected_patterns.append(pattern_name)
        
        # Convert containers to dict format
        container_dicts = [self._container_to_dict(c) for c in containers]
        
        return ContentParserOutput(
            containers=container_dicts,
            content_stats=dict(content_stats),
            detected_patterns=detected_patterns
        )
    
    def _parse_title(self, title: str, slide_id: str) -> SemanticContainer:
        """Parse title into semantic container"""
        # Determine if it's a headline or section header
        role = ContainerRole.HEADLINE
        if any(word in title.lower() for word in ['chapter', 'section', 'part']):
            role = ContainerRole.SECTION_HEADER
        
        return SemanticContainer(
            id=f"{slide_id}_title",
            role=role,
            content=title,
            hierarchy_level=1,
            importance=ContentImportance.HIGH,
            visual_weight=0.8,
            preferred_position="top"
        )
    
    def _parse_key_points(self, key_points: List[str], slide_id: str) -> List[SemanticContainer]:
        """Parse key points into semantic containers"""
        containers = []
        
        for i, point in enumerate(key_points):
            # Analyze point content
            role = self._determine_point_role(point)
            importance = self._determine_importance(point)
            
            container = SemanticContainer(
                id=f"{slide_id}_point_{i+1}",
                role=role,
                content=point,
                hierarchy_level=2,
                importance=importance,
                visual_weight=0.6 if importance == ContentImportance.HIGH else 0.4,
                tags=self._extract_tags(point)
            )
            containers.append(container)
        
        return containers
    
    def _parse_narrative(self, narrative: str, slide_id: str) -> List[SemanticContainer]:
        """Parse narrative text into semantic containers"""
        containers = []
        
        # Split narrative into logical chunks
        sentences = re.split(r'[.!?]+', narrative)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            # Determine role based on content
            if self.PATTERNS['definition'].search(sentence):
                role = ContainerRole.DEFINITION
            elif self.PATTERNS['example'].search(sentence):
                role = ContainerRole.EXAMPLE
            elif self.PATTERNS['question'].search(sentence):
                role = ContainerRole.QUESTION
            else:
                role = ContainerRole.SUPPORTING_EVIDENCE_TEXT
            
            container = SemanticContainer(
                id=f"{slide_id}_narrative_{i+1}",
                role=role,
                content=sentence.strip(),
                hierarchy_level=3,
                importance=ContentImportance.MEDIUM,
                visual_weight=0.3
            )
            containers.append(container)
        
        return containers
    
    def _parse_visual_needs(self, visuals: Optional[str], diagrams: Optional[str], slide_id: str) -> List[SemanticContainer]:
        """Parse visual requirements into containers"""
        containers = []
        
        if visuals:
            container = SemanticContainer(
                id=f"{slide_id}_visual",
                role=ContainerRole.IMAGE_CONCEPTUAL,
                content=visuals,
                hierarchy_level=2,
                importance=ContentImportance.HIGH,
                visual_weight=0.7,
                requires_visual=True
            )
            containers.append(container)
        
        if diagrams:
            container = SemanticContainer(
                id=f"{slide_id}_diagram",
                role=ContainerRole.DIAGRAM,
                content=diagrams,
                hierarchy_level=2,
                importance=ContentImportance.HIGH,
                visual_weight=0.8,
                requires_visual=True
            )
            containers.append(container)
        
        return containers
    
    def _parse_analytics_needs(self, analytics: str, slide_id: str) -> List[SemanticContainer]:
        """Parse analytics requirements into containers"""
        containers = []
        
        # Look for specific data types
        if 'chart' in analytics.lower() or 'graph' in analytics.lower():
            container = SemanticContainer(
                id=f"{slide_id}_chart",
                role=ContainerRole.SUPPORTING_EVIDENCE_CHART,
                content=analytics,
                hierarchy_level=2,
                importance=ContentImportance.HIGH,
                visual_weight=0.8,
                requires_visual=True
            )
            containers.append(container)
        
        # Look for KPIs or metrics
        if self.PATTERNS['metric'].search(analytics):
            metrics = self.PATTERNS['metric'].findall(analytics)
            for i, metric in enumerate(metrics):
                container = SemanticContainer(
                    id=f"{slide_id}_kpi_{i+1}",
                    role=ContainerRole.KPI_METRIC,
                    content=metric,
                    hierarchy_level=2,
                    importance=ContentImportance.HIGH,
                    visual_weight=0.5
                )
                containers.append(container)
        
        return containers
    
    def _determine_point_role(self, point: str) -> ContainerRole:
        """Determine the semantic role of a key point"""
        point_lower = point.lower()
        
        if self.PATTERNS['metric'].search(point):
            return ContainerRole.DATA_POINT
        elif self.PATTERNS['action'].search(point):
            return ContainerRole.CALL_TO_ACTION
        elif self.PATTERNS['question'].search(point):
            return ContainerRole.QUESTION
        elif any(word in point_lower for word in ['benefit', 'advantage', 'value']):
            return ContainerRole.KEY_TAKEAWAY
        else:
            return ContainerRole.MAIN_POINT
    
    def _determine_importance(self, text: str) -> ContentImportance:
        """Determine content importance"""
        if self.PATTERNS['key_phrase'].search(text):
            return ContentImportance.HIGH
        elif len(text) < 20:
            return ContentImportance.LOW
        else:
            return ContentImportance.MEDIUM
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from content"""
        tags = []
        
        # Industry keywords
        tech_words = ['AI', 'ML', 'cloud', 'digital', 'software', 'platform']
        for word in tech_words:
            if word in text:
                tags.append(word.lower())
        
        # Content type tags
        if self.PATTERNS['metric'].search(text):
            tags.append('data')
        if self.PATTERNS['action'].search(text):
            tags.append('cta')
        
        return tags
    
    def _container_to_dict(self, container: SemanticContainer) -> Dict[str, Any]:
        """Convert container to dictionary format"""
        return {
            "id": container.id,
            "role": container.role.value,
            "content": container.content,
            "hierarchy_level": container.hierarchy_level,
            "importance": container.importance.value,
            "visual_weight": container.visual_weight,
            "preferred_position": container.preferred_position,
            "requires_visual": container.requires_visual,
            "tags": container.tags
        }


class RelationshipAnalyzerInput(BaseModel):
    """Input for relationship analysis"""
    containers: List[Dict[str, Any]] = Field(description="Semantic containers to analyze")
    slide_context: Dict[str, Any] = Field(description="Additional slide context")


class RelationshipAnalyzerOutput(BaseModel):
    """Output from relationship analysis"""
    relationships: List[Dict[str, Any]] = Field(
        description="Detected relationships between containers"
    )
    relationship_graph: Dict[str, List[str]] = Field(
        description="Graph representation of relationships"
    )
    clusters: List[List[str]] = Field(
        description="Clusters of related containers"
    )


class RelationshipAnalyzer:
    """Analyze relationships between semantic containers"""
    
    def analyze_relationships(self, input_data: RelationshipAnalyzerInput) -> RelationshipAnalyzerOutput:
        """Analyze relationships between containers"""
        containers = input_data.containers
        relationships = []
        graph = defaultdict(list)
        
        # Build container lookup
        container_map = {c['id']: c for c in containers}
        
        # Analyze pairwise relationships
        for i, container1 in enumerate(containers):
            for container2 in containers[i+1:]:
                rel = self._analyze_pair(container1, container2)
                if rel:
                    relationships.append(self._relationship_to_dict(rel))
                    graph[container1['id']].append(container2['id'])
                    if rel.bidirectional:
                        graph[container2['id']].append(container1['id'])
        
        # Find clusters
        clusters = self._find_clusters(graph, list(container_map.keys()))
        
        return RelationshipAnalyzerOutput(
            relationships=relationships,
            relationship_graph=dict(graph),
            clusters=clusters
        )
    
    def _analyze_pair(self, c1: Dict[str, Any], c2: Dict[str, Any]) -> Optional[ContainerRelationship]:
        """Analyze relationship between two containers"""
        # Check hierarchy relationship
        if c1['hierarchy_level'] < c2['hierarchy_level']:
            # C1 is higher in hierarchy, C2 might elaborate
            if self._content_relates(c1['content'], c2['content']):
                return ContainerRelationship(
                    from_container=c2['id'],
                    to_container=c1['id'],
                    relationship_type=RelationshipType.ELABORATES,
                    strength=0.7
                )
        
        # Check supporting evidence
        if c2['role'] in ['supporting_evidence_text', 'supporting_evidence_chart']:
            if c1['role'] in ['main_point', 'key_takeaway']:
                return ContainerRelationship(
                    from_container=c2['id'],
                    to_container=c1['id'],
                    relationship_type=RelationshipType.SUPPORTS,
                    strength=0.8
                )
        
        # Check visual relationships
        if c2['role'] in ['diagram', 'image_conceptual'] and c1['role'] == 'data_point':
            return ContainerRelationship(
                from_container=c2['id'],
                to_container=c1['id'],
                relationship_type=RelationshipType.VISUALIZES,
                strength=0.9
            )
        
        # Check sequential relationships
        if c1['role'] == 'list_item' and c2['role'] == 'list_item':
            id1_num = int(re.search(r'_(\d+)$', c1['id']).group(1)) if re.search(r'_(\d+)$', c1['id']) else 0
            id2_num = int(re.search(r'_(\d+)$', c2['id']).group(1)) if re.search(r'_(\d+)$', c2['id']) else 0
            if id2_num == id1_num + 1:
                return ContainerRelationship(
                    from_container=c1['id'],
                    to_container=c2['id'],
                    relationship_type=RelationshipType.FOLLOWS,
                    strength=1.0
                )
        
        # Check grouping
        if c1['role'] == c2['role'] and c1['hierarchy_level'] == c2['hierarchy_level']:
            return ContainerRelationship(
                from_container=c1['id'],
                to_container=c2['id'],
                relationship_type=RelationshipType.GROUPS_WITH,
                strength=0.6,
                bidirectional=True
            )
        
        return None
    
    def _content_relates(self, content1: str, content2: str) -> bool:
        """Check if two pieces of content are related"""
        # Simple keyword overlap check
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words1 -= stop_words
        words2 -= stop_words
        
        # Check overlap
        overlap = words1 & words2
        return len(overlap) >= 2 or len(overlap) / min(len(words1), len(words2)) > 0.3
    
    def _find_clusters(self, graph: Dict[str, List[str]], all_nodes: List[str]) -> List[List[str]]:
        """Find clusters of related containers"""
        visited = set()
        clusters = []
        
        for node in all_nodes:
            if node not in visited:
                cluster = []
                self._dfs(node, graph, visited, cluster)
                if len(cluster) > 1:
                    clusters.append(cluster)
        
        return clusters
    
    def _dfs(self, node: str, graph: Dict[str, List[str]], visited: Set[str], cluster: List[str]):
        """Depth-first search for cluster finding"""
        visited.add(node)
        cluster.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                self._dfs(neighbor, graph, visited, cluster)
    
    def _relationship_to_dict(self, rel: ContainerRelationship) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        return {
            "from_container": rel.from_container,
            "to_container": rel.to_container,
            "relationship_type": rel.relationship_type.value,
            "strength": rel.strength,
            "bidirectional": rel.bidirectional
        }


class HierarchyDetectorInput(BaseModel):
    """Input for hierarchy detection"""
    containers: List[Dict[str, Any]] = Field(description="Containers to analyze")
    relationships: List[Dict[str, Any]] = Field(description="Container relationships")


class HierarchyDetectorOutput(BaseModel):
    """Output from hierarchy detection"""
    hierarchy_tree: Dict[int, List[str]] = Field(
        description="Containers organized by hierarchy level"
    )
    visual_priority: List[str] = Field(
        description="Container IDs in order of visual priority"
    )
    groupings: List[List[str]] = Field(
        description="Containers that should be grouped"
    )
    balance_score: float = Field(
        description="Visual balance score (0-1)"
    )


class HierarchyDetector:
    """Detect and optimize content hierarchy"""
    
    def detect_hierarchy(self, input_data: HierarchyDetectorInput) -> HierarchyDetectorOutput:
        """Detect hierarchy and visual organization"""
        containers = input_data.containers
        relationships = input_data.relationships
        
        # Build hierarchy tree
        hierarchy_tree = defaultdict(list)
        for container in containers:
            level = container.get('hierarchy_level', 3)
            hierarchy_tree[level].append(container['id'])
        
        # Determine visual priority
        visual_priority = self._calculate_visual_priority(containers, relationships)
        
        # Find groupings
        groupings = self._find_groupings(containers, relationships)
        
        # Calculate balance score
        balance_score = self._calculate_balance(containers)
        
        return HierarchyDetectorOutput(
            hierarchy_tree=dict(hierarchy_tree),
            visual_priority=visual_priority,
            groupings=groupings,
            balance_score=balance_score
        )
    
    def _calculate_visual_priority(self, containers: List[Dict], relationships: List[Dict]) -> List[str]:
        """Calculate visual priority order"""
        # Score each container
        scores = {}
        
        for container in containers:
            score = 0
            
            # Base score from importance
            importance_scores = {
                'critical': 100,
                'high': 75,
                'medium': 50,
                'low': 25,
                'optional': 10
            }
            score += importance_scores.get(container.get('importance', 'medium'), 50)
            
            # Hierarchy bonus
            hierarchy_level = container.get('hierarchy_level', 3)
            score += (5 - hierarchy_level) * 20
            
            # Visual weight bonus
            score += container.get('visual_weight', 0.5) * 50
            
            # Relationship bonus
            rel_count = sum(1 for r in relationships 
                          if r['to_container'] == container['id'])
            score += rel_count * 10
            
            scores[container['id']] = score
        
        # Sort by score
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    def _find_groupings(self, containers: List[Dict], relationships: List[Dict]) -> List[List[str]]:
        """Find containers that should be grouped"""
        groupings = []
        processed = set()
        
        # Find explicit groups
        for rel in relationships:
            if rel['relationship_type'] == 'groups_with' and rel['from_container'] not in processed:
                group = [rel['from_container'], rel['to_container']]
                
                # Expand group
                for other_rel in relationships:
                    if other_rel['relationship_type'] == 'groups_with':
                        if other_rel['from_container'] in group and other_rel['to_container'] not in group:
                            group.append(other_rel['to_container'])
                        elif other_rel['to_container'] in group and other_rel['from_container'] not in group:
                            group.append(other_rel['from_container'])
                
                groupings.append(group)
                processed.update(group)
        
        # Find implicit groups (same role, same level)
        role_groups = defaultdict(list)
        for container in containers:
            if container['id'] not in processed:
                key = (container['role'], container['hierarchy_level'])
                role_groups[key].append(container['id'])
        
        for group in role_groups.values():
            if len(group) > 1:
                groupings.append(group)
        
        return groupings
    
    def _calculate_balance(self, containers: List[Dict]) -> float:
        """Calculate visual balance score"""
        if not containers:
            return 1.0
        
        # Calculate weight distribution
        total_weight = sum(c.get('visual_weight', 0.5) for c in containers)
        if total_weight == 0:
            return 1.0
        
        # Calculate variance
        avg_weight = total_weight / len(containers)
        variance = sum((c.get('visual_weight', 0.5) - avg_weight) ** 2 for c in containers)
        
        # Normalize
        max_variance = len(containers) * (1.0 ** 2)
        balance = 1.0 - (variance / max_variance) if max_variance > 0 else 1.0
        
        return min(1.0, max(0.0, balance))


# Create PydanticAI tools
content_parser_tool = Tool(
    function=ContentParser().parse_content,
    name="parse_content",
    description="Parse slide content into semantic containers"
)

relationship_analyzer_tool = Tool(
    function=RelationshipAnalyzer().analyze_relationships,
    name="analyze_relationships",
    description="Analyze relationships between semantic containers"
)

hierarchy_detector_tool = Tool(
    function=HierarchyDetector().detect_hierarchy,
    name="detect_hierarchy",
    description="Detect content hierarchy and visual organization"
)