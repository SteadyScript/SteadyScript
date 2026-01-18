"""
Utility functions for SteadyScript tremor training system.
Handles JSON I/O, position smoothing, percentile calculations, and geometric helpers.
"""

import json
import os
import math
from typing import List, Tuple, Optional


def load_sessions(data_file: str = "data/sessions.json") -> List[dict]:
    """
    Load session data from JSON file.
    Returns empty list if file doesn't exist.
    
    Args:
        data_file: Path to sessions JSON file
        
    Returns:
        List of session dictionaries
    """
    if not os.path.exists(data_file):
        return []
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading sessions: {e}")
        return []


def save_session(session_data: dict, data_file: str = "data/sessions.json") -> bool:
    """
    Append a session result to the JSON file.
    Creates directory and file if they don't exist.
    
    Args:
        session_data: Dictionary containing session metrics
        data_file: Path to sessions JSON file
        
    Returns:
        True if successful, False otherwise
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    # Load existing sessions
    sessions = load_sessions(data_file)
    
    # Append new session
    sessions.append(session_data)
    
    try:
        with open(data_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving session: {e}")
        return False


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
    
    # Use last N positions
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
