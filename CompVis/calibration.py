"""
Calibration module for SteadyScript.
Handles mouse click-based circle calibration (center + edge point).
"""

import math
import cv2
from typing import Optional, Tuple, Callable


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
        # Recalculate radius if edge is already set
        if self.edge is not None:
            self._calculate_radius()
    
    def set_edge(self, x: int, y: int):
        """Set circle edge point and calculate radius."""
        self.edge = (x, y)
        if self.center is not None:
            self._calculate_radius()
    
    def _calculate_radius(self):
        """Calculate radius from center and edge points."""
        if self.center is None or self.edge is None:
            self.radius = 0.0
            return
        
        dx = self.edge[0] - self.center[0]
        dy = self.edge[1] - self.center[1]
        self.radius = math.sqrt(dx * dx + dy * dy)


class CalibrationHandler:
    """Manages calibration state and mouse callbacks."""
    
    def __init__(self, calibration_state: CalibrationState):
        """
        Initialize calibration handler.
        
        Args:
            calibration_state: CalibrationState instance to manage
        """
        self.calibration = calibration_state
        self.on_calibration_update: Optional[Callable] = None
    
    def mouse_callback(self, event: int, x: int, y: int, flags: int, param):
        """
        OpenCV mouse callback for handling clicks.
        
        Args:
            event: OpenCV mouse event type
            x, y: Mouse coordinates
            flags: Event flags
            param: User data (unused)
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.calibration.center is None:
                # First click: set center
                self.calibration.set_center(x, y)
                print(f"Calibration: Center set at ({x}, {y})")
            elif self.calibration.edge is None:
                # Second click: set edge
                self.calibration.set_edge(x, y)
                print(f"Calibration: Edge set at ({x}, {y}), radius = {self.calibration.radius:.1f}")
            
            # Notify update callback if set
            if self.on_calibration_update:
                self.on_calibration_update()
    
    def reset(self):
        """Reset calibration state."""
        self.calibration.reset()
        if self.on_calibration_update:
            self.on_calibration_update()
