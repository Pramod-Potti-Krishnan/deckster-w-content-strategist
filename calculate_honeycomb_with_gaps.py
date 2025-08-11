#!/usr/bin/env python3
"""
Calculate honeycomb geometry with 15% larger hexagons and gaps
================================================================
"""

import math

# Original radius
original_radius = 50

# New radius (15% larger)
new_radius = original_radius * 1.15
print(f"Original radius: {original_radius}")
print(f"New radius (15% larger): {new_radius}")

# Gap between hexagons (let's use 4px for visual separation)
gap = 4

# For regular hexagons with pointy-top orientation
# Distance between centers for adjacent hexagons (sharing an edge normally)
# = R * sqrt(3) for horizontal neighbors
# = R * 1.5 for vertical step

# With gaps, we need to add the gap to the distance
horizontal_spacing = new_radius * math.sqrt(3) + gap
vertical_step = new_radius * 1.5 + gap * math.sqrt(3)/2

print(f"\nSpacing with gaps:")
print(f"Horizontal spacing: {horizontal_spacing:.3f}")
print(f"Vertical step: {vertical_step:.3f}")

# Center hexagon at (400, 300)
center_x = 400
center_y = 300

print(f"\nHexagon centers:")
print(f"Center (Hex 1): ({center_x}, {center_y})")

# Calculate positions for the 6 surrounding hexagons
# Using the ring layout pattern
positions = []

# East (Hex 2)
east_x = center_x + horizontal_spacing
east_y = center_y
positions.append(("East (Hex 2)", east_x, east_y))

# Northeast (Hex 3)
ne_x = center_x + horizontal_spacing/2
ne_y = center_y - vertical_step
positions.append(("Northeast (Hex 3)", ne_x, ne_y))

# Northwest (Hex 4)
nw_x = center_x - horizontal_spacing/2
nw_y = center_y - vertical_step
positions.append(("Northwest (Hex 4)", nw_x, nw_y))

# West (Hex 5)
west_x = center_x - horizontal_spacing
west_y = center_y
positions.append(("West (Hex 5)", west_x, west_y))

# Southwest (Hex 6)
sw_x = center_x - horizontal_spacing/2
sw_y = center_y + vertical_step
positions.append(("Southwest (Hex 6)", sw_x, sw_y))

# Southeast (Hex 7)
se_x = center_x + horizontal_spacing/2
se_y = center_y + vertical_step
positions.append(("Southeast (Hex 7)", se_x, se_y))

for label, x, y in positions:
    print(f"{label}: ({x:.3f}, {y:.3f})")

# Calculate hexagon vertices for pointy-top orientation
def calculate_vertices(cx, cy, r):
    """Calculate 6 vertices of a regular hexagon (pointy-top)."""
    vertices = []
    for i in range(6):
        angle = math.radians(-90 + i * 60)  # Start from top, go clockwise
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        vertices.append((x, y))
    return vertices

# Generate SVG path for a hexagon
def generate_path(cx, cy, r):
    vertices = calculate_vertices(cx, cy, r)
    path_parts = [f"M {vertices[0][0]:.3f} {vertices[0][1]:.3f}"]
    for v in vertices[1:]:
        path_parts.append(f"L {v[0]:.3f} {v[1]:.3f}")
    path_parts.append("Z")
    return " ".join(path_parts)

print(f"\nSVG Paths for R={new_radius:.3f}:")
print(f"Center hex: {generate_path(center_x, center_y, new_radius)}")

# Check if the honeycomb fits in the 800x600 viewBox
all_positions = [(center_x, center_y)] + [p[1:] for p in positions]
min_x = min(x - new_radius for x, y in all_positions)
max_x = max(x + new_radius for x, y in all_positions)
min_y = min(y - new_radius for x, y in all_positions)
max_y = max(y + new_radius for x, y in all_positions)

print(f"\nBounding box:")
print(f"X: {min_x:.1f} to {max_x:.1f} (width: {max_x - min_x:.1f})")
print(f"Y: {min_y:.1f} to {max_y:.1f} (height: {max_y - min_y:.1f})")
print(f"Fits in 800x600: {max_x - min_x < 800 and max_y - min_y < 600}")