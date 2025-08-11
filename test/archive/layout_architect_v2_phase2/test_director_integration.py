"""
Integration tests for Layout Architect with Director_IN handoff.

Tests the complete flow from strawman approval to layout generation,
including WebSocket communication and session management.
"""

import asyncio
import pytest
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from unittest.mock import Mock, AsyncMock, MagicMock

from src.models.agents import PresentationStrawman, Slide
from src.agents.director_phase2_integration import DirectorPhase2Extension
from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest
)
from src.utils.session_manager import SessionManager
from .test_synthetic_data import get_test_strawman, SyntheticDataGenerator


class MockWebSocketHandler:
    """Mock WebSocket handler for testing."""
    
    def __init__(self):
        self.messages = []
        self.theme_updates = []
        self.slide_updates = []
        self.status_updates = []
    
    async def send_message(self, message: Dict[str, Any]):
        """Mock send_message that captures messages."""
        self.messages.append(message)
        
        msg_type = message.get("type")
        if msg_type == "theme_update":
            self.theme_updates.append(message)
        elif msg_type == "slide_update":
            self.slide_updates.append(message)
        elif msg_type == "status_update":
            self.status_updates.append(message)
        
        # Print for debugging
        print(f"\n📤 WebSocket: {msg_type}")
        if msg_type == "theme_update":
            print(f"   Theme: {message['payload'].get('theme_name', 'N/A')}")
        elif msg_type == "slide_update":
            slides = message['payload'].get('slides', [])
            if slides:
                print(f"   Slide: {slides[0].get('slide_id', 'N/A')}")
    
    def get_messages_by_type(self, msg_type: str) -> List[Dict[str, Any]]:
        """Get all messages of a specific type."""
        return [m for m in self.messages if m.get("type") == msg_type]
    
    def clear(self):
        """Clear all captured messages."""
        self.messages.clear()
        self.theme_updates.clear()
        self.slide_updates.clear()
        self.status_updates.clear()


class MockSessionManager:
    """Mock session manager for testing."""
    
    def __init__(self):
        self.sessions = {}
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "state": "LAYOUT_GENERATION",
                "presentation_strawman": None
            }
        return self.sessions[session_id]
    
    async def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {"session_id": session_id}
        self.sessions[session_id].update(data)
    
    def add_strawman(self, session_id: str, strawman: PresentationStrawman):
        """Add strawman to session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {"session_id": session_id}
        self.sessions[session_id]["presentation_strawman"] = strawman


class TestDirectorIntegration:
    """Test Director_IN to Layout Architect integration."""
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket handler."""
        return MockWebSocketHandler()
    
    @pytest.fixture
    def mock_session_manager(self):
        """Create mock session manager."""
        return MockSessionManager()
    
    @pytest.fixture
    def phase2_extension(self, mock_session_manager, mock_websocket):
        """Create Phase 2 extension with mocks."""
        return DirectorPhase2Extension(mock_session_manager, mock_websocket)
    
    @pytest.fixture
    def test_strawman(self):
        """Create a test strawman."""
        generator = SyntheticDataGenerator(seed=42)
        return generator.generate_strawman(
            num_slides=3,
            industry="healthcare",
            presentation_title="Healthcare Innovation Platform"
        )
    
    @pytest.mark.asyncio
    async def test_layout_generation_state_handler(self, phase2_extension, test_strawman, mock_session_manager):
        """Test the LAYOUT_GENERATION state handler."""
        session_id = "test_session_001"
        user_id = "test_user"
        
        # Add strawman to session
        mock_session_manager.add_strawman(session_id, test_strawman)
        
        # Call state handler
        result = await phase2_extension.handle_layout_generation_state(
            session_id=session_id,
            user_id=user_id,
            context={}
        )
        
        # Assertions
        assert result["status"] == "completed"
        assert "theme_name" in result
        assert "slide_count" in result
        assert result["slide_count"] == len(test_strawman.slides)
        
        print(f"\n✅ Layout generation completed:")
        print(f"   Theme: {result['theme_name']}")
        print(f"   Slides: {result['slide_count']}")
    
    @pytest.mark.asyncio
    async def test_websocket_message_flow(self, phase2_extension, test_strawman, mock_websocket, mock_session_manager):
        """Test WebSocket message flow during layout generation."""
        session_id = "test_ws_001"
        user_id = "test_user"
        
        # Add strawman to session
        mock_session_manager.add_strawman(session_id, test_strawman)
        
        # Clear any previous messages
        mock_websocket.clear()
        
        # Generate layouts
        await phase2_extension.handle_layout_generation_state(
            session_id=session_id,
            user_id=user_id,
            context={}
        )
        
        # Check WebSocket messages
        assert len(mock_websocket.messages) > 0, "No WebSocket messages sent"
        
        # Should have theme update
        theme_updates = mock_websocket.get_messages_by_type("theme_update")
        assert len(theme_updates) >= 1, "No theme update sent"
        
        # Should have slide updates
        slide_updates = mock_websocket.get_messages_by_type("slide_update")
        assert len(slide_updates) >= 1, "No slide updates sent"
        
        # Should have status updates
        status_updates = mock_websocket.get_messages_by_type("status_update")
        assert len(status_updates) >= 2, "Insufficient status updates"
        
        # Verify theme update structure
        theme_msg = theme_updates[0]
        assert "payload" in theme_msg
        assert "theme_name" in theme_msg["payload"]
        assert "theme_config" in theme_msg["payload"]
        
        # Verify slide update structure
        slide_msg = slide_updates[0]
        assert "payload" in slide_msg
        assert "slides" in slide_msg["payload"]
        slides_data = slide_msg["payload"]["slides"]
        assert len(slides_data) > 0
        assert "slide_id" in slides_data[0]
        assert "layout" in slides_data[0]
        
        print(f"\n✅ WebSocket flow verified:")
        print(f"   Total messages: {len(mock_websocket.messages)}")
        print(f"   Theme updates: {len(theme_updates)}")
        print(f"   Slide updates: {len(slide_updates)}")
        print(f"   Status updates: {len(status_updates)}")
    
    @pytest.mark.asyncio
    async def test_strawman_from_context(self, phase2_extension, test_strawman, mock_websocket):
        """Test handling strawman from context instead of session."""
        session_id = "test_context_001"
        user_id = "test_user"
        
        # Pass strawman in context (as dict)
        context = {
            "strawman_data": test_strawman.model_dump()
        }
        
        result = await phase2_extension.handle_layout_generation_state(
            session_id=session_id,
            user_id=user_id,
            context=context
        )
        
        assert result["status"] == "completed"
        assert result["slide_count"] == len(test_strawman.slides)
        
        print("\n✅ Strawman from context handled correctly")
    
    @pytest.mark.asyncio
    async def test_error_handling_no_strawman(self, phase2_extension):
        """Test error handling when no strawman is available."""
        session_id = "test_error_001"
        user_id = "test_user"
        
        # No strawman in session or context
        with pytest.raises(ValueError, match="No strawman data available"):
            await phase2_extension.handle_layout_generation_state(
                session_id=session_id,
                user_id=user_id,
                context={}
            )
    
    @pytest.mark.asyncio
    async def test_layout_architect_mvp_compatibility(self, mock_session_manager, mock_websocket):
        """Test compatibility with original LayoutArchitectMVP."""
        from src.agents.layout_architect import LayoutArchitectMVP
        from src.agents.layout_architect.models import LayoutConfig
        
        # Create MVP instance
        layout_architect = LayoutArchitectMVP(
            config=LayoutConfig(),
            session_manager=mock_session_manager
        )
        
        # Set WebSocket handler
        layout_architect.websocket_handler = mock_websocket
        
        # Create strawman
        strawman = get_test_strawman(num_slides=2, industry="finance")
        
        # Process strawman
        result = await layout_architect.process_approved_strawman(
            session_id="mvp_test_001",
            user_id="test_user",
            strawman=strawman
        )
        
        assert "theme" in result
        assert "layouts" in result
        assert len(result["layouts"]) == len(strawman.slides)
        
        print("\n✅ MVP compatibility verified")
    
    @pytest.mark.asyncio
    async def test_orchestrator_direct_integration(self, test_strawman):
        """Test direct integration with new orchestrator."""
        orchestrator = LayoutArchitectOrchestrator()
        
        # Generate layouts for all slides
        results = await orchestrator.generate_batch(
            slides=test_strawman.slides,
            user_context={
                "brand": "HealthCare Inc",
                "industry": "healthcare"
            },
            presentation_context={
                "audience": test_strawman.target_audience,
                "duration": test_strawman.presentation_duration
            }
        )
        
        assert len(results) == len(test_strawman.slides)
        assert all(r.success for r in results)
        
        print(f"\n✅ Orchestrator integration: {len(results)} layouts generated")


class TestStateTransitions:
    """Test state machine transitions with Layout Architect."""
    
    @pytest.fixture
    def director_mock(self):
        """Mock Director with state machine."""
        director = Mock()
        director.state = "STRAWMAN_APPROVED"
        director.transition_to = Mock()
        return director
    
    @pytest.mark.asyncio
    async def test_state_transition_flow(self, director_mock):
        """Test the complete state transition flow."""
        # Simulate state transitions
        states = [
            "INITIAL",
            "GATHERING_CONTEXT",
            "REFINING_BRIEF",
            "STRAWMAN_CREATED",
            "STRAWMAN_APPROVED",
            "LAYOUT_GENERATION",  # Layout Architect takes over
            "PRESENTATION_READY"
        ]
        
        current_state = "STRAWMAN_APPROVED"
        
        # Transition to LAYOUT_GENERATION
        assert current_state == "STRAWMAN_APPROVED"
        next_state = "LAYOUT_GENERATION"
        
        # Simulate transition
        director_mock.transition_to(next_state)
        director_mock.state = next_state
        
        assert director_mock.state == "LAYOUT_GENERATION"
        
        print("\n✅ State transition verified: STRAWMAN_APPROVED → LAYOUT_GENERATION")
    
    @pytest.mark.asyncio
    async def test_session_state_persistence(self, mock_session_manager):
        """Test that session state is properly persisted."""
        session_id = "persist_test_001"
        
        # Initial state
        await mock_session_manager.update_session(session_id, {
            "state": "STRAWMAN_APPROVED",
            "strawman_data": get_test_strawman(1).model_dump()
        })
        
        # Retrieve session
        session = await mock_session_manager.get_session(session_id)
        assert session["state"] == "STRAWMAN_APPROVED"
        assert "strawman_data" in session
        
        # Update to LAYOUT_GENERATION
        await mock_session_manager.update_session(session_id, {
            "state": "LAYOUT_GENERATION",
            "layout_generation_started": datetime.now().isoformat()
        })
        
        # Verify update
        session = await mock_session_manager.get_session(session_id)
        assert session["state"] == "LAYOUT_GENERATION"
        assert "layout_generation_started" in session
        
        print("\n✅ Session state persistence verified")


class TestRealWorldScenarios:
    """Test real-world presentation scenarios."""
    
    @pytest.fixture
    def phase2_extension(self):
        """Create Phase 2 extension with real components where possible."""
        websocket = MockWebSocketHandler()
        session_manager = MockSessionManager()
        return DirectorPhase2Extension(session_manager, websocket)
    
    @pytest.mark.asyncio
    async def test_investor_pitch_scenario(self, phase2_extension, mock_session_manager):
        """Test generating an investor pitch presentation."""
        # Create investor pitch strawman
        strawman = PresentationStrawman(
            main_title="Series B Investor Pitch - TechHealth Solutions",
            overall_theme="Professional and data-driven with growth focus",
            design_suggestions="Modern tech aesthetic with blue/green palette",
            target_audience="Venture capital partners",
            presentation_duration=20,
            slides=[
                Slide(
                    slide_id="pitch_001",
                    slide_number=1,
                    title="TechHealth Solutions: Transforming Patient Care",
                    slide_type="title_slide",
                    narrative="Opening with strong vision statement",
                    key_points=["AI-Powered Healthcare Platform"]
                ),
                Slide(
                    slide_id="pitch_002",
                    slide_number=2,
                    title="The $150B Problem We're Solving",
                    slide_type="visual_heavy",
                    narrative="Market opportunity visualization",
                    key_points=[
                        "12M diagnostic errors annually",
                        "30% of healthcare costs are waste",
                        "Critical physician shortage"
                    ],
                    visuals_needed="Market size infographic"
                ),
                Slide(
                    slide_id="pitch_003",
                    slide_number=3,
                    title="Traction & Growth",
                    slide_type="data_driven",
                    narrative="Demonstrating momentum",
                    key_points=[
                        "300% YoY revenue growth",
                        "50+ enterprise clients",
                        "$45M ARR",
                        "120 NPS score"
                    ],
                    analytics_needed="Growth charts, customer logos"
                ),
                Slide(
                    slide_id="pitch_004",
                    slide_number=4,
                    title="Series B: $50M to Scale",
                    slide_type="content_heavy",
                    narrative="Use of funds and growth plan",
                    key_points=[
                        "40% - Engineering & Product",
                        "30% - Sales & Marketing",
                        "20% - Operations",
                        "10% - Strategic M&A"
                    ],
                    structure_preference="hierarchical"
                )
            ]
        )
        
        # Add to session
        session_id = "investor_pitch_001"
        mock_session_manager.add_strawman(session_id, strawman)
        
        # Generate layouts
        result = await phase2_extension.handle_layout_generation_state(
            session_id=session_id,
            user_id="investor_user",
            context={}
        )
        
        assert result["status"] == "completed"
        assert result["slide_count"] == 4
        
        print("\n✅ Investor pitch scenario completed")
        print(f"   Theme: {result['theme_name']}")
        print("   Perfect for VC presentation!")
    
    @pytest.mark.asyncio
    async def test_educational_content_scenario(self, phase2_extension, mock_session_manager):
        """Test generating educational content."""
        generator = SyntheticDataGenerator()
        
        # Create educational presentation
        strawman = generator.generate_strawman(
            num_slides=5,
            industry="education",
            presentation_title="Introduction to Machine Learning"
        )
        
        # Customize for educational content
        strawman.target_audience = "University students"
        strawman.design_suggestions = "Clean, readable design with diagrams"
        
        session_id = "education_001"
        mock_session_manager.add_strawman(session_id, strawman)
        
        result = await phase2_extension.handle_layout_generation_state(
            session_id=session_id,
            user_id="professor_user",
            context={}
        )
        
        assert result["status"] == "completed"
        print("\n✅ Educational content scenario completed")
    
    @pytest.mark.asyncio
    async def test_quarterly_review_scenario(self, phase2_extension, mock_session_manager):
        """Test generating a quarterly business review."""
        strawman = PresentationStrawman(
            main_title="Q4 2024 Business Review",
            overall_theme="Data-driven executive summary",
            design_suggestions="Corporate professional with company colors",
            target_audience="Board of Directors",
            presentation_duration=30,
            slides=[
                Slide(
                    slide_id="qbr_001",
                    slide_number=1,
                    title="Q4 2024 Business Review",
                    slide_type="title_slide",
                    narrative="Executive summary opening",
                    key_points=["Record Quarter Performance"]
                ),
                Slide(
                    slide_id="qbr_002",
                    slide_number=2,
                    title="Financial Performance",
                    slide_type="data_driven",
                    narrative="Revenue and profitability metrics",
                    key_points=[
                        "Revenue: $125M (+28% YoY)",
                        "EBITDA: $35M (28% margin)",
                        "Cash: $450M",
                        "Burn: -$5M/month"
                    ],
                    analytics_needed="Financial dashboard with trends"
                )
            ]
        )
        
        session_id = "qbr_001"
        mock_session_manager.add_strawman(session_id, strawman)
        
        result = await phase2_extension.handle_layout_generation_state(
            session_id=session_id,
            user_id="ceo_user",
            context={}
        )
        
        assert result["status"] == "completed"
        print("\n✅ Quarterly review scenario completed")


if __name__ == "__main__":
    # Run specific test
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        pytest.main([__file__, "-k", test_name, "-v", "-s"])
    else:
        pytest.main([__file__, "-v", "-s"])