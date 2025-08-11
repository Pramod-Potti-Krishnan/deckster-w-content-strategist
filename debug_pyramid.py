#!/usr/bin/env python3
"""Debug pyramid coordinates"""

# Apex at (400, 150)
# Base corners at (200, 455) and (600, 455)

# Calculate slope
apex_x = 400
apex_y = 150
base_left_x = 200
base_right_x = 600
base_y = 455

# Slope calculation
height = base_y - apex_y  # 305
half_width = apex_x - base_left_x  # 200

print(f"Height: {height}")
print(f"Half width: {half_width}")
print(f"Slope ratio: {half_width/height}")

# For any y value, calculate x positions
def calc_x_positions(y, with_gap=0):
    """Calculate left and right x positions for a given y"""
    distance_from_apex = y - apex_y
    x_offset = (half_width / height) * distance_from_apex
    
    left_x = apex_x - x_offset + with_gap
    right_x = apex_x + x_offset - with_gap
    
    return left_x, right_x

print("\nLevel 1 (Top Triangle):")
print(f"  Apex: ({apex_x}, {apex_y})")
left, right = calc_x_positions(250, with_gap=5)
print(f"  Base at y=250: ({left:.3f}, 250) to ({right:.3f}, 250)")

print("\nLevel 2 (Middle Trapezoid):")
left_top, right_top = calc_x_positions(255, with_gap=5)
left_bot, right_bot = calc_x_positions(350, with_gap=5)
print(f"  Top at y=255: ({left_top:.3f}, 255) to ({right_top:.3f}, 255)")
print(f"  Bottom at y=350: ({left_bot:.3f}, 350) to ({right_bot:.3f}, 350)")

print("\nLevel 3 (Bottom Trapezoid):")
left_top, right_top = calc_x_positions(355, with_gap=5)
left_bot, right_bot = calc_x_positions(455, with_gap=5)
print(f"  Top at y=355: ({left_top:.3f}, 355) to ({right_top:.3f}, 355)")
print(f"  Bottom at y=455: ({left_bot:.3f}, 455) to ({right_bot:.3f}, 455)")

print("\n\nSVG Path coordinates:")
print("Level 1: M 339.344 250 L 460.656 250 L 400 150 Z")
print("Level 2: M 273.770 350 L 526.230 350 L 463.770 255 L 336.230 255 Z")  
print("Level 3: M 205 455 L 595 455 L 529.344 355 L 270.656 355 Z")