"""
OpenCV color tracking logic.

This module handles:
- Decoding base64 video frames
- HSV color space conversion
- Color mask creation and contour detection
- Position extraction from detected objects

TODO: Implement color tracking with OpenCV
"""

import cv2
import numpy as np
import base64
from typing import Optional, Tuple

COLOR_RANGES = {
    "red": {"lower": (0, 100, 100), "upper": (10, 255, 255)},
    "green": {"lower": (35, 100, 100), "upper": (85, 255, 255)},
    "blue": {"lower": (100, 100, 100), "upper": (130, 255, 255)},
}


def decode_frame(base64_data: str) -> Optional[np.ndarray]:
    """Decode a base64-encoded image to numpy array."""
    try:
        img_data = base64.b64decode(base64_data)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def track_color(frame: np.ndarray, color: str = "red") -> Optional[Tuple[int, int]]:
    """
    Track a colored object in the frame.
    
    Args:
        frame: BGR image as numpy array
        color: Color to track (red, green, blue)
    
    Returns:
        (x, y) position of detected object center, or None if not detected
    """
    if color not in COLOR_RANGES:
        return None

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array(COLOR_RANGES[color]["lower"])
    upper = np.array(COLOR_RANGES[color]["upper"])
    
    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 100:
        return None
    
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return (cx, cy)

