#!/usr/bin/env python3
"""
Quick test to verify imports are working correctly.
Run this before running the full test suite.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")

# Also set GEMINI_API_KEY from GOOGLE_API_KEY if needed
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    print("Set GEMINI_API_KEY from GOOGLE_API_KEY")

print(f"Python path includes: {project_root}")

try:
    print("\n1. Testing basic imports...")
    from src.agents.layout_architect import (
        LayoutArchitectOrchestrator,
        MVPLayout,
        MVPContainer,
        ThemeDefinition,
        ContainerManifest
    )
    print("✓ Basic imports successful")
    
    print("\n2. Testing agent imports...")
    from src.agents.layout_architect import (
        ThemeAgent,
        StructureAgent,
        LayoutEngineAgent
    )
    print("✓ Agent imports successful")
    
    print("\n3. Testing model imports...")
    from src.agents.layout_architect import (
        DesignTokens,
        SemanticContainer,
        LayoutState,
        GridPosition,
        ContainerContent
    )
    print("✓ Model imports successful")
    
    print("\n4. Testing orchestrator creation...")
    print(f"   GOOGLE_API_KEY set: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")
    print(f"   GEMINI_API_KEY set: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
    orchestrator = LayoutArchitectOrchestrator()
    print("✓ Orchestrator created successfully")
    
    print("\n5. Testing synthetic data imports...")
    from .test_synthetic_data import SyntheticDataGenerator
    generator = SyntheticDataGenerator()
    print("✓ Synthetic data generator created")
    
    print("\n✅ All imports successful! You can now run the tests.")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nMake sure you have:")
    print("1. Activated your virtual environment")
    print("2. Installed all dependencies: pip install -r requirements.txt")
    print("3. Are running from the project root directory")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)