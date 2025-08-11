#!/bin/bash

# Run All Diagram Tests
# =====================
# Tests the complete diagram generation pipeline

echo "=================================="
echo "RUNNING ALL DIAGRAM TESTS"
echo "=================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create output directory
mkdir -p test_output

# Test 1: Unit Tests (No API Required)
echo "1. Running Unit Tests..."
echo "------------------------"
for test in unit/test_*.py; do
    if [ -f "$test" ]; then
        echo "  Running: $(basename $test)"
        python3 "$test"
    fi
done
echo ""

# Test 2: Integration Tests
echo "2. Running Integration Tests..."
echo "-------------------------------"
for test in integration/test_*.py; do
    if [ -f "$test" ]; then
        echo "  Running: $(basename $test)"
        python3 "$test"
    fi
done
echo ""

# Test 3: Template Tests
echo "3. Running Template Tests..."
echo "----------------------------"
for test in templates/test_*.py; do
    if [ -f "$test" ]; then
        echo "  Running: $(basename $test)"
        python3 "$test"
    fi
done
echo ""

# Test 4: Pyramid Tests
echo "4. Running Pyramid Tests..."
echo "---------------------------"
for test in pyramid/test_*.py; do
    if [ -f "$test" ]; then
        echo "  Running: $(basename $test)"
        python3 "$test"
    fi
done
echo ""

echo "=================================="
echo "ALL TESTS COMPLETE"
echo "Check outputs in: test_output/"
echo "=================================="

# Count generated files
if [ -d "test_output" ]; then
    echo ""
    echo "Generated files:"
    find test_output -type f -name "*.svg" -o -name "*.mmd" -o -name "*.png" -o -name "*.txt" | wc -l
    echo "files created"
    echo ""
    echo "Files by type:"
    echo "  SVG files: $(find test_output -name "*.svg" | wc -l)"
    echo "  Mermaid files: $(find test_output -name "*.mmd" | wc -l)"
    echo "  PNG files: $(find test_output -name "*.png" | wc -l)"
    echo "  Text files: $(find test_output -name "*.txt" | wc -l)"
fi