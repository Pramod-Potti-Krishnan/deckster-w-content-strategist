"""
Content Agent - Prepares detailed content for slides before layout generation.
"""

from .content_agent_v5 import ContentAgentV5
from .content_agent_v2 import ContentManifest, VisualSpec

__all__ = [
    # Agent and models
    'ContentAgentV5',
    'ContentManifest',
    'VisualSpec',
]