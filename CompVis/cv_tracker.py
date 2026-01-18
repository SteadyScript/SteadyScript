"""
Computer vision marker detection module for SteadyScript.
Uses HSV color segmentation to track a colored marker on the pen.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


# Default HSV ranges for blue marker
DEFAULT_HSV_LOWER = np.array([100, 50, 50])
DEFAULT_HSV_UPPER = np.array([130, 255, 255])

# Minimum contour area to filter noise
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
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask using color range
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    
    # Morphological operations to reduce noise
    # Opening: removes small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Closing: fills small holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return None
    
    # Get largest contour (the marker)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Filter by minimum area
    if cv2.contourArea(largest_contour) < MIN_CONTOUR_AREA:
        return None
    
    # Compute centroid using moments
    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return None
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return (cx, cy)


def create_hsv_trackbars(window_name: str, 
                         initial_lower: np.ndarray = None, 
                         initial_upper: np.ndarray = None) -> None:
    """
    Create HSV tuning trackbars for marker color adjustment.
    
    Args:
        window_name: Name of the OpenCV window
        initial_lower: Initial lower HSV bounds (defaults to DEFAULT_HSV_LOWER)
        initial_upper: Initial upper HSV bounds (defaults to DEFAULT_HSV_UPPER)
    """
    if initial_lower is None:
        initial_lower = DEFAULT_HSV_LOWER
    if initial_upper is None:
        initial_upper = DEFAULT_HSV_UPPER
    
    def nothing(x):
        pass
    
    # Create trackbars for lower bounds (H, S, V)
    cv2.createTrackbar('Lower H', window_name, int(initial_lower[0]), 179, nothing)
    cv2.createTrackbar('Lower S', window_name, int(initial_lower[1]), 255, nothing)
    cv2.createTrackbar('Lower V', window_name, int(initial_lower[2]), 255, nothing)
    
    # Create trackbars for upper bounds (H, S, V)
    cv2.createTrackbar('Upper H', window_name, int(initial_upper[0]), 179, nothing)
    cv2.createTrackbar('Upper S', window_name, int(initial_upper[1]), 255, nothing)
    cv2.createTrackbar('Upper V', window_name, int(initial_upper[2]), 255, nothing)


def get_hsv_from_trackbars(window_name: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Get current HSV bounds from trackbars.
    
    Args:
        window_name: Name of the OpenCV window
        
    Returns:
        Tuple of (lower_bounds, upper_bounds) as numpy arrays
    """
    lower_h = cv2.getTrackbarPos('Lower H', window_name)
    lower_s = cv2.getTrackbarPos('Lower S', window_name)
    lower_v = cv2.getTrackbarPos('Lower V', window_name)
    
    upper_h = cv2.getTrackbarPos('Upper H', window_name)
    upper_s = cv2.getTrackbarPos('Upper S', window_name)
    upper_v = cv2.getTrackbarPos('Upper V', window_name)
    
    lower = np.array([lower_h, lower_s, lower_v])
    upper = np.array([upper_h, upper_s, upper_v])
    
    return lower, upper


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
