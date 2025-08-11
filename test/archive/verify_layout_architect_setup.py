#!/usr/bin/env python3
"""
Verification script to check if Layout Architect is properly set up.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Layout Architect Setup Verification ===\n")

# 1. Check Python imports
print("1. Checking Python imports...")
errors = []

try:
    from src.agents.layout_architect import LayoutArchitectMVP
    print("   ✅ Layout Architect agent imports correctly")
except ImportError as e:
    errors.append(f"   ❌ Cannot import Layout Architect: {e}")

try:
    from src.agents.director_out import DirectorOUT
    print("   ✅ Director OUT imports correctly")
except ImportError as e:
    errors.append(f"   ❌ Cannot import Director OUT: {e}")

try:
    from src.agents.director_phase2_integration import DirectorPhase2Extension
    print("   ✅ Phase 2 integration imports correctly")
except ImportError as e:
    errors.append(f"   ❌ Cannot import Phase 2 integration: {e}")

# 2. Check environment variables
print("\n2. Checking environment variables...")
env_vars = {
    "GOOGLE_API_KEY": "Required for theme generation",
    "SUPABASE_URL": "Required for database",
    "SUPABASE_ANON_KEY": "Required for database",
    "LAYOUT_ARCHITECT_MODEL": "Optional (default: gemini-1.5-flash)",
    "LAYOUT_GRID_WIDTH": "Optional (default: 160)",
    "LAYOUT_GRID_HEIGHT": "Optional (default: 90)"
}

for var, desc in env_vars.items():
    value = os.getenv(var)
    if value:
        if "KEY" in var:
            print(f"   ✅ {var}: {'*' * 8} ({desc})")
        else:
            print(f"   ✅ {var}: {value} ({desc})")
    else:
        if "Optional" in desc:
            print(f"   ⚠️  {var}: Not set ({desc})")
        else:
            print(f"   ❌ {var}: Missing! ({desc})")
            errors.append(f"Missing required env var: {var}")

# 3. Check file structure
print("\n3. Checking file structure...")
files_to_check = [
    "src/agents/layout_architect/__init__.py",
    "src/agents/layout_architect/agent.py",
    "src/agents/layout_architect/models.py",
    "src/agents/layout_architect/theme_generator.py",
    "src/agents/layout_architect/layout_engine.py",
    "src/agents/layout_architect/tools/__init__.py",
    "src/agents/layout_architect/tools/grid_calculator.py",
    "src/agents/layout_architect/tools/white_space_tool.py",
    "src/agents/layout_architect/tools/alignment_validator.py",
    "src/agents/director_out.py",
    "src/agents/director_phase2_integration.py",
    "migrations/create_themes_table.sql",
    "test/test_layout_architect.py",
    "test/test_layout_architect_integration.py",
    "test/test_layout_with_main.py"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} - Missing!")
        errors.append(f"Missing file: {file_path}")

# 4. Check state machine
print("\n4. Checking state machine...")
try:
    from src.workflows.state_machine import WorkflowOrchestrator
    orchestrator = WorkflowOrchestrator()
    if "LAYOUT_GENERATION" in orchestrator.STATES:
        print("   ✅ LAYOUT_GENERATION state is configured")
    else:
        print("   ❌ LAYOUT_GENERATION state not found in state machine")
        errors.append("LAYOUT_GENERATION state missing from state machine")
    
    # Check transitions
    if "GENERATE_STRAWMAN" in orchestrator.TRANSITIONS:
        if "LAYOUT_GENERATION" in orchestrator.TRANSITIONS["GENERATE_STRAWMAN"]:
            print("   ✅ GENERATE_STRAWMAN → LAYOUT_GENERATION transition configured")
        else:
            print("   ❌ Missing transition from GENERATE_STRAWMAN to LAYOUT_GENERATION")
            errors.append("Missing state transition to LAYOUT_GENERATION")
except Exception as e:
    print(f"   ❌ Error checking state machine: {e}")
    errors.append(f"State machine error: {e}")

# 5. Check WebSocket handler integration
print("\n5. Checking WebSocket handler integration...")
try:
    with open("src/handlers/websocket.py", "r") as f:
        ws_content = f.read()
        
    checks = [
        ("DirectorPhase2Extension import", "from src.agents.director_phase2_integration import DirectorPhase2Extension"),
        ("Phase 2 extension initialization", "self.phase2_extension"),
        ("LAYOUT_GENERATION handling", "LAYOUT_GENERATION"),
        ("Accept_Strawman mapping", '"Accept_Strawman": "LAYOUT_GENERATION"')
    ]
    
    for check_name, check_str in checks:
        if check_str in ws_content:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name} not found")
            errors.append(f"WebSocket handler missing: {check_name}")
            
except Exception as e:
    print(f"   ❌ Error checking WebSocket handler: {e}")
    errors.append(f"WebSocket handler error: {e}")

# Summary
print("\n" + "="*50)
if errors:
    print(f"\n❌ Setup verification FAILED with {len(errors)} error(s):\n")
    for error in errors:
        print(f"  - {error}")
    print("\nPlease fix the above issues before running tests.")
else:
    print("\n✅ All checks passed! Layout Architect is properly set up.")
    print("\nYou can now run:")
    print("  - Unit tests: pytest test/test_layout_architect.py -v")
    print("  - Integration test: python test/test_layout_architect_integration.py")
    print("  - Full test: python main.py (Terminal 1), then python test/test_layout_with_main.py (Terminal 2)")

sys.exit(1 if errors else 0)