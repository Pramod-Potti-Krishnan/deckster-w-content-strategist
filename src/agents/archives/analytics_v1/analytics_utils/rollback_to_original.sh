#!/bin/bash
# Emergency Rollback Script for Analytics System
# Created: 2024-08-11
# Purpose: Restore original analytics system if playbook implementation has issues

echo "=========================================="
echo "ANALYTICS SYSTEM EMERGENCY ROLLBACK"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKUP_DIR="$SCRIPT_DIR/backup_before_playbook"
AGENTS_DIR="$SCRIPT_DIR/.."

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ ERROR: Backup directory not found at $BACKUP_DIR"
    echo "Cannot proceed with rollback."
    exit 1
fi

echo "📁 Backup directory found: $BACKUP_DIR"
echo ""
echo "⚠️  This will restore the following files:"
echo "   - conductor.py"
echo "   - data_synthesizer.py"
echo "   - python_chart_agent.py"
echo "   - mermaid_chart_agent.py"
echo "   - analytics_agent.py"
echo ""
read -p "Are you sure you want to rollback? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting rollback..."
    
    # Restore analytics_utils files
    if [ -f "$BACKUP_DIR/conductor.py.backup" ]; then
        cp "$BACKUP_DIR/conductor.py.backup" "$SCRIPT_DIR/conductor.py"
        echo "✅ Restored conductor.py"
    fi
    
    if [ -f "$BACKUP_DIR/data_synthesizer.py.backup" ]; then
        cp "$BACKUP_DIR/data_synthesizer.py.backup" "$SCRIPT_DIR/data_synthesizer.py"
        echo "✅ Restored data_synthesizer.py"
    fi
    
    if [ -f "$BACKUP_DIR/python_chart_agent.py.backup" ]; then
        cp "$BACKUP_DIR/python_chart_agent.py.backup" "$SCRIPT_DIR/python_chart_agent.py"
        echo "✅ Restored python_chart_agent.py"
    fi
    
    if [ -f "$BACKUP_DIR/mermaid_chart_agent.py.backup" ]; then
        cp "$BACKUP_DIR/mermaid_chart_agent.py.backup" "$SCRIPT_DIR/mermaid_chart_agent.py"
        echo "✅ Restored mermaid_chart_agent.py"
    fi
    
    # Restore analytics_agent.py to parent directory
    if [ -f "$BACKUP_DIR/analytics_agent.py.backup" ]; then
        cp "$BACKUP_DIR/analytics_agent.py.backup" "$AGENTS_DIR/analytics_agent.py"
        echo "✅ Restored analytics_agent.py"
    fi
    
    # Disable playbook system feature flag
    echo ""
    echo "📝 Setting environment variable to disable playbook system..."
    export USE_PLAYBOOK_SYSTEM=false
    echo "✅ USE_PLAYBOOK_SYSTEM=false"
    
    echo ""
    echo "=========================================="
    echo "✅ ROLLBACK COMPLETE"
    echo "=========================================="
    echo ""
    echo "The original analytics system has been restored."
    echo "All files have been reverted to their backed-up versions."
    echo ""
    echo "To make the environment variable permanent, add to your shell profile:"
    echo "  export USE_PLAYBOOK_SYSTEM=false"
    echo ""
else
    echo "❌ Rollback cancelled."
    exit 0
fi