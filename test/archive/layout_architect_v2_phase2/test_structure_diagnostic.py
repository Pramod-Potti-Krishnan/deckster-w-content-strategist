"""
Diagnostic test for Structure Agent hanging issue.
"""

import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SimpleOutput(BaseModel):
    """Simple output model"""
    message: str = Field(description="A simple message")
    items: List[str] = Field(description="List of items", default_factory=list)


async def test_simple_agent():
    """Test if a simple agent works with gemini-2.5-flash"""
    # Set up API key
    if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    
    try:
        # Create simple agent
        model = GeminiModel("gemini-2.5-flash")
        agent = Agent(
            model,
            output_type=SimpleOutput,
            system_prompt="You are a helpful assistant. Return a simple message."
        )
        
        # Run agent
        print("Testing simple agent with gemini-2.5-flash...")
        result = await agent.run("Say hello and list three colors")
        print(f"✅ Success! Message: {result.output.message}")
        print(f"   Items: {result.output.items}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_structure_agent_direct():
    """Test the structure agent directly"""
    from src.agents.layout_architect import StructureAgent
    from src.models.agents import Slide
    
    try:
        # Create test slide
        slide = Slide(
            slide_id="test_001",
            slide_number=1,
            title="Test Title",
            slide_type="title_slide",
            key_points=["Welcome"],
            narrative="Opening slide"
        )
        
        # Create agent
        print("\nTesting StructureAgent with gemini-2.5-flash...")
        agent = StructureAgent()
        
        # Use timeout
        print("Running analyze_structure with 20s timeout...")
        result = await asyncio.wait_for(
            agent.analyze_structure(slide),
            timeout=20
        )
        
        print(f"✅ Success! Found {len(result.containers)} containers")
        
    except asyncio.TimeoutError:
        print("❌ Timeout after 20 seconds!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Load env
    from dotenv import load_dotenv
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env from: {env_path}")
    
    # Run tests
    asyncio.run(test_simple_agent())
    asyncio.run(test_structure_agent_direct())