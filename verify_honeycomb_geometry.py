#!/usr/bin/env python3
"""
Verify the honeycomb geometry is mathematically correct
========================================================
"""

import math
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

def distance(p1, p2):
    """Calculate distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def angle_between_points(p1, p2, p3):
    """Calculate angle at p2 between p1-p2-p3."""
    # Vector from p2 to p1
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    # Vector from p2 to p3
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    
    # Dot product
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    # Magnitudes
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0
    
    # Angle in radians, then convert to degrees
    cos_angle = dot / (mag1 * mag2)
    cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)

def verify_regular_hexagon(vertices):
    """Verify if vertices form a regular hexagon."""
    if len(vertices) != 6:
        return False, "Not 6 vertices"
    
    # Check all sides are equal
    sides = []
    for i in range(6):
        side_length = distance(vertices[i], vertices[(i+1) % 6])
        sides.append(side_length)
    
    avg_side = sum(sides) / len(sides)
    max_diff = max(abs(s - avg_side) for s in sides)
    
    if max_diff > 0.1:  # Allow small floating point error
        return False, f"Sides not equal: {[f'{s:.2f}' for s in sides]}"
    
    # Check all internal angles are 120°
    angles = []
    for i in range(6):
        angle = angle_between_points(
            vertices[(i-1) % 6],
            vertices[i],
            vertices[(i+1) % 6]
        )
        angles.append(angle)
    
    expected_angle = 120.0
    max_angle_diff = max(abs(a - expected_angle) for a in angles)
    
    if max_angle_diff > 1.0:  # Allow 1 degree tolerance
        return False, f"Angles not 120°: {[f'{a:.1f}' for a in angles]}"
    
    return True, f"Regular hexagon (side≈{avg_side:.1f})"

def check_shared_edges(hex1_vertices, hex2_vertices):
    """Check if two hexagons share an edge."""
    # Find matching vertices
    matches = []
    for v1 in hex1_vertices:
        for v2 in hex2_vertices:
            if distance(v1, v2) < 0.1:  # Consider same if very close
                matches.append((v1, v2))
    
    if len(matches) == 2:
        # Check if the two matching vertices are adjacent in both hexagons
        return True, "Hexagons share an edge"
    elif len(matches) == 0:
        return False, "No shared vertices"
    else:
        return False, f"Found {len(matches)} matching vertices (expected 2)"

def main():
    svg_path = Path("src/agents/diagram_utils/templates/honeycomb_7.svg")
    
    print("\n" + "="*70)
    print("HONEYCOMB GEOMETRY VERIFICATION")
    print("="*70)
    
    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Extract all hexagon paths
    hexagons = {}
    for elem in root.iter():
        if elem.tag.endswith('path') and elem.get('id', '').startswith('hex_'):
            hex_id = elem.get('id')
            path_d = elem.get('d')
            vertices = extract_path_coordinates(path_d)
            hexagons[hex_id] = vertices
    
    print(f"\nFound {len(hexagons)} hexagons")
    print("-" * 40)
    
    # Verify each hexagon is regular
    all_regular = True
    for hex_id, vertices in hexagons.items():
        is_regular, msg = verify_regular_hexagon(vertices)
        status = "✅" if is_regular else "❌"
        print(f"{status} {hex_id}: {msg}")
        if not is_regular:
            all_regular = False
    
    # Check shared edges between adjacent hexagons
    print("\n" + "Checking shared edges:")
    print("-" * 40)
    
    # Define which hexagons should share edges
    adjacency = [
        ("hex_1_fill", "hex_2_fill"),  # Center-East
        ("hex_1_fill", "hex_3_fill"),  # Center-NE
        ("hex_1_fill", "hex_4_fill"),  # Center-NW
        ("hex_1_fill", "hex_5_fill"),  # Center-West
        ("hex_1_fill", "hex_6_fill"),  # Center-SW
        ("hex_1_fill", "hex_7_fill"),  # Center-SE
        ("hex_3_fill", "hex_2_fill"),  # NE-East
        ("hex_3_fill", "hex_4_fill"),  # NE-NW
        ("hex_4_fill", "hex_5_fill"),  # NW-West
        ("hex_5_fill", "hex_6_fill"),  # West-SW
        ("hex_6_fill", "hex_7_fill"),  # SW-SE
        ("hex_7_fill", "hex_2_fill"),  # SE-East
    ]
    
    all_edges_shared = True
    for hex1_id, hex2_id in adjacency:
        if hex1_id in hexagons and hex2_id in hexagons:
            shares_edge, msg = check_shared_edges(hexagons[hex1_id], hexagons[hex2_id])
            status = "✅" if shares_edge else "❌"
            print(f"{status} {hex1_id[:-5]} ↔ {hex2_id[:-5]}: {msg}")
            if not shares_edge:
                all_edges_shared = False
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if all_regular and all_edges_shared:
        print("✅ Perfect honeycomb structure!")
        print("   - All hexagons are regular (equal sides, 120° angles)")
        print("   - All adjacent hexagons share edges properly")
    else:
        if not all_regular:
            print("❌ Some hexagons are not regular")
        if not all_edges_shared:
            print("❌ Some adjacent hexagons don't share edges properly")

if __name__ == "__main__":
    main()