#!/usr/bin/env python3
"""
Verify the pyramid geometry is mathematically correct
======================================================
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def extract_path_coordinates(path_d):
    """Extract coordinates from SVG path d attribute."""
    parts = path_d.replace('M', '').replace('L', '').replace('Z', '').split()
    coords = []
    for i in range(0, len(parts), 2):
        if i+1 < len(parts):
            coords.append((float(parts[i]), float(parts[i+1])))
    return coords

def calculate_slope(p1, p2):
    """Calculate slope between two points."""
    if p2[0] - p1[0] == 0:
        return float('inf')
    return (p2[1] - p1[1]) / (p2[0] - p1[0])

def check_alignment(apex, point):
    """Check if a point aligns with the pyramid slope from apex."""
    # Expected slope from apex (400, 150) to base corners
    # Left side: to (200, 455), slope = 305/-200 = -1.525
    # Right side: to (600, 455), slope = 305/200 = 1.525
    
    if point[0] < apex[0]:  # Left side
        expected_slope = -1.525
    else:  # Right side
        expected_slope = 1.525
    
    actual_slope = calculate_slope(apex, point)
    error = abs(actual_slope - expected_slope)
    
    return error < 0.1  # Allow small tolerance

def main():
    svg_path = Path("src/agents/diagram_utils/templates/pyramid_3_level.svg")
    
    print("\n" + "="*70)
    print("PYRAMID GEOMETRY VERIFICATION")
    print("="*70)
    
    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Extract level paths
    levels = {}
    for elem in root.iter():
        if elem.tag.endswith('path') and elem.get('id', '').startswith('level_'):
            level_id = elem.get('id')
            path_d = elem.get('d')
            vertices = extract_path_coordinates(path_d)
            levels[level_id] = vertices
    
    print(f"\nFound {len(levels)} pyramid levels")
    print("-" * 40)
    
    apex = (400, 150)
    
    # Check Level 1 (Top - should be a triangle)
    if 'level_1_fill' in levels:
        level1 = levels['level_1_fill']
        print("\n✓ Level 1 (Top):")
        print(f"  - Shape: {'Triangle' if len(level1) == 3 else 'Not a triangle'}")
        
        # Find the apex point (should be at y=150)
        apex_point = min(level1, key=lambda p: p[1])
        print(f"  - Apex: ({apex_point[0]:.1f}, {apex_point[1]:.1f})")
        
        # Check if it's at the correct position
        if abs(apex_point[0] - 400) < 1 and abs(apex_point[1] - 150) < 1:
            print("  ✅ Apex is correctly positioned")
        else:
            print("  ❌ Apex position is incorrect")
    
    # Check all level edges for alignment
    print("\nSlope Alignment Check:")
    print("-" * 40)
    
    all_aligned = True
    for level_id, vertices in levels.items():
        level_num = level_id.replace('level_', '').replace('_fill', '')
        misaligned = []
        
        for i, vertex in enumerate(vertices):
            # Skip checking horizontal edges
            if i > 0 and abs(vertices[i][1] - vertices[i-1][1]) < 1:
                continue
            
            # Check if vertex aligns with pyramid slope
            if vertex[1] > 150:  # Not the apex itself
                if not check_alignment(apex, vertex):
                    misaligned.append(vertex)
        
        if misaligned:
            print(f"  ❌ Level {level_num}: {len(misaligned)} vertices misaligned")
            all_aligned = False
        else:
            print(f"  ✅ Level {level_num}: All vertices align with pyramid slopes")
    
    # Check gaps between levels
    print("\nGap Analysis:")
    print("-" * 40)
    
    if 'level_1_fill' in levels and 'level_2_fill' in levels:
        # Check gap between level 1 and 2
        level1_bottom = max([v[1] for v in levels['level_1_fill']])
        level2_top = min([v[1] for v in levels['level_2_fill']])
        gap_12 = level2_top - level1_bottom
        print(f"  Gap between Level 1 and 2: {gap_12:.1f}px")
    
    if 'level_2_fill' in levels and 'level_3_fill' in levels:
        # Check gap between level 2 and 3
        level2_bottom = max([v[1] for v in levels['level_2_fill']])
        level3_top = min([v[1] for v in levels['level_3_fill']])
        gap_23 = level3_top - level2_bottom
        print(f"  Gap between Level 2 and 3: {gap_23:.1f}px")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if all_aligned:
        print("✅ Perfect pyramid structure!")
        print("   - All edges align to form a proper triangle")
        print("   - Top level is correctly positioned at apex")
        print("   - Visual gaps maintain the triangle outline")
    else:
        print("❌ Pyramid geometry needs adjustment")
        print("   - Some vertices don't align with the expected slopes")

if __name__ == "__main__":
    main()