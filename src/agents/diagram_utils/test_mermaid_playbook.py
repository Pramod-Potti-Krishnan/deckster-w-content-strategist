#!/usr/bin/env python3
"""
Test script for Mermaid Playbook
=================================

Validates that the Mermaid playbook is properly structured and functional.

Author: Test System
Date: 2024
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.agents.diagram_utils.mermaid_playbook import (
    MERMAID_PLAYBOOK,
    get_diagram_spec,
    get_diagrams_by_category,
    get_diagram_when_to_use,
    get_syntax_patterns,
    get_construction_rules,
    get_escape_rules,
    get_diagram_examples,
    find_diagrams_for_intent,
    get_all_diagram_types,
    get_diagram_categories,
    validate_mermaid_syntax,
    get_best_diagram_for_data,
    get_template,
    list_available_templates
)


def test_playbook_structure():
    """Test the basic structure of the playbook."""
    print("Testing Mermaid Playbook Structure...")
    print("=" * 50)
    
    # Check version
    assert "version" in MERMAID_PLAYBOOK
    print(f"✓ Playbook version: {MERMAID_PLAYBOOK['version']}")
    
    # Check diagrams exist
    assert "diagrams" in MERMAID_PLAYBOOK
    diagram_count = len(MERMAID_PLAYBOOK["diagrams"])
    print(f"✓ Total diagram types: {diagram_count}")
    
    # List all diagram types
    print("\nAvailable Diagram Types:")
    for i, diagram_type in enumerate(get_all_diagram_types(), 1):
        spec = get_diagram_spec(diagram_type)
        print(f"  {i}. {spec['name']} ({diagram_type}) - Category: {spec['category']}")
    
    return True


def test_diagram_specifications():
    """Test individual diagram specifications."""
    print("\n\nTesting Diagram Specifications...")
    print("=" * 50)
    
    test_types = ["flowchart", "class_diagram", "gantt", "quadrant"]
    
    for diagram_type in test_types:
        print(f"\nTesting '{diagram_type}':")
        spec = get_diagram_spec(diagram_type)
        
        # Check required fields
        assert spec is not None, f"Spec not found for {diagram_type}"
        assert "name" in spec
        assert "category" in spec
        assert "when_to_use" in spec
        assert "syntax_patterns" in spec
        assert "construction_rules" in spec
        assert "escape_rules" in spec
        
        print(f"  ✓ Name: {spec['name']}")
        print(f"  ✓ Category: {spec['category']}")
        print(f"  ✓ Use cases: {len(spec['when_to_use'])} defined")
        
        # Check new enhanced structure
        syntax_patterns = get_syntax_patterns(diagram_type)
        construction_rules = get_construction_rules(diagram_type)
        escape_rules = get_escape_rules(diagram_type)
        
        assert syntax_patterns, f"No syntax patterns for {diagram_type}"
        assert construction_rules, f"No construction rules for {diagram_type}"
        assert escape_rules, f"No escape rules for {diagram_type}"
        
        print(f"  ✓ Syntax patterns: {len(syntax_patterns)} patterns")
        print(f"  ✓ Construction rules: {len(construction_rules)} rules")
        print(f"  ✓ Escape rules: {len(escape_rules)} categories")
        
        # Check examples
        examples = get_diagram_examples(diagram_type)
        assert examples, f"No examples for {diagram_type}"
        print(f"  ✓ Examples: {list(examples.keys())}")
    
    return True


def test_helper_functions():
    """Test helper functions."""
    print("\n\nTesting Helper Functions...")
    print("=" * 50)
    
    # Test category filtering
    categories = get_diagram_categories()
    print(f"\nDiagram categories: {categories}")
    
    for category in categories[:3]:  # Test first 3 categories
        diagrams = get_diagrams_by_category(category)
        print(f"  {category}: {len(diagrams)} diagrams")
    
    # Test intent matching
    print("\nTesting intent matching:")
    test_intents = [
        "project timeline",
        "database design",
        "process flow",
        "task management"
    ]
    
    for intent in test_intents:
        matches = find_diagrams_for_intent(intent)
        print(f"  '{intent}' → {matches[:3] if len(matches) > 3 else matches}")
    
    # Test data-based recommendation
    print("\nTesting data-based recommendations:")
    test_data_sets = [
        {"tasks": [], "dates": [], "schedule": []},
        {"entities": [], "relationships": []},
        {"states": [], "workflow": []},
        {"quadrants": [], "compare": []}
    ]
    
    for data in test_data_sets:
        recommendation = get_best_diagram_for_data(data)
        print(f"  Data with {list(data.keys())} → {recommendation}")
    
    return True


def test_syntax_validation():
    """Test syntax validation."""
    print("\n\nTesting Syntax Validation...")
    print("=" * 50)
    
    # Test valid syntax
    valid_code = """flowchart TD
    A[Start] --> B[End]"""
    
    result = validate_mermaid_syntax("flowchart", valid_code)
    assert result["valid"], "Valid syntax marked as invalid"
    print(f"✓ Valid flowchart syntax recognized")
    
    # Test invalid syntax
    invalid_code = """gantt
    A[Start] --> B[End]"""
    
    result = validate_mermaid_syntax("flowchart", invalid_code)
    assert not result["valid"], "Invalid syntax marked as valid"
    print(f"✓ Invalid syntax detected correctly")
    
    return True


def test_templates():
    """Test template functionality."""
    print("\n\nTesting Templates...")
    print("=" * 50)
    
    templates = list_available_templates()
    print(f"Available templates: {len(templates)}")
    
    for template_name in templates[:3]:  # Test first 3 templates
        template = get_template(template_name)
        assert template is not None
        lines = template.strip().split('\n')
        print(f"  ✓ {template_name}: {lines[0][:50]}... ({len(lines)} lines)")
    
    return True


def test_enhanced_syntax():
    """Test the enhanced syntax patterns with placeholders."""
    print("\n\nTesting Enhanced Syntax Patterns...")
    print("=" * 50)
    
    # Test flowchart syntax patterns
    flowchart_patterns = get_syntax_patterns("flowchart")
    assert "diagram_start" in flowchart_patterns
    assert "node_definition" in flowchart_patterns
    assert "edge_definition" in flowchart_patterns
    print("✓ Flowchart has complete syntax patterns")
    
    # Check for placeholder format
    node_def = flowchart_patterns["node_definition"]["with_label"]
    assert "<nodeId>" in node_def, "Missing placeholder format"
    assert "<label>" in node_def, "Missing placeholder format"
    print("✓ Placeholders use correct <placeholder> format")
    
    # Test construction rules
    construction_rules = get_construction_rules("flowchart")
    assert len(construction_rules) > 5, "Should have detailed construction rules"
    print(f"✓ Construction rules: {len(construction_rules)} steps")
    
    # Test escape rules
    escape_rules = get_escape_rules("flowchart")
    assert "special_characters" in escape_rules
    assert "reserved_words" in escape_rules
    print("✓ Escape rules include special characters and reserved words")
    
    return True


def main():
    """Run all tests."""
    print("MERMAID PLAYBOOK TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Structure", test_playbook_structure),
        ("Specifications", test_diagram_specifications),
        ("Helper Functions", test_helper_functions),
        ("Syntax Validation", test_syntax_validation),
        ("Templates", test_templates),
        ("Enhanced Syntax", test_enhanced_syntax)
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