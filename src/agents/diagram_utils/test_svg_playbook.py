#!/usr/bin/env python3
"""
Test script for SVG Template Playbook
======================================

Validates that the SVG playbook is properly structured and functional.

Author: Test System
Date: 2024
"""

import sys
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.agents.diagram_utils.svg_playbook import (
    SVG_PLAYBOOK,
    get_template_spec,
    get_templates_by_category,
    get_text_capacity,
    get_placeholder_ids,
    get_color_elements,
    get_template_dimensions,
    get_all_template_names,
    get_template_categories,
    get_existing_templates,
    get_planned_templates,
    validate_svg_structure,
    calculate_text_fit
)


def test_playbook_structure():
    """Test the basic structure of the playbook."""
    print("Testing SVG Playbook Structure...")
    print("=" * 50)
    
    # Check version
    assert "version" in SVG_PLAYBOOK
    print(f"✓ Playbook version: {SVG_PLAYBOOK['version']}")
    
    # Check templates exist
    assert "templates" in SVG_PLAYBOOK
    template_count = len(SVG_PLAYBOOK["templates"])
    print(f"✓ Total templates: {template_count}")
    
    # Check categories
    categories = get_template_categories()
    print(f"✓ Categories: {', '.join(categories)}")
    
    # Check status distribution
    existing = get_existing_templates()
    planned = get_planned_templates()
    print(f"✓ Existing templates: {len(existing)}")
    print(f"✓ Planned templates: {len(planned)}")
    
    return True


def test_template_specifications():
    """Test individual template specifications."""
    print("\n\nTesting Template Specifications...")
    print("=" * 50)
    
    # Test a few key templates
    test_templates = ["cycle_4_step", "honeycomb_7", "matrix_2x2", "pyramid_3_level"]
    
    for template_name in test_templates:
        print(f"\nTesting '{template_name}':")
        spec = get_template_spec(template_name)
        
        # Check required fields
        assert spec is not None, f"Spec not found for {template_name}"
        assert "name" in spec
        assert "category" in spec
        assert "file_name" in spec
        assert "status" in spec
        assert "visual_description" in spec
        assert "dimensions" in spec
        assert "text_placeholders" in spec
        assert "color_elements" in spec
        assert "when_to_use" in spec
        
        print(f"  ✓ Name: {spec['name']}")
        print(f"  ✓ Category: {spec['category']}")
        print(f"  ✓ Status: {spec['status']}")
        print(f"  ✓ File: {spec['file_name']}")
        
        # Check text placeholders
        placeholders = spec.get("text_placeholders", {})
        print(f"  ✓ Text placeholders: {len(placeholders)}")
        
        # Check each placeholder has capacity info
        for placeholder_key, placeholder_data in placeholders.items():
            assert "id" in placeholder_data
            assert "purpose" in placeholder_data
            assert "capacity" in placeholder_data
            capacity = placeholder_data["capacity"]
            assert "chars_per_line" in capacity
            assert "max_lines" in capacity
            assert "font_size" in capacity
        
        print(f"  ✓ All placeholders have capacity specs")
    
    return True


def test_helper_functions():
    """Test helper functions."""
    print("\n\nTesting Helper Functions...")
    print("=" * 50)
    
    # Test category filtering
    print("\nTesting category filtering:")
    for category in ["cycle", "funnel", "matrix"]:
        templates = get_templates_by_category(category)
        print(f"  {category}: {len(templates)} templates")
        assert len(templates) > 0
    
    # Test text capacity retrieval
    print("\nTesting text capacity:")
    capacity = get_text_capacity("cycle_4_step", "step_1_text")
    assert capacity is not None
    assert capacity["chars_per_line"] == 15
    assert capacity["max_lines"] == 2
    print(f"  ✓ cycle_4_step/step_1_text: {capacity['chars_per_line']} chars × {capacity['max_lines']} lines")
    
    # Test placeholder ID retrieval
    print("\nTesting placeholder IDs:")
    ids = get_placeholder_ids("honeycomb_7")
    assert len(ids) > 0
    assert "hex_1_text" in ids
    print(f"  ✓ honeycomb_7 has {len(ids)} placeholder IDs")
    
    # Test color elements
    print("\nTesting color elements:")
    colors = get_color_elements("matrix_2x2")
    assert "quadrant_fills" in colors
    print(f"  ✓ matrix_2x2 has color elements: {list(colors.keys())}")
    
    # Test dimensions
    print("\nTesting dimensions:")
    dims = get_template_dimensions("pyramid_3_level")
    assert dims["width"] == 1000
    assert dims["height"] == 750
    print(f"  ✓ pyramid_3_level: {dims['width']}×{dims['height']}")
    
    return True


def test_text_fitting():
    """Test text fitting calculation."""
    print("\n\nTesting Text Fitting...")
    print("=" * 50)
    
    # Test short text that fits
    capacity = {"chars_per_line": 20, "max_lines": 2}
    result = calculate_text_fit("Short text", capacity)
    assert result["fits"] == True
    print(f"✓ Short text fits: {result['lines_needed']} lines")
    
    # Test long text that needs wrapping
    long_text = "This is a much longer text that will need to be wrapped across multiple lines"
    result = calculate_text_fit(long_text, capacity)
    print(f"✓ Long text needs: {result['lines_needed']} lines (max: {result['max_lines']})")
    print(f"  Wrapped: {result['wrapped_text']}")
    
    # Test text that exceeds capacity
    capacity = {"chars_per_line": 10, "max_lines": 1}
    result = calculate_text_fit("This text is too long", capacity)
    assert result["fits"] == False
    print(f"✓ Overflow detected: needs {result['lines_needed']} lines, max is {result['max_lines']}")
    
    return True


def test_svg_validation():
    """Test SVG structure validation."""
    print("\n\nTesting SVG Validation...")
    print("=" * 50)
    
    # Create mock SVG content
    mock_svg = """
    <svg xmlns="http://www.w3.org/2000/svg">
        <text id="step_1_text">Step 1</text>
        <text id="step_2_text">Step 2</text>
        <text id="step_3_text">Step 3</text>
        <text id="step_4_text">Step 4</text>
    </svg>
    """
    
    # Test validation with matching template
    result = validate_svg_structure(mock_svg, "cycle_4_step")
    print(f"✓ Validation for matching SVG: {len(result['missing_ids'])} missing IDs")
    
    # Test validation with missing IDs
    incomplete_svg = """
    <svg xmlns="http://www.w3.org/2000/svg">
        <text id="step_1_text">Step 1</text>
    </svg>
    """
    
    result = validate_svg_structure(incomplete_svg, "cycle_4_step")
    assert result["valid"] == False
    print(f"✓ Detected missing IDs: {len(result['missing_ids'])} missing")
    
    return True


def test_template_coverage():
    """Test template coverage across categories."""
    print("\n\nTesting Template Coverage...")
    print("=" * 50)
    
    categories = get_template_categories()
    
    print("\nTemplates by category:")
    for category in categories:
        templates = get_templates_by_category(category)
        print(f"  {category:15} : {len(templates):2} templates")
        
        # Show first few templates
        for template in templates[:3]:
            spec = get_template_spec(template)
            status = spec.get("status", "unknown")
            print(f"    - {template:25} [{status}]")
    
    # Check we have good coverage
    assert len(categories) >= 10, "Should have at least 10 categories"
    print(f"\n✓ Good category coverage: {len(categories)} categories")
    
    all_templates = get_all_template_names()
    assert len(all_templates) >= 20, "Should have at least 20 templates"
    print(f"✓ Good template coverage: {len(all_templates)} total templates")
    
    return True


def test_existing_files():
    """Test that existing templates are marked correctly."""
    print("\n\nTesting Existing Files...")
    print("=" * 50)
    
    # Get the templates directory
    templates_dir = Path(__file__).parent / "templates"
    
    if templates_dir.exists():
        svg_files = list(templates_dir.glob("*.svg"))
        print(f"Found {len(svg_files)} SVG files in templates directory")
        
        # Check that existing files are marked as existing
        for svg_file in svg_files:
            template_name = svg_file.stem  # filename without extension
            spec = get_template_spec(template_name)
            if spec:
                status = spec.get("status")
                print(f"  {template_name}: status = {status}")
                if status != "existing":
                    print(f"    ⚠️ Warning: File exists but status is '{status}'")
    else:
        print("⚠️ Templates directory not found - skipping file check")
    
    return True


def main():
    """Run all tests."""
    print("SVG PLAYBOOK TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Structure", test_playbook_structure),
        ("Specifications", test_template_specifications),
        ("Helper Functions", test_helper_functions),
        ("Text Fitting", test_text_fitting),
        ("SVG Validation", test_svg_validation),
        ("Template Coverage", test_template_coverage),
        ("Existing Files", test_existing_files)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} test passed")
            else:
                failed += 1
                print(f"\n❌ {test_name} test failed")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} test failed with error: {e}")
    
    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed successfully!")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())