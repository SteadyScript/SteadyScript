"""
Target path module for Level 2 FOLLOW mode.
Generates back-and-forth movement between points A and B.
"""

import math
from typing import Tuple, Optional


class TargetPath:
    """Manages moving target dot path for FOLLOW mode (A to B and back)."""
    
    def __init__(self, frame_width: int, frame_height: int):
        """
        Initialize target path.
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Points A and B (will be set via calibration)
        self.point_a: Optional[Tuple[int, int]] = None
        self.point_b: Optional[Tuple[int, int]] = None
        
        # Starting direction (True = A to B, False = B to A)
        self.starting_direction = True
        
        # Base speed (will increase over time)
        # Speed in cycles per second (one cycle = A->B->A)
        self.base_cycles_per_second = 0.3  # Start slow: ~0.3 cycles/sec = ~3.3 sec per cycle
    
    def set_points(self, point_a: Tuple[int, int], point_b: Tuple[int, int]):
        """Set calibration points A and B."""
        self.point_a = point_a
        self.point_b = point_b
    
    def is_calibrated(self) -> bool:
        """Check if both points are set."""
        return self.point_a is not None and self.point_b is not None
    
    def get_position(self, elapsed_time: float) -> Tuple[int, int]:
        """
        Get target position at given elapsed time.
        Moves back and forth between A and B with increasing speed.
        
        Args:
            elapsed_time: Time since session start in seconds
            
        Returns:
            (x, y) position of target dot
        """
        if not self.is_calibrated():
            # Default to center if not calibrated
            return (self.frame_width // 2, self.frame_height // 2)
        
        # Calculate distance between A and B
        dx = self.point_b[0] - self.point_a[0]
        dy = self.point_b[1] - self.point_a[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return self.point_a
        
        # Speed increases over time (metronome speeds up)
        # Start at base speed, increase by 0.1x every 5 seconds
        speed_multiplier = 1.0 + (elapsed_time / 5.0) * 0.1
        current_cycles_per_second = self.base_cycles_per_second * speed_multiplier
        
        # Calculate cycles (one cycle = A->B->A)
        # How many cycles have completed
        total_cycles = elapsed_time * current_cycles_per_second
        
        # Position within current cycle (0.0 to 1.0)
        cycle_position = total_cycles % 1.0
        
        # Determine direction: 0.0-0.5 = A to B, 0.5-1.0 = B to A
        if cycle_position <= 0.5:
            # A to B (0.0 -> 0.5 maps to 0.0 -> 1.0)
            position_ratio = cycle_position * 2.0
        else:
            # B to A (0.5 -> 1.0 maps to 1.0 -> 0.0)
            position_ratio = 2.0 - (cycle_position * 2.0)
        
        # Interpolate between A and B
        x = int(self.point_a[0] + position_ratio * dx)
        y = int(self.point_a[1] + position_ratio * dy)
        
        return (x, y)
    
    def get_current_speed_multiplier(self, elapsed_time: float) -> float:
        """Get current speed multiplier for metronome display."""
        return 1.0 + (elapsed_time / 5.0) * 0.1
