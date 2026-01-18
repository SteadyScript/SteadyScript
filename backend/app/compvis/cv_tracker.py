"""
Computer vision marker detection module for SteadyScript.
Uses HSV color segmentation to track a colored marker on the pen.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


DEFAULT_HSV_LOWER = np.array([100, 50, 50])
DEFAULT_HSV_UPPER = np.array([130, 255, 255])

MIN_CONTOUR_AREA = 100


def detect_marker(frame: np.ndarray, hsv_lower: np.ndarray, hsv_upper: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Detect colored marker in frame using HSV color segmentation.
    
    Args:
        frame: BGR image frame from camera
        hsv_lower: Lower HSV bounds (numpy array)
        hsv_upper: Upper HSV bounds (numpy array)
        
    Returns:
        (x, y) centroid of detected marker, or None if not found
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return None
    
    largest_contour = max(contours, key=cv2.contourArea)
    
    if cv2.contourArea(largest_contour) < MIN_CONTOUR_AREA:
        return None
    
    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return None
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return (cx, cy)


def get_mask(frame: np.ndarray, hsv_lower: np.ndarray, hsv_upper: np.ndarray) -> np.ndarray:
    """
    Get the binary mask for visualization/debugging.
    
    Args:
        frame: BGR image frame
        hsv_lower: Lower HSV bounds
        hsv_upper: Upper HSV bounds
        
    Returns:
        Binary mask image
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    return mask


def draw_marker_overlay(frame: np.ndarray, position: Optional[Tuple[int, int]], 
                        stability_level: str = "stable") -> np.ndarray:
    """
    Draw marker overlay on frame.
    
    Args:
        frame: BGR image frame
        position: (x, y) marker position or None
        stability_level: "stable", "warning", or "unstable"
        
    Returns:
        Frame with overlay drawn
    """
    if position is None:
        cv2.putText(frame, "Marker: NOT FOUND", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame
    
    colors = {
        "stable": (0, 255, 0),
        "warning": (0, 255, 255),
        "unstable": (0, 0, 255),
    }
    color = colors.get(stability_level, (0, 255, 0))
    
    cv2.circle(frame, position, 20, color, 2)
    cv2.circle(frame, position, 5, color, -1)
    
    cv2.putText(frame, f"Marker: ({position[0]}, {position[1]})", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame
