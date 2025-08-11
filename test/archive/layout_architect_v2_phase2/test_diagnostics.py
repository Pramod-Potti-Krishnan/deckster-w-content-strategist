"""
Diagnostic utilities for Layout Architect tests.

Provides pre-test checks, performance monitoring, and debugging helpers.
"""

import os
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from src.agents.layout_architect.utils.model_utils import (
    check_model_availability, get_available_models, get_model_name
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TestDiagnostics:
    """Diagnostic utilities for tests."""
    
    def __init__(self):
        self.performance_data: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    async def check_prerequisites(self) -> Dict[str, bool]:
        """
        Check all prerequisites before running tests.
        
        Returns:
            Dict with check results
        """
        results = {}
        
        # Check API keys
        results['google_api_key'] = bool(os.getenv('GOOGLE_API_KEY'))
        results['gemini_api_key'] = bool(os.getenv('GEMINI_API_KEY'))
        results['any_api_key'] = results['google_api_key'] or results['gemini_api_key']
        
        # Check model availability
        if results['any_api_key']:
            available_models = await get_available_models()
            results['available_models'] = available_models
            results['preferred_model'] = get_model_name()
            results['preferred_model_available'] = results['preferred_model'] in available_models
            results['any_model_available'] = len(available_models) > 0
        else:
            results['available_models'] = []
            results['preferred_model'] = get_model_name()
            results['preferred_model_available'] = False
            results['any_model_available'] = False
        
        return results
    
    def start_timing(self, test_name: str):
        """Start timing a test."""
        self.start_times[test_name] = time.time()
    
    def end_timing(self, test_name: str) -> float:
        """
        End timing a test and record the duration.
        
        Returns:
            Duration in seconds
        """
        if test_name not in self.start_times:
            logger.warning(f"No start time recorded for {test_name}")
            return 0.0
        
        duration = time.time() - self.start_times[test_name]
        
        if test_name not in self.performance_data:
            self.performance_data[test_name] = []
        self.performance_data[test_name].append(duration)
        
        del self.start_times[test_name]
        return duration
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """Get performance summary for all tests."""
        summary = {}
        
        for test_name, durations in self.performance_data.items():
            if durations:
                summary[test_name] = {
                    'min': min(durations),
                    'max': max(durations),
                    'avg': sum(durations) / len(durations),
                    'count': len(durations),
                    'total': sum(durations)
                }
        
        return summary
    
    def save_performance_baseline(self, filename: Optional[str] = None):
        """Save performance data as baseline."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test/layout_architect_v2_phase2/performance_baseline_{timestamp}.json"
        
        import json
        summary = self.get_performance_summary()
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'performance_data': summary,
                'raw_data': self.performance_data
            }, f, indent=2)
        
        logger.info(f"Performance baseline saved to {filename}")
    
    @staticmethod
    async def diagnose_hanging_test(test_func, timeout: int = 30) -> Dict[str, any]:
        """
        Diagnose why a test might be hanging.
        
        Args:
            test_func: The test function to diagnose
            timeout: Timeout in seconds
            
        Returns:
            Diagnostic information
        """
        import traceback
        
        result = {
            'completed': False,
            'duration': None,
            'error': None,
            'traceback': None
        }
        
        start_time = time.time()
        
        try:
            # Run with timeout
            await asyncio.wait_for(test_func(), timeout=timeout)
            result['completed'] = True
            result['duration'] = time.time() - start_time
        except asyncio.TimeoutError:
            result['error'] = 'TimeoutError'
            result['duration'] = timeout
            result['traceback'] = f"Test timed out after {timeout} seconds"
        except Exception as e:
            result['error'] = type(e).__name__
            result['duration'] = time.time() - start_time
            result['traceback'] = traceback.format_exc()
        
        return result


# Global diagnostics instance
diagnostics = TestDiagnostics()


async def run_pre_test_checks():
    """Run all pre-test checks and print results."""
    print("\n" + "="*60)
    print("LAYOUT ARCHITECT TEST DIAGNOSTICS")
    print("="*60)
    
    results = await diagnostics.check_prerequisites()
    
    print("\n📋 API Key Status:")
    print(f"   GOOGLE_API_KEY: {'✅ Set' if results['google_api_key'] else '❌ Not set'}")
    print(f"   GEMINI_API_KEY: {'✅ Set' if results['gemini_api_key'] else '❌ Not set'}")
    
    if results['any_api_key']:
        print("\n🤖 Model Availability:")
        print(f"   Preferred model: {results['preferred_model']}")
        print(f"   Available models: {', '.join(results['available_models']) if results['available_models'] else 'None'}")
        
        if not results['preferred_model_available'] and results['available_models']:
            print(f"   ⚠️  Preferred model not available, will use: {results['available_models'][0]}")
    else:
        print("\n❌ No API keys found! Tests will fail.")
        print("   Please set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file")
    
    print("\n🏃 Test Categories:")
    print("   Quick tests: pytest -m 'quick'")
    print("   Skip slow tests: pytest -m 'not slow'")
    print("   Integration only: pytest -m 'integration'")
    
    print("\n⏱️  Timeout Settings:")
    print("   Default: 30s")
    print("   Slow tests: 120s")
    print("   E2E tests: 180s")
    
    print("="*60 + "\n")
    
    return results


if __name__ == "__main__":
    # Run diagnostics when executed directly
    asyncio.run(run_pre_test_checks())