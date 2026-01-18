"""
CompVis - Computer Vision module for SteadyScript.
Handles marker detection, session management, and calibration.
"""

from .cv_tracker import detect_marker, get_mask, draw_marker_overlay, DEFAULT_HSV_LOWER, DEFAULT_HSV_UPPER
from .session import SessionManager
from .calibration import CalibrationState, CalibrationHandler
from .utils import point_in_circle, smooth_positions, compute_percentile

__all__ = [
    'detect_marker',
    'get_mask',
    'draw_marker_overlay',
    'DEFAULT_HSV_LOWER',
    'DEFAULT_HSV_UPPER',
    'SessionManager',
    'CalibrationState',
    'CalibrationHandler',
    'point_in_circle',
    'smooth_positions',
    'compute_percentile',
]

