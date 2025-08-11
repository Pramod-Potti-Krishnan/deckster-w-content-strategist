# Content Agent V4 Testing Options

## Comprehensive Test - All Features in One

### Main Test Script
```bash
# The main comprehensive test with all features and options
python3 test/test_content_agent_v4.py
```

### Available Command-Line Options
```bash
# Show help and all available options
python3 test/test_content_agent_v4.py --help

# Basic test with defaults (3 slides, healthcare theme)
python3 test/test_content_agent_v4.py

# Show all details with verbose output
python3 test/test_content_agent_v4.py --verbose

# Display content as it's generated in real-time
python3 test/test_content_agent_v4.py --real-time

# Test single slide only
python3 test/test_content_agent_v4.py --test-mode single

# Test full deck with icon enrichment
python3 test/test_content_agent_v4.py --test-mode full

# Use different themes
python3 test/test_content_agent_v4.py --theme finance
python3 test/test_content_agent_v4.py --theme tech

# Export results
python3 test/test_content_agent_v4.py --export-html --export-json

# Combine multiple options
python3 test/test_content_agent_v4.py --verbose --real-time --test-mode full --theme healthcare --export-html
```

### Test Modes
- `single`: Test 1 slide (quick verification)
- `multi`: Test 3 slides (default)
- `full`: Test all slides with icon enrichment

### Themes
- `healthcare`: AI Healthcare Revolution (default)
- `finance`: Q3 Financial Results
- `tech`: Microservices Architecture

### Display Options
- `--verbose`: Show detailed process information
- `--real-time`: Display full content as generated
- `--show-process`: Show all 5 stages (default: True)
- `--show-playbooks`: Display playbook selections
- `--show-briefs`: Show strategic brief details
- `--show-icons`: Display icon enrichment (default: True)
- `--pause`: Pause between slides

### Export Options
- `--export-html`: Export results to HTML file
- `--export-json`: Export results to JSON file

## Legacy Test Scripts (Consolidated into main test)

The following test scripts have been consolidated into the comprehensive `test_content_agent_v4.py`:
- `test_content_agent_v4_simple.py` → Use `--test-mode single`
- `test_content_agent_v4_debug.py` → Use `--verbose`
- `test_content_agent_v4_verbose.py` → Use `--real-time --verbose`
- `test_content_agent_v4_dual_phase.py` → Use `--test-mode full`

The main test script provides all functionality with better formatting and more options.

```bash
# Show all available options
python3 test/test_content_agent_v4.py --help

# Basic run
python3 test/test_content_agent_v4.py

# Verbose mode - show all internal details
python3 test/test_content_agent_v4.py --verbose

# Real-time display - show content as generated
python3 test/test_content_agent_v4.py --real-time

# Pause between slides for review
python3 test/test_content_agent_v4.py --pause-between-slides

# Show strategic briefs
python3 test/test_content_agent_v4.py --show-briefs

# Show playbook selections
python3 test/test_content_agent_v4.py --show-playbooks

# Show icon mapping process
python3 test/test_content_agent_v4.py --show-icons

# Export results to HTML
python3 test/test_content_agent_v4.py --export-html

# Combine multiple options
python3 test/test_content_agent_v4.py --verbose --real-time --show-playbooks
```

## Quick Test Sequence

```bash
# 1. First verify basic functionality
echo "=== Testing basic content generation ==="
python3 test/test_content_agent_v4_simple.py

# 2. Check detailed content blocks
echo -e "\n=== Debugging content structure ==="
python3 test/test_content_agent_v4_debug.py

# 3. Test full dual-phase pipeline
echo -e "\n=== Testing dual-phase architecture ==="
python3 test/test_content_agent_v4_dual_phase.py

# 4. Run verbose test for complete visibility
echo -e "\n=== Verbose process test ==="
python3 test/test_content_agent_v4_verbose.py
```

## Integration Tests

### Test with Theme Agent
```bash
# Test V4 with theme generation
python3 test/test_theme_content_direct.py --use-v4
```

### Test with Director Agent
```bash
# Test V4 in full pipeline
python3 test/test_director_e2e.py --content-version v4
```

## Performance Test Script

```bash
# Create a simple performance test
cat > test_v4_performance.sh << 'EOF'
#!/bin/bash
echo "Content Agent V4 Performance Test"
echo "================================="

# Time single slide generation
echo -e "\nTiming single slide generation..."
time python3 test/test_content_agent_v4_simple.py

# Time 3-slide deck generation
echo -e "\nTiming 3-slide deck generation..."
time python3 test/test_content_agent_v4_dual_phase.py

echo -e "\nTest complete!"
EOF

chmod +x test_v4_performance.sh
./test_v4_performance.sh
```

## Rate Limit Handling Script

```bash
# Create a script with delays to avoid rate limits
cat > test_v4_with_delays.sh << 'EOF'
#!/bin/bash
echo "V4 Test with Rate Limit Handling"
echo "================================"

# Run tests with delays between them
tests=(
    "test_content_agent_v4_simple.py"
    "test_content_agent_v4_debug.py"
    "test_content_agent_v4_dual_phase.py"
)

for test in "${tests[@]}"; do
    echo -e "\nRunning $test..."
    python3 test/$test
    
    # Wait 30 seconds between tests to avoid rate limits
    if [ "$test" != "${tests[-1]}" ]; then
        echo "Waiting 30 seconds to avoid rate limits..."
        sleep 30
    fi
done

echo -e "\nAll tests completed!"
EOF

chmod +x test_v4_with_delays.sh
./test_v4_with_delays.sh
```

## Comparison Test Script

```bash
# Compare V4 output with V3
cat > compare_v3_v4.sh << 'EOF'
#!/bin/bash
echo "Comparing V3 and V4 Content Generation"
echo "======================================"

# Test V3
echo -e "\n=== Testing V3 ==="
python3 test/test_content_agent_v3.py --real-time | head -50

# Test V4
echo -e "\n=== Testing V4 ==="
python3 test/test_content_agent_v4_simple.py

echo -e "\nComparison complete!"
EOF

chmod +x compare_v3_v4.sh
./compare_v3_v4.sh
```

## Output Capture Script

```bash
# Capture V4 output for analysis
cat > capture_v4_output.sh << 'EOF'
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
output_dir="v4_test_output_$timestamp"
mkdir -p $output_dir

echo "Capturing V4 test outputs to $output_dir"
echo "========================================"

# Run each test and capture output
tests=(
    "simple"
    "debug"
    "dual_phase"
    "verbose"
)

for test in "${tests[@]}"; do
    echo -e "\nRunning $test test..."
    python3 test/test_content_agent_v4_${test}.py > "$output_dir/${test}_output.txt" 2>&1
    echo "Output saved to $output_dir/${test}_output.txt"
done

echo -e "\nAll outputs captured in $output_dir/"
ls -la $output_dir/
EOF

chmod +x capture_v4_output.sh
./capture_v4_output.sh
```

## Tips for Testing

1. **Start with simple test** to verify basic functionality
2. **Use debug test** to troubleshoot content generation issues
3. **Run verbose test** to see the complete process flow
4. **Add delays** between tests to avoid API rate limits
5. **Use --pause-between-slides** for interactive review
6. **Capture outputs** for later analysis and comparison