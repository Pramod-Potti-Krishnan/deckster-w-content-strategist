"""
Structure Layout Agent - Combined content analysis and layout generation.

This agent merges the functionality of Structure Agent and Layout Engine
to eliminate the Chinese whisper effect and ensure direct preservation 
of strawman metadata and structure preferences.
"""

from .agent import StructureLayoutAgent

__all__ = ["StructureLayoutAgent"]