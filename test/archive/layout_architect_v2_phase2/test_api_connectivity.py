"""
Quick test to verify Gemini API connectivity and model availability.
"""

import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel
import time

class SimpleOutput(BaseModel):
    message: str

async def test_gemini_models():
    """Test different Gemini models to see which ones work."""
    
    # Ensure API key is set
    if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    
    models_to_test = [
        "gemini-2.5-flash",
        "gemini-2.0-flash", 
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    for model_name in models_to_test:
        print(f"\nTesting {model_name}...")
        try:
            start_time = time.time()
            
            # Create a simple agent
            model = GeminiModel(model_name)
            agent = Agent(
                model,
                output_type=SimpleOutput,
                system_prompt="You are a helpful assistant. Reply with a simple message."
            )
            
            # Set a timeout for the API call
            result = await asyncio.wait_for(
                agent.run("Say hello"),
                timeout=10.0  # 10 second timeout
            )
            
            elapsed = time.time() - start_time
            print(f"✅ {model_name} works! Response time: {elapsed:.2f}s")
            print(f"   Response: {result.output.message}")
            
        except asyncio.TimeoutError:
            print(f"❌ {model_name} timed out after 10 seconds")
        except Exception as e:
            print(f"❌ {model_name} failed: {type(e).__name__}: {e}")
    
    # Test API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"\n✅ API key is set (starts with: {api_key[:10]}...)")
    else:
        print("\n❌ No API key found!")

if __name__ == "__main__":
    # Load .env file if it exists
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env from: {env_path}")
    
    asyncio.run(test_gemini_models())