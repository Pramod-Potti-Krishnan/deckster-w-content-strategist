#!/usr/bin/env python3
"""
Comprehensive Test for SVGDiagramAgent Text Wrapping
=====================================================

Tests the actual SVGDiagramAgent class and its text wrapping functionality.
This ensures the programmatic text wrapping works correctly for all cases.
"""

import asyncio
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.path.append(str(Path(__file__).parent))

from src.agents.diagram_utils.models import DiagramSpec, SVGTemplateSpec
import xml.etree.ElementTree as ET
from typing import List

# Import only the methods we need to test, not the full agent
class SVGTextWrapper:
    """Minimal wrapper to test text wrapping functions without API keys."""
    
    def _wrap_text_for_svg(self, text: str, max_width_chars: int) -> List[str]:
        """Copy of the wrap function from SVGDiagramAgent."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + (1 if current_line else 0) <= max_width_chars:
                current_line.append(word)
                current_length += word_length + (1 if current_line else 0)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _get_pyramid_level_width(self, element_id: str) -> int:
        """Copy of width function from SVGDiagramAgent."""
        width_map = {
            'level_1_text': 12,  # Top level - narrowest (force wrapping)
            'level_2_text': 20,  # Middle level
            'level_3_text': 32,  # Bottom level - widest
        }
        return width_map.get(element_id, 30)

OUTPUT_DIR = Path("test/diagram-tests/test_output/svg_agent_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_svg_and_check_wrapping(svg_content: str, element_id: str) -> dict:
    """Parse SVG and check if text is wrapped into multiple lines."""
    tree = ET.fromstring(svg_content)
    
    # Find the element
    for elem in tree.iter():
        if elem.get('id') == element_id:
            # Check for tspan elements (indicates wrapping)
            tspans = list(elem.findall('.//{http://www.w3.org/2000/svg}tspan'))
            
            if tspans:
                return {
                    'wrapped': True,
                    'lines': len(tspans),
                    'text_lines': [tspan.text for tspan in tspans],
                    'y_position': elem.get('y')
                }
            else:
                return {
                    'wrapped': False,
                    'text': elem.text,
                    'y_position': elem.get('y')
                }
    
    return {'found': False}


async def test_pyramid_text_wrapping():
    """Test text wrapping for pyramid diagram with various text lengths."""
    print("\n" + "="*70)
    print("TESTING PYRAMID TEXT WRAPPING")
    print("="*70)
    
    agent = SVGDiagramAgent()
    
    test_cases = [
        {
            'name': 'Short text (no wrapping needed)',
            'level_1': 'Vision',
            'level_2': 'Strategy',
            'level_3': 'Execution',
            'title': 'Simple'
        },
        {
            'name': 'Strategic Vision (should wrap)',
            'level_1': 'Strategic Vision',
            'level_2': 'Tactical Planning',
            'level_3': 'Operational Excellence',
            'title': 'Business Strategy'
        },
        {
            'name': 'Long text (multiple wraps)',
            'level_1': 'Long Term Strategic Vision',
            'level_2': 'Middle Management Planning Process',
            'level_3': 'Day to Day Operational Excellence Standards',
            'title': 'Comprehensive Business Strategy Framework'
        },
        {
            'name': 'Very long single word',
            'level_1': 'InternationalizationAndLocalization',
            'level_2': 'ImplementationStrategy',
            'level_3': 'ExecutionExcellence',
            'title': 'I18n/L10n'
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        print("-" * 50)
        
        # Create spec directly (bypassing pydantic_ai agent)
        spec = SVGTemplateSpec(
            template_name="pyramid_3_level.svg",
            text_replacements={
                'level_1_text': test_case['level_1'],
                'level_2_text': test_case['level_2'],
                'level_3_text': test_case['level_3'],
                'pyramid_title': test_case['title']
            },
            color_replacements={
                'level_1_fill': '#a5b4fc',
                'level_2_fill': '#818cf8',
                'level_3_fill': '#6366f1'
            }
        )
        
        # Apply template directly using the internal method
        template_path = Path("src/agents/diagram_utils/templates/pyramid_3_level.svg")
        context = agent._create_context(DiagramSpec(
            diagram_type="pyramid",
            content={},
            theme={'colors': {'primary': '#6366f1'}},
            layout_hints={}
        ))
        
        svg_content = await agent._apply_template_spec(
            template_path,
            spec,
            context
        )
        
        # Check wrapping for each level
        for level_id in ['level_1_text', 'level_2_text', 'level_3_text']:
            result = parse_svg_and_check_wrapping(svg_content, level_id)
            level_text = test_case[level_id.replace('_text', '')]
            
            if result.get('wrapped'):
                print(f"  ✅ {level_id}: Wrapped into {result['lines']} lines")
                for j, line in enumerate(result['text_lines']):
                    print(f"      Line {j+1}: '{line}'")
            else:
                text = result.get('text', 'NOT FOUND')
                if len(level_text) > agent._get_pyramid_level_width(level_id):
                    print(f"  ❌ {level_id}: Should wrap but didn't - '{text}'")
                else:
                    print(f"  ✓ {level_id}: No wrap needed - '{text}'")
        
        # Save output
        output_file = OUTPUT_DIR / f"pyramid_test_{i+1}.svg"
        output_file.write_text(svg_content)
        print(f"  Saved to: {output_file}")


async def test_width_constraints():
    """Test that width constraints are properly applied."""
    print("\n" + "="*70)
    print("TESTING WIDTH CONSTRAINTS")
    print("="*70)
    
    agent = SVGDiagramAgent()
    
    # Test the width constraints
    constraints = {
        'level_1_text': agent._get_pyramid_level_width('level_1_text'),
        'level_2_text': agent._get_pyramid_level_width('level_2_text'),
        'level_3_text': agent._get_pyramid_level_width('level_3_text'),
        'unknown_element': agent._get_pyramid_level_width('unknown_element')
    }
    
    print("Width constraints (characters):")
    for elem_id, width in constraints.items():
        print(f"  {elem_id}: {width} chars")
    
    # Test wrap function with different lengths
    print("\nTesting _wrap_text_for_svg function:")
    
    test_texts = [
        ("Short text", 20),
        ("This is a much longer text that definitely needs wrapping", 20),
        ("OneVeryLongWordWithoutSpaces", 15),
        ("Multiple words that should wrap nicely across lines", 25)
    ]
    
    for text, max_width in test_texts:
        lines = agent._wrap_text_for_svg(text, max_width)
        print(f"\n  Text: '{text}'")
        print(f"  Max width: {max_width} chars")
        print(f"  Result: {len(lines)} line(s)")
        for i, line in enumerate(lines):
            print(f"    Line {i+1}: '{line}' ({len(line)} chars)")


async def test_edge_cases():
    """Test edge cases for text wrapping."""
    print("\n" + "="*70)
    print("TESTING EDGE CASES")
    print("="*70)
    
    agent = SVGDiagramAgent()
    
    edge_cases = [
        {
            'name': 'Empty text',
            'text': '',
            'expected_lines': 1
        },
        {
            'name': 'Single character',
            'text': 'A',
            'expected_lines': 1
        },
        {
            'name': 'Exactly at limit',
            'text': 'A' * 12,  # Exactly 12 chars for level_1
            'expected_lines': 1
        },
        {
            'name': 'Just over limit',
            'text': 'A' * 13,  # 13 chars for level_1 (limit is 12)
            'expected_lines': 1  # Single word can't be split
        },
        {
            'name': 'Multiple spaces',
            'text': 'Word1     Word2     Word3',
            'expected_lines': 2
        },
        {
            'name': 'Special characters',
            'text': 'Strategy & Vision',
            'expected_lines': 2
        }
    ]
    
    print("Testing edge cases with level_1_text (12 char limit):")
    for case in edge_cases:
        lines = agent._wrap_text_for_svg(case['text'], 12)
        status = "✅" if len(lines) == case['expected_lines'] else "❌"
        print(f"\n  {status} {case['name']}")
        print(f"     Input: '{case['text']}'")
        print(f"     Expected lines: {case['expected_lines']}, Got: {len(lines)}")
        print(f"     Result: {lines}")


async def test_other_templates():
    """Test that non-pyramid templates still work correctly."""
    print("\n" + "="*70)
    print("TESTING OTHER TEMPLATES")
    print("="*70)
    
    agent = SVGDiagramAgent()
    
    # Test matrix template (should not wrap by default)
    spec = SVGTemplateSpec(
        template_name="matrix_2x2.svg",
        text_replacements={
            'quadrant_1': 'High Growth High Share Products',  # Long text
            'quadrant_2': 'Question Marks',
            'quadrant_3': 'Dogs',
            'quadrant_4': 'Cash Cows',
            'x_label': 'Market Share',
            'y_label': 'Market Growth Rate',
            'matrix_title': 'BCG Growth-Share Matrix Analysis'
        },
        color_replacements={}
    )
    
    template_path = Path("src/agents/diagram_utils/templates/matrix_2x2.svg")
    if template_path.exists():
        context = agent._create_context(DiagramSpec(
            diagram_type="matrix",
            content={},
            theme={'colors': {'primary': '#6366f1'}},
            layout_hints={}
        ))
        
        svg_content = await agent._apply_template_spec(
            template_path,
            spec,
            context
        )
        
        # Check if any text was wrapped (matrix elements typically don't wrap)
        for elem_id in ['quadrant_1', 'quadrant_2', 'quadrant_3', 'quadrant_4']:
            result = parse_svg_and_check_wrapping(svg_content, elem_id)
            if result.get('wrapped'):
                print(f"  Note: {elem_id} was wrapped (unexpected for matrix)")
            else:
                print(f"  ✓ {elem_id}: Not wrapped (as expected for matrix)")
        
        output_file = OUTPUT_DIR / "matrix_test.svg"
        output_file.write_text(svg_content)
        print(f"\n  Saved matrix test to: {output_file}")
    else:
        print("  ⚠️ Matrix template not found")


async def main():
    """Run all SVGDiagramAgent tests."""
    print("\n" + "="*70)
    print("COMPREHENSIVE SVGDiagramAgent TEXT WRAPPING TESTS")
    print("="*70)
    
    # Run all test suites
    await test_pyramid_text_wrapping()
    await test_width_constraints()
    await test_edge_cases()
    await test_other_templates()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print(f"Check outputs in: {OUTPUT_DIR}")
    print("="*70)
    
    # Summary
    print("\n📊 Test Coverage:")
    print("  ✓ Pyramid text wrapping with various lengths")
    print("  ✓ Width constraint validation")
    print("  ✓ Edge cases (empty, single char, special chars)")
    print("  ✓ Other templates (matrix)")
    print("\n💡 Note: Check the debug output above for any ❌ marks indicating issues")


if __name__ == "__main__":
    asyncio.run(main())