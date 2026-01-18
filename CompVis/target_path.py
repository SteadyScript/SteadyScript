"""
Target path module for Level 2 FOLLOW mode.
Generates moving target dot positions for smooth pursuit training.
"""

import math
import numpy as np
from typing import Tuple


class TargetPath:
    """Manages moving target dot path for FOLLOW mode."""
    
    def __init__(self, frame_width: int, frame_height: int):
        """
        Initialize target path.
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Center of frame
        self.center = (frame_width // 2, frame_height // 2)
        
        # Radius: 25% of minimum dimension
        min_dim = min(frame_width, frame_height)
        self.radius = int(0.25 * min_dim)
        
        # Angular speed: one full loop in ~8 seconds
        # omega = 2*pi / 8 = pi/4 rad/s
        self.angular_speed = math.pi / 4.0  # radians per second
        
        # Starting angle (can be randomized if desired)
        self.start_angle = 0.0
    
    def get_position(self, elapsed_time: float) -> Tuple[int, int]:
        """
        Get target position at given elapsed time.
        
        Args:
            elapsed_time: Time since session start in seconds
            
        Returns:
            (x, y) position of target dot
        """
        # Calculate angle at current time
        angle = self.start_angle + self.angular_speed * elapsed_time
        
        # Circular path
        x = self.center[0] + self.radius * math.cos(angle)
        y = self.center[1] + self.radius * math.sin(angle)
        
        return (int(x), int(y))
    
    def get_velocity(self, elapsed_time: float) -> Tuple[float, float]:
        """
        Get target velocity at given elapsed time (for optional tracking error).
        
        Args:
            elapsed_time: Time since session start in seconds
            
        Returns:
            (vx, vy) velocity vector in pixels per second
        """
        angle = self.start_angle + self.angular_speed * elapsed_time
        
        # Velocity is tangent to circle
        vx = -self.radius * self.angular_speed * math.sin(angle)
        vy = self.radius * self.angular_speed * math.cos(angle)
        
        return (vx, vy)
