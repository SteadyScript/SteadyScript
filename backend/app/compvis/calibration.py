"""
Calibration module for SteadyScript.
Handles circle calibration (center + radius).
"""

import math
from typing import Optional, Tuple


class CalibrationState:
    """Stores calibration data for the target circle."""
    
    def __init__(self):
        self.center: Optional[Tuple[int, int]] = None
        self.edge: Optional[Tuple[int, int]] = None
        self.radius: float = 0.0
    
    def is_complete(self) -> bool:
        """Check if calibration is complete (both center and edge set)."""
        return self.center is not None and self.edge is not None
    
    def reset(self):
        """Reset calibration to uninitialized state."""
        self.center = None
        self.edge = None
        self.radius = 0.0
    
    def set_center(self, x: int, y: int):
        """Set circle center point."""
        self.center = (x, y)
        if self.edge is not None:
            self._calculate_radius()
    
    def set_edge(self, x: int, y: int):
        """Set circle edge point and calculate radius."""
        self.edge = (x, y)
        if self.center is not None:
            self._calculate_radius()
    
    def set_radius(self, radius: float):
        """Set radius directly."""
        self.radius = radius
        self.edge = None
    
    def _calculate_radius(self):
        """Calculate radius from center and edge points."""
        if self.center is None or self.edge is None:
            self.radius = 0.0
            return
        
        dx = self.edge[0] - self.center[0]
        dy = self.edge[1] - self.center[1]
        self.radius = math.sqrt(dx * dx + dy * dy)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "center": {"x": self.center[0], "y": self.center[1]} if self.center else None,
            "radius": self.radius,
            "is_complete": self.is_complete()
        }


class CalibrationHandler:
    """Manages calibration state."""
    
    def __init__(self, calibration_state: CalibrationState = None):
        """
        Initialize calibration handler.
        
        Args:
            calibration_state: CalibrationState instance to manage
        """
        self.calibration = calibration_state or CalibrationState()
    
    def handle_click(self, x: int, y: int) -> dict:
        """
        Handle a click event for calibration.
        
        Args:
            x, y: Click coordinates
            
        Returns:
            Status dictionary
        """
        if self.calibration.center is None:
            self.calibration.set_center(x, y)
            return {"action": "center_set", "x": x, "y": y}
        elif self.calibration.edge is None:
            self.calibration.set_edge(x, y)
            return {"action": "edge_set", "x": x, "y": y, "radius": self.calibration.radius}
        else:
            return {"action": "already_complete"}
    
    def reset(self):
        """Reset calibration state."""
        self.calibration.reset()

