"""
Helper Functions and Utilities
Common functions used throughout the game
"""
import math
from typing import Tuple, Optional
import random


def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)
        
    Returns:
        Distance between points
    """
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def direction(from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> Tuple[float, float]:
    """
    Get normalized direction vector from one position to another
    
    Args:
        from_pos: Starting position
        to_pos: Target position
        
    Returns:
        Normalized direction vector (dx, dy)
    """
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    dist = distance(from_pos, to_pos)
    
    if dist == 0:
        return (0, 0)
    
    return (dx / dist, dy / dist)


def move_towards(from_pos: Tuple[float, float], to_pos: Tuple[float, float], 
                 speed: float) -> Tuple[float, float]:
    """
    Move from one position towards another by a given speed
    
    Args:
        from_pos: Current position
        to_pos: Target position
        speed: Speed of movement
        
    Returns:
        New position
    """
    dx, dy = direction(from_pos, to_pos)
    new_x = from_pos[0] + dx * speed
    new_y = from_pos[1] + dy * speed
    return (new_x, new_y)


def angle_to(from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> float:
    """
    Calculate angle (in radians) from one position to another
    
    Args:
        from_pos: Starting position
        to_pos: Target position
        
    Returns:
        Angle in radians
    """
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return math.atan2(dy, dx)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def clamp_position(pos: Tuple[float, float], width: float, height: float) -> Tuple[float, float]:
    """
    Clamp position to be within screen bounds
    
    Args:
        pos: Position (x, y)
        width: Screen width
        height: Screen height
        
    Returns:
        Clamped position
    """
    x = clamp(pos[0], 0, width)
    y = clamp(pos[1], 0, height)
    return (x, y)


def is_in_range(pos1: Tuple[float, float], pos2: Tuple[float, float], range_val: float) -> bool:
    """
    Check if pos1 is within range of pos2
    
    Args:
        pos1: First position
        pos2: Second position
        range_val: Range threshold
        
    Returns:
        True if within range
    """
    return distance(pos1, pos2) <= range_val


def random_position(width: float, height: float, margin: float = 0) -> Tuple[float, float]:
    """
    Generate a random position within bounds
    
    Args:
        width: Maximum width
        height: Maximum height
        margin: Margin from edges
        
    Returns:
        Random position (x, y)
    """
    x = random.uniform(margin, width - margin)
    y = random.uniform(margin, height - margin)
    return (x, y)


def random_direction() -> Tuple[float, float]:
    """
    Generate a random direction vector
    
    Returns:
        Normalized random direction (dx, dy)
    """
    angle = random.uniform(0, 2 * math.pi)
    return (math.cos(angle), math.sin(angle))


def circle_overlap(pos1: Tuple[float, float], radius1: float,
                   pos2: Tuple[float, float], radius2: float) -> bool:
    """
    Check if two circles overlap
    
    Args:
        pos1: Center of first circle
        radius1: Radius of first circle
        pos2: Center of second circle
        radius2: Radius of second circle
        
    Returns:
        True if circles overlap
    """
    return distance(pos1, pos2) < radius1 + radius2


def rect_overlap(rect1: Tuple[float, float, float, float],
                 rect2: Tuple[float, float, float, float]) -> bool:
    """
    Check if two rectangles overlap
    
    Args:
        rect1: Rectangle (x, y, width, height)
        rect2: Rectangle (x, y, width, height)
        
    Returns:
        True if rectangles overlap
    """
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)


def line_of_sight(from_pos: Tuple[float, float], to_pos: Tuple[float, float],
                  obstacles: list, sight_range: float) -> bool:
    """
    Check if there is line of sight between two positions
    
    Args:
        from_pos: Observer position
        to_pos: Target position
        obstacles: List of obstacles as rectangles
        sight_range: Maximum sight range
        
    Returns:
        True if line of sight exists
    """
    # Check distance first
    if distance(from_pos, to_pos) > sight_range:
        return False
    
    # Simple line of sight check - no obstacle intersection
    for obstacle in obstacles:
        if line_intersects_rect(from_pos, to_pos, obstacle):
            return False
    
    return True


def line_intersects_rect(p1: Tuple[float, float], p2: Tuple[float, float],
                         rect: Tuple[float, float, float, float]) -> bool:
    """
    Check if a line segment intersects a rectangle
    
    Args:
        p1: Line start point
        p2: Line end point
        rect: Rectangle (x, y, width, height)
        
    Returns:
        True if line intersects rectangle
    """
    x, y, w, h = rect
    
    # Simple AABB line intersection
    # Check if line from p1 to p2 intersects rectangle
    x1, y1 = p1
    x2, y2 = p2
    
    # Rectangle bounds
    left, top = x, y
    right, bottom = x + w, y + h
    
    # Quick rejection test
    if max(x1, x2) < left or min(x1, x2) > right:
        return False
    if max(y1, y2) < top or min(y1, y2) > bottom:
        return False
    
    return True


def smooth_lerp(start: float, end: float, t: float) -> float:
    """
    Linear interpolation between two values
    
    Args:
        start: Start value
        end: End value
        t: Interpolation factor (0-1)
        
    Returns:
        Interpolated value
    """
    return start + (end - start) * clamp(t, 0, 1)


def format_time(seconds: float) -> str:
    """
    Format seconds into MM:SS format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"


def format_vector(vector: Tuple[float, float]) -> str:
    """Format a vector as string"""
    return f"({vector[0]:.1f}, {vector[1]:.1f})"


def format_position(pos: Tuple[float, float]) -> str:
    """Format a position as string"""
    return f"({int(pos[0])}, {int(pos[1])})"
