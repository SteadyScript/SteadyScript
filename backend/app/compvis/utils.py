"""
Utility functions for SteadyScript tremor training system.
Handles position smoothing, percentile calculations, and geometric helpers.
"""

import math
from typing import List, Tuple, Optional


def smooth_positions(positions: List[Tuple[float, float]], window: int = 10) -> Optional[Tuple[float, float]]:
    """
    Compute moving average of positions over a window.
    
    Args:
        positions: List of (x, y) tuples
        window: Number of recent positions to average
        
    Returns:
        Smoothed (x, y) position or None if insufficient data
    """
    if len(positions) == 0:
        return None
    
    recent = positions[-window:] if len(positions) > window else positions
    
    if len(recent) == 0:
        return None
    
    avg_x = sum(p[0] for p in recent) / len(recent)
    avg_y = sum(p[1] for p in recent) / len(recent)
    
    return (avg_x, avg_y)


def compute_percentile(values: List[float], percentile: float) -> float:
    """
    Compute percentile value from a list of numbers.
    
    Args:
        values: List of numeric values
        percentile: Percentile to compute (0-100)
        
    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    
    sorted_vals = sorted(values)
    index = (percentile / 100.0) * (len(sorted_vals) - 1)
    
    if index.is_integer():
        return sorted_vals[int(index)]
    else:
        lower = sorted_vals[int(index)]
        upper = sorted_vals[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))


def point_in_circle(point: Tuple[float, float], center: Tuple[float, float], radius: float) -> bool:
    """
    Check if a point is inside a circle using Euclidean distance.
    
    Args:
        point: (x, y) coordinates of the point
        center: (x, y) coordinates of circle center
        radius: Circle radius
        
    Returns:
        True if point is inside or on the circle boundary
    """
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    return distance <= radius


def calculate_jitter(positions: List[Tuple[float, float]], window: int = 10) -> float:
    """
    Calculate jitter (deviation from smoothed position).
    
    Args:
        positions: List of (x, y) positions
        window: Smoothing window size
        
    Returns:
        Jitter value in pixels
    """
    if len(positions) < 2:
        return 0.0
    
    smoothed = smooth_positions(positions, window)
    if smoothed is None:
        return 0.0
    
    current = positions[-1]
    dx = current[0] - smoothed[0]
    dy = current[1] - smoothed[1]
    
    return math.sqrt(dx * dx + dy * dy)

