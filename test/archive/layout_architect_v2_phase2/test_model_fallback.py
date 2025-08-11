"""
Test with model fallback to diagnose API issues.
"""

import os
import sys
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def get_working_model() -> Optional[str]:
    """Try to find a working Gemini model."""
    from pydantic_ai.models.gemini import GeminiModel
    
    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    for model_name in models:
        try:
            # Try to create the model
            model = GeminiModel(model_name)
            # If no exception, assume it works
            print(f"✅ Model {model_name} is available")
            return model_name
        except Exception as e:
            print(f"❌ Model {model_name} failed: {e}")
            continue
    
    return None

if __name__ == "__main__":
    # Load env
    from dotenv import load_dotenv
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    # Set GEMINI_API_KEY from GOOGLE_API_KEY if needed
    if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    
    working_model = get_working_model()
    if working_model:
        print(f"\n✅ Recommended model: {working_model}")
    else:
        print("\n❌ No working models found!")