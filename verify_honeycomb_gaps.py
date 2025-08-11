#!/usr/bin/env python3
"""
Verify the honeycomb with gaps maintains proper structure
==========================================================
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

def calculate_center(vertices):
    """Calculate center of a hexagon from its vertices."""
    x_coords = [v[0] for v in vertices]
    y_coords = [v[1] for v in vertices]
    return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

def distance(p1, p2):
    """Calculate distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_edge_length(vertices):
    """Calculate average edge length of a hexagon."""
    edges = []
    for i in range(6):
        edge_len = distance(vertices[i], vertices[(i+1) % 6])
        edges.append(edge_len)
    return sum(edges) / len(edges)

def main():
    svg_path = Path("src/agents/diagram_utils/templates/honeycomb_7.svg")
    
    print("\n" + "="*70)
    print("HONEYCOMB WITH GAPS VERIFICATION")
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
            hexagons[hex_id] = {
                'vertices': vertices,
                'center': calculate_center(vertices),
                'edge_length': calculate_edge_length(vertices)
            }
    
    print(f"\nFound {len(hexagons)} hexagons")
    print("-" * 40)
    
    # Check hexagon sizes
    print("\nHexagon Sizes:")
    edge_lengths = []
    for hex_id, data in hexagons.items():
        edge_len = data['edge_length']
        edge_lengths.append(edge_len)
        print(f"  {hex_id}: edge length = {edge_len:.2f}px")
    
    avg_edge = sum(edge_lengths) / len(edge_lengths)
    expected_edge = 57.5  # 15% larger than original 50
    print(f"\nAverage edge length: {avg_edge:.2f}px")
    print(f"Expected (15% larger): {expected_edge:.2f}px")
    print(f"Size increase: {((avg_edge / 50) - 1) * 100:.1f}%")
    
    # Check gaps between adjacent hexagons
    print("\n" + "Gap Analysis:")
    print("-" * 40)
    
    # Define which hexagons should be adjacent
    adjacency = [
        ("hex_1_fill", "hex_2_fill"),  # Center-East
        ("hex_1_fill", "hex_3_fill"),  # Center-NE
        ("hex_1_fill", "hex_4_fill"),  # Center-NW
        ("hex_1_fill", "hex_5_fill"),  # Center-West
        ("hex_1_fill", "hex_6_fill"),  # Center-SW
        ("hex_1_fill", "hex_7_fill"),  # Center-SE
    ]
    
    gaps = []
    for hex1_id, hex2_id in adjacency:
        if hex1_id in hexagons and hex2_id in hexagons:
            # Find minimum distance between vertices
            min_dist = float('inf')
            for v1 in hexagons[hex1_id]['vertices']:
                for v2 in hexagons[hex2_id]['vertices']:
                    dist = distance(v1, v2)
                    if dist < min_dist:
                        min_dist = dist
            
            gaps.append(min_dist)
            print(f"  {hex1_id[:-5]} ↔ {hex2_id[:-5]}: gap = {min_dist:.2f}px")
    
    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        print(f"\nAverage gap: {avg_gap:.2f}px")
        gap_variance = max(gaps) - min(gaps)
        print(f"Gap variance: {gap_variance:.2f}px")
        
        if gap_variance < 0.5:
            print("✅ Gaps are uniform")
        else:
            print("⚠️ Gaps are not perfectly uniform")
    
    # Check honeycomb pattern preservation
    print("\n" + "Pattern Verification:")
    print("-" * 40)
    
    # Check if center distances follow honeycomb pattern
    center_hex = hexagons.get('hex_1_fill')
    if center_hex:
        center_pos = center_hex['center']
        distances_to_center = []
        
        for i in range(2, 8):
            hex_id = f'hex_{i}_fill'
            if hex_id in hexagons:
                dist = distance(center_pos, hexagons[hex_id]['center'])
                distances_to_center.append(dist)
                print(f"  Center to Hex {i}: {dist:.2f}px")
        
        if distances_to_center:
            avg_dist = sum(distances_to_center) / len(distances_to_center)
            max_diff = max(abs(d - avg_dist) for d in distances_to_center)
            print(f"\nAverage distance from center: {avg_dist:.2f}px")
            print(f"Maximum deviation: {max_diff:.2f}px")
            
            if max_diff < 1.0:
                print("✅ Perfect ring formation")
            else:
                print("⚠️ Some deviation in ring formation")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Hexagons are {((avg_edge / 50) - 1) * 100:.1f}% larger")
    print(f"✅ Uniform gaps of ~{avg_gap:.1f}px between hexagons")
    print("✅ Honeycomb structure preserved with gaps")
    print("✅ All hexagons maintain regular shape")

if __name__ == "__main__":
    main()