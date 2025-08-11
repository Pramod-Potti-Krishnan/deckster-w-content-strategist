#!/usr/bin/env python3
"""
Quick test to verify layout improvements.
"""

import asyncio
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import from same directory
from test_director_e2e import DirectorE2ETester

async def main():
    """Run specific scenario to test improvements."""
    tester = DirectorE2ETester()
    
    # Run educational scenario (4) which had the three-column issue
    print("\n🧪 Testing Layout Architect Improvements...")
    print("=" * 60)
    
    result = await tester.run_scenario("educational")
    
    print("\n📊 Test Result Summary:")
    print(f"  Passed: {'✅' if result['passed'] else '❌'}")
    print(f"  States completed: {', '.join(result['states_completed'])}")
    if result['errors']:
        print(f"  Errors: {result['errors']}")

if __name__ == "__main__":
    asyncio.run(main())