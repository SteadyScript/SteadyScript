"""
Utility functions for SteadyScript tremor training system.
Handles position smoothing, percentile calculations, and geometric helpers.
"""

import math
from typing import List, Tuple, Optional


def smooth_positions(positions: List[Tuple[float, float]], window: int = 10) -> Optional[Tuple[float, float]]:
    """Compute moving average of positions over a window."""
    if len(positions) == 0:
        return None
    
    recent = positions[-window:] if len(positions) > window else positions
    
    if len(recent) == 0:
        return None
    
    avg_x = sum(p[0] for p in recent) / len(recent)
    avg_y = sum(p[1] for p in recent) / len(recent)
    
    return (avg_x, avg_y)


def compute_percentile(values: List[float], percentile: float) -> float:
    """Compute percentile value from a list of numbers."""
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
