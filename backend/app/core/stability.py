"""
Stability and jitter calculation.

This module handles:
- Tracking position history
- Calculating jitter (standard deviation of positions)
- Computing stability score (0-100)
- Determining stability level (stable/warning/unstable)

TODO: Fine-tune thresholds based on testing
"""

from collections import deque
from typing import List, Tuple, Optional
import numpy as np

from ..config import settings


class StabilityCalculator:
    def __init__(self, window_size: int = None):
        self.window_size = window_size or settings.stability_window_size
        self.positions: deque = deque(maxlen=self.window_size)
    
    def add_position(self, x: int, y: int) -> None:
        """Add a new position to the history."""
        self.positions.append((x, y))
    
    def calculate_jitter(self) -> float:
        """Calculate jitter as standard deviation of recent positions."""
        if len(self.positions) < 2:
            return 0.0
        
        positions = np.array(list(self.positions))
        std_x = np.std(positions[:, 0])
        std_y = np.std(positions[:, 1])
        
        return float(np.sqrt(std_x**2 + std_y**2))
    
    def calculate_stability_score(self) -> Tuple[int, str]:
        """
        Calculate stability score and level.
        
        Returns:
            (score, level) where score is 0-100 and level is stable/warning/unstable
        """
        jitter = self.calculate_jitter()
        
        if jitter <= settings.jitter_threshold_low:
            score = 100
            level = "stable"
        elif jitter >= settings.jitter_threshold_high:
            score = max(0, int(100 - (jitter - settings.jitter_threshold_high) * 5))
            level = "unstable"
        else:
            ratio = (jitter - settings.jitter_threshold_low) / (
                settings.jitter_threshold_high - settings.jitter_threshold_low
            )
            score = int(100 - ratio * 50)
            level = "warning"
        
        return (score, level)
    
    def get_stability_data(self) -> dict:
        """Get complete stability data."""
        jitter = self.calculate_jitter()
        score, level = self.calculate_stability_score()
        
        return {
            "score": score,
            "level": level,
            "jitter": round(jitter, 2),
        }
    
    def reset(self) -> None:
        """Clear position history."""
        self.positions.clear()

